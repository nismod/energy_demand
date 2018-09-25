"""Read in model results and plot results
"""
import os
from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import logger_setup, basic_functions
from energy_demand.basic import lookup_tables

def main(
        path_data_energy_demand,
        path_shapefile_input,
        plot_crit_dict,
        base_yr,
        comparison_year
    ):
    """Read in all results and plot PDFs

    Arguments
    ----------
    path_data_energy_demand : str
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

    # Get all yealy results
    all_result_folders = os.listdir(path_data_energy_demand)

    weather_yrs = []
    for result_folder in all_result_folders:
        try:
            weather_yr = int(result_folder)
            weather_yrs.append(weather_yr)
        except ValueError:
            pass

    # Execute script to generate PDF results
    for weather_yr in weather_yrs:

        path_data_energy_demand_weather_yr = os.path.join(path_data_energy_demand, str(weather_yr))

        # Set up logger
        logger_setup.set_up_logger(
            os.path.join(
                path_data_energy_demand_weather_yr, "plotting.log"))

        # ------------------
        # Load necessary inputs for read in
        # ------------------
        data = {}
        data['local_paths'] = data_loader.get_local_paths(
            path_data_energy_demand_weather_yr)
        data['result_paths'] = data_loader.get_result_paths(
            os.path.join(path_data_energy_demand_weather_yr))
        data['lookups'] = lookup_tables.basic_lookups()

        # ---------------
        # Folder cleaning
        # ---------------
        basic_functions.del_previous_setup(data['result_paths']['data_results_PDF'])
        basic_functions.del_previous_setup(data['result_paths']['data_results_shapefiles'])
        basic_functions.create_folder(data['result_paths']['data_results_PDF'])
        basic_functions.create_folder(data['result_paths']['data_results_shapefiles'])
        basic_functions.create_folder(data['result_paths']['individual_enduse_lp'])

        # Simulation information is read in from .ini file for results
        data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
            os.path.join(path_data_energy_demand))

        # Other information is read in
        data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

        # Read scenario data
        data['scenario_data'] = {}

        data['scenario_data']['population'] = read_data.read_scenaric_population_data(
            os.path.join(path_data_energy_demand, 'model_run_pop'))

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
            plot_crit=plot_crit_dict,
            base_yr=base_yr,
            comparison_year=comparison_year)

        # ------------------------------
        # Plotting spatial results
        # ------------------------------
        if plot_crit_dict['spatial_results']:
            result_mapping.create_geopanda_files(
                data,
                results_container,
                data['result_paths']['data_results_shapefiles'],
                data['regions'],
                data['lookups']['fueltypes_nr'],
                data['lookups']['fueltypes'],
                path_shapefile_input,
                plot_crit_dict,
                base_yr=base_yr)

    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")
