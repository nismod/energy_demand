"""All assumptions are either loaded in this file or definied here
"""
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions, date_prop
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.profiles import hdd_cdd

class Assumptions(object):
    """Assumptions of energy demand model

    Arguments
    ---------
    base_yr : int, default=None
        Base year
    curr_yr : int, default=None
        Current year
    simulated_yrs : list, default=None
        Simulated years
    paths : dict, default=None
        Paths
    enduses : list, default=None
        All modelled end uses
    sectors : list, default=None
        All modelled sectors
    fueltypes : dict, default=None
        Fueltype lookup
    fueltypes_nr : int, default=None
        Number of modelled fueltypes
    """
    def __init__(
            self,
            base_yr=None,
            curr_yr=None,
            simulated_yrs=None,
            paths=None,
            enduses=None,
            sectors=None,
            fueltypes=None,
            fueltypes_nr=None
        ):

        yr_until_changed_all_things = 2050

        # Simulation parameters
        self.base_yr = base_yr
        self.curr_yr = curr_yr
        self.simulated_yrs = simulated_yrs

        # ============================================================
        # Spatially modelled variables
        #
        # If spatial explicit diffusion is modelled, all parameters
        # or technologies having a spatial explicit diffusion need
        # to be defined.
        # ============================================================
        self.spatial_explicit_diffusion = 0 #0: False, 1: True

        # Define all variables which are affected by regional diffusion
        self.spatially_modelled_vars = [] # ['smart_meter_improvement_p']

        # Define technologies which are affected by spatial explicit diffusion
        self.techs_affected_spatial_f = ['heat_pumps_electricity']


        # --------
        # Demand management of heat pumps
        # --------
        self.flat_heat_pump_profile_both = 0 # 0: FAlse, 1: True
        self.flat_heat_pump_profile_only_water = 0  # Only water
    
        # ============================================================
        # Model calibration factors
        # ============================================================
        #
        #   These calibration factors are used to match the modelled
        #   electrictiy demand better with the validation data.
        #
        #   Weekend effects are used to distribut energy demands
        #   between working and weekend days. With help of these
        #   factors, the demand on weekends and holidays can be
        #   be lowered compared to working days.
        #   This factor can be applied either directly to an enduse
        #   or to the hdd or cdd calculations (to correct cooling
        #   or heating demand)
        #
        #       f_ss_cooling_weekend : float
        #           Weekend effect for cooling enduses
        #       f_ss_weekend : float
        #           WWeekend effect for service submodel enduses
        #       f_is_weekend : float
        #           Weekend effect for industry submodel enduses
        #       f_mixed_floorarea : float
        #           Share of floor_area which is assigned to either
        #           residential or non_residential floor area
        # ------------------------------------------------------------

        # Temporal calibration factors
        self.f_ss_cooling_weekend = 0.45              # 0.55
        self.f_ss_weekend = 0.8                      # 0.75
        self.f_is_weekend = 0.45                      # 0.4

        # Spatial calibration factor
        #self.f_mixed_floorarea = 0.8                  # 0.5 #TODO

        # ============================================================
        #   Modelled day related factors
        # ============================================================
        #
        #       model_yeardays_nrs : int
        #           Number of modelled yeardays (default=365)
        #       model_yearhours_nrs : int
        #           Number of modelled yearhours (default=8760)
        #        model_yeardays_date : dict
        #           Contains for the base year for each days
        #           the information wheter this is a working or holiday
        # ------------------------------------------------------------
        self.model_yeardays = list(range(365))

        # Calculate dates
        self.model_yeardays_date = []
        for yearday in self.model_yeardays:
            self.model_yeardays_date.append(
                date_prop.yearday_to_date(base_yr, yearday))

        self.model_yeardays_nrs = len(self.model_yeardays)
        self.model_yearhours_nrs = len(self.model_yeardays) * 24

        # ============================================================
        #   Dwelling stock related assumptions
        # ============================================================
        #
        #   Assumptions to generate a virtual dwelling stock
        #
        #       assump_diff_floorarea_pp : float
        #           Change in floor area per person (%, 1=100%)
        #       assump_diff_floorarea_pp_yr_until_changed : int
        #           Year until this change in floor area happens
        #       dwtype_distr_by : dict
        #           Housing Stock Distribution by Type
        #               Source: UK Housing Energy Fact File, Table 4c
        #       dwtype_distr_fy : dict
        #           welling type distribution end year
        #               Source: UK Housing Energy Fact File, Table 4c
        #       dwtype_floorarea_by : dict
        #           Floor area per dwelling type (Annex Table 3.1)
        #               Source: UK Housing Energy Fact File, Table 4c
        #       dwtype_floorarea_fy : dict
        #           Floor area per dwelling type
        #               Source: UK Housing Energy Fact File, Table 4c
        #       dwtype_age_distr : dict
        #           Floor area per dwelling type
        #               Source: Housing Energy Fact Sheet)
        #       yr_until_changed : int
        #           Year until change is realised
        #
        # https://www.gov.uk/government/statistics/english-housing-survey-2014-to-2015-housing-stock-report
        # ------------------------------------------------------------
        self.assump_diff_floorarea_pp = 1.0

        self.assump_diff_floorarea_pp_yr_until_changed = yr_until_changed_all_things

        self.dwtype_distr_by = {
            'semi_detached': 0.26,
            'terraced': 0.283,
            'flat': 0.203,
            'detached': 0.166,
            'bungalow': 0.088}

        self.dwtype_distr_fy = {

            'yr_until_changed': yr_until_changed_all_things,

            'semi_detached': 0.26,
            'terraced': 0.283,
            'flat': 0.203,
            'detached': 0.166,
            'bungalow': 0.088}

        self.dwtype_floorarea_by = {
            'semi_detached': 96,
            'terraced': 82.5,
            'flat': 61,
            'detached': 147,
            'bungalow': 77}

        self.dwtype_floorarea_fy = {

            'yr_until_changed': yr_until_changed_all_things,

            'semi_detached': 96,
            'terraced': 82.5,
            'flat': 61,
            'detached': 147,
            'bungalow': 77}

        # (Average builing age within age class, fraction)
        # The newest category of 2015 is added to implement change in refurbishing rate
        # For the base year, this is set to zero (if e.g. with future scenario set to 5%, then
        # proportionally to base year distribution number of houses are refurbished)
        self.dwtype_age_distr = {
            2015: {
                '1918' :0.21,
                '1941': 0.36,
                '1977.5': 0.3,
                '1996.5': 0.08,
                '2002': 0.05}}

        # ============================================================
        #   Scenario drivers
        # ============================================================
        #
        #   For every enduse the relevant factors which affect enduse
        #   consumption can be added in a list.
        #
        #   Note:   If e.g. floorarea and population are added, the
        #           effects will be overestimates (i.e. no multi-
        #           collinearity are considered).
        #
        #       scenario_drivers : dict
        #           Scenario drivers per enduse
        # ------------------------------------------------------------
        self.scenario_drivers = {}

        # --Residential SubModel
        self.scenario_drivers['rs_submodule'] = {
            'rs_space_heating': ['floorarea', 'hlc'], # Do not use HDD or pop because otherweise double count
            'rs_water_heating': ['population'],
            'rs_lighting': ['population', 'floorarea'],
            'rs_cooking': ['population'],
            'rs_cold': ['population'],
            'rs_wet': ['population'],
            'rs_consumer_electronics': ['population'],  #GVA TODO. As soon as GVA is avaiable, drive it with GVA
            'rs_home_computing': ['population']}        #GVA 

        # --Service Submodel (Table 5.5a)
        self.scenario_drivers['ss_submodule'] = {
            'ss_space_heating': ['floorarea'],
            'ss_water_heating': ['population'],
            'ss_lighting': ['floorarea'],
            'ss_catering': ['population'],
            'ss_ICT_equipment': ['population'],
            'ss_cooling_humidification': ['floorarea', 'population'],
            'ss_fans': ['floorarea', 'population'],
            'ss_small_power': ['population'],
            'ss_cooled_storage': ['population'],
            'ss_other_gas': ['population'],
            'ss_other_electricity': ['population']}

        # --Industry Submodel
        self.scenario_drivers['is_submodule'] = {
            'is_high_temp_process': ['gva'],
            'is_low_temp_process': ['gva'],
            'is_drying_separation': ['gva'],
            'is_motors': ['gva'],
            'is_compressed_air': ['gva'],
            'is_lighting': ['gva'],
            'is_space_heating': ['gva'],
            'is_other': ['gva'],
            'is_refrigeration': ['gva']}

        # ============================================================
        #   Cooling related assumptions
        # ============================================================
        #
        #   Parameters related to cooling enduses are defined here.
        #
        #   assump_cooling_floorarea : int
        #       The percentage of cooled floor space in the base year
        #
        #   Literature
        #   ----------
        #   Abela, A. et al. (2016). Study on Energy Use by Air
        #   Conditioning. Bre, (June), 31. Retrieved from
        #   https://www.bre.co.uk/filelibrary/pdf/projects/aircon-energy-use
        #   /StudyOnEnergyUseByAirConditioningFinalReport.pdf
        # ------------------------------------------------------------

        # See Abela et al. (2016)
        # Carbon Trust. (2012). Air conditioning. Maximising comfort, minimising energy consumption
        self.cooled_ss_floorarea_by = 0.35

        # ============================================================
        # Smart meter related base year assumptions
        # ============================================================
        #
        #   Parameters related to smart metering
        #
        #   smart_meter_p_by : int
        #       The percentage of households with smart meters in by
        #   smart_meter_diff_params : dict
        #       Sigmoid diffusion parameter of smater meters
        # ------------------------------------------------------------
        self.smart_meter_assump = {}
        self.smart_meter_assump['smart_meter_p_by'] = 0.1
        self.smart_meter_assump['smart_meter_diff_params'] = {
            'sig_midpoint': 0,
            'sig_steepness': 1}

        # ============================================================
        # Base temperature assumptions
        # ============================================================
        #
        #   Parameters related to smart metering
        #
        #   rs_t_heating_by : int
        #       Residential submodel base temp of heating of base year
        #   rs_t_cooling_by : int
        #       Residential submodel base temp of cooling of base year
        #   base_temp_diff_params : dict
        #       Sigmoid temperature diffusion parameters
        #   ...
        #
        #   Note
        #   ----
        #   Because demand for cooling cannot directly be linked to
        #   calculated cdd, the paramters 'ss_t_cooling_by' is used
        #   as a calibration factor. By artifiallcy lowering this
        #   parameter, the energy demand assignement over the days
        #   in a year is improved.
        # ------------------------------------------------------------
        t_bases = {}
        t_bases['rs_t_heating_by'] = 15.5    #
        #t_bases['rs_t_cooling_by'] = Not implemented

        t_bases['ss_t_heating_by'] = 15.5    #
        t_bases['ss_t_cooling_by'] = 5       # Orig: 5

        t_bases['is_t_heating_by'] = 15.5    #
        #self.t_bases['is_t_cooling_by'] = Not implemented

        self.t_bases = DummyClass(t_bases)

        self.base_temp_diff_params = {
            'sig_midpoint': 0,
            'sig_steepness': 1,
            'yr_until_changed': yr_until_changed_all_things}

        # ============================================================
        # Enduses lists affed by hdd/cdd
        # ============================================================
        #
        #   These lists show for which enduses temperature related
        #   calculations are performed.
        #
        #   enduse_space_heating : list
        #       All enduses for which hdd are used for yd calculations
        #   enduse_rs_space_cooling : list
        #       All residential enduses for which cdd are used for
        #       yd calculations
        #   ss_enduse_space_cooling : list
        #       All service submodel enduses for which cdd are used for
        #       yd calculations
        # ------------------------------------------------------------
        self.enduse_space_heating = [
            'rs_space_heating', 'ss_space_heating', 'is_space_heating']

        self.enduse_rs_space_cooling = []
        self.ss_enduse_space_cooling = ['ss_cooling_humidification']

        # ============================================================
        # Industry submodel related parameters
        # ============================================================
        #
        #   Assumptions related to industrial enduses
        #
        #   Overal changes in industry related enduse can be changed
        #   in 'enduse_overall_change_enduses'
        #
        # ------------------------------------------------------------

        # --------------------------------------------
        # heating
        # -------------------------------------------- 
        # --> No scenario drivers but driven by switches

        # --------------------------------------------
        # lighting
        #
        # No individual technologies are defined. Only
        # overall efficiency increase can be implemented
        #--------------------------------------------

        # --------------------------------------------
        # high_temp_ process
        #
        #       High temperature processing dominates energy consumption in the iron and steel,
        #       non-ferrous metal, bricks, cement, glass and potteries industries. This includes
        #          - coke ovens
        #          - blast furnaces and other furnaces
        #          - kilns and
        #          - glass tanks.
        # High consumption in Chemicals, Non_metallic mineral products, paper, food_production
        # Fuel use ratio - electric arc furnace over blast furnace steel making in cement sector
        # BAT - iron & steel - continous/Ingot casting 	Sectoral share - continuous %
        # --------------------------------------------

        # Share of cold rolling in steel manufacturing
        # *****************
        self.p_cold_rolling_steel_by = 0.2      # Estimated  based on https://aceroplatea.es/docs/EuropeanSteelFigures_2015.pdf
        self.eff_cold_rolling_process = 1.8     # 80% more efficient than hot rolling Fruehan et al. (2002)
        self.eff_hot_rolling_process = 1.0      # 100% assumed efficiency

        # Steel production - Enduse: is_high_temp_process, Sector: basic_metals
        # *****************
        # With industry service switch, the future shares
        # in 'basic_oxygen_furnace', 'electric_arc_furnace', and 'SNG_furnace'
        # can be specified

        #scrap-based production: electric arc furnace 
        #direct reduction process: natrual gas based, electric arc furnace
        #BF-BOF (blast furnace - basix oxgen furnace)
        #       Example service switch: 
        #           is_high_temp_process,SNG_furnace,1.0,2050,basic_metals

        # Cement production - Enduse: is_high_temp_process, Sector: non_metallic_mineral_products
        # *****************
        # technologies: Dry kilns, semidry kilns

        # CHEMICALs - Enduse: is_high_temp_process, Sector: CHEMICALS
        # *****************
        # technologies: Dry & wet kilns

        # ----------------
        # Efficiency of motors
        # ----------------
        #is_motors_eff_change = 0

        # ----------------
        # Efficiency of others
        # ----------------
        #is_others_eff_change = 0

        # ----------------
        # Efficiency of others
        # ----------------
        #is_refrigeration_eff_change = 0

        # ----------------
        # Efficiency of is_compressed_air
        # ----------------
        #is_compressed_air_eff_change =

        # ----------------
        # Efficiency of is_drying_separation
        # ----------------
        #is_drying_separation_eff_change = 

        # ----------------
        # Efficiency of is_low_temp_process
        # ----------------
        #is_low_temp_process_eff_change = 

        # ============================================================
        # Assumption related to heat pump technologies
        # ============================================================
        #
        #   Assumptions related to technologies
        #
        #   gshp_fraction : list
        #       Fraction of installed gshp_fraction heat pumps in base year
        #       ASHP = 1 - gshp_fraction
        # ------------------------------------------------------------
        self.gshp_fraction = 0.1

        # Load defined technologies
        self.technologies, self.tech_list = read_data.read_technologies(
            paths['path_technologies'], fueltypes)

        self.installed_heat_pump_by = tech_related.generate_ashp_gshp_split(
            self.gshp_fraction)

        # Add heat pumps to technologies
        self.technologies, self.tech_list['heating_non_const'], self.heat_pumps = tech_related.generate_heat_pump_from_split(
            self.technologies,
            self.installed_heat_pump_by,
            fueltypes)

        # Collect all heating technologies
        # TODO: MAYBE ADD IN TECH DOC ANOTHER LIST SPECIFYING ALL HEATING TECHs
        self.heating_technologies = get_all_heating_techs(self.tech_list)

        # ============================================================
        # Enduse diffusion paramters
        # ============================================================
        #
        #   Assumptions related to general diffusion
        #
        #   This parameters are used to specify e.g. diffusion of
        #   an enduse which is not specified by technologies
        #   or the diffusion of a policy of changing a parameter
        #   over time.
        # ------------------------------------------------------------
        self.enduse_overall_change = {}
        self.enduse_overall_change['other_enduse_mode_info'] = {
            'diff_method': 'linear',
            'sigmoid': {
                'sig_midpoint': 0,
                'sig_steepness': 1}}

        # ============================================================
        # Fuel Stock Definition
        # Provide for every fueltype of an enduse
        # the share of fuel which is used by technologies for thebase year
        # ============================================================
        self.rs_fuel_tech_p_by, self.ss_fuel_tech_p_by, self.is_fuel_tech_p_by = assumptions_fuel_shares.assign_by_fuel_tech_p(
            enduses,
            sectors,
            fueltypes,
            fueltypes_nr)

        # ========================================
        # Get technologies of an enduse
        # ========================================
        self.rs_specified_tech_enduse_by = helpers.get_def_techs(
            self.rs_fuel_tech_p_by, sector_crit=False)

        self.ss_specified_tech_enduse_by = helpers.get_def_techs(
            self.ss_fuel_tech_p_by, sector_crit=True)

        self.is_specified_tech_enduse_by = helpers.get_def_techs(
            self.is_fuel_tech_p_by, sector_crit=True)

        rs_specified_tech_enduse_by_new = helpers.add_undef_techs(
            self.heat_pumps,
            self.rs_specified_tech_enduse_by,
            'rs_space_heating')
        self.rs_specified_tech_enduse_by = rs_specified_tech_enduse_by_new

        ss_specified_tech_enduse_by_new = helpers.add_undef_techs(
            self.heat_pumps,
            self.ss_specified_tech_enduse_by,
            'ss_space_heating')
        self.ss_specified_tech_enduse_by = ss_specified_tech_enduse_by_new

        is_specified_tech_enduse_by_new = helpers.add_undef_techs(
            self.heat_pumps,
            self.is_specified_tech_enduse_by,
            'is_space_heating')
        self.is_specified_tech_enduse_by = is_specified_tech_enduse_by_new

        # ============================================================
        # Read in switches
        # ============================================================

        # Read in scenaric fuel switches
        self.rs_fuel_switches = read_data.read_fuel_switches(
            paths['rs_path_fuel_switches'], enduses, fueltypes, self.technologies)
        self.ss_fuel_switches = read_data.read_fuel_switches(
            paths['ss_path_fuel_switches'], enduses, fueltypes, self.technologies)
        self.is_fuel_switches = read_data.read_fuel_switches(
            paths['is_path_fuel_switches'], enduses, fueltypes, self.technologies)

        # Read in scenaric service switches
        self.rs_service_switches = read_data.service_switch(
            paths['rs_path_service_switch'], self.technologies)
        self.ss_service_switches = read_data.service_switch(
            paths['ss_path_service_switch'], self.technologies)
        self.is_service_switches = read_data.service_switch(
            paths['is_path_industry_switch'], self.technologies)

        # Read in scenaric capacity switches
        self.rs_capacity_switches = read_data.read_capacity_switch(
            paths['rs_path_capacity_installation'])
        self.ss_capacity_switches = read_data.read_capacity_switch(
            paths['ss_path_capacity_installation'])
        self.is_capacity_switches = read_data.read_capacity_switch(
            paths['is_path_capacity_installation'])

        # Testing
        self.crit_switch_happening = testing_functions.switch_testing(
            fuel_switches = [self.rs_fuel_switches, self.ss_fuel_switches, self.is_fuel_switches],
            service_switches = [self.rs_service_switches, self.ss_service_switches, self.is_service_switches],
            capacity_switches = [
                self.rs_capacity_switches,
                self.ss_capacity_switches, 
                self.is_capacity_switches])

        # ========================================
        # General other assumptions
        # ========================================
        self.seasons = date_prop.get_season(year_to_model=base_yr)

        self.model_yeardays_daytype, self.yeardays_month, self.yeardays_month_days = date_prop.get_model_yeardays_daytype(
            year_to_model=base_yr)

        # ========================================
        # Helper functions
        # ========================================
        self.rs_fuel_tech_p_by, self.rs_specified_tech_enduse_by, self.technologies = tech_related.insert_placholder_techs(
            self.technologies,
            self.rs_fuel_tech_p_by,
            self.rs_specified_tech_enduse_by,
            sector_crit=False)

        self.ss_fuel_tech_p_by, self.ss_specified_tech_enduse_by, self.technologies = tech_related.insert_placholder_techs(
            self.technologies,
            self.ss_fuel_tech_p_by,
            self.ss_specified_tech_enduse_by,
            sector_crit=True)

        self.is_fuel_tech_p_by, self.is_specified_tech_enduse_by, self.technologies = tech_related.insert_placholder_techs(
            self.technologies,
            self.is_fuel_tech_p_by,
            self.is_specified_tech_enduse_by,
            sector_crit=True)

        # ========================================
        # Calculations with assumptions
        # ========================================
        self.cdd_weekend_cfactors = hdd_cdd.calc_weekend_corr_f(
            self.model_yeardays_daytype,
            self.f_ss_cooling_weekend)

        self.ss_weekend_f = hdd_cdd.calc_weekend_corr_f(
            self.model_yeardays_daytype,
            self.f_ss_weekend)

        self.is_weekend_f = hdd_cdd.calc_weekend_corr_f(
            self.model_yeardays_daytype,
            self.f_is_weekend)

        # ========================================
        # Testing
        # ========================================
        testing_functions.testing_fuel_tech_shares(
            self.rs_fuel_tech_p_by)
        for enduse in self.ss_fuel_tech_p_by:
            testing_functions.testing_fuel_tech_shares(
                self.ss_fuel_tech_p_by[enduse])
        for enduse in self.is_fuel_tech_p_by:
            testing_functions.testing_fuel_tech_shares(
                self.is_fuel_tech_p_by[enduse])

        testing_functions.testing_tech_defined(
            self.technologies, self.rs_specified_tech_enduse_by)
        testing_functions.testing_tech_defined(
            self.technologies, self.ss_specified_tech_enduse_by)
        testing_functions.testing_tech_defined(
            self.technologies, self.is_specified_tech_enduse_by)

    def update(self, name, value):
        """Update assumptions

        Arguments
        ---------
        name : str
            name of attribute
        value : any
            Type of value
        """
        setattr(self, name, value)

