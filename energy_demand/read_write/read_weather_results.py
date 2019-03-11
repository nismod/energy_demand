"""Read in model results and plot results
"""
import os
import logging
import numpy as np
import time

from energy_demand.read_write import data_loader, read_data
from energy_demand.technologies import tech_related

def read_in_weather_results(
        path_result,
        seasons,
        model_yeardays_daytype,
        pop_data,
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

    # Read in total regional demands per fueltype
    results_container['ed_reg_tot_y'] = read_data.read_results_yh(
        path_result, 'only_total')

    #print(results_container['ed_reg_tot_y'][2015].shape)
    results_container['ed_reg_peakday'] = read_data.read_results_yh(
        os.path.join('simulation_results', path_result), 'only_peak')

    #print(results_container['ed_reg_peakday'][2015].shape)
    results_container['ed_reg_peakday_peak_hour'] = {}
    results_container['ed_reg_peakday_peak_hour_per_pop'] = {}
    
    results_container['national_peak'] = {}
    results_container['regional_share_national_peak'] = {}
    results_container['regional_share_national_peak_pp'] = {}
    results_container['pp_peak_abs'] = {}
    results_container['regional_peak'] = {}
    results_container['national_all_fueltypes'] = {}
    results_container['mean_peak_day_demand'] = {}

    for year in results_container['ed_reg_peakday']:

        reg_pop_yr = pop_data[year]

        # Get peak demand of each region
        results_container['ed_reg_peakday_peak_hour'][year] = results_container['ed_reg_peakday'][year].max(axis=2)

        # Divide peak by number of population
        results_container['ed_reg_peakday_peak_hour_per_pop'][year] = results_container['ed_reg_peakday_peak_hour'][year] / reg_pop_yr

        # Get national peak
        national_demand_per_hour = results_container['ed_reg_peakday'][year].sum(axis=1) #Aggregate hourly across all regions

        # Get maximum hour for electricity demand
        max_hour = national_demand_per_hour[fueltype_int].argmax()

        results_container['national_peak'][year] = national_demand_per_hour[:, max_hour]

        # Calculate regional share of peak hour to national peak
        national_peak = results_container['national_peak'][year][fueltype_int]
        regional_peak = results_container['ed_reg_peakday'][year][fueltype_int][:, max_hour]
        
        results_container['regional_peak'][year] = regional_peak
        results_container['regional_share_national_peak'][year] = (100 / national_peak) * regional_peak #1 = 1 %
        results_container['regional_share_national_peak_pp'][year] = ((100 / national_peak) * regional_peak) /  reg_pop_yr #1 = 1 %

        # Calculate mean of peak day demand of peak day
        results_container['national_all_fueltypes'][year] = np.sum(results_container['ed_reg_tot_y'][year], axis=1)
        results_container['mean_peak_day_demand'][year] = np.mean(national_demand_per_hour, axis=1)

        # Calculate contribution per person towards national peak (reg_peak / people) [abs]
        #print(results_container['ed_reg_peakday'][year].shape)
        #print(reg_pop_yr.shape)
        # results_container['pp_peak_abs'][year] = (
        #    results_container['ed_reg_peakday'][year][:,:, max_hour] / reg_pop_yr)
        #(cpp = (regional peak / national peak) / people [%]

    logging.info("... Reading in results finished")
    return results_container