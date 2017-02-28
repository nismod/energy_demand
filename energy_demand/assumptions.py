""" This file contains all assumptions of the energy demand model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_assumptions():
    """All assumptions

    Returns
    -------
    data : dict
        dict with assumptions

    Notes
    -----

    """
    assumptions_dict = {}



    # ------------------------------------------------------------------------
    # Residential model
    # ------------------------------------------------------------------------

    # Building stock related
    change_floor_area_pp = -0.1        # Assumption of change in floor area up to end_year ASSUMPTION


    #assump_dwtype_distr = {'semi_detached': 26.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}    # Assumption of distribution of dwelling types in end_year ASSUMPTION






    # Add to dictionary
    assumptions_dict['change_floor_area_pp'] = change_floor_area_pp

    return assumptions_dict
