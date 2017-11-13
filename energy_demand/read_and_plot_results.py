"""Read in model results and plot results
"""
import os
from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results

def run(local_data_path):
    """
    """
    # ------------------
    # Load necessary inputs for read in
    # ------------------
    data = {}
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()

    # Simulation information is read in from .ini file for results
    data['sim_param'], data['enduses'], data['assumptions'], data['reg_nrs'] = data_loader.load_sim_param_ini(data['local_paths']['data_results'])

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
    print("finished")
    return

run("C://Users//cenv0553//nismod//data_energy_demand")