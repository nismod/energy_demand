""" This file contains all assumptions of the energy demand model"""
import copy
import numpy as np

import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_assumptions(data, data_external):
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
    # Residential dwelling stock assumptions
    # ============================================================

    # Building stock related, assumption of change in floor area up to end_yr (Checked)
    assumptions['assump_diff_floorarea_pp'] = 0 # [%] If e.g. 0.4 --> 40% increase (the one is added in the model)  ASSUMPTION (if minus, check if new buildings are needed)

    # Dwelling type distribution
    assumptions['assump_dwtype_distr_by'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #base year
    assumptions['assump_dwtype_distr_ey'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #end year

    # Floor area per dwelling type
    assumptions['assump_dwtype_floorarea'] = {'semi_detached': 96, 'terraced': 82.5, 'flat': 61, 'detached': 147, 'bungalow': 77} # SOURCE?

    # TODO: Get assumptions for heat loss coefficient
    # TODO: INCLUDE HAT LOSS COEFFICIEN ASSUMPTIONS
    #assumptions['dwtype_age_distr_by'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr_ey'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr'] = mf.calc_age_distribution()
    assumptions['dwtype_age_distr'] = {
        2015.0: {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}} #TODO READ IN

    # TODO: Include refurbishment of houses --> Change percentage of age distribution of houses --> Which then again influences HLC

    # ========================================================================================================================
    # Climate Change assumptions
    #     Temperature changes for every month until end year for every month
    # ========================================================================================================================
    assumptions['climate_change_temp_diff_month'] = [-3] * 12 # No change

    '''# Hotter winter, cooler summers
    assumptions['climate_change_temp_diff_month'] = [
        1, # January
        1, # February
        1, # March
        1, # April
        1, # May
        1, # June
        -1, # July
        -1, # August
        -1, # September
        -1, # October
        -1, # November
        -1 # December
    ]'''

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # (so far the diffusion is asumed to be sigmoid (can be made linear with minor adaptions))
    # ============================================================
    # Heating base temperature
    assumptions['t_base_heating'] = {
        'base_yr': 15.5,
        'end_yr': 15.5
    }

    # Cooling base temperature
    assumptions['t_base_cooling'] = {
        'base_yr': 21.0,
        'end_yr': 21.0
    }



    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #RESIDENTIAL


    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Dwelling stock related scenario driver assumptions
    # ============================================================
    assumptions['resid_scen_driver_assumptions'] = {
        'space_heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
        'water_heating': ['pop'],
        'lighting': ['pop', 'floorarea'],
        'cooking': ['pop'],
        'cold': ['pop'],
        'wet': ['pop'],
        'consumer_electronics': ['pop'],
        'home_computing': ['pop'],
    }

    # ============================================================
    # Demand elasticities (Long-term resid_elasticities) # #TODO: Elasticties over time change? Not implemented so far ()
    # https://en.wikipedia.org/wiki/Price_elasticity_of_demand (e.g. -5 is much more sensitive to change than -0.2)
    # ============================================================
    resid_elasticities = {
        'space_heating': 0,
        'water_heating' : 0,
        'water' : 0,
        'cooking' : 0,                  #-0.05, -0.1. - 0.3 #Pye et al. 2014
        'lighting': 0,
        'cold': 0,
        'wet': 0,
        'consumer_electronics': 0,      #-0.01, -0.1. - 0.15 #Pye et al. 2014
        'home_computing': 0,            #-0.01, -0.1. - 0.15 #Pye et al. 2014
    }
    assumptions['resid_elasticities'] = resid_elasticities      # Add dictionaries to assumptions


    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 3 and 10 % (DECC 2015)
    # ============================================================

    # Fraction of population with smart meters NTH: saturation year
    assumptions['smart_meter_p_by'] = 0.1 #base year
    assumptions['smart_meter_p_ey'] = 0.1 #end year

    # Long term smart meter induced general savings, purley as a result of having a smart meter
    assumptions['general_savings_smart_meter'] = {
        'cold': -0.03,
        'cooking': -0.03,
        'lighting': -0.03,
        'wet': -0.03,
        'consumer_electronics': -0.03,
        'home_computing': -0.03,
        'space_heating': -0.03
    }

    # ============================================================
    # Technologies and their efficiencies over time
    # ============================================================

    # Fixed assumptions of technologies (do not change for scenario)
    assumptions['heat_pump_slope_assumption'] = -.08 # Temperature dependency (slope). Derived from SOURCE #GROUND SOURCE HP

    # Load all technologies and their efficiencies from csv file
    assumptions['technologies'] = mf.read_csv_assumptions_technologies(data['path_dict']['path_assumptions_STANDARD'], data)

    # --Helper Function to write same achieved efficiency for all technologies
    assumptions['technologies'] = helper_define_same_efficiencies_all_tech(assumptions['technologies'])

    # Other function
    data = create_lu_technologies(assumptions, data) # - LU Function Create lookup for technologies (That technologies can be replaced for calculating with arrays)
    assumptions = create_lu_fueltypes(assumptions) # - LU  Create lookup for fueltypes

    # ---------------------------
    # Fuel switches residential sector
    # ---------------------------

    # Read in switches from csv file
    assumptions['resid_fuel_switches'] = mf.read_csv_assumptions_fuel_switches(data['path_dict']['path_FUELSWITCHES'], data)

    # ---------------------------------------------------------------------------------------------------------------------
    # General change in fuel consumption for specific enduses
    # ---------------------------------------------------------------------------------------------------------------------
    #   With these assumptions, general efficiency gain (across all fueltypes) can be defined
    #   for specific enduses. This may be e.g. due to general efficiency gains or anticipated increases in demand.
    #   NTH: Specific hanges per fueltype (not across al fueltesp)
    #
    #   Change in fuel until the simulation end year (if no change set to 1, if e.g. 10% decrease change to 0.9)
    # ---------------------------------------------------------------------------------------------------------------------
    assumptions['sig_midpoint'] = 0 # Midpoint of sigmoid diffusion
    assumptions['sig_steeppness'] = 1 # Steepness of sigmoid diffusion

    assumptions['enduse_overall_change_ey'] = {
        'space_heating': 1,
        'water_heating': 1,
        'lighting': 1,
        'cooking': 1,
        'cold': 1,
        'wet': 1,
        'consumer_electronics': 1,
        'home_computing': 1,
    }

    # Specifid diffusion information
    assumptions['other_enduse_mode_info'] = {
        'diff_method': 'linear', # sigmoid or linear
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1
            }}
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Fuel Switches assumptions
    # ---------------------------------------------------------------------------------------------------------------------
    # Provide for every fueltype of an enduse the share of fuel which is used by technologies
    # Example: From electricity used for heating, 80% is used for heat pumps, 80% for electric boilers)
    # ---------------------------------
    # Assert: - if market enntry is not before base year, wheater always 100 % etc.. --> Check if fuel switch input makes sense
    assumptions = helper_create_stock(assumptions, data['fuel_raw_data_resid_enduses'], len(data['fuel_type_lu'])) # Initiate

    # Technologies used
    assumptions['list_tech_heating_const'] = ['gas_boiler', 'elec_boiler', 'gas_boiler2', 'elec_boiler2', 'oil_boiler', 'hydrogen_boiler', 'hydrogen_boiler2']
    assumptions['list_tech_heating_temp_dep'] = ['heat_pump']

    # ---Space Heating
    assumptions['fuel_enduse_tech_p_by']['space_heating'][data['lu_fueltype']['gas']] = {'gas_boiler': 1.0}

    # Provides shares of fuel within each fueltype
    assumptions['fuel_enduse_tech_p_by']['space_heating'][data['lu_fueltype']['electricity']] = {'elec_boiler2': 0.2, 'elec_boiler': 0.8, 'heat_pump': 0.02}  # {'heat_pump': 0.02, 'elec_boiler': 0.98}  H annon 2015, heat-pump share in uk
    assumptions['fuel_enduse_tech_p_by']['space_heating'][data['lu_fueltype']['oil']] = {'oil_boiler': 1.0}
    assumptions['fuel_enduse_tech_p_by']['space_heating'][data['lu_fueltype']['hydrogen']] = {'hydrogen_boiler': 0.0, 'hydrogen_boiler2': 0.0}

    # ---Lighting
    #assumptions['fuel_enduse_tech_p_by']['lighting'][data['lu_fueltype']['electricity']] = {'halogen_elec': 0.5, 'standard_lighting_bulb': 0.5}


    # TODO: ADD dummy technology for all enduses where no technologies are defined
    # TODO: Assert if all defined technologies are in assumptions['list_tech_heating_const'] or similar...

    #IF new technologs is introduced: assign_shapes_to_tech_stock(), 
    return assumptions



#TODO: Make that HLC can be improved
# Assumption share of existing dwelling stock which is assigned new HLC coefficients

def get_hlc(dw_type, age):
    """Calculates the linearly derived hlc depending on age and dwelling type

    Parameters
    ----------
    dw_type : int
        Dwelling type
    age : int
        Age of dwelling

    Returns
    -------
    hls : Heat loss coefficient [W/m2 * K]

    Notes
    -----
    Source: Linear trends derived from Table 3.17 ECUK Tables
    https://www.gov.uk/government/collections/energy-consumption-in-the-uk
    """
    # Dict with linear fits for all different dwelling types {dw_type: [slope, constant]}
    linear_fits_hlc = {
        0: [-0.0223, 48.292],       # Detached
        1: [-0.0223, 48.251],       # Semi-Detached
        2: [-0.0223, 48.063],       # Terraced Average
        3: [-0.0223, 47.02],        # Flats
        4: [-0.0223, 48.261],       # Bungalow
        }

    # Get linearly fitted value
    hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]

    return hlc


