"""Plotting model results and storing as PDF to result folder
"""
import os
import logging
from collections import defaultdict
import operator
from math import pi
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy import stats

from energy_demand import enduse_func
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions, conversions
from energy_demand.plotting import plotting_styles
from energy_demand.technologies import tech_related
from energy_demand.profiles import load_factors
from energy_demand.plotting import plotting_results
from scipy.interpolate import interp1d

def smooth_data(x_list, y_list, num=500, spider=False):
    """Smooth data

    x_list : list
        List with hours

    # https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html

    """
    if spider:

        nr_x_values = len(x_list)
        min_x_val = min(x_list)
        max_x_val = math.pi * 2 #max is tow pi

        x_values = np.linspace(min_x_val, max_x_val, num=nr_x_values, endpoint=True)

        f2 = interp1d(x_values, y_list, kind='quadratic') #quadratic cubic

        smoothed_data_x = np.linspace(
            min_x_val,
            max_x_val,
            num=num,
            endpoint=True)
    else:
        nr_x_values = len(x_list)
        min_x_val = min(x_list)
        max_x_val = max(x_list)

        x_values = np.linspace(min_x_val, max_x_val, num=nr_x_values, endpoint=True)

        f2 = interp1d(x_values, y_list, kind='cubic')

        smoothed_data_x = np.linspace(
            min_x_val,
            max_x_val,
            num=num,
            endpoint=True)

    smoothed_data_y = f2(smoothed_data_x)

    return smoothed_data_x, smoothed_data_y

def plot_lp_dh_SCRAP(data_dh_modelled):
    x_values = range(24)
    plt.plot(x_values, list(data_dh_modelled), color='red', label='modelled')
    plt.tight_layout()
    plt.margins(x=0)
    plt.show()

def run_all_plot_functions(
        results_container,
        reg_nrs,
        regions,
        lookups,
        result_paths,
        assumptions,
        enduses,
        plot_crit
    ):
    """Summary function to plot all results
    """

    if plot_crit['plot_lad_cross_graphs']:
        # Plot cross graph where very region is a dot
        plot_cross_graphs(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['results_every_year'],
            reg_load_factor_y=results_container['reg_load_factor_y'],
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_cross_graph_electricity_by_cy.pdf"),
            label_points=False,
            plotshow=False)

        plot_cross_graphs(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['results_every_year'],
            reg_load_factor_y=results_container['reg_load_factor_y'],
            fueltype_int=lookups['fueltypes']['gas'],
            fueltype_str='gas',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_cross_graph_gas_by_cy.pdf"),
            label_points=False,
            plotshow=False)

    # ----------
    # Plot LAD differences for first and last year
    # ----------
    try:
        plot_lad_comparison(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['results_every_year'],
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_modelled_electricity_by_cy.pdf"),
            label_points=False,
            plotshow=False)
        print("... plotted by-cy LAD energy demand compariosn")

        # Plot peak h for every hour
        plot_lad_comparison_peak(
            base_yr=2015,
            comparison_year=2050,
            regions=regions,
            ed_year_fueltype_regs_yh=results_container['results_every_year'],
            fueltype_int=lookups['fueltypes']['electricity'],
            fueltype_str='electricity',
            fig_name=os.path.join(
                result_paths['data_results_PDF'], "comparions_LAD_modelled_electricity_peakh_by_cy.pdf"),
            label_points=False,
            plotshow=False)
        print("... plotted by-cy LAD energy demand compariosn")
    except:
        pass

    # ----------------
    # Plot demand for every region over time
    # -------------------
    if plot_crit['plot_line_for_every_region_of_peak_demand']:
        logging.info("... plot fuel per fueltype for every region over annual teimsteps")
        plt_one_fueltype_multiple_regions_peak_h(
            results_container['results_every_year'],
            lookups,
            regions,
            os.path.join(
                result_paths['data_results_PDF'],
                'peak_h_total_electricity.pdf'),
            fueltype_str_to_plot="electricity")

    if plot_crit['plot_fuels_enduses_y']:
        logging.info("... plot fuel per fueltype for whole country over annual timesteps")
        #... Plot total fuel (y) per fueltype as line chart"
        plt_fuels_enduses_y(
            results_container['results_every_year'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'y_fueltypes_all_enduses.pdf'))

    # ------------
    # Plot stacked annual enduses
    # ------------
    if plot_crit['plot_stacked_enduses']:
        logging.info("plot stacked enduses")

        # Residential
        plt_stacked_enduse(
            assumptions['simulated_yrs'],
            results_container['results_enduse_every_year'],
            enduses['rs_enduses'],
            os.path.join(
                result_paths['data_results_PDF'], "stacked_rs_country.pdf"))

        # Service
        plt_stacked_enduse(
            assumptions['simulated_yrs'],
            results_container['results_enduse_every_year'],
            enduses['ss_enduses'],
            os.path.join(
                result_paths['data_results_PDF'], "stacked_ss_country.pdf"))

        # Industry
        plt_stacked_enduse(
            assumptions['simulated_yrs'],
            results_container['results_enduse_every_year'],
            enduses['is_enduses'],
            os.path.join(
                result_paths['data_results_PDF'], "stacked_is_country_.pdf"))

    # ------------------------------
    # Plot annual demand for enduses for all submodels
    # ------------------------------
    if plot_crit['plot_y_all_enduses']:
        logging.info("plot annual demand for enduses for all submodels")
        plt_stacked_enduse_sectors(
            lookups,
            assumptions['simulated_yrs'],
            results_container['results_enduse_every_year'],
            enduses['rs_enduses'],
            enduses['ss_enduses'],
            enduses['is_enduses'],
            os.path.join(result_paths['data_results_PDF'],
            "stacked_all_enduses_country.pdf"))

    # --------------
    # Fuel per fueltype for whole country over annual timesteps
    # ----------------
    if plot_crit['plot_fuels_enduses_y']:
        logging.info("... plot fuel per fueltype for whole country over annual timesteps")
        #... Plot total fuel (y) per fueltype as line chart"
        plt_fuels_enduses_y(
            results_container['results_every_year'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'y_fueltypes_all_enduses.pdf'))

    # ----------
    # Plot seasonal typical load profiles
    # Averaged load profile per daytpe for a region
    # ----------

    # ------------------------------------
    # Load factors per fueltype and region
    # ------------------------------------
    if plot_crit['plot_lf'] :
        for fueltype_str, fueltype_int in lookups['fueltypes'].items():
            logging.info("plot Load factors per fueltype and region")
            plot_seasonal_lf(
                fueltype_int,
                fueltype_str,
                results_container['load_factor_seasons'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'],
                    'lf_seasonal_{}.pdf'.format(fueltype_str)))

            '''plot_lf_y(
                fueltype_int,
                fueltype_str,
                results_container['reg_load_factor_yd'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'], 'lf_yd_{}.pdf'.format(fueltype_str)))'''

            # reg_load_factor_yd = max daily value / average annual daily value
            plot_lf_y(
                fueltype_int,
                fueltype_str,
                results_container['reg_load_factor_y'],
                reg_nrs,
                os.path.join(
                    result_paths['data_results_PDF'],
                    'lf_y_{}.pdf'.format(fueltype_str)))

    # --------------
    # Fuel week of base year
    # ----------------
    if plot_crit['plot_week_h']:
        logging.debug("... plot a full week")
        plt_fuels_enduses_week(
            results_container['results_every_year'],
            lookups,
            assumptions['model_yearhours_nrs'],
            assumptions['model_yeardays_nrs'],
            2015,
            os.path.join(result_paths['data_results_PDF'], "tot_all_enduse03.pdf"))

    # ------------------------------------
    # Plot averaged per season and fueltype
    # ------------------------------------
    if plot_crit['plot_averaged_season_fueltype']:
        base_year = 2015
        for year in results_container['av_season_daytype_cy'].keys():
            for fueltype_int in results_container['av_season_daytype_cy'][year].keys():

                fueltype_str = tech_related.get_fueltype_str(
                    lookups['fueltypes'], fueltype_int)

                plot_load_profile_dh_multiple(
                    path_fig_folder=result_paths['data_results_PDF'],
                    path_plot_fig=os.path.join(
                        result_paths['data_results_PDF'],
                        'season_daytypes_by_cy_comparison__{}__{}.pdf'.format(year, fueltype_str)),
                    calc_av_lp_modelled=results_container['av_season_daytype_cy'][year][fueltype_int],  # current year
                    calc_av_lp_real=results_container['av_season_daytype_cy'][base_year][fueltype_int], # base year
                    calc_lp_modelled=results_container['season_daytype_cy'][year][fueltype_int],        # current year
                    calc_lp_real=results_container['season_daytype_cy'][base_year][fueltype_int],       # base year
                    plot_peak=True,
                    plot_all_entries=False,
                    plot_max_min_polygon=True,
                    plotshow=False,
                    plot_radar=plot_crit['plot_radar_seasonal'],
                    max_y_to_plot=120,
                    fueltype_str=fueltype_str,
                    year=year)

    # ---------------------------------
    # Plot hourly peak loads over time for different fueltypes
    # --------------------------------
    if plot_crit['plot_h_peak_fueltypes']:

        plt_fuels_peak_h(
            results_container['results_every_year'],
            lookups,
            os.path.join(
                result_paths['data_results_PDF'],
                'fuel_fueltypes_peak_h.pdf'))

    print("finisthed plotting")
    return

