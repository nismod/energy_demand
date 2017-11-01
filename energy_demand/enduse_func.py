"""
Enduse
======

Contains the `Enduse` Class. This is the most important class
where the change in enduse specific energy demand is simulated
depending on scenaric assumptions.
"""
import logging
from collections import defaultdict
import numpy as np
from energy_demand.basic import testing_functions as testing
from energy_demand.initalisations import helpers as init
from energy_demand.profiles import load_profile as lp
from energy_demand.profiles import load_factors as lf
from energy_demand.technologies import diffusion_technologies
from energy_demand.technologies import fuel_service_switch

class Enduse(object):
    """Enduse Class (Residential, Service and Industry)

    For every region and sector, a different instance
    is generated. In this class, first the change in
    energy demand is calculated on a yearls temporal scale.
    Calculations are performed in a cascade (e.g. first
    reducing climate change induced savings, then substracting
    further behavioural savings etc.). After yearly calculations,
    the demand is converted to hourly demand.

    Also within this function, the fuel inputs are converted
    to energy service (short: service) and later on
    converted back to fuel demand.

    Arguments
    ----------
    region_name : str
        Region name
    scenario_data : dict
        Scenario data
    lookups : dict
        Lookups
    assumptions : dict
        Assumptions
    non_regional_lp_stock : dict
        Load profile stock
    sim_param : dict
        Simulation parameter
    enduse : str
        Enduse name
    sector : str
        Sector name
    fuel : array
        Yearly fuel data for different fueltypes
    tech_stock : object
        Technology stock of region
    heating_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with HDD)
    cooling_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with CDD)
    fuel_switches : list
        Fuel switches
    service_switches : list
        Service switches
    fuel_tech_p_by : dict
        Fuel tech assumtions in base year
    tech_increased_service : dict
        Technologies per enduse with increased service due to scenarios
    tech_decreased_share : dict
        Technologies per enduse with decreased service due to scenarios
    tech_constant_share : dict
        Technologies per enduse with constat service
    installed_tech : dict
        Installed technologes for this enduse
    sig_param_tech : dict
        Sigmoid parameters
    enduse_overall_change_ey : dict
        Assumptions related to overal change in endyear
    regional_lp_stock : object
        Load profile stock
    dw_stock : object,default=False
        Dwelling stock
    reg_scen_drivers : bool,default=None
        Scenario drivers per enduse
    crit_flat_profile : bool,default=False
        Criteria of enduse has a flat shape or not

    Note
    ----
    - Load profiles are assigned independently of the fueltype, i.e.
      the same profiles are assumed to hold true across different fueltypes

    - ``self.fuel_new_y`` is always overwritten in the cascade of calculations

    Warning
    -------
    Not all enduses have technologies assigned. Load peaks are derived
    from techstock in case technologies are defined. Otherwise enduse load
    profiles are used.
    """
    def __init__(
            self,
            region_name,
            scenario_data,
            lookups,
            assumptions,
            non_regional_lp_stock,
            sim_param,
            enduse,
            sector,
            fuel,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            fuel_switches,
            service_switches,
            fuel_tech_p_by,
            tech_increased_service,
            tech_decreased_share,
            tech_constant_share,
            installed_tech,
            sig_param_tech,
            enduse_overall_change_ey,
            regional_lp_stock,
            dw_stock=False,
            reg_scen_drivers=None,
            crit_flat_profile=False,
        ):
        """Enduse class constructor
        """
        self.region_name = region_name
        self.enduse = enduse
        self.sector = sector
        self.fuel_new_y = fuel
        self.crit_flat_profile = crit_flat_profile

        if np.sum(fuel) == 0: #If enduse has no fuel return empty shapes
            self.crit_flat_profile = True
            self.fuel_y = np.zeros((lookups['fueltypes_nr']), dtype=float)
            self.fuel_yh = 0
            self.fuel_peak_dh = np.zeros((lookups['fueltypes_nr'], 24), dtype=float)
            self.fuel_peak_h = 0
        else:
            # Get correct parameters depending on model configuration
            load_profiles = get_lp_stock(
                enduse, non_regional_lp_stock, regional_lp_stock)

            self.enduse_techs = get_enduse_tech(fuel_tech_p_by)

            # -------------------------------
            # Cascade of calculations on a yearly scale
            # --------------------------------
            # --Change fuel consumption based on climate change induced temperature differences
            self.fuel_new_y = apply_climate_change(
                enduse,
                self.fuel_new_y,
                cooling_factor_y,
                heating_factor_y,
                assumptions)
            logging.debug("... Fuel train B: " + str(np.sum(self.fuel_new_y)))

            # --Change fuel consumption based on smart meter induced general savings
            self.fuel_new_y = apply_smart_metering(
                enduse,
                self.fuel_new_y,
                assumptions,
                sim_param)
            logging.debug("... Fuel train C: " + str(np.sum(self.fuel_new_y)))

            # --Enduse specific consumption change in %
            self.fuel_new_y = apply_specific_change(
                enduse,
                self.fuel_new_y,
                assumptions,
                enduse_overall_change_ey,
                sim_param)
            logging.debug("... Fuel train D: " + str(np.sum(self.fuel_new_y)))

            # -------------------------------------------------------------------------------
            # Calculate new fuel demands after scenario drivers
            # -------------------------------------------------------------------------------
            self.fuel_new_y = apply_scenario_drivers(
                enduse,
                self.fuel_new_y,
                dw_stock,
                region_name,
                scenario_data['gva'],
                scenario_data['population'],
                reg_scen_drivers,
                sim_param)
            logging.debug("... Fuel train E: " + str(np.sum(self.fuel_new_y)))

            # ----------------------------------
            # Hourly Disaggregation
            # ----------------------------------
            if self.enduse_techs == []:
                """If no technologies are defined for an enduse, the load profiles
                are read from dummy shape, which show the load profiles of the whole enduse.
                No switches can be implemented and only overall change of enduse.

                Note: for heating, technologies need to be assigned. Otherwise,
                here there will be problems
                """
                if crit_flat_profile:
                    self.fuel_y = self.fuel_new_y * assumptions['model_yeardays_nrs'] / 365.0
                else:
                    self.fuel_yh, self.fuel_peak_dh, self.fuel_peak_h = assign_lp_no_techs(
                        enduse,
                        sector,
                        load_profiles,
                        self.fuel_new_y)
            else:
                """If technologies are defined for an enduse
                """
                # ----
                # Get enduse specific configurations
                # ----
                mode_constrained, crit_switch_fuel, crit_switch_service = get_enduse_configuration(
                    enduse, assumptions, sim_param, fuel_switches, service_switches)

                # ------------------------------------
                # Calculate regional energy service
                # ------------------------------------
                tot_service_y_cy, service_tech_y_cy, service_tech_cy_p, service_fueltype_tech_cy_p, service_fueltype_cy_p = fuel_to_service(
                    enduse,
                    self.fuel_new_y,
                    self.enduse_techs,
                    fuel_tech_p_by,
                    tech_stock,
                    lookups['fueltype'],
                    mode_constrained)

                # ------------------------------------
                # Reduction of service because of heat recovery
                # (standard sigmoid diffusion)
                # ------------------------------------
                tot_service_y_cy = apply_heat_recovery(
                    enduse,
                    assumptions,
                    tot_service_y_cy,
                    'tot_service_y_cy',
                    sim_param)

                service_tech_y_cy = apply_heat_recovery(
                    enduse,
                    assumptions,
                    service_tech_y_cy,
                    'service_tech',
                    sim_param)

                # --------------------------------
                # Switches (service or fuel)
                # --------------------------------
                if crit_switch_service:
                    logging.debug("... Service switch is implemented " + str(self.enduse))
                    service_tech_y_cy = service_switch(
                        enduse,
                        tot_service_y_cy,
                        service_tech_cy_p,
                        tech_increased_service,
                        tech_decreased_share,
                        tech_constant_share,
                        sig_param_tech,
                        sim_param['curr_yr'])
                elif crit_switch_fuel:
                    logging.debug("... fuel_switch is implemented " + str(self.enduse))
                    service_tech_y_cy = fuel_switch(
                        enduse,
                        installed_tech,
                        sig_param_tech,
                        tot_service_y_cy,
                        service_tech_y_cy,
                        service_fueltype_tech_cy_p,
                        service_fueltype_cy_p,
                        fuel_switches,
                        fuel_tech_p_by,
                        sim_param['curr_yr'])
                else:
                    pass #No switch implemented
                
                # -------------------------------------------
                # Convert annual service to fuel per fueltype
                # -------------------------------------------
                self.fuel_new_y, fuel_tech_y = service_to_fuel(
                    enduse,
                    service_tech_y_cy,
                    tech_stock,
                    lookups,
                    mode_constrained)

                # ------------------------------------------
                # Assign load profiles
                # ------------------------------------------
                '''print(self.crit_flat_profile)
                if self.crit_flat_profile:
                    priddnt("ee")
                    self.fuel_y = assign_flat_load_profiles_techs(
                        enduse,
                        tech_stock,
                        fuel_tech_y,
                        lookups,
                        mode_constrained)
                    print("tt")
                else:'''

                self.fuel_y = self.fuel_new_y

                '''fuel_yh, self.fuel_peak_dh, self.fuel_peak_h = assign_load_profiles_techs(
                    enduse,
                    sector,
                    self.enduse_techs,
                    tech_stock,
                    fuel_tech_y,
                    lookups,
                    assumptions['model_yeardays_nrs'],
                    mode_constrained,
                    load_profiles)'''

                #---NON-PEAK
                fuel_yh = calc_fuel_tech_yh(
                    enduse,
                    sector,
                    self.enduse_techs,
                    fuel_tech_y,
                    tech_stock,
                    load_profiles,
                    lookups,
                    mode_constrained,
                    assumptions['model_yeardays_nrs'])

                # --PEAK
                # Iterate technologies in enduse and assign technology specific profiles
                fuel_peak_dh = calc_peak_tech_dh(
                    enduse,
                    sector,
                    self.enduse_techs,
                    fuel_tech_y,
                    fuel_yh,
                    tech_stock,
                    load_profiles,
                    lookups)

                # ---------------------------------------
                # Demand Management (peak shaving)
                # ---------------------------------------
                # Calculate average for every day
                average_fuel_yd = np.mean(fuel_yh, axis=2)

                # Calculate laod factors (only inter_day load shifting as for now)
                loadfactor_yd_cy = lf.calc_lf_d(fuel_yh, average_fuel_yd)

                # Calculate current year load factors
                lf_cy_improved_d, peak_shift_crit = calc_lf_improvement(
                    enduse, sim_param, loadfactor_yd_cy, assumptions['demand_management'])

                if not peak_shift_crit:
                    self.fuel_yh = fuel_yh
                    self.fuel_peak_dh = fuel_peak_dh
                    # Get maximum hour demand of peak day
                    self.fuel_peak_h = lp.calk_peak_h_dh(fuel_peak_dh)
                else:

                    self.fuel_yh = lf.peak_shaving_max_min(
                        lf_cy_improved_d,
                        average_fuel_yd,
                        fuel_yh)

                    self.fuel_peak_dh = calc_peak_tech_dh(
                        enduse,
                        sector,
                        self.enduse_techs,
                        fuel_tech_y,
                        self.fuel_yh,
                        tech_stock,
                        load_profiles,
                        lookups)

                    self.fuel_peak_h = lp.calk_peak_h_dh(self.fuel_peak_dh)

