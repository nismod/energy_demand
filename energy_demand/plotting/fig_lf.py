"""
"""
import logging
import matplotlib.pyplot as plt
import numpy as np

from energy_demand.plotting import basic_plot_functions

def order_polygon(upper_boundary, lower_boundary):
    """Create correct sorting to draw filled polygon

    Arguments
    ---------
    upper_boundary
    lower_boundary

    Returns
    -------
    """
    min_max_polygon = []
    for pnt in upper_boundary:
        min_max_polygon.append(pnt)
    for pnt in reversed(lower_boundary):
        min_max_polygon.append(pnt)

    return min_max_polygon

def create_min_max_polygon_from_lines(line_data):
    """

    Arguments
    ---------
    line_data : dict
        linedata containing info
            {'x_value': [y_values]}

    """
    upper_boundary = []
    lower_bdoundary = []

    for x_value, y_value in line_data.items():
        min_y = np.min(y_value)
        max_y = np.max(y_value)
        upper_boundary.append((x_value, min_y))
        lower_bdoundary.append((x_value, max_y))

        # create correct sorting to draw filled polygon
        min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)

    return min_max_polygon

def plot_lf_y(
        fueltype_int,
        fueltype_str,
        reg_load_factor_y,
        reg_nrs,
        path_plot_fig,
        plot_individ_lines=False,
        plot_max_min_polygon=True
    ):
    """Plot load factors per region for every year

    Arguments
    --------

    """
    print("... plotting load factors")

    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    if plot_individ_lines:
        # Line plot for every region over years
        for reg_nr in range(reg_nrs):
            x_values_year = []
            y_values_year = []

            for year, lf_fueltype_reg in reg_load_factor_y.items():
                x_values_year.append(year)
                y_values_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

            plt.plot(
                x_values_year,
                y_values_year,
                linewidth=0.2,
                color='grey')

    if plot_max_min_polygon:
        '''lower_bdoundary = []
        upper_boundary = []

        for year_nr, lf_fueltype_reg in reg_load_factor_y.items():

            # Get min and max of all entries of year of all regions
            min_y = np.min(lf_fueltype_reg[fueltype_int])
            max_y = np.max(lf_fueltype_reg[fueltype_int])
            upper_boundary.append((year_nr, min_y))
            lower_bdoundary.append((year_nr, max_y))

        # create correct sorting to draw filled polygon
        min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)'''

        min_max_polygon = create_min_max_polygon_from_lines(reg_load_factor_y)

        polygon = plt.Polygon(
            min_max_polygon,
            color='grey',
            alpha=0.2,
            edgecolor=None,
            linewidth=0,
            fill='True')

        ax.add_patch(polygon)
    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor, fueltpye {} [%]".format(fueltype_str))

    years = list(reg_load_factor_y.keys())
    base_yr = 2015

    # Major ticks
    major_interval = 10
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)

    # Minor ticks
    minor_interval = 5
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(path_plot_fig)
    plt.close()

def plot_seasonal_lf(
        fueltype_int,
        fueltype_str,
        load_factors_seasonal,
        reg_nrs,
        path_plot_fig,
        plot_individ_lines=False,
        plot_max_min_polygon=True
    ):
    """Plot load factors per region for every year

    Arguments
    --------
    fueltype_int : int
        Fueltype_int to print (see lookup)
    fueltype_str : str
        Fueltype string to print
    load_factors_seasonal : dict
        Seasonal load factors per season
    reg_nrs : int
        Number of region
    """
    print("... plotting seasonal load factors")

    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(8, 8))
    ax = fig.add_subplot(1, 1, 1)

    # Settings
    color_list = {
        'winter': 'midnightblue',
        'summer': 'olive',
        'spring': 'darkgreen',
        'autumn': 'gold'}

    classes = list(color_list.keys())
    #class_colours = list(color_list.values())

    # ------------
    # Iterate regions and plot load factors for every region
    # ------------
    if plot_individ_lines:
        for reg_nr in range(reg_nrs):
            for season, lf_fueltypes_season in load_factors_seasonal.items():

                x_values_season_year = []
                y_values_season_year = []
                for year, lf_fueltype_reg in lf_fueltypes_season.items():
                    x_values_season_year.append(year)
                    y_values_season_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

                # plot individual saisonal data point
                plt.plot(
                    x_values_season_year,
                    y_values_season_year,
                    color=color_list[season],
                    linewidth=0.2,
                    alpha=0.2)

    # -----------------
    # Plot min_max_area
    # -----------------
    if plot_max_min_polygon:

        for season, lf_fueltypes_season in load_factors_seasonal.items():
            upper_boundary = []
            lower_bdoundary = []

            min_max_polygon = create_min_max_polygon_from_lines(lf_fueltypes_season)

            '''for year_nr, lf_fueltype_reg in lf_fueltypes_season.items():

                # Get min and max of all entries of year of all regions
                min_y = np.min(lf_fueltype_reg[fueltype_int])
                max_y = np.max(lf_fueltype_reg[fueltype_int])
                upper_boundary.append((year_nr, min_y))
                lower_bdoundary.append((year_nr, max_y))

            # create correct sorting to draw filled polygon
            min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)'''

            polygon = plt.Polygon(
                min_max_polygon,
                color=color_list[season],
                alpha=0.2,
                edgecolor=None,
                linewidth=0,
                fill='True')

            ax.add_patch(polygon)

    # ------------------------------------
    # Calculate average per season for all regions
    # and plot average line a bit thicker
    # ------------------------------------
    for season in classes:
        years = []
        average_season_year_years = []
        for year in load_factors_seasonal[season].keys():
            average_season_year = []

            # Iterate over regions
            for reg_nr in range(reg_nrs):
                average_season_year.append(
                    load_factors_seasonal[season][year][fueltype_int][reg_nr])

            years.append(int(year))
            average_season_year_years.append(np.average(average_season_year))

        # plot average
        plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            linewidth=0.5,
            linestyle='--',
            alpha=1.0,
            markersize=0.5,
            marker='o',
            label=season)

        # Plot markers for average line
        '''plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            markersize=0.5,
            linewidth=0.5,
            marker='o')'''

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling and ticks
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor {} [%]".format(fueltype_str))

    base_yr = 2015
    minor_interval = 5
    major_interval = 10

    # Major ticks
    major_ticks = np.arange(base_yr,years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)
    #ax.set_xlabel(major_ticks)

    # Minor ticks
    minor_ticks = np.arange(base_yr,years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)
    #ax.set_xlabel(minor_ticks)

    # ------------
    # Plot color legend with colors for every season
    # ------------
    plt.legend(
        ncol=2,
        prop={
            'family': 'arial',
            'size': 5},
        loc='best',
        frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_plot_fig)
    plt.close()