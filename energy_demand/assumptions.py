""" This file contains all assumptions of the energy demand model"""
import pprint
import numpy as np
import energy_demand.main_functions as mf

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
    assumptions['assump_dwtype_distr_by'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #base year
    assumptions['assump_dwtype_distr_ey'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #end year

    # Floor area per dwelling type
    assumptions['assump_dwtype_floorarea'] = {'semi_detached': 96, 'terraced': 82.5, 'flat': 61, 'detached': 147, 'bungalow': 77} # SOURCE?

    # Assumption about age distribution
    assumptions['dwtype_age_distr'] = {2015.0: {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}}

    # TODO: Get assumptions for heat loss coefficient
    # TODO: INCLUDE HAT LOSS COEFFICIEN ASSUMPTIONS
    #assumptions['dwtype_age_distr_by'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr_ey'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    #assumptions['dwtype_age_distr'] = mf.calc_age_distribution()
    # TODO: Include refurbishment of houses --> Change percentage of age distribution of houses --> Which then again influences HLC

    # ============================================================
    # Dwelling stock related scenario driver assumptions
    # ============================================================
    assumptions['resid_scen_driver_assumptions'] = {
        'resid_space_heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
        'resid_water_heating': ['pop'],
        'resid_lighting': ['pop', 'floorarea'],
        'resid_cooking': ['pop'],
        'resid_cold': ['pop'],
        'resid_wet': ['pop'],
        'resid_consumer_electronics': ['pop'],
        'resid_home_computing': ['pop'],
    }

    # ========================================================================================================================
    # Climate Change assumptions
    #     Temperature changes for every month until end year for every month
    # ========================================================================================================================
    assumptions['climate_change_temp_diff_month'] = [0] * 12 # No change

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
    # The diffusion is asumed to be sigmoid (can be made linear with minor adaptions)
    # ============================================================
    # Heating base temperature
    assumptions['t_base_heating_resid'] = {
        'base_yr': 15.5,
        'end_yr': 15.5
    }

    # Cooling base temperature
    assumptions['t_base_cooling_resid'] = {
        'base_yr': 21.0,
        'end_yr': 21.0
    }

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Demand elasticities (Long-term resid_elasticities)
    # https://en.wikipedia.org/wiki/Price_elasticity_of_demand (e.g. -5 is much more sensitive to change than -0.2)
    # ============================================================
    assumptions['resid_elasticities'] = {
        'resid_space_heating': 0,
        'resid_water_heating' : 0,
        'water' : 0,
        'resid_cooking' : 0,                  #-0.05, -0.1. - 0.3 #Pye et al. 2014
        'resid_lighting': 0,
        'resid_cold': 0,
        'resid_wet': 0,
        'resid_consumer_electronics': 0,      #-0.01, -0.1. - 0.15 #Pye et al. 2014
        'resid_home_computing': 0,            #-0.01, -0.1. - 0.15 #Pye et al. 2014
    }

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 3 and 10 % (DECC 2015)
    # NTH: saturation year
    # ============================================================

    # Fraction of population with smart meters
    assumptions['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_p_ey'] = 0.1

    # Long term smart meter induced general savings, purley as a result of having a smart meter
    assumptions['general_savings_smart_meter'] = {
        'resid_cold': -0.03,
        'resid_cooking': -0.03,
        'resid_lighting': -0.03,
        'resid_wet': -0.03,
        'resid_consumer_electronics': -0.03,
        'resid_home_computing': -0.03,
        'resid_space_heating': -0.03
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
        'resid_space_heating': 1,
        'resid_water_heating': 1,
        'resid_lighting': 1,
        'resid_cooking': 1,
        'resid_cold': 1,
        'resid_wet': 1,
        'resid_consumer_electronics': 1,
        'resid_home_computing': 1,
    }

    # Specifid diffusion information
    assumptions['other_enduse_mode_info'] = {
        'diff_method': 'linear', # sigmoid or linear
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1
            }}

    assumptions['sig_midpoint'] = 0 # Midpoint of sigmoid diffusion
    assumptions['sig_steeppness'] = 1 # Steepness of sigmoid diffusion

    # ============================================================
    # Technologies & Efficiencies
    # ============================================================
    assumptions['technologies'] = mf.read_technologies(data['path_dict']['path_assumptions_tech_resid'], data) # Load all technologies

    # --Assumption how much of technological efficiency is reached
    efficiency_achieving_factor = 1.0


    # --Share of installed heat pumps for every fueltype (ASHP to GSHP) (0.7 e.g. 0.7 ASHP and 0.3 GSHP)
    split_heat_pump_ASHP_GSHP = 0.7

    # Further technology related input
    assumptions['heat_pump_slope_assumption'] = -.08    # Temperature dependency of heat pumps (slope). Derived from Staffell et al. (2012),  Fixed tech assumptions (do not change for scenario)
    assumptions['list_tech_heating_temp_dep'] = []      # To store all temperature dependent heating technology
    assumptions['list_tech_heating_const'] = ['boiler_gas', 'boiler_elec', 'boiler_hydrogen', 'boiler_biomass']

    assumptions['list_tech_cooling_const'] = ['cooling_tech_lin']
    assumptions['list_tech_cooling_temp_dep'] = []
    #assumptions['enduse_resid_space_heating'] = ['resid_space_heating']
    #assumptions['enduse_space_cooling'] = ['resid_space_cooling']

    # --Helper functions
    assumptions['heat_pump_stock_install'] = helper_assign_ASHP_GSHP_split(split_heat_pump_ASHP_GSHP, data)
    assumptions['technologies'], assumptions['list_tech_heating_temp_dep'] = mf.generate_heat_pump_from_split(data, assumptions['list_tech_heating_temp_dep'], assumptions['technologies'], assumptions['heat_pump_stock_install'])
    assumptions['technologies'] = helper_define_same_efficiencies_all_tech(assumptions['technologies'], eff_achieved_factor=efficiency_achieving_factor)



    # ============================================================
    # Fuel switches
    # ============================================================
    assumptions['resid_fuel_switches'] = mf.read_csv_assumptions_fuel_switches(data['path_dict']['path_fuel_switches'], data) # Read in switches
    assumptions['fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['fuel_raw_data_resid_enduses'], len(data['fuel_type_lu']))

    # --Provide for every fueltype of an enduse the share of fuel which is used by technologies

    # ---Residential space heating
    assumptions['fuel_enduse_tech_p_by']['resid_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['fuel_enduse_tech_p_by']['resid_space_heating'][data['lu_fueltype']['electricity']] = {'boiler_elec': 0.98, 'av_heat_pump_electricity': 0.02}  #  Hannon 2015, heat-pump share in uk
    assumptions['fuel_enduse_tech_p_by']['resid_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['fuel_enduse_tech_p_by']['resid_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 0.0}
    assumptions['fuel_enduse_tech_p_by']['resid_space_heating'][data['lu_fueltype']['bioenergy_waste']] = {'boiler_biomass': 0.0}

    # ---resid_lighting
    #assumptions['fuel_enduse_tech_p_by']['resid_lighting'][data['lu_fueltype']['electricity']] = {'halogen_elec': 0.5, 'standard_resid_lighting_bulb': 0.5}




    # ---Residential cooking
    assumptions['list_enduse_tech_cooking'] = []
    '''assumptions['list_enduse_tech_cooking'] = ['cooking_hob_elec', 'cooking_hob_gas']
    assumptions['enduse_resid_cooking'] = ['resid_cooking']
    assumptions['fuel_enduse_tech_p_by']['resid_cooking'][data['lu_fueltype']['electricity']] = {'cooking_hob_elec': 1.0}
    assumptions['fuel_enduse_tech_p_by']['resid_cooking'][data['lu_fueltype']['gas']] = {'cooking_hob_gas': 1.0}
    '''

    # Helper function: Add all technologies with correct fueltype to assumptions['fuel_enduse_tech_p_by'] if not already added
    ###assumptions['fuel_enduse_tech_p_by'] = add_all_tech_to_base_year_stock(assumptions['fuel_enduse_tech_p_by'], assumptions['technologies'])

    #assumptions['heat_pump_technologies'] = ['heat_pump_ASHP_elec', 'heat_pump_GSHP_elec'] # Share of ASHP to GSHP

    # TODO: ADD dummy technology for all enduses where no technologies are defined
    # TODO: Assert if all defined technologies are in assumptions['list_tech_heating_const'] or similar...
    #IF new technologs is introduced: assign_shapes_tech_stock()


    # ============================================================
    # Service Switches
    # The share of energy service is the same across all regions
    # ============================================================

    # Load assumptions on service switches
    assumptions = mf.read_csv_assumptions_service_switch(data['path_dict']['path_service_switch'], assumptions)

    print("--Service in base year of each technology")
    print(assumptions['service_tech_by_p'])

    # Get technologies with increased, decreased and constant service
    data = mf.get_diff_direct_installed(assumptions['service_tech_by_p'], assumptions['share_service_tech_ey_p'], data)



    # Helper functions
    data['tech_lu_resid'] = create_lu_technologies(assumptions, assumptions['technologies'], data)

    return assumptions

def helper_assign_ASHP_GSHP_split(split_factor, data):
    """Assing split for each fueltyp of heat pump technologies

    Parameters
    ----------
    split_factor : float
        Fraction of ASHP to GSHP
    data : dict
        Data

    Returns
    --------
    heat_pump_stock_install : dict
        Ditionary with split of heat pumps for every fueltype

    Info
    -----
    The heat pump technologies need to be defined.

    """
    ASHP_fraction = split_factor
    GSHP_fraction = 1 - split_factor

    heat_pump_stock_install = {
        data['lu_fueltype']['hydrogen']: {'heat_pump_ASHP_hydro': ASHP_fraction, 'heat_pump_GSHP_hydro': GSHP_fraction},
        data['lu_fueltype']['gas']: {'heat_pump_ASHP_elec': ASHP_fraction, 'heat_pump_GSHP_elec': GSHP_fraction},
        data['lu_fueltype']['electricity']: {'heat_pump_ASHP_gas': ASHP_fraction, 'heat_pump_GSHP_gas': GSHP_fraction},
    }

    return heat_pump_stock_install

def add_all_tech_to_base_year_stock(fuel_enduse_tech_p_by, technologies):
    """All defines technologies are added if they are not manually definied

    If fueltypes are manually defined, copy these values. Otherwise insert the technologies but assign no fuel to them
    TODO: SO far all technologies are added in every enduse. not realistic...
    """
    for technology in technologies:

        # Fueltype of technology
        fueltype_tech = technologies[technology]['fuel_type']

        for enduse in fuel_enduse_tech_p_by:
            if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech]:
                fuel_enduse_tech_p_by[enduse][fueltype_tech][technology] = 0.0
    return fuel_enduse_tech_p_by

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

def create_lu_technologies(assumptions, technologies, data):
    """Helper function: Create lookup-table for technologies
    """
    out_dict = {}
    for tech_id, technology in enumerate(technologies, 1000):
        out_dict[technology] = tech_id
    return out_dict

def initialise_dict_fuel_enduse_tech_p_by(fuel_raw_data_resid_enduses, nr_of_fueltypes):
    """Helper function to define stocks for all enduse and fueltype

    Parameters
    ----------
    fuel_raw_data_resid_enduses : dict
        Provided fuels
    nr_of_fueltypes : int
        Nr of fueltypes
    
    Returns
    -------
    fuel_enduse_tech_p_by : dict

    """
    fuel_enduse_tech_p_by = {}

    all_enduses_with_fuels = fuel_raw_data_resid_enduses.keys()

    for enduse in all_enduses_with_fuels:
        fuel_enduse_tech_p_by[enduse] = {}
        for fueltype in range(nr_of_fueltypes):
            fuel_enduse_tech_p_by[enduse][fueltype] = {}

    return fuel_enduse_tech_p_by

def helper_define_same_efficiencies_all_tech(tech_assump, eff_achieved_factor=1):
    """Helper function to assing same achieved efficiency
    """
    for technology in tech_assump:
        tech_assump[technology]['eff_achieved'] = eff_achieved_factor
    return tech_assump
    