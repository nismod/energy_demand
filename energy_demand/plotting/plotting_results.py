"""Plotting model results and storing as PDF to result folder
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions
#import matplotlib.colors as colors #for color_name in colors.cnmaes:

# INFO
# https://stackoverflow.com/questions/35099130/change-spacing-of-dashes-in-dashed-line-in-matplotlib
# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781849513265/4/ch04lvl1sec56/using-a-logarithmic-scale
# Setting x labels: https://matplotlib.org/examples/pylab_examples/major_minor_demo1.html

def run_all_plot_functions(results_container, reg_nrs, lookups, local_paths, assumptions, sim_param, enduses):
    """Summary function to plot all results


    """
    logging.info("... plotting results")
    ##pf.plot_load_curves_fueltype(results_every_year, data)

    # ----------
    # Plot seasonal typical load profiles
    # ----------
    # Averaged load profile per daytpe for a region

    # ------------------------------------
    # Load factors per fueltype and region
    # ------------------------------------
    for fueltype_str, fueltype_int in lookups['fueltype'].items():

        plot_seasonal_lf(
            fueltype_int,
            fueltype_str,
            results_container['load_factor_seasons'],
            reg_nrs,
            os.path.join(
                local_paths['data_results_PDF'],
                'lf_seasonal_{}.pdf'.format(fueltype_str)))

        plot_lf_y(
            fueltype_int,
            fueltype_str,
            results_container['load_factors_yh'],
            reg_nrs,
            os.path.join(
                local_paths['data_results_PDF'], 'lf_yh_{}.pdf'.format(fueltype_str)))

        plot_lf_y(
            fueltype_int,
            fueltype_str,
            results_container['load_factors_y'],
            reg_nrs,
            os.path.join(
                local_paths['data_results_PDF'],
                'lf_y_{}.pdf'.format(fueltype_str)))

    # --------------
    # Fuel per fueltype for whole country over annual timesteps
    # ----------------
    logging.debug("... Plot total fuel (y) per fueltype")
    plt_fuels_enduses_y(
        results_container['results_every_year'],
        lookups,
        os.path.join(
            local_paths['data_results_PDF'],
            'fig_tot_all_enduse01.pdf'))

    # --------------
    # Fuel week of base year
    # ----------------
    logging.debug("... plot a full week")
    plt_fuels_enduses_week(
        results_container['results_every_year'],
        lookups,
        assumptions['model_yearhours_nrs'],
        assumptions['model_yeardays_nrs'],
        2015,
        os.path.join(local_paths['data_results_PDF'], "tot_all_enduse03.pdf"))

    logging.debug("... plot a full week")
    plt_fuels_enduses_week(
        results_container['results_every_year'],
        lookups,
        assumptions['model_yearhours_nrs'],
        assumptions['model_yeardays_nrs'],
        2015,
        os.path.join(local_paths['data_results_PDF'], "tot_all_enduse04.pdf"))

    # ------------
    # Stacked enduses
    # ------------
    # Residential
    plt_stacked_enduse(
        sim_param['sim_period'],
        results_container['results_enduse_every_year'],
        enduses['rs_all_enduses'],
        os.path.join(local_paths['data_results_PDF'], "stacked_rs_country_final.pdf"))

    # Service
    plt_stacked_enduse(
        sim_param['sim_period'],
        results_container['results_enduse_every_year'],
        enduses['ss_all_enduses'],
        os.path.join(local_paths['data_results_PDF'], "stacked_ss_country_final.pdf"))

    # Industry
    plt_stacked_enduse(
        sim_param['sim_period'],
        results_container['results_enduse_every_year'],
        enduses['is_all_enduses'],
        os.path.join(local_paths['data_results_PDF'], "stacked_is_country_final.pdf"))

    # ------------------------------------
    # Plot averaged per season an fueltype
    # ------------------------------------
    base_year = 2015
    for year in results_container['av_season_daytype_current_year'].keys():
        for fueltype in results_container['av_season_daytype_current_year'][year].keys():
            plot_load_profile_dh_multiple(
                os.path.join(local_paths['data_results_PDF'], 'season_daytypes_by_cy_comparison__{}__{}.pdf'.format(year, fueltype)),
                results_container['av_season_daytype_current_year'][year][fueltype], #d#MAYBE CURRENT YEAR
                results_container['av_season_daytype_current_year'][base_year][fueltype]#, #BASEYEAR
                #results_container['season_daytype_current_year'][year][fueltype], #MAYBE CURRENT YEAR
                #results_container['season_daytype_current_year'][base_year][fueltype] #BASEYEAR
                )
    
    # Plot all enduses
    #plt_stacked_enduse(
    # sim_param['sim_period'],
    # results_container['results_every_year'],
    # data['enduses']['rs_all_enduses'],
    # 'tot_fuel_y_enduse_specific_h',
    # os.path.join(data['local_paths']['data_results_PDF'], "figure_stacked_country_final.pdf")))

    # ---------------------------------
    # Plot peak loads for different seasons
    # --------------------------------
    #plt_fuels_peak_h(results_container['tot_fuel_y_max'], data)
    return

def plot_seasonal_lf(fueltype_int, fueltype_str, load_factors_seasonal, reg_nrs, path_plot_fig):
    """Plot load factors per region for every year

    Arguments
    --------
    fueltype_int : int
        Fueltype_int to print (see lookup)
    fueltype_str : str
        Fueltype string to print
    load_factors_seasonal : dict
        Seasonal load factors per season
    reg_nrs : int
        Number of region
    """
    print("... plotting seasonal load factors")

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1) # fig plot

    # Settings
    color_list = {
        'winter': 'midnightblue',
        'summer': 'darkgreen',
        'spring': 'springgreen',
        'autumn': 'gold'}

    classes = list(color_list.keys())
    class_colours = list(color_list.values())

    # ------------
    # Iterate regions and plot load factors
    # ------------
    for reg_nr in range(reg_nrs):
        for season, lf_fueltypes_season in load_factors_seasonal.items():
            x_values_season_year = []
            y_values_season_year = []
            for year, lf_fueltype_reg in lf_fueltypes_season.items():
                x_values_season_year.append(year)
                y_values_season_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

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
                average_season_year.append(
                    load_factors_seasonal[season][year][fueltype_int][reg_nr])

            years.append(int(year))
            average_season_year_years.append(np.mean(average_season_year))

        # plot individual saisonal data point
        plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            linewidth=1,
            linestyle='--') #, dashes=(5, 10))

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling and ticks
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor {} [%]".format(fueltype_str))

    base_yr = 2015
    minor_interval = 5
    major_interval = 10

    # Major ticks
    major_ticks = np.arange(base_yr,years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)
    #ax.set_xlabel(major_ticks)

    # Minor ticks
    minor_ticks = np.arange(base_yr,years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor = True)
    #ax.set_xlabel(minor_ticks)

    # ------------
    # Plot color legend with colors for every season
    # ------------
    recs = []
    for color_nr in range(0, len(class_colours)):
        recs.append(mpatches.Rectangle((0,0), 1, 1, fc=class_colours[color_nr], alpha=0.7))

    plt.legend(
        recs,
        classes,
        ncol=2,
        loc='best',
        frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_plot_fig)
    plt.close()

def plot_lf_y(fueltype_int, fueltype_str, load_factors_y, reg_nrs, path_plot_fig):
    """Plot load factors per region for every year

    Arguments
    --------

    """
    print("... plotting load factors")

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1) # fig plot

    # Line plot for every region over years
    for reg_nr in range(reg_nrs):
        x_values_year = []
        y_values_year = []

        for year, lf_fueltype_reg in load_factors_y.items():
            x_values_year.append(year)
            y_values_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

        plt.plot(x_values_year, y_values_year, color='grey')

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor, fueltpye {} [%]".format(fueltype_str))

    years = list(load_factors_y.keys())
    base_yr = 2015

    # Major ticks
    major_interval = 10
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)
    #ax.set_xlabel(major_ticks)

    # Minor ticks
    minor_interval = 5
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(path_plot_fig)
    plt.close()

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
    plt.ylabel("Energy demand [GW]")
    plt.title("Energy Demand")
    plt.legend(ncol=2, frameon=False)

    plt.show()
    plt.close()

def plot_load_shape_yd(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 0] * 100) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Percentage of daily demand")
    plt.title("Load curve of a day")
    plt.legend(ncol=2, frameon=False)
    
    plt.show()
    plt.close()

def plot_load_shape_yd_non_resid(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 1]) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("ABSOLUTE VALUES TEST NONRESID")
    plt.legend(ncol=2, frameon=False)
    plt.show()

def plt_stacked_enduse(sim_period, results_enduse_every_year, enduses_data, fig_name):
    """Plots stacked end_use for a region

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
    years_simulated = sim_period

    x_data = years_simulated
    y_data = np.zeros((len(enduses_data), len(years_simulated)))

    legend_entries = []
    for fueltype_int, enduse in enumerate(enduses_data):
        legend_entries.append(enduse)

        for model_year, data_model_run in enumerate(results_enduse_every_year.values()):
            y_data[fueltype_int][model_year] = np.sum(data_model_run[enduse])

    fig, ax = plt.subplots()

    # ----------
    # Stack plot
    # ----------
    stack_plot = ax.stackplot(x_data, y_data)

    # -------
    # Legend
    # -------
    # Get color of stacks in stackplot
    color_stackplots = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in stack_plot]

    plt.legend(
        color_stackplots,
        legend_entries,
        ncol=2,
        loc='best',
        frameon=False)

    # -------
    # Axis
    # -------
    plt.xticks(years_simulated, years_simulated)

    # -------
    # Labels
    # -------
    plt.ylabel("energy demand [GWh per year]")
    plt.xlabel("years")
    plt.title("stacked energy demand for simulation years for whole UK")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(fig_name)
    plt.close()

