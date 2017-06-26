""" This file contains all assumptions of the energy demand model"""
import sys
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
    #assumptions['dwtype_age_distr'] = mf.calc_age_distribution()
    # TODO: Include refurbishment of houses --> Change percentage of age distribution of houses --> Which then again influences HLC

    # ============================================================
    #  Dwelling stock related scenario driver assumptions
    # ============================================================

    # RESIDENTIALSECTOR
    assumptions['rs_scen_driver_assumptions'] = {
        'rs_space_heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
        'rs_water_heating': ['pop'],
        'rs_lighting': ['pop', 'floorarea'],
        'rs_cooking': ['pop'],
        'rs_cold': ['pop'],
        'rs_wet': ['pop'],
        'rs_consumer_electronics': ['pop'],
        'rs_home_computing': ['pop'],
    }



    # ..SERVICE SECTOR

    # Scenario drivers #TODO: SCENARIO DRIVERS POP? GENERATE TABLE
    assumptions['ss_scen_driver_assumptions'] = {
        'sscatering': [],
        'ss_computing': [],
        'ss_space_cooling': ['floorarea'],
        'ss_water_heating': [],
        'ss_space_heating': ['floorarea'],
        'ss_lighting': ['floorarea'],
        'ss_other_gas': ['floorarea'],
        'ss_other_electricity': ['floorarea']
    }

    # Change in floor depending on sector (if no change set to 1, if e.g. 10% decrease change to 0.9)
    # TODO: READ IN FROM READL BUILDING SCENARIOS...
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
    assumptions['rs_t_base_heating'] = {'base_yr': 15.5, 'end_yr': 15.5}
    assumptions['ss_t_base_heating'] = {'base_yr': 15.5, 'end_yr': 15.5}

    # Cooling base temperature
    assumptions['rs_t_base_cooling'] = {'base_yr': 21.0, 'end_yr': 21.0}
    assumptions['ss_t_base_cooling'] = {'base_yr': 15.5, 'end_yr': 15.5}

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Demand elasticities (Long-term rs_elasticities)
    # https://en.wikipedia.org/wiki/Price_elasticity_of_demand (e.g. -5 is much more sensitive to change than -0.2)
    # ============================================================
    assumptions['rs_elasticities'] = {
        'rs_space_heating': 0,
        'rs_water_heating' : 0,
        'rs_cooking' : 0,                  #-0.05, -0.1. - 0.3 #Pye et al. 2014
        'rs_lighting': 0,
        'rs_cold': 0,
        'rs_wet': 0,
        'rs_consumer_electronics': 0,      #-0.01, -0.1. - 0.15 #Pye et al. 2014
        'rs_home_computing': 0,            #-0.01, -0.1. - 0.15 #Pye et al. 2014
    }
    #TODO: ADD FOR SERVICE SECTOR

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
        'rs_cold': -0.03,
        'rs_cooking': -0.03,
        'rs_lighting': -0.03,
        'rs_wet': -0.03,
        'rs_consumer_electronics': -0.03,
        'rs_home_computing': -0.03,
        'rs_space_heating': -0.03
    }

    # ============================================================
    # HEAT RECYCLING
    # ============================================================
    #assumptions['rs_heat_recovered] = 0.0
    #assumptions['rs_heat_recovered] =
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
        'residential_sector': {
            'rs_space_heating': 1,
            'rs_water_heating': 1,
            'rs_lighting': 1,
            'rs_cooking': 1,
            'rs_cold': 1,
            'rs_wet': 1,
            'rs_consumer_electronics': 1,
            'rs_home_computing': 1
        },
        'service_sector': {
            'ss_catering': 1,
            'ss_computing': 1,
            'ss_space_cooling': 1, #Cooling and ventilation
            'ss_water_heating': 1,
            'ss_space_heating': 1,
            'ss_lighting': 1,
            'ss_other_gas': 1,
            'ss_other_electricity': 1
        }
    }

    # Specific diffusion information
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
    # Load all technologies
    assumptions['technologies'] = mf.read_technologies(data['path_dict']['path_technologies'], data)

    # Temperature dependency of heat pumps (slope). Derived from Staffell et al. (2012),  Fixed tech assumptions (do not change for scenario)
    assumptions['hp_slope_assumpt'] = -.08    

    # --Assumption how much of technological efficiency is reached
    efficiency_achieving_factor = 1.0

    # --Share of installed heat pumps for every fueltype (ASHP to GSHP) (0.7 e.g. 0.7 ASHP and 0.3 GSHP)
    split_heat_pump_ASHP_GSHP = 0.7

    # Create av heat pump technologies and list with heat pumps
    assumptions['heat_pump_stock_install'] = helper_assign_ASHP_GSHP_split(split_heat_pump_ASHP_GSHP, data)
    assumptions['technologies'], assumptions['list_tech_heating_temp_dep'] = mf.generate_heat_pump_from_split(data, [], assumptions['technologies'], assumptions['heat_pump_stock_install'])

    # ------------------
    # --Technology type definition
    # ------------------
    assumptions['list_tech_heating_const'] = ['boiler_gas', 'boiler_elec', 'boiler_hydrogen', 'boiler_biomass']
    assumptions['list_tech_cooling_const'] = ['cooling_tech_lin']
    assumptions['list_tech_cooling_temp_dep'] = []
    assumptions['list_tech_heating_hybrid'] = ['hybrid_gas_elec']

    ## Is assumptions['list_tech_heating_temp_dep'] = [] # To store all temperature dependent heating technology
    #assumptions['list_tech_rs_lighting'] = ['halogen_elec', 'standard_rs_lighting_bulb']
    assumptions['enduse_space_heating'] = ['rs_space_heating', 'rs_space_heating']
    assumptions['enduse_space_cooling'] = ['rs_space_cooling', 'ss_space_heating']

    # ---------------------------------
    # --Hybrid technologies assumptions
    #   The technology for higher temperatures is always a heat pump
    # ---------------------------------
    assumptions['hybrid_gas_elec'] = {
        "tech_low_temp": 'boiler_gas',
        "tech_high_temp": 'av_heat_pump_electricity',
        "hybrid_cutoff_temp_low": -5,
        "hybrid_cutoff_temp_high": 7,
        "average_efficiency_national_by": get_average_eff_by(
            'boiler_gas', #Provide same tech as above
            'av_heat_pump_electricity',
            0.2, #Assumption on share of service provided by lower temperature technology on a national scale in by
            assumptions
        )
    }

    # --Helper functions
    assumptions['technologies'] = helper_define_same_efficiencies_all_tech(assumptions['technologies'], eff_achieved_factor=efficiency_achieving_factor)

    # ============================================================
    # Fuel Stock Definition (necessary to define before model run)
    #    --Provide for every fueltype of an enduse the share of fuel which is used by technologies
    # ============================================================
    assumptions['rs_fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['rs_all_enduses'], data['nr_of_fueltypes'])
    assumptions['ss_fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['ss_all_enduses'], data['nr_of_fueltypes'])


    # ------------------
    # RESIDENTIAL SECTOR
    # ------------------

    #---Residential space heating
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['gas']] = {'hybrid_gas_elec': 0.02, 'boiler_gas': 0.98}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['electricity']] = {'hybrid_gas_elec': 0.02, 'boiler_elec': 0.98, 'av_heat_pump_electricity': 0}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 0.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['bioenergy_waste']] = {'boiler_biomass': 0.0}

    # ---Residential lighting 
    #assumptions['rs_fuel_enduse_tech_p_by']['rs_lighting'][data['lu_fueltype']['electricity']] = {'halogen_elec': 0.5, 'standard_rs_lighting_bulb': 0.5}

    # ---Residential cooking
    #assumptions['list_enduse_tech_cooking'] = []
    '''assumptions['list_enduse_tech_cooking'] = ['cooking_hob_elec', 'cooking_hob_gas']
    assumptions['enduse_rs_cooking'] = ['rs_cooking']
    assumptions['rs_fuel_enduse_tech_p_by']['rs_cooking'][data['lu_fueltype']['electricity']] = {'cooking_hob_elec': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_cooking'][data['lu_fueltype']['gas']] = {'cooking_hob_gas': 1.0}
    '''
    assumptions['all_specified_tech_enduse_by'] = helper_function_get_all_specified_tech(assumptions['rs_fuel_enduse_tech_p_by'])

    # ------------------
    # SERVICE SECTOR
    # ------------------
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['gas']] = {'hybrid_gas_elec': 0.02, 'boiler_gas': 0.98}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['electricity']] = {'hybrid_gas_elec': 0.02, 'boiler_elec': 0.98, 'av_heat_pump_electricity': 0}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 0.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['bioenergy_waste']] = {'boiler_biomass': 0.0}


    # ============================================================
    # Scenaric FUEL switches
    # ============================================================
    assumptions['rs_fuel_switches'] = mf.read_csv_assumptions_fuel_switches(data['path_dict']['rs_path_fuel_switches'], data) # Read in switches
    assumptions['ss_fuel_switches'] = mf.read_csv_assumptions_fuel_switches(data['path_dict']['ss_path_fuel_switches'], data) # Read in switches

    # Get criteria which enduese has fuel switches
    #assumptions[]
    # ============================================================
    # Scenaric SERVICE switches
    # ============================================================

    # Get criteria which enduse has service switches
    assumptions['rs_share_service_tech_ey_p'], assumptions['rs_enduse_tech_maxL_by_p'], assumptions['rs_service_switches'] = mf.read_csv_assumptions_service_switch(data['path_dict']['rs_path_service_switch'], assumptions)
    assumptions['ss_share_service_tech_ey_p'], assumptions['ss_enduse_tech_maxL_by_p'], assumptions['ss_service_switches'] = mf.read_csv_assumptions_service_switch(data['path_dict']['ss_path_service_switch'], assumptions)

    # ============================================================
    # Helper functions
    # ============================================================
    assumptions['tech_lu'] = create_lu_technologies(assumptions['technologies'])


    # Testing
    testing_all_defined_tech_in_tech_stock(assumptions['technologies'], assumptions['all_specified_tech_enduse_by'])
    testing_all_defined_tech_in_switch_in_fuel_definition(assumptions['rs_fuel_enduse_tech_p_by'], assumptions['rs_share_service_tech_ey_p'], assumptions['technologies'], assumptions)

    return assumptions



