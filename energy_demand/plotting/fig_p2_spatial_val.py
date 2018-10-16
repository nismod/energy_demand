"""
"""
import os
import operator
import logging
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

from energy_demand.technologies import tech_related
from energy_demand.read_write import data_loader
from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import plotting_styles
from energy_demand.validation import lad_validation

def run(
        simulation_yr_to_plot,
        demand_year_non_regional,
        demand_year_regional,
        fueltypes,
        fig_path,
        path_temporal_elec_validation,
        path_temporal_gas_validation,
        regions,
        plot_crit
    ):
    """Validate spatial and temporal energy demands

    Info
    -----
    Because the floor area is only availabe for LADs from 2001,
    the LADs are converted to 2015 LADs.
    """
    logging.info("... temporal validation")

    ######################################
    # Data preparation
    ######################################
    subnational_elec = data_loader.read_lad_demands(path_temporal_elec_validation) # Read only domestic heating
    subnational_gas = data_loader.read_lad_demands(path_temporal_gas_validation)   # Read only domestic heating

    # ----------------------------------------
    # Remap demands between 2011 and 2015 LADs
    # ----------------------------------------
    subnational_elec = lad_validation.map_LAD_2011_2015(subnational_elec)
    subnational_gas = lad_validation.map_LAD_2011_2015(subnational_gas)

    # Create fueltype secific dict electricity
    fuel_elec_regs_yh_non_regional = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled_tot = demand_year_non_regional[fueltypes['electricity']][region_array_nr]
        fuel_elec_regs_yh_non_regional[region] = gwh_modelled_tot

    # Create fueltype secific dict for gas
    fuel_gas_regs_yh = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled_tot = np.sum(demand_year_non_regional[fueltypes['gas']][region_array_nr])
        fuel_gas_regs_yh[region] = gwh_modelled_tot

    fuel_elec_regs_yh_non_regional = lad_validation.map_LAD_2011_2015(fuel_elec_regs_yh_non_regional)
    fuel_gas_regs_yh = lad_validation.map_LAD_2011_2015(fuel_gas_regs_yh)

    ######################################
    # Plotting
    ######################################
    # Electrcity
    plot_spatial_validation(
        simulation_yr_to_plot,
        fuel_elec_regs_yh_non_regional,
        demand_year_regional,
        subnational_elec,
        regions,
        'electricity',
        fig_path=os.path.join(fig_path, "spatial_validation_electricity.pdf"),
        label_points=False,
        plotshow=plot_crit)

    # Gas
    plot_spatial_validation(
        simulation_yr_to_plot,
        fuel_gas_regs_yh,
        demand_year_regional,
        subnational_gas,
        regions,
        'gas',
        fig_path=os.path.join(fig_path, "spatial_validation_gas.pdf"),
        label_points=False,
        plotshow=plot_crit)

