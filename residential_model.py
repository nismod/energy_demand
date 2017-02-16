"""
    ----------------------------------------------------------------
    Description: This is the residential model
    Authors:
    ----------------------------------------------------------------

"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import residential_model_functions as rf

def run(sim_Param, load_profiles, reg_pop, dwelling_type_lu, timesteps_app_bd):
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
    year_current_number = year_base + year_current

    # --------------------------------------
    # Appliances
    # --------------------------------------

    # Assumptions about efficiences, technologies (Change  eletricity load curves for the appliances)
    timesteps_app_sim_year = rf.changeLoadProfilesDependingOnEfficiencies(timesteps_app_bd) # Dummy so far

    # Crate Building Stock
    #building_stock = create_building_stock(reg_pop, dwelling_type_lu)

    # Calculate total demand (multiply individual building load curves with number of buildings)
    #dict_elec_demand_all_buildings(load_profiles_sim_year, building_stock)

    # Define how much of different technologies and efficiens are taken up on the market and calculate new usage

    # Read in population, floor area, nr of households etc...for current year (depending on scenario)



    #-------------------
    # Space heating
    # ------------------
    # getSpaceHeating()


    #-------------------
    # Sum Appliances & heating
    # ------------------

    return timesteps_app_sim_year
