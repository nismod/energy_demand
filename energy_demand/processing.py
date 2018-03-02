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
    # ---------
    # Criterias
    # ---------
    write_shapefiles = False    # Write shapefiles
    spatial_results = False      # Spatial geopanda maps

    # Set up logger
    logger_setup.set_up_logger(
        os.path.join(
            path_data_energy_demand, "logging_plotting.log"))

    # ------------------
    # Load necessary inputs for read in
    # ------------------
    data = {}
    data['local_paths'] = data_loader.load_local_paths(
        path_data_energy_demand)
    data['lookups'] = lookup_tables.basic_lookups()

    # ---------------
    # Folder cleaning
    # ---------------
    basic_functions.del_previous_setup(data['local_paths']['data_results_PDF'])
    basic_functions.del_previous_setup(data['local_paths']['data_results_shapefiles'])
    basic_functions.create_folder(data['local_paths']['data_results_PDF'])
    basic_functions.create_folder(data['local_paths']['data_results_shapefiles'])

    # Simulation information is read in from .ini file for results
    data['sim_param'], data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_sim_param_ini(
        data['local_paths']['data_results'])

    # Other information is read in
    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_daytype(year_to_model=2015)

    # Read scenario data
    data['scenario_data'] = {}
    data['scenario_data']['population'] = read_data.read_scenaric_population_data(
        data['local_paths']['model_run_pop'])

    # --------------------------------------------
    # Reading in results from different model runs
    # Read in and plot in same step if memory is a problem
    # --------------------------------------------
    results_container = read_data.read_in_results(
        data['local_paths']['data_results_model_runs'],
        data['assumptions']['seasons'],
        data['assumptions']['model_yeardays_daytype'])

    # ----------------
    # Write results to CSV files and merge with shapefile
    # ----------------
    if write_shapefiles:
        write_data.create_shp_results(
            data,
            results_container,
            data['local_paths'],
            data['lookups'],
            data['regions'])

    if spatial_results:
        result_mapping.create_geopanda_files(
            data,
            results_container,
            data['local_paths'],
            data['regions'],
            data['lookups']['fueltypes_nr'],
            data['lookups']['fueltypes'],
            path_shapefile_input)

    # ------------------------------
    # Plotting results
    # ------------------------------
    plotting_results.run_all_plot_functions(
        results_container,
        data['reg_nrs'],
        data['regions'],
        data['lookups'],
        data['local_paths'],
        data['assumptions'],
        data['sim_param'],
        data['enduses'])

    logging.info("... finished reading and plotting results")
    print("... finished reading and plotting results")

#main(os.path.abspath("C://Users//cenv0553//nismod//data_energy_demand"))
#main(os.path.abspath("C://DATA_NISMODII//data_energy_demand"))
#main("C:/Users/cenv0553/nismod/data_energy_demand")
