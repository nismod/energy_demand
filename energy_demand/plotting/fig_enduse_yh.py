"""
"""
import os
import matplotlib.pyplot as plt
from energy_demand.plotting import basic_plot_functions

def run(
        name_fig,
        path_result,
        ed_yh,
        days_to_plot=365,
        plot_crit=False
    ):
    """Plot individual enduse
    """
    nr_of_h_to_plot = len(days_to_plot) * 24

    x_data = range(nr_of_h_to_plot)

    y_calculated = []

    for day in days_to_plot:
        for hour in range(24):
            y_calculated.append(ed_yh[day][hour])

    # ----------
    # Plot figure
    # ----------
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(16, 8))

    plt.plot(
        x_data,
        y_calculated,
        label='model',
        linestyle='--',
        linewidth=0.5,
        fillstyle='full',
        color='blue')

    plt.xlim([0, 8760])
    plt.margins(x=0)
    plt.axis('tight')

    # ----------
    # Labelling
    # ----------
    plt.xlabel("hour", fontsize=10)
    plt.ylabel("uk elec use [GW]", fontsize=10)

    plt.legend(frameon=False)

    plt.savefig(os.path.join(path_result, name_fig))

    if plot_crit:
        plt.show()
        plt.close()
    else:
        plt.close()
