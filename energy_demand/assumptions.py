""" This file contains all assumptions of the energy demand model"""
import numpy as np
import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325

'''
----------------------
# RESIDENTIAL END_USES
----------------------

The ECUK table serves as the most important national energy demand input.

[y]   Yearly variation
[h]   Shape of each hour in a day
[d]   Shape of each day in a year
[p_h] Shape of heak day in hours
[p_d] Relationship between demand of peak day and demand in a year

ECUK TABLE FUEL DATA                              Shapes
====================                              ==================
                                                  [y] ?? Wheater Generator

heating (Table 3.8)                 -->     [h,p_h] Sansom (2014) which is based on Carbon Trust field data:
                                                  [d,p_d] National Grid (residential data based on CWW):

Water_heating (Table 3.8)                 -->     [d,h,p_d,p_h] HES: Water heating (shapes for all fuels)

Cooking (Table 3.8)                       -->     [d,h,p_d,p_h] HES: Cooking (shapes for all fuels)

Lighting (Table 3.8)                      -->     [d,h,p_d,p_h] HES: Lighting

Appliances (elec) (Table 3.02)
  cold (table 3.8)                        -->     [d,h,p_d,p_h] HES: Cold appliances
  wet (table 3.8)                         -->     [d,h,p_d,p_h] HES: Washing/drying
  consumer_electronics (table 3.8)        -->     [d,h,p_d,p_h] HES: Audiovisual
  home_computing (table 3.8)              -->     [d,h,p_d,p_h] HES: ICT

----------------------
# Service END_USES
----------------------

ECUK TABLE FUEL DATA                              Shapes
====================                              ==================

Carbon Trust data is for sectors and in electricity and gas

For Elec, individual shapes are used to generate shape
For gas, all gas data cross all sectors is used to generate shape
--> For enduse where both elec and gas are used, take shape of dominant fueltype and use same load shape for other fueltypes

ENDUSE
  Catering
  Computing
  Cooling and ventilation
  Hot water
  Heating
  Lighting
  Other

SECTORS                                           SHAPES
  Community, arts and leisure (individ)    -->    Carbon Trust: Community
  Education (individ)                      -->    Carbon Trust: Education
  Retail (individ)                         -->    Carbon Trust: Retail
  Health (individ)                         -->    Carbon Trust: Health
  Offices (individ)                        -->    Carbon Trust: Financial & Government??

  Emergency Services (aggr)                -->    Carbon Trust: Manufacturing, other Sectors ?? (or averaged of all?)
  Hospitality (aggr)
  Military (aggr)
  Storage (aggr)

  TODO: Exclude heating from electricity by contrasting winter/summer
  (excl. heating with summer/winter comparison)
  Select individual load shapes for different sectors where possible (only electricity) (excl. heating with summer/winter comparison)
  For sectors where no carbon trail data relates,use aggregated load curves from carbon trust with: Financial, Government, Manufacturing, other Sectors

SHAPES Elec
Calculate electricity shapes for aggregated and individual sectors:
    [h]    Carbon Trust Metering Trial: averaged daily profily for every month (daytype, month, h)
    [p_h]  Carbon Trust Metering Trial: maximum peak day is selected and daily load shape exported
    [d]    Carbon Trust Metering Trial: Use (daytype, month, h) to distribute over year
    [p_d]  Carbon Trust Metering Trial: Select day with most enduse and compare how relateds to synthetically generated year

SHAPES Gas
Calculate gas shapes across all sectors:
    [h]   Carbon Trust Metering Trial: averaged daily profily for every month
    [p_h] Carbon Trust Metering Trial: the maximum peak day is selected and daily load shape exported
    [p_d] National Grid (non-residential data based on CWW)
    [d]   National Grid (non-residential data based on CWW) used to assign load for every day (then multiply with h shape)

USED SHAPES FOR ENDUSES

Catering (e,g) (Table 5.05)                         -->   Use electricity shape (disaggregate other fueltypes with this shape)

Computing (e) (Table 5.05)                          -->   Use electricity shape

Cooling and Ventilation (mainly e) (Table 5.05)     -->   Use electricity shapes and distribute other fueltypes with this shape

Hot Water (e,g) (Table 5.05)                        -->   More gas enduse --> Use gas shape across all sectors and distribute also with it elec.

Heating (mainly g) (Table 5.05)                     -->   Use gas load shape accross all sectors and disaggregate other fuels with this load shape

Lighting (e) (Table 5.05)                           -->   Use electricity shapes

Other (e,g) (Table 5.05)                            -->   Use overall electricity and overall gas curve



'''