def calc_lf_improvement(enduse, sim_param, loadfactor_yd_cy, lf_improvement_ey):
    """Calculate lf improvement depending on linear diffusion

    Test if lager than zero --> replace by one

    """
    try:
        # Get assumed load shift
        if lf_improvement_ey[enduse] == 0:
            return False, False
        else:
            # Calculate linear diffusion of improvement of load management
            # TODO: Could be sligliht made faster if linear diffusion is calculated once
            # on top of enduse class
            lin_diff_factor = diffusion_technologies.linear_diff(
                sim_param['base_yr'],
                sim_param['curr_yr'],
                0,
                1,
                sim_param['sim_period_yrs'])

            # Current year load factor improvement
            lf_improvement_cy = lf_improvement_ey[enduse] * lin_diff_factor

            # Improve load factor
            lf_cy_improved_d = loadfactor_yd_cy + lf_improvement_cy

            # If lager than zero, set to 1
            lf_cy_improved_d[lf_cy_improved_d > 1] = 1

            peak_shift_crit = True

            return lf_cy_improved_d, peak_shift_crit
    except KeyError:
        logging.debug("... no load management was defined for enduse")
        return False, False

def assign_flat_load_profiles_techs(enduse, tech_stock, fuel_tech_y, lookups, mode_constrained):
    '''If a flat load profile is assigned (crit_flat_profile)
    do not store whole 8760 profile. This is only done in
    the summing step to save on memory TODO
    '''
    fuel_y = calc_fuel_tech_y(
        enduse,
        tech_stock,
        fuel_tech_y,
        lookups,
        mode_constrained)

    return fuel_y