def order_polygon(upper_boundary, lower_boundary):
    """Create correct sorting to draw filled polygon

    Arguments
    ---------
    upper_boundary
    lower_boundary

    Returns
    -------
    """
    min_max_polygon = []
    for pnt in upper_boundary:
        min_max_polygon.append(pnt)
    for pnt in reversed(lower_boundary):
        min_max_polygon.append(pnt)

    return min_max_polygon

def create_min_max_polygon_from_lines(line_data):
    """

    Arguments
    ---------
    line_data : dict
        linedata containing info
            {'x_value': [y_values]}

    """
    upper_boundary = []
    lower_bdoundary = []

    for x_value, y_value in line_data.items():
        min_y = np.min(y_value)
        max_y = np.max(y_value)
        upper_boundary.append((x_value, min_y))
        lower_bdoundary.append((x_value, max_y))

        # create correct sorting to draw filled polygon
        min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)

    return min_max_polygon

def plot_seasonal_lf(
        fueltype_int,
        fueltype_str,
        load_factors_seasonal,
        reg_nrs,
        path_plot_fig,
        plot_individ_lines=False,
        plot_max_min_polygon=True
    ):
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
    logging.info("... plotting seasonal load factors")

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(8, 8))
    ax = fig.add_subplot(1, 1, 1)

    # Settings
    color_list = {
        'winter': 'midnightblue',
        'summer': 'olive',
        'spring': 'darkgreen',
        'autumn': 'gold'}

    classes = list(color_list.keys())
    #class_colours = list(color_list.values())

    # ------------
    # Iterate regions and plot load factors for every region
    # ------------
    if plot_individ_lines:
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
                    linewidth=0.2,
                    alpha=0.2)

    # -----------------
    # Plot min_max_area
    # -----------------
    if plot_max_min_polygon:

        for season, lf_fueltypes_season in load_factors_seasonal.items():
            upper_boundary = []
            lower_bdoundary = []

            min_max_polygon = plotting_results.create_min_max_polygon_from_lines(lf_fueltypes_season)
            #TODO GOOD
            '''for year_nr, lf_fueltype_reg in lf_fueltypes_season.items():

                # Get min and max of all entries of year of all regions
                min_y = np.min(lf_fueltype_reg[fueltype_int])
                max_y = np.max(lf_fueltype_reg[fueltype_int])
                upper_boundary.append((year_nr, min_y))
                lower_bdoundary.append((year_nr, max_y))

            # create correct sorting to draw filled polygon
            min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)'''

            polygon = plt.Polygon(
                min_max_polygon,
                color=color_list[season],
                alpha=0.2,
                edgecolor=None,
                linewidth=0,
                fill='True')

            ax.add_patch(polygon)

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
            average_season_year_years.append(np.average(average_season_year))

        # plot average
        plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            linewidth=0.5,
            linestyle='--',
            alpha=1.0,
            markersize=0.5,
            marker='o',
            label=season)

        # Plot markers for average line
        '''plt.plot(
            years,
            average_season_year_years,
            color=color_list[season],
            markersize=0.5,
            linewidth=0.5,
            marker='o')'''

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
    ax.set_xticks(minor_ticks, minor=True)
    #ax.set_xlabel(minor_ticks)

    # ------------
    # Plot color legend with colors for every season
    # ------------
    plt.legend(
        ncol=2,
        prop={
            'family': 'arial',
            'size': 5},
        loc='best',
        frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_plot_fig)
    plt.close()

