"""
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from energy_demand.scripts_technologies import technologies_related

# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def plot_x_days(all_hours_year, region, days):
    """With input 2 dim array plot daily load"""

    x_values = range(days * 24)
    y_values = []
    #y_values = all_hours_year[region].values()

    for day, daily_values in enumerate(all_hours_year[region].values()):

        # ONLY PLOT HALF A YEAR
        if day < days:
            for hour in daily_values:
                y_values.append(hour)

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Energy demand in kWh")
    plt.title("Energy Demand")
    plt.legend()
    plt.show()


def plot_load_shape_yd(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 0] * 100) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Percentage of daily demand")
    plt.title("Load curve of a day")
    plt.legend()
    plt.show()


def plot_load_shape_yd_non_resid(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 1]) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("ABSOLUTE VALUES TEST NONRESID")
    plt.legend()
    plt.show()

def plot_stacked_Country_end_use(results_resid, enduses_data, attribute_to_get): # nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """
    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years

    x = range(nr_y_to_plot)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((len(enduses_data), nr_y_to_plot))

    for k, enduse in enumerate(enduses_data):
        legend_entries.append(enduse)
        data_over_years = []

        for model_year_object in results_resid:
            tot_fuel = getattr(model_year_object, attribute_to_get) # Hourly fuel data
            data_over_years.append(tot_fuel[enduse])

        Y_init[k] = data_over_years

    #print("Y_init:" + str(Y_init))
    #color_list = ["green", "red", "#6E5160"]

    sp = ax.stackplot(x, Y_init)
    proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

    ax.legend(proxy, legend_entries)

    #ticks x axis
    #ticks_x = range(2015, 2015 + nr_y_to_plot)
    #plt.xticks(ticks_x)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='red')
    plt.axis('tight')

    plt.xlabel("Simulation years")
    plt.title("Stacked energy demand for simulation years for whole UK")

    plt.show()

def plot_load_curves_fueltype(results_resid, data): # nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years

    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        for fueltype_str in data['lu_fueltype']:
            if data['lu_fueltype'][fueltype_str] == fueltype:
                fueltype_in_string = fueltype_str
        legend_entries.append(fueltype_in_string)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:
            # Max hourly load curve of fueltype
            fueltype_load_max_h = model_year_object.tot_country_fuel_load_max_h

            data_over_years.append(fueltype_load_max_h[fueltype][0])

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='red')
    plt.axis('tight')

    plt.ylabel("Percent %")
    plt.xlabel("Simulation years")
    plt.title("Load factor of maximum hour across all enduses")

    plt.show()

def plot_fuels_tot_all_enduses_week(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    # Number of days to plot
    days_to_plot = range(10, 17)

    # Which year in simulation (2015 = 0)
    year_to_plot = 2

    fig, ax = plt.subplots()
    nr_of_h_to_plot = len(days_to_plot) * 24

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_of_h_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = technologies_related.get_fueltype_str(data['lu_fueltype'], fueltype)
        legend_entries.append(fueltype_in_string)

        # Read out fueltype specific max h load
        tot_fuels = getattr(results_resid[year_to_plot], attribute_to_get)
        print("TEESTFUL : " + str(np.sum(tot_fuels[fueltype])))
        data_over_day = []
        for day, daily_values in enumerate(tot_fuels[fueltype]):
            if day in days_to_plot:
                for hour in daily_values:
                    data_over_day.append(hour)

        Y_init[fueltype] = data_over_day

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    x_tick_pos = []
    for day in range(len(days_to_plot)):
        x_tick_pos.append(day * 24)
    plt.xticks(x_tick_pos, days_to_plot, color='black')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("days")
    plt.title("Total yearly fuels of all enduses per fueltype for simulation year {} ".format(year_to_plot + 2050))
    plt.show()

def plot_fuels_tot_all_enduses(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots()
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = technologies_related.get_fueltype_str(data['lu_fueltype'], fueltype)
        legend_entries.append(fueltype_in_string)

        # Read out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:

            tot_fuels = getattr(model_year_object, attribute_to_get)

            #for every hour is summed to have yearl fuel
            tot_fuel_fueltype_y = np.sum(tot_fuels[fueltype])
            data_over_years.append(tot_fuel_fueltype_y)

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Total yearly fuels of all enduses per fueltype")
    plt.show()


def plot_fuels_peak_hour(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = technologies_related.get_fueltype_str(data['lu_fueltype'], fueltype)

        legend_entries.append(fueltype_in_string)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:
            fueltype_load_max_h = getattr(model_year_object, attribute_to_get)
            data_over_years.append(fueltype_load_max_h[fueltype])

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Fuels for peak hour in a year across all enduses")
    plt.show()
