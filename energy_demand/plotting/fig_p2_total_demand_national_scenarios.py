import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import result_mapping
from energy_demand.plotting import fig_p2_weather_val

def total_demand_national_scenarios(
        scenario_result_paths,
        sim_yrs,
        fueltype_str,
        path_out_plots
    ):
    dict_scenarios_weather_yrs = {}

    columns = [
        'weather_yr',
        'national_peak_demand']

    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # ----------------
    # Read all data inform of scenario, simulationyr, weather_yrs
    # ----------------
    for scenario_path in scenario_result_paths:
        scenario_name = os.path.split(scenario_path)[-1]
        dict_scenarios_weather_yrs[scenario_name] = {}

        weather_yrs = []
        # Get all folders with weather_yr run results (name of folder is scenario)
        weather_yr_scenarios_paths = os.listdir(scenario_path)

        for simulation_run in weather_yr_scenarios_paths:   
            if simulation_run != '_results_PDF_figs':

                weather_yr_scenarios_paths = os.listdir(os.path.join(scenario_path, simulation_run))     

                for weather_yr_scenario_path in weather_yr_scenarios_paths:
                    try:
                        split_path_name = weather_yr_scenario_path.split("__")
                        weather_yr = int(split_path_name[0])
                        path_to_weather_yr = os.path.join(scenario_path, simulation_run, "{}__{}".format(weather_yr, 'all_stations'))
                        weather_yrs.append((weather_yr, path_to_weather_yr))
                    except:
                        pass

        for simulation_yr in sim_yrs:
            dict_scenarios_weather_yrs[scenario_name][simulation_yr] = pd.DataFrame(columns=columns)
            for weather_yr, path_to_weather_yr in weather_yrs:
            
                seasons = date_prop.get_season(year_to_model=2015)
                model_yeardays_daytype, _, _ = date_prop.get_yeardays_daytype(year_to_model=2015)

                results_container = read_data.read_in_results(
                    os.path.join(path_to_weather_yr, 'model_run_results_txt'),
                    seasons,
                    model_yeardays_daytype)

                # ---------------------------------------------------
                # Calculate hour with national peak demand
                # This may be different depending on the weather yr
                # ---------------------------------------------------
                ele_regions_8760 = results_container['ed_fueltype_regs_yh'][simulation_yr][fueltype_int]
                sum_all_regs_fueltype_8760 = np.sum(ele_regions_8760, axis=0) # Sum for every hour

                max_day = int(basic_functions.round_down((np.argmax(sum_all_regs_fueltype_8760) / 24), 1))
                max_h = np.argmax(sum_all_regs_fueltype_8760)
                max_demand = np.max(sum_all_regs_fueltype_8760)

                # Calculate the national peak demand in GW
                national_peak_GW = np.max(sum_all_regs_fueltype_8760)

                # -----------------------
                # Add to final container
                # -----------------------
                line_entry = [[
                    weather_yr,
                    national_peak_GW
                    ]]

                line_df = pd.DataFrame(line_entry, columns=columns)
                existing_df = dict_scenarios_weather_yrs[scenario_name][simulation_yr] 
                appended_df = existing_df.append(line_df)

                dict_scenarios_weather_yrs[scenario_name][simulation_yr] = appended_df


    # ------------------------------------------------------------------------------------------
    # Create plot
    # ------------------------------------------------------------------------------------------
    print("....create plot")

    weather_yr_to_plot = 1979 #TODO

    color_list = ['red', 'green', 'orange', '#37AB65', '#C0E4FF', '#3DF735', '#AD6D70', '#EC2504', '#8C0B90', '#27B502', '#7C60A8', '#CF95D7', '#F6CC1D']
    
    # Calculate quantiles
    quantile_95 = 0.95
    quantile_05 = 0.05

    # Create dataframe with rows as scenario and lines as simulation yrs
    scenarios = list(dict_scenarios_weather_yrs.keys())

    # Containers
    df_total_demand_2015 = pd.DataFrame(columns=scenarios)
    df_q_95_scenarios = pd.DataFrame(columns=scenarios)
    df_q_05_scenarios = pd.DataFrame(columns=scenarios)

    for simulation_yr in sim_yrs:

        line_entries_95 = []
        line_entries_05 = []
        line_entries_tot_h = []

        for scenario_name in scenarios:
            print("-- {}  {}".format(scenario_name, simulation_yr))
            # Calculate entires over year
            df_weather_yrs = dict_scenarios_weather_yrs[scenario_name][simulation_yr]

            df_q_95 = df_weather_yrs['national_peak_demand'].quantile(quantile_95)
            df_q_05 = df_weather_yrs['national_peak_demand'].quantile(quantile_05)

            peak_weather_yr_2015 = df_weather_yrs[df_weather_yrs['weather_yr']==weather_yr_to_plot]['national_peak_demand'].values[0]
            
            line_entries_95.append(df_q_95)
            line_entries_05.append(df_q_05)
            line_entries_tot_h.append(peak_weather_yr_2015)

        # Try to smooth lines
        try:
            sim_yrs_smoothed, line_entries_tot_h_smoothed = basic_plot_functions.smooth_data(sim_yrs, line_entries_tot_h, num=40000)
        except:
            sim_yrs_smoothed = sim_yrs
            line_entries_tot_h_smoothed = line_entries_tot_h


        df_q_95_scenarios = df_q_95_scenarios.append(pd.DataFrame([line_entries_95], columns=scenarios))
        df_q_05_scenarios = df_q_05_scenarios.append(pd.DataFrame([line_entries_05], columns=scenarios))
        df_total_demand_2015 = df_total_demand_2015.append(pd.DataFrame([line_entries_tot_h_smoothed], columns=scenarios))


    # ----
    # Set simulation year as index
    # ----
    df_total_demand_2015 = df_total_demand_2015.set_index([sim_yrs_smoothed])
    df_q_95_scenarios = df_q_95_scenarios.set_index([sim_yrs])
    df_q_05_scenarios = df_q_05_scenarios.set_index([sim_yrs])


    # plot lines
    for cnt, scenario in enumerate(scenarios):

        # Print total demand for specific year
        df_total_demand_2015[scenario].plot.line(color=color_list[cnt], style='-', label=": {}".format(scenario))

        # print quantiles
        #df_q_95_scenarios[scenario].plot.line(color=color_list[cnt], linestyle='--', linewidth=0.5, label="0.05")
        #df_q_05_scenarios[scenario].plot.line(color=color_list[cnt], linestyle='--', linewidth=0.5, label="0.05")
        
        # -----------------
        # Uncertainty range
        # -----------------
        plt.fill_between(
            sim_yrs, #x
            df_q_95_scenarios[scenario],  #y1
            df_q_05_scenarios[scenario],  #y2
            alpha=0.15,
            facecolor=color_list[cnt])#,
            #label=": {}".format(scenario))

    # ------------
    # Legend
    # ------------
    plt.legend(
        ncol=1,
        bbox_to_anchor=(0.5, 0., 0.5, 0.5), #bbox_to_anchor=(0.2, -0.1),
        prop={'size': 8},
        frameon=False)

    plt.ylabel("GW")
    plt.xlabel("year")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.show()
    prnt(".")
    # Calculate std per simulation year
    '''
    std_total_demand = list(np.std(weather_yrs_total_demand, axis=0)) # across columns calculate std
            std_peak_demand = list(np.std(weather_yrs_peak_demand, axis=0)) # across columns calculate std



            # convert to list
            df_total_demand_q_95 = df_total_demand_q_95.tolist()
            df_total_demand_q_05 = df_total_demand_q_05.tolist()
            df_peak_q_95 = df_peak_q_95.tolist()


    # -------------------
    # Base year data (2015)
    # -------------------
    # total demand
    tot_demand_twh_2015 = []
    for sim_yr, data_sim_yr in data_input[2015].items():
        gwh_2015_y = np.sum(data_sim_yr[fueltype_int])
        twh_2015_y = conversions.gwh_to_twh(gwh_2015_y)
        tot_demand_twh_2015.append(twh_2015_y)

    # peak
    df_peak_2015 = []
    for sim_yr, data_sim_yr in data_input[2015].items():
        peak_gwh_2015_y = np.max(data_sim_yr[fueltype_int])
        df_peak_2015.append(peak_gwh_2015_y)

    # ---------------
    # Smoothing lines
    # ---------------
    if len(nr_weather_yrs) > 2:
        try:
            sim_yrs_smoothed, tot_demand_twh_2015_smoothed = basic_plot_functions.smooth_data(columns, tot_demand_twh_2015, num=40000)
            period_h_smoothed, df_total_demand_q_95_smoothed = basic_plot_functions.smooth_data(list(columns), df_total_demand_q_95, num=40000)
            period_h_smoothed, df_total_demand_q_05_smoothed = basic_plot_functions.smooth_data(columns, df_total_demand_q_05, num=40000)
            period_h_smoothed, df_peak_q_95_smoothed = basic_plot_functions.smooth_data(list(columns), df_peak_q_95, num=40000)
            period_h_smoothed, df_peak_q_05_smoothed = basic_plot_functions.smooth_data(columns, df_peak_q_05, num=40000)
            period_h_smoothed, df_peak_2015_smoothed = basic_plot_functions.smooth_data(columns, df_peak_2015, num=40000)
        except:
            period_h_smoothed = columns
            df_total_demand_q_95_smoothed = df_total_demand_q_95
            df_total_demand_q_05_smoothed = df_total_demand_q_05
            df_peak_q_95_smoothed = df_peak_q_95
            df_peak_q_05_smoothed = df_peak_q_05
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015
            df_peak_2015_smoothed = df_peak_2015
    else:
        try:
            period_h_smoothed, tot_demand_twh_2015_smoothed = basic_plot_functions.smooth_data(columns, tot_demand_twh_2015, num=40000)
            period_h_smoothed, df_peak_2015_smoothed = basic_plot_functions.smooth_data(columns, df_peak_2015, num=40000)
        except:
            period_h_smoothed = columns
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015
            df_peak_2015_smoothed = df_peak_2015
     
    # --------------
    # Two axis figure
    # --------------
    fig, ax1 = plt.subplots(
        figsize=basic_plot_functions.cm2inch(15, 10))

    ax2 = ax1.twinx()

    # Axis label
    ax1.set_xlabel('Years')
    ax2.set_ylabel('Peak hour {} demand (GW)'.format(fueltype_str), color='black')
    ax1.set_ylabel('Total {} demand (TWh)'.format(fueltype_str), color='black')

    # Make the y-axis label, ticks and tick labels match the line color.¨
    color_axis1 = 'lightgrey'
    color_axis2 = 'blue'

    ax1.tick_params('y', colors='black')
    ax2.tick_params('y', colors='black')

    if len(nr_weather_yrs) > 2:

    '''



    pass
