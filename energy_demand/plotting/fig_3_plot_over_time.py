
"""
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import copy
import pylab

from energy_demand.plotting import basic_plot_functions
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_styles

colors = {

    # High elec
    'h_l': '#004529',
    'h_c': '#238443',
    'h_h': '#78c679',

    # Low elec
    'l_l': '#800026',
    'l_c': '#e31a1c',
    'l_h': '#fd8d3c',

    'other1': '#C044FF',
    'other2': '#3DF735',
    'other3': '#AD6D70',
    'other4': '#EC2504',
    'other5': '#8C0B90'}

marker_list = plotting_styles.marker_list()

marker_styles = {
    'h_h': marker_list[0],
    'h_l': marker_list[1],
    'l_l': marker_list[2],
    'l_h': marker_list[6],
}

def scenario_over_time(
        scenario_result_container,
        sim_yrs,
        fig_name,
        result_path,
        plot_points,
        crit_smooth_line=True
    ):
    """Plot peak over time
    """
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(10, 10)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    for cnt, i in enumerate(scenario_result_container):
        scenario_name = i['scenario_name']
        national_peak = i['national_peak']

        # dataframe with national peak (columns= simulation year, row: Realisation) 

        # Calculate quantiles
        quantile_95 = 0.95
        quantile_05 = 0.05

        try:
            color = colors[scenario_name]
            marker = marker_styles[scenario_name]
        except KeyError:
            color = list(colors.values())[cnt]

        print("SCENARIO NAME {}  {}".format(scenario_name, color))

        # Calculate average across all weather scenarios
        mean_national_peak = national_peak.mean(axis=0)
        mean_national_peak_sim_yrs = copy.copy(mean_national_peak)

        # Standard deviation over all realisations
        df_q_05 = national_peak.quantile(quantile_05)
        df_q_95 = national_peak.quantile(quantile_95)

        # --------------------
        # Try to smooth lines
        # --------------------
        sim_yrs_smoothed = sim_yrs
        if crit_smooth_line:
            try:
                sim_yrs_smoothed, mean_national_peak_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_peak, num=40000)
                _, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=40000)
                _, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=40000)

                mean_national_peak = pd.Series(mean_national_peak_smoothed, sim_yrs_smoothed)
                df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
                df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
            except:
                sim_yrs_smoothed = sim_yrs

        # -----------------------
        # Plot lines
        # ------------------------
        plt.plot(
            mean_national_peak,
            label="{} (mean)".format(scenario_name),
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
                s=15,
                clip_on=False) #do not clip points on axis


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

    plt.xlim(2015, 2050)
    
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
        #title="tt",
        ncol=2,
        prop={'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)

    basic_plot_functions.export_legend(
        legend,
        os.path.join(result_path, "legend_{}.pdf".format(fig_name)))
    legend.remove()

    # --------
    # Labeling
    # --------
    plt.ylabel("national peak demand in GW")
    #plt.xlabel("year")
    #plt.title("Title")

    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(result_path, fig_name))
    plt.close()

def fueltypes_over_time(
        scenario_result_container,
        sim_yrs,
        fig_name,
        fueltypes,
        result_path,
        plot_points=False,
        unit='TWh',
        crit_smooth_line=True
    ):
    """Plot fueltypes over time
    """
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(10, 10)) #width, height
    ax = fig.add_subplot(1, 1, 1)

    colors = {
        # Low elec
        'electricity':  '#001871',
        'gas':          '#ffb743',
        'hydrogen':     '#138d90',
    }

    line_styles_default = plotting_styles.linestyles()

    linestyles = {
        'h_h': line_styles_default[0],
        'h_l': line_styles_default[6],
        'l_l': line_styles_default[8],
        'l_h': line_styles_default[9],
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

            # Calculate quantiles
            quantile_95 = 0.95
            quantile_05 = 0.05

            try:
                color = colors[fueltype_str]
            except KeyError:
                #color = list(colors.values())[cnt_linestyle]
                raise Exception("Wrong color")

            try:
                linestyle = linestyles[scenario_name]
                marker = marker_styles[scenario_name]
            except KeyError:
                linestyle = list(linestyles.values())[cnt_scenario]

            # Calculate average across all weather scenarios
            mean_national_sum = national_sum.mean(axis=0)
            mean_national_sum_sim_yrs = copy.copy(mean_national_sum)

            if fueltype_str == 'hydrogen':
                print("..")
                print(mean_national_sum.values)
            # Standard deviation over all realisations
            df_q_05 = national_sum.quantile(quantile_05)
            df_q_95 = national_sum.quantile(quantile_95)

            # --------------------
            # Try to smooth lines
            # --------------------
            sim_yrs_smoothed = sim_yrs
            if crit_smooth_line:
                try:
                    sim_yrs_smoothed, mean_national_sum_smoothed = basic_plot_functions.smooth_data(sim_yrs, mean_national_sum, num=500)
                    _, df_q_05_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_05, num=500)
                    _, df_q_95_smoothed = basic_plot_functions.smooth_data(sim_yrs, df_q_95, num=500)

                    mean_national_sum = pd.Series(mean_national_sum_smoothed, sim_yrs_smoothed)
                    df_q_05 = pd.Series(df_q_05_smoothed, sim_yrs_smoothed)
                    df_q_95 = pd.Series(df_q_95_smoothed, sim_yrs_smoothed)
                except:
                    print("did not owrk {} {}".format(fueltype_str, scenario_name))
                    pass
            
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
        #title="tt",
        ncol=2,
        prop={'size': 6},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)
    
    basic_plot_functions.export_legend(
        legend,
        os.path.join(result_path, "legend_{}.pdf".format(fig_name)))
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
