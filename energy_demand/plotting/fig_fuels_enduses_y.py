"""
"""
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import plotting_styles
from energy_demand.basic import conversions

def run(results, lookups, fig_name, plotshow=False):
    """Plot lines with total energy demand for all enduses
    per fueltype over the simluation period. Annual GWh
    are converted into GW.

    Arguments
    ---------
    results : dict
        Results for every year and fueltype (yh)
    lookups : dict
        Lookup fueltypes
    fig_name : str
        Figure name

    Note
    ----
    Values are divided by 1'000
    """
    print("... plot fuel per fueltype for whole country over annual timesteps")

    # Set figure size
    plt.figure(figsize=basic_plot_functions.cm2inch(14, 8))

    # Initialise (number of enduses, number of hours to plot)
    y_values_fueltype = {}

    for fueltype_str, fueltype_int in lookups['fueltypes'].items():

        # Read out fueltype specific max h load
        data_years = {}
        for year, data_year in results.items():
            tot_gwh_fueltype_y = np.sum(data_year[fueltype_int])

            #Conversion: Convert gwh per years to gw
            yearly_sum_gw = tot_gwh_fueltype_y

            yearly_sum_twh = conversions.gwh_to_twh(yearly_sum_gw)

            data_years[year] = yearly_sum_twh #yearly_sum_gw

        y_values_fueltype[fueltype_str] = data_years

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2015, 5
    end_yr = list(results.keys())

    major_ticks = np.arange(
        base_yr,
        end_yr[-1] + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list_selection = plotting_styles.color_list_selection()

    for fueltype_str, fuel_fueltype_yrs in y_values_fueltype.items():

        smooth_x_line_data, smooth_y_line_data = basic_plot_functions.smooth_line(
            np.array(list(fuel_fueltype_yrs.keys())),
            np.array(list(fuel_fueltype_yrs.values())))

        plt.plot(
            smooth_x_line_data,     # years
            smooth_y_line_data,   # yearly data per fueltype
            color=str(color_list_selection.pop()),
            label=fueltype_str)

    # ----
    # Axis
    # ----
    plt.ylim(ymin=0) #no upper limit to xmax

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=2,
        loc=2,
        prop={
            'family': 'arial',
            'size': 10},
        frameon=False)

    # ---------
    # Labels
    # ---------
    plt.ylabel("TWh")
    plt.xlabel("year")
    plt.title("tot annual ED per fueltype")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()
    