'''def assign_load_profiles_techs(
        enduse,
        sector,
        enduse_techs,
        tech_stock,
        fuel_tech_y,
        lookups,
        model_yeardays_nrs,
        mode_constrained,
        load_profiles
    ):
    """Assign load profile to enduse

    TODO
    """
    #---NON-PEAK
    fuel_yh = calc_fuel_tech_yh(
        enduse,
        sector,
        enduse_techs,
        fuel_tech_y,
        tech_stock,
        load_profiles,
        lookups,
        mode_constrained,
        model_yeardays_nrs
        )

    # --PEAK
    # Iterate technologies in enduse and assign technology specific profiles
    fuel_peak_dh = calc_peak_tech_dh(
        enduse,
        sector,
        enduse_techs,
        fuel_tech_y,
        fuel_yh,
        tech_stock,
        load_profiles,
        lookups
        )

    # Get maximum hour demand of peak day
    fuel_peak_h = lp.calk_peak_h_dh(fuel_peak_dh)

    return fuel_yh, fuel_peak_dh, fuel_peak_h
'''
def assign_lp_no_techs(enduse, sector, load_profiles, fuel_new_y):
    """Assign load profiles for an enduse which has not
    technologies defined.

    Arguments
    ---------
    enduse : str
        Enduse
    sector : str
        Enduse
    load_profiles : obj
        Load profiles
    fuel_new_y : array
        Fuels

    Returns
    -------
    """
    _fuel = fuel_new_y[:, np.newaxis, np.newaxis]

    fuel_yh = load_profiles.get_lp(
        enduse, sector, 'dummy_tech', 'shape_yh') * _fuel

    # Read dh profile from peak day
    peak_day = get_peak_day(fuel_yh)

    shape_peak_dh = lp.abs_to_rel(fuel_yh[:, peak_day, :])

    enduse_peak_yd_factor = load_profiles.get_lp(
        enduse, sector, 'dummy_tech', 'enduse_peak_yd_factor')

    fuel_peak_dh = fuel_new_y[:, np.newaxis] * enduse_peak_yd_factor * shape_peak_dh

    fuel_peak_h = lp.calk_peak_h_dh(fuel_peak_dh)

    return fuel_yh, fuel_peak_dh, fuel_peak_h

def get_lp_stock(enduse, non_regional_lp_stock, regional_lp_stock):
    """Defines the load profile stock depending on `enduse`.
    (Get regional or non-regional load profile data)

    Arguments
    ----------
    enduse : str
        Enduse
    non_regional_lp_stock : object
        Non regional dependent load profiles
    regional_lp_stock : object
        Regional dependent load profiles

    Returns
    -------
    load_profiles : object
        Load profile

    Note
    -----
    Because for some enduses the load profiles depend on the region
    they are stored in the `WeatherRegion` Class. One such example is
    heating. If the enduse is not dependent on the region, the same
    load profile can be used for all regions

    If the enduse depends on regional factors, `regional_lp_stock`
    is returned. Otherwise, non-regional load profiles which can
    be applied for all regions is used (`non_regional_lp_stock`)
    """
    if enduse in non_regional_lp_stock.enduses_in_stock:
        return non_regional_lp_stock
    else:
        return regional_lp_stock

def get_running_mode(enduse, mode_constrained, enduse_space_heating):
    """Check which mode needs to be run for an enduse

    Arguments
    -----------
    mode_constrained : bool
        Criteria of running mode
    enduse_space_heating : dict
        All heating enduses across all models

    Returns
    -------
    bool : bool
        The return value

    Note
    ----
    If 'crit_mode' == True, then overall heat is provided to
    the supply model not specified for technologies. Otherwise,
    heat demand is supplied per technology
    """
    if mode_constrained and enduse in enduse_space_heating:
        return True
    else:
        return False

def get_enduse_configuration(enduse, assumptions, sim_param, fuel_switches, service_switches):
    """Get enduse specific configuration

    Arguments
    ---------

    """
    mode_constrained = get_running_mode(
        enduse,
        assumptions['mode_constrained'],
        assumptions['enduse_space_heating'])

    crit_switch_fuel = get_crit_switch(
        enduse,
        fuel_switches,
        sim_param,
        mode_constrained)

    crit_switch_service = get_crit_switch(
        enduse,
        service_switches,
        sim_param,
        mode_constrained)

    testing.testing_switch_criteria(
        crit_switch_fuel,
        crit_switch_service,
        enduse)

    # Test if capacity switch is implemented
    try:
        if assumptions['capacity_switch'] and crit_switch_service:
            logging.warning(
                "Warning: Capacity switch and service switch are installed simultaniously"
                )
    except KeyError:
        logging.debug("... no capacity and service switch defined simultaniously")

    return mode_constrained, crit_switch_fuel, crit_switch_service

def get_crit_switch(enduse, fuelswitches, base_parameters, mode_constrained):
    """Test whether there is a switch (service or fuel)

    Arguments
    ----------
    fuelswitches : dict
        All fuel switches
    base_parameters : float
        Base Arguments
    mode_constrained : bool
        Mode criteria

    Note
    ----
    If base year, no switches are implemented
    """
    if base_parameters['base_yr'] == base_parameters['curr_yr'] or mode_constrained is True:
        return False
    else:
        for fuelswitch in fuelswitches:
            if fuelswitch['enduse'] == enduse:
                return True

        return False