def helper_assign_ASHP_GSHP_split(split_factor, data):
    """Assing split for each fueltype of heat pump technologies

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

    if dw_type is None or age is None:
        print("The HLC could not be calculated of a dwelling")

        return None

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

def create_lu_technologies(technologies):
    """Helper function: Create lookup-table for technologies
    """
    out_dict = {}
    for tech_id, technology in enumerate(technologies, 1000):
        out_dict[technology] = tech_id
    return out_dict

def initialise_dict_fuel_enduse_tech_p_by(all_enduses_with_fuels, nr_of_fueltypes):
    """Helper function to define stocks for all enduse and fueltype

    Parameters
    ----------
    all_enduses_with_fuels : dict
        Provided fuels
    nr_of_fueltypes : int
        Nr of fueltypes

    Returns
    -------
    fuel_enduse_tech_p_by : dict

    """
    fuel_enduse_tech_p_by = {}

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

def helper_function_get_all_specified_tech(fuel_enduse_tech_p_by):
    """Collect all technologies across all fueltypes for all endueses where a service share is defined for the end_year
    """
    all_defined_tech_service_ey = {}
    for enduse in fuel_enduse_tech_p_by:
        all_defined_tech_service_ey[enduse] = []
        for fueltype in fuel_enduse_tech_p_by[enduse]:
            all_defined_tech_service_ey[enduse].extend(fuel_enduse_tech_p_by[enduse][fueltype])

    return all_defined_tech_service_ey

def testing_all_defined_tech_in_tech_stock(technologies, all_specified_tech_enduse_by):
    """Test if all defined technologies of fuels are also defined in technology stock
    """
    for enduse in all_specified_tech_enduse_by:
        for tech in all_specified_tech_enduse_by[enduse]:
            if tech not in technologies:
                sys.exit("Error: The technology '{}' for which fuel was attributed is not defined in technology stock".format(tech))
    return

def get_average_eff_by(tech_low_temp, tech_high_temp, assump_service_share_low_tech, assumptions):
    """Calculate average efficiency for base year of hybrid technologies for overall national energy service calculation

    Parameters
    ----------
    tech_low_temp : str
        Technology for lower temperatures
    tech_high_temp : str
        Technology for higher temperatures
    assump_service_share_low_tech : float
        Assumption of the service provided by the technology used for lower temperatures (needs to be between 1.0 and 0)

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
    # The average is calculated for the 0-intercept
    average_h_diff = 0 #TODO: HEAT PUMP IF PROVIDED not for 0 differeence but for 10, use 10 degree temp here

    # Service shares
    service_share_low_temp_tech = assump_service_share_low_tech
    service_share_high_temp_tech = 1 - assump_service_share_low_tech

    # Efficiencies of technologies of hybrid tech
    if tech_low_temp in assumptions['list_tech_heating_temp_dep']:
        eff_tech_low_temp = mf.eff_heat_pump(
            assumptions['hp_slope_assumpt'],
            average_h_diff,
            assumptions['technologies'][tech_low_temp]['eff_by'] #b, treated as eff
        )
    else:
        eff_tech_low_temp = assumptions['technologies'][tech_low_temp]['eff_by']

    if tech_high_temp in assumptions['list_tech_heating_temp_dep']:
        eff_tech_high_temp = mf.eff_heat_pump(
            assumptions['hp_slope_assumpt'],
            average_h_diff,
            assumptions['technologies'][tech_high_temp]['eff_by'] #b, treated as eff
        )
    else:
        eff_tech_high_temp = assumptions['technologies'][tech_high_temp]['eff_by']

    # Weighted average efficiency
    av_eff = service_share_low_temp_tech * eff_tech_low_temp + service_share_high_temp_tech * eff_tech_high_temp

    return av_eff

def testing_all_defined_tech_in_switch_in_fuel_definition(fuel_enduse_tech_p_by, share_service_tech_ey_p, technologies, assumptions):
    """Test if there is a technology share defined in end year which is not listed in technology fuel stock definition
    """
    for enduse, technology_enduse in share_service_tech_ey_p.items():
        for technology in technology_enduse:
            # If hybrid tech
            if technology in assumptions['list_tech_heating_hybrid']:
                tech_high = assumptions[technology]['tech_high_temp']
                tech_low = assumptions[technology]['tech_low_temp']
                fueltype_tech_low = technologies[tech_low]['fuel_type']
                fueltype_tech_high = technologies[tech_high]['fuel_type']

                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech_low].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech_high].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
            else:
                fueltype_tech = technologies[technology]['fuel_type']
                if technology not in fuel_enduse_tech_p_by[enduse][fueltype_tech].keys():
                    sys.exit("Error: The defined technology '{}' in service switch is not defined in fuel technology stock assumptions".format(technology))
    return
