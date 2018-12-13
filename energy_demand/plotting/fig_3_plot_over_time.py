
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
        scenario_result_container,
        sim_yrs,
        fig_name,
        result_path
    ):

    colors = {

        # High elec
        'h_l': '#004529',
        'h_c': '#238443',
        'h_h': '#78c679',

        # Low elec
        'l_l': '#800026',
        'l_c': '#e31a1c',
        'l_h': '#fd8d3c',

        'other1': '#C0E4FF',
        'other2': '#3DF735',
        'other3': '#AD6D70',
        'other4': '#EC2504',
        'other5': '#8C0B90',
    }

    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8)) #width, height
    ax = fig.add_subplot(1, 1, 1)

    for cnt, i in enumerate(scenario_result_container):
        scenario_name = i['scenario_name']
        national_peak = i['national_electricity']

        # dataframe with national peak (columns= simulation year, row: Realisation) 

        # Calculate quantiles
        quantile_95 = 0.95
        quantile_05 = 0.05

        try:
            color = colors[scenario_name]
        except KeyError:
            color = list(colors.values())[cnt]

        print("SCENARIO NAME {}  {}".format(scenario_name, color))

        # Calculate average across all weather scenarios
        mean_national_peak = national_peak.mean(axis=0)

        # Standard deviation over all realisations
        df_q_05 = national_peak.quantile(quantile_05)
        df_q_95 = national_peak.quantile(quantile_95)

        # --------------------
        # Try to smooth lines
        # --------------------
        sim_yrs_smoothed = sim_yrs
        try:
            sim_yrs_smoothed, mean_national_peak_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_peak, num=40000)
            _, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=40000)
            _, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=40000)

            mean_national_peak = pd.Series(mean_national_peak_smoothed, sim_yrs_smoothed)
            #sim_yrs = pd.Series(sim_yrs_smoothed, sim_yrs_smoothed)
            #sim_yrs = list(sim_yrs_smoothed)
            df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
            df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
        except:
            sim_yrs_smoothed = sim_yrs
            pass

        plt.plot(
            mean_national_peak,
            label="{} (mean)".format(scenario_name),
            color=color)

        # Plottin qunatilse and average scenario
        df_q_05.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_') #, label="0.05")
        df_q_95.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_') #, label="0.05")

        plt.fill_between(
            sim_yrs_smoothed,
            list(df_q_95),  #y1
            list(df_q_05),  #y2
            alpha=0.25,
            facecolor=color,
            #label="weather uncertainty"
            )

    #plt.ylim(0, y_lim_val)
    plt.xlim(2015, 2050)
    
    # --------
    # Different style
    # --------
    ax = plt.gca()
    ax.grid(which='major', color='black', axis='y', linestyle='--')
    
    ax.spines['right'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    #'''
    plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    #'''
    #plt.yticks([], [])

    # --------
    # Legend
    # --------
    '''legend = plt.legend(
        #title="tt",
        ncol=2,
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)'''

    # Put a legend to the right of the current axis
    ax.legend(
        ncol=1,
        prop={'size': 8},
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False)
    #legend.get_title().set_fontsize(8)

    # --------
    # Labeling
    # --------
    plt.ylabel("national peak demand in GW")
    #plt.xlabel("year")
    #plt.title("Title")

    plt.tight_layout()
    plt.show()
    plt.savefig(os.path.join(result_path, fig_name))


def fueltypes_over_time(
        scenario_result_container,
        sim_yrs,
        fig_name,
        fueltype_str,
        result_path
    ):

    colors = {

        # High elec
        'h_l': '#004529',
        'h_c': '#238443',
        'h_h': '#78c679',

        # Low elec
        'l_l': '#800026',
        'l_c': '#e31a1c',
        'l_h': '#fd8d3c',

        'other1': '#C0E4FF',
        'other2': '#3DF735',
        'other3': '#AD6D70',
        'other4': '#EC2504',
        'other5': '#8C0B90',
    }

    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8)) #width, height
    ax = fig.add_subplot(1, 1, 1)

    for cnt, i in enumerate(scenario_result_container):
        scenario_name = i['scenario_name']
        national_sum = i['national_{}'.format(fueltype_str)]
        # dataframe with national peak (columns= simulation year, row: Realisation) 

        # Calculate quantiles
        quantile_95 = 0.95
        quantile_05 = 0.05

        try:
            color = colors[scenario_name]
        except KeyError:
            color = list(colors.values())[cnt]

        print("SCENARIO NAME {}  {}".format(scenario_name, color))

        # Calculate average across all weather scenarios
        mean_national_sum = national_sum.mean(axis=0)

        # Standard deviation over all realisations
        df_q_05 = national_sum.quantile(quantile_05)
        df_q_95 = national_sum.quantile(quantile_95)
        print("dd")
        print(df_q_05)
        # --------------------
        # Try to smooth lines
        # --------------------
        sim_yrs_smoothed = sim_yrs
        try:
            sim_yrs_smoothed, mean_national_sum_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_sum, num=40000)
            _, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=40000)
            _, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=40000)

            mean_national_sum = pd.Series(mean_national_sum_smoothed, sim_yrs_smoothed)
            #sim_yrs = pd.Series(sim_yrs_smoothed, sim_yrs_smoothed)
            #sim_yrs = list(sim_yrs_smoothed)
            df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
            df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
        except:
            sim_yrs_smoothed = sim_yrs
            pass

        plt.plot(
            mean_national_sum,
            label="{} (mean)".format(scenario_name),
            color=color)

        # Plottin qunatilse and average scenario
        df_q_05.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_') #, label="0.05")
        df_q_95.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_') #, label="0.05")

        plt.fill_between(
            sim_yrs_smoothed,
            list(df_q_95),  #y1
            list(df_q_05),  #y2
            alpha=0.25,
            facecolor=color,
            #label="weather uncertainty"
            )

    #plt.ylim(0, y_lim_val)
    plt.xlim(2015, 2050)
    
    # --------
    # Different style
    # --------
    ax = plt.gca()
    ax.grid(which='major', color='black', axis='y', linestyle='--')
    
    ax.spines['right'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    #'''
    plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    #'''
    #plt.yticks([], [])

    # --------
    # Legend
    # --------
    '''legend = plt.legend(
        #title="tt",
        ncol=2,
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)'''

    # Put a legend to the right of the current axis
    ax.legend(
        ncol=1,
        prop={'size': 8},
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False)
    #legend.get_title().set_fontsize(8)

    # --------
    # Labeling
    # --------
    plt.ylabel("national peak demand in GW")
    #plt.xlabel("year")
    #plt.title("Title")

    plt.tight_layout()
    plt.show()
    plt.savefig(os.path.join(result_path, fig_name))