def get_peak_day(fuel_yh):
    """Iterate yh and get day with highes fuel (across all fueltypes)

    Return
    ------
    peak_day_nr : int
        Day with most fuel or service across all fueltypes

    Note
    -----
    - The day with most fuel across all fueltypes is
    considered to be the peak day
    - The Peak day may change date in a year
    """
    # Sum all fuel across all fueltypes for every hour in a year
    all_fueltypes_tot_h = np.sum(fuel_yh, axis=0)

    # Sum fuel within every hour for every day and get day with maximum fuel
    peak_day_nr = np.argmax(np.sum(all_fueltypes_tot_h, axis=1))

    return peak_day_nr

def calc_peak_tech_dh(
        enduse,
        sector,
        enduse_techs,
        enduse_fuel_tech,
        fuel_yh,
        tech_stock,
        load_profile,
        lookups
    ):
    """Calculate peak demand for every fueltype

    Arguments
    ----------
    assumptions : array
        Assumptions
    enduse_fuel_tech : array
        Fuel per enduse and technology
    tech_stock : data
        Technology stock
    load_profile : object
        Load profile

    Returns
    -------
    fuels_peak_dh : array
        Peak values for peak day for every fueltype

    Note
    ----
    - This function gets the hourly values of the peak day for every fueltype.
        The daily fuel is converted to dh for each technology.

    - For some technology types (heat_pump and hybrid)
        the dh peak day profile is not read in from technology
        stock but from shape_yh of peak day (hybrid technologies).
    """
    fuels_peak_dh = np.zeros((lookups['fueltypes_nr'], 24), dtype=float)

    for tech in enduse_techs:

        tech_type = tech_stock.get_tech_attr(enduse, tech, 'tech_type')

        tech_fuel_type_int = tech_stock.get_tech_attr(
            enduse, tech, 'tech_fueltype_int')

        if tech_type == 'heat_pump':
            """Read fuel from peak day
            """
            # Get day with most fuel across all fueltypes
            peak_day_nr = get_peak_day(fuel_yh)

            # Calculate absolute fuel values for yd (multiply fuel with yd_shape)
            fuel_tech_yd = enduse_fuel_tech[tech] * load_profile.get_lp(
                enduse, sector, tech, 'shape_yd')

            # Calculate fuel for peak day
            fuel_tech_peak_d = fuel_tech_yd[peak_day_nr]

            # The 'shape_peak_dh'is not defined in technology stock because
            # in the 'Region' the peak day is not yet known
            # Therfore, the shape_yh is read in and with help of
            # information on peak day the hybrid dh shape generated
            tech_peak_dh = load_profile.get_lp(
                enduse, sector, tech, 'shape_y_dh')[peak_day_nr]
        else:
            """Calculate fuel with peak factor
            """
            enduse_peak_yd_factor = load_profile.get_lp(
                enduse, sector, tech, 'enduse_peak_yd_factor')

            # Calculate fuel for peak day
            fuel_tech_peak_d = enduse_fuel_tech[tech] * enduse_peak_yd_factor

            # Assign Peak shape of a peak day of a technology
            tech_peak_dh = load_profile.get_shape_peak_dh(
                enduse, sector, tech)

        # Multiply absolute d fuels with dh peak fuel shape
        fuel_tech_peak_dh = tech_peak_dh * fuel_tech_peak_d

        # Peak day fuel shape * fueltype distribution for peak day
        # select from (7, nr_of_days, 24) only peak day for all fueltypes
        fuels_peak_dh[tech_fuel_type_int] += fuel_tech_peak_dh

    return fuels_peak_dh

def get_enduse_tech(fuel_tech_p_by):
    """Get all defined technologies of an enduse

    Arguments
    ----------
    fuel_tech_p_by : dict
        Percentage of fuel per enduse per technology

    Return
    ------
    enduse_techs : list
        All technologies

    Note
    ----
    All technologies are read out, including those which
    are potentiall defined in fuel or service switches.

    If for an enduse a dummy technology is defined,
    the technologies of an enduse are set to an empty
    list.

    Warning
    -------
    For every enduse technologes must either be defined
    for no fueltype or for all fueltypes
    """
    enduse_techs = []
    for tech_fueltype in fuel_tech_p_by.values():
        if 'dummy_tech' in tech_fueltype.keys():
            return []
        else:
            enduse_techs += tech_fueltype.keys()

    return list(set(enduse_techs))

def calc_fuel_tech_yh(
        enduse,
        sector,
        enduse_techs,
        enduse_fuel_tech,
        tech_stock,
        load_profiles,
        lookups,
        mode_constrained,
        model_yeardays_nrs
    ):
    """Iterate fuels for each technology and assign shape yd and yh shape

    Arguments
    ----------
    enduse_fuel_tech : dict
        Fuel per technology in enduse
    tech_stock : object
        Technologies
    load_profiles : object
        Load profiles
    lookups : dict
        Fuel look-up table
    mode_constrained : bool
        Mode criteria
    model_yeardays_nrs : int
        Number of modelled days

    Return
    ------
    fuels_yh : array
        Fueltype storing hourly fuel for every fueltype (fueltype, model_yeardays_nrs, 24)
    """
    fuels_yh = np.zeros((lookups['fueltypes_nr'], model_yeardays_nrs, 24), dtype=float)

    if mode_constrained:
        for tech in enduse_techs:
            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            if model_yeardays_nrs != 365:
                load_profile = lp.abs_to_rel(load_profile)

            fuel_tech_yh = enduse_fuel_tech[tech] * load_profile

            fuels_yh[lookups['fueltype']['heat']] += fuel_tech_yh
    else:
        for tech in enduse_techs:

            tech_fueltype_int = tech_stock.get_tech_attr(
                enduse, tech, 'tech_fueltype_int')

            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            # Fuel distribution
            # Only needed if modelled days is not 365 because the
            # service in fuel_to_service() was already reduced
            # to selected modelled days
            if model_yeardays_nrs != 365:
                load_profile = lp.abs_to_rel(load_profile)

            fuel_tech_yh = enduse_fuel_tech[tech] * load_profile

            # Get distribution per fueltype
            fuels_yh[tech_fueltype_int] += fuel_tech_yh

    return fuels_yh

