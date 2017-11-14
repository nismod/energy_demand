"""Read in model results and plot results
"""
import os
import logging
from energy_demand.read_write import data_loader, read_data, write_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results
from energy_demand.basic import logger_setup

def main(local_data_path):
    """Read in all results and plot PDFs

    Arguments
    ----------
    local_data_path : str
        Path to results
    """
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_plotting.log"))
    # ------------------
    # Load necessary inputs for read in
    # ------------------
    data = {}
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()

    # Simulation information is read in from .ini file for results
    data['sim_param'], data['enduses'], data['assumptions'], data['reg_nrs'], data['lu_reg'] = data_loader.load_sim_param_ini(
        data['local_paths']['data_results'])

    # Other information is read in
    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

    # --------------------------------------------
    # Reading in results from different model runs
    # --------------------------------------------
    results_container = read_data.read_in_results(
        data['local_paths']['data_results_model_runs'],
        data['lookups'],
        data['assumptions']['seasons'],
        data['assumptions']['model_yeardays_daytype'])

    # ----------------
    # Write results to CSV files and merge with shapefile
    # ----------------
    write_data.create_shp_results(
        results_container,
        data['local_paths'],
        data['lookups'],
        data['lu_reg'])

    # ------------------------------
    # Plotting results
    # ------------------------------
    plotting_results.run_all_plot_functions(
        results_container,
        data['reg_nrs'],
        data['lookups'],
        data['local_paths'],
        data['assumptions'],
        data['sim_param'],
        data['enduses'])

    logging.info("... finished reading and plotting results")

main("C://Users//cenv0553//nismod//data_energy_demand")
