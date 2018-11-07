"""Generate charts from multiple scenarios
"""
import os
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import data_loader

from energy_demand.plotting import fig_cross_graphs

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
    heat_pump_range_plot = False        # Plot of changing scenario values stored in scenario name
    plot_multiple_cross_charts = True   # Compare cross charts of different scenario
    comparison_year = 2050
    year_to_plot = 2050

    # Delete folder results if existing
    path_result_folder = os.path.join(
        path_to_scenarios, "__results_multiple_scenarios")

    basic_functions.delete_folder(path_result_folder)

    seasons = date_prop.get_season(
        year_to_model=year_to_model)

    model_yeardays_daytype, _, _ = date_prop.get_yeardays_daytype(
        year_to_model=year_to_model)

    lookups = lookup_tables.basic_lookups()

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    # Simulation information is read in from .ini file for results
    path_fist_scenario = os.path.join(path_to_scenarios, scenarios[0])
    enduses, assumptions, regions = data_loader.load_ini_param(
        path_fist_scenario)

    # -------------------------------
    # Iterate folders and get results
    # -------------------------------
    scenario_data = {}
    for scenario in scenarios:
        scenario_data[scenario] = {}

        all_stations = os.listdir(
            os.path.join(path_to_scenarios, scenario))

        _to_igore = [
            'infoparam.txt',
            'model_run_pop',
            'PDF_validation', 'model_run_sim_param.ini']

        for station in all_stations:
            if station not in _to_igore:

                path_to_result_files = os.path.join(
                    path_to_scenarios,
                    scenario,
                    station,
                    'model_run_results_txt')

                scenario_data[scenario] = read_data.read_in_results(
                    path_result=path_to_result_files,
                    seasons=seasons,
                    model_yeardays_daytype=model_yeardays_daytype)
            else:
                pass

    # Create result folder
    basic_functions.create_folder(path_result_folder)

    # -------------------------------
    # Generate plot with heat pump ranges
    # -------------------------------
    if heat_pump_range_plot:

        plotting_multiple_scenarios.plot_heat_pump_chart(
            lookups,
            regions,
            scenario_data,
            fig_name=os.path.join(path_result_folder, "comparison_hp_service_switch_and_lf.pdf"),
            fueltype_str_input='electricity',
            plotshow=True)

    # -------------------------------
    # Compare cross charts for different scenario
    # Ideally only compare two scenario
    # -------------------------------
    if plot_multiple_cross_charts:
        fig_cross_graphs.plot_cross_graphs_scenarios(
            base_yr=2015,
            comparison_year=comparison_year,
            regions=regions,
            scenario_data=scenario_data,
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(path_result_folder, "cross_chart_electricity.pdf"),
            label_points=False,
            plotshow=False)

        fig_cross_graphs.plot_cross_graphs_scenarios(
            base_yr=2015,
            comparison_year=comparison_year,
            regions=regions,
            scenario_data=scenario_data,
            fueltype_int=lookups['fueltypes']['gas'],
            fueltype_str='gas',
            fig_name=os.path.join(path_result_folder, "cross_chart_gas.pdf"),
            label_points=False,
            plotshow=False)

    # -------------------------------
    # Plot total demand for every year in line plot
    # -------------------------------
    plotting_multiple_scenarios.plot_tot_fueltype_y_over_time(
        scenario_data,
        lookups['fueltypes'],
        fueltypes_to_plot=['electricity', 'gas'],
        fig_name=os.path.join(path_result_folder, "tot_y_multiple_fueltypes.pdf"),
        txt_name=os.path.join(path_result_folder, "tot_y_multiple_fueltypes.txt"),
        plotshow=False)

    plotting_multiple_scenarios.plot_tot_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot for all regions demand for every year in line plot
    # -------------------------------
    plotting_multiple_scenarios.plot_reg_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "reg_y_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot comparison of total demand for a year for all LADs (scatter plot)
    # -------------------------------
    plotting_multiple_scenarios.plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot=year_to_plot,
        fig_name=os.path.join(path_result_folder, "LAD_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot different profiles in radar plot (spider plot)
    # -------------------------------
    plotting_multiple_scenarios.plot_radar_plots_average_peak_day(
        scenario_data,
        fueltype_to_model='electricity',
        fueltypes=lookups['fueltypes'],
        year_to_plot=year_to_plot,
        fig_name=os.path.join(path_result_folder))

    plotting_multiple_scenarios.plot_radar_plots_average_peak_day(
        scenario_data,
        fueltype_to_model='gas',
        fueltypes=lookups['fueltypes'],
        year_to_plot=year_to_plot,
        fig_name=os.path.join(path_result_folder))

    # ----------------------
    # Plot peak hour of all fueltypes for different scenario
    # ----------------------
    plotting_multiple_scenarios.plot_tot_y_peak_hour(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_peak_h_electricity.pdf"),
        fueltype_str_input='electricity',
        plotshow=False)

    plotting_multiple_scenarios.plot_tot_y_peak_hour(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_peak_h_gas.pdf"),
        fueltype_str_input='gas',
        plotshow=False)
    print("Finished processing multiple scenario")
    return

# Generate plots across all scenarios

#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/scen_A"))
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/scen_B"))
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/scen_C"))
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/scen_D"))

#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/Fig_11"))
process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/scen_C_Fig12"))

##process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/Fig_08_09"))
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/Fig_13"))  # Color scheme Fig 13
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ed/results/_multiple_TEST"))