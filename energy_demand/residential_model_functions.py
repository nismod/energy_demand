"""
# ----------------------------------------------------------------
# Description: This is the residential model
# Authors:
# ----------------------------------------------------------------
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

# Imports
import numpy as np

def changeLoadProfilesDependingOnEfficiencies(load_profiles):
    """
    This function changes individual load profiles depending on efficiency and technology assumptions

    Input:
    -load_profiles  Base load profiles
    -cur_year       Current year of simulation
    -technologies
    -effficiency_assupmtions
    -...

    Output:
    -load_profiles  Load profiles for simulation year
    """

    # Needed Input: Efficiences over time of technologies
    # Technological split

    print("Change Load Profiles depending on effiiencies over time")

    return load_profiles

def create_building_stock(reg_pop, dwtype_lu):
    """
    This function reads in base buildings, floor area etc. and calculates the number of buildings for each dwelling type....

    Input:
    -assumption_welling_types
    -.....

    Output:
    -
    """

    building = np.zeros(len(reg_pop), len(dwtype_lu))
    return building