'''
        'back_boiler' : 0.01,
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gain to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gain to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb
'''
'''

    assumptions['eff_ey'] = {
        # -- heating boiler ECUK Table 3.19
        'back_boiler' : 0.01,
        #'combination_boiler' : 0.0,
        'condensing_boiler' : 0.5,
        #'condensing_combination_boiler' : 0.0,


        # -- lighting
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulb
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb


        # -- wet
        #'boiler_gas': 0.5,
        #'boiler_oil': 0.5,
        #'boiler_condensing': 0.5,
        #'boiler_biomass': 0.5,

        # -- consumer electronics
        #'ASHP': 0.5,
        #'HP_ground_source': 0.5,
        #'HP_air_source': 0.5,
        #'HP_gas': 0.5,

        # -- home_computing
        #'micro_CHP_elec': 0.5,
        #'micro_CHP_thermal': 0.5,

        'gas_boiler': 0.3,
        'elec_boiler': 0.5,
        'heat_pump_m': -0.1,
        'heat_pump_b': 22.0
        #'heat_pump': get_heatpump_eff(data_external, 0.1, 8)
        }
'''

def create_lu_technologies(assumptions, data):
    """Create lookup-table for technologies
    """
    data['tech_lu'] = {}
    for tech_id, technology in enumerate(assumptions['technologies'], 1000):
        data['tech_lu'][technology] = tech_id

    return data

def create_lu_fueltypes(assumptions):
    """Create lookup-table for fueltypes
    """
    assumptions['tech_fueltype'] = {}
    for technology in assumptions['technologies']:
        assumptions['tech_fueltype'][technology] = assumptions['technologies'][technology]['fuel_type']

    return assumptions

def helper_create_stock(assumptions, fuel_raw_data_resid_enduses, nr_of_fueltypes):
    """Helper function to define stocks for all enduse and fueltypes
    """
    all_enduses_with_fuels = fuel_raw_data_resid_enduses.keys()
    assumptions['fuel_enduse_tech_p_by'] = {}
    for enduse in all_enduses_with_fuels: #data['resid_enduses']:
        assumptions['fuel_enduse_tech_p_by'][enduse] = {}
        for fueltype in range(nr_of_fueltypes):
            assumptions['fuel_enduse_tech_p_by'][enduse][fueltype] = {}
    return assumptions

def helper_define_same_efficiencies_all_tech(tech_assump):
    factor_efficiency_achieved = 1.0
    for technology in tech_assump:
        tech_assump[technology]['eff_achieved'] = factor_efficiency_achieved
    return tech_assump
    