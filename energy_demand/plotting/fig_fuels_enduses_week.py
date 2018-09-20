"""
"""
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.plotting import basic_plot_functions

def run(
        results_resid,
        lookups,
        hours_to_plot,
        year_to_plot,
        fig_name
    ):
    """Plots stacked end_use for all regions. As
    input GWh per h are provided, which cancels out to
    GW.

    Arguments
    ---------
    year_to_plot : int
        2015 --> 0

    # INFO Cannot plot a single year?
    """
    print("... plot a full week")

    fig, ax = plt.subplots()

    days_to_plot = range(365)

    legend_entries = []

    numer_h = len(hours_to_plot)
    x_values = np.array(range(numer_h))

    y_init = np.zeros((lookups['fueltypes_nr'], numer_h))

    for fueltype_str, fueltype_int in lookups['fueltypes'].items():
        legend_entries.append(fueltype_str)

        # Select year to plot
        fuel_all_regions = results_resid[year_to_plot][fueltype_int]

        data_over_day = np.zeros((8760))
        for region_data in fuel_all_regions:
            data_over_day += region_data

        y_init[fueltype_int] = data_over_day[hours_to_plot] #Select hours

    for line, _ in enumerate(y_init):

        smooth_x_line_data, smooth_y_line_data = basic_plot_functions.smooth_line(
            x_values, y_init[line], nr_line_points=300)

        #plt.plot(y_init[line])
        plt.plot(smooth_x_line_data, smooth_y_line_data)

    ax.legend(legend_entries)

    x_tick_pos = []
    for day in range(365):
        x_tick_pos.append(day * 24)
    plt.xticks(x_tick_pos, days_to_plot, color='black')

    plt.axis('tight')

    plt.legend(
        ncol=2,
        frameon=False,
        prop={
            'family': 'arial',
            'size': 10},)

    plt.ylabel("GW")
    plt.xlabel("day")
    plt.title("tot annual ED, all enduses, fueltype {}".format(year_to_plot + 2050))

    plt.savefig(fig_name)
    plt.close()

