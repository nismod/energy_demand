"""Contains the `Enduse` Class. This is the most important class
where the change in enduse specific energy demand is simulated
depending on scenaric assumptions"""
import logging
import math
import numpy as np

from energy_demand.profiles import load_factors as lf
from energy_demand.technologies import diffusion_technologies
from energy_demand.technologies import fuel_service_switch
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions
from energy_demand.basic import basic_functions
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
    fuel_tech_p_by : dict
        Fuel tech assumtions in base year
    regional_lp_stock : object
        Load profile stock
    dw_stock : object,default=False
        Dwelling stock
    reg_scen_drivers : bool,default=None
        Scenario drivers per enduse
    flat_profile_crit : bool,default=False
        Criteria of enduse has a flat shape or not
    make_all_flat : bool
        Crit to make everything flat

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
            submodel_name,
            region,
            scenario_data,
            assumptions,
            load_profiles,
            f_weather_correction,
            base_yr,
            curr_yr,
            enduse,
            sector,
            fuel,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            fuel_tech_p_by,
            criterias,
            strategy_vars,
            fueltypes_nr,
            fueltypes,
            dw_stock=False,
            reg_scen_drivers=None,
            flat_profile_crit=False,
            make_all_flat=False
        ):
        """Enduse class constructor
        """
        self.submodel_name = submodel_name
        self.region = region
        self.enduse = enduse
        self.fuel_y = fuel
        self.flat_profile_crit = flat_profile_crit
        self.techs_fuel_yh = None

        #If enduse has no fuel return empty shapes
        if np.sum(fuel) == 0:
            self.flat_profile_crit = True
            self.fuel_y = fuel
            self.fuel_yh = 0
            self.enduse_techs = []
        else:
            #print("------INFO  {} {} {}  {}".format(self.enduse, sector, region, curr_yr))
            #print("FUEL TRAIN A0: " + str(np.sum(self.fuel_y)))

            # Get technologies of enduse
            self.enduse_techs = get_enduse_techs(fuel_tech_p_by)

            # -----------------------------
            # Cascade of annual calculations
            # -----------------------------
            _fuel_new_y = apply_weather_correction(
                enduse,
                self.fuel_y,
                cooling_factor_y,
                heating_factor_y,
                assumptions.enduse_space_heating,
                assumptions.ss_enduse_space_cooling,
                f_weather_correction)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN B0: " + str(np.sum(self.fuel_y)))

            _fuel_new_y = apply_smart_metering(
                enduse,
                self.fuel_y,
                assumptions.smart_meter_assump,
                strategy_vars,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN C0: " + str(np.sum(self.fuel_y)))

            _fuel_new_y = generic_demand_change(
                enduse,
                sector,
                self.fuel_y,
                strategy_vars['generic_enduse_change'],
                curr_yr)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN D0: " + str(np.sum(self.fuel_y)))

            _fuel_new_y = apply_scenario_drivers(
                enduse=enduse,
                sector=sector,
                fuel_y=self.fuel_y,
                dw_stock=dw_stock,
                region=region,
                gva_industry=scenario_data['gva_industry'],
                gva_per_head=scenario_data['gva_per_head'],
                population=scenario_data['population'],
                reg_scen_drivers=reg_scen_drivers,
                base_yr=base_yr,
                curr_yr=curr_yr)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN E0: " + str(np.sum(self.fuel_y)))

            # Apply cooling scenario variable
            _fuel_new_y = apply_cooling(
                enduse,
                self.fuel_y,
                strategy_vars['cooled_floorarea'],
                assumptions.cooled_ss_floorarea_by,
                curr_yr)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN E1: " + str(np.sum(self.fuel_y)))

            # Industry related change
            _fuel_new_y = industry_enduse_changes(
                enduse,
                sector,
                curr_yr,
                strategy_vars,
                self.fuel_y,
                assumptions)
            self.fuel_y = _fuel_new_y
            #print("FUEL TRAIN E2: " + str(np.sum(self.fuel_y)))

            # Generic fuel switch of an enduse and sector
            _fuel_new_y = generic_fuel_switch(
                enduse,
                sector,
                curr_yr,
                strategy_vars['generic_fuel_switch'],
                self.fuel_y)
            self.fuel_y = _fuel_new_y

            # ----------------------------------
            # Hourly Disaggregation
            # ----------------------------------
            if self.enduse_techs == []:
                # If no technologies are defined for an enduse, the load profiles
                # are read from dummy shape, which show the load profiles of the whole enduse.
                # No switches can be implemented and only overall change of enduse
                if flat_profile_crit:
                    pass
                else:
                    fuel_yh = assign_lp_no_techs(
                        enduse,
                        sector,
                        load_profiles,
                        self.fuel_y,
                        make_all_flat=make_all_flat)

                    #print("FUEL TRAIN X " + str(np.sum(fuel_yh)))
                    # Demand management for non-technology enduse
                    self.fuel_yh = demand_management(
                        enduse,
                        curr_yr,
                        strategy_vars['dm_improvement'],
                        fuel_yh,
                        mode_constrained=False,
                        make_all_flat=make_all_flat)
                    #print("FUEL TRAIN Y" + str(np.sum(fuel_yh)))

                    #assert not testing_functions.test_if_minus_value_in_array(self.fuel_yh)
            else:
                #If technologies are defined for an enduse

                # Get enduse specific configurations
                mode_constrained = get_enduse_configuration(
                    criterias['mode_constrained'],
                    enduse,
                    assumptions.enduse_space_heating)

                # ------------------------------------
                # Calculate regional energy service
                # ------------------------------------
                s_tot_y_cy, s_tech_y_by = fuel_to_service(
                    enduse,
                    sector,
                    self.fuel_y,
                    fuel_tech_p_by,
                    tech_stock,
                    fueltypes,
                    mode_constrained)

                # ------------------------------------
                # Reduction of service because of heat recovery
                # ------------------------------------
                s_tot_y_cy, s_tech_y_cy = apply_heat_recovery(
                    enduse,
                    strategy_vars['heat_recovered'],
                    s_tot_y_cy,
                    s_tech_y_by,
                    curr_yr)

                # ------------------------------------
                # Reduction of service because of improvement in air leakeage
                # ------------------------------------
                s_tot_y_cy, s_tech_y_cy = apply_air_leakage(
                    enduse,
                    strategy_vars['air_leakage'],
                    s_tot_y_cy,
                    s_tech_y_cy,
                    curr_yr)

                # --------------------------------
                # Switches
                # --------------------------------
                s_tech_y_cy = apply_service_switch(
                    enduse=enduse,
                    s_tech_y_cy=s_tech_y_cy,
                    all_technologies=self.enduse_techs,
                    curr_yr=curr_yr,
                    base_yr=base_yr,
                    sector=sector,
                    annual_tech_diff_params=strategy_vars['annual_tech_diff_params'],
                    crit_switch_happening=assumptions.crit_switch_happening)

                # -------------------------------------------
                # Convert annual service to fuel per fueltype
                # -------------------------------------------
                self.fuel_y, fuel_tech_y = service_to_fuel(
                    enduse,
                    sector,
                    s_tech_y_cy,
                    tech_stock,
                    fueltypes_nr,
                    fueltypes,
                    mode_constrained)

                # Delete all technologies with no fuel assigned
                for tech, fuel_tech in fuel_tech_y.items():
                    if np.sum(fuel_tech) == 0:
                        self.enduse_techs.remove(tech)

                # ------------------------------------------
                # Assign load profiles
                # ------------------------------------------
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
                        mode_constrained)

                    # --------------------------------------
                    # Demand Management
                    # --------------------------------------
                    if mode_constrained:
                        self.techs_fuel_yh = {}

                        for tech in fuel_yh:
                            self.techs_fuel_yh[tech] = demand_management(
                                enduse,
                                curr_yr,
                                strategy_vars['dm_improvement'],
                                fuel_yh[tech],
                                mode_constrained=True,
                                make_all_flat=make_all_flat)

                        self.fuel_yh = None
                    else:
                        self.fuel_yh = demand_management(
                            enduse,
                            curr_yr,
                            strategy_vars['dm_improvement'],
                            fuel_yh,
                            mode_constrained=False,
                            make_all_flat=make_all_flat)

                         #assert not testing_functions.test_if_minus_value_in_array(self.fuel_yh)

