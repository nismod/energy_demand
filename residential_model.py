# ----------------------------------------------------------------
# Description: This is the residential model
# Authors: 
# ----------------------------------------------------------------

# Imports
import numpy as np
import math as m
from residential_model_functions import *

def run(sim_Param, load_profiles, reg_pop, dwelling_type_lu):
    """
    Main function of residential model.

    Main steps:

    A. Residential electriciy demand

    Input:
    -sim_Param
       ...
    -load_profiles

    Output:
    -ED_h_residential   Hourly energy demand residential
    """
    year_current = sim_Param[0]     # Current year of simulation
    year_base = sim_Param[1]        # Base year
    year_current_Number = year_base + year_current

    # --------------------------------------
    # Appliances
    # --------------------------------------
    # getAppliances()



    # Assumptions about efficiences, technologies (Change  eletricity load curves for the appliances)
    load_profiles_sim_year = changeLoadProfilesDependingOnEfficiencies(load_profiles) # Dummy so far

    # Crate Building Stock
    building_stock = create_building_stock(reg_pop, dwelling_type_lu)

    # Calculate total demand (multiply individual building load curves with number of buildings)
    dict_elec_demand_all_buildings(load_profiles_sim_year, building_stock)

    # Add eletricity load profiles into timeSteps
    timeStepContainer = createLoadProfilesTimeStepContainer(load_profiles_sim_year, )

    # Define how much of different technologies and efficiens are taken up on the market and calculate new usage


    # Read in population, floor area, nr of households etc...for current year (depending on scenario)



    #-------------------
    # Space heating
    # ------------------
    # getSpaceHeating()


    #-------------------
    # Sum Appliances & heating
    # ------------------

    return load_profiles
