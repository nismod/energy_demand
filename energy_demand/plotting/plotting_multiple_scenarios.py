"""
This file containes functions to plot multiple scenarios in a folder
"""
import operator
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.plotting import plotting_styles
from energy_demand.plotting import plotting_program

def plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot=2050,
        plotshow=True
    ):
    """Plot chart comparing total annual demand for all LADs
    """

    # Get first scenario in dict
    all_scenarios = list(scenario_data.keys())
    first_scenario = str(all_scenarios[:1][0])

    # ----------------
    # Sort regions according to size
    # -----------------
    regions = {}
    for fueltype, fuel_regs in enumerate(scenario_data[first_scenario]['results_every_year'][2015]):
        for region_array_nr, fuel_regs in enumerate(fuel_regs):
            try:
                regions[region_array_nr] += np.sum(fuel_regs[region_array_nr])
            except KeyError:
                regions[region_array_nr] = np.sum(fuel_regs[region_array_nr])

    sorted_regions = sorted(
        regions.items(),
        key=operator.itemgetter(1))

    sorted_regions_nrs = []
    for sort_info in sorted_regions:
        sorted_regions_nrs.append(sort_info[0])

    # Labels
    labels = []
    for sorted_region in sorted_regions_nrs:
        geocode_lad = sorted_region # If actual LAD name, change this
        labels.append(geocode_lad)

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=plotting_program.cm2inch(9, 8)) #width, height (9, 8)

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_regions_nrs), 1)

    # ----------------------------------------------
    # Plot base year values
    # ----------------------------------------------
    # Order data (actually not necessar for base year)
    base_year_data = []
    for reg_array_nr in sorted_regions_nrs:

        tot_fuel_across_fueltypes = 0
        for fueltype, fuel_fueltype in enumerate(scenario_data[first_scenario]['results_every_year'][2015]):
            tot_fuel_across_fueltypes += np.sum(fuel_fueltype[reg_array_nr])

        base_year_data.append(tot_fuel_across_fueltypes)

    plt.plot(
        x_values,
        base_year_data,
        linestyle='None',
        marker='o',
        markersize=1.6,
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.2,
        color='black',
        label='actual')

    # ----------------------------------------------
    # Plot all future scenario values
    # ----------------------------------------------
    color_list = plotting_styles.color_list()

    for scenario_nr, (scenario, fuel_data) in enumerate(scenario_data.items()):

        sorted_year_data = []
        for reg_array_nr in sorted_regions_nrs:

            tot_fuel_across_fueltypes = 0
            for fueltype, fuel_fueltype in enumerate(fuel_data['results_every_year'][year_to_plot]):
                tot_fuel_across_fueltypes += np.sum(fuel_fueltype[reg_array_nr])

            sorted_year_data.append(tot_fuel_across_fueltypes)

        plt.plot(
            x_values,
            sorted_year_data,
            linestyle='None',
            marker='o',
            markersize=1.6,
            fillstyle='full',
            markerfacecolor=color_list[scenario_nr],
            markeredgewidth=0.2,
            color='black',
            label='actual')

    # --------
    # Axis
    # --------
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    label_points = False
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_modelled_elec_demand[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=3)

    font_additional_info = {
        'family': 'arial',
        'color': 'black',
        'weight': 'normal',
        'size': 8}
    title_info = "TEST"
    plt.title(
        title_info,
        loc='left',
        fontdict=font_additional_info)

    plt.xlabel("UK regions (excluding northern ireland)")
    plt.ylabel("{} [GWh]")

    # --------
    # Legend
    # --------
    plt.legend(
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    else:
        plt.close()
