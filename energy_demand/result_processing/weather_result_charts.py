"""Read in model results and plot results
"""
import os
import pandas as pd
import numpy as np

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import read_weather_results
from energy_demand.plotting import fig_3_weather_map
from energy_demand.technologies import tech_related

def main(
        path_data_ed,
        path_shapefile_input,
        plot_crit_dict,
        base_yr,
        simulation_yr_to_plot=2050
    ):
    """Read in all results and plot PDFs

    Arguments
    ----------
    path_data_ed : str
        Path to results
    path_shapefile_input : str
        Path to shapefile
    plot_crit_dict : dict
        Criteria to select plots to plot
    base_yr : int
        Base year
    comparison_year : int
        Year to generate comparison plots
    """
    print("...Start creating plots")
    data = {}

    # ---------------------------------------------------------
    # Iterate folders and read out all weather years and stations
    # ---------------------------------------------------------
    to_ignores = [
        'model_run_pop',
        'PDF_validation']

    endings_to_ignore = [
        '.pdf',
        '.txt',
        '.ini']

    # ---------------
    # Create result folder
    # -------------------
    basic_functions.del_previous_setup(os.path.join(path_data_ed, '_results_weather_plots'))

    all_result_folders = os.listdir(path_data_ed)
    paths_folders_result = []

    for result_folder in all_result_folders:
        if result_folder not in to_ignores and result_folder[-4:] not in endings_to_ignore:
            paths_folders_result.append(
                os.path.join(path_data_ed, result_folder))

    basic_functions.create_folder(os.path.join(path_data_ed, '_results_weather_plots'))

    fueltype_str_to_create_maps = [
        'electricity']
    fueltype_str ='electricity'
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    ####################################################################
    # Collect regional simulation data for every realisation
    ####################################################################
    total_regional_demand = pd.DataFrame()

    for path_result_folder in paths_folders_result:
        print("path_result_folder: " + str(path_result_folder))

        data = {}
    
        # Simulation information is read in from .ini file for results
        data['enduses'], data['assumptions'], data['regions'] = data_loader.load_ini_param(
            os.path.join(path_result_folder))
        
        pop_data = read_data.read_scenaric_population_data(
            os.path.join(path_result_folder, 'model_run_pop'))

        # Update path
        path_result_folder = os.path.join(path_result_folder, 'simulation_results')
        data['local_paths'] = data_loader.get_local_paths(path_result_folder)
        data['result_paths'] = data_loader.get_result_paths(os.path.join(path_result_folder))
        data['lookups'] = lookup_tables.basic_lookups()

        # Other information is read in
        data['assumptions'] = {}
        data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

        # --------------------------------------------
        # Reading in results from different model runs
        # --------------------------------------------
        results_container = read_weather_results.read_in_weather_results(
            data['result_paths']['data_results_model_runs'],
            data['assumptions']['seasons'],
            data['assumptions']['model_yeardays_daytype'])

        # Collect results of realisation (dataframe with row: realisation, column=region)
        realisation_data = pd.DataFrame(
            [results_container['ed_reg_tot_y'][simulation_yr_to_plot][fueltype_int]],
            columns=data['regions'])

        total_regional_demand = total_regional_demand.append(realisation_data)

    # ------------------------------
    # Plotting spatial results
    # ------------------------------
    fig_3_weather_map.total_annual_demand(
        total_regional_demand,
        path_shapefile_input,
        data['regions'],
        data['lookups']['fueltypes_nr'],
        data['lookups']['fueltypes'],
        pop_data=pop_data,
        simulation_yr_to_plot=simulation_yr_to_plot,
        result_path=path_result_folder,
        fig_name="tot_demand_{}.pdf".format(fueltype_str))

    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")


path_shapefile_input="C:/Users/cenv0553/ED/data/energy_demand/region_definitions/lad_2016_uk_simplified.shp"

plot_crit_dict = {
    "spatial_results": True,              # Spatial geopanda maps

    "plot_differences_p": True,           # Spatial maps of percentage difference per fueltype over time
    "plot_total_demand_fueltype": True, #False,  # Spatial maps of total demand per fueltype over time
    "plot_population": True,             # Spatial maps of population
    "plot_load_factors": True,           # Spatial maps of load factor
    "plot_load_factors_p": True,         # Spatial maps of load factor change
    "plot_abs_peak_h": True,             # Spatial maps of peak h demand
    "plot_diff_peak_h": True,             # Spatial maps of peak h difference (%)
    "plot_stacked_enduses": True,
    "plot_y_all_enduses": True,
    "plot_fuels_enduses_y": True,
    "plot_lf": True,
    "plot_week_h": True,
    "plot_h_peak_fueltypes": True,
    "plot_averaged_season_fueltype": True, # Compare for every season and daytype the daily loads
    "plot_radar": True,
    "plot_radar_seasonal": True,                      # Plot radar spider charts
    "plot_line_for_every_region_of_peak_demand": True,
    "plot_lad_cross_graphs": True}

main(
    path_data_ed="C:/_NNEW",
    path_shapefile_input=path_shapefile_input,
    plot_crit_dict=plot_crit_dict,
    base_yr=2015)