def demand_management(
        enduse,
        curr_yr,
        dm_improvement,
        fuel_yh,
        mode_constrained,
        make_all_flat=False
    ):
    """This function shifts peak per of this enduse
    depending on peak shifting factors.
    So far only inter day load shifting

    Arguments
    ----------
    enduse : str
        Enduse
    curr_yr : int
        Current year
    dm_improvement : dict
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
    make_all_flat : bool
        If true, all shapes are flat

    Returns
    -------
    fuel_yh : array
        Fuel of yh
    """

    # Get assumed load shift
    if dm_improvement[enduse][curr_yr] == 0:
        pass # no load management
    else:
        # Calculate average for every day
        if mode_constrained:
            average_fuel_yd = np.average(fuel_yh, axis=1)
        else:
            average_fuel_yd = np.average(fuel_yh, axis=2)

        # Calculate load factors (only inter_day load shifting as for now)
        loadfactor_yd_cy = lf.calc_lf_d(
            fuel_yh, average_fuel_yd, mode_constrained)

        # Load factor improvement parameter in current year
        param_lf_improved_cy = dm_improvement[enduse][curr_yr]

        # Calculate current year load factors
        lf_improved_cy = calc_lf_improvement(
            param_lf_improved_cy,
            loadfactor_yd_cy,)

        fuel_yh = lf.peak_shaving_max_min(
            lf_improved_cy,
            average_fuel_yd,
            fuel_yh,
            mode_constrained)

    # -------------------------------------------------
    # Convert all load profiles into flat load profiles
    # -------------------------------------------------
    if make_all_flat:
        if mode_constrained:
            sum_fueltypes_days = np.sum(fuel_yh)                 #sum over all hours
            average_fueltype = sum_fueltypes_days / 8760         # Average
            fuel_yh_empty = np.ones((fuel_yh.shape))
            fuel_yh = fuel_yh_empty * average_fueltype
        else:
            sum_fueltypes_days_h = np.sum(fuel_yh, 2)            #sum over all hours
            sum_fueltypes_days = np.sum(sum_fueltypes_days_h, 1) #sum over all days
            average_fueltype = sum_fueltypes_days / 8760         #Average per fueltype
            fuel_yh_empty = np.ones((fuel_yh.shape))
            fuel_yh = fuel_yh_empty * average_fueltype[:, np.newaxis, np.newaxis]

    return fuel_yh

