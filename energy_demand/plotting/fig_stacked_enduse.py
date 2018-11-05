"""Plot stacked enduses for each submodel
"""
import logging
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.basic import conversions
from energy_demand.plotting import basic_plot_functions

def run(
        years_simulated,
        results_enduse_every_year,
        enduses,
        color_list,
        fig_name,
        plot_legend=True
    ):
    """Plots stacked energy demand

    Arguments
    ----------
    years_simulated : list
        Simulated years
    results_enduse_every_year : dict
        Results [year][enduse][fueltype_array_position]

    enduses :
    fig_name : str
        Figure name

    Note
    ----
        -   Sum across all fueltypes
        -   Not possible to plot single year

    https://matplotlib.org/examples/pylab_examples/stackplot_demo.html
    """
    print("...plot stacked enduses")
    nr_of_modelled_years = len(years_simulated)

    x_data = np.array(years_simulated)

    y_value_arrays = []
    legend_entries = []

    for enduse in enduses:
        legend_entries.append(enduse)

        y_values_enduse_yrs = np.zeros((nr_of_modelled_years))

        for year_array_nr, model_year in enumerate(results_enduse_every_year.keys()):

            # Sum across all fueltypes
            tot_across_fueltypes = np.sum(results_enduse_every_year[model_year][enduse])

            # Conversion: Convert GWh per years to GW
            yearly_sum_twh = conversions.gwh_to_twh(tot_across_fueltypes)

            logging.debug("... model_year {} enduse {}  twh {}".format(
                model_year, enduse, np.sum(yearly_sum_twh)))

            if yearly_sum_twh < 0:
                raise Exception("no minus values allowed {}  {}  {}".format(enduse, yearly_sum_twh, model_year))

            y_values_enduse_yrs[year_array_nr] = yearly_sum_twh

        # Add array with values for every year to list
        y_value_arrays.append(y_values_enduse_yrs)

    # Try smoothing line
    try:
        x_data_smoothed, y_value_arrays_smoothed = basic_plot_functions.smooth_data(
            x_data, y_value_arrays, num=40000)
    except:
        x_data_smoothed = x_data
        y_value_arrays_smoothed = y_value_arrays

    # Convert to stacked
    y_stacked = np.row_stack((y_value_arrays_smoothed))

    # Set figure size
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    # ----------
    # Stack plot
    # ----------
    color_stackplots = color_list[:len(enduses)]

    ax.stackplot(
        x_data_smoothed,
        y_stacked,
        alpha=0.8,
        colors=color_stackplots)

    if plot_legend:
        plt.legend(
            legend_entries,
            prop={
                'family':'arial',
                'size': 5},
            ncol=2,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.1),
            frameon=False,
            shadow=True)

    # -------
    # Axis
    # -------
    year_interval = 10
    major_ticks = np.arange(
        years_simulated[0],
        years_simulated[-1] + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    plt.ylim(ymax=500)
    #yticks = [100, 200, 300, 400, 500]
    #plt.yticks(yticks, yticks)
    # -------
    # Labels
    # -------
    plt.ylabel("TWh", fontsize=10)
    plt.xlabel("Year", fontsize=10)
    #plt.title("ED whole UK", fontsize=10)

    # Tight layout
    fig.tight_layout()

    plt.margins(x=0)
    plt.savefig(fig_name)
    plt.close()
