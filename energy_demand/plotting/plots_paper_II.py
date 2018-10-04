"""All plots of paper II
"""
import os
from collections import defaultdict
import numpy as np

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.plotting import fig_weather_variability_priod
from energy_demand.plotting import fig_total_demand_peak
from energy_demand.plotting import fig_spatial_local_regional
from energy_demand.validation import elec_national_data
from energy_demand.technologies import tech_related
from energy_demand.plotting import fig_p2_weather_var
from energy_demand.plotting import fig_p2_annual_hours_sorted

def main(
        path_data_ed,
        path_shapefile_input,
        plot_crit_dict):
    """Figure II plots
    """
    data = {}

    # ---------------------------------------------------------
    # Iterate folders and read out all weather years and stations
    # ---------------------------------------------------------
    all_result_folders = os.listdir(path_data_ed)
    paths_folders_result = []
    weather_yrs = []
    weather_station_per_y = {}

    for result_folder in all_result_folders:
        try:
            split_path_name = result_folder.split("__")

            weather_yr = int(split_path_name[0])
            weather_yrs.append(weather_yr)

            try:
                weather_station = int(split_path_name[1])
            except:
                weather_station = "all_station"

            try:
                weather_station_per_y[weather_yr].append(weather_station)
            except:
                weather_station_per_y[weather_yr] = [weather_station]

            # Collect all paths to simulation result folders
            paths_folders_result.append(
                os.path.join(path_data_ed, result_folder))

        except ValueError:
            pass

    # -----------
    # Used across different plots
    # -----------
    data['lookups'] = lookup_tables.basic_lookups()

    data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
        os.path.join(path_data_ed))

    data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

    path_out_plots = os.path.abspath(os.path.join(path_data_ed, '..', '_results_PDF_figs'))
    basic_functions.del_previous_setup(path_out_plots)
    basic_functions.create_folder(path_out_plots)

    population_data = read_data.read_scenaric_population_data(
        os.path.join(path_data_ed, 'model_run_pop'))
    
    # ####################################################################
    # Create plot with regional and non-regional plots for second paper
    # Compare hdd calculations and disaggregation of regional and local
    # ####################################################################
    if plot_crit_dict['plot_national_regional_hdd_disaggregation']:

        # Specify paths
        path_val_elec_2015 = os.path.join(
            "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
            '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')

        path_non_regional_elec_2015 = os.path.abspath(os.path.join(path_data_ed, '..',  "_FigII_non_regional_2015"))

        # Reading in results from different weather_yrs and aggregate
        data_container = defaultdict(dict)
        for weather_yr in weather_yrs:

            station_tot_fueltype_h = {}

            for weather_station in weather_station_per_y[weather_yr]:

                path_with_txt = os.path.join(
                    path_data_ed, "{}__{}".format(weather_yr, weather_station), 'model_run_results_txt')

                results_container = read_data.read_in_results(
                    path_with_txt,
                    data['assumptions']['seasons'],
                    data['assumptions']['model_yeardays_daytype'])

                # Store data in weather container
                tot_fueltype_h = fig_weather_variability_priod.sum_all_enduses_fueltype(
                    results_container['results_enduse_every_year'])

                station_tot_fueltype_h[weather_station] = tot_fueltype_h

            data_container['tot_fueltype_h'][weather_yr] = station_tot_fueltype_h

        #---Collect non regional 2015 elec data
        year_non_regional = 2015 
        path_with_txt = os.path.join(
            path_non_regional_elec_2015,
            "{}__{}".format(str(weather_yr), "all_stations"),
            'model_run_results_txt')

        demand_year_non_regional = read_data.read_in_results(
            path_with_txt,
            data['assumptions']['seasons'],
            data['assumptions']['model_yeardays_daytype'])

        # Store data in weather container
        tot_fueltype_h = fig_weather_variability_priod.sum_all_enduses_fueltype(
            demand_year_non_regional['results_enduse_every_year'])
        fueltype_int = tech_related.get_fueltype_int('electricity')

        non_regional_elec_2015 = tot_fueltype_h[year_non_regional][fueltype_int]

        # ---Collect real electricity data of year 2015
        elec_2015_indo, _ = elec_national_data.read_raw_elec_2015(
            path_val_elec_2015)

        # Factor data as total sum is not identical
        f_diff_elec = np.sum(non_regional_elec_2015) / np.sum(elec_2015_indo)
        elec_factored_yh = f_diff_elec * elec_2015_indo

        # ---Plot figure
        fig_spatial_local_regional.run(
            data_input=data_container['tot_fueltype_h'],
            weather_yr=2015,
            fueltype_str='electricity',
            simulation_yr_to_plot=2015, # Simulation year to plot
            period_h=list(range(0,8760)), #period to plot
            validation_elec_2015=elec_factored_yh,
            non_regional_elec_2015=non_regional_elec_2015,
            fig_name=os.path.join(path_out_plots, "fig_paper_II.pdf"))

    ####################################################################
    # Plotting weather variability results for all weather stations (Fig 2b)
    #
    ####################################################################

    # --------------------------------------------
    # Reading in results from different weather_yrs and aggregate
    # --------------------------------------------
    weather_yr_container = defaultdict(dict)

    for weather_yr in weather_yrs:
        results_container = read_data.read_in_results(
            os.path.join(
                path_data_ed, "{}__{}".format(str(weather_yr), "all_stations"),
                'model_run_results_txt'),
            data['assumptions']['seasons'],
            data['assumptions']['model_yeardays_daytype'])

        # Store data in weather container
        tot_fueltype_yh = fig_weather_variability_priod.sum_all_enduses_fueltype(
            results_container['results_enduse_every_year'])

        weather_yr_container['tot_fueltype_yh'][weather_yr] = tot_fueltype_yh
        weather_yr_container['results_enduse_every_year'][weather_yr] = results_container['results_every_year']

    # ---------------
    # Plot
    # ---------------
    if plot_crit_dict['plot_weather_day_year']:

        # --------------------------------------------
        # Plot peak demand and total demand per fueltype
        # --------------------------------------------
        for fueltype_str in data['lookups']['fueltypes'].keys():

            fig_total_demand_peak.run(
                data_input=weather_yr_container['tot_fueltype_yh'],
                fueltype_str=fueltype_str,
                fig_name=os.path.join(
                    path_out_plots, "tot_{}_h.pdf".format(fueltype_str)))

        # plot over period of time across all weather scenario
        fig_weather_variability_priod.run(
            data_input=weather_yr_container['tot_fueltype_yh'],
            fueltype_str='electricity',
            simulation_yr_to_plot=2015, # Simulation year to plot
            period_h=list(range(200,500)), #period to plot
            fig_name=os.path.join(
                path_out_plots, "weather_var_period.pdf"))

    # ####################################################################
    # Plot for paper II, specific figure
    # ####################################################################
    if plot_crit_dict['plot_spatial_weather_var_peak']:
        # Plot maps of spatial variabioly related to heating use
        fig_p2_weather_var.run(
            data_input=weather_yr_container['results_enduse_every_year'],
            regions=data['regions'],
            simulation_yr_to_plot=2015, # Simulation year to plot
            population=population_data[2015],
            fueltype_str='electricity',
            path_shapefile=path_shapefile_input,
            fig_name=os.path.join(path_out_plots, "fig_paper_IIb_weather_var_map.pdf"))
    
    # ####################################################################
    # Create plot with regional and non-regional plots for second paper
    # Compare hdd calculations and disaggregation of regional and local
    # ####################################################################
    if plot_crit_dict['plot_scenarios_sorted']:

        fig_p2_annual_hours_sorted.run(
            data_input=weather_yr_container['results_enduse_every_year'],
            regions=data['regions'],
            simulation_yrs_to_plot=[2015], # Simulation year to plot
            fueltype_str='electricity',
            path_shapefile=path_shapefile_input,
            fig_name=os.path.join(path_out_plots, "fig_paper_IIb_weather_var_map.pdf"))