def calc_fuel_tech_y(enduse, tech_stock, fuel_tech_y, lookups, mode_constrained):
    """Calculate yearly fuel per fueltype (no load profile assigned)

    Arguments
    -----------
    tech_stock : object
        Technology stock
    fuel_tech_y : dict
        Fuel per technology per year
    lookups : dict
        look-up
    mode_constrained : bool
        Running mode

    Returns
    -------
    fuel_y : array
        Fuel per year per fueltype

    Note
    ----
    This function can be run in two different modes
    """
    fuel_y = np.zeros((lookups['fueltypes_nr']), dtype=float)

    if mode_constrained:
        for tech, fuel_tech_y in fuel_tech_y.items():
            tech_fuel_type_int = tech_stock.get_tech_attr(
                enduse,
                tech,
                'tech_fueltype_int')
            # Assign all to heat fueltype
            fuel_y[lookups['fueltype']['heat']] += np.sum(fuel_tech_y)
    else:
        for tech, fuel_tech_y in fuel_tech_y.items():
            tech_fuel_type_int = tech_stock.get_tech_attr(
                enduse,
                tech,
                'tech_fueltype_int')
            # Assign to fueltype of technology
            fuel_y[tech_fuel_type_int] += np.sum(fuel_tech_y)

    return fuel_y

def service_to_fuel(enduse, service_tech, tech_stock, lookups, mode_constrained):
    """Convert yearly energy service to yearly fuel demand.
    For every technology the service is taken and converted
    to fuel based on efficiency of current year

    Inputs
    ------
    service_tech : dict
        Service per fueltype and technology
    tech_stock : object
        Technological stock
    lookups : dict
        look-up
    mode_constrained : bool
        Mode running criteria

    Return
    ------
    fuel_per_tech : dict
        Fuel per technology  Convert annaul service to fuel per fueltype for each technology

    Note
    -----
    - The attribute 'fuel_new_y' is updated
    - Fuel = Energy service / efficiency
    """
    fuel_per_tech = {}
    fuel_new_y = np.zeros((lookups['fueltypes_nr']), dtype=float)

    if mode_constrained:
        for tech, fuel_tech in service_tech.items():
            fuel = fuel_tech
            fuel_new_y[lookups['fueltype']['heat']] += fuel
            fuel_per_tech[tech] = fuel
    else:
        for tech, service in service_tech.items():
            tech_eff = tech_stock.get_tech_attr(
                enduse, tech, 'eff_cy')

            tech_fuel_type_int = tech_stock.get_tech_attr(
                enduse, tech, 'tech_fueltype_int')

            # Convert to fuel
            fuel = service / tech_eff

            fuel_per_tech[tech] = fuel

            # Multiply fuel of technology per fueltype with shape of yearl distrbution
            fuel_new_y[tech_fuel_type_int] += fuel

    return fuel_new_y, fuel_per_tech

def fuel_to_service(
        enduse,
        fuel_new_y,
        enduse_techs,
        fuel_tech_p_by,
        tech_stock,
        lu_fueltypes,
        mode_constrained,
    ):
    """Converts fuel to energy service (1),
    calcualates contribution service fraction (2)

    Arguments
    ----------
    fuel_tech_p_by : dict
        Fuel composition of base year for every fueltype for each
        enduse (assumtions for national scale)
    tech_stock : object
        Technology stock of region
    lu_fueltypes : dict
        Fueltype look-up
    load_profiles : object
        Load profiles
    mode_constrained : bool
        Criteria about mode

    Return
    ------
    tot_service_yh : array
        Absolute total yh energy service per technology and fueltype
    service_tech : dict
        Absolute energy service for every technology
    service_tech_p : dict
        Fraction of energy service for every technology
        (sums up to one in total (not specified by fueltype))
    service_fueltype_tech_p : dict
        Fraction of energy service per fueltype and technology
        (within every fueltype sums up to one)
    service_fueltype_p : dict
        Fraction of service per fueltype
        (within every fueltype sums up to one)

    Note
    -----
    **(1)** Calculate energy service of each technology based on assumptions
    about base year fuel shares of an enduse (`fuel_tech_p_by`).

    **(2)** The fraction of an invidual technology to which it
    contributes to total energy service (e.g. how much of
    total heat service is provided by boiler technology).

    -   Efficiency changes of technologis are considered.
    -   Energy service = fuel * efficiency
    -   This function can be run in two modes, depending on `mode_constrained` criteria
    -   The base year efficiency is taken because the actual service can
        only be calculated with base year. Otherwise, the service would
        increase e.g. if technologies would become more efficient.
        Efficiencies are only considered if converting back to fuel
        However, the self.fuel_new_y is taken because the actual
        service was reduced e.g. due to smart meters or temperatur changes
    """
    service_tech = dict.fromkeys(enduse_techs, 0)
    tot_service_y = 0

    if mode_constrained:
        """
        Constrained version
        no efficiencies are considered, because not technology specific service calculation
        """
        service_fueltype_tech = init.service_type_tech_by_p(lu_fueltypes, fuel_tech_p_by)
        # Calculate share of service
        for fueltype, tech_list in fuel_tech_p_by.items():
            for tech, fuel_share in tech_list.items():
                fuel_tech = fuel_new_y[fueltype] * fuel_share
                tot_service_y += fuel_tech
                service_tech[tech] += fuel_tech

                # Assign all service to fueltype 'heat_fueltype'
                try:
                    service_fueltype_tech[lu_fueltypes['heat']][tech] += float(np.sum(fuel_tech))
                except KeyError:
                    service_fueltype_tech[lu_fueltypes['heat']][tech] = 0
                    service_fueltype_tech[lu_fueltypes['heat']][tech] += float(np.sum(fuel_tech))
    else:
        """Unconstrained version
        """
        service_fueltype_tech = init.service_type_tech_by_p(lu_fueltypes, fuel_tech_p_by)

        # Calulate share of energy service per tech depending on fuel and efficiencies
        for fueltype, tech_list in fuel_tech_p_by.items():
            for tech, fuel_share in tech_list.items():
                tech_eff = tech_stock.get_tech_attr(enduse, tech, 'eff_by')

                # Calculate fuel share and convert fuel to service
                service_tech_y = fuel_new_y[fueltype] * fuel_share * tech_eff

                service_tech[tech] += service_tech_y

                # Add fuel for each technology (float() is necessary to avoid inf error)
                service_fueltype_tech[fueltype][tech] += service_tech_y

                # Sum total yearly service
                tot_service_y += service_tech_y #(y)

    # Convert service of every technology to fraction of total service
    service_tech_p = convert_service_to_p(tot_service_y, service_fueltype_tech)

    # Convert service per technology to share of service within fueltype
    service_fueltype_tech_p = convert_service_tech_to_p(service_fueltype_tech)

    # Calculate service fraction per fueltype
    service_fueltype_p = {
        fueltype: sum(service.values()) for fueltype, service in service_fueltype_tech_p.items()}

    return tot_service_y, service_tech, service_tech_p, service_fueltype_tech_p, service_fueltype_p

