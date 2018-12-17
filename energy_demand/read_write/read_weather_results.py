"""Read in model results and plot results
"""
import os
import logging
import numpy as np

from energy_demand.read_write import data_loader, read_data
from energy_demand.technologies import tech_related

def read_in_weather_results(
        path_result,
        seasons,
        model_yeardays_daytype,
        fueltype_str
    ):
    """Read and post calculate results from txt files
    and store into container

    Arguments
    ---------
    path_result : str
        Paths
    seasons : dict
        seasons
    model_yeardays_daytype : dict
        Daytype of modelled yeardays
    """
    logging.info("... Reading in results")

    fueltype_int = tech_related.get_fueltype_int(fueltype_str)


    results_container = {}

    # -----------------
    # Read in demands
    # -----------------

    # Read in total regional demands per fueltype
    print("path_result " + str(path_result))
    results_container['ed_reg_tot_y'] = read_data.read_results_yh(
        path_result, 'only_total')

    print(results_container['ed_reg_tot_y'][2015].shape)

    print("path_result " + str(path_result))
    results_container['ed_reg_peakday'] = read_data.read_results_yh(
        os.path.join('simulation_results', path_result), 'only_peak')

    print(results_container['ed_reg_peakday'][2015].shape)
    results_container['ed_reg_peakday_peak_hour'] = {}
    results_container['national_peak'] = {}
    results_container['regional_share_national_peak'] = {}

    results_container['national_all_fueltypes'] = {}

    for year in results_container['ed_reg_peakday']:

        # Get peak demand of each region
        results_container['ed_reg_peakday_peak_hour'][year] = results_container['ed_reg_peakday'][year].max(axis=2)

        # Get national peak
        national_demand_per_hour = results_container['ed_reg_peakday'][year].sum(axis=1) #Aggregate hourly across all regions

        # Get maximum hour for electricity demand
        max_hour = national_demand_per_hour[fueltype_int].argmax()

        results_container['national_peak'][year] = national_demand_per_hour[:, max_hour]

        # Calculate regional share of peak hour to national peak
        national_peak = results_container['national_peak'][year][fueltype_int]
        regional_peak = results_container['ed_reg_peakday'][year][fueltype_int][:, max_hour]
        results_container['regional_share_national_peak'][year] = (100 / national_peak) * regional_peak #1 = 1 %

        # Sum all regions for each fueltypes
        print(results_container['ed_reg_tot_y'][year].shape)
        results_container['national_all_fueltypes'][year] = np.sum(results_container['ed_reg_tot_y'][year], axis=1)
        print(results_container['national_all_fueltypes'][year].shape)

    logging.info("... Reading in results finished")
    return results_container