def plot_spatial_validation(
        simulation_yr_to_plot,
        non_regional_modelled,
        regional_modelled,
        subnational_real,
        regions,
        fueltype_str,
        fig_path,
        label_points=False,
        plotshow=False
    ):
    result_dict = {}
    result_dict['real_demand'] = {}
    result_dict['modelled_demand'] = {}
    result_dict['modelled_demands_regional'] = {}

    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # -------------------------------------------
    # Match ECUK sub-regional demand with geocode
    # -------------------------------------------
    for region_nr, region in enumerate(regions):
        try:
            # --Sub Regional Electricity demand (as GWh)
            real = subnational_real[region]
            modelled = non_regional_modelled[region]
            result_dict['real_demand'][region] = real
            result_dict['modelled_demand'][region] = modelled

        except KeyError:
            logging.debug("Sub-national spatial validation: No fuel for region %s", region)

        # Do this for every weather station data
        for weather_station in regional_modelled:
            try:
                _reg_demand = regional_modelled[weather_station][simulation_yr_to_plot][fueltype_int][region_nr]
                result_dict['modelled_demands_regional'][region].append(_reg_demand)
            except KeyError:
                _reg_demand = regional_modelled[weather_station][simulation_yr_to_plot][fueltype_int][region_nr]
                result_dict['modelled_demands_regional'][region] = [_reg_demand]

    # --------------------
    # Calculate statistics
    # --------------------
    diff_real_modelled_p = []
    diff_real_modelled_abs = []

    for region in regions:
        try:
            real = result_dict['real_demand'][region]
            modelled = result_dict['modelled_demand'][region]
            diff_real_modelled_p.append(abs(100 - ((100 / real) * modelled)))
            diff_real_modelled_abs.append(real - modelled)
        except KeyError:
            pass

    # Calculate the average deviation between reald and modelled
    av_deviation_real_modelled = np.average(diff_real_modelled_p)
    median_absolute_deviation = np.median(diff_real_modelled_p)    # median deviation

    # Calculate standard deviation
    std_dev_p = np.std(diff_real_modelled_p)        # Given as percent
    std_dev_abs = np.std(diff_real_modelled_abs)    # Given as energy unit

    # -----------------
    # Sort results according to size
    # -----------------
    sorted_dict_real = sorted(
        result_dict['real_demand'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    x_values = np.arange(0, len(sorted_dict_real), 1)
    y_real_demand = []
    y_modelled_demand = []
    y_modelled_demands_non_regional = []
    labels = []

    for sorted_region in sorted_dict_real:
        geocode_lad = sorted_region[0]
        y_real_demand.append(result_dict['real_demand'][geocode_lad])
        y_modelled_demand.append(result_dict['modelled_demand'][geocode_lad])
        y_modelled_demands_non_regional.append(result_dict['modelled_demands_regional'][geocode_lad])
    
        print(
            "validation %s LAD %s: real: %s modelled: %s  modelled percentage: %s (%sp diff)",
            fueltype_str,
            geocode_lad,
            round(result_dict['real_demand'][geocode_lad], 4),
            round(result_dict['modelled_demand'][geocode_lad], 4),
            round(100 / result_dict['real_demand'][geocode_lad] * result_dict['modelled_demand'][geocode_lad], 4),
            round(100 - (100 / result_dict['real_demand'][geocode_lad] * result_dict['modelled_demand'][geocode_lad]), 4))

        labels.append(geocode_lad)

    # Calculate r_squared
    _slope, _intercept, r_value, _p_value, _std_err = stats.linregress(
        y_real_demand,
        y_modelled_demand)

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
    markersize = 3
    markeredgewidth = 0
    linewidth = 2
    color_real = 'black'
    color_all_stations = 'green'
    color_single_station = 'red'
    plt.plot(
        x_values,
        y_real_demand,
        linestyle='-',
        marker='o',
        alpha=0.6,
        markersize=markersize,
        fillstyle='full',
        markerfacecolor='black',
        markeredgewidth=markeredgewidth,
        color=color_real,
        label='actual demand')

    plt.plot(
        x_values,
        y_modelled_demand,
        marker='o',
        linestyle='-',
        markersize=markersize,
        alpha=0.6,
        markerfacecolor='blue',
        fillstyle='none',
        markeredgewidth=markeredgewidth,
        markeredgecolor='blue',
        color=color_all_stations,
        label='modelled using all stations')

    # Demands calculated only from one weather station
    station_nr = 0
    nr_of_stations = len(y_modelled_demands_non_regional[0])
    station_vals = []
    for region_vals in y_modelled_demands_non_regional:
        station_vals.append(region_vals[station_nr])

    plt.plot(
        x_values,
        station_vals,
        marker='o',
        linestyle='-',
        linewidth=linewidth,
        markersize=markersize,
        alpha=0.6,
        markerfacecolor='green',
        fillstyle='none',
        markeredgewidth=markeredgewidth,
        markeredgecolor='green',
        color=color_single_station,
        label='modelled using only a single stations')

    '''for i in range(nr_of_stations):
        station_data = []
        for reg_nr in range(nr_of_regions):
            station_data.append(y_modelled_demands_non_regional[reg_nr][i])

        plt.plot(
            x_values,
            station_data, #y_modelled_demands_non_regional,
            marker='o',
            linestyle='None',
            markersize=1.6,
            alpha=0.6,
            markerfacecolor='white',
            fillstyle='none',
            markeredgewidth=0.5,
            markeredgecolor='orange',
            color='black',
            label='model')'''

    '''# ------------
    # Collect all values per weather_yr
    list_with_station_vals = []
    for station_i in range(nr_of_stations):
        station_vals = []
        for region_vals in y_modelled_demands_non_regional:
            station_vals.append(region_vals[station_i])
        list_with_station_vals.append(station_vals)

    df = pd.DataFrame(
        list_with_station_vals,
        columns=range(nr_of_regions)) #note not region_rn as ordered

    period_h = range(nr_of_regions)

    quantile_95 = 0.95
    quantile_05 = 0.05

    df_q_95 = df.quantile(quantile_95)
    df_q_05 = df.quantile(quantile_05)

    #Transpose for plotting purposes
    df = df.T
    df_q_95 = df_q_95.T
    df_q_05 = df_q_05.T

    # ---------------
    # Smoothing lines
    # ---------------
    try:
        period_h_smoothed, df_q_95_smoothed = basic_plot_functions.smooth_data(period_h, df_q_95, num=40000)
        period_h_smoothed, df_q_05_smoothed = basic_plot_functions.smooth_data(period_h, df_q_05, num=40000)
    except:
        period_h_smoothed = period_h
        df_q_95_smoothed = df_q_95
        df_q_05_smoothed = df_q_05
    #plt.plot(period_h_smoothed, df_q_05_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.05")
    #plt.plot(period_h_smoothed, df_q_95_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.95")

    # -----------------
    # Uncertainty range
    # -----------------
    plt.fill_between(
        period_h_smoothed, #x
        df_q_95_smoothed,  #y1
        df_q_05_smoothed,  #y2
        alpha=.40,
        facecolor="grey",
        label="uncertainty band")
    # -----------'''


    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    if label_points:
        for pos, txt in enumerate(labels):

            ax.text(
                x_values[pos],
                y_modelled_demand[pos],
                txt,
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=1)

    font_additional_info = plotting_styles.font_info(size=4)

    title_info = ('R_2: {}, std_%: {} (GWh {}), av_diff_%: {} median_abs_dev: {}'.format(
        round(r_value, 2),
        round(std_dev_p, 2),
        round(std_dev_abs, 2),
        round(av_deviation_real_modelled, 2),
        round(median_absolute_deviation, 2)))

    plt.title(
        title_info,
        loc='left',
        fontdict=font_additional_info)

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
    plt.savefig(fig_path)

    if plotshow:
        plt.show()
    else:
        plt.close()