def calc_lf_improvement(
        param_lf_improved_cy,
        loadfactor_yd_cy,
    ):
    """Calculate load factor improvement

    Arguments
    ---------
    lf_improvement_ey : dict
        Load factor improvement until end year
    loadfactor_yd_cy : float
        Yd Load factor of current year

    Returns
    -------
    lf_improved_cy : str
        Improved load factor of current year
    peak_shift_crit : bool
        True: Peak is shifted, False: Peak isn't shifed
    """
    # Add load factor improvement to current year load factor
    lf_improved_cy = loadfactor_yd_cy + param_lf_improved_cy

    # Where load factor larger than zero, set to 1
    lf_improved_cy[lf_improved_cy > 1] = 1

    return lf_improved_cy

def assign_lp_no_techs(
        enduse,
        sector,
        load_profiles,
        fuel_y,
        make_all_flat
    ):
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

    # Convert all load profiles into flat load profiles
    if make_all_flat:
        sum_fueltypes_days_h = np.sum(fuel_yh, 2)            #sum over all hours
        sum_fueltypes_days = np.sum(sum_fueltypes_days_h, 1) #sum over all days
        average_fueltype = sum_fueltypes_days / 8760         #Average per fueltype
        fuel_yh_empty = np.ones((fuel_yh.shape))
        fuel_yh = fuel_yh_empty * average_fueltype[:, np.newaxis, np.newaxis]

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
        peak_day_nr = basic_functions.round_down(np.argmax(all_fueltypes_tot_h) / 24, 1)

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
        #logging.info("No peak can be found because no fuel assigned")
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
    fuel_yh_8760 = fuel_yh.reshape(8760)

    if np.sum(fuel_yh_8760) == 0:
        #logging.info("No peak can be found because no fuel assigned")
        # Return first entry of element (which is zero)
        return 0, 0
    else:
        # Sum fuel within every hour for every day and get day with maximum fuel
        peak_day_nr = int(basic_functions.round_down(np.argmax(fuel_yh_8760) / 24, 1))

        peak_h = np.max(fuel_yh_8760)

        return int(peak_day_nr), peak_h

