""" This file contains all assumptions of the energy demand model"""
import numpy as np
import energy_demand.main_functions as mf

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
    # Elasticities (Long-term elasticities) #TODO: Elasticties over time change? Not implemented so far
    # ============================================================
    elasticities = {'light': 0,
                    'cold' : 0,
                    'wet' : 0
                   }
    assump_dict['elasticities'] = elasticities      # Add dictionaries to assumptions


    # ============================================================
    # Assumptions Technological Stock
    # ============================================================

    # eff_by: Efficiencies of technologes in base year
    # eff_ey: Efficiencies of technologes in end year

    # -----------------
    # Efficiencies
    # -----------------

    ## Efficiencies residential, base year
    eff_by = {
            'boiler_A' : 0.4,
            'boiler_B' : 0.3,
            'new_tech_A': 0.05,
            'tech_A' : 0.5,
            'tech_B' : 0.9,
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
        
            # -- Lighting
            'halogen_elec': 0.036,                # 80% efficiency gaing to standard light blub RElative calculated to be 80% better than standard light bulb (180*0.02) / 100
            'standard_light_bulb': 0.02,          # Found on wiki: self
            'fluorescent_strip_lighting': 0.054,  # 50% efficiency gaint to halogen (0.036*150) / 100
            'energy_saving_light_bulb': 0.034,    # 70% efficiency gain to standard lightbulg
            'LED' : 0.048                         # 40% savings compared to energy saving light bulb

            }

    assump_dict['eff_by'] = eff_by      # Add dictionaries to assumptions

    ## Efficiencies residential, end year
    eff_ey = {
        'boiler_A' : 0.9,
        'boiler_B' : 0.5,
        'new_tech_A': 0.1,
        'tech_A' : 0.5,
        'tech_B' : 0.9,
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

        # -- Lighting
        'halogen_elec': 0.08,                # 80% efficiency gaing to standard light blub RElative calculated to be 80% better than standard light bulb (180*0.02) / 100
        'standard_light_bulb': 0.02,          # Found on wiki: self
        'fluorescent_strip_lighting': 0.054,  # 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_light_bulb': 0.034,    # 70% efficiency gain to standard lightbulg
        'LED' : 0.048                         # 40% savings compared to energy saving light bulb

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


        # -- Lighting
        'halogen_elec': 0.036,                # 80% efficiency gaing to standard light blub RElative calculated to be 80% better than standard light bulb (180*0.02) / 100
        'standard_light_bulb': 0.02,          # Found on wiki: self
        'fluorescent_strip_lighting': 0.054,  # 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_light_bulb': 0.034,    # 70% efficiency gain to standard lightbulg
        'LED' : 0.048                         # 40% savings compared to energy saving light bulb

        }
    assump_dict['eff_achieved'] = eff_achieved # Add dictionaries to assumptions

    # Helper function eff_achieved
    for i in assump_dict['eff_achieved']:
      assump_dict['eff_achieved'][i] = 0.5


    # Create lookup for technologies (That technologies can be replaced for calculating with arrays)
    data['tech_lu'] = {}
    tech_id = 1000
    for tech in eff_by:
          data['tech_lu'][tech] = tech_id
          tech_id += 1


    # -------------
    # Fuel Switches assumptions
    # -------------
    # TODO: Write function to insert fuel swatches

    # Technology which is installed for which enduse in case of fuel switches
    tech_install = {'light': 'boiler_A'}

    assump_dict['tech_install'] = tech_install

    # Technologies used for the different fuel types where the new technology is introduced
    tech_replacement_dict = {'light': {0: 'boiler_B',
                                       1: 'boiler_B',
                                       2: 'boiler_B',
                                       3: 'boiler_B',
                                       4: 'boiler_B',
                                       5: 'boiler_B',
                                       6: 'boiler_B',
                                       7: 'boiler_B'
                                      },
                            }

    assump_dict['tech_replacement_dict'] = tech_replacement_dict


    # Percentage of fuel types (base year could also be calculated and loaded)
    fuel_type_p_by = {'light': {0 : 0.0,
                                1 : 0.0,
                                2 : 0.1,
                                3 : 0.0,
                                4 : 0.0,
                                5 : 0.0,
                                6 : 0.2
                               },
                      'cold': {'0' : 0.0182,
                               '1' : 0.7633,
                               '2' : 0.0791,
                               '3' : 0.0811,
                               '4' : 0.0,
                               '5' : 0.0581,
                               '6' : 0.0
                              },

                      'wet': {'0' : 0.0182,
                              '1' : 0.7633,
                              '2' : 0.0791,
                              '3' : 0.0811,
                              '4' : 0.0,
                              '5' : 0.0581,
                              '6' : 0.0
                             },
                    'consumer_electronics': {
                              '0' : 0.0182,
                              '1' : 0.7633,
                              '2' : 0.0791,
                              '3' : 0.0811,
                              '4' : 0.0,
                              '5' : 0.0581,
                              '6' : 0.0
                             },

                    'home_computing': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'cooking': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'heating': {
                                  '0' : 0.2,
                                  '1' : 0.3,
                                  '2' : 0.5,
                                  '3' : 0.0,
                                  '4' : 0.0,
                                  '5' : 0.0,
                                  '6' : 0.0
                                  }
                    }
    # Convert to array
    fuel_type_p_by = mf.convert_to_array(fuel_type_p_by)
    assump_dict['fuel_type_p_by'] = fuel_type_p_by

    # Check if base demand is 100 %
    #assert p_tech_by['boiler_A'] + p_tech_by['boiler_B'] == 1.0

    fuel_type_p_ey = {'light': {
                                  '0' : 0.2,
                                  '1' : 0.3,
                                  '2' : 0.5,
                                  '3' : 0.0,
                                  '4' : 0.0,
                                  '5' : 0.0,
                                  '6' : 0.0
                                  },
                      'cold': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                     'cooking': {
                                  '0' : 0.2,
                                  '1' : 0.3,
                                  '2' : 0.4,
                                  '3' : 0.0,
                                  '4' : 0.0,
                                  '5' : 0.0,
                                  '6' : 0.0
                                },
                    'wet': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'consumer_electronics': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'home_computing': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'cooking': {
                                  '0' : 0.0182,
                                  '1' : 0.7633,
                                  '2' : 0.0791,
                                  '3' : 0.0811,
                                  '4' : 0.0,
                                  '5' : 0.0581,
                                  '6' : 0.0
                                },
                    'heating': {
                                  '0' : 0.2,
                                  '1' : 0.3,
                                  '2' : 0.5,
                                  '3' : 0.0,
                                  '4' : 0.0,
                                  '5' : 0.0,
                                  '6' : 0.0
                                  }
                    }
    
    # Convert to array
    assump_dict['fuel_type_p_ey'] = mf.convert_to_array(fuel_type_p_ey)

    # Check if base demand is 100 %
    #assert p_tech_by['boiler_A'] + p_tech_by['boiler_B'] == 1.0




    # ----------------------------------
    # Which technologies are used for which end_use and to which share
    # ----------------------------------
    #Share of technology for every enduse and fueltype in base year [in %]
    technologies_enduse_by = {
                              'light': {
                                        0: {},
                                        1: {},
                                        2: {'halogen_elec': 0.37, 'standard_light_bulb': 0.35, 'fluorescent_strip_lighting': 0.09, 'energy_saving_light_bulb': 0.18}, #As in old model
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                               'cold': {
                                        0: {},
                                        1: {},
                                        2: {},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                               'wet': {
                                        0: {},
                                        1: {},
                                        2: {},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      }
                             }

    assump_dict['technologies_enduse_by'] = technologies_enduse_by

    # --Technological split in end_year
    # FOR END YEAR ALWAYS SAME NR OF TECHNOLOGIES AS INITIAL YEAR (TODO: ASSERT IF ALWAYS 100%)
    technologies_enduse_ey = {
                            'light': {
                                        0: {},
                                        1: {},
                                        2: {'halogen_elec': 0.00, 'standard_light_bulb': 0.72, 'fluorescent_strip_lighting': 0.09, 'energy_saving_light_bulb': 0.18},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                               'cold': {
                                        0: {},
                                        1: {},
                                        2: {},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                               'wet': {
                                        0: {},
                                        1: {},
                                        2: {},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      }
                             }

    assump_dict['technologies_enduse_ey'] = technologies_enduse_ey


    # CALCULATE 


    #assump_dict['technologies_enduse_cy'] = technologies_enduse_cy


    # ============================================================
    # Assumptions Residential Building Stock
    # ============================================================

    # Building stock related
    assump_change_floorarea_pp = 0.1 # [%]                                                                           # Assumption of change in floor area up to end_year ASSUMPTION (if minus, check if new buildings are needed)
    assump_dwtype_distr_ey = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}     # Assumption of distribution of dwelling types in end_year ASSUMPTION
    assump_dwtype_floorarea = dwtype_floorarea                                                                       # Average floor area per dwelling type (loaded from CSV)


    # Add to dictionary
    assump_dict['assump_change_floorarea_pp'] = assump_change_floorarea_pp
    assump_dict['assump_dwtype_distr_ey'] = assump_dwtype_distr_ey
    assump_dict['assump_dwtype_floorarea'] = assump_dwtype_floorarea

    data['assumptions'] = assump_dict
    return data
