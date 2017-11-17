"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
import os
import operator
import logging
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.basic import conversions
from energy_demand.profiles import generic_shapes
from energy_demand.plotting import plotting_program
from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions
from energy_demand.validation import elec_national_data
from energy_demand.read_write import data_loader
from energy_demand.basic import date_prop
from energy_demand import enduse_func
from energy_demand.profiles import load_profile

def temporal_validation(
        local_paths,
        lookups,
        elec_ed_fueltype_national_yh,
        elec_factored_yh,
        elec_2015_indo,
        elec_2015_itsdo
    ):
    """National hourly electricity data is validated with
    the summed modelled hourly demand for all regions.
    Because the total annual modelled and real demands
    do not match (because of different data sources
    and because Northern Ireland is not included in the
    validation data) a correction factor is used.

    Arguments
    ---------
    local_paths :
    lookups :
    ed_fueltype_national_yh
    elec_2015_indo
    elec_2015_itsdo
    """
    # Select years to plot
    winter_week = list(range(
        date_prop.date_to_yearday(2015, 1, 12), date_prop.date_to_yearday(2015, 1, 19))) #Jan
    spring_week = list(range(
        date_prop.date_to_yearday(2015, 5, 11), date_prop.date_to_yearday(2015, 5, 18))) #May
    summer_week = list(range(
        date_prop.date_to_yearday(2015, 7, 13), date_prop.date_to_yearday(2015, 7, 20))) #Jul
    autumn_week = list(range(
        date_prop.date_to_yearday(2015, 10, 12), date_prop.date_to_yearday(2015, 10, 19))) #Oct
    days_to_plot = winter_week + spring_week + summer_week + autumn_week
    #days_to_plot = list(range(0, 365))

    # Hourly national electricity data
    elec_national_data.compare_results(
        'validation_electricity_weeks_selection.pdf',
        local_paths['data_results_validation'],
        elec_2015_indo,
        elec_2015_itsdo,
        elec_factored_yh,
        elec_ed_fueltype_national_yh,
        'all_submodels',
        days_to_plot)

    logging.debug(
        "FUEL gwh TOTAL  elec_2015_indo: {} elec_2015_itsdo: {}  MODELLED DATA:  {} ".format(np.sum(elec_2015_indo), np.sum(elec_2015_itsdo), elec_ed_fueltype_national_yh))
    logging.debug(
        "FUEL ktoe TOTAL  elec_2015_indo: {} elec_2015_itsdo: {}  MODELLED DATA:  {} ".format(np.sum(elec_2015_indo)/11.63, np.sum(elec_2015_itsdo)/11.63, elec_ed_fueltype_national_yh/11.63))

    return