def plot_lf_y(
        fueltype_int,
        fueltype_str,
        reg_load_factor_y,
        reg_nrs,
        path_plot_fig,
        plot_individ_lines=False,
        plot_max_min_polygon=True
    ):
    """Plot load factors per region for every year

    Arguments
    --------

    """
    logging.info("... plotting load factors")

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    if plot_individ_lines:
        # Line plot for every region over years
        for reg_nr in range(reg_nrs):
            x_values_year = []
            y_values_year = []

            for year, lf_fueltype_reg in reg_load_factor_y.items():
                x_values_year.append(year)
                y_values_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

            plt.plot(
                x_values_year,
                y_values_year,
                linewidth=0.2,
                color='grey')

    if plot_max_min_polygon:
        '''lower_bdoundary = []
        upper_boundary = []

        for year_nr, lf_fueltype_reg in reg_load_factor_y.items():

            # Get min and max of all entries of year of all regions
            min_y = np.min(lf_fueltype_reg[fueltype_int])
            max_y = np.max(lf_fueltype_reg[fueltype_int])
            upper_boundary.append((year_nr, min_y))
            lower_bdoundary.append((year_nr, max_y))

        # create correct sorting to draw filled polygon
        min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)'''

        min_max_polygon = plotting_results.create_min_max_polygon_from_lines(reg_load_factor_y)

        polygon = plt.Polygon(
            min_max_polygon,
            color='grey',
            alpha=0.2,
            edgecolor=None,
            linewidth=0,
            fill='True')

        ax.add_patch(polygon)
    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 100)

    # -----------------
    # Axis labelling
    # -----------------
    plt.xlabel("years")
    plt.ylabel("load factor, fueltpye {} [%]".format(fueltype_str))

    years = list(reg_load_factor_y.keys())
    base_yr = 2015

    # Major ticks
    major_interval = 10
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)

    # Minor ticks
    minor_interval = 5
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    plt.savefig(path_plot_fig)
    plt.close()

