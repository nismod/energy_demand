"""
    ----------------------------------------------------------------
    Description: This is the residential model
    Authors:
    ----------------------------------------------------------------

"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import residential_model_functions as rf

def run(SIM_PARAM, load_profiles, reg_pop, timesteps_app_bd, timesteps_hd_bd):
    """
    Main function of residential model.

    Main steps:

    A. Residential electriciy demand

    Input:
    -SIM_PARAM
    -load_profiles
    -...

    Output:
    -timesteps_app_bd   Hourly energy demand residential
    -timesteps_hd_bd    Hourly gas demand residential
    """
    year_curr = SIM_PARAM[0]     # Current year of simulation
    year_base = SIM_PARAM[1]        # Base year


    # --------------------------------------
    # Appliances
    # --------------------------------------

    # Assumptions about efficiences, technologies (Change  eletricity load curves for the appliances)
    #timesteps_app_sim_year = rf.changeLoadProfilesDependingOnEfficiencies(timesteps_app_bd) # Dummy so far

    # Crate Building Stock
    #building_stock = create_building_stock(reg_pop, dwelling_type_lu)

    # Calculate total demand (multiply individual building load curves with number of buildings)
    #dict_elec_demand_all_buildings(load_profiles_sim_year, building_stock)

    # Define how much of different technologies and efficiens are taken up on the market and calculate new usage

    # Read in population, floor area, nr of households etc...for current year (depending on scenario)


    #-------------------
    # Space heating
    # ------------------


    #-------------------
    # Sum Appliances & heating
    # ------------------

    # ---------------------------------------------
    # DUMMY SIMULATION WITH POPULATION
    # ---------------------------------------------
    pop_base_year = reg_pop[:, 1]  # 1: 2015, 2: 2016...
    pop_curr_year = reg_pop[:, year_curr + 1]

    if year_curr != 0: # not base year
        print("Elec appliance base year: " + str(timesteps_app_bd.sum()))
        print("Gas heatinb base year:     " + str(timesteps_hd_bd.sum()))

        # Initiliase
        timesteps_app_sim_year = timesteps_app_bd * 0
        timesteps_hd_sim_year = timesteps_hd_bd * 0

        # Calculate new regional demand
        for region_Nr in range(len(reg_pop)):

            # New electricity demand
            fuel_e = 0
            timesteps_app_sim_year[fuel_e][region_Nr] = (pop_curr_year[region_Nr] / pop_base_year[region_Nr]) * timesteps_app_bd[fuel_e][region_Nr]     # New pop / old pop * base demand

            # New heating demand
            fuel_gas = 1
            timesteps_hd_sim_year[fuel_gas][region_Nr] = (pop_curr_year[region_Nr] / pop_base_year[region_Nr]) * timesteps_hd_bd[fuel_gas][region_Nr]        # New pop / old pop * base demand

        print("Elec appliance simulation year:  " + str(timesteps_app_sim_year.sum()))
        print("Gas heatinb simulation year:     " + str(timesteps_hd_sim_year.sum()))

        return timesteps_app_sim_year, timesteps_hd_sim_year

    else:
        return timesteps_app_bd, timesteps_hd_bd
    
