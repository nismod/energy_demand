"""Read in model results and plot results
"""
import os
import pandas as pd
import numpy as np

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
        simulation_yrs_to_plot
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
    print("Start creating plots")

    # -------------------
    # Create temperatuere figur plot
    # -------------------
    plot_weather_chart = False
    if plot_weather_chart:
        from energy_demand.plotting import fig3_weather_at_home_plot
        path_weather_data = "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/J-MARIUS_data/_weather_realisation"
        fig3_weather_at_home_plot.plotting_weather_data(path_weather_data)

    # -------------------
    # Create result folder
    # -------------------
    result_path = os.path.join(scenarios_path, '_results_weather_plots')
    basic_functions.del_previous_setup(result_path)
    basic_functions.create_folder(result_path)

    x_chart_yrs_storage = {}

    for simulation_yr_to_plot in simulation_yrs_to_plot:
        print("=================")
        print("...simulation_yr_to_plot: " + str(simulation_yr_to_plot))
        print("=================")
        data = {}
        x_chart_yrs_storage[simulation_yr_to_plot] = {}

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

        all_scenarios_incl_ignored = os.listdir(scenarios_path)
        all_scenarios = []
        for scenario in all_scenarios_incl_ignored:
            if scenario not in to_ignores:
                all_scenarios.append(scenario)

        scenario_result_container = []
        for scenario_nr, scenario_name in enumerate(all_scenarios):
            print(" ")
            print("Scenario: {}".format(scenario_name), flush=True)
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
            fueltype_elec_int = tech_related.get_fueltype_int('electricity')

            ####################################################################
            # Collect regional simulation data for every realisation
            ####################################################################
            total_regional_demand_electricity = pd.DataFrame()
            peak_hour_demand = pd.DataFrame()
            peak_hour_demand_per_person = pd.DataFrame()
            national_peak = pd.DataFrame()
            regional_share_national_peak = pd.DataFrame()
            regional_share_national_peak_pp = pd.DataFrame()
            national_electricity = pd.DataFrame()
            national_gas = pd.DataFrame()
            national_hydrogen = pd.DataFrame()
            national_heating_peak = pd.DataFrame()
            daily_mean_peak_day = pd.DataFrame()

            for path_result_folder in paths_folders_result:
                print("... path_result_folder: {}".format(path_result_folder), flush=True)
                data = {}
                ed_national_heating_peak = {}

                try:

                    # ================================
                    # Loading in only heating peak demands (seperate calculations)
                    # ================================
                    
                    # Simulation information is read in from .ini file for results
                    data['enduses'], data['assumptions'], data['regions'] = data_loader.load_ini_param(os.path.join(path_result_folder))
                    pop_data = read_data.read_scenaric_population_data(os.path.join(path_result_folder, 'model_run_pop'))
                    path_result_folder_heating = os.path.join(path_result_folder, 'simulation_results')
                    path_result_folder_model_runs = os.path.join(path_result_folder_heating, 'model_run_results_txt')
                    data['lookups'] = lookup_tables.basic_lookups()

                    # Read in heating deamnds
                    path_heating_demands = os.path.join(path_result_folder_model_runs, 'enduse_specific_results')
                    all_files = os.listdir(path_heating_demands)
                    for file_name in all_files:
                        
                        ending  = file_name[-4:]
                        if ending == ".npy":
                            year = int(file_name.split("__")[2][:-4])
                            file_path = os.path.join(path_heating_demands, file_name)
                            heating_demand = np.load(file_path)
                            maximum_hour_of_peak_day = heating_demand[fueltype_elec_int].argmax() #get maxim hour of peak day
                            ed_national_heating_peak[year] = heating_demand[fueltype_elec_int][maximum_hour_of_peak_day]

                    simulation_yrs_result = [ed_national_heating_peak[year] for year in simulation_yrs_to_plot]
                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    national_heating_peak = national_heating_peak.append(realisation_data)

                except:
                    raise Exception("... no heating peak data available " + str(path_result_folder))

                try:
                    # Simulation information is read in from .ini file for results
                    data['enduses'], data['assumptions'], data['regions'] = data_loader.load_ini_param(os.path.join(path_result_folder))
                    pop_data = read_data.read_scenaric_population_data(os.path.join(path_result_folder, 'model_run_pop'))
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
                        pop_data,
                        fueltype_str='electricity')

                    # --Total demand (dataframe with row: realisation, column=region)
                    realisation_data = pd.DataFrame(
                        [results_container['ed_reg_tot_y'][simulation_yr_to_plot][fueltype_elec_int]],
                        columns=data['regions'])
                    total_regional_demand_electricity = total_regional_demand_electricity.append(realisation_data)

                    # National per fueltype electricity
                    simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_elec_int] for year in simulation_yrs_to_plot]

                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    national_electricity = national_electricity.append(realisation_data)

                    # National per fueltype gas
                    fueltype_gas_int = tech_related.get_fueltype_int('gas')
                    simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_gas_int] for year in simulation_yrs_to_plot]

                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    national_gas = national_gas.append(realisation_data)

                    # National per fueltype hydrogen
                    fueltype_hydrogen_int = tech_related.get_fueltype_int('hydrogen')
                    simulation_yrs_result = [results_container['national_all_fueltypes'][year][fueltype_hydrogen_int] for year in simulation_yrs_to_plot]

                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    national_hydrogen = national_hydrogen.append(realisation_data)

                    # --Peak hour demand per region (dataframe with row: realisation, column=region)
                    realisation_data = pd.DataFrame(
                        [results_container['ed_reg_peakday_peak_hour'][simulation_yr_to_plot][fueltype_elec_int]],
                        columns=data['regions'])

                    peak_hour_demand = peak_hour_demand.append(realisation_data)

                    # --Peak hour demand / pop per region (dataframe with row: realisation, column=region)
                    realisation_data = pd.DataFrame(
                        [results_container['ed_reg_peakday_peak_hour_per_pop'][simulation_yr_to_plot][fueltype_elec_int]],
                        columns=data['regions'])

                    peak_hour_demand_per_person = peak_hour_demand_per_person.append(realisation_data)

                    # --National peak
                    simulation_yrs_result = [results_container['national_peak'][year][fueltype_elec_int] for year in simulation_yrs_to_plot]

                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    national_peak = national_peak.append(realisation_data)

                    # --Regional percentage of national peak demand
                    realisation_data = pd.DataFrame(
                        [results_container['regional_share_national_peak'][simulation_yr_to_plot]],
                        columns=data['regions'])
                    regional_share_national_peak = regional_share_national_peak.append(realisation_data)

                    # --Regional percentage of national peak demand per person
                    realisation_data = pd.DataFrame(
                        [results_container['regional_share_national_peak_pp'][simulation_yr_to_plot]],
                        columns=data['regions'])

                    regional_share_national_peak_pp = regional_share_national_peak_pp.append(realisation_data)

                    # Mean demand of peak day
                    simulation_yrs_result = [results_container['mean_peak_day_demand'][year][fueltype_elec_int] for year in simulation_yrs_to_plot]
                    realisation_data = pd.DataFrame(
                        [simulation_yrs_result],
                        columns=data['assumptions']['sim_yrs'])
                    daily_mean_peak_day = daily_mean_peak_day.append(realisation_data)
                except:
                    raise Exception("The run '{}' is corrupted".format(path_result_folder))

            # Add to scenario container
            result_entry = {
                'national_heating_peak': national_heating_peak,
                'scenario_name': scenario_name,
                'peak_hour_demand': peak_hour_demand,
                'peak_hour_demand_per_person': peak_hour_demand_per_person,
                'national_peak': national_peak,
                'regional_share_national_peak': regional_share_national_peak,
                'regional_share_national_peak_pp': regional_share_national_peak_pp,
                'total_regional_demand_electricity': total_regional_demand_electricity,
                'national_electricity': national_electricity,
                'national_gas': national_gas,
                'national_hydrogen': national_hydrogen,
                'daily_mean_peak_day': daily_mean_peak_day}

            scenario_result_container.append(result_entry)

            # ---------------------------------------------------------------
            # TEST PLOT X-axis: Contribution to peak y-axis: Std: deviation
            # ---------------------------------------------------------------
            x_chart_yrs_storage[simulation_yr_to_plot][scenario_name] = result_entry

        # ------------------------------
        # Plot national sum over time per fueltype and scenario
        # ------------------------------
        crit_smooth_line = True
        seperate_legend = True

        try:
            print("... plotting national sum of fueltype over time ")
            fig_3_plot_over_time.fueltypes_over_time(
                scenario_result_container=scenario_result_container,
                sim_yrs=data['assumptions']['sim_yrs'],
                fig_name="fueltypes_over_time__{}__{}.pdf".format(simulation_yr_to_plot, fueltype_str),
                fueltypes=['electricity', 'gas', 'hydrogen'],
                result_path=result_path,
                unit='TWh',
                plot_points=True,
                crit_smooth_line=crit_smooth_line,
                seperate_legend=seperate_legend)
        except:
            raise Exception("FAILS national sum")

        # ------------------------------
        # Plot national peak change over time for each scenario including weather variability
        # ------------------------------
        try:
            fig_3_plot_over_time.scenario_over_time(
                scenario_result_container=scenario_result_container,
                field_name='national_peak',
                sim_yrs=data['assumptions']['sim_yrs'],
                fig_name="scenarios_peak_over_time__{}__{}.pdf".format(simulation_yr_to_plot, fueltype_str),
                plot_points=True,
                result_path=result_path,
                crit_smooth_line=crit_smooth_line,
                seperate_legend=seperate_legend)
        except:
            raise Exception("FAILED")
            pass

        # ------------------------------
        # Plot heating peak change over time for each scenario including weather variability
        # ------------------------------
        try:
            fig_3_plot_over_time.scenario_over_time(
                scenario_result_container=scenario_result_container,
                field_name='national_heating_peak',
                sim_yrs=data['assumptions']['sim_yrs'],
                fig_name="scenarios_heating_peak_over_time__{}__{}.pdf".format(simulation_yr_to_plot, fueltype_str),
                plot_points=True,
                result_path=result_path,
                crit_smooth_line=crit_smooth_line,
                seperate_legend=seperate_legend)
        except:
            raise Exception("FAILED")
            pass

        # ------------------------------
        # plot PEAK DAY mean
        # ------------------------------
        try:
            fig_3_plot_over_time.scenario_over_time(
                scenario_result_container=scenario_result_container,
                field_name='daily_mean_peak_day',
                sim_yrs=data['assumptions']['sim_yrs'],
                fig_name="mean_demand_of_peak_day{}__{}.pdf".format(simulation_yr_to_plot, fueltype_str),
                plot_points=True,
                result_path=result_path,
                crit_smooth_line=crit_smooth_line,
                seperate_legend=seperate_legend)
        except:
            raise Exception("FAILED")
            pass

    ## ------------------------------
    ## Plotting x-chart
    ## ------------------------------
    fig_3_plot_over_time.plot_std_dev_vs_contribution(
        scenario_result_container=x_chart_yrs_storage,
        sim_yrs=data['assumptions']['sim_yrs'],
        fig_name="_scenarios_4_chart_absolute.pdf",
        fueltypes=['electricity'],
        result_path=result_path,
        path_shapefile_input=path_shapefile_input,
        unit='TWh',
        plot_points=True)

    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")

# Code to run charts generation for weather paper
main(
    scenarios_path="//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final",
    path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp",
    base_yr=2015,
    simulation_yrs_to_plot=[2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050])
