"""Functions used for plotting"""
import matplotlib.pyplot as plt
import numpy as np

import matplotlib as mpl


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


def plot_load_shape_d(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 0] * 100) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Percentage of daily demand")
    plt.title("Load curve of a day")
    plt.legend()
    plt.show()


def plot_load_shape_d_non_resid(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 1]) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("ABSOLUTE VALUES TEST NONRESID")
    plt.legend()
    plt.show()

def plot_FUNCTIONSE():

    plot_average = True

    x_values = range(24)

    #-- plot yearly average
    print("Yearly Average over all measurements")
    for daytype in yearly_averaged_load_curve:

        # y-values
        y_values = list(yearly_averaged_load_curve[daytype].values())
        print("y_values")
        print(y_values)
        plt.plot(x_values, y_values, label = 'daytype %s'%daytype)

    plt.xlabel("hours")
    plt.ylabel("percentage of daily demand")
    plt.title("Plotting all month for the daytype {}".format(str(daytype)))
    plt.legend()
    plt.show()


    # --- if average is calculated
    if plot_average == True:

        # plot all month
        for month in range(12):

            # y-values
            y_values = list(out_dict_average[daytype][month].values())
            plt.plot(x_values, y_values, label = 'Month %s'%month)

        plt.xlabel("hours")
        plt.ylabel("percentage of daily demand")
        plt.title("Plotting all month for the daytype {}".format(daytype))
        plt.legend()
        plt.show()


    # --- if individual days are plotted
    if plot_average == False:

        month = 3
        daytype = 1 # Daytaoe

        # y-values
        y_values = list(out_dict_not_average[daytype][month].values()) #) # daytype = 0, January = 0

        plt.plot(x_values, y_values)
        plt.xlabel("hours")
        plt.ylabel("percentage of daily demand")
        plt.title("Plotting the Month of {} for the daytype {}".format(month, daytype))
        plt.show()

#print("Finished loead profiles generator")

def plot_stacked_Country_end_use(results_resid, data): # nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years
    print("nr_y_to_plot" + str(nr_y_to_plot))
    x = range(nr_y_to_plot)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((len(data['resid_enduses']), nr_y_to_plot))

    for k, enduse in enumerate(data['resid_enduses']):
        legend_entries.append(enduse)
        data_over_years = []

        for model_year_object in results_resid:
            tot_fuel = model_year_object.tot_country_fuel_enduse_specific # FUEL DATA
            data_over_years.append(tot_fuel[enduse])

        Y_init[k] = data_over_years

    print("Y_init:" + str(Y_init))
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