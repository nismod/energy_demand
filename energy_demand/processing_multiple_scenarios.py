"""Generate plots for multiple scenarios 
"""
import os
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios
from energy_demand import processing
from energy_demand.basic import basic_functions

def process_result_multi_scen(path_to_scenarios, path_shapefile_input):
    """Iterate the folders with scenario
    runs and calculate PDF results

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """
    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    for scenario in scenarios:
        processing.main(
            os.path.join(path_to_scenarios, scenario),
            path_shapefile_input)

    return

def process_scenarios(path_to_scenarios, year_to_model=2015):
    """Iterate folder with scenario results and plot charts

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    """
    # Delete folder results if existing
    path_result_folder = os.path.join(path_to_scenarios, "results_multiple_scenarios")
    basic_functions.delete_folder(path_result_folder)

    seasons = date_prop.get_season(
        year_to_model=year_to_model)

    model_yeardays_daytype, _, _ = date_prop.get_model_yeardays_daytype(
        year_to_model=year_to_model)

    # Get all folders with scenario run results  (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    # -------------------------------
    # Iterate folders and get results
    # -------------------------------
    scenario_data = {}
    for scenario in scenarios:

        # Add scenario name to folder
        scenario_data[scenario] = {}

        path_to_result_files = os.path.join(
            path_to_scenarios,
            scenario,
            '_result_data',
            'model_run_results_txt')

        scenario_data[scenario] = read_data.read_in_results(
            path_runs=path_to_result_files,
            seasons=seasons,
            model_yeardays_daytype=model_yeardays_daytype)

    # -----------------------
    # Generate result folder
    # -----------------------
    basic_functions.create_folder(path_result_folder)

    # ------------
    # Create plots
    # ------------
    # Plot total demand for every year in line plot
    plotting_multiple_scenarios.plot_tot_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_multiple.pdf"),
        plotshow=False)

    # Plot for all regions demand for every year in line plot
    plotting_multiple_scenarios.plot_reg_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "reg_y_multiple.pdf"),
        plotshow=False)

    # Plot comparison of total demand for a year for all LADs (scatter plot)
    plotting_multiple_scenarios.plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot=2050,
        fig_name=os.path.join(path_result_folder, "LAD_multiple.pdf"),
        plotshow=False)

    # Plot different profiels in radar plot
    plotting_multiple_scenarios.plot_radar_plots_average_peak_day(
        scenario_data,
        year_to_plot=2050,
        fig_name=os.path.join(path_result_folder),
        plotshow=False)
    return

# ------------------------------------
# Execute rusult processing for every scenario
# ------------------------------------^
'''
process_result_multi_scen(
    os.path.abspath("C:/Users/cenv0553/nismod/data_energy_demand/_MULT2"),
    os.path.abspath('C:/Users/cenv0553/nismod/data_energy_demand/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp'))
'''

# ------------------------------------
# Generate plots across all scenarios
# ------------------------------------
process_scenarios(os.path.abspath("C:/Users/cenv0553/nismod/data_energy_demand/_MULT2"))
