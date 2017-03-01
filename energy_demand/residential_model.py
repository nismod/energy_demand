"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import energy_demand.residential_model_functions as rf

def run(glob_var, load_profiles, reg_pop_base, reg_pop_external, timesteps_app_bd, timesteps_hd_bd):
    """
    Main function of residential model.

    Main steps:

    A. Residential electriciy demand

    Input:
    -glob_var
    -load_profiles
    -...

    Output:
    -timesteps_app_bd   Hourly energy demand residential
    -timesteps_hd_bd    Hourly gas demand residential
    """
    year_curr = glob_var['current_year']     # Current year of simulation
    year_base = glob_var['base_year']        # Base year

    # --------------------------------------
    # Appliances
    # --------------------------------------

    # Assumptions about efficiences, technologies (Change  eletricity load curves for the appliances)
    #timesteps_app_sim_year = rf.changeLoadProfilesDependingOnEfficiencies(timesteps_app_bd) # Dummy so far

    # Crate Building Stock
    #building_stock = create_building_stock(reg_pop, dwtype_lu)

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
    # DUMMY SIMULATION WITH POPULATION (scrap)
    # ---------------------------------------------
    pop_base_year = reg_pop_base[:, 1]  # 1: 2015, 2: 2016...

    # Convert base year to array # TODO: REMOVE
    pop_curr_year = reg_pop_external[year_curr][:, 1]
    #print(reg_pop_external * reg_pop_base)
    #print("..")
    if year_curr != 0: # not base year
        print("Elec appliance base year: " + str(timesteps_app_bd.sum()))
        print("Gas heatinb base year:     " + str(timesteps_hd_bd.sum()))

        # Initiliase
        timesteps_app_sim_year = timesteps_app_bd * 0
        timesteps_hd_sim_year = timesteps_hd_bd * 0

        # Calculate new regional demand
        for region_Nr in range(len(reg_pop_base)):

            # New electricity demand
            fuel_e = 0
            print(region_Nr)
            print(timesteps_app_sim_year[fuel_e][region_Nr])
            print(pop_curr_year[region_Nr])
            print(pop_base_year[region_Nr])
            print(timesteps_app_bd[fuel_e][region_Nr])
            print("..")
            print(timesteps_app_bd[fuel_e][region_Nr].shape)
            print(timesteps_app_sim_year[fuel_e][region_Nr].shape)
            print(pop_curr_year[region_Nr].shape)
            print("...")
            print((pop_curr_year[region_Nr] / pop_base_year[region_Nr]))

            timesteps_app_sim_year[fuel_e][region_Nr] = (pop_curr_year[region_Nr] / pop_base_year[region_Nr]) * timesteps_app_bd[fuel_e][region_Nr]     # New pop / old pop * base demand

            # New heating demand
            fuel_gas = 1
            timesteps_hd_sim_year[fuel_gas][region_Nr] = (pop_curr_year[region_Nr] / pop_base_year[region_Nr]) * timesteps_hd_bd[fuel_gas][region_Nr]        # New pop / old pop * base demand

        print("Elec appliance simulation year:  " + str(timesteps_app_sim_year.sum()))
        print("Gas heatinb simulation year:     " + str(timesteps_hd_sim_year.sum()))

        return timesteps_app_sim_year, timesteps_hd_sim_year

    else:
        return timesteps_app_bd, timesteps_hd_bd

def read_raw_UKERC_data():
    """ This file read in UKERC data


    """
    return
