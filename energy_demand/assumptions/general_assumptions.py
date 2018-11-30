"""All assumptions are either loaded in this file or definied here
"""
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions, date_prop
from energy_demand.assumptions import fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.profiles import hdd_cdd
from energy_demand.read_write import narrative_related
from energy_demand.basic import lookup_tables

class Assumptions(object):
    """Assumptions of energy demand model

    Arguments
    ---------
    base_yr : int, default=None
        Base year
    curr_yr : int, default=None
        Current year
    sim_yrs : list, default=None
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
            lookup_enduses=None,
            lookup_sector_enduses=None,
            base_yr=None,
            weather_by=None,
            simulation_end_yr=None,
            curr_yr=None,
            sim_yrs=None,
            paths=None,
            enduses=None,
            sectors=None,
            reg_nrs=None
        ):
        """Constructor
        """
        self.lookup_enduses = lookup_enduses
        self.lookup_sector_enduses = lookup_sector_enduses

        self.submodels_names = lookup_tables.basic_lookups()['submodels_names']
        self.nr_of_submodels = len(self.submodels_names)
        self.fueltypes = lookup_tables.basic_lookups()['fueltypes']
        self.fueltypes_nr = lookup_tables.basic_lookups()['fueltypes_nr']

        self.base_yr = base_yr
        self.weather_by = weather_by
        self.reg_nrs = reg_nrs
        self.simulation_end_yr = simulation_end_yr
        self.curr_yr = curr_yr
        self.sim_yrs = sim_yrs

        # ============================================================
        # Spatially modelled variables
        #
        # If spatial explicit diffusion is modelled, all parameters
        # or technologies having a spatial explicit diffusion need
        # to be defined.
        # ============================================================
        self.spatial_explicit_diffusion = 0 #0: False, 1: True

        # Define all variables which are affected by regional diffusion
        self.spatially_modelled_vars = [] # ['smart_meter_p']

        # Define technologies which are affected by spatial explicit diffusion
        self.techs_affected_spatial_f = ['heat_pumps_electricity']

        # Max penetration speed
        self.speed_con_max = 1 #1.5 # 1: uniform distribution >1: regional differences

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
        self.f_ss_cooling_weekend = 0.45                # Temporal calibration factor
        self.f_ss_weekend = 0.8                         # Temporal calibration factor
        self.f_is_weekend = 0.45                        # Temporal calibration factor

        # ============================================================
        #   Modelled day related factors
        # ============================================================
        #   model_yeardays_date : dict
        #     Contains for the base year for each days
        #     the information wheter this is a working or holiday
        # ------------------------------------------------------------
        self.model_yeardays = list(range(365))

        # Calculate dates
        self.model_yeardays_date = []
        for yearday in self.model_yeardays:
            self.model_yeardays_date.append(
                date_prop.yearday_to_date(base_yr, yearday))

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
        yr_until_changed_all_things = 2050

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
        #  Scenario drivers
        # ============================================================
        #
        #   For every enduse the relevant factors which affect enduse
        #   consumption can be added in a list.
        #
        #   Note:   If e.g. floorarea and population are added, the
        #           effects will be overestimates (i.e. no multi-
        #           collinearity are considered).
        #
        #   scenario_drivers : dict
        #     Scenario drivers per enduse
        # ------------------------------------------------------------
        self.scenario_drivers = {

            # --Residential
            'rs_space_heating': ['floorarea', 'hlc'], # Do not use HDD or pop because otherweise double count
            'rs_water_heating': ['population'],
            'rs_lighting': ['population', 'floorarea'],
            'rs_cooking': ['population'],
            'rs_cold': ['population'],
            'rs_wet': ['population'],
            'rs_consumer_electronics': ['population', 'gva'],
            'rs_home_computing': ['population'],

            # --Service
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
            'ss_other_electricity': ['population'],

            # Industry
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
        #   assump_cooling_floorarea : int
        #       The percentage of cooled floor space in the base year
        #
        #   Literature
        #   ----------
        #   Abela, A. et al. (2016). Study on Energy Use by Air
        #   Conditioning. Bre, (June), 31. Retrieved from
        #   https://www.bre.co.uk/filelibrary/pdf/projects/aircon-energy-use/StudyOnEnergyUseByAirConditioningFinalReport.pdf
        # ------------------------------------------------------------

        # See Abela et al. (2016) & Carbon Trust. (2012). Air conditioning. Maximising comfort, minimising energy consumption
        self.cooled_ss_floorarea_by = 0.35

        # ============================================================
        # Smart meter related base year assumptions
        # ============================================================
        #   smart_meter_p_by : int
        #       The percentage of households with smart meters in by
        # ------------------------------------------------------------
        self.smart_meter_assump = {}

        # Currently in 2017 8.6 mio smart meter installed of 27.2 mio households --> 31.6%
        # https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/671930/Smart_Meters_2017_update.pdf)
        # In 2015, 5.8 % percent of all househods had one: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/533060/2016_Q1_Smart_Meters_Report.pdf 
        self.smart_meter_assump['smart_meter_p_by'] = 0.05

        # Long term smart meter induced general savings, purley as
        # a result of having a smart meter (e.g. 0.03 --> 3% savings)
        # DECC 2015: Smart Metering Early Learning Project: Synthesis report
        # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
        # Reasonable assumption is between 0.03 and 0.01 (DECC 2015)
        self.smart_meter_assump['savings_smart_meter'] = {

            # Residential
            'rs_cold': 0.03,
            'rs_cooking': 0.03,
            'rs_lighting': 0.03,
            'rs_wet': 0.03,
            'rs_consumer_electronics': 0.03,
            'rs_home_computing': 0.03,
            'rs_space_heating': 0.03,
            'rs_water_heating': 0.03,

            # Service
            'ss_space_heating': 0.03,
            'ss_water_heating': 0.03,
            'ss_cooling_humidification': 0.03,
            'ss_fans': 0.03,
            'ss_lighting': 0.03,
            'ss_catering': 0.03,
            'ss_small_power': 0.03,
            'ss_ICT_equipment': 0.03,
            'ss_cooled_storage': 0.03,
            'ss_other_gas': 0.03,
            'ss_other_electricity': 0.03,

            # Industry submodule
            'is_high_temp_process': 0,
            'is_low_temp_process': 0,
            'is_drying_separation': 0,
            'is_motors': 0,
            'is_compressed_air': 0,
            'is_lighting': 0,
            'is_space_heating': 0,
            'is_other': 0,
            'is_refrigeration': 0}

        # ============================================================
        # Base temperature assumptions
        # ============================================================
        #
        #   Parameters related to smart metering
        #
        #   rs_t_heating : int
        #       Residential submodel base temp of heating of base year
        #   rs_t_cooling_by : int
        #       Residential submodel base temp of cooling of base year
        #   ...
        #
        #   Note
        #   ----
        #   Because demand for cooling cannot directly be linked to
        #   calculated cdd, the paramters 'ss_t_base_cooling' is used
        #   as a calibration factor. By artifiallcy lowering this
        #   parameter, the energy demand assignement over the days
        #   in a year is improved.
        # ------------------------------------------------------------
        t_bases = {
            'rs_t_heating': 15.5,
            'ss_t_heating': 15.5,
            'ss_t_cooling': 5,
            'is_t_heating': 15.5}

        self.t_bases = DummyClass(t_bases)

        # ============================================================
        # Enduses lists affed by hdd/cdd
        # ============================================================
        #
        #   These lists show for which enduses temperature related
        #   calculations are performed.
        #
        #   enduse_space_heating : list
        #       All enduses for which hdd are used for yd calculations
        #   ss_enduse_space_cooling : list
        #       All service submodel enduses for which cdd are used for
        #       yd calculations
        # ------------------------------------------------------------
        self.enduse_space_heating = [
            'rs_space_heating',
            'ss_space_heating',
            'is_space_heating']

        self.ss_enduse_space_cooling = [
            'ss_cooling_humidification']

        # ============================================================
        # Industry related
        #
        # High temperature processing (high_temp_ process) dominates
        # energy consumption in the iron and steel
        #
        # ---- Steel production - Enduse: is_high_temp_process, Sector: basic_metals
        # With industry service switch, the future shares of 'is_temp_high_process'
        # in sector 'basic_metals' can be set for 'basic_oxygen_furnace',
        # 'electric_arc_furnace', and 'SNG_furnace' can be specified
        #
        # ---- Cement production - Enduse: is_high_temp_process, Sector: non_metallic_mineral_products
        # Dry kilns, semidry kilns can be set
        # ============================================================

        # Share of cold rolling in steel manufacturing
        self.p_cold_rolling_steel_by = 0.2   # Estimated based on https://aceroplatea.es/docs/EuropeanSteelFigures_2015.pdf
        self.eff_cold_rolling_process = 1.8  # 80% more efficient than hot rolling Fruehan et al. (2002)
        self.eff_hot_rolling_process = 1.0   # 100% assumed efficiency

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
        self.technologies, self.tech_list = read_data.read_technologies(paths['path_technologies'])

        self.installed_heat_pump_by = tech_related.generate_ashp_gshp_split(
            self.gshp_fraction)

        # Add heat pumps to technologies
        self.technologies, self.tech_list['heating_non_const'], self.heat_pumps = tech_related.generate_heat_pump_from_split(
            self.technologies,
            self.installed_heat_pump_by,
            self.fueltypes)

        # ============================================================
        # Fuel Stock Definition
        # Provide for every fueltype of an enduse the share of fuel
        # which is used by technologies in the base year
        # ============================================================$
        fuel_tech_p_by = fuel_shares.assign_by_fuel_tech_p(
            enduses,
            sectors,
            self.fueltypes,
            self.fueltypes_nr)

        # ========================================
        # Get technologies of an enduse and sector
        # ========================================
        self.specified_tech_enduse_by = helpers.get_def_techs(
            fuel_tech_p_by)

        _specified_tech_enduse_by = helpers.add_undef_techs(
            self.heat_pumps,
            self.specified_tech_enduse_by,
            self.enduse_space_heating)
        self.specified_tech_enduse_by = _specified_tech_enduse_by

        # ========================================
        # General other info
        # ========================================
        self.seasons = date_prop.get_season(year_to_model=base_yr)
        self.model_yeardays_daytype, self.yeardays_month, self.yeardays_month_days = date_prop.get_yeardays_daytype(
            year_to_model=base_yr)

        # ========================================
        # Helper functions
        # ========================================
        self.fuel_tech_p_by, self.specified_tech_enduse_by, self.technologies = tech_related.insert_placholder_techs(
            self.technologies,
            fuel_tech_p_by,
            self.specified_tech_enduse_by)

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
            self.fuel_tech_p_by)

        testing_functions.testing_tech_defined(
            self.technologies, self.specified_tech_enduse_by)

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
        narrative_f_eff_achieved,
        narrative_gshp_fraction,
        crit_narrative_input=True
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
    gshp_fraction : float
        Mix of GSHP and GSHP
    crit_narrative_input : bool
        Criteria wheter inputs are single values or a narrative

    Note
    ----
    This needs to be run everytime an assumption is changed
    """
    if crit_narrative_input:
        # Read from narrative the value
        f_eff_achieved = narrative_related.read_from_narrative(narrative_f_eff_achieved) 
        gshp_fraction = narrative_related.read_from_narrative(narrative_gshp_fraction)
    else:
        f_eff_achieved = narrative_f_eff_achieved
        gshp_fraction = narrative_gshp_fraction

    # Assign same achieved efficiency factor for all technologies
    technologies = helpers.set_same_eff_all_tech(
        technologies,
        f_eff_achieved)

    # Calculate average eff of hp depending on fraction of GSHP to ASHP
    installed_heat_pump_ey = tech_related.generate_ashp_gshp_split(
        gshp_fraction)

    technologies = tech_related.calc_av_heat_pump_eff_ey(
        technologies, installed_heat_pump_ey)

    return technologies

class DummyClass(object):
    """Assumptions
    """
    def __init__(
            self,
            variables
        ):
        for var, value in variables.items():
            setattr(self, var, value)
