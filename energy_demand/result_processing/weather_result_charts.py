"""Read in model results and plot results
"""
import os
import pandas as pd

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.read_write import read_weather_results
from energy_demand.plotting import fig_3_weather_map
from energy_demand.technologies import tech_related
from energy_demand.plotting import fig_3_plot_over_time

def main(
        scenarios_path,
        path_shapefile_input,
        base_yr,
        simulation_yr_to_plot=2050
    ):
    """Read in all results and plot PDFs

    Arguments
    ----------
    scenarios_path : str
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
        'PDF_validation',
        '_results_weather_plots']

    endings_to_ignore = [
        '.pdf',
        '.txt',
        '.ini']

    # -------------------
    # Create result folder
    # -------------------
    result_path = os.path.join(scenarios_path, '_results_weather_plots')
    basic_functions.del_previous_setup(result_path)

    all_scenarios = os.listdir(scenarios_path)
    scenario_result_container = []
    basic_functions.create_folder(result_path)

    for scenario_nr, scenario_name in enumerate(all_scenarios):
        print(" ")
        print("Scenario: {}".format(scenario_name))
        print(" ")
        scenario_path = os.path.join(scenarios_path, scenario_name)
        all_result_folders = os.listdir(scenario_path)
        
        paths_folders_result = []

        for result_folder in all_result_folders:
            if result_folder not in to_ignores and result_folder[-4:] not in endings_to_ignore:
                paths_folders_result.append(
                    os.path.join(scenario_path, result_folder))

        fueltype_str_to_create_maps = ['electricity']

        fueltype_str ='electricity'
        fueltype_int = tech_related.get_fueltype_int(fueltype_str)

        ####################################################################
        # Collect regional simulation data for every realisation
        ####################################################################
        total_regional_demand_electricity = pd.DataFrame()
        peak_hour_demand = pd.DataFrame()
        national_peak = pd.DataFrame()
        regional_share_national_peak = pd.DataFrame()
        national_electricity = pd.DataFrame()
        national_gas = pd.DataFrame()
        national_hydrogen = pd.DataFrame()

        for path_result_folder in paths_folders_result:
            print("path_result_folder: " + str(path_result_folder))

            data = {}

            # Simulation information is read in from .ini file for results
            data['enduses'], data['assumptions'], data['regions'] = data_loader.load_ini_param(
                os.path.join(path_result_folder))

            pop_data = read_data.read_scenaric_population_data(
                os.path.join(path_result_folder, 'model_run_pop'))
  

            path_result_folder = os.path.join(path_result_folder, 'simulation_results')
            path_result_folder_model_runs = os.path.join(path_result_folder, 'model_run_results_txt')

            data['lookups'] = lookup_tables.basic_lookups()

            # Other information is read in
            data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
            data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

            # --------------------------------------------
            # Reading in results from different model runs
            # --------------------------------------------
            results_container = read_weather_results.read_in_weather_results(
                path_result_folder_model_runs,
                data['assumptions']['seasons'],
                data['assumptions']['model_yeardays_daytype'],
                fueltype_str='electricity')

            # --Total demand (dataframe with row: realisation, column=region)
            realisation_data = pd.DataFrame(
                [results_container['ed_reg_tot_y'][simulation_yr_to_plot][fueltype_int]],
                columns=data['regions'])
            total_regional_demand_electricity = total_regional_demand_electricity.append(realisation_data)

            # National per fueltype electricity
            fueltype_elec_int = tech_related.get_fueltype_int('electricity')
            simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_elec_int] for year in results_container['national_all_fueltypes'].keys()]

            realisation_data = pd.DataFrame(
                [simulation_yrs_result],
                columns=data['assumptions']['sim_yrs'])
            national_electricity = national_electricity.append(realisation_data)

            # National per fueltype gas
            fueltype_elec_int = tech_related.get_fueltype_int('gas')
            simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_elec_int] for year in results_container['national_all_fueltypes'].keys()]

            realisation_data = pd.DataFrame(
                [simulation_yrs_result],
                columns=data['assumptions']['sim_yrs'])
            national_gas = national_gas.append(realisation_data)

            # National per fueltype hydrogen
            fueltype_elec_int = tech_related.get_fueltype_int('hydrogen')
            simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_elec_int] for year in results_container['national_all_fueltypes'].keys()]

            realisation_data = pd.DataFrame(
                [simulation_yrs_result],
                columns=data['assumptions']['sim_yrs'])
            national_hydrogen = national_hydrogen.append(realisation_data)

            # --Peak day demand (dataframe with row: realisation, column=region)
            realisation_data = pd.DataFrame(
                [results_container['ed_reg_peakday_peak_hour'][simulation_yr_to_plot][fueltype_int]],
                columns=data['regions'])

            peak_hour_demand = peak_hour_demand.append(realisation_data)

            # --National peak
            simulation_yrs_result = [results_container['national_peak'][year][fueltype_int] for year in results_container['national_peak'].keys()]

            realisation_data = pd.DataFrame(
                [simulation_yrs_result],
                columns=data['assumptions']['sim_yrs'])
            national_peak = national_peak.append(realisation_data)

            # --Regional percentage of national peak demand
            realisation_data = pd.DataFrame(
                [results_container['regional_share_national_peak'][simulation_yr_to_plot]],
                columns=data['regions'])

            regional_share_national_peak = regional_share_national_peak.append(realisation_data)

        # Add to scenario container
        scenario_result_container.append({
            'scenario_name': scenario_name,
            'peak_hour_demand': peak_hour_demand,
            'national_peak': national_peak,
            'regional_share_national_peak': regional_share_national_peak,

            'total_regional_demand_electricity': total_regional_demand_electricity,
            'national_electricity': national_electricity,
            'national_gas': national_gas,
            'national_hydrogen': national_hydrogen,
        })

    # ------------------------------
    # Plot national sum over time per fueltype and scenario
    # ------------------------------
    print("... plotting national sum of fueltype over time")
    fig_3_plot_over_time.fueltypes_over_time(
        scenario_result_container=scenario_result_container,
        sim_yrs=data['assumptions']['sim_yrs'],
        fig_name="fueltypes_over_time_{}.pdf".format(fueltype_str),
        fueltypes=['electricity', 'gas', 'hydrogen'],
        result_path=result_path,
        unit='TWh',
        plot_points=True,
        crit_smooth_line=True,
        seperate_legend=False)

    # ------------------------------
    # Plot national peak change over time for each scenario
    # including weather variability
    # ------------------------------
    fig_3_plot_over_time.scenario_over_time(
        scenario_result_container=scenario_result_container,
        sim_yrs=data['assumptions']['sim_yrs'],
        fig_name="scenarios_peak_over_time_{}.pdf".format(fueltype_str),
        plot_points=True,
        result_path=result_path,
        crit_smooth_line=True,
        seperate_legend=False)

    # ------------------------------
    # Plotting spatial results for electricity
    # ------------------------------
    for i in scenario_result_container:
        scenario_name = i['scenario_name']
        total_regional_demand_electricity = i['total_regional_demand_electricity']
        peak_hour_demand = i['peak_hour_demand']
        regional_share_national_peak = i['regional_share_national_peak']

        print("... plot spatial map of total annual demand")
        field_to_plot = 'std_dev'
        fig_3_weather_map.total_annual_demand(
            total_regional_demand_electricity,
            path_shapefile_input,
            data['regions'],
            pop_data=pop_data,
            simulation_yr_to_plot=simulation_yr_to_plot,
            result_path=result_path,
            fig_name="{}__tot_demand__{}_{}_{}.pdf".format(scenario_name, field_to_plot, fueltype_str, simulation_yr_to_plot),
            field_to_plot=field_to_plot,
            unit='GW')

        print("... plot spatial map of peak hour demand")
        field_to_plot = 'std_dev'
        fig_3_weather_map.total_annual_demand(
            peak_hour_demand,
            path_shapefile_input,
            data['regions'],
            pop_data=pop_data,
            simulation_yr_to_plot=simulation_yr_to_plot,
            result_path=result_path,
            fig_name="{}__peak_h_demand_{}_{}_{}.pdf".format(scenario_name, field_to_plot, fueltype_str, simulation_yr_to_plot),
            field_to_plot=field_to_plot,
            unit='GW')

        print("... plot spatial map of percentage of regional peak hour demand")
        field_to_plot = 'mean'
        fig_3_weather_map.total_annual_demand(
            regional_share_national_peak,
            path_shapefile_input,
            data['regions'],
            pop_data=pop_data,
            simulation_yr_to_plot=simulation_yr_to_plot,
            result_path=result_path,
            fig_name="{}__regional_share_national_peak_{}_{}_{}.pdf".format(scenario_name, field_to_plot, fueltype_str, simulation_yr_to_plot),
            field_to_plot=field_to_plot,
            unit='percentage')

        field_to_plot = 'std_dev'
        fig_3_weather_map.total_annual_demand(
            regional_share_national_peak,
            path_shapefile_input,
            data['regions'],
            pop_data=pop_data,
            simulation_yr_to_plot=simulation_yr_to_plot,
            result_path=result_path,
            fig_name="{}__regional_share_national_peak_{}_{}_{}.pdf".format(scenario_name, field_to_plot, fueltype_str, simulation_yr_to_plot),
            field_to_plot=field_to_plot,
            unit='percentage')

    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")


path_shapefile_input="C:/Users/cenv0553/ED/data/energy_demand/region_definitions/lad_2016_uk_simplified.shp"

main(
    scenarios_path="C:/_FF",
    path_shapefile_input=path_shapefile_input,
    base_yr=2015)