def apply_heat_recovery(enduse, assumptions, service, crit_dict, base_sim_param):
    """Reduce heating demand according to assumption on heat reuse

    Arguments
    ----------
    assumptions : dict
        Assumptions
    service : dict or array
        Service of current year
    crit_dict : str
        Criteria to run function differently
    base_sim_param : dict
        Base simulation parameters

    Returns
    -------
    service_reduced : dict or array
        Reduced service after assumption on reuse

    Note
    ----
    A standard sigmoid diffusion is assumed from base year to end year
    """
    if enduse in assumptions['heat_recovered']:

        # Fraction of heat recovered until end_year
        heat_recovered_p_by = assumptions['heat_recovered'][enduse]

        if heat_recovered_p_by == 0:
            return service
        else:
            # Fraction of heat recovered in current year
            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                base_sim_param['base_yr'],
                base_sim_param['curr_yr'],
                base_sim_param['end_yr'],
                assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness']
            )

            heat_recovered_p_cy = sig_diff_factor * heat_recovered_p_by

            # Apply to technologies each stored in dictionary
            if crit_dict == 'service_tech':
                service_reduced = {}
                for tech, service_tech in service.items():
                    service_reduced[tech] = service_tech * (1.0 - heat_recovered_p_cy)

            # Apply to array
            elif crit_dict == 'tot_service_y_cy':
                service_reduced = service * (1.0 - heat_recovered_p_cy)

            return service_reduced
    else:
        return service

def apply_scenario_drivers(
        enduse,
        fuel_y,
        dw_stock,
        region_name,
        gva,
        population,
        reg_scen_drivers,
        base_sim_param
    ):
    """The fuel data for every end use are multiplied with respective scenario driver

    Arguments
    ----------
    enduse: str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    dw_stock : object
        Dwelling stock
    region_name : str
        Region name
    data : dict
        Data container
    reg_scen_drivers : dict
        Scenario drivers per enduse
    base_sim_param : dict
        Base simulation parameters

    Returns
    -------
    fuel_y : array
        Changed yearly fuel per fueltype

    Note
    -----
    - If no dwelling specific scenario driver is found, the identical fuel is returned.

        TODO
    """
    if reg_scen_drivers is None:
        reg_scen_drivers = {}

    base_yr = base_sim_param['base_yr']
    curr_yr = base_sim_param['curr_yr']

    if not dw_stock:
        """Calculate non-dwelling related scenario drivers, if no dwelling stock
        Info: No dwelling stock is defined for this submodel
        """
        scenario_drivers = reg_scen_drivers[enduse]

        by_driver, cy_driver = 1, 1 #not 0

        for scenario_driver in scenario_drivers:

            # Get correct data depending on driver
            if scenario_driver == 'gva':
                by_driver_data = gva[base_yr][region_name]
                cy_driver_data = gva[curr_yr][region_name]
            elif scenario_driver == 'population':
                by_driver_data = population[base_yr][region_name]
                cy_driver_data = population[curr_yr][region_name]
            #TODO :ADD OTHER ENDSES

            # Multiply drivers
            by_driver *= by_driver_data
            cy_driver *= cy_driver_data
        try:
            factor_driver = cy_driver / by_driver # FROZEN (as in chapter 3.1.2 EQ E-2)
        except ZeroDivisionError:
            factor_driver = 1

        fuel_y = fuel_y * factor_driver
    else:
        # Test if enduse has a dwelling related scenario driver
        if hasattr(dw_stock[region_name][base_yr], enduse) and curr_yr != base_yr:

            # Scenariodriver of dwelling stock base year and new stock
            by_driver = getattr(dw_stock[region_name][base_yr], enduse)
            cy_driver = getattr(dw_stock[region_name][curr_yr], enduse)

            # base year / current (checked) (as in chapter 3.1.2 EQ E-2)
            try:
                factor_driver = cy_driver / by_driver # FROZEN
            except ZeroDivisionError:
                factor_driver = 1

            fuel_y = fuel_y * factor_driver
        else:
            pass #enduse not define with scenario drivers

    return fuel_y

def apply_specific_change(
        enduse,
        fuel_y,
        assumptions,
        enduse_overall_change_ey,
        base_parameters
    ):
    """Calculates fuel based on assumed overall enduse specific fuel consumption changes

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    assumptions : dict
        Assumptions
    enduse_overall_change_ey : dict
        Assumption of overall change in end year

    base_parameters : dict
        Base simulation parameters

    Returns
    -------
    fuel_y : array
        Yearly new fuels

    Note
    -----
    -   Because for enduses where no technology stock is defined (and may
        consist of many different) technologies, a linear diffusion is
        suggested to best represent multiple sigmoid efficiency improvements
        of individual technologies.

    -   The changes are assumed across all fueltypes.

    -   Either a sigmoid standard diffusion or linear diffusion can be implemented.
        inear is suggested.
    """
    # Fuel consumption shares in base and end year
    percent_by = 1.0
    percent_ey = enduse_overall_change_ey[enduse]

    # Share of fuel consumption difference
    diff_fuel_consump = percent_ey - percent_by
    diffusion_choice = assumptions['other_enduse_mode_info']['diff_method']

    if diff_fuel_consump != 0: # If change in fuel consumption

        # Lineare diffusion up to cy
        if diffusion_choice == 'linear':
            lin_diff_factor = diffusion_technologies.linear_diff(
                base_parameters['base_yr'],
                base_parameters['curr_yr'],
                percent_by,
                percent_ey,
                base_parameters['sim_period_yrs'])
            change_cy = lin_diff_factor

        # Sigmoid diffusion up to cy
        elif diffusion_choice == 'sigmoid':
            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                base_parameters['base_yr'],
                base_parameters['curr_yr'],
                base_parameters['end_yr'],
                assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness'])
            change_cy = diff_fuel_consump * sig_diff_factor

        return fuel_y * change_cy
    else:
        return fuel_y