def update_technology_assumption(
        technologies,
        f_eff_achieved,
        gshp_fraction_ey
    ):
    """Updates technology related properties based on
    scenario assumptions. Calculate average efficiency of
    heat pumps depending on mix of GSHP and ASHP,
    set the efficiency achieval factor of all factor according
    to strategy assumptions

    Parameters
    ----------
    technologies : dict
        Technologies
    f_eff_achieved : float
        Factor achieved
    gshp_fraction_ey : float
        Mix of GSHP and GSHP

    Note
    ----
    This needs to be run everytime an assumption is changed
    """
    # Assign same achieved efficiency factor for all technologies
    technologies = helpers.set_same_eff_all_tech(
        technologies,
        f_eff_achieved)

    # Calculate average eff of hp depending on fraction of GSHP to ASHP
    installed_heat_pump_ey = tech_related.generate_ashp_gshp_split(
        gshp_fraction_ey)

    technologies = tech_related.calc_av_heat_pump_eff_ey(
        technologies, installed_heat_pump_ey)

    return technologies

def get_all_heating_techs(tech_lists):
    """Get all heating technologies from tech lists

    Arguments
    ----------
    tech_lists : dict
        Technologies as types

    Returns
    -------
    heating_technologies : list
        All heating technologies
    """
    #TODO: REMOVE
    heating_technologies = []

    for tech in tech_lists['heating_const']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)
    for tech in tech_lists['heating_non_const']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)
    for tech in tech_lists['tech_district_heating']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)
    for tech in tech_lists['secondary_heating_electricity']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)
    for tech in tech_lists['storage_heating_electricity']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)
    for tech in tech_lists['tech_CHP']:
        if tech != 'placeholder_tech':
            heating_technologies.append(tech)

    return heating_technologies

class DummyClass(object):
    """Assumptions
    """
    def __init__(
            self,
            variables
        ):
        for var, value in variables.items():
            setattr(self, var, value)
