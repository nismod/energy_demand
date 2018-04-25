"""Contains the `Enduse` Class. This is the most important class
where the change in enduse specific energy demand is simulated
depending on scenaric assumptions."""
import logging
import math
import numpy as np
from energy_demand.profiles import load_profile as lp
from energy_demand.profiles import load_factors as lf
from energy_demand.technologies import diffusion_technologies
from energy_demand.technologies import fuel_service_switch
from energy_demand.technologies import tech_related
from energy_demand.basic import lookup_tables

class Enduse(object):
    """Enduse Class for all endueses in each SubModel

    For every region and sector, a different instance
    is generated. In this class, first the change in
    energy demand is calculated on a annual temporal scale.
    Calculations are performed in a cascade (e.g. first
    reducing climate change induced savings, then substracting
    further behavioral savings etc.). After annual calculations,
    the demand is converted to hourly demand.

    Also within this function, the fuel inputs are converted
    to energy service (short: service) and converted back to
    fuels (e.g. electricit).

    Arguments
    ----------
    submodel : str
        Submodel
    region : str
        Region name
    scenario_data : dict
        Scenario data
    assumptions : dict
        Assumptions
    load_profiles : dict
        Load profile stock
    base_yr : int
        Base year
    curr_yr : int
        Current year
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
    fuel_fueltype_tech_p_by : dict
        Fuel tech assumtions in base year
    sig_param_tech : dict
        Sigmoid parameters
    enduse_overall_change : dict
        Assumptions related to overal change in endyear
    regional_lp_stock : object
        Load profile stock
    dw_stock : object,default=False
        Dwelling stock
    reg_scen_drivers : bool,default=None
        Scenario drivers per enduse
    flat_profile_crit : bool,default=False
        Criteria of enduse has a flat shape or not

    Note
    ----
    - Load profiles are assigned independently of the fueltype, i.e.
      the same profiles are assumed to hold true across different fueltypes

    - ``self.fuel_y`` is always overwritten
      in the cascade of calculations

    Warning
    -------
    Not all enduses have technologies assigned. Load peaks are derived
    from techstock in case technologies are defined. Otherwise enduse load
    profiles are used.
    """
    def __init__(
            self,
            submodel,
            region,
            scenario_data,
            assumptions,
            load_profiles,
            base_yr,
            curr_yr,
            enduse,
            sector,
            fuel,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            fuel_fueltype_tech_p_by,
            sig_param_tech,
            enduse_overall_change,
            criterias,
            strategy_variables,
            fueltypes_nr,
            fueltypes,
            model_yeardays_nrs,
            dw_stock=False,
            reg_scen_drivers=None,
            flat_profile_crit=False
        ):
        """Enduse class constructor
        """
        #logging.info(" =====Enduse: {}  Sector:  {}".format(enduse, sector))
        self.region = region
        self.enduse = enduse
        self.fuel_y = fuel
        self.flat_profile_crit = flat_profile_crit

        self.techs_fuel_yh = None

        if np.sum(fuel) == 0:
            #If enduse has no fuel return empty shapes
            self.flat_profile_crit = True
            self.fuel_y = fuel
            self.fuel_yh = 0
            self.enduse_techs = []
        else:

            # Get technologies of enduse
            self.enduse_techs = get_enduse_techs(fuel_fueltype_tech_p_by)

            # -------------------------------
            # Cascade of calculations on a yearly scale
            # --------------------------------
            # --Change fuel consumption based on climate change induced temperature differences
            _fuel_new_y = apply_climate_change(
                enduse,
                self.fuel_y,
                cooling_factor_y,
                heating_factor_y,
                assumptions.enduse_space_heating,
                assumptions.ss_enduse_space_cooling)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train B: " + str(np.sum(self.fuel_y)))

            # --Change fuel consumption based on smart meter induced general savings
            _fuel_new_y = apply_smart_metering(
                enduse,
                self.fuel_y,
                assumptions.smart_meter_assump,
                strategy_variables,
                base_yr,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train C: " + str(np.sum(self.fuel_y)))

            # --Enduse specific fuel consumption change in %
            _fuel_new_y = apply_specific_change(
                enduse,
                self.fuel_y,
                enduse_overall_change,
                strategy_variables,
                base_yr,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train D: " + str(np.sum(self.fuel_y)))

            # Calculate new fuel demands after scenario drivers
            _fuel_new_y = apply_scenario_drivers(
                submodel,
                enduse,
                sector,
                self.fuel_y,
                dw_stock,
                region,
                scenario_data['gva'],
                scenario_data['population'],
                scenario_data['industry_gva'],
                reg_scen_drivers,
                base_yr,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train E: " + str(np.sum(self.fuel_y)))

            # Apply cooling scenario variable
            _fuel_new_y = apply_cooling(
                enduse,
                self.fuel_y,
                strategy_variables,
                assumptions.cooled_ss_floorarea_by,
                enduse_overall_change['other_enduse_mode_info'],
                base_yr,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train E1: " + str(np.sum(self.fuel_y)))

            # Industry related change
            _fuel_new_y = industry_enduse_changes(
                enduse,
                sector,
                base_yr,
                curr_yr,
                strategy_variables,
                self.fuel_y,
                enduse_overall_change['other_enduse_mode_info'],
                assumptions)
            self.fuel_y = _fuel_new_y
            #logging.debug("... Fuel train E2: " + str(np.sum(self.fuel_y)))

            # ----------------------------------
            # Hourly Disaggregation
            # ----------------------------------
            if self.enduse_techs == []:
                """If no technologies are defined for an enduse, the load profiles
                are read from dummy shape, which show the load profiles of the whole enduse.
                No switches can be implemented and only overall change of enduse.
                """
                if flat_profile_crit:
                    self.fuel_y = self.fuel_y * model_yeardays_nrs / 365.0
                else:
                    self.fuel_yh = assign_lp_no_techs(
                        enduse,
                        sector,
                        load_profiles,
                        self.fuel_y)
            else:
                """If technologies are defined for an enduse
                """
                # ----
                # Get enduse specific configurations
                # ----
                mode_constrained = get_enduse_configuration(
                    criterias['mode_constrained'],
                    enduse,
                    assumptions.enduse_space_heating)

                #logging.debug("... Fuel train F2: " + str(np.sum(self.fuel_y)))
                # ------------------------------------
                # Calculate regional energy service
                # ------------------------------------
                s_tot_y_cy, s_tech_y_by = fuel_to_service(
                    enduse,
                    self.fuel_y,
                    fuel_fueltype_tech_p_by,
                    tech_stock,
                    fueltypes,
                    mode_constrained)

                # ------------------------------------
                # Reduction of service because of heat recovery
                # ------------------------------------
                s_tot_y_cy, s_tech_y_cy = apply_heat_recovery(
                    enduse,
                    strategy_variables,
                    assumptions.enduse_overall_change,
                    s_tot_y_cy,
                    s_tech_y_by,
                    base_yr,
                    curr_yr)

                # ------------------------------------
                # Reduction of service because of improvement in air leakeage
                # ------------------------------------
                s_tot_y_cy, s_tech_y_cy = apply_air_leakage(
                    enduse,
                    strategy_variables,
                    assumptions.enduse_overall_change,
                    s_tot_y_cy,
                    s_tech_y_cy,
                    base_yr,
                    curr_yr)

                # --------------------------------
                # Switches
                # Calculate services per technology for cy based on fitted parameters
                # --------------------------------
                s_tech_y_cy = calc_service_switch(
                    enduse,
                    s_tech_y_cy,
                    self.enduse_techs,
                    sig_param_tech,
                    curr_yr,
                    base_yr,
                    sector,
                    assumptions.crit_switch_happening)

                # -------------------------------------------
                # Convert annual service to fuel per fueltype
                # -------------------------------------------
                self.fuel_y, fuel_tech_y = service_to_fuel(
                    enduse,
                    s_tech_y_cy,
                    tech_stock,
                    fueltypes_nr,
                    fueltypes,
                    mode_constrained)
                #logging.debug("... Fuel train H: " + str(np.sum(self.fuel_y)))

                # Delete all technologies with no fuel assigned
                for tech, fuel_tech in fuel_tech_y.items():
                    if np.sum(fuel_tech) == 0:
                        self.enduse_techs.remove(tech)

                # ------------------------------------------
                # Assign load profiles
                # ------------------------------------------
                #logging.info("ENDUSE : {}   TECHS:  {}".format(enduse, self.enduse_techs))
                if self.flat_profile_crit:
                    pass
                else:
                    fuel_yh = calc_fuel_tech_yh(
                        enduse,
                        sector,
                        self.enduse_techs,
                        fuel_tech_y,
                        load_profiles,
                        fueltypes_nr,
                        fueltypes,
                        model_yeardays_nrs,
                        mode_constrained)

                    # --------------------------------------
                    # Demand Management
                    # ---------------------------------------
                    if mode_constrained:
                        self.techs_fuel_yh = {}

                        for tech in fuel_yh:
                            self.techs_fuel_yh[tech] = demand_management(
                                enduse,
                                base_yr,
                                curr_yr,
                                strategy_variables,
                                fuel_yh[tech],
                                mode_constrained=True)

                        self.fuel_yh = None
                    else:
                        self.fuel_yh = demand_management(
                            enduse,
                            base_yr,
                            curr_yr,
                            strategy_variables,
                            fuel_yh,
                            mode_constrained=False)

def demand_management(
        enduse,
        base_yr,
        curr_yr,
        strategy_variables,
        fuel_yh,
        mode_constrained
    ):
    """Demand management. This function shifts peak per of this enduse
    depending on peak shifting factors. So far only inter day load shifting

    Arguments
    ----------
    enduse : str
        Enduse
    base_yr : int
        Base year
    curr_yr : int
        Current year
    strategy_variables : dict
        Assumptions of strategy variables
    fuel_yh : array
        Fuel per hours
    enduse_techs : list
        Enduse specfic technologies
    sector : str
        Sector
    tech_stock : obj
        Technology stock
    load_profiles : obj
        Load profiles
    mode_constrained : bool
        Running mode
        If mode_constrained, always only one technology imported

    Returns
    -------
    fuel_yh : array
        Fuel of yh
    """
    # ------------------------------
    # Test if peak is shifted or not
    # ------------------------------
    try:
        # Get assumed load shift
        param_name = 'demand_management_improvement__{}'.format(enduse)

        if strategy_variables[param_name]['scenario_value'] == 0:

            # no load management
            peak_shift_crit = False
        else:
            # load management
            peak_shift_crit = True
    except KeyError:

        # no load management
        peak_shift_crit = False

    # ------------------------------
    # If peak shifting implemented, calculate new lp
    # ------------------------------
    if peak_shift_crit:

        # Calculate average for every day
        if mode_constrained:
            average_fuel_yd = np.average(fuel_yh, axis=1)
        else:
            average_fuel_yd = np.average(fuel_yh, axis=2)

        # Calculate load factors (only inter_day load shifting as for now)
        loadfactor_yd_cy = lf.calc_lf_d(
            fuel_yh, average_fuel_yd, mode_constrained)

        # Calculate current year load factors
        lf_improved_cy = calc_lf_improvement(
            strategy_variables[param_name]['scenario_value'],
            base_yr,
            curr_yr,
            loadfactor_yd_cy,
            strategy_variables['demand_management_yr_until_changed']['scenario_value'])

        fuel_yh = lf.peak_shaving_max_min(
            lf_improved_cy, average_fuel_yd, fuel_yh, mode_constrained)

    else: # no peak shifting
        pass

    return fuel_yh

def calc_lf_improvement(
        lf_improvement_ey,
        base_yr,
        curr_yr,
        loadfactor_yd_cy,
        yr_until_changed
    ):
    """Calculate load factor improvement depending on linear diffusion
    over time.

    Arguments
    ---------
    lf_improvement_ey : dict
        Load factor improvement until end year
    base_yr : int
        Base year
    curr_yr : int
        Current year
    loadfactor_yd_cy : float
        Yd Load factor of current year
    yr_until_changed : int
        Year until fully changed

    Returns
    -------
    lf_improved_cy : str
        Improved load factor of current year
    peak_shift_crit : bool
        True: Peak is shifted, False: Peak isn't shifed
    """
    # Calculate linear diffusion of improvement of load management
    lin_diff_factor = diffusion_technologies.linear_diff(
        base_yr, curr_yr, 0, 1, yr_until_changed)

    # Current year load factor improvement
    lf_improvement_cy = lf_improvement_ey * lin_diff_factor

    # Add load factor improvement to current year load factor
    lf_improved_cy = loadfactor_yd_cy + lf_improvement_cy

    # Where load factor larger than zero, set to 1
    lf_improved_cy[lf_improved_cy > 1] = 1

    return lf_improved_cy

def assign_lp_no_techs(enduse, sector, load_profiles, fuel_y):
    """Assign load profiles for an enduse which has no technologies defined

    Arguments
    ---------
    enduse : str
        Enduse
    sector : str
        Enduse
    load_profiles : obj
        Load profiles
    fuel_y : array
        Fuels

    Returns
    -------
    fuel_yh : array (fueltype, 365, 24)
        Fuel yh
    """
    # Load profile for all fueltypes
    load_profile = load_profiles.get_lp(
        enduse, sector, 'placeholder_tech', 'shape_yh')

    fuel_yh = load_profile[:np.newaxis] * fuel_y[:, np.newaxis, np.newaxis]

    return fuel_yh

def get_running_mode(enduse, mode_constrained, enduse_space_heating):
    """Checks which mode needs to be run for an enduse.

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
    if mode_constrained:
        return True
    elif not mode_constrained and enduse in enduse_space_heating:
        return False
    elif not mode_constrained and enduse not in enduse_space_heating:
        # All other not constrained enduses where technologies are defined
        # are run in 'constrained' mode (e.g. lighting)
        return True

def get_enduse_configuration(
        mode_constrained,
        enduse,
        enduse_space_heating,
    ):
    """Get enduse specific configuration

    Arguments
    ---------
    mode_constrained : bool
        Constrained mode criteria
    enduse : str
        Enduse
    enduse_space_heating : list
        All endueses classified as space heating
    base_yr, curr_yr : int
        Base, current, year
    """
    mode_constrained = get_running_mode(
        enduse,
        mode_constrained,
        enduse_space_heating)

    return mode_constrained

def round_down(num, divisor):
    """Round down
    """
    return num - (num%divisor)

def get_peak_day_all_fueltypes(fuel_yh):
    """Iterate yh and get day containing the hour
    with the largest demand (across all fueltypes).

    Arguments
    ---------
    fuel_yh : array (fueltype, 365, 24)
        Fuel for every yh (fueltypes, yh)

    Return
    ------
    peak_day_nr : int
        Day with most fuel or service across all fueltypes
    """
    fuel_8760 = fuel_yh.reshape(fuel_yh.shape[0], 8760)

    # Sum all fuel across all fueltypes for every hour in a year
    all_fueltypes_tot_h = np.sum(fuel_8760, axis=0)

    if np.sum(all_fueltypes_tot_h) == 0:
        logging.warning("No peak can be found because no fuel assigned")
        return 0
    else:

        # Get day with maximum hour
        peak_day_nr = round_down(np.argmax(all_fueltypes_tot_h) / 24, 1)

        return int(peak_day_nr)

def get_peak_day(fuel_yh):
    """Iterate an array with entries and get
    entry nr with hightest value

    Arguments
    ---------
    fuel_yh : array (hours)
        Fuel for every day

    Return
    ------
    peak_day_nr : int
        Day with most fuel or service
    """
    if np.sum(fuel_yh) == 0:
        logging.info("No peak can be found because no fuel assigned")
        # Return first entry of element (which is zero)
        return 0
    else:
        # Sum fuel within every hour for every day and get day with maximum fuel
        peak_day_nr = np.argmax(fuel_yh)

        return int(peak_day_nr)

def get_peak_day_single_fueltype(fuel_yh):
    """Iterate yh and get day with highes fuel for a single fueltype
    The day with most fuel is considered to
    be the peak day. Over the simulation period,
    the peak day may change date in a year.

    Arguments
    ---------
    fuel_yh : array (365, 24) or array (8760)
        Fuel for every yh (yh)

    Return
    ------
    peak_day_nr : int
        Day with most fuel or service
    peak_h : float
        Peak hour value
    """
    #import copy
    #fuel_yh_copy = copy.copy(fuel_yh)
    #fuel_yh_8760 = fuel_yh_copy.reshape(8760)
    fuel_yh_8760 = fuel_yh.reshape(8760)

    if np.sum(fuel_yh_8760) == 0:
        logging.info("No peak can be found because no fuel assigned")
        # Return first entry of element (which is zero)
        return 0, 0
    else:
        # Sum fuel within every hour for every day and get day with maximum fuel
        peak_day_nr = round_down(np.argmax(fuel_yh_8760) / 24, 1)

        peak_h = np.max(fuel_yh_8760)

        return int(peak_day_nr), peak_h

def get_enduse_techs(fuel_fueltype_tech_p_by):
    """Get all defined technologies of an enduse

    Arguments
    ----------
    fuel_fueltype_tech_p_by : dict
        Percentage of fuel per enduse per technology

    Return
    ------
    enduse_techs : list
        All technologies

    Note
    ----
    All technologies are read out, including those which
    are potentially defined in fuel or service switches.

    If for an enduse a dummy technology is defined,
    the technologies of an enduse are set to an empty
    list.

    Warning
    -------
    For every enduse technologes must either be defined
    for no fueltype or for all fueltypes
    """
    enduse_techs = []

    for tech_fueltype in fuel_fueltype_tech_p_by.values():
        if 'placeholder_tech' in tech_fueltype.keys():
            return []
        else:
            enduse_techs += tech_fueltype.keys()

    return list(set(enduse_techs))

def calc_fuel_tech_yh(
        enduse,
        sector,
        enduse_techs,
        fuel_tech_y,
        load_profiles,
        fueltypes_nr,
        fueltypes,
        model_yeardays_nrs,
        mode_constrained
    ):
    """Iterate fuels for each technology and assign shape yd and yh shape

    Arguments
    ----------
    fuel_tech_y : dict
        Fuel per technology in enduse
    tech_stock : object
        Technologies
    load_profiles : object
        Load profiles
    fueltypes_nr : dict
        Nr of fueltypes
    fueltypes : dict
        Fueltypes lookup
    mode_constrained : bool
        Mode criteria
    model_yeardays_nrs : int
        Number of modelled yeardays

    Return
    ------
    fuels_yh : array
        Fueltype storing hourly fuel for every fueltype (fueltype, model_yeardays_nrs, 24)
    """
    if mode_constrained:

        fuels_yh = {}
        for tech in enduse_techs:

            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            if model_yeardays_nrs != 365:
                load_profile = lp.abs_to_rel(load_profile)

            fuels_yh[tech] = fuel_tech_y[tech] * load_profile
    else:
        # --
        # Unconstrained mode, i.e. not technolog specific.
        # Store according to fueltype and heat
        # --
        fuels_yh = np.zeros((fueltypes_nr, model_yeardays_nrs, 24), dtype=float)

        for tech in enduse_techs:

            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            if model_yeardays_nrs != 365:
                load_profile = lp.abs_to_rel(load_profile)

            # If no fuel for this tech and not defined in enduse
            fuel_tech_yh = fuel_tech_y[tech] * load_profile

            fuels_yh[fueltypes['heat']] += fuel_tech_yh

    return fuels_yh

def service_to_fuel(
        enduse,
        service_tech,
        tech_stock,
        fueltypes_nr,
        fueltypes,
        mode_constrained
    ):
    """Convert yearly energy service to yearly fuel demand.
    For every technology the service is taken and converted
    to fuel based on efficiency of current year

    Arguments
    ------
    enduse : str
        Enduse
    service_tech : dict
        Service per fueltype and technology
    tech_stock : object
        Technological stock
    fueltypes_nr : int
        Number of fueltypes
    fueltypes : dict
        Fueltypes
    mode_constrained : bool
        Mode running criteria

    Returns
    -------
    fuel_y : array
        Fuel per fueltype
    fuel_per_tech : dict
        Fuel per technology

    Note
    -----
        - Fuel = Energy service / efficiency
    """
    fuel_tech_y = {}
    fuel_y = np.zeros((fueltypes_nr), dtype=float)

    if mode_constrained:
        for tech, service in service_tech.items():

            tech_eff = tech_stock.get_tech_attr(
                enduse, tech, 'eff_cy')
            fueltype_int = tech_stock.get_tech_attr(
                enduse, tech, 'fueltype_int')

            # Convert to fuel
            fuel_tech = service / tech_eff

            # Add fuel
            fuel_tech_y[tech] = fuel_tech

            fuel_y[fueltype_int] += fuel_tech
    else:
        for tech, fuel_tech in service_tech.items():

            fuel_y[fueltypes['heat']] += fuel_tech
            fuel_tech_y[tech] = fuel_tech

    return fuel_y, fuel_tech_y

def fuel_to_service(
        enduse,
        fuel_y,
        fuel_fueltype_tech_p_by,
        tech_stock,
        fueltypes,
        mode_constrained
    ):
    """Converts fuel to energy service. Calculate energy service
    of each technology based on assumptions about base year fuel
    shares of an enduse (`fuel_fueltype_tech_p_by`).

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Fuel per fueltype
    fuel_fueltype_tech_p_by : dict
        Fuel composition of base year for every fueltype for each
        enduse (assumtions for national scale)
    tech_stock : object
        Technology stock of region
    fueltypes : dict
        Fueltype look-up
    mode_constrained : bool
        Criteria about mode

    Return
    ------
    tot_s_y : array
        Total annual energy service per technology
    s_tech_y : dict
        Total annual energy service per technology

    Note
    -----
    -   Efficiency changes of technologis are considered.
    -   Energy service = fuel * efficiency
    -   This function can be run in two modes, depending on `mode_constrained`
    -   The base year efficiency is taken because the actual service can
        only be calculated with base year.
        Efficiencies are only considered if converting back to fuel
        The 'self.fuel_y' is taken because the actual
        service was reduced e.g. due to smart meters or temperatur changes
    """
    s_tech_y = {}
    s_tot_y = 0

    # Calculate share of service
    for fueltype_int, tech_list in fuel_fueltype_tech_p_by.items():

        # Get technologies to iterate
        if tech_list == {} and fuel_y[fueltype_int] == 0:   # No technology or fuel defined
            techs_with_fuel = {}
        elif tech_list == {} and fuel_y[fueltype_int] > 0:  # Fuel defined but no technologies
            fueltype_str = tech_related.get_fueltype_str(fueltypes, fueltype_int)
            placeholder_tech = 'placeholder_tech__{}'.format(fueltype_str)
            techs_with_fuel = {placeholder_tech: 1.0}
        else:
            techs_with_fuel = tech_list

        for tech, fuel_share in techs_with_fuel.items():

            if mode_constrained:
                """Constrained version
                """
                tech_eff = tech_stock.get_tech_attr(enduse, tech, 'eff_by')

                # Get fuel share and convert fuel to service per technology
                s_tech = fuel_y[fueltype_int] * fuel_share * tech_eff

                s_tech_y[tech] = s_tech

                # Sum total yearly service
                s_tot_y += s_tech #(y)
            else:
                """Unconstrained version
                efficiencies are not considered, because not technology
                specific service calculation
                """
                # Calculate fuel share
                fuel_tech = fuel_y[fueltype_int] * fuel_share

                s_tech_y[tech] = fuel_tech

                # Sum total yearly service
                s_tot_y += fuel_tech

    return s_tot_y, s_tech_y

def apply_heat_recovery(
        enduse,
        strategy_variables,
        enduse_overall_change,
        service,
        service_techs,
        base_yr,
        curr_yr
    ):
    """Reduce heating demand according to assumption on heat reuse

    Arguments
    ----------
    enduse : str
        Enduse
    strategy_variables : dict
        Strategy variables
    enduse_overall_change : dict
        Sigmoid diffusion info
    service : dict or array
        Service of current year
    crit_dict : str
        Criteria to run function differently
    base_yr : int
        Base year
    curr_yr : int
        Current year

    Returns
    -------
    service_reduced : dict or array
        Reduced service after assumption on reuse

    Note
    ----
    A standard sigmoid diffusion is assumed from base year to end year
    """
    try:
        # Fraction of heat recovered until end year
        heat_recovered_p = strategy_variables["heat_recoved__{}".format(enduse)]['scenario_value']

        if heat_recovered_p == 0:
            return service, service_techs
        else:
            # Fraction of heat recovered in current year
            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                base_yr,
                curr_yr,
                strategy_variables['heat_recovered_yr_until_changed']['scenario_value'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_steepness'])

            heat_recovered_p_cy = sig_diff_factor * heat_recovered_p

            # Apply to technologies each stored in dictionary
            service_reduced_techs = {}
            for tech, service_tech in service_techs.items():
                service_reduced_techs[tech] = service_tech * (1.0 - heat_recovered_p_cy)

            # Apply to array
            service_reduced = service * (1.0 - heat_recovered_p_cy)

            return service_reduced, service_reduced_techs
    except KeyError:
        # no recycling defined
        return service, service_techs

def apply_air_leakage(
        enduse,
        strategy_variables,
        enduse_overall_change,
        service,
        service_techs,
        base_yr,
        curr_yr
    ):
    """Reduce heating demand according to assumption on
    improvements in air leaking

    Arguments
    ----------
    enduse : str
        Enduse
    strategy_variables : dict
        Strategy variables
    enduse_overall_change : dict
        Sigmoid diffusion info
    service : dict or array
        Service of current year
    crit_dict : str
        Criteria to run function differently
    base_yr : int
        Base year
    curr_yr : int
        Current year

    Returns
    -------
    service_reduced : dict or array
        Service after assumptions on air leaking improvements

    Note
    ----
    A standard sigmoid diffusion is assumed from base year to end year
    """
    try:
        # Fraction of heat recovered until end year
        air_leakage_improvement = strategy_variables["air_leakage__{}".format(enduse)]['scenario_value']

        if air_leakage_improvement == 0:
            return service, service_techs
        else:
            air_leakage_by = 1

            # Fraction of heat recovered in current year
            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                base_yr,
                curr_yr,
                strategy_variables['air_leakage_yr_until_changed']['scenario_value'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_steepness'])

            air_leakage_improvement_cy = sig_diff_factor * air_leakage_improvement
            air_leakage_cy = 1 - air_leakage_improvement_cy

            f_improvement = air_leakage_cy / air_leakage_by

            # Apply to technologies each stored in dictionary or array
            service_reduced_techs = {}
            for tech, service_tech in service_techs.items():
                service_reduced_techs[tech] = service_tech * f_improvement

            service_reduced = service * f_improvement

            return service_reduced, service_reduced_techs
    except KeyError:
        return service, service_techs

def apply_scenario_drivers(
        submodel,
        enduse,
        sector,
        fuel_y,
        dw_stock,
        region,
        gva,
        population,
        industry_gva,
        reg_scen_drivers,
        base_yr,
        curr_yr
    ):
    """The fuel data for every end use are multiplied with respective
    scenario drivers. If no dwelling specific scenario driver is found,
    the identical fuel is returned.

    Arguments
    ----------
    enduse: str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    dw_stock : object
        Dwelling stock
    region : str
        Region name
    gva : dict
        GVA
    population : dict
        Population
    reg_scen_drivers : dict
        Scenario drivers per enduse
    base_yr : int
        Base year
    curr_yr : int
        Current year

    Returns
    -------
    fuel_y : array
        Changed yearly fuel per fueltype
    """
    if reg_scen_drivers is None:
        reg_scen_drivers = {}

    if not dw_stock:
        """Calculate non-dwelling related scenario drivers, if no dwelling stock
        Info: No dwelling stock is defined for this submodel
        """
        scenario_drivers = reg_scen_drivers[enduse]

        by_driver, cy_driver = 1, 1 #not 0

        for scenario_driver in scenario_drivers:

            # Get correct data depending on driver
            if scenario_driver == 'gva':
                by_driver_data = gva[base_yr][region]
                cy_driver_data = gva[curr_yr][region]

                '''if submodel == 'is_submodel':

                    # Map enduse to SIC letter
                    lu_industry_sic = lookup_tables.industrydemand_name_sic2007()
                    sic_letter = lu_industry_sic[sector][sic_2007_letter]

                    by_driver_data = industry_gva[base_yr][region][sic_lettersector]
                    cy_driver_data = industry_gva[curr_yr][region][sic_letter]
                else:

                    # Calculate overall GVA for all sectors TODO

                    by_driver_data = gva[base_yr][region]
                    cy_driver_data = gva[curr_yr][region]'''

            elif scenario_driver == 'population':
                by_driver_data = population[base_yr][region]
                cy_driver_data = population[curr_yr][region]
            #TODO :ADD OTHER ENDSES

            if math.isnan(by_driver_data):
                #logging.warning("INF ERROR")
                by_driver_data = 1
            if math.isnan(cy_driver_data):
                #logging.warning("INF ERROR")
                cy_driver_data = 1

            # Multiply drivers
            by_driver *= by_driver_data
            cy_driver *= cy_driver_data

        try:
            factor_driver = cy_driver / by_driver # FROZEN (as in chapter 3.1.2 EQ E-2)
        except ZeroDivisionError:
            factor_driver = 1

        if math.isnan(factor_driver):
            raise Exception("Error xcx")

        fuel_y = fuel_y * factor_driver
    else:
        """Scenario driver calculation based on dwelling stock
        """
        # Test if enduse has a dwelling related scenario driver
        if hasattr(dw_stock[base_yr], enduse) and curr_yr != base_yr:

            # Scenariodriver of dwelling stock base year and new stock
            by_driver = getattr(dw_stock[base_yr], enduse)
            cy_driver = getattr(dw_stock[curr_yr], enduse)
            #assert by_driver != 'nan' and assert cy_driver != 'nan'

            # base year / current (checked)
            try:
                factor_driver = cy_driver / by_driver
            except ZeroDivisionError:
                factor_driver = 1

            # Check if float('nan')
            if math.isnan(factor_driver):
                #logging.warning("Something went wrong wtih scenario")
                factor_driver = 1

            #logging.debug("... Scenario drivers: {} {} {}".format(by_driver, cy_driver, factor_driver))

            fuel_y = fuel_y * factor_driver
        else:
            pass #enduse not define with scenario drivers

    assert math.isnan(np.sum(fuel_y)) != 'nan' #SPEED ESTING

    return fuel_y

def apply_specific_change(
        enduse,
        fuel_y,
        enduse_overall_change,
        strategy_variables,
        base_yr,
        curr_yr
    ):
    """Calculates fuel based on assumed overall enduse specific
    fuel consumption changes.

    The changes are assumed across all fueltypes.
    Because for enduses where no technologies are defined, a linear
    diffusion is suggested to best represent multiple sigmoid efficiency
    improvements of individual technologies.

    Either a sigmoid standard diffusion or linear diffusion can be
    implemented. Linear is suggested.

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    enduse_overall_change : dict
        Info about how the enduse is overall changed (e.g. diff method)
    strategy_variables : dict
        Change in overall enduse for every enduse (percent ey)
    base_yr : int
        Base year
    curr_yr : int
        Current year

    Returns
    -------
    fuel_y : array
        Yearly new fuels
    """
    # Fuel consumption shares in base and end year
    percent_by = 1.0

    percent_ey = percent_by + strategy_variables['enduse_change__{}'.format(enduse)]['scenario_value']

    # Share of fuel consumption difference
    diff_fuel_consump = percent_ey - percent_by
    diffusion_choice = enduse_overall_change['other_enduse_mode_info']['diff_method']

    if diff_fuel_consump != 0: # If change in fuel consumption

        # Lineare diffusion up to cy
        if diffusion_choice == 'linear':
            lin_diff_factor = diffusion_technologies.linear_diff(
                base_yr,
                curr_yr,
                percent_by,
                percent_ey,
                strategy_variables['enduse_specific_change_yr_until_changed']['scenario_value'])
            change_cy = lin_diff_factor

        # Sigmoid diffusion up to cy
        elif diffusion_choice == 'sigmoid':
            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                base_yr,
                curr_yr,
                strategy_variables['enduse_specific_change_yr_until_changed']['scenario_value'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                enduse_overall_change['other_enduse_mode_info']['sigmoid']['sig_steepness'])
            change_cy = diff_fuel_consump * sig_diff_factor

        return fuel_y * change_cy
    else:
        return fuel_y

def apply_climate_change(
        enduse,
        fuel_y,
        cooling_factor_y,
        heating_factor_y,
        enduse_space_heating,
        enduse_space_cooling
    ):
    """Change fuel demand for heat and cooling service
    depending on changes in HDD and CDD within a region
    (e.g. climate change induced)

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    cooling_factor_y : array
        Distribution of fuel within year to days (yd)
    heating_factor_y : array
        Distribution of fuel within year to days (yd)
    enduse_space_heating : list
        Enduses defined as space heating
    enduse_space_cooling : list
        Enduses defined as space cooling

    Return
    ------
    fuel_y : array
        Changed yearly fuel per fueltype

    Note
    ----
    - `cooling_factor_y` and `heating_factor_y` are based on the sum
        over the year. Therefore it is assumed that fuel correlates
        directly with HDD or CDD.
    """
    if enduse in enduse_space_heating:
        fuel_y = fuel_y * heating_factor_y
    elif enduse in enduse_space_cooling:
        fuel_y = fuel_y * cooling_factor_y

    return fuel_y

def apply_smart_metering(
        enduse,
        fuel_y,
        sm_assump,
        strategy_variables,
        base_yr,
        curr_yr
    ):
    """Calculate fuel savings depending on smart meter penetration

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    sm_assump : dict
        smart meter assumptions
    strategy_variables : dict
        Base simulation parameters
    base_yr, curr_yr : int
        years

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
    try:

        enduse_savings = strategy_variables['smart_meter_improvement_{}'.format(enduse)]['scenario_value']

        # Sigmoid diffusion up to current year
        sigm_factor = diffusion_technologies.sigmoid_diffusion(
            base_yr,
            curr_yr,
            strategy_variables['smart_meter_yr_until_changed']['scenario_value'],
            sm_assump['smart_meter_diff_params']['sig_midpoint'],
            sm_assump['smart_meter_diff_params']['sig_steepness'])

        # Check if float
        assert isinstance(sigm_factor, float)

        # Improvement of smart meter penetration
        penetration_improvement = strategy_variables['smart_meter_improvement_p']['scenario_value']

        # Smart Meter penetration (percentage of people having smart meters)
        penetration_by = sm_assump['smart_meter_p_by']
        penetration_cy = sm_assump['smart_meter_p_by'] + sigm_factor * penetration_improvement

        saved_fuel = fuel_y * (penetration_cy - penetration_by) * enduse_savings
        fuel_y = fuel_y - saved_fuel

        return fuel_y

    except KeyError:
        # not defined for this enduse
        return fuel_y

def convert_service_to_p(tot_s_y, s_fueltype_tech):
    """Calculate fraction of service for every technology
    of total service

    Arguments
    ----------
    tot_s_y : float
        Total yearly service
    s_fueltype_tech : dict
        Service per technology and fueltype

    Returns
    -------
    s_tech_p : dict
        All tecnology services are
        provided as a fraction of total service

    Note
    ----
    Iterate over values in dict and apply calculations
    """
    if tot_s_y == 0:
        _total_service = 0
    else:
        _total_service = 1 / tot_s_y

    # Iterate all technologies and calculate fraction of total service
    s_tech_p = {}
    for tech_services in s_fueltype_tech.values():
        for tech, service_tech in tech_services.items():
            s_tech_p[tech] = _total_service * service_tech

    return s_tech_p

def get_service_diffusion(sig_param_tech, curr_yr):
    """Calculate energy service fraction of technologies with increased service
    for current year based on sigmoid diffusion

    Arguments
    ----------
    sig_param_tech : dict
        Sigmoid diffusion parameters per technology
    curr_yr : dict
        Current year

    Returns
    -------
    s_tech_p : dict
        Share of service per technology of current year
    """
    if sig_param_tech['l_parameter'] is None:
        s_tech_p = 0
    elif sig_param_tech['l_parameter'] == 'linear':
        s_tech_p = 'identical'
    else:
        s_tech_p = diffusion_technologies.sigmoid_function(
            curr_yr,
            sig_param_tech['l_parameter'],
            sig_param_tech['midpoint'],
            sig_param_tech['steepness'])

    return s_tech_p

def calc_service_switch(
        enduse,
        s_tech_y_cy,
        all_technologies,
        sig_param_tech,
        curr_yr,
        base_yr,
        sector,
        crit_switch_happening
    ):
    """Apply change in service depending on defined service switches.

    The service which is fulfilled by new technologies as defined
    in the service switches is substracted of the replaced
    technologies proportionally to the base year distribution
    of these technologies.

    Arguments
    ---------
    tot_s_yh_cy : array
        Hourly service of all technologies
    all_technologies : dict
        Technologies to iterate
    sig_param_tech : dict
        Sigmoid diffusion parameters
    curr_yr : int
        Current year

    Returns
    -------
    switched_s_tech_y_cy : dict
        Service per technology in current year after switch in a year
    """
    # ----------------------------------------
    # Test wheter switch is defined or not
    # ----------------------------------------
    crit_switch_service = fuel_service_switch.get_switch_criteria(
        enduse,
        sector,
        crit_switch_happening,
        base_yr,
        curr_yr)

    # ----------------------------------------
    # Calculate switch
    # ----------------------------------------
    if crit_switch_service:
        logging.info("SWITCH TRUE")

        switched_s_tech_y_cy = {}

        # Service of all technologies
        service_all_techs = sum(s_tech_y_cy.values())

        for tech in all_technologies:

            # Calculated service share per tech for cy with sigmoid parameters
            s_tech_cy_p = get_service_diffusion(
                sig_param_tech[tech], curr_yr)

            if tech == 'heat_pumps_electricity':
                logging.info("HEP SHARE: " + str(s_tech_cy_p))

            if s_tech_cy_p == 'identical':
                switched_s_tech_y_cy[tech] = s_tech_y_cy[tech]
            else:
                switched_s_tech_y_cy[tech] = service_all_techs * s_tech_cy_p

            assert switched_s_tech_y_cy[tech] >= 0

        return switched_s_tech_y_cy
    else:
        return s_tech_y_cy

def apply_cooling(
        enduse,
        fuel_y,
        strategy_variables,
        cooled_floorarea_p_by,
        other_enduse_mode_info,
        base_yr,
        curr_yr):
    """Apply changes for cooling enduses depending
    on assumption of how much of the floor area in percent
    is cooled

    It is aassumption a linear correlation between the
    percentage of cooled floor space (area) and energy demand.

    Arguments
    ---------
    enduse : str
        Enduse
    fuel_y : array
        Annual fuel demand
    strategy_variables : dict
        Strategy variables
    cooled_floorarea_p_by : dict
        Assumption about cooling floor area in base year
    other_enduse_mode_info : dict
        diffusion parameters
    base_yr : int
        Base year
    curr_yr : int
        Current year

    Returns
    -------
    fuel_y : array
        Fuel array (either changed fuel depending on cooling percentage)
        of identical array
    """
    try:

        # Floor area share cooled in end year
        cooled_floorearea_p_ey = cooled_floorarea_p_by + strategy_variables["cooled_floorarea__{}".format(enduse)]['scenario_value']

        # Fraction of heat recovered up to current year
        sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
            base_yr,
            curr_yr,
            strategy_variables['cooled_floorarea_yr_until_changed']['scenario_value'],
            other_enduse_mode_info['sigmoid']['sig_midpoint'],
            other_enduse_mode_info['sigmoid']['sig_steepness'])

        # Additionall floor area
        additional_floor_area_p = sig_diff_factor * (cooled_floorearea_p_ey - cooled_floorarea_p_by)

        cooled_floorarea_p_cy = cooled_floorarea_p_by + additional_floor_area_p

        # Calculate factor
        floorare_cooling_factor = cooled_floorarea_p_cy / cooled_floorarea_p_by

        # Apply factor
        fuel_y = fuel_y * floorare_cooling_factor
        return fuel_y

    except KeyError:
        # no cooling defined for enduse
        return fuel_y

def industry_enduse_changes(
        enduse,
        sector,
        base_yr,
        curr_yr,
        strategy_variables,
        fuels,
        other_enduse_mode_info,
        assumptions
    ):
    """This function changes the demand if the enduse
    is a an industrial enduse depending on assumed
    industry related scenario paramters

    Arguments
    ---------
    enduse : str
        Enduse
    sector : str
        Sector
    curr_yr : int
        Current year
    strategy_variables : dict
        All strategy variables
    fuels : array
        Annual fuels

    Returns
    --------
    fuels : np.array
        Changed fuels depending on scenario

    Info
    ----
    OLD MODEL TODO

    """
    factor = 1

    if enduse == "is_low_temp_process":

        # Diffusion of policy
        #cy_factor = by_value / cy_value / by_value
        #Multiply fuels
        #fuels = fuels * cy_factor

        '''
        Theoretical maximal potential for every sector
        --> improvement in % of every sector?


        '''
        pass
    elif enduse == 'is_high_temp_process':


        if sector == 'basic_metals':

            # Calculate factor depending on fraction of hot and cold steel rolling process
            factor = hot_cold_process(
                base_yr,
                curr_yr,
                strategy_variables,
                other_enduse_mode_info,
                assumptions)

        #elif sector == 'non_metallic_mineral_products':

        #    # Calculate factor depending on cement processes

    else:
        pass

    fuels_out = fuels * factor

    return fuels_out

def hot_cold_process(
        base_yr,
        curr_yr,
        strategy_variables,
        other_enduse_mode_info,
        assumptions
    ):
    """Calculate factor based on the fraction of hot
    and cold rolling processes in steel manufacturing.
    The fraction of either process is calculated based on
    the scenario input of the future share of cold rollling
    processes. A sigmoid diffusion towards this fucture defined
    fraction is implemented.

    Arguments
    ----------
    base_yr : int
        Base year
    curr_yr : int
        Current year
    strategy_variables : dict
        Strategy variables
    other_enduse_mode_info : dict
        Sigmoid diffusion parameters
    assumptions : dict
        Assumptions including efficiencies of either process
        and the base year share

    Returns
    -------
    factor : float
        Factor to change energy demand
    """

    # Reduce demand depending on fraction of hot and cold steel rolling process
    p_cold_rolling_by = assumptions.p_cold_rolling_steel_by
    p_hot_rolling_by = 1.0 - p_cold_rolling_by

    # Get sigmoid transition for share in rolling
    sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        strategy_variables['hot_cold_rolling_yr_until_changed']['scenario_value'],
        other_enduse_mode_info['sigmoid']['sig_midpoint'],
        other_enduse_mode_info['sigmoid']['sig_steepness'])

    # Difference p cold rolling
    diff_cold_rolling = strategy_variables['p_cold_rolling_steel']['scenario_value'] - p_cold_rolling_by

    # Difference until cy
    diff_cold_rolling_cy = sig_diff_factor * diff_cold_rolling

    # Calculate cy p
    p_cold_rolling_cy = p_cold_rolling_by + diff_cold_rolling_cy
    p_hot_rolling_cy = 1 - p_cold_rolling_cy

    # Calculate factor
    eff_cold = assumptions.eff_cold_rolling_process
    eff_hot = assumptions.eff_hot_rolling_process

    p_by = p_cold_rolling_by * eff_cold + p_hot_rolling_by * eff_hot
    p_cy = p_cold_rolling_cy * eff_cold  + p_hot_rolling_cy * eff_hot

    factor = p_cy  / p_by

    return factor
