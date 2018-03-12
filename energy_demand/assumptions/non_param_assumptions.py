"""All assumptions are either loaded in this file or definied here
"""
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions, date_prop
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.profiles import hdd_cdd

#TODO MAKE THAT ALL ASSUMPTIONS ARE IMPROVEMENTS (e.g. improvement floor area cooling)
class Assumptions(object):
    """Assumptions
    """
    def __init__(
            self,
            base_yr=None,
            paths=None,
            enduses=None,
            sectors=None,
            fueltypes=None,
            fueltypes_nr=None
        ):

        yr_until_changed_all_things = 2050

        # ============================================================
        # Spatially modelled variables
        # ============================================================
        # Define all variables which are affected by regional diffusion
        self.spatially_modelled_vars = []
        #    'smart_meter_improvement_p'
        #]

        # Define technologies which are affected by spatial explicit diffusion
        self.techs_affected_spatial_f = ['heat_pumps_electricity']

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
        self.f_ss_cooling_weekend = 0.6              # 0.5
        self.f_ss_weekend = 0.8                      # 0.7
        self.f_is_weekend = 0.4                      # 0.4

        # Spatial calibration factor
        self.f_mixed_floorarea = 0.2                 # 0.4

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
        #       assump_dwtype_distr_by : dict
        #           Housing Stock Distribution by Type
        #               Source: UK Housing Energy Fact File, Table 4c
        #       assump_dwtype_distr_future : dict
        #           welling type distribution end year
        #               Source: UK Housing Energy Fact File, Table 4c
        #       assump_dwtype_floorarea_by : dict
        #           Floor area per dwelling type (Annex Table 3.1)
        #               Source: UK Housing Energy Fact File, Table 4c
        #       assump_dwtype_floorarea_future : dict
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

        self.assump_dwtype_distr_by = {
            'semi_detached': 0.26,
            'terraced': 0.283,
            'flat': 0.203,
            'detached': 0.166,
            'bungalow': 0.088}

        self.assump_dwtype_distr_future = {

            'yr_until_changed': yr_until_changed_all_things,

            'semi_detached': 0.26,
            'terraced': 0.283,
            'flat': 0.203,
            'detached': 0.166,
            'bungalow': 0.088}

        self.assump_dwtype_floorarea_by = {
            'semi_detached': 96,
            'terraced': 82.5,
            'flat': 61,
            'detached': 147,
            'bungalow': 77}

        self.assump_dwtype_floorarea_future = {

            'yr_until_changed': yr_until_changed_all_things,

            'semi_detached': 96,
            'terraced': 82.5,
            'flat': 61,
            'detached': 147,
            'bungalow': 77}

        # (Average builing age within age class, fraction)
        # Note: the number of refurbished houses can be changed ?? TODO: IMPELEMENT AS SCENARIO
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
            'rs_consumer_electronics': ['population'],
            'rs_home_computing': ['population']}

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
        self.t_bases = {}
        self.t_bases['rs_t_heating_by'] = 15.5    #
        #self.t_bases['rs_t_cooling_by'] = Not implemented

        self.t_bases['ss_t_heating_by'] = 15.5    #
        self.t_bases['ss_t_cooling_by'] = 5       # Orig: 5

        self.t_bases['is_t_heating_by'] = 15.5    #
        #self.t_bases['is_t_cooling_by'] = Not implemented

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
        #   s
        #       S
        # ------------------------------------------------------------

        # --------------------------------------------
        # heating 
        # -------------------------------------------- 
        # --> No scenario drivers but driven by switches

        # --------------------------------------------
        # lighting 
        # -------------------------------------------- 
        # --> No scenario drivers but driven by switches

        # --------------------------------------------
        # high_temp_ process 
        #       High temperature processing dominates energy consumption in the iron and steel,
        #       non-ferrous metal, bricks, cement, glass and potteries industries. This includes
        #          - coke ovens
        #          - blast furnaces and other furnaces
        #          - kilns and
        #          - glass tanks.

        #BAF: basic_oxygen_furnace
        #EAF: electric_arc_furnace
        #BAT - iron & steel - Coke ovens	Sectoral share (%)
        #BAT - iron & steel - EAF/BOF 	    Sectoral share - EOF %
        #BAT - iron & steel - continous/Ingot casting 	Sectoral share - continuous %
        #BAT - iron & steel - cold/hot rolling 	Sectoral share - cold %                     #DONE
        #BAT - iron & steel - substitute	Sectoral share - substitute %

        # --------------------------------------------

        # Share of cold rolling in steel manufacturing (total = hot and cold)
        self.p_cold_rolling_steel_by  = 0.5  #TODO
        self.eff_cold_rolling_process = 1.0  #TODO
        self.eff_hot_rolling_process = 1.0   #TODO

        # ---------------
        p_service_electric_arc_furnace = 0.5            #TODO: DEFINE FROM BASE YEAR FUEL MIX
        p_service_basic_oxygen_furnace = 1 - p_service_electric_arc_furnace
        p_SNG_furnace = 0 #biomass
        # Sector metalic (steel industry)

        assumpt_fraction_cement_of_high_temp_process = 0.5 # (non_metallic)
        assumpt_fraction_netall_of_high_temp_process = 0.5 # (basic_metals)
        
        #scrap-based production: electric arc furnace 
        #direct reduction process: natrual gas based, electric arc furnace
        #BF-BOF (blast furnace - basix oxgen furnace)


        # Sectors non_metallic_mineral_products

        # --> Define efficiencis of technologies
        #   - Other (?)
        #   .ev refrigeration / compressed air / motors
        #   
        #
        #  

        # High consumption in Chemicals, Non_metallic mineral products, paper, food_production
        ''' 'is_high_temp_process': ['gva'],
            'is_low_temp_process': ['gva'],
            'is_drying_separation': ['gva'],
            'is_motors': ['gva'],
            'is_compressed_air': ['gva'],
            'is_lighting': ['gva'],
            'is_space_heating': ['gva'],
            'is_other': ['gva'],
            'is_refrigeration': ['gva']}'''

        # Sectors
        '''
        'other_manufacturing': ,
        'pharmaceuticals': ,
        'waste_collection': ,
        'machinery': ,
        'leather': ,
        'furniture': ,
        'mining': ,
        'rubber_plastics': ,
        'computer': ,
        'other_transport_equipment': ,
        'basic_metals': ,
        'tobacco': ,
        'textiles': ,
        'paper': ,
        'chemicals': ,
        'non_metallic_mineral_products': ,
        'food_production': ,
        'wearing_appeal': ,
        'fabricated_metal_products': ,
        'beverages': ,
        'motor_vehicles': ,
        'wood': ,
        'printing': ,
        'water_collection_treatment': ,
        'electrical_equipment': '''

        '''
        Fuel use ratio - dry process over wet process in cement sector
        Fuel use ratio - novel alkali cement over incumbent process in cement sector
        Fuel use ratio - novel partially dehydrated cement over incumbent process in cement sector
        Fuel use ratio - electric arc furnace over blast furnace steel making in cement sector
        Fuel use ratio - continuous over ingot casting in cement sector
        Fuel use ratio - cold over hot rolling in cement sector
        '''
        '''

        BAT - cement - dry/wet process 	Dry/wet process (Dry %)
        BAT - cement - Novel-Alkali-activated (alumino-silicate, geopolymer)	Sectoral share of Alkali activated %
        BAT - cement - Novel-Partially prehydrated Calcium silicate hydrate	Sectoral share - Partially prehydrated %'''

        # -----------------
        # Steel production
        # -----------------
        # blast furnace process
        # electric arc furnace
        # directe reduced iron
        # Hith temperature process -- cement, non-ferrous metla, coke ovens, blast furnaces, kilns,..

        # ============================================================
        # Assumption related to technologies
        # ============================================================
        #
        #   Assumptions related to technologies
        #
        #   split_hp_gshp_to_ashp_by : list
        #       Split between GSHP and ASHP (in %, 1=100%),
        #       Share of installed heat pumps in base year (ASHP to GSHP)
        # ------------------------------------------------------------
        self.split_hp_gshp_to_ashp_by = 0.1

        self.technologies, self.tech_list = read_data.read_technologies(
            paths['path_technologies'], fueltypes)

        self.installed_heat_pump_by = tech_related.generate_ashp_gshp_split(
            self.split_hp_gshp_to_ashp_by)

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
            paths['rs_path_fuel_switches'], enduses, fueltypes)
        self.ss_fuel_switches = read_data.read_fuel_switches(
            paths['ss_path_fuel_switches'], enduses, fueltypes)
        self.is_fuel_switches = read_data.read_fuel_switches(
            paths['is_path_fuel_switches'], enduses, fueltypes)

        # Read in scenaric service switches
        self.rs_service_switches = read_data.service_switch(
            paths['rs_path_service_switch'], self.technologies)
        self.ss_service_switches = read_data.service_switch(
            paths['ss_path_service_switch'], self.technologies)
        self.is_service_switches = read_data.service_switch(
            paths['is_path_industry_switch'], self.technologies)

        # Read in scenaric capacity switches
        self.capacity_switches = {}
        self.capacity_switches['rs_capacity_switches'] = read_data.read_capacity_switch(
            paths['rs_path_capacity_installation'])
        self.capacity_switches['ss_capacity_switches'] = read_data.read_capacity_switch(
            paths['ss_path_capacity_installation'])
        self.capacity_switches['is_capacity_switches'] = read_data.read_capacity_switch(
            paths['is_path_capacity_installation'])

        # ========================================
        # General other assumptions
        # ========================================
        self.seasons = date_prop.read_season(year_to_model=base_yr)

        model_yeardays_daytype, yeardays_month, yeardays_month_days = date_prop.get_model_yeardays_daytype(
            year_to_model=base_yr)

        self.model_yeardays_daytype = model_yeardays_daytype
        self.yeardays_month = yeardays_month
        self.yeardays_month_days = yeardays_month_days

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
            model_yeardays_daytype,
            self.f_ss_cooling_weekend)

        self.ss_weekend_f = hdd_cdd.calc_weekend_corr_f(
            model_yeardays_daytype,
            self.f_ss_weekend)

        self.is_weekend_f = hdd_cdd.calc_weekend_corr_f(
            model_yeardays_daytype,
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

def update_assumptions(
        technologies,
        factor_achieved,
        split_hp_gshp_to_ashp_ey
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
    factor_achieved : float
        Factor achieved
    split_hp_gshp_to_ashp_ey : float
        Mix of GSHP and GSHP

    Note
    ----
    This needs to be run everytime an assumption is changed
    """
    # Assign same achieved efficiency factor for all technologies
    technologies = helpers.set_same_eff_all_tech(
        technologies,
        factor_achieved)

    # Calculate average eff of hp depending on fraction of GSHP to ASHP
    installed_heat_pump_ey = tech_related.generate_ashp_gshp_split(
        split_hp_gshp_to_ashp_ey)

    technologies = tech_related.calc_av_heat_pump_eff_ey(
        technologies, installed_heat_pump_ey)

    return technologies

def get_all_heating_techs(tech_lists):
    """Get all heating technologies from tech lists
    """
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
