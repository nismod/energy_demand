""" This file contains all assumptions of the energy demand model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_assumptions(data):
    """All assumptions

    Returns
    -------
    data : dict
        dict with assumptions

    Notes
    -----

    """
    assumptions_dict = {}


    # Load assumptions from csv files
    dwtype_floorarea = data['dwtype_floorarea']


    # ============================================================
    # Assumptions Technological stock
    # ============================================================


    # -- Efficiencies

    # Residential - Appliances
    eff_boiler_A_by = 0.5           # Efficiency of technology 




    # -- Share of technology in base year [in %]
    distr_boiler_A_by = 0.5 # [%] 




    # Share of technology in the year 2060
    distr_boiler_A_by =



    assumptions_dict['distr_e_boiler_A'] = generate_distr(eff_boiler_A_by, 

    # ============================================================
    # Residential model
    # ============================================================

    # Building stock related
    assump_change_floorarea_pp = 0.1 # [%]                                                                           # Assumption of change in floor area up to end_year ASSUMPTION (if minus, check if new buildings are needed)
    assump_dwtype_distr_ey = {'semi_detached': 20.0, 'terraced': 20, 'flat': 30, 'detached': 20, 'bungalow': 10}     # Assumption of distribution of dwelling types in end_year ASSUMPTION
    assump_dwtype_floorarea = dwtype_floorarea                                                                       # Average floor area per dwelling type (loaded from CSV)








    # Add to dictionary
    assumptions_dict['assump_change_floorarea_pp'] = assump_change_floorarea_pp
    assumptions_dict['assump_dwtype_distr_ey'] = assump_dwtype_distr_ey
    assumptions_dict['assump_dwtype_floorarea'] = assump_dwtype_floorarea

    return assumptions_dict
