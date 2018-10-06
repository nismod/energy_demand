"""
"""
import operator
import logging
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from energy_demand.read_write import data_loader
from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import plotting_styles
from energy_demand.validation import lad_validation

def run(
        weather_yr,
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
    subnational_gas = data_loader.read_lad_demands(path_temporal_gas_validation)   ## Read only domestic heating TODO??

    # ----------------------------------------
    # Remap demands between 2011 and 2015 LADs
    # ----------------------------------------
    subnational_elec = lad_validation.map_LAD_2011_2015(subnational_elec)
    subnational_gas = lad_validation.map_LAD_2011_2015(subnational_gas)

    # Create fueltype secific dict electricity
    fuel_elec_regs_yh_non_regional = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled_tot = 0

        for enduse in ['rs_space_heating']:
            gwh_modelled_tot += np.sum(demand_year_non_regional[enduse][fueltypes['electricity']][region_array_nr])
        fuel_elec_regs_yh_non_regional[region] = gwh_modelled_tot

    # Create fueltype secific dict for gas
    '''fuel_gas_regs_yh = {}
    for region_array_nr, region in enumerate(regions):
        gwh_modelled_tot = np.sum(demand_year_non_regional[fueltypes['gas']][region_array_nr])
        fuel_gas_regs_yh[region] = gwh_modelled_tot'''

    fuel_elec_regs_yh_non_regional = lad_validation.map_LAD_2011_2015(fuel_elec_regs_yh_non_regional)
    #fuel_gas_regs_yh = lad_validation.map_LAD_2011_2015(fuel_gas_regs_yh)

    ######################################
    # Plotting
    ######################################
    plot_spatial_validation(
        weather_yr,
        fuel_elec_regs_yh_non_regional,
        demand_year_regional,
        subnational_elec,
        regions,
        'elec',
        fig_path=fig_path,
        label_points=False,
        plotshow=plot_crit)

def plot_spatial_validation(
        weather_yr,
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
    result_dict['modelled_demand_regional'] = {}

    # -------------------------------------------
    # Match ECUK sub-regional demand with geocode
    # -------------------------------------------
    for region in regions:
        try:
            # --Sub Regional Electricity demand (as GWh)
            result_dict['real_demand'][region] = subnational_real[region]
            result_dict['modelled_demand'][region] = non_regional_modelled[region]
        except KeyError:
            logging.debug("Sub-national spatial validation: No fuel for region %s", region)

        # Do this for every weather station data
        '''for weather_station in regional_modelled:
            result_dict['modelled_demand_regional'][weather_station] = {}
            try:
                _reg_demand = regional_modelled[weather_station][weather_yr][region]
                result_dict['modelled_demand_regional'][weather_station][region] = _reg_demand
            except KeyError:
                pass'''

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
    #y_modelled_demand_non_regional = []
    labels = []

    for sorted_region in sorted_dict_real:
        geocode_lad = sorted_region[0]
        y_real_demand.append(result_dict['real_demand'][geocode_lad])
        y_modelled_demand.append(result_dict['modelled_demand'][geocode_lad])
        #y_modelled_demand_non_regional.append(
        #    result_dict['modelled_demand_regional'][geocode_lad]) 
        print(
            "validation %s LAD %s: real: %s modelled: %s  modelled percentage: %s (%sp diff)",
            fueltype_str,
            geocode_lad,
            round(result_dict['real_demand'][geocode_lad], 4),
            round(result_dict['modelled_demand'][geocode_lad], 4),
            round(100 / result_dict['real_demand'][geocode_lad] * result_dict['modelled_demand'][geocode_lad], 4),
            round(100 - (100 / result_dict['real_demand'][geocode_lad] * result_dict['modelled_demand'][geocode_lad]), 4))

        # Labels
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
    plt.plot(
        x_values,
        y_real_demand,
        linestyle='None',
        marker='o',
        alpha=0.6,
        markersize=1.6,
        fillstyle='full',
        markerfacecolor='grey',
        markeredgewidth=0.2,
        color='black',
        label='actual')

    plt.plot(
        x_values,
        y_modelled_demand,
        marker='o',
        linestyle='None',
        markersize=1.6,
        alpha=0.6,
        markerfacecolor='white',
        fillstyle='none',
        markeredgewidth=0.5,
        markeredgecolor='blue',
        color='black',
        label='model')

    # Regional demands
    '''plt.plot(
        x_values,
        y_modelled_demand_non_regional,
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
    #plt.savefig(fig_name)

    if plotshow:
        plt.show()
    else:
        plt.close()
    
    raise Exception("WHAT HAPPEND")