def load_assumptions(data):
    """All assumptions of the energy demand model are loaded and added to the data

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict

    Notes
    -----

    """
    assump_dict = {}

    # Load assumptions from csv files
    dwtype_floorarea = data['dwtype_floorarea']


    # ============================================================
    # Elasticities (Long-term resid_elasticities)
    # #TODO: Elasticties over time change? Not implemented so far
    # ============================================================
    resid_elasticities = {'heating': -0.4,
                          'water' : 0,
                          'cooking' : 0,
                          'lighting': 0,
                          'cold': 0,
                          'wet': 0,
                          'consumer_electronics': 0,
                          'home_computing': 0,
                         }
    assump_dict['resid_elasticities'] = resid_elasticities      # Add dictionaries to assumptions


    # ============================================================
    # Technologies (Residential)
    # ============================================================

    # -----------------
    # Efficiencies
    # -----------------

    ## --Efficiencies residential, base year
    eff_by = {
        # -- water
        'boiler_A' : 0.4,
        'boiler_B' : 0.3,

        # -- cooking
        'new_tech_A': 0.05,
        'tech_A' : 0.5,
        'tech_B' : 0.9,
        'tech_C': 0.0,

        # -- lighting
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        # -- cold
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,

        # -- wet
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,

        # -- consumer electronics
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,

        # -- home_computing
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5
        }
    assump_dict['eff_by'] = eff_by      # Add dictionaries to assumptions

    ## Efficiencies residential, end year
    eff_ey = {
        # -- water
        'boiler_A' : 0.4,
        'boiler_B' : 0.3,

        # -- cooking
        'new_tech_A': 0.05,
        'tech_A' : 0.5,
        'tech_B' : 0.9,
        'tech_C': 0.0,

        # -- lighting
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        # -- cold
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,

        # -- wet
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,

        # -- consumer electronics
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,

        # -- home_computing
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5
        }
    assump_dict['eff_ey'] = eff_ey # Add dictionaries to assumptions

    ## How much of efficiency potential is achieved
    eff_achieved = {
        'boiler_A' : 0.5,
        'boiler_B' : 0.3,
        'new_tech_A': 0.1,
        'tech_A' : 0.5,
        'tech_B' : 0.5,
        'tech_C': 0.0,
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5,


        # -- lightinging
        'halogen_elec': 0.036,                # 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wiki: self
        'fluorescent_strip_lightinging': 0.054,  # 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # 70% efficiency gain to standard lightingbulg
        'LED' : 0.048                         # 40% savings compared to energy saving lighting bulb
        }
    assump_dict['eff_achieved'] = eff_achieved # Add dictionaries to assumptions

    # Helper function eff_achieved
    # THIS can be used for scenarios to define how much of the fficiency was achieved
    for i in assump_dict['eff_achieved']:
        assump_dict['eff_achieved'][i] = 0.0


    # Create lookup for technologies (That technologies can be replaced for calculating with arrays) Helper function
    data['tech_lu'] = {}
    for tech_id, tech in enumerate(eff_by, 1000):
        data['tech_lu'][tech] = tech_id
        tech_id += 1



    # ---------------------------------------------------------------------------------------------------------------------
    # Fuel Switches assumptions ()
    # ---------------------------------------------------------------------------------------------------------------------

    # A. Calc share which is to be switched
    # B. Calculate efficiency of technology which is to be replaced and new technology
    # C: get shift from fuel to fuel

    # -- Share of fuel types for each enduse
    # TODO: Write function to insert fuel swatches

    #Generate fuel distribution of base year for every end_use #TODO: Assert if always 100% #assert p_tech_by['boiler_A'] + p_tech_by['boiler_B'] == 1.0
    fuel_type_p_by = generate_fuel_type_p_by(data)

    assump_dict['fuel_type_p_by'] = mf.convert_to_array(fuel_type_p_by)

    #print("")
    #print(assump_dict['fuel_type_p_by']['lighting'])
    #print(",,,")
    #prnt("..")

    # Perc
    # Only write those which should be replaced --> How much the fuel of each fueltype is reduced based on base_demand (can be more than 100% overall fueltypes)
    # Don't specify total fuel percentage of enduse but only how much is reduced to base_year
    # TODO: Acual percentage of fueltype yould be calculated...
    assump_fuel_frac_ey = {} 
    '''{'lighting': {'0' : 0,
                                        '1' : 0,
                                        '2' : 0,
                                        '3' : 0.0,
                                        '4' : 0.0,
                                        '5' : 0.0,
                                        '6' : 0.0
                                       }
                          }'''

    # Helper function - Replace all enduse from assump_fuel_frac_ey
    fuel_type_p_ey = {}
    for enduse in fuel_type_p_by:
        if enduse not in assump_fuel_frac_ey:
            fuel_type_p_ey[enduse] = fuel_type_p_by[enduse]
        else:
            fuel_type_p_ey[enduse] = assump_fuel_frac_ey[enduse]
    # Convert to array
    assump_dict['fuel_type_p_ey'] = mf.convert_to_array(fuel_type_p_ey)


    # ----------------------------------------------------------------------------------
    # -- Share of technologies within each fueltype and for each enduse
    # ----------------------------------------------------------------------------------
    # Technology which is installed for the share of fueltype to be replaced
    assump_dict['tech_install'] = {} #{'lighting': 'LED'}

    # Technologies used for the different fuel types where the new technology is introduced
    tech_replacement_dict = {}
    '''{'lighting':{0: 'boiler_oil',
                                         1: 'boiler_gas',
                                         2: 'boiler_B',
                                         3: '',
                                         4: 'boiler_B',
                                         5: '',
                                         6: '',
                                         7: ''
                                        },
                            }'''
    assump_dict['tech_replacement_dict'] = tech_replacement_dict





    # ----------------------------------
    # Which technologies are used for which end_use and to which share
    # ----------------------------------
    #Share of technology for every enduse and fueltype in base year [in %]
    # Only shares within each fueltype !!!!

    # Create technoogy empties for all enduses
    technologies_enduse_by = {}
    fuel_data = data['data_residential_by_fuel_end_uses']
    for enduse in fuel_data:

        technologies_enduse_by[enduse] = {}

        for fueltype in range(len(data['fuel_type_lu'])): #
            technologies_enduse_by[enduse][fueltype] = {}

    # Add technological split where known
    technologies_enduse_by['lighting'][2] = {'halogen_elec': 0.37, 'standard_lighting_bulb': 0.35, 'fluorescent_strip_lightinging': 0.09, 'energy_saving_lighting_bulb': 0.18} #As in old model

    # add to dict
    assump_dict['technologies_enduse_by'] = technologies_enduse_by

    # --Technological split in end_year  # FOR END YEAR ALWAYS SAME NR OF TECHNOLOGIES AS INITIAL YEAR (TODO: ASSERT IF ALWAYS 100%)
    technologies_enduse_ey = technologies_enduse_by.copy()

    technologies_enduse_ey['lighting'][2] = {'halogen_elec': 0.37, 'standard_lighting_bulb': 0.35, 'fluorescent_strip_lightinging': 0.09, 'energy_saving_lighting_bulb': 0.18} #As in old model
    #technologies_enduse_ey['lighting'][2] = {'halogen_elec': 0.00, 'standard_lighting_bulb': 0.72, 'fluorescent_strip_lightinging': 0.09, 'energy_saving_lighting_bulb': 0.18} #As in old model

    assump_dict['technologies_enduse_ey'] = technologies_enduse_ey
    #assump_dict['technologies_enduse_cy'] = technologies_enduse_cy




    # ============================================================
    # Assumptions Residential Dwelling Stock
    # ============================================================

    # Building stock related
    assump_change_floorarea_pp = 0.4 # [%] If e.g. 0.4 --> 40% increase (the one is added in the model) # Assumption of change in floor area up to end_year ASSUMPTION (if minus, check if new buildings are needed)

    #BASE YEAR: 2015.0: {'semi_detached': 26.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    assump_dwtype_distr_ey = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}     # Assumption of distribution of dwelling types in end_year ASSUMPTION

    #assump_dwtype_distr_ey = copy.(data['dwtype_distr'])
    assump_dwtype_floorarea = dwtype_floorarea                                                                       # Average floor area per dwelling type (loaded from CSV)


    # Add to dictionary
    assump_dict['assump_change_floorarea_pp'] = assump_change_floorarea_pp
    assump_dict['assump_dwtype_distr_ey'] = assump_dwtype_distr_ey
    assump_dict['assump_dwtype_floorarea'] = assump_dwtype_floorarea

    data['assumptions'] = assump_dict
    return data



# ------------- Helper functions

def generate_fuel_type_p_by(data):
    """Assumption helper function to generate percentage fuel distribution for every encuse"""

    fuel_data = data['data_residential_by_fuel_end_uses']
    out_dict = {}

    for enduse in fuel_data:
        out_dict[enduse] = {}

        # sum fueltype
        sum_fueltype = np.sum(fuel_data[enduse])
        if sum_fueltype != 0:
            fuels_in_p = fuel_data[enduse] / sum_fueltype
        else:
            fuels_in_p = fuel_data[enduse] # all zeros

        for fueltype, fuels in enumerate(fuels_in_p):
            out_dict[enduse][fueltype] = float(fuels) # Convert to %

    return out_dict
