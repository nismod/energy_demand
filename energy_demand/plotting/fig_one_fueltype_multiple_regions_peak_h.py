"""
"""
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.plotting import basic_plot_functions
from energy_demand import enduse_func
#from energy_demand.plotting import plotting_styles

def plt_regions_peak_h(
        results_every_year,
        lookups,
        regions,
        path_plot_fig,
        fueltype_str_to_plot
    ):
    """Plot
    Arguments
    ---------
    """
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(14, 8))

    ax = fig.add_subplot(1, 1, 1)

    nr_y_to_plot = len(results_every_year)

    legend_entries = []

    for fueltype_str, fueltype in lookups['fueltypes'].items():

        if fueltype_str != fueltype_str_to_plot:
            pass
        else:
            # Legend
            # Read out fueltype specific load
            data_over_years = {}
            for reg_nr, reg_geocode in enumerate(regions):
                data_over_years[reg_nr] = []

            for model_year_object in results_every_year.values():

                for reg_nr, reg_geocode in enumerate(regions):

                    # Get peak hour value
                    _, peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(model_year_object[fueltype][reg_nr])

                    # Add peak hour
                    data_over_years[reg_nr].append(peak_fueltyp_h)
    
            y_init = data_over_years

    # ----------
    # Plot lines
    # ----------
    #linestyles = plotting_styles.linestyles()
    years = list(results_every_year.keys())

    for reg in y_init:
        plt.plot(
            years,
            y_init[reg],
            #linestyle=linestyles[fueltype],
            color='lightblue',
            linewidth=0.2,)

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
    plt.title("ED peak hour, y, all enduses, single regs")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    fig.savefig(path_plot_fig)
    plt.close()