def get_trough_day_single_fueltype(fuel_yh):
    """Iterate yh and get day with lowest fuel for a single fueltype
    The day with most fuel is considered to
    be the peak day. Over the simulation period,
    the peak day may change date in a year.

    Arguments
    ---------
    fuel_yh : array (365, 24) or array (8760)
        Fuel for every yh (yh)

    Return
    ------
    trough_day_nr : int
        Day with most fuel or service
    trough_h : float
        Peak hour value
    """
    fuel_yh_8760 = fuel_yh.reshape(8760)

    if np.sum(fuel_yh_8760) == 0:
        #logging.info("No peak can be found because no fuel assigned")
        # Return first entry of element (which is zero)
        return 0, 0
    else:
        # Sum fuel within every hour for every day and get day with maximum fuel
        trough_day_nr = int(basic_functions.round_down(np.argmin(fuel_yh_8760) / 24, 1))

        fuel_yh_365_24 = fuel_yh_8760.reshape(365, 24)
        trough_peak_h = np.max(fuel_yh_365_24[trough_day_nr])

        return int(trough_day_nr), trough_peak_h

def get_enduse_techs(fuel_tech_p_by):
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

    for tech_fueltype in fuel_tech_p_by.values():
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

    Return
    ------
    fuels_yh : array
        Fueltype storing hourly fuel for every fueltype (fueltype, 365, 24)
    """
    if mode_constrained:
        fuels_yh = {}
        for tech in enduse_techs:

            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            fuels_yh[tech] = fuel_tech_y[tech] * load_profile

    else:
        # --
        # Unconstrained mode, i.e. not technolog specific.
        # Store according to fueltype and heat
        # --
        fuels_yh = np.zeros((fueltypes_nr, 365, 24), dtype="float")

        for tech in enduse_techs:

            load_profile = load_profiles.get_lp(
                enduse, sector, tech, 'shape_yh')

            # If no fuel for this tech and not defined in enduse
            fuel_tech_yh = fuel_tech_y[tech] * load_profile

            fuels_yh[fueltypes['heat']] += fuel_tech_yh

    return fuels_yh

def service_to_fuel(
        enduse,
        sector,
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
    fuel_y = np.zeros((fueltypes_nr), dtype="float")

    if mode_constrained:
        for tech, service in service_tech.items():

            tech_eff = tech_stock.get_tech_attr(
                enduse, sector, tech, 'eff_cy')
            fueltype_int = tech_stock.get_tech_attr(
                enduse, sector, tech, 'fueltype_int')

            # Convert to fuel
            fuel_tech = service / tech_eff

            # Add fuel
            fuel_tech_y[tech] = fuel_tech

            fuel_y[fueltype_int] += fuel_tech
            #logging.debug("S --> F: tech: {} eff: {} fuel: {} fuel {}".format(tech, tech_eff, fuel_y[fueltype_int], fuel_tech))
    else:
        for tech, fuel_tech in service_tech.items():

            fuel_y[fueltypes['heat']] += fuel_tech
            fuel_tech_y[tech] = fuel_tech

    return fuel_y, fuel_tech_y

def fuel_to_service(
        enduse,
        sector,
        fuel_y,
        fuel_tech_p_by,
        tech_stock,
        fueltypes,
        mode_constrained
    ):
    """Converts fuel to energy service. Calculate energy service
    of each technology based on assumptions about base year fuel
    shares of an enduse (`fuel_tech_p_by`).

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Fuel per fueltype
    fuel_tech_p_by : dict
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
    for fueltype_int, tech_list in fuel_tech_p_by.items():

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
                tech_eff = tech_stock.get_tech_attr(enduse, sector, tech, 'eff_by')

                # Get fuel share and convert fuel to service per technology
                s_tech = fuel_y[fueltype_int] * fuel_share * tech_eff

                s_tech_y[tech] = s_tech

                # Sum total yearly service
                s_tot_y += s_tech #(y)

                ##logging.debug("F --> S: tech: {} eff: {} fuel: {} service {}".format(tech, tech_eff, fuel_y[fueltype_int], s_tech))
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
        heat_recovered,
        service,
        service_techs,
        curr_yr
    ):
    """Reduce heating demand according to assumption on heat reuse

    Arguments
    ----------
    enduse : str
        Enduse
    strategy_vars : dict
        Strategy variables
    service : dict or array
        Service of current year
    crit_dict : str
        Criteria to run function differently
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
        # Fraction of heat recovered in current year
        heat_recovered_p_cy = heat_recovered[enduse][curr_yr]

        if heat_recovered_p_cy == 0:
            return service, service_techs
        else:
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
        air_leakage,
        service,
        service_techs,
        curr_yr
    ):
    """Reduce heating demand according to assumption on
    improvements in air leaking

    Arguments
    ----------
    enduse : str
        Enduse
    air_leakage : dict
        Strategy variables
    service : dict or array
        Service of current year
    crit_dict : str
        Criteria to run function differently
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
        # Fraction of heat recovered in current year
        air_leakage_improvement_cy = air_leakage[enduse][curr_yr]

        if air_leakage_improvement_cy == 0:
            return service, service_techs
        else:
            air_leakage_by = 1
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
        enduse,
        sector,
        fuel_y,
        dw_stock,
        region,
        gva_industry,
        gva_per_head,
        population,
        reg_scen_drivers,
        base_yr,
        curr_yr
    ):
    """The fuel data for every end use are multiplied
    with respective scenario drivers. This is either
    done based on a dwelling stock or not.

    Arguments
    ----------
    enduse: str
        Enduse
    sector : str
        sector
    fuel_y : array
        Yearly fuel per fueltype
    dw_stock : object
        Dwelling stock
    region : str
        Region name
    gva_industry : dict
        GVA
    gva_per_head : dict
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
    if not dw_stock: # No dwelling stock is available
        """Calculate non-dwelling related scenario drivers
        """
        scenario_drivers = reg_scen_drivers[enduse]

        by_driver, cy_driver = 1, 1

        for scenario_driver in scenario_drivers:

            # Get correct data depending on driver
            if scenario_driver == 'gva':
                if not sector:
                    by_driver_data = gva_per_head[base_yr][region]
                    cy_driver_data = gva_per_head[curr_yr][region]
                else:
                    try:
                        gva_sector_lu = lookup_tables.economic_sectors_regional_MISTRAL()
                        gva_sector_nr = gva_sector_lu[sector]['match_int']

                        # Get sector specific GVA
                        by_driver_data = gva_industry[base_yr][gva_sector_nr][region]
                        cy_driver_data = gva_industry[curr_yr][gva_sector_nr][region]

                    except KeyError:
                        # No sector specific GVA data defined
                        logging.debug("No gva data found for sector {} {} ".format(sector, curr_yr))
                        by_driver_data = gva_per_head[base_yr][region]
                        cy_driver_data = gva_per_head[curr_yr][region]

                    #logging.info("gva  {}   {}".format(by_driver_data, cy_driver_data))

            elif scenario_driver == 'population':
                by_driver_data = population[base_yr][region]
                cy_driver_data = population[curr_yr][region]

                #logging.info("pop  {}   {}".format(population[base_yr][region], population[curr_yr][region]))

            # Multiply drivers
            by_driver *= by_driver_data
            cy_driver *= cy_driver_data

            # Testing
            if math.isnan(by_driver_data) or math.isnan(cy_driver_data):
                raise Exception("Scenario driver error")

        # Calculate scenario driver factor
        try:
            factor_driver = cy_driver / by_driver
        except ZeroDivisionError:
            factor_driver = 1

        #logging.info("  eda  {}   {}  {} {}".format(
        #    scenario_drivers, factor_driver, by_driver_data, cy_driver_data))

        fuel_y = fuel_y * factor_driver
    else:
        """Scenario driver calculation based on dwelling stock
        """
        # Test if enduse has a dwelling related scenario driver
        if hasattr(dw_stock[base_yr], enduse) and curr_yr != base_yr:

            # Scenariodriver of dwelling stock base year and new stock
            by_driver = getattr(dw_stock[base_yr], enduse)
            cy_driver = getattr(dw_stock[curr_yr], enduse)

            # Calculate scenario driver factor
            try:
                factor_driver = cy_driver / by_driver
            except ZeroDivisionError:
                factor_driver = 1

            # Testing
            if math.isnan(factor_driver):
                raise Exception("Scenario driver error")

            fuel_y = fuel_y * factor_driver
        else:
            pass #enduse not define with scenario drivers

    return fuel_y

def generic_demand_change(
        enduse,
        sector,
        fuel_y,
        generic_enduse_change,
        curr_yr
    ):
    """Calculates fuel based on assumed overall enduse or enduse/sector specific
    fuel consumption changes.

    The changes are assumed across all fueltypes.
    Because for enduses where no technologies are defined, a linear
    diffusion is suggested to best represent multiple sigmoid efficiency
    improvements of individual technologies.

    Arguments
    ----------
    enduse : str
        Enduse
    sector : str
        Sector. If True, then the change is valid for all sectors. if None, then no sector is defined for enduse.
    fuel_y : array
        Yearly fuel per fueltype
    generic_enduse_change : dict
        Change in overall enduse for every enduse (percent ey)
    curr_yr : int
        Current year

    Returns
    -------
    fuel_y : array
        Yearly new fuels
    """
    change_enduse = False

    # True for all sectors or no sector defined
    if sector is True or sector is None:
        try:
            change_cy = generic_enduse_change[enduse][curr_yr]
            change_enduse = True
        except KeyError: #no sector enduse is defined
            pass
    else:
        try:
            # Generic enduse change is defined sector specific
            change_cy = generic_enduse_change[enduse][sector][curr_yr]
            change_enduse = True
        except (KeyError, TypeError):
            pass
        try:
            # Generic enduse change is not defined sector specific
            change_cy = generic_enduse_change[enduse][curr_yr]

            change_enduse = True
        except (KeyError, TypeError):
            pass

    if change_enduse is True and change_cy != 0:
        fuel_y = fuel_y * (1 + change_cy)
    else:
        #logging.debug("No annual parameters are provided for enduse %s %s", enduse, sector)
        pass

    return fuel_y

def apply_weather_correction(
        enduse,
        fuel_y,
        cooling_factor_y,
        heating_factor_y,
        enduse_space_heating,
        enduse_space_cooling,
        f_weather_correction
    ):
    """Change fuel demand for heat and cooling service
    depending on changes in HDD and CDD within a region
    (e.g. climate change induced). Change fuel consumption based on
    climate change induced temperature differences

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
    f_weather_correction : dict
        Correction factors to calculate hdd and cdd
        related extra demands in case a different
        weather station is used

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

        # Apply correction factor for different weather year
        # which has different wheather stations and associated temperatures
        fuel_y = fuel_y * f_weather_correction['hdd']

        # Apply correction factor for change in climate over simulation period
        fuel_y = fuel_y * heating_factor_y

    elif enduse in enduse_space_cooling:
        fuel_y = fuel_y * f_weather_correction['cdd']
        fuel_y = fuel_y * cooling_factor_y

    return fuel_y

