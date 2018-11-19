"""Function to generate plots based on simulation results stored in a folder
"""
import os
import sys

from energy_demand.basic import basic_functions
from energy_demand.plotting import figs_p2
from energy_demand.plotting import fig_spatial_distribution_of_peak
from energy_demand.plotting import fig_p2_spatial_weather_map
from energy_demand.plotting import fig_p2_total_demand_national_scenarios

def paper_II_plots(
        #/soge-home/staff/cenv0553/ED
        #scenario_path_all_stations_single_weather_yr="C:/Users/cenv0553/ed/results/_multiple_TEST_two_scenarios",
        #scenario_path_all_stations_single_weather_yr="C:/Users/cenv0553/ed/results/_Fig2_multiple_all_yrs_all_stations",
        ed_path='C:/Users/cenv0553/ED',
        scenario_path_single_stations='C:/Users/cenv0553/ED/results/_Fig2_multiple_2015_weather_stations',
        scenario_path_all_stations_single_weather_yr="C:/Users/cenv0553/ED/results/_Fig2_multiple_all_yrs_all_stations",
        path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp"
    ):
    """Iterate the folders with scenario
    runs and generate PDF results of individual
    simulation runs

    """
    # Chose which plots should be generated
    plot_crit_dict = {


        # Scenario plots
        'scenario_plots': False, #True,

        #Plot weather map
        'weather_map': False, #True,

        # Spatio temporal validation
        'spatio_temporal_validation': False, #True,

        # Spatial map of distribution of peak and contribution in terms of overall variability
        "plot_spatial_distribution_of_peak": True,

        # Needs to have weatehryr_stationid files in folder
        "plot_national_regional_hdd_disaggregation": False,

        # Plot weather variability for every weather station
        # of demand generated with regional HDD calculation
        "plot_weather_day_year": False,

        # Plot spatial distribution of differences in
        # variability of demand by weather variability
        # normed by population
        "plot_spatial_weather_var_peak": False,

        # Plot scenario years sorted with weather variability
        "plot_scenarios_sorted": True,
        }


    ####################################################################
    # Plot scenarios 
    ####################################################################
    if plot_crit_dict['scenario_plots']:
        sim_yrs = [2015, 2020, 2030, 2040, 2050]
        sim_yrs = [2015, 2050]

        scenario_result_paths = [
            "C:/Users/cenv0553/ed/results/_scenario_low_elec",
            "C:/Users/cenv0553/ed/results/_scenario_high_elec"]
        
        scenario_result_paths = ["C:/Users/cenv0553/ed/results/_Fig2_multiple_all_yrs_all_stations"]
        
        # Create result folder
        path_out_plots = os.path.join("C:/Users/cenv0553/ed/results/_results_nationalFIGS")
        basic_functions.del_previous_setup(path_out_plots)
        basic_functions.create_folder(path_out_plots)
        
        fig_p2_total_demand_national_scenarios.total_demand_national_scenarios(
            scenario_result_paths,
            sim_yrs=sim_yrs,
            fueltype_str='electricity',
            path_out_plots=os.path.join(path_out_plots, "PDF_national_scenarios.pdf"))

    ####################################################################
    # Plot weather station availability map
    ####################################################################
    if plot_crit_dict['weather_map']:

        # Wheather station distribution map
        path_to_weather_data = os.path.join(ed_path, "data/_raw_data/A-temperature_data/cleaned_weather_stations_data")
        folder_path_weater_stations = os.path.join(ed_path, "data/_raw_data/A-temperature_data/cleaned_weather_stations.csv")
        fig_path = os.path.join(ed_path, scenario_path_single_stations, "weather_station_maps.pdf")
        fig_p2_spatial_weather_map.run(
            path_to_weather_data,
            folder_path_weater_stations,
            path_shapefile=path_shapefile_input,
            fig_path=fig_path)
        
        print("... plotted weather station distribution map")

    ####################################################################
    # Plot regional vs national spatio-temporal validation
    ####################################################################
    if plot_crit_dict['spatio_temporal_validation']:

        path_regional_calculations = os.path.join(scenario_path_single_stations, "_regional_calculations")
        path_non_regional_elec_2015 = os.path.abspath(os.path.join(path_regional_calculations, '..', "_all_stations_wy_2015"))
        path_rolling_elec_demand = os.path.join(ed_path, "energy_demand", "energy_demand", "config_data", '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')
        path_temporal_elec_validation = os.path.join(ed_path, "energy_demand", "energy_demand", "config_data", '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_domestic.csv')
        path_temporal_gas_validation = os.path.join(ed_path, "energy_demand", "energy_demand", "config_data", '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_domestic.csv')

        path_results = os.path.abspath(os.path.join(path_regional_calculations, '..'))
        path_out_plots = os.path.join(path_results, '_results_PDF_figs')
        basic_functions.del_previous_setup(path_out_plots)
        basic_functions.create_folder(path_out_plots)

        # Plot figure national an regional validation comparison
        figs_p2.plot_fig_spatio_temporal_validation(
            path_regional_calculations=path_regional_calculations,
            path_rolling_elec_demand=path_rolling_elec_demand,
            path_temporal_elec_validation=path_temporal_elec_validation,
            path_temporal_gas_validation=path_temporal_gas_validation,
            path_non_regional_elec_2015=path_non_regional_elec_2015,
            path_out_plots=path_out_plots)

        print("... plotted spatio-temporal validation")

    ####################################################################
    # Plot spatial distribution of variability depending on weather year
    # Plot the variability of the contribution of regional peak demand
    # to national peak demand
    ####################################################################
    if plot_crit_dict['plot_spatial_distribution_of_peak']:

        # Create result folder
        path_out_plots = os.path.join(scenario_path_all_stations_single_weather_yr, '_results_PDF_figs')
        basic_functions.del_previous_setup(path_out_plots)
        basic_functions.create_folder(path_out_plots)

        # Get all folders with scenario run results (name of folder is scenario)
        scenarios = os.listdir(scenario_path_all_stations_single_weather_yr)

        scenario_names_ignored = [
            '__results_multiple_scenarios',
            '_FigII_non_regional_2015',
            '_results_PDF_figs']

        only_scenarios = []
        for scenario in scenarios:
            if scenario in scenario_names_ignored:
                pass
            else:
                only_scenarios.append(scenario)

        # Select simulation years
        sim_yrs = [2015, 2050]
        unit = 'kW' #'GW'

        # Plot standard deviation of demand per person in peak hour
        fig_spatial_distribution_of_peak.run_fig_spatial_distribution_of_peak(
            only_scenarios,
            scenario_path_all_stations_single_weather_yr,
            path_shapefile_input,
            sim_yrs=sim_yrs,
            field_to_plot="std_deviation_df_abs_demand_in_peak_h_pp",
            unit=unit,
            fig_path=path_out_plots)

        # Plot standard deviation of percentage of national peak
        fig_spatial_distribution_of_peak.run_fig_spatial_distribution_of_peak(
            only_scenarios,
            scenario_path_all_stations_single_weather_yr,
            path_shapefile_input,
            sim_yrs=sim_yrs,
            field_to_plot='std_deviation_p_demand_peak_h',
            unit='percent',
            fig_path=path_out_plots)

        # Plot standard deviation of absolute demand of national peak
        fig_spatial_distribution_of_peak.run_fig_spatial_distribution_of_peak(
            only_scenarios,
            scenario_path_all_stations_single_weather_yr,
            path_shapefile_input,
            sim_yrs=sim_yrs,
            field_to_plot='std_deviation_abs_demand_peak_h',
            unit=unit,
            fig_path=path_out_plots)

        # Plot maximum peak hour - mean peak hour demand
        fig_spatial_distribution_of_peak.run_fig_spatial_distribution_of_peak(
            only_scenarios,
            scenario_path_all_stations_single_weather_yr,
            path_shapefile_input,
            sim_yrs=sim_yrs,
            field_to_plot='diff_peak_h_minus_mean',
            unit='GW',
            fig_path=path_out_plots)

        print("... plotted variability maps")

    
    print("Finihsed")
    raise Exception("Finished")

    ####################################################################
    # left overs
    ####################################################################
    for scenario in only_scenarios:

        # -----------
        # Other plots
        # -----------
        figs_p2.main(
            os.path.join(scenario_path_all_stations_single_weather_yr, scenario),
            path_shapefile_input,
            path_out_plots,
            plot_crit_dict)

    # ####################################################################
    # Plot demand over time and peak over time (for modassar paper)
    # ####################################################################
    '''if plot_crit_dict['plot_weather_day_year']:

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
                path_out_plots, "weather_var_period.pdf"))'''

    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    paper_II_plots(*sys.argv[1:])
