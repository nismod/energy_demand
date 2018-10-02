"""Generate charts from multiple scenarios
"""
import os
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import data_loader

def process_scenarios(path_to_scenarios, year_to_model=2015):
    """Iterate folder with scenario results and plot charts

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    year_to_model : int, default=2015
        Year of base year
    """
    # -----------
    # Charts to plot
    # -----------
    heat_pump_range_plot = True        # Plot of changing scenario values stored in scenario name

    # Delete folder results if existing
    path_result_folder = os.path.join(
        path_to_scenarios, "__results_hp_chart")

    basic_functions.delete_folder(path_result_folder)

    seasons = date_prop.get_season(
        year_to_model=year_to_model)

    model_yeardays_daytype, _, _ = date_prop.get_yeardays_daytype(
        year_to_model=year_to_model)

    lookups = lookup_tables.basic_lookups()

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios_hp = os.listdir(path_to_scenarios)

    scenario_data = {}

    for scenario_hp in scenarios_hp:
        print("HP SCENARIO " + str(scenario_hp))
        print(path_to_scenarios)
        scenario_data[scenario_hp] = {}

        # Simulation information is read in from .ini file for results
        path_fist_scenario = os.path.join(path_to_scenarios, scenario_hp)

        # -------------------------------
        # Iterate folders and get results
        # -------------------------------
        scenarios = os.listdir(path_fist_scenario)

        for scenario in scenarios:

            enduses, assumptions, reg_nrs, regions = data_loader.load_ini_param(
                os.path.join(path_fist_scenario, scenario))

            # Add scenario name to folder
            scenario_data[scenario_hp][scenario] = {}

            path_to_result_files = os.path.join(
                path_fist_scenario,
                scenario,
                'model_run_results_txt')

            scenario_data[scenario_hp][scenario] = read_data.read_in_results(
                path_result=path_to_result_files,
                seasons=seasons,
                model_yeardays_daytype=model_yeardays_daytype)

    # -----------------------
    # Generate result folder
    # -----------------------
    basic_functions.create_folder(path_result_folder)

    # -------------------------------
    # Generate plot with heat pump ranges
    # -------------------------------
    if heat_pump_range_plot:

        plotting_multiple_scenarios.plot_heat_pump_chart_multiple(
            lookups,
            regions,
            hp_scenario_data=scenario_data,
            fig_name=os.path.join(path_result_folder, "comparison_hp_share_peak_h.pdf"),
            txt_name=os.path.join(path_result_folder, "comparison_hp_share_peak_h.txt"),
            fueltype_str_input='electricity',
            plotshow=True)

    return

# Generate plots across all scenarios
process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/Fig_12_multi_hp"))