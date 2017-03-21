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
    # Assumptions Technological Stock
    # ============================================================

    # eff_by: Efficiencies of technologes in base year
    # eff_ey: Efficiencies of technologes in end year

    # -----------------
    # Efficiencies
    # -----------------
  
    ## Efficiencies residential, base year
    eff_by = {
        'boiler_A' : 0.1,
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
        'micro_CHP_thermal': 0.5
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
        'micro_CHP_thermal': 0.5
        }

    # Helper function eff_achieved
    for i in eff_achieved:
      eff_achieved[i] = 0.5
    
    assump_dict['eff_achieved'] = eff_achieved # Add dictionaries to assumptions

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
                                1 : 0.7,
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
                                        2: {'tech_A': 0.5, 'tech_B': 0.5},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      }
                             }

    assump_dict['technologies_enduse_by'] = technologies_enduse_by

    # --Technological split in end_year
    technologies_enduse_ey = {
                            'light': {
                                        0: {},
                                        1: {},
                                        2: {'tech_A': 0.3, 'tech_B': 0.4},
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                    }  
                            }

    assump_dict['technologies_enduse_ey'] = technologies_enduse_ey





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