def tempo_spatial_validation(
        base_yr,
        model_yearhours_nrs,
        model_yeardays_nrs,
        scenario_data,
        ed_fueltype_national_yh,
        ed_fueltype_regs_yh,
        tot_peak_enduses_fueltype,
        lookups,
        local_paths,
        lu_reg,
        reg_coord,
        seasons,
        model_yeardays_daytype
    ):
    """Validate national hourly demand for yearls fuel
    for all LADs. Test how the national disaggregation
    works
    """
    logging.info("... spatial validation")

    # -------------------------------------------
    # Add electricity and gas for transportation sector
    # -------------------------------------------
    fueltype_elec = lookups['fueltype']['electricity']
    fuel_elec_year_validation = 385
    fuel_national_tranport = np.zeros((lookups['fueltypes_nr']), dtype=float)

    # Elec demand from ECUK for transport sector
    fuel_national_tranport[fueltype_elec] = conversions.ktoe_to_gwh(fuel_elec_year_validation)

    # Create transport model (add flat shapes)
    model_object_transport = generic_shapes.GenericFlatEnduse(
        fuel_national_tranport, model_yeardays_nrs)

    ed_fueltype_national_yh = np.add(ed_fueltype_national_yh, model_object_transport.fuel_yh)
    tot_peak_enduses_fueltype = np.add(tot_peak_enduses_fueltype, model_object_transport.fuel_peak_dh)

    # Add electricity of transportion to regional yh fuel proportionally to population
    for region_array_nr, region in enumerate(lu_reg):

        # Disaggregation factor for transport electricity
        factor_transport_reg = scenario_data['population'][base_yr][region] / sum(scenario_data['population'][base_yr].values())
        ed_fueltype_regs_yh[fueltype_elec][region_array_nr] += model_object_transport.fuel_yh[fueltype_elec].reshape(model_yearhours_nrs) * factor_transport_reg

    # -------------------------------------------
    # Spatial validation
    # -------------------------------------------
    subnational_elec = data_loader.read_national_real_elec_data(local_paths['path_val_subnational_elec'])
    subnational_gas = data_loader.read_national_real_gas_data(local_paths['path_val_subnational_gas'])

    spatial_validation(
        reg_coord,
        ed_fueltype_regs_yh,
        lookups['fueltype']['electricity'],
        'electricity',
        lu_reg,
        subnational_elec,
        os.path.join(local_paths['data_results_validation'], 'validation_spatial_elec.pdf'))

    spatial_validation(
        reg_coord,
        ed_fueltype_regs_yh,
        lookups['fueltype']['gas'],
        'gas',
        lu_reg,
        subnational_gas,
        os.path.join(local_paths['data_results_validation'], 'validation_spatial_gas.pdf'))

    # -------------------------------------------
    # Temporal validation (hourly for national)
    # -------------------------------------------
    # Read validation data
    elec_2015_indo, elec_2015_itsdo = elec_national_data.read_raw_elec_2015(local_paths['path_val_nat_elec_data'])

    diff_factor_elec = np.sum(ed_fueltype_national_yh[lookups['fueltype']['electricity']]) / np.sum(elec_2015_indo)
    logging.info("... ed difference between modellend and real [percent] %s: ", (1 - diff_factor_elec) * 100)

    elec_factored_yh = diff_factor_elec * elec_2015_indo

    temporal_validation(
        local_paths,
        lookups,
        ed_fueltype_national_yh[lookups['fueltype']['electricity']],
        elec_factored_yh,
        elec_2015_indo,
        elec_2015_itsdo)

    # ---------------------------------------------------
    # Calculate average season and daytypes and plot
    # ---------------------------------------------------
    logging.info("...calculate average data and plot per season and fueltype")

    calc_av_lp_modelled, calc_lp_modelled = load_profile.calc_av_lp(
        ed_fueltype_national_yh[lookups['fueltype']['electricity']],
        seasons,
        model_yeardays_daytype)

    calc_av_lp_real, calc_lp_real = load_profile.calc_av_lp(
        elec_factored_yh,
        seasons,
        model_yeardays_daytype)

    # Plot average daily loads
    plotting_results.plot_load_profile_dh_multiple(
        os.path.join(local_paths['data_results_validation'], 'validation_all_season_daytypes.pdf'),
        calc_av_lp_modelled,
        calc_av_lp_real,
        calc_lp_modelled,
        calc_lp_real,
        plot_peak=True,
        plot_all_entries=True)

    # ---------------------------------------------------
    # Validation of national electrictiy demand for peak
    # ---------------------------------------------------
    logging.debug("...validation of peak data: compare peak with data")

    # Peak across all fueltypes WARNING: Fueltype specific
    peak_day = enduse_func.get_peak_day(ed_fueltype_national_yh)

    elec_national_data.compare_peak(
        "validation_elec_peak_comparison_peakday_yh.pdf",
        local_paths['data_results_validation'],
        elec_2015_indo[peak_day],
        ed_fueltype_national_yh[lookups['fueltype']['electricity']][peak_day])

    logging.info("...compare peak from max peak factors")
    elec_national_data.compare_peak(
        "validation_elec_peak_comparison_peak_shapes.pdf",
        local_paths['data_results_validation'],
        elec_2015_indo[peak_day],
        tot_peak_enduses_fueltype[lookups['fueltype']['electricity']])

    # ---------------------------------------------------
    # Validate boxplots for every hour (temporal validation)
    # ---------------------------------------------------
    elec_national_data.compare_results_hour_boxplots(
        "validation_hourly_boxplots_electricity_01.pdf",
        local_paths['data_results_validation'],
        elec_2015_indo,
        ed_fueltype_national_yh[lookups['fueltype']['electricity']])

    return