def plot_load_curves_fueltype(results_objects, data, fig_name):
    """Plots stacked end_use for a region
    # INFO Cannot plot a single year?
    """
    fig, ax = plt.subplots()
    nr_y_to_plot = len(results_objects) #number of simluated years

    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype_int in data['lookups']['fueltype'].items():

        # Legend
        legend_entries.append(fueltype_str)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_objects:
            # Max hourly load curve of fueltype
            fueltype_load_max_h = model_year_object.tot_country_fuel_load_max_h

            data_over_years.append(fueltype_load_max_h[fueltype_int][0])

        y_init[fueltype_int] = data_over_years

    # Plot lines
    for line, _ in enumerate(y_init):
        plt.plot(y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot)) #, color='red')
    plt.axis('tight')

    plt.ylabel("Percent %")
    plt.xlabel("Simulation years")
    plt.title("Load factor of maximum hour across all enduses")
    plt.show()
    plt.savefig(fig_name)
    plt.close()

def plt_fuels_enduses_week(results_resid, lookups, nr_of_h_to_plot, model_yeardays_nrs, year_to_plot, fig_name):
    """Plots stacked end_use for all regions

    Input
    -----
    year_to_plot : int
        2015 --> 0

    # INFO Cannot plot a single year?
    """
    days_to_plot = range(model_yeardays_nrs)

    fig, ax = plt.subplots()

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((lookups['fueltypes_nr'], nr_of_h_to_plot))

    for fueltype_str, fueltype_int in lookups['fueltype'].items():
        legend_entries.append(fueltype_str)

        # Select year to plot
        fuel_all_regions = results_resid[year_to_plot][fueltype_int]

        data_over_day = np.zeros((8760))
        for region_data in fuel_all_regions:
            data_over_day += region_data

        y_init[fueltype_int] = data_over_day

    # Plot lines
    for line, _ in enumerate(y_init):
        plt.plot(y_init[line])

    ax.legend(legend_entries)

    x_tick_pos = []
    for day in range(model_yeardays_nrs):
        x_tick_pos.append(day * 24)
    plt.xticks(x_tick_pos, days_to_plot, color='black')
    plt.axis('tight')

    plt.legend(ncol=2, frameon=False)

    plt.ylabel("energy demand [GWh per hour]")
    plt.xlabel("days")
    plt.title("Total yearly fuels of all enduses per fueltype for simulation year {} ".format(year_to_plot + 2050))

    # Saving figure
    plt.savefig(fig_name)
    plt.close()

