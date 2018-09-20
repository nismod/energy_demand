"""
"""
import logging
import numpy as np
from collections import defaultdict
import operator
import matplotlib.pyplot as plt

from energy_demand import enduse_func
from energy_demand.plotting import basic_plot_functions

def lad_comparison_peak(
        base_yr,
        comparison_year,
        regions,
        ed_year_fueltype_regs_yh,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points=False,
        plotshow=False
    ):
    """Compare energy demand for regions for the base yeard and
    a future year

    Arguments
    ----------
    comparison_year : int
        Year to compare base year values to

    Note
    -----
    SOURCE OF LADS:
        - Data for northern ireland is not included in that, however in BEIS dataset!
    """
    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand
    # -------------------------------------------
    for year, fuels in ed_year_fueltype_regs_yh.items():
        if year == base_yr:
            for region_array_nr, reg_geocode in enumerate(regions):
                _, gw_peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(fuels[fueltype_int][region_array_nr])
                result_dict['demand_by'][reg_geocode] = gw_peak_fueltyp_h

        elif year == comparison_year:
            for region_array_nr, reg_geocode in enumerate(regions):
                _, gw_peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(fuels[fueltype_int][region_array_nr])
                result_dict['demand_cy'][reg_geocode] = gw_peak_fueltyp_h
        else:
            pass

    # -----------------
    # Sort results according to size
    # -----------------
    sorted_dict_real = sorted(
        result_dict['demand_by'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_dict_real), 1)

    y_real_elec_demand = []
    y_modelled_elec_demand = []

    labels = []
    for sorted_region in sorted_dict_real:
        geocode_lad = sorted_region[0]

        y_real_elec_demand.append(
            result_dict['demand_by'][geocode_lad])
        y_modelled_elec_demand.append(
            result_dict['demand_cy'][geocode_lad])

        logging.debug(
            "validation for LAD region: %s %s diff: %s",
            result_dict['demand_by'][geocode_lad],
            result_dict['demand_cy'][geocode_lad],
            result_dict['demand_cy'][geocode_lad] - result_dict['demand_by'][geocode_lad])

        labels.append(geocode_lad)

    # --------
    # Axis
    # --------
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    # ----------------------------------------------
    # Plot
    # ----------------------------------------------
    plt.plot(
        x_values,
        y_real_elec_demand,
        linestyle='None',
        marker='o',
        markersize=1.6, #1.6
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.2,
        color='black',
        label='base year: {}'.format(base_yr))

    plt.plot(
        x_values,
        y_modelled_elec_demand,
        marker='o',
        linestyle='None',
        markersize=1.6,
        markerfacecolor='white',
        fillstyle='none',
        markeredgewidth=0.5,
        markeredgecolor='blue',
        color='black',
        label='current year: {}'.format(comparison_year))

    # Limit
    plt.ylim(ymin=0, ymax=1.2)
    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_modelled_elec_demand[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=3)

    plt.xlabel("UK regions (excluding northern ireland)")
    plt.ylabel("peak h {} [GWh]".format(fueltype_str))

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
        plt.close()
    else:
        plt.close()

def plot_lad_comparison(
        base_yr,
        comparison_year,
        regions,
        ed_year_fueltype_regs_yh,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points=False,
        plotshow=False
    ):
    """Compare energy demand for regions for the base yeard and
    a future year

    Arguments
    ----------
    comparison_year : int
        Year to compare base year values to

    Note
    -----
    SOURCE OF LADS:
        - Data for northern ireland is not included in that, however in BEIS dataset!
    """
    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand
    # -------------------------------------------
    for year, fuels in ed_year_fueltype_regs_yh.items():

        if year == base_yr:
            for region_array_nr, reg_geocode in enumerate(regions):
                gw_per_region_modelled = np.sum(fuels[fueltype_int][region_array_nr])
                result_dict['demand_by'][reg_geocode] = gw_per_region_modelled
        elif year == comparison_year:
            for region_array_nr, reg_geocode in enumerate(regions):
                gw_per_region_modelled = np.sum(fuels[fueltype_int][region_array_nr])
                result_dict['demand_cy'][reg_geocode] = gw_per_region_modelled
        else:
            pass

    logging.info("Comparison: modelled: %s real: %s".format(
        sum(result_dict['demand_by'].values()),
        sum(result_dict['demand_cy'].values())))

    # -----------------
    # Sort results according to size
    # -----------------
    sorted_dict_real = sorted(
        result_dict['demand_by'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(9, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_dict_real), 1)

    y_real_elec_demand = []
    y_modelled_elec_demand = []

    labels = []
    for sorted_region in sorted_dict_real:
        geocode_lad = sorted_region[0]

        y_real_elec_demand.append(
            result_dict['demand_by'][geocode_lad])
        y_modelled_elec_demand.append(
            result_dict['demand_cy'][geocode_lad])

        logging.debug(
            "validation for LAD region: %s %s diff: %s",
            result_dict['demand_by'][geocode_lad],
            result_dict['demand_cy'][geocode_lad],
            result_dict['demand_cy'][geocode_lad] - result_dict['demand_by'][geocode_lad])

        labels.append(geocode_lad)

    # --------
    # Axis
    # --------
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off

    # ----------------------------------------------
    # Plot
    # ----------------------------------------------
    plt.plot(
        x_values,
        y_real_elec_demand,
        linestyle='None',
        marker='o',
        markersize=1.6, #1.6
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.2,
        color='black',
        label='base year: {}'.format(base_yr))

    plt.plot(
        x_values,
        y_modelled_elec_demand,
        marker='o',
        linestyle='None',
        markersize=1.6,
        markerfacecolor='white',
        fillstyle='none',
        markeredgewidth=0.5,
        markeredgecolor='blue',
        color='black',
        label='current year: {}'.format(comparison_year))

    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_modelled_elec_demand[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=3)

    plt.xlabel("UK regions (excluding northern ireland)")
    plt.ylabel("{} [GWh]".format(fueltype_str))

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
        plt.close()
    else:
        plt.close()