"""Plotting model results and storing as PDF to result folder
"""
import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions, conversions
from matplotlib.patches import Rectangle
from energy_demand.plotting import plotting_styles
from energy_demand.technologies import tech_related
from scipy import stats

# INFO
# https://stackoverflow.com/questions/35099130/change-spacing-of-dashes-in-dashed-line-in-matplotlib
# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781849513265/4/ch04lvl1sec56/using-a-logarithmic-scale
# Setting x labels: https://matplotlib.org/examples/pylab_examples/major_minor_demo1.html

def plot_lp_dh_SCRAP(data_dh_modelled):
    x_values = range(24)
    plt.plot(x_values, list(data_dh_modelled), color='red', label='modelled')
    plt.tight_layout()
    plt.margins(x=0)
    plt.show()

def order_polygon(upper_boundary, lower_bdoundary):
    """create correct sorting to draw filled polygon
    """
    min_max_polygon = []
    for pnt in upper_boundary:
        min_max_polygon.append(pnt)
    for pnt in reversed(lower_bdoundary):
        min_max_polygon.append(pnt)
    return min_max_polygon

def run_all_plot_functions(
        results_container,
        reg_nrs,
        lookups,
        local_paths,
        assumptions,
        sim_param,
        enduses
    ):
    """Summary function to plot all results
    """
    logging.info("... plotting results")
    print("... plotting results")

    # ------------
    # Plot stacked annual enduses
    # ------------
    # Residential
    plt_stacked_enduse(
        sim_param['simulated_yrs'],
        results_container['results_enduse_every_year'],
        enduses['rs_all_enduses'],
        os.path.join(
            local_paths['data_results_PDF'],"stacked_rs_country.pdf"))

    # Service
    plt_stacked_enduse(
        sim_param['simulated_yrs'],
        results_container['results_enduse_every_year'],
        enduses['ss_all_enduses'],
        os.path.join(
            local_paths['data_results_PDF'], "stacked_ss_country.pdf"))

    # Industry
    plt_stacked_enduse(
        sim_param['simulated_yrs'],
        results_container['results_enduse_every_year'],
        enduses['is_all_enduses'],
        os.path.join(
            local_paths['data_results_PDF'], "stacked_is_country_.pdf"))

    # ------------------------------
    # Plot annual demand for enduses for all submodels
    # ------------------------------
    #TODO IMPROVE WITH OTHER STACK
    plt_stacked_enduse_sectors(
        lookups,
        sim_param['simulated_yrs'],
        results_container['results_enduse_every_year'],
        enduses['rs_all_enduses'],
        enduses['ss_all_enduses'],
        enduses['is_all_enduses'],
        os.path.join(local_paths['data_results_PDF'],
        "stacked_all_enduses_country.pdf"))

    # --------------
    # Fuel per fueltype for whole country over annual timesteps
    # ----------------
    logging.debug("... Plot total fuel (y) per fueltype")
    plt_fuels_enduses_y(
        results_container['results_every_year'],
        lookups,
        os.path.join(
            local_paths['data_results_PDF'],
            'y_fueltypes_all_enduses.pdf'))

    # ----------
    # Plot seasonal typical load profiles
    # Averaged load profile per daytpe for a region
    # ----------

    # ------------------------------------
    # Load factors per fueltype and region
    # ------------------------------------
    for fueltype_str, fueltype_int in lookups['fueltypes'].items():
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
            results_container['load_factors_yd'],
            reg_nrs,
            os.path.join(
                local_paths['data_results_PDF'], 'lf_yd_{}.pdf'.format(fueltype_str)))

        # load_factors_yd = max daily value / average annual daily value
        plot_lf_y(
            fueltype_int,
            fueltype_str,
            results_container['load_factors_y'],
            reg_nrs,
            os.path.join(
                local_paths['data_results_PDF'],
                'lf_y_{}.pdf'.format(fueltype_str)))

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

    # ------------------------------------
    # Plot averaged per season and fueltype
    # ------------------------------------
    base_year = 2015
    for year in results_container['av_season_daytype_cy'].keys():
        for fueltype_int in results_container['av_season_daytype_cy'][year].keys():
            fueltype_str = tech_related.get_fueltype_str(lookups['fueltypes'], fueltype_int)
            plot_load_profile_dh_multiple(
                os.path.join(
                    local_paths['data_results_PDF'],
                    'season_daytypes_by_cy_comparison__{}__{}.pdf'.format(year, fueltype_str)),
                results_container['av_season_daytype_cy'][year][fueltype_int], #current year
                results_container['av_season_daytype_cy'][base_year][fueltype_int], # base year
                results_container['season_daytype_cy'][year][fueltype_int], #current year
                results_container['season_daytype_cy'][base_year][fueltype_int], # base year
                plot_peak=True,
                plot_all_entries=False,
                plot_figure=False,
                max_y_to_plot=120)

    # ---------------------------------
    # Plot hourly peak loads over time for different fueltypes
    # --------------------------------
    plt_fuels_peak_h(
        results_container['tot_peak_enduses_fueltype'],
        lookups,
        os.path.join(
            local_paths['data_results_PDF'],
            'fuel_fueltypes_peak_h.pdf'))

    # -
    #     #tot_fuel_y_enduse_specific_h
    # -
    print("finisthed plotting")
    return

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

            for year_nr, lf_fueltype_reg in lf_fueltypes_season.items():

                # Get min and max of all entries of year of all regions
                min_y = np.min(lf_fueltype_reg[fueltype_int])
                max_y = np.max(lf_fueltype_reg[fueltype_int])
                upper_boundary.append((year_nr, min_y))
                lower_bdoundary.append((year_nr, max_y))

            # create correct sorting to draw filled polygon
            min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)

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
            average_season_year_years.append(np.mean(average_season_year))

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
    ax.set_xticks(minor_ticks, minor = True)
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
    '''recs = []
    for color_nr in range(0, len(class_colours)):
        recs.append(mpatches.Rectangle((0,0), 1, 1, fc=class_colours[color_nr], alpha=1.0))

    plt.legend(
        recs,
        classes,
        ncol=2,
        prop={'family': 'arial','size': 8},
        loc='best',
        frameon=False)'''

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_plot_fig)
    plt.close()

