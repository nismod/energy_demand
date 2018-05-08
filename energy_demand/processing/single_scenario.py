"""Read in model results and plot results
"""
import os
import logging
from energy_demand.read_write import data_loader, read_data, write_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import logger_setup, basic_functions
from energy_demand.basic import lookup_tables

def main(path_data_energy_demand, path_shapefile_input):
    """Read in all results and plot PDFs

    Arguments
    ----------
    path_data_energy_demand : str
        Path to results
    path_shapefile_input : str
        Path to shapefile
    """
    print("Start processing")

    plot_crit_dict = {
        "write_shapefiles": False,          # Write shapefiles
        "spatial_results": True,            # Spatial geopanda maps

        "plot_differences_p": True,           # Spatial maps of percentage difference per fueltype over time
        "plot_total_demand_fueltype": False,  # Spatial maps of total demand per fueltype over time
        "plot_population": False,             # Spatial maps of population
        "plot_load_factors": False,           # Spatial maps of load factor 
        "plot_load_factors_p": False,         # Spatial maps of load factor change
        "plot_peak_h": False,                 # Spatial maps of peak h demand

        "plot_stacked_enduses": True,
        "plot_y_all_enduses": True,
        "plot_fuels_enduses_y": True,
        "plot_lf": False,
        "plot_week_h": True,
        "plot_h_peak_fueltypes": True,
        "plot_averaged_season_fueltype": True, # Compare for every season and daytype the daily loads
        "plot_radar" : True,
        "plot_radar_seasonal" : False,                      # Plot radar spider charts
        "plot_line_for_every_region_of_peak_demand" : True,
        "plot_lad_cross_graphs" : True} 

    # Set up logger
    logger_setup.set_up_logger(
        os.path.join(
            path_data_energy_demand, "plotting.log"))

    # ------------------
    # Load necessary inputs for read in
    # ------------------
    data = {}
    data['local_paths'] = data_loader.load_local_paths(
        path_data_energy_demand)
    data['result_paths'] = data_loader.load_result_paths(
        os.path.join(path_data_energy_demand))
    data['lookups'] = lookup_tables.basic_lookups()

    # ---------------
    # Folder cleaning
    # ---------------
    basic_functions.del_previous_setup(data['result_paths']['data_results_PDF'])
    basic_functions.del_previous_setup(data['result_paths']['data_results_shapefiles'])
    basic_functions.create_folder(data['result_paths']['data_results_PDF'])
    basic_functions.create_folder(data['result_paths']['data_results_shapefiles'])

    # Simulation information is read in from .ini file for results
    data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
        os.path.join(path_data_energy_demand))

    # Other information is read in
    data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_daytype(year_to_model=2015)

    # Read scenario data
    data['scenario_data'] = {}
    data['scenario_data']['population'] = read_data.read_scenaric_population_data(
        data['result_paths']['model_run_pop'])

    # --------------------------------------------
    # Reading in results from different model runs
    # Read in and plot in same step if memory is a problem
    # --------------------------------------------
    results_container = read_data.read_in_results(
        data['result_paths']['data_results_model_runs'],
        data['assumptions']['seasons'],
        data['assumptions']['model_yeardays_daytype'])

    # ------------------------------
    # Plotting other results
    # ------------------------------
    plotting_results.run_all_plot_functions(
        results_container,
        data['reg_nrs'],
        data['regions'],
        data['lookups'],
        data['result_paths'],
        data['assumptions'],
        data['enduses'],
        plot_crit=plot_crit_dict)

    # ------------------------------
    # Plotting spatial results
    # ------------------------------
    if plot_crit_dict['spatial_results']:
        print("plotting geopandas")
        result_mapping.create_geopanda_files(
            data,
            results_container,
            data['result_paths']['data_results_shapefiles'],
            data['regions'],
            data['lookups']['fueltypes_nr'],
            data['lookups']['fueltypes'],
            path_shapefile_input,
            plot_crit_dict)

    # ----------------
    # Write results to CSV files and merge with shapefile
    # ----------------
    if plot_crit_dict['write_shapefiles']:
        write_data.create_shp_results(
            data,
            results_container,
            data['local_paths'],
            data['lookups'],
            data['regions'])


    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")