def apply_climate_change(enduse, fuel_new_y, cooling_factor_y, heating_factor_y, assumptions):
    """Change fuel demand for heat and cooling service
    depending on changes in HDD and CDD within a region
    (e.g. climate change induced)

    Paramters
    ---------
    enduse : str
        Enduse
    fuel_new_y : array
        Yearly fuel per fueltype
    cooling_factor_y : array
        Distribution of fuel within year to days (yd)
    heating_factor_y : array
        Distribution of fuel within year to days (yd)
    assumptions : dict
        Assumptions

    Return
    ------
    fuel_new_y : array
        Changed yearly fuel per fueltype

    Note
    ----
    - `cooling_factor_y` and `heating_factor_y` are based on the sum
        over the year. Therefore it is assumed that fuel correlates
        directly with HDD or CDD.
    """
    if enduse in assumptions['enduse_space_heating']:
        fuel_new_y = fuel_new_y * heating_factor_y
    elif enduse in assumptions['enduse_space_cooling']:
        fuel_new_y = fuel_new_y * cooling_factor_y

    return fuel_new_y

def apply_smart_metering(enduse, fuel_y, assumptions, base_sim_param):
    """Calculate fuel savings depending on smart meter penetration

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    assumptions : dict
        assumptions
    base_sim_param : dict
        Base simulation parameters

    Returns
    -------
    fuel_y : array
        New fuel per year

    Note
    -----
    - The smart meter penetration is assumed with a sigmoid diffusion.

    - In the assumptions the maximum penetration and also the
        generally fuel savings for each enduse can be defined.
    """
    if enduse in assumptions['savings_smart_meter']:

        # Sigmoid diffusion up to current year
        sigm_factor = diffusion_technologies.sigmoid_diffusion(
            base_sim_param['base_yr'],
            base_sim_param['curr_yr'],
            base_sim_param['end_yr'],
            assumptions['smart_meter_diff_params']['sig_midpoint'],
            assumptions['smart_meter_diff_params']['sig_steeppness']
            )

        # Smart Meter penetration (percentage of people having smart meters)
        penetration_by = assumptions['smart_meter_p_by']
        penetration_cy = assumptions['smart_meter_p_by'] + (
            sigm_factor * (assumptions['smart_meter_p_ey'] - assumptions['smart_meter_p_by']))

        savings = assumptions['savings_smart_meter'][enduse]
        saved_fuel = fuel_y * (penetration_by - penetration_cy) * savings
        fuel_y = fuel_y - saved_fuel

    return fuel_y

def service_switch(
        enduse,
        tot_service_yh_cy,
        service_tech_by_p,
        tech_increase_service,
        tech_decrease_service,
        tech_constant_service,
        sig_param_tech,
        curr_yr
    ):
    """Apply change in service depending on
    defined service switches.

    Paramters
    ---------
    tot_service_yh_cy : array
        Hourly service of all technologies
    service_tech_by_p : dict
        Fraction of service per technology
    tech_increase_service : dict
        Technologies with increased service
    tech_decrease_service : dict
        Technologies with decreased service
    tech_constant_service : dict
        Technologies with constant service
    sig_param_tech : dict
        Sigmoid diffusion parameters
    curr_yr : int
        Current year

    Returns
    -------
    service_tech_yh_cy : dict
        Service per technology in current year after switch
        for every hour in a year

    Note
    ----
    The service which is fulfilled by new technologies is
    substracted of the replaced technologies proportionally
    to the base year distribution of these technologies
    """
    # Result dict with cy service for every technology
    service_tech_cy_p = {}

    # ------------
    # Update all technologies with constant service
    # ------------
    service_tech_cy_p.update(tech_constant_service)

    # ------------
    # Calculate service for technology with increased service
    # ------------
    service_tech_incr_cy_p = get_service_diffusion(
        enduse,
        tech_increase_service,
        sig_param_tech,
        curr_yr)
    service_tech_cy_p.update(service_tech_incr_cy_p)

    # ------------
    # Calculate service for technologies with decreasing service
    # ------------
    # Add base year of decreasing technologies to substract from that later on
    for tech in tech_decrease_service:
        service_tech_cy_p[tech] = service_tech_by_p[tech]

    # Calculate service share to assing for substracted fuel
    service_tech_decrease_by_rel = fuel_service_switch.get_service_rel_tech_decr_by(
        tech_decrease_service,
        service_tech_by_p)

    # Calculated gained service and substract this proportionally
    # along all decreasing technologies
    for tech_incr, service_tech_incr_cy in service_tech_incr_cy_p.items():

        # Difference in service up to current year per technology
        diff_service_incr = service_tech_incr_cy - service_tech_by_p[tech_incr]

        # Substract service gain proportionaly to all technologies which are
        # lowered and substract from other technologies
        for tech_decr, service_tech_decr_by in service_tech_decrease_by_rel.items():
            service_to_substract_p_cy = service_tech_decr_by * diff_service_incr

            # TODO: Leave away for speed uproses
            ##assert (service_tech_cy_p[tech_decr] - service_to_substract_p_cy) >= 0
            service_tech_cy_p[tech_decr] -= service_to_substract_p_cy

    # Assign total service share to service share of technologies
    service_tech_yh_cy = {}
    for tech, enduse_share in service_tech_cy_p.items():
        service_tech_yh_cy[tech] = tot_service_yh_cy * enduse_share

    return service_tech_yh_cy

