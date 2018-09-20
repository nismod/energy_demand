
"""Plot stacked enduses per sector
"""
import logging
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.basic import conversions
from energy_demand.plotting import basic_plot_functions
##import matplotlib.colors as colors #for color_name in colors.cnmaes:

def run(
        lookups,
        years_simulated,
        results_enduse_every_year,
        rs_enduses,
        ss_enduses,
        is_enduses,
        fig_name
    ):
    """Plots summarised endues for the three sectors. Annual
    GWh are converted into GW.

    Arguments
    ----------
    data : dict
        Data container
    results_objects :

    enduses_data :

    Note
    ----
        -   Sum across all fueltypes

    # INFO Cannot plot a single year?
    """
    logging.info("plot annual demand for enduses for all submodels")

    submodels = ['residential', 'service', 'industry']
    nr_submodels = len(submodels)

    x_data = years_simulated
    y_data = np.zeros((nr_submodels, len(years_simulated)))

    # Set figure size
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    for model_year, data_model_run in enumerate(results_enduse_every_year.values()):

        submodel = 0
        for fueltype_int in range(lookups['fueltypes_nr']):
            for enduse in rs_enduses:

                # Conversion: Convert gwh per years to gw
                yearly_sum_gw = np.sum(data_model_run[enduse][fueltype_int])
                yearly_sum_twh = conversions.gwh_to_twh(yearly_sum_gw)
                y_data[submodel][model_year] += yearly_sum_twh #yearly_sum_gw

        submodel = 1
        for fueltype_int in range(lookups['fueltypes_nr']):
            for enduse in ss_enduses:

                # Conversion: Convert gwh per years to gw
                yearly_sum_gw = np.sum(data_model_run[enduse][fueltype_int])
                yearly_sum_twh = conversions.gwh_to_twh(yearly_sum_gw)
                y_data[submodel][model_year] += yearly_sum_twh #yearly_sum_gw

        submodel = 2
        for fueltype_int in range(lookups['fueltypes_nr']):
            for enduse in is_enduses:

                # Conversion: Convert gwh per years to gw
                yearly_sum_gw = np.sum(data_model_run[enduse][fueltype_int])
                yearly_sum_twh = conversions.gwh_to_twh(yearly_sum_gw)
                y_data[submodel][model_year] += yearly_sum_twh #yearly_sum_gw

    # Convert to stack
    y_stacked = np.row_stack((y_data))

    color_stackplots = ['darkturquoise', 'orange', 'firebrick']

    # ----------
    # Stack plot
    # ----------
    ax.stackplot(
        x_data,
        y_stacked,
        colors=color_stackplots)

    # ------------
    # Plot color legend with colors for every SUBMODEL
    # ------------
    plt.legend(
        submodels,
        ncol=1,
        prop={
            'family': 'arial',
            'size': 5},
        loc='best',
        frameon=False)

    # -------
    # Axis
    # -------
    plt.xticks(years_simulated, years_simulated)
    plt.axis('tight')

    # -------
    # Labels
    # -------
    plt.ylabel("TWh")
    plt.xlabel("year")
    plt.title("UK ED per sector")

    # Tight layout
    plt.margins(x=0)
    fig.tight_layout()

    # Save fig
    plt.savefig(fig_name)
    plt.close()