def plt_stacked_enduse(
        years_simulated,
        results_enduse_every_year,
        enduses_data,
        fig_name
    ):
    """Plots stacked energy demand

    Arguments
    ----------
    years_simulated : list
        Simulated years
    results_enduse_every_year : dict
        Results [year][enduse][fueltype_array_position]

    enduses_data :
    fig_name : str
        Figure name

    Note
    ----
        -   Sum across all fueltypes
        -   Not possible to plot single year

    https://matplotlib.org/examples/pylab_examples/stackplot_demo.html
    """
    nr_of_modelled_years = len(years_simulated)

    x_data = np.array(years_simulated)

    y_value_arrays = []
    legend_entries = []

    for enduse_array_nr, enduse in enumerate(enduses_data):
        legend_entries.append(enduse)

        y_values_enduse_yrs = np.zeros((nr_of_modelled_years))

        for year_array_nr, model_year in enumerate(results_enduse_every_year.keys()):

            # Sum across all fueltypes
            tot_across_fueltypes = np.sum(results_enduse_every_year[model_year][enduse])

            # Conversion: Convert GWh per years to GW
            yearly_sum_twh = conversions.gwh_to_twh(tot_across_fueltypes)

            logging.debug("... model_year {} enduse {}  twh {}".format(
                model_year, enduse, np.sum(yearly_sum_twh)))

            if yearly_sum_twh < 0:
                raise Exception("no minus values allowed {}  {}  {}".format(enduse, yearly_sum_twh, model_year))

            y_values_enduse_yrs[year_array_nr] = yearly_sum_twh

        # Add array with values for every year to list
        y_value_arrays.append(y_values_enduse_yrs)

    # Convert to stacked
    y_stacked = np.row_stack((y_value_arrays))

    # Set figure size
    fig = plt.figure(
        figsize=plotting_program.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    color_list = plotting_styles.color_list_scenarios()

    # ----------
    # Stack plot
    # ----------
    color_stackplots = color_list[:len(enduses_data)]

    ax.stackplot(
        x_data,
        y_stacked,
        colors=color_stackplots)

    plt.legend(
        legend_entries,
        prop={
            'family':'arial',
            'size': 5},
        ncol=2,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False,
        shadow=True)

    # -------
    # Axis
    # -------
    plt.xticks(years_simulated, years_simulated)

    # -------
    # Labels
    # -------
    plt.ylabel("TWh", fontsize=10)
    plt.xlabel("Year", fontsize=10)
    plt.title("ED whole UK", fontsize=10)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(fig_name)
    plt.close()

def plt_stacked_enduse_sectors(
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
    x_data = years_simulated
    nr_submodels = 3
    y_data = np.zeros((nr_submodels, len(years_simulated)))

    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(8, 8))

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

    ##import matplotlib.colors as colors #for color_name in colors.cnmaes:
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
    leg_labels = ['residential', 'service', 'industry']

    plt.legend(
        leg_labels,
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

def plot_load_curves_fueltype(results_objects, data, fig_name, plotshow=False):
    """Plots stacked end_use for a region
    # INFO Cannot plot a single year?
    """
    fig, ax = plt.subplots()
    nr_y_to_plot = len(results_objects) #number of simluated years

    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((data['lookups']['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype_int in data['lookups']['fueltypes'].items():

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

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot))
    plt.axis('tight')

    plt.ylabel("Percent %")
    plt.xlabel("Simulation years")
    plt.title("Load factor of maximum hour across all enduses")

    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plt_fuels_enduses_week(
        results_resid,
        lookups,
        nr_of_h_to_plot,
        model_yeardays_nrs,
        year_to_plot,
        fig_name
    ):
    """Plots stacked end_use for all regions. As
    input GWh per h are provided, which cancels out to
    GW.

    Arguments
    ---------
    year_to_plot : int
        2015 --> 0

    # INFO Cannot plot a single year?
    """
    days_to_plot = range(model_yeardays_nrs)

    fig, ax = plt.subplots()

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((lookups['fueltypes_nr'], nr_of_h_to_plot))

    for fueltype_str, fueltype_int in lookups['fueltypes'].items():
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

    plt.legend(
        ncol=2,
        frameon=False,
        prop={
            'family': 'arial',
            'size': 10},)

    plt.ylabel("GW")
    plt.xlabel("day")
    plt.title("tot annual ED, all enduses, fueltype {}".format(year_to_plot + 2050))

    plt.savefig(fig_name)
    plt.close()

def plt_fuels_enduses_y(results, lookups, fig_name, plotshow=False):
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
    # Set figure size
    plt.figure(figsize=plotting_program.cm2inch(14, 8))

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

    for counter, (fueltype_str, fuel_fueltype_yrs) in enumerate(y_values_fueltype.items()):

        plt.plot(
            list(fuel_fueltype_yrs.keys()),     # years
            list(fuel_fueltype_yrs.values()),   # yearly data per fueltype
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

def plt_fuels_peak_h(results_every_year, lookups, path_plot_fig):
    """Plots

    Plot peak hour per fueltype over time for 

    Arguments
    ---------
    tot_fuel_dh_peak : dict
        year, fueltype, peak_dh

    """
    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(14, 8))
    ax = fig.add_subplot(1, 1, 1)

    nr_y_to_plot = len(results_every_year)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((lookups['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype in lookups['fueltypes'].items():
        fueltype_int = tech_related.get_fueltype_int(lookups['fueltypes'], fueltype_str)

        # Legend
        legend_entries.append(fueltype_str)

        # Read out fueltype specific load
        data_over_years = []
        for model_year_object in results_every_year.values():

            # Sum fuel across all regions
            fuel_all_regs = np.sum(model_year_object, axis=1) # (fueltypes, 8760 hours)

            # Get peak day across all enduses for every region
            _, gw_peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(fuel_all_regs[fueltype_int])

            # Add peak hour
            data_over_years.append(gw_peak_fueltyp_h)

        y_init[fueltype] = data_over_years

    # ----------
    # Plot lines
    # ----------
    #linestyles = plotting_styles.linestyles()

    years = list(results_every_year.keys())
    for fueltype, _ in enumerate(y_init):
        plt.plot(
            years,
            y_init[fueltype],
            #linestyle=linestyles[fueltype],
            linewidth=0.7)

    ax.legend(
        legend_entries,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # -
    # Axis
    # -
    base_yr = 2015
    major_interval = 10
    minor_interval = 5

    # Major ticks
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)

    # Minor ticks
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    plt.xlim(2015, years[-1])

    # --------
    # Labeling
    # --------
    plt.ylabel("GW")
    plt.xlabel("year")
    plt.title("ED peak hour, y, all enduses and regions")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    fig.savefig(path_plot_fig)
    plt.close()

def plot_load_profile_dh_multiple(
        path_fig_folder,
        path_plot_fig,
        calc_av_lp_modelled,
        calc_av_lp_real,
        calc_lp_modelled=None,
        calc_lp_real=None,
        plot_peak=False,
        plot_radar=False,
        plot_all_entries=False,
        plot_max_min_polygon=True,
        plotshow=False,
        max_y_to_plot=60,
        fueltype_str=False,
        year=False
    ):
    """Plotting average saisonal loads for each daytype. As an input
    GWh is provided, which for each h is cancelled out to GW.

    https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
    http://matthiaseisen.com/matplotlib/shapes/reg-polygon/
    """
    fig = plt.figure(
        figsize=plotting_program.cm2inch(14, 25))
    
    ax = fig.add_subplot(
        nrows=4,
        ncols=2)

    plot_nr = 0
    row = -1
    for season in calc_av_lp_modelled:
        row += 1
        col = -1
        for daytype in calc_av_lp_modelled[season]:
            col += 1
            plot_nr += 1

            axes = plt.subplot(4, 2, plot_nr)

            # ------------------
            # Plot average
            # ------------------
            x_values = range(24)

            plt.plot(
                x_values,
                list(calc_av_lp_real[season][daytype]),
                color='black',
                label='av_real or av by',
                linestyle='--',
                linewidth=0.5)

            plt.plot(
                x_values,
                list(calc_av_lp_modelled[season][daytype]),
                color='blue',
                label='av_modelled or av cy',
                linestyle='--',
                linewidth=0.5)

            # --------------
            # Radar plots
            # --------------
            if plot_radar:
                name_spider_plot = os.path.join(
                    path_fig_folder,
                    "spider_{}_{}_{}_{}_.pdf".format(
                        year,
                        fueltype_str,
                        season,
                        daytype))

                plot_radar_plot(
                    list(calc_av_lp_modelled[season][daytype]),
                    name_spider_plot,
                    plot_steps=20,
                    plotshow=False)

            # ------------------
            # Plot every single line
            # ------------------
            if plot_all_entries:
                for entry in range(len(calc_lp_real[season][daytype])):
                    plt.plot(
                        x_values,
                        list(calc_lp_real[season][daytype][entry]),
                        color='grey',
                        markersize=0.5,
                        alpha=0.2)

                    plt.plot(
                        x_values,
                        list(calc_lp_modelled[season][daytype][entry]),
                        color='blue',
                        markersize=0.5,
                        alpha=0.2)

            # ----------
            # Plot max_min range polygons
            # ----------
            if plot_max_min_polygon:

                # ----Draw real
                min_max_polygon = []
                upper_boundary = []
                lower_bdoundary = []

                # Get min and max of all entries for hour
                for hour in range(24):
                    min_y = np.min(calc_lp_real[season][daytype][:, hour], axis=0)
                    max_y = np.max(calc_lp_real[season][daytype][:, hour], axis=0)
                    upper_boundary.append((hour, min_y))
                    lower_bdoundary.append((hour, max_y))

                # create correct sorting to draw filled polygon
                min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)
                #min_max_polygon = plotting_results.create_min_max_polygon_from_lines(reg_load_factor_y)

                polygon = plt.Polygon(
                    min_max_polygon,
                    color='grey',
                    alpha=0.2,
                    edgecolor=None,
                    linewidth=0,
                    fill='True')

                axes.add_patch(polygon)

                # -----Draw modelled
                min_max_polygon = []
                upper_boundary = []
                lower_bdoundary = []

                # Get min and max of all entries for hour
                for hour in range(24):
                    min_y = np.min(calc_lp_modelled[season][daytype][:, hour], axis=0)
                    max_y = np.max(calc_lp_modelled[season][daytype][:, hour], axis=0)
                    upper_boundary.append((hour, min_y))
                    lower_bdoundary.append((hour, max_y))

                # create correct sorting to draw filled polygon
                min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)

                polygon = plt.Polygon(
                    min_max_polygon,
                    color='blue',
                    alpha=0.2,
                    edgecolor=None,
                    linewidth=0,
                    fill='True')

                axes.add_patch(polygon)

            # --------------------
            # Get load shape within season with highest houly load
            # --------------------
            if plot_peak:

                # Get row with maximum hourly value
                day_with_max_h = np.argmax(np.max(calc_lp_real[season][daytype], axis=1))

                plt.plot(
                    x_values,
                    list(calc_lp_real[season][daytype][day_with_max_h]),
                    color='grey',
                    markersize=1.0,
                    label='real_peak or by peak',
                    linestyle='-.',
                    linewidth=0.5)

                # Get row with maximum hourly value
                day_with_max_h = np.argmax(np.max(calc_lp_modelled[season][daytype], axis=1))

                plt.plot(
                    x_values,
                    list(calc_lp_modelled[season][daytype][day_with_max_h]),
                    color='blue',
                    markersize=1.0,
                    label='modelled_peak or cy peak',
                    linestyle='-.',
                    linewidth=0.5)

            # -----------------
            # Axis
            # -----------------
            plt.ylim(0, max_y_to_plot)
            plt.xlim(0, 23)

            # Tight layout
            plt.tight_layout()
            plt.margins(x=0)

            # Calculate RMSE
            rmse = basic_functions.rmse(
                calc_av_lp_modelled[season][daytype],
                calc_av_lp_real[season][daytype])

            # Calculate R_squared
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                calc_av_lp_modelled[season][daytype],
                calc_av_lp_real[season][daytype])

            # Calculate standard deviation
            std_dev_p = np.std(calc_av_lp_real[season][daytype] - calc_av_lp_modelled[season][daytype])
            std_dev_abs = np.std(abs(calc_av_lp_real[season][daytype] - calc_av_lp_modelled[season][daytype]))

            # -----------
            # Labelling
            # -----------
            font_additional_info = plotting_styles.font_info()

            title_info = ('{}, {}'.format(season, daytype))
            plt.text(1, 0.55, "RMSE: {}, R_squared: {}, std: {} (+- {})".format(
                round(rmse, 2),
                round(r_value, 2),
                round(std_dev_p, 2),
                round(std_dev_abs, 2),
                fontdict=font_additional_info))
            plt.title(title_info, loc='left', fontdict=font_additional_info)
            #plt.ylabel("hours")
            #plt.ylabel("average electricity [GW]")

    # ------------
    # Plot legend
    # ------------
    plt.legend(
        ncol=1,
        loc=2,
        prop={
            'family': 'arial',
            'size': 5},
        frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    fig.savefig(path_plot_fig)

    if plotshow:
        plt.show()
        plt.close()
    else:
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


def plot_lp_dh(data_dh_modelled, path_plot_fig, fig_name):
    """plot daily profile
    """
    x_values = range(24)

    plt.plot(x_values, list(data_dh_modelled), color='red', label='modelled') #'ro', markersize=1,

    path_fig_name = os.path.join(
        path_plot_fig,
        fig_name)

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 30)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_fig_name)
    plt.close()

def plot_lp_yh(data_dh_modelled, plotshow=False):
    """plot yearly profile
    """
    x_values = range(8760)

    yh_data_dh_modelled = np.reshape(data_dh_modelled, 8760)
    plt.plot(x_values, list(yh_data_dh_modelled), color='red', label='modelled') #'ro', markersize=1,

    # -----------------
    # Axis
    # -----------------
    #plt.ylim(0, 30)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_lp_yd(data_dh_modelled, plotshow=False):
    """plot yearly profile
    """
    def close_event():
        """Timer to close window automatically
        """
        plt.close()

    fig = plt.figure()
    x_values = range(365)

    plt.plot(x_values, data_dh_modelled, color='blue', label='modelled') #'ro', markersize=1,

    # -----------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

    #creating a timer object and setting an interval
    timer = fig.canvas.new_timer(interval = 1500)
    timer.add_callback(close_event)

def plot_enduse_yh(
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
    fig = plt.figure(figsize=plotting_program.cm2inch(16, 8))

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

def plot_lad_comparison_peak(
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
        figsize=plotting_program.cm2inch(9, 8)) #width, height

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
        figsize=plotting_program.cm2inch(9, 8)) #width, height

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

def plot_radar_plot(dh_profile, fig_name, plot_steps=30, plotshow=False):
    """Plot daily load profile on a radar plot

    Arguments
    ---------
    dh_profile : list
        Dh values to plot
    fig_name : str
        Path to save figure

    SOURCE: https://python-graph-gallery.com/390-basic-radar-chart/
    """

    # Get maximum demand
    max_entry = np.array(dh_profile).max()
    max_demand = round(max_entry, -1) + 10 # Round to nearest 10 plus add 10
    max_demand = 120 #SCRAP

    nr_of_plot_steps = int(max_demand / plot_steps) + 1

    axis_plots_inner = []
    axis_plots_innter_position = []

    # Innter ciruclar axis
    for i in range(nr_of_plot_steps):
        axis_plots_inner.append(plot_steps*i)
        axis_plots_innter_position.append(str(plot_steps*i))

    # ---------
    data = {
        'dh_profile': ['testname']}

    for hour in range(24):

        # Key: Label outer circle
        data[hour] = dh_profile[hour]

    # Set data
    df = pd.DataFrame(data)

    # number of variable
    categories=list(df)[1:]
    N = len(categories)

    # We are going to plot the first line of the data frame.
    # But we need to repeat the first value to close the circular graph:
    values=df.loc[0].drop('dh_profile').values.flatten().tolist()
    values += values[:1]

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    # Change circula axis
    ax.yaxis.grid(color='lightgrey', linestyle='--', linewidth=0.8, alpha=0.8) # Circular axis
    ax.xaxis.grid(color='lightgrey', linestyle='--', linewidth=0.8, alpha=0.8) # Regular axis

    # Change to clockwise cirection
    ax.set_theta_direction(-1)
    #ax.set_theta_offset(pi/2.0)

    # Set first hour on top
    ax.set_theta_zero_location("N")

    # Draw one axe per variable + add labels labels yet
    plt.xticks(
        angles[:-1],
        categories,
        color='grey',
        size=8)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(
        axis_plots_inner,
        axis_plots_innter_position,
        color="grey",
        size=7)

    # Set limit to size
    plt.ylim(0, max_demand)

    # Plot data
    ax.plot(
        angles,
        values,
        linestyle='--',
        linewidth=0.5)

    ax.fill(
        angles,
        values,
        'blue', #b
        alpha=0.1)

    # Save fig
    print("fig_name: " + str(fig_name))
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

def plot_radar_plot_multiple_lines(
        dh_profiles,
        fig_name,
        plot_steps,
        scenario_names,
        plotshow=False,
        lf_y_by=None,
        lf_y_cy=None,
        list_diff_max_h=None
    ):
    """Plot daily load profile on a radar plot

    Arguments
    ---------
    dh_profile : list
        Dh values to plot
    fig_name : str
        Path to save figure

    SOURCE: https://python-graph-gallery.com/390-basic-radar-chart/
    """
    fig = plt.figure(
        figsize=plotting_program.cm2inch(9, 14))

    # Get maximum demand of all lines
    max_entry = 0
    for line_entries in dh_profiles:
        max_in_line = max(line_entries)
        if max_in_line > max_entry:
            max_entry = max_in_line

    max_demand = round(max_entry, -1) + 10 # Round to nearest 10 plus add 10

    nr_of_plot_steps = int(max_demand / plot_steps) + 1

    axis_plots_inner = []
    axis_plots_innter_position = []

    # --------------------
    # Ciruclar axis
    # --------------------
    for i in range(nr_of_plot_steps):
        axis_plots_inner.append(plot_steps*i)
        axis_plots_innter_position.append(str(plot_steps*i))

    # Minor ticks
    minor_tick_interval = plot_steps / 2
    minor_ticks = []
    for i in range(nr_of_plot_steps * 2):
        minor_ticks.append(minor_tick_interval * i)

    # Colors with scenarios
    color_scenarios = plotting_styles.color_list_scenarios()

    # Colors for plotting Fig. 13
    color_scenarios = plotting_styles.color_list_selection()

    color_lines = ['black'] + color_scenarios
    years = ['2015', '2050']
    linewidth_list = [1.0, 0.7]
    linestyle_list = ['-', '--']
    scenario_names.insert(0, "any")

    # Iterate lines
    cnt = -1
    for dh_profile in dh_profiles:

        if cnt >= 0:
            cnt_year = 1
        else:
            cnt_year = 0
        cnt += 1

        # Line properties
        color_line = color_lines[cnt]
        year_line = years[cnt_year]

        data = {'dh_profile': ['testname']}

        # Key: Label outer circle
        for hour in range(24):
            data[hour] = dh_profile[hour]

        # Set data
        df = pd.DataFrame(data)

        # number of variable
        categories = list(df)[1:]
        N = len(categories)

        # We are going to plot the first line of the data frame.
        # But we need to repeat the first value to close the circular graph:
        values = df.loc[0].drop('dh_profile').values.flatten().tolist()
        values += values[:1]

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        ax = plt.subplot(111, polar=True)

        # Change axis properties
        ax.yaxis.grid(color='grey', linestyle=':', linewidth=0.4)
        ax.xaxis.grid(color='lightgrey', linestyle=':', linewidth=0.4)

        # Change to clockwise cirection
        ax.set_theta_direction(-1)

        # Set first hour on top
        ax.set_theta_zero_location("N")

        # Draw one axe per variable + add labels labels yet (numbers)
        plt.xticks(
            angles[:-1],
            categories,
            color='black',
            size=8)

        # Draw ylabels (numbers)
        ax.set_rlabel_position(0)

        # Working alternative
        plt.yticks(
            axis_plots_inner,
            axis_plots_innter_position,
            color="black",
            size=8)

        #ax.set_yticks(axis_plots_inner, minor=False)
        #ax.tick_params(axis='y', pad=35) 
        #ax.set_yticks(minor_ticks, minor=True) #Somehow not working

        # Set limit to size
        plt.ylim(0, max_demand)
        plt.ylim(0, nr_of_plot_steps*plot_steps)

        # Smooth lines
        angles_smoothed, values_smoothed = plotting_results.smooth_data(
            angles, values, spider=True)

        # Plot data
        ax.plot(
            angles_smoothed,
            values_smoothed,
            color=color_line,
            linestyle=linestyle_list[cnt_year],
            linewidth=linewidth_list[cnt_year],
            label="{} {}".format(year_line, scenario_names[cnt]))

        # Radar area
        ax.fill(
            angles_smoothed,
            values_smoothed,
            color_line,
            alpha=0.05)

    font_additional_info = plotting_styles.font_info(size=5)

    for cnt, entry in enumerate(list_diff_max_h):
        plt.text(
            0.25,
            0 + cnt/50,
            entry,
            fontdict=font_additional_info,
            transform=plt.gcf().transFigure)

    # ------------
    # Title
    # ------------
    font_additional_info = plotting_styles.font_info(size=4)
    #plt.title(
    #    title_info,
    #    loc='left',
    #    fontdict=font_additional_info)

    # ------------
    # Legend
    # ------------
    plt.legend(
        ncol=1,
        bbox_to_anchor=(0.5, -0.1),
        prop={
            'family': 'arial',
            'size': 4},
        frameon=False)

    plt.savefig(fig_name)

    if plotshow:
        plt.show()

    plt.close()

def plt_one_fueltype_multiple_regions_peak_h(
        results_every_year,
        lookups,
        regions,
        path_plot_fig,
        fueltype_str_to_plot
    ):
    """Plot
    Arguments
    ---------
    """
    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(14, 8))

    ax = fig.add_subplot(1, 1, 1)

    nr_y_to_plot = len(results_every_year)

    legend_entries = []

    for fueltype_str, fueltype in lookups['fueltypes'].items():

        if fueltype_str != fueltype_str_to_plot:
            pass
        else:
            # Legend
            #legend_entries.append(fueltype_str)

            # Read out fueltype specific load
            data_over_years = {}
            for reg_nr, reg_geocode in enumerate(regions):
                data_over_years[reg_nr] = []

            for model_year_object in results_every_year.values():

                for reg_nr, reg_geocode in enumerate(regions):

                    # Get peak hour value
                    _, peak_fueltyp_h = enduse_func.get_peak_day_single_fueltype(model_year_object[fueltype][reg_nr])

                    # Add peak hour
                    data_over_years[reg_nr].append(peak_fueltyp_h)
                    #_scrap += np.sum(peak_fueltyp_h)
    
            y_init = data_over_years

    # ----------
    # Plot lines
    # ----------
    linestyles = plotting_styles.linestyles()
    years = list(results_every_year.keys())
    #color_list_selection = plotting_styles.color_list_selection()

    for reg in y_init:
        plt.plot(
            years,
            y_init[reg],
            #linestyle=linestyles[fueltype],
            color='lightblue',
            linewidth=0.2,)

    ax.legend(
        legend_entries,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)

    # -
    # Axis
    # -
    base_yr = 2015
    major_interval = 10
    minor_interval = 5

    # Major ticks
    major_ticks = np.arange(base_yr, years[-1] + major_interval, major_interval)
    ax.set_xticks(major_ticks)

    # Minor ticks
    minor_ticks = np.arange(base_yr, years[-1] + minor_interval, minor_interval)
    ax.set_xticks(minor_ticks, minor=True)

    plt.xlim(2015, years[-1])

    # --------
    # Labeling
    # --------
    plt.ylabel("GW")
    plt.xlabel("year")
    plt.title("ED peak hour, y, all enduses, single regs")

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    fig.savefig(path_plot_fig)
    plt.close()

def plot_cross_graphs(
        base_yr,
        comparison_year,
        regions,
        ed_year_fueltype_regs_yh,
        reg_load_factor_y,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points,
        plotshow):

    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand
    # -------------------------------------------
    for year, fuels in ed_year_fueltype_regs_yh.items():

        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_by'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_by'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_by_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0)# Sum across all regions
            result_dict['peak_h_demand_by_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_by_all_regs_av'] = load_factor_y[fueltype_int]

        elif year == comparison_year:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_cy'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_cy'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_cy_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0) # Sum across all regions
            result_dict['peak_h_demand_cy_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_cy_all_regs_av'] = load_factor_y[fueltype_int]
        else:
            pass

    # Get load factor
    for year, lf_fueltype_regs in reg_load_factor_y.items():

        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_by'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]

        elif year == comparison_year:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_cy'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]
        else:
            pass

    labels = []

    #Base year
    x_values, y_values = [], []
    x_values_0_quadrant, y_values_0_quadrant = [], []
    x_values_1_quadrant, y_values_1_quadrant = [], []
    x_values_2_quadrant, y_values_2_quadrant = [], []
    x_values_3_quadrant, y_values_3_quadrant = [], []

    for reg_nr, reg_geocode in enumerate(regions):

        # Change in load factor
        lf_change_p = ((100 / result_dict['lf_by'][reg_geocode]) * result_dict['lf_cy'][reg_geocode]) - 100

        # Change in peak h deman
        demand_peak_h_p = ((100 / result_dict['peak_h_demand_by'][reg_geocode]) * result_dict['peak_h_demand_cy'][reg_geocode]) - 100

        # Change in total regional demand
        tot_demand_p = ((100 / result_dict['demand_by'][reg_geocode]) * result_dict['demand_cy'][reg_geocode]) - 100

        x_values.append(lf_change_p)
        #y_values.append(tot_demand_p)
        y_values.append(demand_peak_h_p)

        labels.append(reg_geocode)

        if lf_change_p < 0 and tot_demand_p > 0:
            x_values_0_quadrant.append(lf_change_p)
            y_values_0_quadrant.append(tot_demand_p)
        elif lf_change_p > 0 and tot_demand_p > 0:
            x_values_1_quadrant.append(lf_change_p)
            y_values_1_quadrant.append(tot_demand_p)
        elif lf_change_p > 0 and tot_demand_p < 0:
            x_values_2_quadrant.append(lf_change_p)
            y_values_2_quadrant.append(tot_demand_p)
        else:
            x_values_3_quadrant.append(lf_change_p)
            y_values_3_quadrant.append(tot_demand_p)

    # Add average
    national_tot_cy_p = ((100 / result_dict['lf_by_all_regs_av']) * result_dict['lf_cy_all_regs_av']) - 100
    #national_tot_demand_p = ((100 / result_dict['demand_by_all_regs']) * result_dict['demand_cy_all_regs']) - 100
    national_peak_h_p = ((100 / result_dict['peak_h_demand_by_all_regs']) * result_dict['peak_h_demand_cy_all_regs']) - 100

    x_val_national_lf_demand_cy = [national_tot_cy_p]
    #y_val_national_lf_demand_cy = [national_tot_demand_p]
    y_val_national_lf_demand_cy = [national_peak_h_p]

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(
        figsize=plotting_program.cm2inch(9, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(
        x_values_0_quadrant,
        y_values_0_quadrant,
        alpha=0.6,
        color='rosybrown',
        s=8)
    ax.scatter(
        x_values_1_quadrant,
        y_values_1_quadrant,
        alpha=0.6,
        color='firebrick',
        s=8)
    ax.scatter(
        x_values_2_quadrant,
        y_values_2_quadrant,
        alpha=0.6,
        color='forestgreen',
        s=8)
    ax.scatter(
        x_values_3_quadrant,
        y_values_3_quadrant,
        alpha=0.6,
        color='darkolivegreen',
        s=8)

    # Add average
    ax.scatter(
        x_val_national_lf_demand_cy,
        y_val_national_lf_demand_cy,
        alpha=1.0,
        color='black',
        s=20,
        marker="v",
        linewidth=0.5,
        edgecolor='black',
        label='national')

    # --------
    # Axis
    # --------
    ax.set_xlabel("load factor change (%) {}".format(fueltype_str))
    ax.set_ylabel("change in peak h (%) {}".format(fueltype_str))

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='on') # labels along the bottom edge are off

    # --------
    # Grd
    # --------
    ax.set_axisbelow(True)
    ax.set_xticks([0], minor=True)
    ax.set_yticks([0], minor=True)
    ax.yaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')
    ax.xaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')

    # Limit
    #plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_values[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=6)
    # --------
    # Legend
    # --------
    '''legend(
        loc=3,
        prop={
            'family': 'arial',
            'size': 8},
        frameon=False)'''

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    plt.close()

def plot_cross_graphs_scenarios(
        base_yr,
        comparison_year,
        regions,
        scenario_data,
        fueltype_int,
        fueltype_str,
        fig_name,
        label_points,
        plotshow):

    result_dict = defaultdict(dict)

    # -------------------------------------------
    # Get base year modelled demand of any scenario (becasue base year the same in every scenario)
    # -------------------------------------------$
    all_scenarios = list(scenario_data.keys())
    first_scenario = all_scenarios[0]
    ed_year_fueltype_regs_yh = scenario_data[first_scenario]['results_every_year']

    for year, fuels in ed_year_fueltype_regs_yh.items():

        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['demand_by'][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                result_dict['peak_h_demand_by'][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

            # Demand across all regs
            result_dict['demand_by_all_regs'] = np.sum(fuels[fueltype_int])

            # Peak demand
            fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0)# Sum across all regions
            result_dict['peak_h_demand_by_all_regs'] = np.max(fuel_all_reg_yh)

            # Calculate national load factor
            fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
            load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
            result_dict['lf_by_all_regs_av'] = load_factor_y[fueltype_int]

    for scenario, data in scenario_data.items():
        result_dict['demand_cy'][scenario] = {}
        result_dict['peak_h_demand_cy'][scenario] = {}

        for year, fuels in data['results_every_year'].items():
            if year == comparison_year:
                for reg_nr, reg_geocode in enumerate(regions):
                    result_dict['demand_cy'][scenario][reg_geocode] = np.sum(fuels[fueltype_int][reg_nr])
                    result_dict['peak_h_demand_cy'][scenario][reg_geocode] = np.max(fuels[fueltype_int][reg_nr])

                # Demand across all regs
                result_dict['demand_cy_all_regs'][scenario] = np.sum(fuels[fueltype_int])

                # Peak demand
                fuel_all_reg_yh = np.sum(fuels[fueltype_int], axis=0) # Sum across all regions
                result_dict['peak_h_demand_cy_all_regs'][scenario] = np.max(fuel_all_reg_yh)

                # Calculate national load factor
                fuel_all_fueltype_reg_yh = np.sum(fuels, axis=1)# Sum across all regions per fueltype
                load_factor_y = load_factors.calc_lf_y(fuel_all_fueltype_reg_yh)
                result_dict['lf_cy_all_regs_av'][scenario] = load_factor_y[fueltype_int]
            else:
                pass

    # Get load factor of base year
    reg_load_factor_y = scenario_data[first_scenario]['reg_load_factor_y']
    for year, lf_fueltype_regs in reg_load_factor_y.items():
        if year == base_yr:
            for reg_nr, reg_geocode in enumerate(regions):
                result_dict['lf_by'][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]

    for scenario, data in scenario_data.items():
        reg_load_factor_y = scenario_data[scenario]['reg_load_factor_y']
        result_dict['lf_cy'][scenario] = {}

        for year, lf_fueltype_regs in reg_load_factor_y.items():
            if year == comparison_year:
                for reg_nr, reg_geocode in enumerate(regions):
                    result_dict['lf_cy'][scenario][reg_geocode] = lf_fueltype_regs[fueltype_int][reg_nr]
            else:
                pass

    # --------------------------
    # Iterate scenario and plot
    # --------------------------
    fig = plt.figure(
        figsize=plotting_program.cm2inch(18, 8)) #width, height

    ax = fig.add_subplot(1, 1, 1)

    color_list = plotting_styles.color_list_scenarios()
    marker_list = plotting_styles.marker_list()
    '''color_list = [
        'forestgreen',
        'rosybrown',
        'blue',
        'darkolivegreen',
        'firebrick']'''
    all_x_values = []
    all_y_values = []

    for scenario_nr, scenario in enumerate(all_scenarios):

        labels = []

        #Base year
        x_values, y_values = [], []

        for reg_nr, reg_geocode in enumerate(regions):

            # Change in load factor
            lf_change_p = ((100 / result_dict['lf_by'][reg_geocode]) * result_dict['lf_cy'][scenario][reg_geocode]) - 100

            # Change in peak h deman
            demand_peak_h_p = ((100 / result_dict['peak_h_demand_by'][reg_geocode]) * result_dict['peak_h_demand_cy'][scenario][reg_geocode]) - 100

            # Change in total regional demand
            tot_demand_p = ((100 / result_dict['demand_by'][reg_geocode]) * result_dict['demand_cy'][scenario][reg_geocode]) - 100

            x_values.append(lf_change_p)
            #y_values.append(tot_demand_p)
            y_values.append(demand_peak_h_p)

            labels.append(reg_geocode)

        # Add average
        national_tot_cy_p = ((100 / result_dict['lf_by_all_regs_av']) * result_dict['lf_cy_all_regs_av'][scenario]) - 100
        #national_tot_demand_p = ((100 / result_dict['demand_by_all_regs']) * result_dict['demand_cy_all_regs'][scenario]) - 100
        national_peak_h_p = ((100 / result_dict['peak_h_demand_by_all_regs']) * result_dict['peak_h_demand_cy_all_regs'][scenario]) - 100

        x_val_national_lf_demand_cy = [national_tot_cy_p]
        #y_val_national_lf_demand_cy = [national_tot_demand_p]
        y_val_national_lf_demand_cy = [national_peak_h_p]

        all_x_values += x_values
        all_y_values += y_values
        # -------------------------------------
        # Plot
        # -------------------------------------
        color = color_list[scenario_nr]
        marker = marker_list[scenario_nr]

        alpha_value = 0.6
        marker_size = 7
        ax.scatter(
            x_values,
            y_values,
            alpha=alpha_value,
            color=color,
            #marker=marker,
            edgecolor=color,
            linewidth=0.5,
            s=marker_size,
            label=scenario)

        # Add average
        ax.scatter(
            x_val_national_lf_demand_cy,
            y_val_national_lf_demand_cy,
            alpha=1.0,
            color=color,
            s=20,
            marker="v",
            linewidth=0.5,
            edgecolor='black',
            label='national')

    # --------
    # Axis
    # --------
    ax.set_xlabel("load factor change (%) {}".format(fueltype_str))
    ax.set_ylabel("change in peak h (%) {}".format(fueltype_str))

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='on') # labels along the bottom edge are off

    # --------
    # Grd
    # --------
    ax.set_axisbelow(True)
    #ax.grid(True)
    #ax.set_xticks(minor=False)
    ax.set_xticks([0], minor=True)
    #ax.set_yticks(minor=False)
    ax.set_yticks([0], minor=True)
    #ax.yaxis.grid(True, which='major')
    ax.yaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')
    #ax.xaxis.grid(True, which='major')
    ax.xaxis.grid(True, which='minor', linewidth=0.7, color='grey', linestyle='--')

    # Limit
    #plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):
            ax.text(
                x_values[pos],
                y_values[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=6)

    # -------
    # Title information
    # -------
    max_lf = round(max(all_x_values), 2)
    min_lf = round(min(all_x_values), 2)
    min_peak_h = round(min(all_y_values), 2)
    max_peak_h = round(max(all_y_values), 2)

    font_additional_info = plotting_styles.font_info(size=4)

    plt.title(
        "max_peak_h: {} min_peak_h: {}, min_lf: {} max_lf: {}".format(
            max_peak_h,
            min_peak_h,
            min_lf,
            max_lf),
        fontdict=font_additional_info)

    # --------
    # Legend
    # --------
    plt.legend(
        loc='best',
        ncol=1,
        prop={
            'family': 'arial',
            'size': 3},
        frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(fig_name)

    if plotshow:
        plt.show()
    plt.close()