def apply_smart_metering(
        enduse,
        fuel_y,
        sm_assump,
        strategy_vars,
        curr_yr
    ):
    """Calculate fuel savings depending on smart meter penetration.
    Change fuel consumption based on smart meter induced general savings.

    Arguments
    ----------
    enduse : str
        Enduse
    fuel_y : array
        Yearly fuel per fueltype
    sm_assump : dict
        smart meter assumptions
    strategy_vars : dict
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
    # Enduse saving potentail of enduse of smart meter
    enduse_savings = sm_assump['savings_smart_meter'][enduse]

    # Smart meter penetration in current year (percentage of people having smart meters)
    penetration_cy = strategy_vars['smart_meter_p'][curr_yr]

    # Smart meter penetration in base year (percentage of people having smart meters)
    penetration_by = sm_assump['smart_meter_p_by']

    # Calculate fuel savings
    saved_fuel = fuel_y * (penetration_cy - penetration_by) * enduse_savings

    # Substract fuel savings
    fuel_y = fuel_y - saved_fuel

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

def get_service_diffusion(param_tech, curr_yr):
    """Calculate energy service fraction of technologies
    with increased service for current year based
    on sigmoid diffusion or linear diffusion according
    to provided param_tech

    Arguments
    ----------
    param_tech : dict
        Sigmoid diffusion parameters per technology
    curr_yr : dict
        Current year

    Returns
    -------
    s_tech_p : dict
        Share of service per technology of current year
    """
    if param_tech['l_parameter'] is None:
        s_tech_p = 0
    elif param_tech['l_parameter'] == 'linear':

        # Calcuate linear diffusion
        s_tech_p = param_tech['linear_slope'] * curr_yr + param_tech['linear_y_intercept']
    else:
        # Calculate sigmoid diffusion
        s_tech_p = diffusion_technologies.sigmoid_function(
            curr_yr,
            param_tech['l_parameter'],
            param_tech['midpoint'],
            param_tech['steepness'])

    # becuase of rounding error may be minus
    if s_tech_p < 0:
        assert s_tech_p < 0.0001 # Trow error if not rounding error. Something else went wrong
        s_tech_p = 0

    return s_tech_p

def apply_service_switch(
        enduse,
        s_tech_y_cy,
        all_technologies,
        curr_yr,
        base_yr,
        sector,
        annual_tech_diff_params,
        crit_switch_happening
    ):
    """Apply change in service depending on defined service switches.

    The service which is newly fulfilled by new technologies (as defined
    in the service switches) is substracted of the replaced
    technologies proportionally to their base year contribution.

    Arguments
    ---------
    enduse : str
        Enduse
    s_tech_y_cy : dict
        Service per technology
    all_technologies : dict
        Technologies to iterate
    curr_yr : int
        Current year
    base_yr : int
        Base year
    sector : str
        Sector
    annual_tech_diff_params : dict
        Sigmoid technology specific calculated annual diffusion values
    crit_switch_happening : bool
        Criteria wheter switch is defined or not

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

    # ---------------------------------------
    # Calculate switch
    # ----------------------------------------
    if crit_switch_service:
        switched_s_tech_y_cy = {}

        # Service of all technologies
        service_all_techs = sum(s_tech_y_cy.values())

        for tech in all_technologies:
            # Get service share per tech of cy of sigmoid parameter calculations
            p_s_tech_cy = annual_tech_diff_params[enduse][sector][tech][curr_yr]
            switched_s_tech_y_cy[tech] = service_all_techs * p_s_tech_cy
        return switched_s_tech_y_cy
    else:
        return s_tech_y_cy

