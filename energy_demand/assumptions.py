""" This file contains all assumptions of the energy demand model"""

import numpy as np

import energy_demand.main_functions as mf

def load_assumptions(data):
    """All assumptions

    Returns
    -------
    data : dict
        dict with assumptions

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

    ## Efficiencies residential, end year
    eff_ey = {
        'boiler_A' : 0.9,
        'boiler_B' : 0.5,
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

    # -------------
    # Fuel Switches assumptions
    # -------------
    # TODO: Write function to insert fuel swatches

    # Technology which is installed for which enduse
    tech_install = {'light': 'boiler_A'}

    # Technologies used for the different fuel types where the new technology is used
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

    # Percentage of fuel types (base year could also be calculated and loaded)
    fuel_type_p_by = {'light': {'0' : 0.0,
                                '1' : 0.7,
                                '2' : 0.1,
                                '3' : 0.0,
                                '4' : 0.0,
                                '5' : 0.0,
                                '6' : 0.2
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
                                }
                    }

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
                                }
                    }

    # Check if base demand is 100 %
    #assert p_tech_by['boiler_A'] + p_tech_by['boiler_B'] == 1.0


    # Convert to array
    fuel_type_p_by = mf.convert_to_array(fuel_type_p_by)
    fuel_type_p_ey = mf.convert_to_array(fuel_type_p_ey)




    # ----------------------------------
    # Technologes for different uses
    # ----------------------------------
    technologies_enduse_by = {'light': {
                                        0: 'boiler_A',
                                        1: 'boiler_A',
                                        2: 'boiler_A',
                                        3: 'boiler_A',
                                        4: 'boiler_A',
                                        5: 'boiler_A',
                                        6: 'boiler_A',
                                        7: 'boiler_A'},
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
                                }
                    }






    # ----------------------------------
    # Fraction of technologies
    # ----------------------------------
    # p_tech_by : Share of technology in base year [in %]
    # p_tech_ey : Share of technology in the end year

    # Residential, base year
    '''
    p_tech_by = {
        'boiler_A' : 0.5,
        'boiler_B' : 0.5,
        'new_tech_A': 0.0
        }

    tech_market_year = {
        'new_tech_A': 2000
        }

    tech_saturation_year = {
        'new_tech_A': 2017
        }
    '''
    # Residential, end year
    '''p_tech_ey = {
        'boiler_A' : 0.4,
        'boiler_B' : 0.5,
        'new_tech_A' : 0.1
        }
    '''

    # Add dictionaries to assumptions
    assump_dict['eff_by'] = eff_by
    assump_dict['eff_ey'] = eff_ey
    #assump_dict['p_tech_by'] = p_tech_by
    #assump_dict['p_tech_ey'] = p_tech_ey
    #assump_dict['tech_market_year'] = tech_market_year
    #assump_dict['tech_saturation_year'] = tech_saturation_year
    assump_dict['fuel_type_p_by'] = fuel_type_p_by
    assump_dict['fuel_type_p_ey'] = fuel_type_p_ey

    assump_dict['tech_replacement_dict'] = tech_replacement_dict 
    assump_dict['tech_install'] = tech_install

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

    return assump_dict
