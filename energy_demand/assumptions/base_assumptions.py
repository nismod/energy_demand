"""All assumptions are either loaded in this file or definied here
"""
import logging
from datetime import date
import numpy as np
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions as testing
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.basic import date_handling
from energy_demand.read_write import data_loader
#TODO: Make that HLC can be improved, ssumption share of existing
#  dwelling stock which is assigned new HLC coefficients

def load_assumptions(data, write_sim_param):
    """All assumptions of the energy demand model are loaded and added to the data dictionary

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict
    """
    logging.debug("... load assumptions")
    assumptions = {}
    if write_sim_param: # == True:
        sim_param = {}
        sim_param['base_yr'] = 2015
        sim_param['end_yr'] = 2020
        sim_param['sim_years_intervall'] = 5 # Make calculation only every X year
        sim_param['sim_period'] = range(sim_param['base_yr'], sim_param['end_yr'] + 1, sim_param['sim_years_intervall'])
        sim_param['sim_period_yrs'] = int(sim_param['end_yr'] + 1 - sim_param['base_yr'])
        sim_param['curr_yr'] = sim_param['base_yr']
        sim_param['list_dates'] = date_handling.fullyear_dates(
            start=date(sim_param['base_yr'], 1, 1),
            end=date(sim_param['base_yr'], 12, 31))

    # ============
    # Date selection for which model is run
    # Store in list all dates which are modelled
    # ============
    year_to_model = 2015
    winter_week = list(range(date_handling.date_to_yearday(year_to_model, 1, 12), date_handling.date_to_yearday(year_to_model, 1, 26))) #Jan
    spring_week = list(range(date_handling.date_to_yearday(year_to_model, 5, 11), date_handling.date_to_yearday(year_to_model, 5, 25))) #May
    summer_week = list(range(date_handling.date_to_yearday(year_to_model, 7, 13), date_handling.date_to_yearday(year_to_model, 7, 27))) #Jul
    autumn_week = list(range(date_handling.date_to_yearday(year_to_model, 10, 12), date_handling.date_to_yearday(year_to_model, 10, 26))) #Oct

    # Modelled days
    assumptions['model_yeardays'] = winter_week + spring_week + summer_week + autumn_week
    #assumptions['model_yeardays'] = list(range(date_handling.date_to_yearday(2015, 1, 1), date_handling.date_to_yearday(2015, 1, 8)))
    assumptions['model_yeardays'] = list(range(365)) #a list with yearday values ranging between 1 and 364

    #Modelled dates
    assumptions['model_yeardays_date'] = []
    for yearday in assumptions['model_yeardays']:
        assumptions['model_yeardays_date'].append(
            date_handling.yearday_to_date(sim_param['base_yr'], yearday))

    # Nr of days to model
    assumptions['model_yeardays_nrs'] = len(assumptions['model_yeardays'])
    assumptions['model_yearhours_nrs'] = len(assumptions['model_yeardays']) * 24 #TODO

    # --------------------------------------
    # Calculate for all yeardays the daytype of base year
    # --------------------------------------
    list_dates = date_handling.fullyear_dates(
        start=date(sim_param['base_yr'], 1, 1),
        end=date(sim_param['base_yr'], 12, 31))

    model_yeardays_daytype = np.chararray(365, itemsize=7)
    model_yeardays_daytype[:] = 'workday'

    for array_day, date_yearday in enumerate(list_dates):
        # Take respectve daily fuel curve depending on weekday or weekend
        if date_handling.get_weekday_type(date_yearday) == 'holiday':
            model_yeardays_daytype[array_day] = 'holiday'

    assumptions['model_yeardays_daytype'] = model_yeardays_daytype

    # ============================================================
    # If unconstrained mode (False), heat demand is provided per technology.
    # True --> Technologies are defined in ED model
    # False: heat is delievered
    assumptions['mode_constrained'] = False #False provides technologies

    # ============================================================
    # Residential dwelling stock assumptions
    # ============================================================
    # Change in floor area per person up to end_yr 1.0 = 100%
    # ASSUMPTION (if minus, check if new dwellings are needed)
    assumptions['assump_diff_floorarea_pp'] = 1

    # Specific Energy Demand factors per dwelling type could be defined
    # (e.g. per dwelling type or GVA class or residents....) #TODO

    # Dwelling type distribution base year (fixed)
    assumptions['assump_dwtype_distr_by'] = {
        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088
        }

    # Dwelling type distribution end year
    assumptions['assump_dwtype_distr_ey'] = {
        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088
        }

    # Floor area per dwelling type (TODO: SOURCE)
    assumptions['assump_dwtype_floorarea_by'] = {
        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77
        }

    # Floor area per dwelling type #TODO
    assumptions['assump_dwtype_floorarea_ey'] = {
        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77
        }

    # Assumption about age distribution
    assumptions['dwtype_age_distr'] = {
        2015: {
            '1918':0.21, #Average builing age within age class, fraction
            '1941': 0.36,
            '1977.5': 0.3,
            '1996.5': 0.08,
            '2002': 0.05}
        }

    # TODO: Get assumptions for heat loss coefficient
    # TODO: INCLUDE HAT LOSS COEFFICIEN ASSUMPTIONS
    # TODO: Include refurbishment of houses --> Change percentage of age distribution of houses -->
    # Which then again influences HLC

    # ============================================================
    #  Demand management assumptions (daily demand shape)
    #  An improvement in load factor improvement can be assigned
    #  for every enduse
    # 
    #  Example: 0.2 --> Improvement in load factor until ey
    # ============================================================
    assumptions['demand_management'] = {}

    # --Residential SubModel
    assumptions['demand_management'] = {

        # Residential submodule
        'rs_space_heating': 0.2,
        'rs_water_heating': 0,
        'rs_lighting': 0,
        'rs_cooking': 0,
        'rs_cold': 0,
        'rs_wet': 0,
        'rs_consumer_electronics': 0,
        'rs_home_computing': 0

        # TODO
    }

    # ============================================================
    #  Scenario drivers
    # ============================================================
    assumptions['scenario_drivers'] = {}

    # --Residential SubModel
    assumptions['scenario_drivers']['rs_submodule'] = {
        'rs_space_heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
        'rs_water_heating': ['population'],
        'rs_lighting': ['population', 'floorarea'],
        'rs_cooking': ['population'],
        'rs_cold': ['population'],
        'rs_wet': ['population'],
        'rs_consumer_electronics': ['population'],
        'rs_home_computing': ['population']
    }

    # --Servicse Submodel
    assumptions['scenario_drivers']['ss_submodule'] = {
        'ss_space_heating': ['floorarea'],
        'ss_water_heating': [],
        'ss_lighting': ['floorarea'],
        'ss_catering': [],
        'ss_computing': [],
        'ss_space_cooling': ['floorarea'],
        'ss_other_gas': ['floorarea'],
        'ss_other_electricity': ['floorarea']
    }

    # --Industry Submodel
    assumptions['scenario_drivers']['is_submodule'] = {
        'is_high_temp_process': ['gva'],
        'is_low_temp_process': ['gva'],
        'is_drying_separation': ['gva'],
        'is_motors': ['gva'],
        'is_compressed_air': ['gva'],
        'is_lighting': ['gva'],
        'is_space_heating': ['gva'],
        'is_other': ['gva'],
        'is_refrigeration': ['gva']
    }

    # Change in floor depending on sector (if no change set to 1, if e.g. 10% decrease change to 0.9)
    # TODO: READ IN FROM READL BUILDING SCENARIOS...
    # TODO: Project future demand based on seperate methodology
    assumptions['ss_floorarea_change_ey_p'] = {
        'community_arts_leisure': 1,
        'education': 1,
        'emergency_services': 1,
        'health': 1,
        'hospitality': 1,
        'military': 1,
        'offices': 1,
        'retail': 1,
        'storage': 1,
        'other': 1
        }

    # =======================================
    # Climate Change assumptions
    # Temperature changes for every month until end year for every month
    # =======================================
    assumptions['climate_change_temp_diff_month'] = [
        0, # January (can be plus or minus)
        0, # February
        0, # March
        0, # April
        0, # May
        0, # June
        0, # July
        0, # August
        0, # September
        0, # October
        0, # November
        0 # December
    ]
    #assumptions['climate_change_temp_diff_month'] = [0] * 12 # No change

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # The diffusion is asumed to be linear
    # ============================================================
    assumptions['rs_t_base_heating'] = {
        'base_yr': 15.5,
        'end_yr': 15.5 #replaced by rs_t_base_heating_ey
        }

    assumptions['ss_t_base_heating'] = {
        'base_yr': 15.5,
        'end_yr': 15.5
        }

    # Cooling base temperature
    assumptions['rs_t_base_cooling'] = {
        'base_yr': 21.0,
        'end_yr': 21.0
        }
    assumptions['ss_t_base_cooling'] = {
        'base_yr': 15.5,
        'end_yr': 15.5
        }

    # Sigmoid parameters for diffusion of penetration of smart meters
    assumptions['base_temp_diff_params'] = {}
    assumptions['base_temp_diff_params']['sig_midpoint'] = 0
    assumptions['base_temp_diff_params']['sig_steeppness'] = 1
    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 0.03 and 0.01 (DECC 2015)
    # NTH: saturation year
    # ============================================================

    # Fraction of population with smart meters (Across all sectors. If wants to be spedified, needs some extra code. Easily possible)
    assumptions['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_p_ey'] = 0.1

    # Long term smart meter induced general savings, purley as a result of having a smart meter
    assumptions['savings_smart_meter'] = {

        # Residential
        'rs_cold': -0.03,
        'rs_cooking': -0.03,
        'rs_lighting': -0.03,
        'rs_wet': -0.03,
        'rs_consumer_electronics': -0.03,
        'rs_home_computing': -0.03,
        'rs_space_heating': -0.03,

        # Service
        'ss_space_heating': -0.03,

        # Industry
        'is_space_heating': -0.03
    }

    # Sigmoid parameters for diffusion of penetration of smart meters
    assumptions['smart_meter_diff_params'] = {}
    assumptions['smart_meter_diff_params']['sig_midpoint'] = 0
    assumptions['smart_meter_diff_params']['sig_steeppness'] = 1

    # ============================================================
    # Heat recycling & Reuse
    # ============================================================
    assumptions['heat_recovered'] = {
        'rs_space_heating': 0.0, # e.g. 0.2 = 20% reduction
        'ss_space_heating': 0.0,
        'is_space_heating': 0.0
    }

    # ---------------------------------------------------------
    # General change in fuel consumption for specific enduses
    # ---------------------------------------------------------
    #   With these assumptions, general efficiency gain (across all fueltypes)
    #   can be defined
    #   for specific enduses. This may be e.g. due to general efficiency gains 
    #   or anticipated increases in demand.
    #   NTH: Specific hanges per fueltype (not across al fueltesp)
    #
    #   Change in fuel until the simulation end year (if no change set to 1, if e.g. 10% decrease change to 0.9)
    # -------------------------------------------------------
    assumptions['enduse_overall_change_ey'] = {

        # Lighting: E.g. how much floor area / % (social change - how much
        # floor area is lighted (smart monitoring)) (smart-lighting)
        # Submodel Residential
        'rs_model': {
            'rs_space_heating': 1,
            'rs_water_heating': 1,
            'rs_lighting': 1,
            'rs_cooking': 1,
            'rs_cold': 1,
            'rs_wet': 1,
            'rs_consumer_electronics': 1,
            'rs_home_computing': 1
        },

        # Submodel Service
        'ss_model': {
            'ss_catering': 1,
            'ss_computing': 1,
            'ss_cooling_ventilation': 1,
            'ss_space_heating': 1,
            'ss_water_heating': 1,
            'ss_lighting': 1,
            'ss_other_gas': 1,
            'ss_other_electricity': 1
        },

        # Submodel Industry
        'is_model': {
            'is_high_temp_process': 1,
            'is_low_temp_process': 1,
            'is_drying_separation': 1,
            'is_motors': 1,
            'is_compressed_air': 1,
            'is_lighting': 1,
            'is_space_heating': 1,
            'is_other': 1,
            'is_refrigeration': 1
        }
    }

    # Specific diffusion information for the diffusion of enduses
    assumptions['other_enduse_mode_info'] = {
        'diff_method': 'linear', # sigmoid or linear
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1
            }
        }

    # ============================================================
    # Technologies & efficiencies
    # ============================================================
    assumptions['tech_list'] = {}

    # Load all technologies
    assumptions['technologies'], assumptions['tech_list'] = read_data.read_technologies(
        data['paths']['path_technologies'])

    # Share of installed heat pumps (ASHP to GSHP) (0.7 e.g. 0.7 ASHP and 0.3 GSHP)
    split_hp_ashp_gshp = 0.5

    # --Assumption how much of technological efficiency is reached
    assumptions['efficiency_achieving_factor'] = 1

    # --Heat pumps
    assumptions['installed_heat_pump'] = tech_related.generate_ashp_gshp_split(
        split_hp_ashp_gshp)

    # Add heat pumps to technologies
    assumptions['technologies'], assumptions['tech_list']['tech_heating_temp_dep'], assumptions['heat_pumps'] = tech_related.generate_heat_pump_from_split(
        [],
        assumptions['technologies'],
        assumptions['installed_heat_pump']
        )

    # ----------
    # Enduse definition list
    # ----------
    assumptions['enduse_space_heating'] = ['rs_space_heating', 'rs_space_heating', 'is_space_heating']
    assumptions['enduse_space_cooling'] = ['rs_space_cooling', 'ss_space_cooling', 'is_space_cooling']
    assumptions['tech_list']['enduse_water_heating'] = ['rs_water_heating', 'ss_water_heating']

    # ============================================================
    # Fuel Stock Definition (necessary to define before model run)
    # Provide for every fueltype of an enduse the share of fuel which is used by technologies
    # ============================================================
    assumptions = assumptions_fuel_shares.assign_by_fuel_tech_p(
        assumptions,
        data
        )

    # ============================================================
    # Scenaric FUEL switches
    # ============================================================
    assumptions['rs_fuel_switches'] = read_data.read_fuel_switches(
        data['paths']['rs_path_fuel_switches'], data['enduses'], data['lookups'])
    assumptions['ss_fuel_switches'] = read_data.read_fuel_switches(
        data['paths']['ss_path_fuel_switches'], data['enduses'], data['lookups'])
    assumptions['is_fuel_switches'] = read_data.read_fuel_switches(
        data['paths']['is_path_fuel_switches'], data['enduses'], data['lookups'])

    # ============================================================
    # Scenaric SERVICE switches
    # ============================================================
    assumptions['rs_share_service_tech_ey_p'], assumptions['rs_enduse_tech_maxL_by_p'], assumptions['rs_service_switches'] = read_data.read_service_switch(
        data['paths']['rs_path_service_switch'], assumptions['rs_specified_tech_enduse_by'])
    assumptions['ss_share_service_tech_ey_p'], assumptions['ss_enduse_tech_maxL_by_p'], assumptions['ss_service_switches'] = read_data.read_service_switch(
        data['paths']['ss_path_service_switch'], assumptions['ss_specified_tech_enduse_by'])
    assumptions['is_share_service_tech_ey_p'], assumptions['is_enduse_tech_maxL_by_p'], assumptions['is_service_switches'] = read_data.read_service_switch(
        data['paths']['is_path_industry_switch'], assumptions['is_specified_tech_enduse_by'])

    # ========================================
    # Other: GENERATE DUMMY TECHNOLOGIES
    # ========================================
    assumptions['rs_fuel_tech_p_by'], assumptions['rs_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['rs_fuel_tech_p_by'], assumptions['rs_specified_tech_enduse_by'])
    assumptions['ss_fuel_tech_p_by'], assumptions['ss_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['ss_fuel_tech_p_by'], assumptions['ss_specified_tech_enduse_by'])
    assumptions['is_fuel_tech_p_by'], assumptions['is_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['is_fuel_tech_p_by'], assumptions['is_specified_tech_enduse_by'])

    # All enduses with dummy technologies
    assumptions['rs_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['rs_fuel_tech_p_by'])
    assumptions['ss_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['ss_fuel_tech_p_by'])
    assumptions['is_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['is_fuel_tech_p_by'])

    # ============================================================
    # Helper functions
    # ============================================================
    ##testing.testing_service_switch_insert(
    # assumptions['ss_fuel_tech_p_by'], assumptions['rs_fuel_switches'])
    ##testing.testing_service_switch_insert(
    # assumptions['ss_fuel_tech_p_by'], assumptions['ss_fuel_switches'])

    # Test if fuel shares sum up to 1 within each fueltype
    testing.testing_fuel_tech_shares(assumptions['rs_fuel_tech_p_by'])
    testing.testing_fuel_tech_shares(assumptions['ss_fuel_tech_p_by'])
    testing.testing_fuel_tech_shares(assumptions['is_fuel_tech_p_by'])

    testing.testing_tech_defined(
        assumptions['technologies'], assumptions['rs_specified_tech_enduse_by'])
    testing.testing_tech_defined(
        assumptions['technologies'], assumptions['ss_specified_tech_enduse_by'])
    testing.testing_tech_defined(
        assumptions['technologies'], assumptions['is_specified_tech_enduse_by'])

    if write_sim_param == True:
        return sim_param, assumptions
    else:
        return assumptions

def update_assumptions(assumptions):
    """Updates calculations based on assumptions

    Note
    ----
    This needs to be run everytime an assumption is changedf

    """
    assumptions['technologies'] = helpers.helper_set_same_eff_all_tech(
        assumptions['technologies'],
        assumptions['efficiency_achieving_factor']
        )

    return assumptions
