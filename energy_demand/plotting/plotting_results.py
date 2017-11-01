"""
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from energy_demand.technologies import tech_related
from energy_demand.plotting import plotting_program

# INFO
# https://stackoverflow.com/questions/35099130/change-spacing-of-dashes-in-dashed-line-in-matplotlib
# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781849513265/4/ch04lvl1sec56/using-a-logarithmic-scale

def run_all_plot_functions(
        results_every_year,
        results_enduse_every_year,
        tot_fuel_y_max,
        data,
        load_factors_y,
        load_factors_yh,
        load_factor_seasons
    ):
    """Function summarising all functions to plot
    """

    ##pf.plot_load_curves_fueltype(results_every_year, data)
    # plotting load factors per fueltype and region
    plot_seasonal_lf(
        data['lookups']['fueltype']['electricity'],
        load_factor_seasons,
        data['reg_nrs'])

    print("... plotting load_factors_yh")
    plot_lf_y(
        data['lookups']['fueltype']['electricity'],
        load_factors_yh,
        data['reg_nrs'])
    print("... plotting plot_lf_y")
    plot_lf_y(
        data['lookups']['fueltype']['electricity'],
        load_factors_y,
        data['reg_nrs'])

    logging.debug("... Plot total fuel (y) per fueltype")
    plt_fuels_enduses_y(
        "fig_tot_all_enduse01.pdf",
        results_every_year,
        data)

    logging.debug("... plot other figure")
    plt_fuels_enduses_y(
        "fig_tot_all_enduse02.pdf",
        results_every_year,
        data)

    logging.debug("... plot a full week")
    plt_fuels_enduses_week(
        "fig_tot_all_enduse03.pdf",
        results_every_year,
        data,
        data['assumptions']['model_yearhours_nrs'],
        data['assumptions']['model_yeardays_nrs'])

    logging.debug("... plot a full week")
    plt_fuels_enduses_week(
        "fig_tot_all_enduse04.pdf",
        results_every_year,
        data,
        data['assumptions']['model_yearhours_nrs'],
        data['assumptions']['model_yeardays_nrs'])

    plt_stacked_enduse(
        "figure_stacked_country_final.pdf",
        data,
        results_enduse_every_year,
        data['enduses']['rs_all_enduses'],
        'tot_fuel_y_enduse_specific_h')

    # Plot all enduses
    #plt_stacked_enduse(
    # "figure_stacked_country_final.pdf",
    # data,
    # results_every_year,
    # data['enduses']['rs_all_enduses'],
    # 'tot_fuel_y_enduse_specific_h')

    #logging.debug('Plot peak demand (h) per fueltype')
    #plt_fuels_peak_h(tot_fuel_y_max, data)
    return

def plot_seasonal_lf(fueltype_lf, load_factors_seasonal, reg_nrs):
    """Plot load factors per region for every year

    Arguments
    --------
    fueltype_lf : int
        Fueltype_int to print (see lookup)
    load_factors_seasonal : dict
        Seasonal load factors per season
    reg_nrs : int
        Number of region
    """
    print("... plotting seasonal load factors")

    # Set figure size
    plt.figure(figsize=plotting_program.cm2inch(8, 8))

    # Settings
    color_list = {
        'winter': 'wheat',
        'summer': 'olive',
        'spring': 'yellowgreen',
        'autumn': 'darkkhaki'}

    classes = color_list.keys()
    class_colours = color_list.values()

    # ------------
    # Iterate regions and plot load factors
    # ------------
    for reg_nr in range(reg_nrs):
        for season, lf_fueltypes_season in load_factors_seasonal.items():
            x_values_season_year = []
            y_values_season_year = []
            for year, lf_fueltype_reg in lf_fueltypes_season.items():
                x_values_season_year.append(year)
                y_values_season_year.append(lf_fueltype_reg[fueltype_lf][reg_nr])
                #y_values_season_year.append(load_factors_seasonal[season][year][fueltype_lf][reg_nr])

            # plot individual saisonal data point
            plt.plot(
                x_values_season_year,
                y_values_season_year,
                color=color_list[season],
                linewidth=0.5,
                alpha=0.7) #, label=season)

    # ------------------------------------
    # Calculate average per season for all regions
    # and plot average line a bit thicker
    # ------------------------------------
    for season in classes:
        years = []
        average_season_year_years = []
        for year in load_factors_seasonal[season].keys():
            average_season_year = []

            # Iterate over regions
            for reg_nr in range(reg_nrs):
                average_season_year.append(load_factors_seasonal[season][year][fueltype_lf][reg_nr])

            years.append(int(year))
            average_season_year_years.append(np.mean(average_season_year))

        # plot individual saisonal data point
        plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            linewidth=2,
            linestyle='--', dashes=(5, 10))

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor [%]")

    base_yr = 2015
    year_interval = 5
    major_ticks = np.arange(base_yr, years[-1] + year_interval, year_interval)                                                                                          
    plt.xticks(major_ticks, major_ticks) #, rotation=90)



    # ------------
    # Plot color legend with colors for every season
    # ------------
    recs = []
    for color_nr in range(0, len(class_colours)):
        recs.append(mpatches.Rectangle((0,0), 1, 1, fc=class_colours[color_nr]))

    plt.legend(recs, classes, loc='best') #4

    # plot
    plt.show()

def plot_lf_y(fueltype_lf, load_factors_y, reg_nrs):
    """Plot load factors per region for every year

    Arguments
    --------

    """
    # Line plot for every region over years
    for reg_nr in range(reg_nrs):
        x_values_year = []
        y_values_year = []

        for year, lf_fueltype_reg in load_factors_y.items():
            x_values_year.append(year)
            y_values_year.append(lf_fueltype_reg[fueltype_lf][reg_nr])

        plt.plot(x_values_year, y_values_year, color='grey')

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor [%]")

    base_yr = 2015
    year_interval = 2
    years = list(load_factors_y.keys())

    major_ticks = np.arange(base_yr, years[-1] + year_interval, year_interval)                                                                                          
    plt.xticks(major_ticks, major_ticks) #, rotation=90)

    plt.show()

def plot_x_days(all_hours_year, region, days):
    """With input 2 dim array plot daily load
    """

    x_values = range(days * 24)
    y_values = []

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

    plt.show()

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
    plt.show()

def plt_fuels_enduses_week(fig_name, results_resid, data, nr_of_h_to_plot, model_yeardays_nrs, year_to_plot=2015):
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
   
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_of_h_to_plot))

    for fueltype_str, fueltype_int in data['lookups']['fueltype'].items():
        legend_entries.append(fueltype_str)

        # Select year to plot
        fuel_all_regions = results_resid[year_to_plot][fueltype_int]

        data_over_day = np.zeros((8760))
        for region_data in fuel_all_regions:
            data_over_day += region_data
        #_a = np.sum(data_over_day, axis=0)  #FASTER with numpy TODO

        Y_init[fueltype_int] = data_over_day

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    x_tick_pos = []
    for day in range(model_yeardays_nrs):
        x_tick_pos.append(day * 24)
    plt.xticks(x_tick_pos, days_to_plot, color='black')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("days")
    plt.title("Total yearly fuels of all enduses per fueltype for simulation year {} ".format(year_to_plot + 2050))

    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))

    plt.show()

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

    for fueltype_str, fueltype in data['lookups']['fueltype'].items():

        # Legend
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

    # -----------------
    # Axis labelling
    # -----------------
    #plt.xlabel("years")
    #plt.ylabel("load factor [%]")

    base_yr = 2015
    year_interval = 2
    #years = load_factors_y.keys()

    major_ticks = np.arange(base_yr, base_yr + nr_y_to_plot, year_interval) #, )                                                                                          
    plt.xticks(major_ticks, major_ticks, color='green') #, rotation=90)

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    # ------------
    # Plot legend
    # ------------
    ax.legend(legend_entries)

    #plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Total yearly fuels of all enduses per fueltype")
    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))

    plt.show()

    return

def plt_fuels_peak_h(tot_fuel_y_max, data):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(tot_fuel_y_max) #number of simluated years

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype in data['lookups']['fueltype'].items():

        # Legend
        legend_entries.append(fueltype_str)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in tot_fuel_y_max.values():
            print("model_year_object: "  + str(model_year_object))
            print(fueltype)
            data_over_years.append(model_year_object[fueltype])

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


def plot_load_profile_dh(array_dh):
    """plot daily profile
    """
    x_values = range(24)

    plt.plot(x_values, list(array_dh), color='green') #'ro', markersize=1,
    
    plt.show()

def testplot():
    """TESTLINELOTS
    """
    x_values = [[3,23],[32,12]]
    y_values = [[4,44],[33,1]]

    for line_nr in range(2):
        plt.plot(x_values[line_nr], y_values[line_nr], color='green') #'ro', markersize=1,
    testplot()
    plt.show()

'''
    # Scatter plot over years
    for year, lf_fueltype_reg in load_factors_y.items():
        for _region, lf_reg in enumerate(lf_fueltype_reg[fueltype_lf]):
            x_values.append(year)
            y_values.append(lf_reg)

    #plt.plot(x_values, y_values)
    plt.scatter(x_values, y_values)

'''