def plt_fuels_enduses_y(results_resid, lookups, fig_name):
    """Plot lines with total fuel demand for all enduses
    per fueltype over the simluation period

    Arguments
    ---------
    results_resid : dict
        Results for every year and fueltype (yh)
    lookups : dict
        Lookup fueltypes
    fig_name : str
        Figure name

    Note
    ----
    Values are divided by 1'000
    """
    # Set figure size
    plt.figure(figsize=plotting_program.cm2inch(14, 8))

    # Initialise (number of enduses, number of hours to plot)
    y_values_fueltype = {}

    for fueltype_str, fueltype_int in lookups['fueltype'].items():

        # Read out fueltype specific max h load
        data_years = {}
        for year, data_year in results_resid.items():
            tot_fuel_fueltype_y = np.sum(data_year[fueltype_int])

            # -------
            # Conversion i necessary?? TODO
            # -------
            data_years[year] = tot_fuel_fueltype_y

        y_values_fueltype[fueltype_str] = data_years

    # -----------------
    # Axis
    # -----------------
    base_yr, year_interval = 2015, 5
    end_yr = list(results_resid.keys())

    major_ticks = np.arange(
        base_yr, end_yr[-1] + year_interval, year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list = [
        'darkturquoise', 'orange', 'firebrick',
        'darkviolet', 'khaki', 'olive', 'darkseagreen',
        'darkcyan', 'indianred', 'darkblue']

    for fueltype_str, fuel_fueltype_yrs in y_values_fueltype.items():
        color_line = str(color_list.pop())

        # plot line
        plt.plot(
            list(fuel_fueltype_yrs.keys()), #years
            list(fuel_fueltype_yrs.values()), #yearly data per fueltype
            color=color_line,
            label=fueltype_str)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # ---------
    # Labels
    # ---------
    plt.ylabel("energy demand [GWh per year]")
    plt.xlabel("years")
    plt.title("total yearly fuels of all enduses per fueltype")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)#ax.margins(x=0)

    # Save fig
    plt.savefig(fig_name)
    plt.close()

