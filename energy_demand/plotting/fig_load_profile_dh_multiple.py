"""
"""
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

from energy_demand.plotting import plotting_styles
from energy_demand.basic import basic_functions
from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import fig_lf

def run(
        path_fig_folder,
        path_plot_fig,
        calc_av_lp_modelled,
        calc_av_lp_real,
        calc_lp_modelled=None,
        calc_lp_real=None,
        plot_peak=False,
        plot_radar=False,
        plot_all_entries=False,
        plot_max_min_polygon=True,
        plotshow=False,
        max_y_to_plot=60,
        fueltype_str=False,
        year=False
    ):
    """Plotting average saisonal loads for each daytype. As an input
    GWh is provided, which for each h is cancelled out to GW.

    https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
    http://matthiaseisen.com/matplotlib/shapes/reg-polygon/
    """
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(14, 25))
    
    ax = fig.add_subplot(
        nrows=4,
        ncols=2)

    plot_nr = 0
    row = -1
    for season in calc_av_lp_modelled:
        row += 1
        col = -1
        for daytype in calc_av_lp_modelled[season]:
            col += 1
            plot_nr += 1

            axes = plt.subplot(4, 2, plot_nr)

            # ------------------
            # Plot average
            # ------------------
            x_values = range(24)

            plt.plot(
                x_values,
                list(calc_av_lp_real[season][daytype]),
                color='black',
                label='av_real or av by',
                linestyle='--',
                linewidth=0.5)

            plt.plot(
                x_values,
                list(calc_av_lp_modelled[season][daytype]),
                color='blue',
                label='av_modelled or av cy',
                linestyle='--',
                linewidth=0.5)

            # --------------
            # Radar plots
            # --------------
            if plot_radar:
                name_spider_plot = os.path.join(
                    path_fig_folder,
                    "spider_{}_{}_{}_{}_.pdf".format(
                        year,
                        fueltype_str,
                        season,
                        daytype))

                plot_radar_plot(
                    list(calc_av_lp_modelled[season][daytype]),
                    name_spider_plot,
                    plot_steps=20,
                    plotshow=False)

            # ------------------
            # Plot every single line
            # ------------------
            if plot_all_entries:
                for entry in range(len(calc_lp_real[season][daytype])):
                    plt.plot(
                        x_values,
                        list(calc_lp_real[season][daytype][entry]),
                        color='grey',
                        markersize=0.5,
                        alpha=0.2)

                    plt.plot(
                        x_values,
                        list(calc_lp_modelled[season][daytype][entry]),
                        color='blue',
                        markersize=0.5,
                        alpha=0.2)

            # ----------
            # Plot max_min range polygons
            # ----------
            if plot_max_min_polygon:

                # ----Draw real
                min_max_polygon = []
                upper_boundary = []
                lower_bdoundary = []

                # Get min and max of all entries for hour
                for hour in range(24):
                    min_y = np.min(calc_lp_real[season][daytype][:, hour], axis=0)
                    max_y = np.max(calc_lp_real[season][daytype][:, hour], axis=0)
                    upper_boundary.append((hour, min_y))
                    lower_bdoundary.append((hour, max_y))

                # create correct sorting to draw filled polygon
                min_max_polygon = fig_lf.order_polygon(upper_boundary, lower_bdoundary)
                #min_max_polygon = create_min_max_polygon_from_lines(reg_load_factor_y)

                polygon = plt.Polygon(
                    min_max_polygon,
                    color='grey',
                    alpha=0.2,
                    edgecolor=None,
                    linewidth=0,
                    fill='True')

                axes.add_patch(polygon)

                # -----Draw modelled
                min_max_polygon = []
                upper_boundary = []
                lower_bdoundary = []

                # Get min and max of all entries for hour
                for hour in range(24):
                    min_y = np.min(calc_lp_modelled[season][daytype][:, hour], axis=0)
                    max_y = np.max(calc_lp_modelled[season][daytype][:, hour], axis=0)
                    upper_boundary.append((hour, min_y))
                    lower_bdoundary.append((hour, max_y))

                # create correct sorting to draw filled polygon
                min_max_polygon = fig_lf.order_polygon(upper_boundary, lower_bdoundary)

                polygon = plt.Polygon(
                    min_max_polygon,
                    color='blue',
                    alpha=0.2,
                    edgecolor=None,
                    linewidth=0,
                    fill='True')

                axes.add_patch(polygon)

            # --------------------
            # Get load shape within season with highest houly load
            # --------------------
            if plot_peak:

                # Get row with maximum hourly value
                day_with_max_h = np.argmax(np.max(calc_lp_real[season][daytype], axis=1))

                plt.plot(
                    x_values,
                    list(calc_lp_real[season][daytype][day_with_max_h]),
                    color='grey',
                    markersize=1.0,
                    label='real_peak or by peak',
                    linestyle='-.',
                    linewidth=0.5)

                # Get row with maximum hourly value
                day_with_max_h = np.argmax(np.max(calc_lp_modelled[season][daytype], axis=1))

                plt.plot(
                    x_values,
                    list(calc_lp_modelled[season][daytype][day_with_max_h]),
                    color='blue',
                    markersize=1.0,
                    label='modelled_peak or cy peak',
                    linestyle='-.',
                    linewidth=0.5)

            # -----------------
            # Axis
            # -----------------
            plt.ylim(0, max_y_to_plot)
            plt.xlim(0, 23)

            # Tight layout
            plt.tight_layout()
            plt.margins(x=0)

            # Calculate RMSE
            rmse = basic_functions.rmse(
                calc_av_lp_modelled[season][daytype],
                calc_av_lp_real[season][daytype])

            # Calculate R_squared
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                calc_av_lp_modelled[season][daytype],
                calc_av_lp_real[season][daytype])

            # Calculate standard deviation
            std_dev_p = np.std(calc_av_lp_real[season][daytype] - calc_av_lp_modelled[season][daytype])
            std_dev_abs = np.std(abs(calc_av_lp_real[season][daytype] - calc_av_lp_modelled[season][daytype]))

            # -----------
            # Labelling
            # -----------
            font_additional_info = plotting_styles.font_info()

            title_info = ('{}, {}'.format(season, daytype))
            plt.text(1, 0.55, "RMSE: {}, R_squared: {}, std: {} (+- {})".format(
                round(rmse, 2),
                round(r_value, 2),
                round(std_dev_p, 2),
                round(std_dev_abs, 2),
                fontdict=font_additional_info))
            plt.title(title_info, loc='left', fontdict=font_additional_info)
            #plt.ylabel("hours")
            #plt.ylabel("average electricity [GW]")

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=1,
        loc=2,
        prop={
            'family': 'arial',
            'size': 5},
        frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    fig.savefig(path_plot_fig)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_radar_plot(
        dh_profile,
        fig_name,
        plot_steps=30,
        plotshow=False
    ):
    """Plot daily load profile on a radar plot

    Arguments
    ---------
    dh_profile : list
        Dh values to plot
    fig_name : str
        Path to save figure

    SOURCE: https://python-graph-gallery.com/390-basic-radar-chart/
    """

    # Get maximum demand
    max_entry = np.array(dh_profile).max()
    max_demand = round(max_entry, -1) + 10 # Round to nearest 10 plus add 10
    max_demand = 120 #SCRAP

    nr_of_plot_steps = int(max_demand / plot_steps) + 1

    axis_plots_inner = []
    axis_plots_innter_position = []

    # Innter ciruclar axis
    for i in range(nr_of_plot_steps):
        axis_plots_inner.append(plot_steps*i)
        axis_plots_innter_position.append(str(plot_steps*i))


    data = {'dh_profile': ['testname']}

    for hour in range(24):

        # Key: Label outer circle
        data[hour] = dh_profile[hour]

    # Set data
    df = pd.DataFrame(data)

    # number of variable
    categories=list(df)[1:]
    N = len(categories)

    # We are going to plot the first line of the data frame.
    # But we need to repeat the first value to close the circular graph:
    values=df.loc[0].drop('dh_profile').values.flatten().tolist()
    values += values[:1]

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    # Change circula axis
    ax.yaxis.grid(color='lightgrey', linestyle='--', linewidth=0.8, alpha=0.8) # Circular axis
    ax.xaxis.grid(color='lightgrey', linestyle='--', linewidth=0.8, alpha=0.8) # Regular axis

    # Change to clockwise cirection
    ax.set_theta_direction(-1)
    #ax.set_theta_offset(pi/2.0)

    # Set first hour on top
    ax.set_theta_zero_location("N")

    # Draw one axe per variable + add labels labels yet
    plt.xticks(
        angles[:-1],
        categories,
        color='grey',
        size=8)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(
        axis_plots_inner,
        axis_plots_innter_position,
        color="grey",
        size=7)

    # Set limit to size
    plt.ylim(0, max_demand)

    # Smooth lines
    angles_smoothed, values_smoothed = basic_plot_functions.smooth_data(
        angles, values, spider=True)

    # Plot data
    ax.plot(
        angles_smoothed,
        values_smoothed,
        linestyle='--',
        linewidth=0.5)

    ax.fill(
        angles,
        values,
        'blue', #b
        alpha=0.1)

    # Save fig
    print("fig_name: " + str(fig_name))
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()
