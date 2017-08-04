""" This file contains all assumptions of the energy demand model"""
from energy_demand.scripts_data import read_data
from energy_demand.scripts_technologies import technologies_related
from energy_demand.scripts_basic import testing_functions as testing
from energy_demand import assumptions_fuel_shares
from energy_demand.scripts_initalisations import helper_functions
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_assumptions(data):
    """All assumptions of the energy demand model are loaded and added to the data dictionary

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict

    Notes
    -----

    """
    assumptions = {}

    # ============================================================
    # Residential building stock assumptions
    # ============================================================

    # Change in floor area per person up to end_yr (e.g. 0.4 --> 40% increase (the one is added in the model))
    # ASSUMPTION (if minus, check if new buildings are needed)
    assumptions['assump_diff_floorarea_pp'] = 0

    # Dwelling type distribution
    assumptions['assump_dwtype_distr_by'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088}
    assumptions['assump_dwtype_distr_ey'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088}

    # Floor area per dwelling type
    assumptions['assump_dwtype_floorarea'] = {'semi_detached': 96, 'terraced': 82.5, 'flat': 61, 'detached': 147, 'bungalow': 77} # SOURCE?

    # Assumption about age distribution
    assumptions['dwtype_age_distr'] = {2015.0: {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}}

    # TODO: Get assumptions for heat loss coefficient
    # TODO: INCLUDE HAT LOSS COEFFICIEN ASSUMPTIONS
    #assumptions['dwtype_age_distr_by'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr_ey'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr'] = plotting_results.calc_age_distribution()
    # TODO: Include refurbishment of houses --> Change percentage of age distribution of houses --> Which then again influences HLC

    # ============================================================
    #  Scenario driver assumptions (for dwelling stocks where available or per enduse)
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
        'is_high_temp_process': [],
        'is_low_temp_process': [],
        'is_drying_separation': [],
        'is_motors': [],
        'is_compressed_air': [],
        'is_lighting': [],
        'is_space_heating': [],
        'is_other': [],
        'is_refrigeration': []
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
    

    #Testing (test if all provided fueltypes)
    #test_if_enduses_are_assigneddata['rs_all_enduses']
    # ========================================================================================================================
    # Climate Change assumptions
    #     Temperature changes for every month until end year for every month
    # ========================================================================================================================
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
    # The diffusion is asumed to be sigmoid (can be made linear with minor adaptions)
    # ============================================================
    # Heating base temperature
    assumptions['rs_t_base_heating'] = {'base_yr': 15.5, 'end_yr': 15.5}
    assumptions['ss_t_base_heating'] = {'base_yr': 15.5, 'end_yr': 15.5}

    # Cooling base temperature
    assumptions['rs_t_base_cooling'] = {'base_yr': 21.0, 'end_yr': 21.0}
    assumptions['ss_t_base_cooling'] = {'base_yr': 15.5, 'end_yr': 21.0}

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 3 and 10 % (DECC 2015)
    # NTH: saturation year
    # ============================================================

    # Fraction of population with smart meters (Across all sectors. If wants to be spedified, needs some extra code. Easily possible)
    assumptions['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_p_ey'] = 0.1

    # Long term smart meter induced general savings, purley as a result of having a smart meter
    assumptions['general_savings_smart_meter'] = {
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

    # ============================================================
    # HEAT RECYCLING & Reuse
    # ============================================================
    assumptions['heat_recovered'] = {
        'rs_space_heating': 0.0, # e.g. 0.2 = 20% reduction
        'ss_space_heating': 0.0
    }

    # ---------------------------------------------------------------------------------------------------------------------
    # General change in fuel consumption for specific enduses
    # ---------------------------------------------------------------------------------------------------------------------
    #   With these assumptions, general efficiency gain (across all fueltypes) can be defined
    #   for specific enduses. This may be e.g. due to general efficiency gains or anticipated increases in demand.
    #   NTH: Specific hanges per fueltype (not across al fueltesp)
    #
    #   Change in fuel until the simulation end year (if no change set to 1, if e.g. 10% decrease change to 0.9)
    # ---------------------------------------------------------------------------------------------------------------------
    assumptions['enduse_overall_change_ey'] = {

    # Lighting: E.g. how much floor area / % (social change - how much floor area is lighted (smart monitoring)) (smart-lighting)
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

    assumptions['sig_midpoint'] = 0 # Midpoint of sigmoid diffusion
    assumptions['sig_steeppness'] = 1 # Steepness of sigmoid diffusion

    # ============================================================
    # Technologies & efficiencies
    # ============================================================
    assumptions['technology_list'] = {}

    # Load all technologies
    assumptions['technologies'] = read_data.read_technologies(data['path_dict']['path_technologies'], data)

    # Temperature dependency of heat pumps (slope). Derived from Staffell et al. (2012), Fixed tech assumptions (do not change for scenario)
    assumptions['hp_slope_assumption'] = -.08

    # --Assumption how much of technological efficiency is reached
    efficiency_achieving_factor = 1.0

    # --Share of installed heat pumps for every fueltype (ASHP to GSHP) (0.7 e.g. 0.7 ASHP and 0.3 GSHP)
    split_heat_pump_ASHP_GSHP = 0.7

    # --Heat pumps
    assumptions['installed_heat_pump'] = generate_ASHP_GSHP_split(split_heat_pump_ASHP_GSHP, data)
    assumptions['technologies'], assumptions['technology_list']['tech_heating_temp_dep'], assumptions['heat_pumps'] = technologies_related.generate_heat_pump_from_split(data, [], assumptions['technologies'], assumptions['installed_heat_pump'])

    # --Hybrid technologies
    assumptions['technologies'], assumptions['technology_list']['tech_heating_hybrid'], assumptions['hybrid_technologies'] = get_all_defined_hybrid_technologies(
        assumptions,
        assumptions['technologies'],
        hybrid_cutoff_temp_low=-5, #Input parameters
        hybrid_cutoff_temp_high=7)

    # ------------------
    # --Technology list definition
    # ------------------
    # Regular heating technologies which are not dependent on temperature
    assumptions['technology_list']['tech_heating_const'] = [
        'boiler_gas',
        'boiler_electricity',
        'boiler_hydrogen',
        'boiler_biomass',
        'boiler_solid_fuel',
        'boiler_oil',
        'boiler_heat_sold']

    assumptions['technology_list']['primary_heating_electricity'] = ['storage_heater_electricity'] # FROM HES Electricity heating
    assumptions['technology_list']['secondary_heating_electricity'] = ['secondary_heater_electricity'] # FROM HES Electricity heating

    # Regular cooling technlogies...
    assumptions['list_tech_cooling_ventilation'] = ['air_fans_electricity', 'air_condition_electricity', 'air_condition_gas', 'air_condition_oil']
    assumptions['list_tech_ventilation'] = ['air_fans_electricity']
    assumptions['list_tech_cooling'] = ['air_condition_electricity', 'air_condition_gas', 'air_condition_oil'] #[ 'air_condition_electricity']
    #assumptions['list_tech_cooling_const'] = ['cooling_tech_lin']
    #assumptions['list_tech_cooling_temp_dep'] = []

    # Lighting technologies
    assumptions['technology_list']['rs_lighting'] = ['standard_resid_lighting_bulb', 'fluorescent_strip_lightinging', 'halogen_elec', 'energy_saving_lighting_bulb']
    ## Is assumptions['technology_list']['tech_heating_temp_dep'] = [] # To store all temperature dependent heating technology

    # Cooking
    #assumptions['list_tech_rs_cooking_kettle'] = ['kettler']
    #assumptions['list_tech_rs_cooking_microwave'] = ['microwave']
    # ----------
    # Enduse definition list
    # ----------
    assumptions['enduse_space_heating'] = ['rs_space_heating', 'rs_space_heating', 'is_space_heating']
    assumptions['enduse_space_cooling'] = ['rs_space_cooling', 'ss_space_cooling', 'is_space_cooling']
    assumptions['technology_list']['enduse_water_heating'] = ['rs_water_heating', 'ss_water_heating']

    # Helper function
    assumptions['technologies'] = helper_functions.helper_set_same_eff_all_tech(assumptions['technologies'], efficiency_achieving_factor)

    # ============================================================
    # Fuel Stock Definition (necessary to define before model run)
    #    --Provide for every fueltype of an enduse the share of fuel which is used by technologies
    # ============================================================
    assumptions = assumptions_fuel_shares.get_fuel_stock_definition(assumptions, data)

    # ============================================================
    # Scenaric FUEL switches
    # ============================================================
    assumptions['rs_fuel_switches'] = read_data.read_assump_fuel_switches(data['path_dict']['rs_path_fuel_switches'], data)
    assumptions['ss_fuel_switches'] = read_data.read_assump_fuel_switches(data['path_dict']['ss_path_fuel_switches'], data)
    assumptions['is_fuel_switches'] = read_data.read_assump_fuel_switches(data['path_dict']['is_path_fuel_switches'], data)

    # ============================================================
    # Scenaric SERVICE switches
    # ============================================================
    assumptions['rs_share_service_tech_ey_p'], assumptions['rs_enduse_tech_maxL_by_p'], assumptions['rs_service_switches'] = read_data.read_service_switch(data['path_dict']['rs_path_service_switch'], assumptions['rs_all_specified_tech_enduse_by'])
    assumptions['ss_share_service_tech_ey_p'], assumptions['ss_enduse_tech_maxL_by_p'], assumptions['ss_service_switches'] = read_data.read_service_switch(data['path_dict']['ss_path_service_switch'], assumptions['ss_all_specified_tech_enduse_by'])
    assumptions['is_share_service_tech_ey_p'], assumptions['is_enduse_tech_maxL_by_p'], assumptions['is_service_switches'] = read_data.read_service_switch(data['path_dict']['is_path_industry_switch'], assumptions['is_all_specified_tech_enduse_by'])

    # ========================================
    # Other: GENERATE DUMMY TECHNOLOGIES
    # ========================================
    #add dummy technology if no technologies are defined per enduse
    assumptions['rs_fuel_enduse_tech_p_by'], assumptions['rs_all_specified_tech_enduse_by'], rs_dummy_techs = scrap_add_dumm_tech(assumptions['rs_fuel_enduse_tech_p_by'], assumptions['rs_all_specified_tech_enduse_by'], assumptions['rs_fuel_enduse_tech_p_by'])
    assumptions['ss_fuel_enduse_tech_p_by'], assumptions['ss_all_specified_tech_enduse_by'], ss_dummy_techs = scrap_add_dumm_tech(assumptions['ss_fuel_enduse_tech_p_by'], assumptions['ss_all_specified_tech_enduse_by'], assumptions['ss_fuel_enduse_tech_p_by'])
    assumptions['is_fuel_enduse_tech_p_by'], assumptions['is_all_specified_tech_enduse_by'], is_dummy_techs = scrap_add_dumm_tech(assumptions['is_fuel_enduse_tech_p_by'], assumptions['is_all_specified_tech_enduse_by'], assumptions['is_fuel_enduse_tech_p_by'])

    # Add dummy technologies to technology stock
    assumptions['technologies'] = scrap_add_dummy_to_tech_stock(rs_dummy_techs, assumptions['technologies'])
    assumptions['technologies'] = scrap_add_dummy_to_tech_stock(ss_dummy_techs, assumptions['technologies'])
    assumptions['technologies'] = scrap_add_dummy_to_tech_stock(is_dummy_techs, assumptions['technologies'])

    # All enduses with dummy technologies
    assumptions['rs_dummy_enduses'] = scrap_get_dummy_enduses(assumptions['rs_fuel_enduse_tech_p_by'])
    assumptions['ss_dummy_enduses'] = scrap_get_dummy_enduses(assumptions['ss_fuel_enduse_tech_p_by'])
    assumptions['is_dummy_enduses'] = scrap_get_dummy_enduses(assumptions['is_fuel_enduse_tech_p_by'])


    # ============================================================
    # Helper functions
    # ============================================================
    #TODO: TESTING IF ALL TECHNOLOGIES Available are assigned in service switch
    ##testing.testing_correct_service_switch_entered(assumptions['ss_fuel_enduse_tech_p_by'], assumptions['rs_fuel_switches'])
    ##testing.testing_correct_service_switch_entered(assumptions['ss_fuel_enduse_tech_p_by'], assumptions['ss_fuel_switches'])


    # Test if fuel shares sum up to 1 within each fueltype
    testing.testing_fuel_tech_shares(assumptions['rs_fuel_enduse_tech_p_by'])
    testing.testing_fuel_tech_shares(assumptions['ss_fuel_enduse_tech_p_by'])
    testing.testing_fuel_tech_shares(assumptions['is_fuel_enduse_tech_p_by'])

    # ----------
    # Testing
    # ----------
    testing.testing_tech_defined(assumptions['technologies'], assumptions['rs_all_specified_tech_enduse_by'])
    testing.testing_tech_defined(assumptions['technologies'], assumptions['ss_all_specified_tech_enduse_by'])
    testing.testing_tech_defined(assumptions['technologies'], assumptions['is_all_specified_tech_enduse_by'])
    testing.testing_switch_technologies(assumptions['hybrid_technologies'], assumptions['rs_fuel_enduse_tech_p_by'], assumptions['rs_share_service_tech_ey_p'], assumptions['technologies'])

    return assumptions

def get_all_defined_hybrid_technologies(assumptions, technologies, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
    """All hybrid technologies and their charactersitics are defined

    The low and high temperature technology is defined, whereby the high temperature technology
    must be a heatpump.

    Cut off temperatures can be defined to change the share of service for each
    technology at a given temperature (see doumentation for more information)

    So far, the standard heat pump is only electricity. Can be changed however
    #TODO: DEFINE WITH REAL VALUES

    #Assumption on share of service provided by lower temperature technology on a national scale in by

    Notes
    ------

    """

    hybrid_tech = {
        'hybrid_gas_electricity': {
            "tech_low_temp": 'boiler_gas',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_gas',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
        'hybrid_hydrogen_electricity': {
            "tech_low_temp": 'boiler_hydrogen',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_hydrogen',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
        'hybrid_biomass_electricity': {
            "tech_low_temp": 'boiler_biomass',
            "tech_high_temp": 'heat_pumps_electricity',
            "hybrid_cutoff_temp_low": hybrid_cutoff_temp_low,
            "hybrid_cutoff_temp_high": hybrid_cutoff_temp_high,
            "average_efficiency_national_by": get_average_eff_by(
                tech_low_temp='boiler_biomass',
                tech_high_temp='heat_pumps_electricity',
                assump_service_share_low_tech=0.2,
                assumptions=assumptions
                )
            },
    }

    # Hybrid technologies
    hybrid_technologies = hybrid_tech.keys()

    # Add hybrid technologies to technological stock and define other attributes
    for tech_name, tech in hybrid_tech.items():

        print("Add hybrid technology to technology stock {}".format(tech_name))
        # Add other technology attributes
        technologies[tech_name] = tech
        technologies[tech_name]['eff_achieved'] = 1
        technologies[tech_name]['diff_method'] = 'linear'

        # Select market entry of later appearing technology
        entry_tech_low = assumptions['technologies'][tech['tech_low_temp']]['market_entry']
        entry_tech_high = assumptions['technologies'][tech['tech_high_temp']]['market_entry']

        if entry_tech_low < entry_tech_high:
            technologies[tech_name]['market_entry'] = entry_tech_high
        else:
            technologies[tech_name]['market_entry'] = entry_tech_low

    return technologies, list(hybrid_technologies), hybrid_tech

def generate_ASHP_GSHP_split(split_factor, data):
    """Assing split for each fueltype of heat pump technologies

    Parameters
    ----------
    split_factor : float
        Fraction of ASHP to GSHP
    data : dict
        Data

    Returns
    --------
    installed_heat_pump : dict
        Ditionary with split of heat pumps for every fueltype

    Info
    -----
    The heat pump technologies need to be defined.

    """
    ASHP_fraction = split_factor
    GSHP_fraction = 1 - split_factor

    installed_heat_pump = {
        data['lu_fueltype']['hydrogen']: {
            'heat_pump_ASHP_hydro': ASHP_fraction,
            'heat_pump_GSHP_hydro': GSHP_fraction
            },
        data['lu_fueltype']['electricity']: {
            'heat_pump_ASHP_electricity': ASHP_fraction,
            'heat_pump_GSHP_electricity': GSHP_fraction
            },
        data['lu_fueltype']['gas']: {
            'heat_pump_ASHP_gas': ASHP_fraction,
            'heat_pump_GSHP_gas': GSHP_fraction
            },
    }

    return installed_heat_pump

#TODO: Make that HLC can be improved
# Assumption share of existing dwelling stock which is assigned new HLC coefficients


def get_average_eff_by(tech_low_temp, tech_high_temp, assump_service_share_low_tech, assumptions):
    """Calculate average efficiency for base year of hybrid technologies for overall national energy service calculation

    Parameters
    ----------
    tech_low_temp : str
        Technology for lower temperatures
    tech_high_temp : str
        Technology for higher temperatures
    assump_service_share_low_tech : float
        Assumption about the overall share of the service provided
        by the technology used for lower temperatures
        (needs to be between 1.0 and 0)

    Returns
    -------
    av_eff : float
        Average efficiency of hybrid tech

    Infos
    -----
    It is necssary to define an average efficiency of hybrid technologies to calcualte
    the share of total energy service in base year for the whole country. Because
    the input is fuel for the whole country, it is not possible to calculate the
    share for individual regions
    """
    # The average is calculated for the 10 temp difference intercept (Because input for heat pumps is provided for 10 degree differences)
    average_h_diff_by = 10

    # Service shares
    service_share_low_temp_tech = assump_service_share_low_tech
    service_share_high_temp_tech = 1 - assump_service_share_low_tech

    # Efficiencies of technologies of hybrid tech
    if tech_low_temp in assumptions['technology_list']['tech_heating_temp_dep']:
        eff_tech_low_temp = technologies_related.eff_heat_pump(
            assumptions['hp_slope_assumption'],
            average_h_diff_by,
            assumptions['technologies'][tech_low_temp]['eff_by'])
    else:
        eff_tech_low_temp = assumptions['technologies'][tech_low_temp]['eff_by']

    if tech_high_temp in assumptions['technology_list']['tech_heating_temp_dep']:
        eff_tech_high_temp = technologies_related.eff_heat_pump(
            m_slope=assumptions['hp_slope_assumption'],
            h_diff=average_h_diff_by,
            intersect=assumptions['technologies'][tech_high_temp]['eff_by'])
    else:
        eff_tech_high_temp = assumptions['technologies'][tech_high_temp]['eff_by']

    # Weighted average efficiency
    av_eff = service_share_low_temp_tech * eff_tech_low_temp + service_share_high_temp_tech * eff_tech_high_temp

    return av_eff

def scrap_add_dumm_tech(tech_p_by, all_specified_tech_enduse_by, fuel_enduse_tech_p_by):
    dummpy_techs = []

    for end_use in tech_p_by:
        installed_tech = False
        for fueltype in tech_p_by[end_use]:
            if tech_p_by[end_use][fueltype] != {}:
                installed_tech = True

        if not installed_tech:

            for ff in tech_p_by[end_use]:
                create_dummy_tech = False

                #if fuel provided, otherwise leave empty
                '''fuels_enduse_sector = fuel_raw_data_enduses[end_use]
                if isinstance(fuels_enduse_sector, dict):
                    for sector in fuels_enduse_sector:
                        if fuels_enduse_sector[sector] >= 0:
                            create_dummy_tech == True
                else:
                    if fuels_enduse_sector > 0:
                        create_dummy_tech == True
                #if fuel_raw_data_enduses[end_use][ff] == 0: #data['rs_fuel_raw_data_enduses']
                #    continue
                if create_dummy_tech == True:
                '''

                dummpy_tech = "dummy__{}__{}__{}__tech".format(end_use, ff, installed_tech)
                tech_p_by[end_use][ff] = {dummpy_tech: 1.0} # Whole fuel to dummy tech
                dummpy_techs.append(dummpy_tech)
                all_specified_tech_enduse_by[end_use].append(dummpy_tech)

    return tech_p_by, all_specified_tech_enduse_by, dummpy_techs

def scrap_add_dummy_to_tech_stock(dummy_techs, technologies):

    for dummy_tech in dummy_techs:
        technologies[dummy_tech] = {
            'fuel_type': int(dummy_tech.split("__")[2]),
            'eff_by': 1.0,
            'eff_ey': 1.0,
            'eff_achieved': 1.0,
            'diff_method': 'sigmoid',
            'market_entry': 2015
        }

    return technologies

def scrap_get_dummy_enduses(enduse_tech_p_by):
    dummy_enduses = set([])
    for enduse in enduse_tech_p_by:
        for fueltype in enduse_tech_p_by[enduse]:
            for tech in enduse_tech_p_by[enduse][fueltype]:
                if tech[:5] == 'dummy':
                    dummy_enduses.add(enduse)
                    continue

    return list(dummy_enduses)