def apply_cooling(
        enduse,
        fuel_y,
        cooled_floorarea,
        cooled_floorarea_p_by,
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
    cooled_floorarea : dict
        Strategy variables
    cooled_floorarea_p_by : dict
        Assumption about cooling floor area in base year
    curr_yr : int
        Current year

    Returns
    -------
    fuel_y : array
        Fuel array (either changed fuel depending on cooling percentage)
        of identical array
    """
    try:
        # Floor area share cooled in current year
        cooled_floorarea_p_cy = cooled_floorarea[enduse][curr_yr]

        # Calculate factor
        floorarea_cooling_factor = cooled_floorarea_p_cy / cooled_floorarea_p_by

        # Apply factor
        fuel_y = fuel_y * floorarea_cooling_factor
    except KeyError:
        pass

    return fuel_y

def generic_fuel_switch(
        enduse,
        sector,
        curr_yr,
        fuel_switch,
        fuel_y
    ):
    """Generic fuel switch in an enduse (e.g. replacing a fraction
    of a fuel with another fueltype)

    Arguments
    ---------
    enduse : str
        Enduse
    sector : str
        Sector
    curr_yr : str
        Current year of simulation
    fuel_switch : str
        Fuel swithces
    fuel_y : str
        Fuel of specific enduse and sector

    Returns
    -------
    fuel_y : array
        Annual fuel demand per fueltype
    """
    try:
        # Test if switch is defined for sector
        fuel_switch = fuel_switch[enduse][sector]
        switch_defined = True
    except KeyError:
        switch_defined = False

        # Test is not a switch for the whole enduse (across every sector) is defined
        try:
            key_of_switch = list(fuel_switch[enduse].keys())

            # Test wheter switches for sectors are provided
            if 'param_info' in key_of_switch: #one switch
                fuel_switch = fuel_switch[enduse]
                switch_defined = True
            else:
                pass # Switch is not defined for this sector
        except KeyError:
            pass

    if switch_defined is True:
        if fuel_switch[curr_yr] != 0:

            # Get fueltype to switch (old)
            fueltype_replace_str = fuel_switch['param_info']['fueltype_replace']
            fueltype_replace_int = tech_related.get_fueltype_int(fueltype_replace_str)

            # Get fueltype to switch to (new)
            fueltype_new_str = fuel_switch['param_info']['fueltype_new']
            fueltype_new_int = tech_related.get_fueltype_int(fueltype_new_str)

            # Value of current year
            fuel_share_switched_cy = fuel_switch[curr_yr]

            # Substract fuel
            fuel_minus = fuel_y[fueltype_replace_int] * (1 - fuel_share_switched_cy)
            fuel_y[fueltype_replace_int] -= fuel_minus

            # Add fuel
            fuel_y[fueltype_new_int] += fuel_minus
        else:
            # no fuel switch defined
            pass

    return fuel_y

def industry_enduse_changes(
        enduse,
        sector,
        curr_yr,
        strategy_vars,
        fuels,
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
    strategy_vars : dict
        All strategy variables
    fuels : array
        Annual fuels

    Returns
    --------
    fuels : np.array
        Changed fuels depending on scenario
    """
    if enduse == 'is_high_temp_process' and sector == 'basic_metals':

        # Calculate factor depending on fraction
        # of hot and cold steel rolling process
        factor = hot_cold_process(
            curr_yr,
            strategy_vars['p_cold_rolling_steel'],
            assumptions)

        fuels_out = fuels * factor

        return fuels_out
    else:
        return fuels

def hot_cold_process(
        curr_yr,
        p_cold_rolling_steel,
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
    curr_yr : int
        Current year
    strategy_vars : dict
        Strategy variables
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

    # Current year fractions
    p_cold_rolling_cy = p_cold_rolling_steel[curr_yr]
    p_hot_rolling_cy = 1 - p_cold_rolling_cy

    # Efficiencies of processes
    eff_cold = assumptions.eff_cold_rolling_process
    eff_hot = assumptions.eff_hot_rolling_process

    p_by = p_cold_rolling_by * eff_cold + p_hot_rolling_by * eff_hot
    p_cy = p_cold_rolling_cy * eff_cold  + p_hot_rolling_cy * eff_hot

    factor = p_cy  / p_by

    return factor