def plt_fuels_peak_h(tot_fuel_y_max, data):
    """Plots stacked end_use for a region

    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(tot_fuel_y_max) #number of simluated years

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype in data['lookups']['fueltype'].items():

        # Legend
        legend_entries.append(fueltype_str)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in tot_fuel_y_max.values():
            print("model_year_object: "  + str(model_year_object))
            print(fueltype)
            data_over_years.append(model_year_object[fueltype])

        y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(y_init):
        plt.plot(y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Fuels for peak hour in a year across all enduses")
    plt.show()

def plot_load_profile_dh_multiple(path_plot_fig, calc_av_lp_modelled, calc_av_lp_real, calc_lp_modelled=None, calc_lp_real=None):
    """Plotting average saisonal loads for each daytype

    https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
    """
    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(14, 25))
    ax = fig.add_subplot(nrows=4, ncols=2)

    plot_nr = 0
    for season in calc_av_lp_modelled:
        for daytype in calc_av_lp_modelled[season]:
            plot_nr += 1

            plt.subplot(4, 2, plot_nr)

            # ------------------
            # Plot average
            # ------------------
            x_values = range(24)
            plt.plot(x_values, list(calc_av_lp_real[season][daytype]), color='green', label='real_by')
            plt.plot(x_values, list(calc_av_lp_modelled[season][daytype]), color='red', label='modelled_future')

            # ------------------
            # Plot every single line
            # ------------------
            if calc_lp_modelled != None:
                for entry in range(len(calc_lp_real[season][daytype])):
                    plt.plot(x_values, list(calc_lp_real[season][daytype][entry]), color='red', markersize=0.5, alpha=0.2)
                    plt.plot(x_values, list(calc_lp_modelled[season][daytype][entry]), color='green', markersize=0.5, alpha=0.2)

            # -----------------
            # Axis
            # -----------------
            plt.ylim(0, 60)

            # Tight layout
            plt.tight_layout()
            plt.margins(x=0)

            # Calculate RMSE
            rmse = basic_functions.rmse(
                calc_av_lp_modelled[season][daytype],
                calc_av_lp_real[season][daytype])

            # -----------
            # Labelling
            # -----------
            font_additional_info = {
                'family': 'arial', 'color': 'black', 'weight': 'normal', 'size': 8}
            title_info = ('{}, {}'.format(season, daytype))
            plt.text(1, 0.55, "RMSE: {}".format(round(rmse, 2)), fontdict=font_additional_info)
            plt.title(title_info, loc='left', fontdict=font_additional_info)
            #plt.ylabel("hours")
            #plt.ylabel("average electricity [GW] ")

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=1, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    fig.savefig(path_plot_fig)
    plt.close()

def plot_load_profile_dh(data_dh_real, data_dh_modelled, path_plot_fig):
    """plot daily profile
    """
    x_values = range(24)

    plt.plot(x_values, list(data_dh_real), color='green', label='real') #'ro', markersize=1,
    plt.plot(x_values, list(data_dh_modelled), color='red', label='modelled') #'ro', markersize=1,

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 60)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_plot_fig)
    plt.close()

def testplot():
    """TESTLINELOTS
    """
    x_values = [[3, 23], [32, 12]]
    y_values = [[4, 44], [33, 1]]

    for line_nr in range(2):
        plt.plot(x_values[line_nr], y_values[line_nr], color='green') #'ro', markersize=1,
    testplot()
    plt.show()

'''
    # Scatter plot over years
    for year, lf_fueltype_reg in load_factors_y.items():
        for _region, lf_reg in enumerate(lf_fueltype_reg[fueltype_int]):
            x_values.append(year)
            y_values.append(lf_reg)

    #plt.plot(x_values, y_values)
    plt.scatter(x_values, y_values)

'''
