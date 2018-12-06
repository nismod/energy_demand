"""Read in model results and plot results
"""
import os
import logging

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import read_data

def read_in_weather_results(
        path_result,
        seasons,
        model_yeardays_daytype
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

    lookups = lookup_tables.basic_lookups()

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

    logging.info("... Reading in results finished")
    return results_container