def spatial_validation(
        reg_coord,
        ed_fueltype_regs_yh,
        fueltype_int,
        fueltype_str,
        lu_reg,
        subnational_elec,
        fig_name
    ):
    """Compare gas/elec demand for LADs

    Arguments
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    ed_fueltype_regs_yh : object
        Regional fuel

    Note
    -----
    SOURCE OF LADS:
        - Data for northern ireland is not included in that, however in BEIS dataset!
    """
    logging.debug("... Validation of spatial disaggregation")
    result_dict = {}
    result_dict['real_demand'] = {}
    result_dict['modelled_demand'] = {}

    # -------------------------------------------
    # Match ECUK sub-regional demand with geocode
    # -------------------------------------------
    for region_array_nr, region_name in enumerate(lu_reg):
        for reg_geocode in reg_coord:
            if reg_geocode == region_name:

                try:
                    # Test wheter data is provided for LAD
                    if subnational_elec[reg_geocode] == 0:
                        # Ignore region
                        pass
                    else:
                        # --Sub Regional Electricity demand
                        gw_per_region_real = conversions.gwhperyear_to_gw(subnational_elec[reg_geocode])
                        result_dict['real_demand'][reg_geocode] = gw_per_region_real

                        # Convert GWh to GW
                        gw_per_region_modelled = conversions.gwhperyear_to_gw(
                            np.sum(ed_fueltype_regs_yh[fueltype_int][region_array_nr]))

                        # Correct ECUK data with correction factor
                        result_dict['modelled_demand'][reg_geocode] = gw_per_region_modelled
                except KeyError:
                    logging.warning("No fuel is defined for region %s", reg_geocode)

    # --------------------
    # Calculate statistics
    # --------------------
    all_diff_real_modelled_p = []

    for reg_geocode in lu_reg:
        try:
            real = result_dict['real_demand'][reg_geocode]
            modelled = result_dict['modelled_demand'][reg_geocode]

            diff_real_modelled_p = (100/real) * modelled
            all_diff_real_modelled_p.append(diff_real_modelled_p)
        except KeyError:
            pass

    d_real_modelled_p = np.mean(all_diff_real_modelled_p)

    # RMSE calculations
    rmse_value = basic_functions.rmse(
        np.array(list(result_dict['modelled_demand'].values())),
        np.array(list(result_dict['real_demand'].values())))

    # -----------------
    # Sort results according to size
    # -----------------
    sorted_dict_real_elec_demand = sorted(
        result_dict['real_demand'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    fig = plt.figure(figsize=plotting_program.cm2inch(17, 10))
    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_dict_real_elec_demand), 1)

    y_real_elec_demand = []
    y_modelled_elec_demand = []

    labels = []
    for sorted_region in sorted_dict_real_elec_demand:
        y_real_elec_demand.append(result_dict['real_demand'][sorted_region[0]])
        y_modelled_elec_demand.append(result_dict['modelled_demand'][sorted_region[0]])
        logging.debug(
            "validation: %s %s diff: %s",
            result_dict['real_demand'][sorted_region[0]],
            result_dict['modelled_demand'][sorted_region[0]],
            result_dict['modelled_demand'][sorted_region[0]] - result_dict['real_demand'][sorted_region[0]])
        labels.append(sorted_region)

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
        markersize=4,
        fillstyle='full',
        markeredgewidth=0.7,
        color='black',
        label='real')

    plt.plot(
        x_values,
        y_modelled_elec_demand,
        marker='o',
        linestyle='None',
        markersize=4, #markerfacecoloralt markeredgecolor=''
        markerfacecolor='blue', #whitesmoke
        fillstyle='none',
        markeredgewidth=0.7,
        color='black',
        label='modelled')

    # Limit
    plt.ylim(ymin=0)

    # -----------
    # Labelling
    # -----------
    font_additional_info = {
        'family': 'arial', 'color': 'black', 'weight': 'normal', 'size': 8}
    title_info = ('RMSE: {}, d_real_model: {}, reg_nr: {}'.format(
        round(rmse_value, 3),
        round(d_real_modelled_p, 3),
        len(y_real_elec_demand)))

    plt.title(
        title_info,
        loc='left',
        fontdict=font_additional_info)

    plt.xlabel("regions")
    plt.ylabel("{} GW".format(fueltype_str))

    # --------
    # Legend
    # --------
    plt.legend(
        prop={'family': 'arial','size': 8},
        frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)
    plt.close()

def correction_uk_northern_ireland_2015():
    """Not used yet. TODO
    """
    # ------------
    # Substraction demand for northern ireland proportionally
    # to the population. The population data are taken from
    # https://www.ons.gov.uk/peoplepopulationandcommunity
    # populationandmigration/populationestimates/bulletins
    # annualmidyearpopulationestimates/mid2015
    #
    # The reason to correct for norther ireland is becauss
    # in the national electricity data, nothern ireland is
    # not included. However, in BEIS, Northern ireland is included.
    # ------------
    pop_northern_ireland_2015 = 1851600
    pop_wales_scotland_england_2015 = 3099100 + 5373000 + 54786300
    pop_tot_uk = pop_northern_ireland_2015 + pop_wales_scotland_england_2015
    correction_factor = pop_wales_scotland_england_2015 / pop_tot_uk

    return correction_factor
