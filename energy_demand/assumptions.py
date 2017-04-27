""" This file contains all assumptions of the energy demand model"""
import numpy as np
import copy
import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325
# 
# Input: Share of fuel consumption to be replaced by EndYear
# The share which needs to be replaced (e.g. 20%) shrinks because of gain in efficencies --> In every sy share is relevant
# 
# 1. Define technological composition in base year (technologies and fractions)
#   - if not known, assumpe dummy technology with efficiency 1
# 
# 2. Calculate fuel change with constant technology mix but increase in efficiencies of these technologies
#   - if dummy technology, no change is made
#
# 3. 

# Eff: Iterate years: SUM_sy(efficiency of technology in year * share in year * fuel_share_20%_tech_eff_considered)
# --> Or make assumption that share of replaced consumption is always replaced in every year with newest technology (problem for long-lasting technologies)
#

def load_assumptions(data, data_external):
    """All assumptions of the energy demand model are loaded and added to the data dictionary

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict

    Notes
    -----
    # TODO: INCLUDE HAT LOSS COEFFICIEN ASSUMPTIONS
    """
    assumptions = {}

    # ============================================================
    # Technology diffusion assumptions (same parameters are used for all the cases where a sigmoid diffusion is assumed)
    # ============================================================
    assumptions['sig_midpoint'] = 0 # Midpoint of sigmoid diffusion
    assumptions['sig_steeppness'] = 1 # Steepness of sigmoid diffusion



    # ============================================================
    # Residential dwelling stock assumptions
    # ============================================================

    # Building stock related, assumption of change in floor area up to end_yr (Checked)
    assumptions['assump_diff_floorarea_pp'] = 0.0 # [%] If e.g. 0.4 --> 40% increase (the one is added in the model)  ASSUMPTION (if minus, check if new buildings are needed)

    # Dwelling type distribution
    assumptions['assump_dwtype_distr_by'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #base year
    assumptions['assump_dwtype_distr_ey'] = {'semi_detached': 0.26, 'terraced': 0.283, 'flat': 0.203, 'detached': 0.166, 'bungalow': 0.088} #end year

    # Floor area per dwelling type
    assumptions['assump_dwtype_floorarea'] = {'semi_detached': 96, 'terraced': 82.5, 'flat': 61, 'detached': 147, 'bungalow': 77} # SOURCE?

    # TODO: Get assumptions for heat loss coefficient

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # ============================================================
    # Heating base temperature
    assumptions['t_base_heating'] = {
        'base_yr': 15.5,
        'end_yr': 15.5
    }

    # Heating base temperature
    assumptions['t_base_cooling'] = {
        'base_yr': 21.0,
        'end_yr': 21.0
    }

    # TODO: Climate scneario data (mutage temperature data from this)

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #RESIDENTIAL


    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Dwelling stock related scenario driver assumptions
    # ============================================================
    assumptions['resid_scen_driver_assumptions'] = {
        'heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
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
        'heating': 0,
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
    # Assumptions about future technologies
    # ============================================================
    # # Fuel consumption per person
    # # Inifital efficiency
    # # Final efficiency
    # # Market entry
    # # Enduse
    # # Saturation year
    # # Penetration (linar/sigmoid)
    # # Percentage of diffusion in population




    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 3 and 10 % (DECC 2015)
    # ============================================================

    # Fraction of population with smart meters #TODO: Make possibie to provide saturation year
    assumptions['smart_meter_p_by'] = 0.9
    assumptions['smart_meter_p_ey'] = 1.0
    #assumptions['smart_meter_saturation_year'] = 2020 # TODO: Year the penetration rated id to be achieved

    # Long term smart meter induced general savings (purley as a result of having a smart meter)
    assumptions['general_savings_smart_meter'] = {
        'cold': 0.03,
        'cooking': 0.03,
        'lighting': 0.03,
        'wet': 0.03,
        'consumer_electronics': 0.03,
        'home_computing': 0.03,
        'heating':0.03
    }

    # ============================================================
    # Technologies and their efficiencies over time
    # ============================================================

    assumptions['heat_pump_slope_assumption'] = -.08

    assumptions['technologies'] = {
        'heat_pump': {
            'eff_by': 5.5, # At a temp diff of 20
            'eff_ey': 8,
            'eff_achieved': 0.5,
            'saturation_yr': 2050,
            'diff_method': 'sigmoid', # sigmoid
            'diff_param': {
                'linear': 'possible_parameters_could_be_passed',
                'sigmoid': {
                    'sig_midpoint': 0,
                    'sig_steeppness': 1
                    }}

            },
        'back_boiler': {
            'eff_by': 0.7, # At a temp diff of 20
            'eff_ey': 0.9,
            'eff_achieved': 1.0,
            'saturation_yr': 2050,
            'diff_method': 'linear', # sigmoid
            'diff_param': {
                'linear': 'possible_parameters_could_be_passed',
                'sigmoid': {
                    'sig_midpoint': 0,
                    'sig_steeppness': 1
                    }}

            }

    }

    # Efficiencies in base year
    assumptions['eff_by'] = {
        'back_boiler' : 0.01,
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gain to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gain to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        'gas_boiler': 0.3,
        'elec_boiler': 0.5,
        'heat_pump_m': -0.1,
        'heat_pump_b': 22.0
        #'heat_pump': get_heatpump_eff(data_external, 0.1, 8)
        }

    # --Efficiencies in end year
    assumptions['eff_ey'] = {
        'back_boiler' : 0.01,
        'condensing_boiler' : 0.5,

        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulb
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        'gas_boiler': 0.3,
        'elec_boiler': 0.5,
        'heat_pump_m': -0.1, # TODO Derive heat pump curve from lit
        'heat_pump_b': 22.0
        #'heat_pump': get_heatpump_eff(data_external, 0.1, 8)
        }


    # --Factor to change the actual achieved efficiency improvements of technologies (same for all technologies)
    factor_efficiency_achieved = 1.0

    assumptions['eff_achieved_resid'] = {}
    for i in assumptions['eff_ey']:
        assumptions['eff_achieved_resid'][i] = factor_efficiency_achieved

    # Define fueltype of each technology
    assumptions['tech_fueltype'] = {
        #Lighting
        'heat_pump': data['lu_fueltype']['electricity'],
        'back_boiler' : data['lu_fueltype']['electricity']
    }
    '''
        'LED': data['lu_fueltype']['electricity'],
        'halogen_elec': data['lu_fueltype']['electricity'],
        'standard_lighting_bulb': data['lu_fueltype']['electricity'],
        'fluorescent_strip_lightinging': data['lu_fueltype']['electricity'],
        'energy_saving_lighting_bulb': data['lu_fueltype']['electricity'],
        'LED' : data['lu_fueltype']['electricity'],

        #test
        'tech_A' : data['lu_fueltype']['gas'],
        'tech_B' : data['lu_fueltype']['gas'],
        
        'condensing_boiler' : data['lu_fueltype']['electricity'],

        'gas_boiler': data['lu_fueltype']['gas'],
        'elec_boiler': data['lu_fueltype']['electricity']
    }
    '''

    # Create lookup for technologies (That technologies can be replaced for calculating with arrays) Helper function
    data['tech_lu'] = {}
    for tech_id, tech in enumerate(assumptions['tech_fueltype'], 1000):
        data['tech_lu'][tech] = tech_id



    # ---------------------------------------------------------------------------------------------------------------------
    # General change in fuel consumption for specific enduses
    #
    # With these assumptions, general efficiency gain (across all fueltypes) can be defined
    # for specific enduses. This may be e.g. due to general efficiency gains or anticipated increases in demand.
    # NTH: Specific hanges per fueltype (not across al fueltesp)
    # ---------------------------------------------------------------------------------------------------------------------

    # Change in fuel until the simulation end year ( if no change : 1, if e.g. 10% decrease change to 0.9)
    assumptions['other_enduse_specific_change_ey'] = {
        'heating': 1,
        'water_heating': 1,
        'lighting': 1,
        'cooking': 1,
        'cold': 1,
        'wet': 1,
        'consumer_electronics': 1,
        'home_computing': 1,
    }

    # Choice of diffusion
    assumptions['other_enduse_mode_choice'] = 'linear' # sigmoid or linear

    # Specifid diffusion information
    assumptions['other_enduse_mode_info'] = {
        'linear': 'possible_parameters_could_be_passed',
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1
            }}

    # ---------------------------------------------------------------------------------------------------------------------
    # Fuel Switches assumptions
    # --------------------- ------------------------------------------------------------------------------------------------
    switch_list = []

    # Modes to calculate efficiencies to be replaced

    # Input for a single switch
    switch_list.append(
        {
            'enduse': 'heating',
            'fueltype': 1,
            'tech_remove': 'gas_tech',  # 'average_mode', 'lowest_mode', 'average_all_except_to_be_replaced?
            'tech_install': 'heat_pump',
            'fuel_share_till_ey': 0.5
            }
        )

    switch_list.append( # Replacing 60% of electricity with fluorescent_strip_lightinging
        {
            'enduse': 'lighting',
            'fueltype': 2,
            'tech_remove': 'lowest_mode', # 'average_mode', 'lowest_mode',
            'tech_install': 'fluorescent_strip_lightinging',
            'fuel_share_ey': 0.6
            #'state_2010':
            #'state_2030':
            }
        )

    # Installed current technology to be replaced
    assumptions['tech_install'] = {
        'heating': 'heat_pump',
        'water_heating': 'tech_A'
    }

    # --Technologies which are replaced within an enduse and fueltype

    # Possible switches:
    #  e.g. 20% of fueltype Gas in Enduse Heating to Technology A
    #
    #
    # Only one technology can be assigned (# If more than one necs)
    assumptions['tech_remove_dict'] = {
        'heating':{
            0: 'gas_boiler',
            1: 'gas_boiler',
            2: 'gas_boiler', # Tech A gets replaced by Tech B
            3: 'gas_boiler',
            4: 'gas_boiler',
            5: 'gas_boiler',
            6: 'gas_boiler',
            7: 'gas_boiler'
        }
    }

    # --Share of fuel types for each enduse (across all fueltypes??) TODO IMPRTANT
    fuel_type_p_by = generate_fuel_type_p_by(data) # Generate fuel distribution of base year for every end_use # Total ED for service for each fueltype
    assumptions['fuel_type_p_by'] = mf.convert_to_array(fuel_type_p_by)

    # --Reduction fraction of each fuel in each enduse compared to base year.( -0.2 --> Minus share)
    assump_fuel_frac_ey = {
        'heating': {
            '0' : 0,
            '1' : 0.0,
            '2' : 0.0, # replaced ( - 20%)
            '3' : 0,
            '4' : 0,
            '5' : 0,
            '6' : 0,
            '7':  0
            }
    }

    # Helper function - Replace all enduse from assump_fuel_frac_ey
    fuel_type_p_ey = {}
    for enduse in fuel_type_p_by:
        if enduse not in assump_fuel_frac_ey:
            fuel_type_p_ey[enduse] = np.array(list(fuel_type_p_by[enduse].items()), dtype=float)
        else:
            array_fuel_switch_assumptions = np.array(list(assump_fuel_frac_ey[enduse].items()), dtype=float)
            factor_to_multiply_fuel_p = abs(array_fuel_switch_assumptions - 1)

            # Multiply fuel percentage with share in fueltype
            fuel_type_p_ey[enduse] = assumptions['fuel_type_p_by'][enduse] * factor_to_multiply_fuel_p
            fuel_type_p_ey[enduse][:, 0] = fuel_type_p_ey[enduse][:, 0] #Copy fuel indices

    assumptions['fuel_type_p_ey'] = fuel_type_p_ey

    print("fuel_type_p_by:" + str(assumptions['fuel_type_p_by']['heating']))
    print("---------------------")
    print(fuel_type_p_ey['heating'])
    # TODO: Write function to insert fuel switches  
    # TODO: Assert if always 100% #assert p_tech_by['boiler_A'] + p_tech_by['boiler_B'] == 1.0
    #print(assumptions['fuel_type_p_ey']['lighting'])



    # ----------------------------------
    # Technology Stock Definition
    #
    # Provide the share of total end-use fuel by technology within fueltype
    # ---------------------------------
    assumptions['tech_enduse_by'] = {}
    # Iterate enduses
    for enduse in data['resid_enduses']:
        assumptions['tech_enduse_by'][enduse] = {}
        for fueltype in range(len(data['fuel_type_lu'])):
            assumptions['tech_enduse_by'][enduse][fueltype] = {}
        


    # -- Lighting, Residential (enduse_fuel_split) Base Year
    '''assumptions['tech_enduse_by']['lighting'][data['lu_fueltype']['electricity']] = {
        'LED': 0.01,
        'halogen_elec': 0.37,
        'standard_lighting_bulb': 0.35,
        'fluorescent_strip_lightinging': 0.09,
        'energy_saving_lighting_bulb': 0.18
        }
    '''
    # Technology assumptions ()
    # Share of total fuel of one technology (e.g. standard_lighting_bulb)


    #assumptions['tech_enduse_by']['heating'][1] = {'back_boiler': 1.0, 'heat_pump': 0.0}
    assumptions['tech_enduse_by']['heating'][1] = {'heat_pump': 1.0}
    assumptions['tech_enduse_by']['heating'][2] = {'back_boiler': 1.0, 'heat_pump': 0.0}

    # --Technological split in end_yr  # FOR END YEAR ALWAYS SAME NR OF TECHNOLOGIES AS INITIAL YEAR (TODO: ASSERT IF ALWAYS 100%)
    assumptions['tech_enduse_ey'] = copy.deepcopy(assumptions['tech_enduse_by'])

    #assumptions['tech_enduse_ey']['lighting'][2] = {'LED': 0.01, 'halogen_elec': 0.37, 'standard_lighting_bulb': 0.35, 'fluorescent_strip_lightinging': 0.09, 'energy_saving_lighting_bulb': 0.18}
    #tech_enduse_ey['water_heating'][2] = {'back_boiler': 0.1, 'condensing_boiler': 0.9}

    #assumptions['tech_enduse_ey']['heating'][2] = {'back_boiler': 1.0, 'heat_pump': 0.0}










    # *********************************************************************************
    # If from yearly fuel of heating tech to heatpumps --> Iterate daily fuel os of gas --> Calc efficiency of this day and multiply with fueltype

    def calc_enduse_fuel_tech_by(enduses, eff_by, fuels, tech_enduse):
        """Assign correct fueltype to technologies and calculate share of technologies

        Iterate enduses and calculate share of total enduse fuels for each technology

        'enduse': {'tech_A': % of total enduse, } #Across all fuels and technologies
        """
        enduse_fuel_tech_by = {}

        #TODO: Add all technologies of all fueltypes found in this enduse

        # Itreate enduse
        for enduse in enduses:
            enduse_fuel_tech_by[enduse] = {}
            tot_enduse_fuel = np.sum(fuels[enduse]) # total fuel enduse

            for fueltype in range(len(fuels[enduse])):
                fuels_fueltype = fuels[enduse][fueltype][0]

                # Iterate tech in fueltype
                overall_tech_share = 0
                for tech in tech_enduse[enduse][fueltype]:
                    overall_tech_share += tech_enduse[enduse][fueltype][tech] / eff_by[tech]

                if tech_enduse[enduse][fueltype] != {}: # if no tech availbale
                    for tech in tech_enduse[enduse][fueltype]: # Calculate fuel within tech in fueltype

                        # Calculate share per fueltype
                        share_tech_fueltype = (1.0 / overall_tech_share) * (tech_enduse[enduse][fueltype][tech] / eff_by[tech])

                        # Convert to absolute fuels per fueltype
                        fuel_fueltype_tech = share_tech_fueltype * fuels_fueltype #Fuels

                        # Calculate relative compared to tot fuel of enduse
                        enduse_fuel_tech_by[enduse][tech] = (1.0 / tot_enduse_fuel ) * fuel_fueltype_tech # Fraction of total fuel

        #TODO: Assert that 100%

        return enduse_fuel_tech_by

    '''# Technolies for single enduse
    tech_enduse_by['water_heating'][1] = {'gas_boiler': 0.9, 'tech_B': 0.1}
    tech_enduse_by['water_heating'][2] = {'heat_pump': 0.5, 'condensing_boiler': 0.5}

    #Calculate enduse fuel split per technology
    enduse_fuel_tech_by = calc_enduse_fuel_tech_by(data['resid_enduses'], eff_by, data['fuel_raw_data_resid_enduses'], tech_enduse_by)


    enduse_fuel_tech_ey = {'water_heating': {'heat_pump': 0.8, 'condensing_boiler': 0.1, 'gas_boiler': 0.1}} #Absolute enduse

    # Apply fuel switches
    #fuel = apply_fuel_switches(enduse_fuel_tech_by, enduse_fuel_tech_ey)
    assump_fuel_frac_ey = {'water_heating': {data['lu_fueltype']['gas']: -0.2}} #Assumptions to change enduse

    # Change enduse_fuel_matrix_ey for fuel switches
    #calc_enduse_fuel_tech_ey_fuel_switches
    

    # DIFFUSION, Fuel Shares,


    print(enduse_fuel_tech_by)
    '''
    #prnt(":.abs")

    # Add assumptions to data dict
    data['assumptions'] = assumptions
    return data







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






# ------------- Helper functions
def generate_fuel_type_p_by(data):
    """Assumption helper function to generate percentage fuel distribution for every enduse of base year"""

    fuel_data = data['fuel_raw_data_resid_enduses']
    out_dict = {}

    for enduse in fuel_data:
        out_dict[enduse] = {}
        sum_fueltype = np.sum(fuel_data[enduse]) # Total fuel of enduse
        if sum_fueltype != 0:
            fuels_in_p = fuel_data[enduse] / sum_fueltype
        else:
            fuels_in_p = fuel_data[enduse] # all zeros

        for fueltype, fuel in enumerate(fuels_in_p):
            out_dict[enduse][fueltype] = float(fuel) # Convert to %

    return out_dict


# ----------- functions SSSSSSSSSSSSSSTUF



def calc_share_of_tot_yearly_fuel_for_hp(): #data_external, 0.2, 4
    """
    Calculate efficiency for temperature dependent technology:

    I. Get y_h shape in percentage of REGULAR BOILERS and calculate HEATFUEL for every day (or take percentages)
    --> Problem dass heat pumps unterschiedliche Daily Shape

    II. Calculate heat demand factor (efficiency_heat):

    SUM(HEATFUEL) / SUM_every_h(eff_h * HEATFUEL_h) = coeff_by #Also % can be taken becose does not matter if real fuel or percentages
    (weighted coefficient)

    III. Calculate total fuel for each technology

    Fuel_frac_hp = frac_hp * (TOTFUEL * coeff_by)
    Fruel_fact_reg_boilers = frac_boilers * (TOTFUEL)

    (Relationship between input tonn equivalents and output heat)




    """


    pass

def generate_shape_reg_boilers():

    pass

def generate_shape_HP():
    """Generate HP d shape for a year based on BY gasfuel
    Assumption: BY: HP == 0%

    1. Get daily gas demand for heat from daily averaged h_temperatures (and assume everything used for heating) based on correlation
     1.b.) Calculate absolute fuels for every day
     1.c.) Convert absolute fuels to % of y (generate daily shape)
     1.d.) Take REGIONAL acualt Gas demand to calculate h gas demand
    2. Take hourly gas shapes from Samson for gas technologs
    3. Calculate hourly fuel demand
    4. Iterate hours and calc: fuel demand h * (eff_gas tech / eff_hp_h)
    5. Convert absolute fuel demand to %


    @ Use same for electric heatiing
    """
    pass


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

        # -- cold

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