
"""
"""

import os
import logging
import copy
import math
import numpy as np
import geopandas as gpd
import pandas as pd
import palettable
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import fig_p2_weather_val, result_mapping
from energy_demand.basic import basic_functions
from energy_demand.technologies import tech_related
from energy_demand.read_write import write_data
from energy_demand.basic import conversions

def scenario_over_time(
        ed_reg_tot_y,
        sim_yrs,
        fig_name,
        result_path
    ):

    # dataframe with national peak (columns= simulation year, row: Realisation) 

    # Calculate quantiles
    quantile_95 = 0.95
    quantile_05 = 0.05

    color_list = [
        'red', 'green', 'orange', '#37AB65',
        '#C0E4FF', '#3DF735', '#AD6D70', '#EC2504',
        '#8C0B90', '#27B502', '#7C60A8', '#CF95D7', '#F6CC1D']



    # Calculate average across all weather scenarios
    mean_ed_reg_tot_y = ed_reg_tot_y.mean(axis=0)

    # Standard deviation over all realisations
    df_q_05 = ed_reg_tot_y.quantile(quantile_05)
    df_q_95 = ed_reg_tot_y.quantile(quantile_95)

    # --------------------
    # Try to smooth lines
    # --------------------
    try:
        sim_yrs_smoothed, mean_ed_reg_tot_y_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_ed_reg_tot_y, num=40000)
        _, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=40000)
        _, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=40000)

        mean_ed_reg_tot_y = pd.Series(mean_ed_reg_tot_y_smoothed, sim_yrs_smoothed)
        sim_yrs = pd.Series(sim_yrs_smoothed, sim_yrs_smoothed)
        #sim_yrs = list(sim_yrs_smoothed)
        df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
        df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
    except:
        pass


    fig = plt.figure(figsize=basic_plot_functions.cm2inch(9, 8)) #width, height
    ax = fig.add_subplot(1, 1, 1)

    #print(mean_ed_reg_tot_y.columns)
    plt.plot(mean_ed_reg_tot_y)

    # Plottin qunatilse and average scenario
    df_q_05.plot.line(color="r", linestyle='--', linewidth=0.5, label="0.05")
    df_q_95.plot.line(color="r", linestyle='--', linewidth=0.5, label="0.05")
    plt.fill_between(
        sim_yrs,
        list(df_q_95),  #y1
        list(df_q_05),  #y2
        alpha=0.15,
        facecolor="r",
        label="uncertainty band")

    #plt.ylim(0, y_lim_val)
    plt.xlim(2015, 2050)

    # --------
    # Labeling
    # --------
    plt.ylabel("peak")
    plt.xlabel("year")
    plt.title("tttt")

    plt.tight_layout()
    plt.show()





    '''



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
    '''