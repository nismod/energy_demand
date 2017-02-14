# ----------------------------------------------------------------
# Description: This is the residential model
# Authors: 
# ----------------------------------------------------------------

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



def createLoadProfilesTimeStepContainder(load_profiles):
    """
    This function takes correct load profiles depending in week day, season etc. and puts it in the list

    Input:
    -load_profiles  Base load profiles

    Output:
    -load_profiles  Load profiles for simulation year
    """


    return load_profiles


def create_building_stock(reg_pop, dwelling_type_lu):
    """
    This function reads in base buildings, floor area etc. and calculates the number of buildings for each dwelling type....

    Input:
    -assumption_welling_types
    -.....

    Output:
    -
    """

    building = np.zeros(len(reg_pop),len(dwelling_type_lu))
    return building



