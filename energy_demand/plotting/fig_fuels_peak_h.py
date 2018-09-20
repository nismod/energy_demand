"""
"""
import numpy as np
import matplotlib.pyplot as plt

from energy_demand import enduse_func
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(results_every_year, lookups, path_plot_fig):
    """Plots

    Plot peak hour per fueltype over time for

    Arguments
    ---------
    tot_fuel_dh_peak : dict
        year, fueltype, peak_dh

    """
    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(14, 8))
    ax = fig.add_subplot(1, 1, 1)

    nr_y_to_plot = len(results_every_year)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((lookups['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype in lookups['fueltypes'].items():
        fueltype_int = tech_related.get_fueltype_int(fueltype_str)

        # Legend
        legend_entries.append(fueltype_str)

        # Read out fueltype specific load
        data_over_years = []
        for model_year_object in results_every_year.values():

            # Sum fuel across all regions
            fuel_all_regs = np.sum(model_year_object, axis=1) # (fueltypes, 8760 hours)

            # Get peak day across all enduses for every region
            _, gw_peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(fuel_all_regs[fueltype_int])

            # Add peak hour
            data_over_years.append(gw_peak_fueltyp_h)

        y_init[fueltype] = data_over_years

    # ----------
    # Plot lines
    # ----------
    #linestyles = plotting_styles.linestyles()

    years = list(results_every_year.keys())
    for fueltype, _ in enumerate(y_init):
        plt.plot(
            years,
            y_init[fueltype],
            linewidth=0.7)

    ax.legend(
        legend_entries,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # -
    # Axis
    # -
    base_yr = 2015
    major_interval = 10
    minor_interval = 5

    # Major ticks
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)

    # Minor ticks
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    plt.xlim(2015, years[-1])

    # --------
    # Labeling
    # --------
    plt.ylabel("GW")
    plt.xlabel("year")
    plt.title("ED peak hour, y, all enduses and regions")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    fig.savefig(path_plot_fig)
    plt.close()
