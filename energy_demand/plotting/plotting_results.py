"""
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from energy_demand.technologies import tech_related
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def run_all_plot_functions(results_every_year, results_enduse_every_year, data):
    """Function summarising all functions to plot 
    """
    ##pf.plot_load_curves_fueltype(results_every_year, data)

    # Plot total fuel (y) per fueltype
    plt_fuels_enduses_y(
        "fig_tot_all_enduse01.pdf",
        results_every_year,
        data)

    plt_fuels_enduses_y(
        "fig_tot_all_enduse02.pdf",
        results_every_year,
        data)

    # Plot a full week
    plt_fuels_enduses_week(
        "fig_tot_all_enduse03.pdf",
        results_every_year,
        data,
        data['assumptions']['model_yeardays_nrs'])

    plt_fuels_enduses_week(
        "fig_tot_all_enduse04.pdf",
        results_every_year,
        data,
        data['assumptions']['model_yeardays_nrs'])

    # Plot all enduses
    #plt_stacked_enduse(
    # "figure_stacked_country_final.pdf",
    # data,
    # results_every_year,
    # data['enduses']['rs_all_enduses'],
    # 'tot_fuel_y_enduse_specific_h')

    plt_stacked_enduse(
        "figure_stacked_country_final.pdf",
        data,
        results_enduse_every_year,
        data['enduses']['rs_all_enduses'],
        'tot_fuel_y_enduse_specific_h')

    # Plot peak demand (h) per fueltype
    plt_fuels_peak_h(results_every_year, data, 'tot_fuel_y_max_enduses')
    return

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
    #plt.show()

def plot_load_shape_yd(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 0] * 100) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Percentage of daily demand")
    plt.title("Load curve of a day")
    plt.legend()
    #plt.show()

def plot_load_shape_yd_non_resid(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 1]) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("ABSOLUTE VALUES TEST NONRESID")
    plt.legend()
    #plt.show()

def plt_stacked_enduse(fig_name, data, results_enduse_every_year, enduses_data, attribute_to_get):
    """Plots stacked end_use for a region

    Arguments
    ----------
    data : dict
        Data container
    results_objects :

    enduses_data :

    attribute_to_get :


    Note
    ----
        -   Sum across all fueltypes

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """
    nr_y_to_plot = data['sim_param']['sim_period_yrs']
    years_simulated = data['sim_param']['sim_period']

    x_data = years_simulated #range(nr_y_to_plot)
    y_data = np.zeros((len(enduses_data), len(years_simulated))) #nr_y_to_plot))

    legend_entries = []
    for k, enduse in enumerate(enduses_data):
        legend_entries.append(enduse)

        for model_year, data_model_run in enumerate(results_enduse_every_year.values()):
            y_data[k][model_year] = np.sum(data_model_run[enduse])

        '''for year, model_year_object in enumerate(results_objects):
            country_enduse_y = getattr(model_year_object, attribute_to_get)

            # Sum all fueltypes
            y_data[k][year] = np.sum(country_enduse_y[enduse]) #Summing across all fueltypes
        '''

    fig, ax = plt.subplots()
    sp = ax.stackplot(x_data, y_data)
    proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]
    ax.legend(proxy, legend_entries)

    plt.xticks(years_simulated, years_simulated, color='red') # range(nr_y_to_plot) range(2015, 2015 + nr_y_to_plot)
    plt.axis('tight')

    plt.xlabel("Simulation years")
    plt.title("Stacked energy demand for simulation years for whole UK")
    logging.debug("...plot figure")
    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))

    if data['print_criteria']:
        plt.show()
    else:
        pass

    return
def plot_load_curves_fueltype(results_objects, data): # nr_of_day_to_plot, fueltype, yearday, region):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_objects) #number of simluated years

    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype_int in data['lookups']['fueltype'].items():

        # Legend
        legend_entries.append(fueltype_str)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_objects:
            # Max hourly load curve of fueltype
            fueltype_load_max_h = model_year_object.tot_country_fuel_load_max_h

            data_over_years.append(fueltype_load_max_h[fueltype_int][0])

        Y_init[fueltype_int] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='red')
    plt.axis('tight')

    plt.ylabel("Percent %")
    plt.xlabel("Simulation years")
    plt.title("Load factor of maximum hour across all enduses")

    #plt.show()

def plt_fuels_enduses_week(fig_name, results_resid, data, model_yeardays_nrs, year_to_plot=2015):
    """Plots stacked end_use for all regions

    Input
    -----
    year_to_plot : int
        2015 --> 0

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    # Number of days to plot
    #days_to_plot = range(10, 17)
    days_to_plot = range(model_yeardays_nrs)

    fig, ax = plt.subplots()
    nr_of_h_to_plot = model_yeardays_nrs * 24

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_of_h_to_plot))

    for fueltype_str, fueltype_int in data['lookups']['fueltype'].items():

        legend_entries.append(fueltype_str) #Legend
        # Select year to plot
        fuel_all_regions = results_resid[year_to_plot][fueltype_int]

        data_over_day = np.zeros((8760))
        for region_data in fuel_all_regions:
            data_over_day += region_data #FASTER with numpy TODO

        Y_init[fueltype_int] = data_over_day

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

    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))
    
    if data['print_criteria']:
        plt.show()
    else:
        pass

def plt_fuels_enduses_y(fig_name, results_resid, data):
    """Plots stacked end_use for a region

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """
    fig, ax = plt.subplots()
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lookups']['fueltype']):

        # Legend
        fueltype_str = tech_related.get_fueltype_str(data['lookups']['fueltype'], fueltype)
        legend_entries.append(fueltype_str)

        # Read out fueltype specific max h load
        data_over_years = []
        for model_year, data_model_run in results_resid.items():
            tot_fuel_fueltype_y = np.sum(data_model_run[fueltype])
            data_over_years.append(tot_fuel_fueltype_y)

        '''for model_year_object in results_resid:
            tot_fuels = getattr(model_year_object, attribute_to_get)

            #for every hour is summed to have yearl fuel
            tot_fuel_fueltype_y = np.sum(tot_fuels[fueltype])
            data_over_years.append(tot_fuel_fueltype_y)
        '''

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Total yearly fuels of all enduses per fueltype")
    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))

    if data['print_criteria']:
        plt.show()
    else:
        pass

    return

def plt_fuels_peak_h(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lookups']['fueltype']):

        # Legend
        fueltype_str = tech_related.get_fueltype_str(data['lookups']['fueltype'], fueltype)

        legend_entries.append(fueltype_str)

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

    if data['print_criteria']:
        plt.show()
    else:
        pass

    return

def plot_load_profile_dh(array_dh):
    """plot daily profile
    """
    x_values = range(24)

    plt.plot(x_values, list(array_dh), color='green') #'ro', markersize=1,
    
    #plt.show()
