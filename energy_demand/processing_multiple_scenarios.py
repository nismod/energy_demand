"""Generate plots for multiple scenarios
"""
import os
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios

def plot_multiple_scenarios(path_to_scenarios):
    """Iterate folder with scenario results and plot charts

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """
    seasons = date_prop.read_season(
        year_to_model=2015)

    model_yeardays_daytype, _, _ = date_prop.get_model_yeardays_daytype(
        year_to_model=2015)

    # -------------------------------
    # Get all folders  (name of folder is scenario)
    # -------------------------------
    all_scenario_folders = os.listdir(path_to_scenarios)

    # -------------------------------
    # Iterate folders and get results
    # -------------------------------
    scenario_data = {}
    for folder_scenario in all_scenario_folders:

        # Add scenario name to folder
        scenario_data[folder_scenario] = {}

        path_to_result_files = os.path.join(path_to_scenarios, folder_scenario, '_result_data', 'model_run_results_txt')

        scenario_data[folder_scenario] = read_data.read_in_results(
            path_runs=path_to_result_files,
            seasons=seasons,
            model_yeardays_daytype=model_yeardays_daytype)


    # ------------
    # Create plots
    # ------------
    plotting_multiple_scenarios.plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot=2050,
        fig_path=os.path.join(path_to_scenarios, "LAD_multiple.pdf"),
        plotshow=False)

    return

plot_multiple_scenarios(os.path.abspath("C:/Users/cenv0553/nismod/data_energy_demand/_MULTIPLE_RESULTS"))