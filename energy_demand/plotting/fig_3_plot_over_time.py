
"""
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import pylab
import numpy as np

from energy_demand.plotting import fig_3_weather_map
from energy_demand.plotting import basic_plot_functions
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_styles
from energy_demand.read_write import write_data

colors = {
    # High elec
    'h_min': 'darkgreen', ##2c7bb6', ##004529',
    'h_c': '#238443',
    'h_max': '#d7191c', #'#78c679',

    # Low elec
    'l_min': 'steelblue', #abd9e9', ##800026',
    'l_c': '#e31a1c',
    'l_max': 'darkorchid', #fdae61', ##fd8d3c',

    'other1': '#C044FF',
    'other2': '#3DF735',
    'other3': '#AD6D70',
    'other4': '#EC2504',
    'other5': '#8C0B90'}

colors_quadrates = {
    0: '#f7f7f7', #Threshold change limit
    1: '#e66101', #'red',
    2: '#fdb863', #'tomato',
    3: '#5e3c99', #'seagreen',
    4: '#b2abd2'} #'orange'}

marker_list = plotting_styles.marker_list()

marker_styles = {
    'h_max': marker_list[0],
    'h_min': marker_list[1],
    'l_min': marker_list[2],
    'l_max': marker_list[6],
}

def clasify_color(diff_mean, diff_std, threshold):
    if diff_mean < -1 * threshold and diff_std < -1 * threshold:
        color_pos = 3
    elif diff_mean > threshold and diff_std < -1 * threshold:
        color_pos = 2
    elif diff_mean < -1 * threshold and diff_std > threshold:
        color_pos = 4
    elif diff_mean > threshold and diff_std > threshold:
        color_pos = 1
    else:
        color_pos = 0

    return color_pos 

def scenario_over_time(
        scenario_result_container,
        field_name,
        sim_yrs,
        fig_name,
        result_path,
        plot_points,
        crit_smooth_line=True,
        seperate_legend=False
    ):
    """Plot peak over time
    """
    statistics_to_print = []

    fig = plt.figure(figsize=basic_plot_functions.cm2inch(10, 10)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    for cnt_scenario, i in enumerate(scenario_result_container):
        scenario_name = i['scenario_name']
        national_peak = i[field_name]

        # dataframe with national peak (columns= simulation year, row: Realisation) 
        # Calculate quantiles
        #quantile_95 = 0.68 #0.95 #0.68
        #quantile_05 = 0.32 #0.05 #0.32

        try:
            color = colors[scenario_name]
            marker = marker_styles[scenario_name]
        except KeyError:
            color = list(colors.values())[cnt_scenario]

        try:
            marker = marker_styles[scenario_name]
        except KeyError:
            marker = list(marker_styles.values())[cnt_scenario]

        #print("SCENARIO NAME {}  {}".format(scenario_name, color))

        # Calculate average across all weather scenarios
        mean_national_peak = national_peak.mean(axis=0)

        mean_national_peak_sim_yrs = copy.copy(mean_national_peak)

        statistics_to_print.append("scenario: {} values over years: {}".format(scenario_name, mean_national_peak_sim_yrs))

        # Standard deviation over all realisations
        #df_q_05 = national_peak.quantile(quantile_05)
        #df_q_95 = national_peak.quantile(quantile_95)

        # Number of sigma
        nr_of_sigma = 1
        std_dev = national_peak.std(axis=0)
        two_std_line_pos = mean_national_peak + (nr_of_sigma * std_dev)
        two_std_line_neg = mean_national_peak - (nr_of_sigma * std_dev)

        # Maximum and minium values
        max_values = national_peak.max()
        min_values = national_peak.min()
        median_values = national_peak.median()

        statistics_to_print.append("scenario: {} two_sigma_pos: {}".format(scenario_name, two_std_line_pos))
        statistics_to_print.append("scenario: {} two_sigma_neg: {}".format(scenario_name, two_std_line_neg))
        statistics_to_print.append("--------min-------------- {}".format(scenario_name))
        statistics_to_print.append("{}".format(min_values)) #Get minimum value for every simulation year of all realizations
        statistics_to_print.append("--------max-------------- {}".format(scenario_name))
        statistics_to_print.append("{}".format(max_values))
        statistics_to_print.append("--------median_-------------- {}".format(scenario_name))
        statistics_to_print.append("{}".format(median_values))
        # --------------------
        # Try to smooth lines
        # --------------------
        sim_yrs_smoothed = sim_yrs
        if crit_smooth_line:
            try:
                sim_yrs_smoothed, mean_national_peak_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_peak, num=40000)
                #_, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=40000)
                #_, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=40000)
                _, two_std_line_pos_smoothed = basic_plot_functions.smooth_data(sim_yrs, two_std_line_pos, num=40000)
                _, two_std_line_neg_smoothed = basic_plot_functions.smooth_data(sim_yrs, two_std_line_neg, num=40000)
                _, max_values_smoothed = basic_plot_functions.smooth_data(sim_yrs, max_values, num=40000)
                _, min_values_smoothed = basic_plot_functions.smooth_data(sim_yrs, min_values, num=40000)
                mean_national_peak = pd.Series(mean_national_peak_smoothed, sim_yrs_smoothed)
                #df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
                #df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
                two_std_line_pos = pd.Series(two_std_line_pos_smoothed, sim_yrs_smoothed)
                two_std_line_neg = pd.Series(two_std_line_neg_smoothed, sim_yrs_smoothed)

                max_values = pd.Series(max_values_smoothed, sim_yrs_smoothed).values
                min_values = pd.Series(min_values_smoothed, sim_yrs_smoothed).values
            except:
                sim_yrs_smoothed = sim_yrs

        # -----------------------
        # Plot lines
        # ------------------------
        plt.plot(
            mean_national_peak,
            label="{} (mean)".format(scenario_name),
            zorder=1,
            color=color)

        # ------------------------
        # Plot markers
        # ------------------------
        if plot_points:
            plt.scatter(
                sim_yrs,
                mean_national_peak_sim_yrs,
                c=color,
                marker=marker,
                edgecolor='black',
                linewidth=0.5,
                zorder=2,
                s=15,
                clip_on=False) #do not clip points on axis

        # ------------------
        # Start with uncertainty one model step later (=> 2020)
        # ------------------
        start_yr_uncertainty = 2020

        if crit_smooth_line:
            #Get position in array of start year uncertainty
            pos_unc_yr = len(np.where(sim_yrs_smoothed < start_yr_uncertainty)[0])
        else:
            pos_unc_yr = 0
            for cnt, year in enumerate(sim_yrs_smoothed):
                if year == start_yr_uncertainty:
                    pos_unc_yr = cnt

        # select based on index which is year
        #df_q_05 = df_q_05.loc[start_yr_uncertainty:]
        #df_q_95 = df_q_95.loc[start_yr_uncertainty:]
        two_std_line_pos = two_std_line_pos.loc[start_yr_uncertainty:]
        two_std_line_neg = two_std_line_neg.loc[start_yr_uncertainty:]
        sim_yrs_smoothed = sim_yrs_smoothed[pos_unc_yr:]

        min_values = min_values[pos_unc_yr:] #min_values.loc[start_yr_uncertainty:]
        max_values = max_values[pos_unc_yr:] #max_values.loc[start_yr_uncertainty:]

        # --------------------------------------
        # Plottin qunatilse and average scenario
        # --------------------------------------
        #df_q_05.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_')
        #df_q_95.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_')

        # Plot standard deviation
        #two_std_line_pos.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_')
        #two_std_line_neg.plot.line(color=color, linestyle='--', linewidth=0.1, label='_nolegend_')

        # plot min and maximum values
        plt.plot(sim_yrs_smoothed, min_values, color=color, linestyle='--', linewidth=0.3, label='_nolegend_')
        plt.plot(sim_yrs_smoothed, max_values, color=color, linestyle='--', linewidth=0.3, label='_nolegend_')

        plt.fill_between(
            sim_yrs_smoothed,
            list(two_std_line_pos),
            list(two_std_line_neg),
            alpha=0.25,
            facecolor=color)

    plt.xlim(2015, 2050)
    plt.ylim(0)

    # --------
    # Different style
    # --------
    ax = plt.gca()
    ax.grid(which='major', color='black', axis='y', linestyle='--')

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
        labeltop=False,
        labelleft=True,
        labelright=False) # labels along the bottom edge are off

    # --------
    # Legend
    # --------
    legend = plt.legend(
        ncol=2,
        prop={'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)

    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(fig_name[:-4])))
        legend.remove()

    # --------
    # Labeling
    # --------
    plt.ylabel("national peak demand (GW)")
    plt.tight_layout()
    plt.savefig(os.path.join(result_path, fig_name))
    plt.close()

    # Write info to txt
    write_data.write_list_to_txt(
        os.path.join(result_path, fig_name).replace(".pdf", ".txt"),
        statistics_to_print)

def plot_std_dev_vs_contribution(
        scenario_result_container,
        sim_yrs,
        fig_name,
        fueltypes,
        result_path,
        plot_points=False,
        path_shapefile_input=False,
        unit='TWh',
        crit_smooth_line=True,
        seperate_legend=False):
    
    colors = {
        2020: 'dimgrey',
        2050: 'forestgreen'
    }

    #plot_numbers = {
    #    'h_max': {'row': 0, 'col': 0},
    #    'h_min': {'row': 0, 'col': 1},
    #    'l_max': {'row': 1, 'col': 0},
    #    'l_min': {'row': 1, 'col': 1}}
    plot_numbers = {
        'h_max': 1,
        'h_min': 2,
        'l_max': 3,
        'l_min': 4}

    sizes = {
        2020: 2,
        2050: 5}

    scenarios = ['l_max', 'l_min', 'h_max', 'h_min']

    threshold = 5 # percent

    # -----------
    # Plot 4x4 chart with relative differences
    # ------------
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(20, 20)) #width, height
    for scenario in scenarios:
        plot_nr = plot_numbers[scenario]
        plt.subplot(2, 2, plot_nr)

        mean_2020 = scenario_result_container[2020][scenario]['regional_share_national_peak'].mean(axis=0)
        mean_2050 = scenario_result_container[2050][scenario]['regional_share_national_peak'].mean(axis=0)
        
        std_2020 = scenario_result_container[2020][scenario]['regional_share_national_peak'].std(axis=0)
        std_2050 = scenario_result_container[2050][scenario]['regional_share_national_peak'].std(axis=0)
        
        diff_2020_2050_reg_share = ((100 / mean_2020) * mean_2050) - 100
        diff_2020_2050_reg_share_std = ((100 / std_2020) * std_2050) - 100
        
        if scenario not in ['h_min', 'l_min']:
            plt.ylabel("Δ standard deviation [%]", fontsize=10)
        if scenario not in ['h_max', 'h_min']:
            plt.xlabel("Δ mean of total peak [%]", fontsize=10)

        regions = diff_2020_2050_reg_share.index
        for region in regions.values:
            diff_mean = diff_2020_2050_reg_share.loc[region]
            diff_std = diff_2020_2050_reg_share_std.loc[region]

            color_pos = clasify_color(diff_mean, diff_std, threshold=threshold)

            color = colors_quadrates[color_pos]
            plt.scatter(
                diff_mean,
                diff_std,
                #alpha=0.6,
                color=color,
                edgecolor=color,
                linewidth=0.5,
                s=3)

        plt.xlim(-30, 60)
        plt.ylim(-50, 300)
        plt.title("{}".format(scenario), size=10)
        plt.axhline(y=0, linewidth=0.7, color='grey', linestyle='--')   # horizontal line
        plt.axvline(x=0, linewidth=0.7, color='grey', linestyle='--')    # vertical line

        # -----------------
        # Plot spatial map
        # -----------------
        regions = diff_2020_2050_reg_share.index
        relclassified_values = pd.DataFrame()
        relclassified_values['reclassified'] = 0
        relclassified_values['name'] = regions
        relclassified_values = relclassified_values.set_index(('name'))
        relclassified_values['name'] = regions

        for region in regions.values:
            diff_mean = diff_2020_2050_reg_share.loc[region]
            diff_std = diff_2020_2050_reg_share_std.loc[region]
            relclassified_values.loc[region, 'reclassified'] = clasify_color(diff_mean, diff_std, threshold=threshold)

        fig_3_weather_map.plot_4_cross_map(
            cmap_rgb_colors=colors_quadrates,
            reclassified=relclassified_values,
            result_path=os.path.join(result_path, "spatial_final_{}.pdf".format(scenario)),
            threshold=threshold,
            path_shapefile_input=path_shapefile_input,
            seperate_legend=True)

    plt.savefig(os.path.join(result_path, "cross_chart_relative.pdf"))

    # -----------
    # Plot 4x4 chart with absolute
    # ------------
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(20, 20)) #width, height
    for year, scenario_results in scenario_result_container.items():
        for scenario_name, scenario_results in scenario_results.items():

            plot_nr = plot_numbers[scenario_name]
            plt.subplot(2, 2, plot_nr)

            if year in [2020, 2050]:
                #regions = list(regional_share_national_peak.columns)
                #nr_of_regions = regional_share_national_peak.shape[1]
                #nr_of_realisations = regional_share_national_peak.shape[0]

                # Mean over all realisations
                mean = scenario_results['regional_share_national_peak'].mean(axis=0) / 100

                # Standard deviation over all realisations
                std_dev = scenario_results['regional_share_national_peak'].std(axis=0) / 100

                # Convert standard deviation given as % of peak into GW (multiply national peak per region share across the columns)
                abs_gw = pd.DataFrame()
                national_peak_per_run = scenario_results['peak_hour_demand'].sum(axis=1).to_frame()

                for reg_column in scenario_results['regional_share_national_peak'].columns.values:

                    #reg share * national peak
                    column_national_peak = national_peak_per_run.columns[0]
                    abs_gw[reg_column] = (scenario_results['regional_share_national_peak'][reg_column] / 100) * national_peak_per_run[column_national_peak]

                # Absolute values
                std_dev_gw = abs_gw.std(axis=0)
                mean_gw = abs_gw.mean(axis=0)
                plt.ylim(0, np.max(std_dev_gw))
                plt.ylim(0, 0.06)
                plt.xlim(0, 1.5)

                if scenario_name not in ['h_min', 'l_min']:
                    plt.ylabel("standard deviation [GW]", fontsize=10)
                if scenario_name not in ['h_max', 'h_min']:
                    plt.xlabel("mean of total peak [GW]", fontsize=10)

                plt.title(scenario_name, size=10)
                plt.scatter(
                    list(mean_gw), #list(mean),
                    list(std_dev_gw), #list(std_dev),
                    color=colors[year],
                    s=sizes[year]) #,
                    #label="{} {}".format(year, scenario_name))

    plt.savefig(os.path.join(result_path, "cross_chart_absolute.pdf"))

def fueltypes_over_time(
        scenario_result_container,
        sim_yrs,
        fig_name,
        fueltypes,
        result_path,
        plot_points=False,
        unit='TWh',
        crit_smooth_line=True,
        seperate_legend=False
    ):
    """Plot fueltypes over time
    """
    statistics_to_print = []

    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(10, 10)) #width, height
    ax = fig.add_subplot(1, 1, 1)

    colors = {
        # Low elec
        'electricity':  '#3e3838',
        'gas':          '#ae7c7c',
        'hydrogen':     '#6cbbb3',
    }

    line_styles_default = plotting_styles.linestyles()

    linestyles = {
        'h_max': line_styles_default[0],
        'h_min': line_styles_default[6],
        'l_min': line_styles_default[8],
        'l_max': line_styles_default[9],
    }

    for cnt_scenario, i in enumerate(scenario_result_container):
        scenario_name = i['scenario_name']

        for cnt_linestyle, fueltype_str in enumerate(fueltypes):
            national_sum = i['national_{}'.format(fueltype_str)]

            if unit == 'TWh':
                unit_factor = conversions.gwh_to_twh(1)
            elif unit == 'GWh':
                unit_factor = 1
            else:
                raise Exception("Wrong unit")

            national_sum = national_sum * unit_factor

            try:
                color = colors[fueltype_str]
            except KeyError:
                raise Exception("Wrong color")

            try:
                linestyle = linestyles[scenario_name]
            except KeyError:
                linestyle = list(linestyles.values())[cnt_scenario]
            try:
                marker = marker_styles[scenario_name]
            except KeyError:
                marker = list(marker_styles.values())[cnt_scenario]

            # Calculate average across all weather scenarios
            mean_national_sum = national_sum.mean(axis=0)
            mean_national_sum_sim_yrs = copy.copy(mean_national_sum)

            statistics_to_print.append("{} fueltype_str: {} mean_national_sum_sim_yrs: {}".format(scenario_name, fueltype_str, mean_national_sum_sim_yrs))

            # Standard deviation over all realisations
            std = np.std(national_sum)

            nr_of_sigma = 1
            pos_sigma = mean_national_sum + (nr_of_sigma * std)
            neg_sigma = mean_national_sum - (nr_of_sigma * std)

            statistics_to_print.append("{} fueltype_str: {} pos_sigma: {}".format(scenario_name, fueltype_str, pos_sigma))
            statistics_to_print.append("{} fueltype_str: {} neg_sigma: {}".format(scenario_name, fueltype_str, neg_sigma))

            # --------------------
            # Try to smooth lines
            # --------------------
            sim_yrs_smoothed = sim_yrs
            if crit_smooth_line:
                try:
                    sim_yrs_smoothed, mean_national_sum_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_sum, num=500)
                    _, pos_sigma_smoothed = basic_plot_functions.smooth_data(sim_yrs, pos_sigma, num=500)
                    _, neg_sigma_smoothed = basic_plot_functions.smooth_data(sim_yrs, neg_sigma, num=500)
                    mean_national_sum = pd.Series(mean_national_sum_smoothed, sim_yrs_smoothed)                 
                    
                    pos_sigma = pd.Series(pos_sigma_smoothed, sim_yrs_smoothed).values
                    neg_sigma = pd.Series(neg_sigma_smoothed, sim_yrs_smoothed).values
                except:
                    pos_sigma = pos_sigma.values
                    neg_sigma = neg_sigma.values
            
            # ------------------------
            # Plot lines
            # ------------------------
            plt.plot(
                mean_national_sum,
                label="{} {}".format(fueltype_str, scenario_name),
                linestyle=linestyle,
                color=color,
                zorder=1,
                clip_on=True)

            # ------------------------
            # Plot markers
            # ------------------------
            if plot_points:
                plt.scatter(
                    sim_yrs,
                    mean_national_sum_sim_yrs,
                    marker=marker,
                    edgecolor='black',
                    linewidth=0.5,
                    c=color,
                    zorder=2,
                    s=15,
                    clip_on=False) #do not clip points on axis

            # ------------------
            # Start with uncertainty one model step later (=> 2020)
            # ------------------
            start_yr_uncertainty = 2020

            if crit_smooth_line:
                #Get position in array of start year uncertainty
                pos_unc_yr = len(np.where(sim_yrs_smoothed < start_yr_uncertainty)[0])
            else:
                pos_unc_yr = 0
                for cnt, year in enumerate(sim_yrs_smoothed):
                    if year == start_yr_uncertainty:
                        pos_unc_yr = cnt

            # Shorten lines
            #pos_sigma = pos_sigma.loc[start_yr_uncertainty:]
            #neg_sigma = neg_sigma.loc[start_yr_uncertainty:]
            pos_sigma = pos_sigma[pos_unc_yr:]
            neg_sigma = neg_sigma[pos_unc_yr:]

            sim_yrs_smoothed = sim_yrs_smoothed[pos_unc_yr:]

            plt.plot(sim_yrs_smoothed, pos_sigma, color=color, linestyle='--', linewidth=0.1, label='_nolegend_')
            plt.plot(sim_yrs_smoothed, neg_sigma, color=color, linestyle='--', linewidth=0.1, label='_nolegend_')

            # Plotting qunatilse and average scenario
            plt.fill_between(
                sim_yrs_smoothed,
                list(pos_sigma),  #y1
                list(neg_sigma),  #y2
                alpha=0.25,
                facecolor=color)

    plt.xlim(2015, 2050)
    plt.ylim(0)

    ax = plt.gca()

    # Major ticks every 20, minor ticks every 5
    major_ticks = [200, 400, 600] #np.arange(0, 600, 200)
    minor_ticks = [100, 200, 300, 400, 500, 600] #np.arange(0, 600, 100)

    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)

    # And a corresponding grid
    ax.grid(
        which='both',
        color='black',
        linewidth=0.5,
        axis='y',
        linestyle=line_styles_default[3]) #[6])

    # Or if you want different settings for the grids:
    ax.grid(which='minor', axis='y', alpha=0.4)
    ax.grid(which='major', axis='y', alpha=0.8)

    # Achsen
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Ticks
    plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
        labeltop=False,
        labelleft=True,
        labelright=False) # labels along the bottom edge are off

    # --------
    # Legend
    # --------
    legend = plt.legend(
        ncol=2,
        prop={'size': 6},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)

    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(fig_name[:-4])))
        legend.remove()

    # --------
    # Labeling
    # --------
    plt.ylabel("national fuel over time [in {}]".format(unit))
    #plt.xlabel("year")
    #plt.title("Title")

    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(result_path, fig_name))
    plt.close()

    write_data.write_list_to_txt(
        os.path.join(result_path, fig_name).replace(".pdf", ".txt"),
        statistics_to_print)