def fuel_switch(
        enduse,
        installed_tech,
        sig_param_tech,
        tot_service_yh_cy,
        service_tech,
        service_fueltype_tech_cy_p,
        service_fueltype_cy_p,
        fuel_switches,
        fuel_tech_p_by,
        curr_yr
    ):
    """Calulation of service by considering fuel switch assumptions.
    Based on  assumptions about shares of fuels which are switched
    per enduse to specific technologies, the installed technologies
    are used to calculate the new service demand after switching
    fuel shares.

    Arguments
    ----------
    enduse : str
        Enduse
    installed_tech : dict
        Technologies installed
    sig_param_tech : dict
        Sigmoid diffusion parameters
    tot_service_yh_cy : dict
        Total regional service for every hour for base year
    service_tech : dict
        Service for every fueltype and technology
    service_fueltype_tech_cy_p : dict
        Fraction of service per fueltype, technology for current year
    service_fueltype_cy_p : dict
        Fraction of service per fueltype in current year
    fuel_switches : dict
        Fuel switches
    fuel_tech_p_by : dict
        Fuel tech assumtions in base year
    curr_yr : int
        Current year

    Returns
    -------
    service_tech_switched : dict
        Containing all service for each technology on a hourly basis

    """
    # Must be like this, otherwise error
    service_tech_switched = service_tech # copy.copy(service_tech)

    # Iterate all technologies installed in fuel switches
    for tech_installed in installed_tech:

        # ---------------------------------------------------
        # Calculate service for cy for installed technologies
        # ---------------------------------------------------
        diffusion_cy = diffusion_technologies.sigmoid_function(
            curr_yr,
            sig_param_tech[enduse][tech_installed]['l_parameter'],
            sig_param_tech[enduse][tech_installed]['midpoint'],
            sig_param_tech[enduse][tech_installed]['steepness'])

        # Calculate service increase based on diffusion of installed technology
        service_tech_installed_cy = diffusion_cy * tot_service_yh_cy
        additional_service_tech_inst = service_tech_installed_cy - service_tech[tech_installed]

        service_tech_switched[tech_installed] = service_tech_installed_cy

        # ------------------------------------------------------------
        # Substrat replaced service demand proportinally
        # to fuel shares in base year
        # ------------------------------------------------------------
        fueltypes_replaced = []
        tot_service_tech_instal_p = 0 # Total replaced service across different fueltypes

        # Get shares of fuel which are switched with the installed technology
        for switch in fuel_switches:
            if switch['enduse'] == enduse and switch['technology_install']:
                fueltype_to_replace = switch['enduse_fueltype_replace']

                # Add replaced fueltype
                fueltypes_replaced.append(fueltype_to_replace)

                # Share of service demand per fueltype * fraction of fuel switched
                tot_service_tech_instal_p += service_fueltype_cy_p[fueltype_to_replace] * switch['share_fuel_consumption_switched']

        # Get fueltypes affected by installed technology
        for fueltype in fueltypes_replaced:

            # Get all technologies of the replaced fueltype
            technologies_replaced_fueltype = fuel_tech_p_by[fueltype].keys()

            # Find fuel switch where this fueltype is replaced
            for switch in fuel_switches:
                if (switch['enduse'] == enduse and
                    switch['technology_install'] == tech_installed and
                    switch['enduse_fueltype_replace'] == fueltype):

                    # Service reduced for this fueltype
                    # (service technology cy sigmoid diff *  % of heat demand within fueltype)
                    if tot_service_tech_instal_p == 0:
                        reduction_service_fueltype = 0
                    else:
                        # share of total service of fueltype * share of replaced fuel
                        service_fueltype_tech_cy_p_rel = service_fueltype_cy_p[fueltype] * switch['share_fuel_consumption_switched'] / tot_service_tech_instal_p

                        reduction_service_fueltype = additional_service_tech_inst * service_fueltype_tech_cy_p_rel
                    break

            # ------------------------------------------
            # Iterate all technologies in within the fueltype
            # and calculate reduction per technology
            # ------------------------------------------
            for tech_replaced in technologies_replaced_fueltype:
                logging.debug("technology_replaced: " + str(tech_replaced))

                # Share of heat demand for technology in fueltype
                # (share of heat demand within fueltype * reduction in servide demand)
                service_demand_tech = service_fueltype_tech_cy_p[fueltype][tech_replaced] * reduction_service_fueltype

                # -------
                # Substract technology specific service
                # -------
                service_tech_switched[tech_replaced] -= service_demand_tech
                #assert np.sum(service_tech[tech_replaced] - service_demand_tech) >= 0

    return service_tech_switched

def convert_service_tech_to_p(service):
    """Convert service per technology to share of service
    within fueltype (per fueltype sum == 1.0)

    Arguments
    ---------
    service : dict
        Service per fueltype and technology

    Returns
    -------
    out_dict : dict
        Service as a percentage of each technology per fueltype
    """
    out_dict = defaultdict(dict)

    for fueltype, service_fueltype in service.items():

        if service_fueltype == {}:
            continue
        else:
            # Sum of all service in enduse
            tot_service_per_fueltype = float(sum(service_fueltype.values()))

            for tech, service_fueltype_tech in service_fueltype.items():
                service_fueltype_tech = float(service_fueltype_tech)

                if service_fueltype_tech == 0:
                    out_dict[fueltype][tech] = 0
                elif tot_service_per_fueltype == 0:
                    out_dict[fueltype][tech] = 0
                else:
                    out_dict[fueltype][tech] = service_fueltype_tech / tot_service_per_fueltype

    return out_dict

def convert_service_to_p(tot_service_y, service_fueltype_tech):
    """Calculate fraction of service for every technology
    of total service

    Arguments
    ----------
    tot_service_y : float
        Total yearly service
    service_fueltype_tech : dict
        Service per technology and fueltype

    Returns
    -------
    service_tech_p : dict
        All tecnology services are
        provided as a fraction of total service

    Note
    ----
    Iterate over values in dict and apply calculations
    """
    if tot_service_y == 0:
        _total_service = 0
    else:
        _total_service = 1 / tot_service_y

    # Iterate all technologies and calculate fraction of total service
    service_tech_p = {}
    for tech_services in service_fueltype_tech.values():
        for tech, service_tech in tech_services.items():
            service_tech_p[tech] = _total_service * service_tech

    return service_tech_p

def get_service_diffusion(enduse, tech_increased_service, sig_param_tech, curr_yr):
    """Calculate energy service fraction of technologies with increased service
    for current year based on sigmoid diffusion

    Arguments
    ----------
    enduse : str
        Enduse
    tech_increased_service : dict
        All technologies per enduse with increased future service share
    sig_param_tech : dict
        Sigmoid diffusion parameters
    curr_yr : dict
        Current year

    Returns
    -------
    service_tech : dict
        Share of service per technology of current year
    """
    service_tech = {}

    for tech in tech_increased_service:
        service_tech[tech] = diffusion_technologies.sigmoid_function(
            curr_yr,
            sig_param_tech[enduse][tech]['l_parameter'],
            sig_param_tech[enduse][tech]['midpoint'],
            sig_param_tech[enduse][tech]['steepness'])

    return service_tech
