"""All plots of paper II
"""
import os
from collections import defaultdict
import numpy as np

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.basic import lookup_tables
from energy_demand.plotting import fig_weather_variability_priod
from energy_demand.plotting import fig_total_demand_peak
from energy_demand.plotting import fig_p2_temporal_validation
from energy_demand.validation import elec_national_data
from energy_demand.technologies import tech_related
from energy_demand.plotting import fig_p2_annual_hours_sorted
from energy_demand.plotting import fig_p2_spatial_val

def main(
        path_data_ed,
        path_shapefile_input,
        path_out_plots,
        plot_crit_dict):
    """Figure II plots
    """

    # ---------------------------------------------------------
    # Iterate folders and read out all weather years and stations
    # ---------------------------------------------------------
    all_result_folders = os.listdir(path_data_ed)
    paths_folders_result = []
    weather_yrs = []
    weather_station_per_y = {}
    all_calculated_yrs_paths = []
    for result_folder in all_result_folders:
        try:
            split_path_name = result_folder.split("__")
            weather_yr = int(split_path_name[0])
            weather_yrs.append(weather_yr)
            try:
                weather_station = int(split_path_name[1])
            except:
                weather_station = "all_stations"
            try:
                weather_station_per_y[weather_yr].append(weather_station)
            except:
                weather_station_per_y[weather_yr] = [weather_station]

            # Collect all paths to simulation result folders
            paths_folders_result.append(
                os.path.join(path_data_ed, result_folder))
            
            tupyle_yr_path = (weather_yr, os.path.join(path_data_ed, result_folder))
            all_calculated_yrs_paths.append(tupyle_yr_path)

        except ValueError:
            pass

    # -----------
    # Used across different plots
    # -----------
    data = {}
    data['lookups'] = lookup_tables.basic_lookups()

    data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
        os.path.join(path_data_ed))

    data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

    population_data = read_data.read_scenaric_population_data(
        os.path.join(path_data_ed, 'model_run_pop'))

    ####################################################################
    # Plotting weather variability results for all weather stations (Fig 2b)
    ####################################################################
    weather_yr_container = defaultdict(dict)

    for weather_yr, result_folder in all_calculated_yrs_paths:
        results_container = read_data.read_in_results(
            os.path.join(result_folder, 'model_run_results_txt'),
            data['assumptions']['seasons'],
            data['assumptions']['model_yeardays_daytype'])

        weather_yr_container['tot_fueltype_yh'][weather_yr] = results_container['tot_fueltype_yh'] #tot_fueltype_yh
        weather_yr_container['results_enduse_every_year'][weather_yr] = results_container['ed_fueltype_regs_yh']

    # ####################################################################
    # Plot demand over time and peak over time (for modassar paper)
    # ####################################################################
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
    # Spatial maps of weather variability
    # ####################################################################
    if plot_crit_dict['plot_spatial_weather_var_peak']:
        # Plot maps of spatial variabioly related to heating use
        fig_weather_variability_priod.run(
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

def plot_fig_spatio_temporal_validation(
        path_regional_calculations,
        path_rolling_elec_demand,
        path_temporal_elec_validation,
        path_temporal_gas_validation,
        path_non_regional_elec_2015,
        path_out_plots
    ):
    """
    Create plot with regional and non-regional plots for second paper
    Compare hdd calculations and disaggregation of regional and local
    """
    # ---------------------------------------------------------
    # Iterate folders and read out all weather years and stations
    # ---------------------------------------------------------
    all_result_folders = os.listdir(path_regional_calculations)

    paths_folders_result = []
    data_container = defaultdict(dict)
    ed_fueltype_regs_yh = defaultdict(dict)
    weather_yr_station_tot_fueltype_yh = defaultdict(dict)
    residential_results = defaultdict(dict)
    for scenario_folder in all_result_folders:
        print("Scenario folder: " + str(scenario_folder))
        result_folders = os.listdir(os.path.join(path_regional_calculations, scenario_folder))
        for result_folder in result_folders:
            try:
                split_path_name = result_folder.split("__")
                weather_yr = int(split_path_name[0])

                try:
                    weather_station = int(split_path_name[1])
                except:
                    weather_station = "all_stations"

                paths_folders_result.append(
                    os.path.join(path_regional_calculations, result_folder))

                data = {}
                data['lookups'] = lookup_tables.basic_lookups()
                data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
                    os.path.join(path_regional_calculations, all_result_folders[0])) # last result folder
                data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
                data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

                results_container = read_data.read_in_results(
                    os.path.join(
                        path_regional_calculations,
                        scenario_folder,
                        "{}__{}".format(weather_yr, weather_station),
                        'model_run_results_txt'),
                    data['assumptions']['seasons'],
                    data['assumptions']['model_yeardays_daytype'])

                weather_yr_station_tot_fueltype_yh[weather_yr][weather_station] =  results_container['tot_fueltype_yh']
                ed_fueltype_regs_yh[weather_yr][weather_station] = results_container['ed_fueltype_regs_yh']
                residential_results[weather_yr][weather_station] = results_container['residential_results']
            except ValueError:
                pass

    data_container['ed_fueltype_regs_yh'] = ed_fueltype_regs_yh
    data_container['tot_fueltype_yh'] = weather_yr_station_tot_fueltype_yh
    data_container['residential_results'] = residential_results
    data_container = dict(data_container)

    # -------------------------------------------------
    # Collect non regional 2015 elec data
    # Calculated with all regional weather stations
    # -------------------------------------------------
    year_non_regional = 2015
    path_with_txt = os.path.join(
        path_non_regional_elec_2015,
        "{}__{}".format(str(year_non_regional), "all_stations"),
        'model_run_results_txt')

    demand_year_non_regional = read_data.read_in_results(
        path_with_txt,
        data['assumptions']['seasons'],
        data['assumptions']['model_yeardays_daytype'])
    tot_fueltype_yh = demand_year_non_regional['tot_fueltype_yh']

    fueltype_int = tech_related.get_fueltype_int('electricity')

    non_regional_elec_2015 = tot_fueltype_yh[year_non_regional][fueltype_int]

    # ---Collect real electricity data of year 2015
    elec_2015_indo, _ = elec_national_data.read_raw_elec_2015(
        path_rolling_elec_demand)

    # Factor data as total sum is not identical
    f_diff_elec = np.sum(non_regional_elec_2015) / np.sum(elec_2015_indo)
    elec_factored_yh = f_diff_elec * elec_2015_indo

    # *****************************************************************
    # Temporal validation
    # Compare regional and non regional and actual demand over time
    # *****************************************************************
    simulation_yr_to_plot = 2015
    period_to_plot = list(range(0, 8760))
    fig_p2_temporal_validation.run(
        data_input=data_container['tot_fueltype_yh'],
        weather_yr=2015,
        fueltype_str='electricity',
        simulation_yr_to_plot=simulation_yr_to_plot, # Simulation year to plot
        period_h=period_to_plot, #period to plot
        validation_elec_2015=elec_factored_yh,
        non_regional_elec_2015=non_regional_elec_2015,
        fig_name=os.path.join(path_out_plots, "temporal_validation.pdf"),
        plot_show=False)

    # -------------------
    # Spatial validation (not with maps)
    # -------------------   
    # non_regional: All weather station, spatially disaggregated TODO Give BETTER NAMES
    # regional: Only one weather station for whole countr but still data for every region
    weather_yr = 2015
    fig_p2_spatial_val.run(
        simulation_yr_to_plot=simulation_yr_to_plot,
        demand_year_non_regional=demand_year_non_regional['residential_results'][weather_yr],
        demand_year_regional=data_container['residential_results'][weather_yr],
        fueltypes=data['lookups']['fueltypes'],
        fig_path=os.path.join(path_out_plots, "spatial_validation.pdf"),
        path_temporal_elec_validation=path_temporal_elec_validation,
        path_temporal_gas_validation=path_temporal_gas_validation,
        regions=data['regions'],
        plot_crit=True)

    # -------------------
    # Spatial validation (plot regional maps)
    # with deviation from average estimated demand across scenarios
    # -------------------