def plot_lf_y(
        fueltype_int,
        fueltype_str,
        load_factors_y,
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

            for year, lf_fueltype_reg in load_factors_y.items():
                x_values_year.append(year)
                y_values_year.append(lf_fueltype_reg[fueltype_int][reg_nr])

            plt.plot(
                x_values_year,
                y_values_year,
                linewidth=0.2,
                color='grey')

    #HANS
    if plot_max_min_polygon:
        lower_bdoundary = []
        upper_boundary = []

        for year_nr, lf_fueltype_reg in load_factors_y.items():

            # Get min and max of all entries of year of all regions
            min_y = np.min(lf_fueltype_reg[fueltype_int])
            max_y = np.max(lf_fueltype_reg[fueltype_int])
            upper_boundary.append((year_nr, min_y))
            lower_bdoundary.append((year_nr, max_y))

        # create correct sorting to draw filled polygon
        min_max_polygon = order_polygon(upper_boundary, lower_bdoundary)

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

    years = list(load_factors_y.keys())
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
                print("no minus values allowed {}  {}  {}".format(enduse, yearly_sum_twh, model_year))
                sys.exit("ERROR")

            y_values_enduse_yrs[year_array_nr] = yearly_sum_twh

        # Add array with values for every year to list
        y_value_arrays.append(y_values_enduse_yrs)

    # Convert to stacked
    y_stacked = np.row_stack((y_value_arrays))

    # Set figure size
    fig = plt.figure(
        figsize=plotting_program.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    color_list = [
        'darkturquoise',
        'orange',
        'firebrick',
        'darkviolet',
        'khaki',
        'olive',
        'darkseagreen',
        'darkcyan',
        'indianred',
        'darkblue',
        'orchid',
        'gainsboro',
        'mediumseagreen',
        'lightgray',
        'mediumturquoise',
        'darksage',
        'lemonchiffon',
        'cadetblue',
        'lightyellow',
        'lavenderblush',
        'coral',
        'purple',
        'aqua',
        'mediumslateblue',
        'darkorange',
        'mediumaquamarine',
        'darksalmon',
        'beige']

    # ----------
    # Stack plot
    # ----------
    color_stackplots = color_list[:len(enduses_data)]

    ax.stackplot(
        x_data,
        y_stacked,
        colors=color_stackplots)  #y_value_arrays
    #ax.stackplot(x, y1, y2, y3, labels=labels)

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
    '''recs = []
    for color_nr in range(0, len(color_stackplots)):
        recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=color_stackplots[color_nr], alpha=1.0))'''
    leg_labels = ['residential', 'service', 'industry']

    plt.legend(
        #recs,
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
    plt.show()
    plt.savefig(fig_name)
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

    plt.legend(ncol=2, frameon=False)

    plt.ylabel("GW")
    plt.xlabel("day")
    plt.title("tot annual ED, all enduses, fueltype {}".format(year_to_plot + 2050))

    # Saving figure
    plt.savefig(fig_name)
    plt.close()

def plt_fuels_enduses_y(results, lookups, fig_name):
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
        base_yr, end_yr[-1] + year_interval, year_interval)

    plt.xticks(major_ticks, major_ticks)

    # ----------
    # Plot lines
    # ----------
    color_list = [
        'darkturquoise', 'orange', 'firebrick',
        'darkviolet', 'khaki', 'olive', 'darkseagreen',
        'darkcyan', 'indianred', 'darkblue']
    linestyles = plotting_styles.linestyles()

    for counter, (fueltype_str, fuel_fueltype_yrs) in enumerate(y_values_fueltype.items()):
        color_line = str(color_list.pop())

        # plot line
        plt.plot(
            list(fuel_fueltype_yrs.keys()), #years
            list(fuel_fueltype_yrs.values()), #yearly data per fueltype
            #linestyle=linestyles[counter], #TODO
            color=color_line,
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
            'size': 5},
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

    # Save fig
    plt.savefig(fig_name)
    plt.close()

def plt_fuels_peak_h(tot_fuel_dh_peak, lookups, path_plot_fig):
    """Plots

    Plot peak hour per fueltype over time

    Arguments
    ---------
    tot_fuel_dh_peak : dict
        year, fueltype, peak_dh

    """
    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(14, 8))
    ax = fig.add_subplot(1, 1, 1)

    nr_y_to_plot = len(tot_fuel_dh_peak)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    y_init = np.zeros((lookups['fueltypes_nr'], nr_y_to_plot))

    for fueltype_str, fueltype in lookups['fueltypes'].items():

        # Legend
        legend_entries.append(fueltype_str)

        # REad out fueltype specific peak dh load
        data_over_years = []
        for model_year_object in tot_fuel_dh_peak.values():

            # Calculate max peak hour
            peak_fueltyp_h = np.max(model_year_object[fueltype])

            # Add peak hour
            data_over_years.append(peak_fueltyp_h)

        y_init[fueltype] = data_over_years

    # ----------
    # Plot lines
    # ----------
    linestyles = plotting_styles.linestyles()

    years = list(tot_fuel_dh_peak.keys())
    for fueltype, _ in enumerate(y_init):
        plt.plot(
            years,
            y_init[fueltype],
            linestyle=linestyles[fueltype],
            linewidth=0.7)

    # Legend
    ax.legend(
        legend_entries,
        prop={'family': 'arial','size': 8},
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
        path_plot_fig,
        calc_av_lp_modelled,
        calc_av_lp_real,
        calc_lp_modelled=None,
        calc_lp_real=None,
        plot_peak=False,
        plot_all_entries=False,
        plot_max_min_polygon=True,
        plot_figure=False,
        max_y_to_plot=60
    ):
    """Plotting average saisonal loads for each daytype. As an input
    GWh is provided, which for each h is cancelled out to GW.

    https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
    http://matthiaseisen.com/matplotlib/shapes/reg-polygon/
    """
    nrows = 4
    ncols = 2

    # set size
    fig = plt.figure(figsize=plotting_program.cm2inch(14, 25))
    ax = fig.add_subplot(nrows=nrows, ncols=ncols)

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
            font_additional_info = {
                'family': 'arial',
                'color': 'black',
                'weight': 'normal',
                'size': 8}

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

    if plot_figure:
        plt.show()

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

def plot_lp_yh(data_dh_modelled):
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

    # Save fig
    plt.show()

def plot_lp_yd(data_dh_modelled):
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

    plt.show()

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
    font_additional_info = {
        'family': 'arial',
        'color': 'black',
        'weight': 'normal',
        'size': 8}

    plt.xlabel("hour", fontsize=10)
    plt.ylabel("uk electrictiy use [GW]", fontsize=10)

    plt.legend(frameon=False)

    plt.savefig(os.path.join(path_result, name_fig))

    if plot_crit:
        plt.show()
        plt.close()
    else:
        plt.close()
