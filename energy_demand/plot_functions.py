"""Functions used for plotting"""
import matplotlib.pyplot as plt
import numpy as np



    


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
    plt.title("Plotting all month for the daytype {}".format(daytype))
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


