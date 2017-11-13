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
        ed_fueltype_national_yh,
        val_elec_data_2015_indo,
        val_elec_data_2015_itsdo,
        indo_factoreddata
    ):
    """National hourly electricity data is validated with fuel of
    all regions for base year

    Arguments
    ---------
    local_paths :
    lookups : 
    ed_fueltype_national_yh, val_elec_data_2015_indo, val_elec_data_2015_itsdo

    # Validation of national electrictiy demand for base year
    # Compare total gas and electrictiy
    # load with Elexon Data for Base year for different regions

    Info
    ----
    It is not sure wheter notheren irleand is included. However does not matter
    because shape is of interest. With correction factor, the shape gets corrected anyway
    """
    # -------------------------------
    # Yeardays to plot for validation
    # -------------------------------
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

    # ---------------------------
    # Hourly national electricity data
    # ---------------------------
    # Compare different models
    elec_national_data.compare_results(
        'plot_figure_01.pdf',
        local_paths,
        val_elec_data_2015_indo,
        val_elec_data_2015_itsdo,
        indo_factoreddata,
        ed_fueltype_national_yh[lookups['fueltype']['electricity']],
        'all_submodels',
        days_to_plot)

    logging.debug(
        "FUEL gwh TOTAL  val_elec_data_2015_indo:  {} val_elec_data_2015_itsdo: {}  MODELLED DATA:  {} ".format(np.sum(val_elec_data_2015_indo), np.sum(val_elec_data_2015_itsdo), np.sum(ed_fueltype_national_yh[lookups['fueltype']['electricity']])))
    logging.debug("FUEL ktoe TOTAL  val_elec_data_2015_indo: {} val_elec_data_2015_itsdo: {}  MODELLED DATA:  {} ".format(np.sum(val_elec_data_2015_indo)/11.63, np.sum(val_elec_data_2015_itsdo)/11.63, np.sum(ed_fueltype_national_yh[lookups['fueltype']['electricity']])/11.63))

    return

def tempo_spatial_validation(
        base_yr,
        model_yearhours_nrs,
        data,
        ed_fueltype_national_yh,
        ed_fueltype_regs_yh,
        tot_peak_enduses_fueltype
    ):
    """Validate national hourly demand for yearls fuel
    for all LADs. Test how the national disaggregation
    works
    """
    logging.info("... spatial validation")

    # -------------------------------------------
    # Add electricity for transportation sector
    # -------------------------------------------
    fueltype_elec = data['lookups']['fueltype']['electricity']
    fuel_elec_year_validation = 385
    fuel_national_tranport = np.zeros((data['lookups']['fueltypes_nr']), dtype=float)
    fuel_national_tranport[fueltype_elec] = conversions.ktoe_to_gwh(
        fuel_elec_year_validation) #Elec demand from ECUK for transport sector

    # Create transport model (add flat shapes)
    model_object_transport = generic_shapes.GenericFlatEnduse(
        fuel_national_tranport, data['assumptions']['model_yeardays_nrs'])

    ed_fueltype_national_yh = np.add(ed_fueltype_national_yh, model_object_transport.fuel_yh)
    tot_peak_enduses_fueltype = np.add(tot_peak_enduses_fueltype, model_object_transport.fuel_peak_dh)

    # Add electricity of transportion to regional yh fuel proportionally to population
    for region_array_nr, region in enumerate(data['lu_reg']):

        # Disaggregation factor for transport electricity
        factor_transport_reg = data['scenario_data']['population'][base_yr][region] / sum(data['scenario_data']['population'][base_yr].values())

        ed_fueltype_regs_yh[fueltype_elec][region_array_nr] += model_object_transport.fuel_yh[fueltype_elec].reshape(model_yearhours_nrs) * factor_transport_reg

    # -------------------------------------------
    # Spatial validation
    # -------------------------------------------
    # Read national electricity data
    national_elec_data = data_loader.read_national_real_elec_data(
        data['local_paths']['path_val_subnational_elec_data'])

    national_gas_data = data_loader.read_national_real_gas_data(
        data['local_paths']['path_val_subnational_gas_data'])

    spatial_validation(
        data['reg_coord'],
        ed_fueltype_regs_yh,
        data['lookups']['fueltype']['electricity'],
        'electricity',
        data['lu_reg'],
        national_elec_data,
        os.path.join(data['local_paths']['data_results_PDF'], 'validation_spatial_elec.pdf'))

    spatial_validation(
        data['reg_coord'],
        ed_fueltype_regs_yh,
        data['lookups']['fueltype']['gas'],
        'gas',
        data['lu_reg'],
        national_gas_data,
        os.path.join(data['local_paths']['data_results_PDF'], 'validation_spatial_gas.pdf'))

    # -------------------------------------------
    # Temporal validation (hourly for national)
    # -------------------------------------------
    val_elec_data_2015_indo, val_elec_data_2015_itsdo = elec_national_data.read_raw_elec_2015_data(
        data['local_paths']['path_val_nat_elec_data'])

    diff_factor_td_ecuk_input = np.sum(ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']]) / np.sum(val_elec_data_2015_indo)

    indo_factoreddata = diff_factor_td_ecuk_input * val_elec_data_2015_indo

    logging.debug("FACTOR: %s", diff_factor_td_ecuk_input)
    logging.debug("Loaded validation data elec demand. ND:  %s  TSD: %s", np.sum(val_elec_data_2015_indo), np.sum(val_elec_data_2015_itsdo))
    logging.debug("--ECUK Elec_demand  %s ", np.sum(ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']]))
    logging.debug("--ECUK Gas Demand   %s", np.sum(ed_fueltype_national_yh[data['lookups']['fueltype']['gas']]))
    logging.debug("CORRECTED DEMAND:  %s", np.sum(indo_factoreddata))

    temporal_validation(
        data['local_paths'],
        data['lookups'],
        ed_fueltype_national_yh,
        val_elec_data_2015_indo,
        val_elec_data_2015_itsdo,
        indo_factoreddata)

    # ---------------------------------------------------
    # Calculate average season and daytypes and plot them
    # ---------------------------------------------------
    logging.debug("...calculate average data and plot per season and fueltype")

    calc_av_lp_modelled, calc_lp_modelled = load_profile.calc_av_lp(
        ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']],
        data['assumptions']['seasons'], data['assumptions']['model_yeardays_daytype'])

    calc_av_lp_real, calc_lp_real = load_profile.calc_av_lp(
        indo_factoreddata, data['assumptions']['seasons'], data['assumptions']['model_yeardays_daytype'])

    # Plot average daily loads
    plotting_results.plot_load_profile_dh_multiple(
        os.path.join(data['local_paths']['data_results_PDF'], 'validation_all_season_daytypes.pdf'),
        calc_av_lp_modelled,
        calc_av_lp_real,
        calc_lp_modelled,
        calc_lp_real,
        plot_peak=True,
        plot_all_entries=True)

    # ---------------------------------------------------
    # Validation of national electrictiy demand for peak
    # ---------------------------------------------------
    logging.debug("...compare peak from data")

    # Peak across all fueltypes WARNING: Fueltype specific
    peak_day = enduse_func.get_peak_day(ed_fueltype_national_yh)

    elec_national_data.compare_peak(
        "validation_elec_peak_comparison_01.pdf",
        data['local_paths'],
        val_elec_data_2015_indo[peak_day],
        ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']][peak_day])

    logging.debug("...compare peak from max peak factors")
    elec_national_data.compare_peak(
        "validation_elec_peak_comparison_02.pdf",
        data['local_paths'],
        val_elec_data_2015_indo[peak_day],
        tot_peak_enduses_fueltype[data['lookups']['fueltype']['electricity']])

    # ---------------------------------------------------
    # Validate boxplots for every hour (temporal validation)
    # ---------------------------------------------------
    elec_national_data.compare_results_hour_boxplots(
        "validation_hourly_boxplots_electricity_01.pdf",
        data['local_paths'],
        val_elec_data_2015_indo,
        ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']])

    return

def spatial_validation(
        reg_coord,
        ed_fueltype_regs_yh,
        fueltype_int,
        fueltype_str,
        lu_reg,
        national_elec_data,
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
    logging.debug("..Validation of spatial disaggregation")
    result_dict = {}
    result_dict['real_elec_demand'] = {}
    result_dict['modelled_elec_demand'] = {}

    # ------------
    # Substraction demand for notheren ireland TODO
    # ------------
    #
    # e.g. proportionally to population

    # -------------------------------------------
    # Match ECUK sub-regional demand with geocode
    # -------------------------------------------
    for region_array_nr, region_name in enumerate(lu_reg):
        for reg_geocode in reg_coord:
            if reg_geocode == region_name:
                try:
                    # --Sub Regional Electricity demand
                    result_dict['real_elec_demand'][reg_geocode] = national_elec_data[reg_geocode]
                    result_dict['modelled_elec_demand'][reg_geocode] = np.sum(ed_fueltype_regs_yh[fueltype_int][region_array_nr])
                except:
                    logging.warning("Error Validation: No fuel is defined for region %s", reg_geocode)

    # -----------------
    # Sort results according to size
    # -----------------
    result_dict['modelled_elec_demand_sorted'] = {}

    # --Sorted sub regional electricity demand
    sorted_dict_real_elec_demand = sorted(
        result_dict['real_elec_demand'].items(),
        key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    # Set figure size
    fig = plt.figure(figsize=plotting_program.cm2inch(17, 10))
    ax = fig.add_subplot(1, 1, 1)

    x_values = np.arange(0, len(sorted_dict_real_elec_demand), 1)

    y_real_elec_demand = []
    y_modelled_elec_demand = []

    labels = []
    for sorted_region in sorted_dict_real_elec_demand:
        y_real_elec_demand.append(result_dict['real_elec_demand'][sorted_region[0]])
        y_modelled_elec_demand.append(result_dict['modelled_elec_demand'][sorted_region[0]])
        labels.append(sorted_region)

    # RMSE calculations
    rmse_value = basic_functions.rmse(
        np.array(y_modelled_elec_demand),
        np.array(y_real_elec_demand))

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
        x_values, y_real_elec_demand,
        'ro', markersize=2, color='green', label='Sub-regional demand (real)')
    plt.plot(
        x_values, y_modelled_elec_demand,
        'ro', markersize=2, color='red', label='Disaggregated demand (modelled)')

    # Limit
    #print(sorted_dict_real_elec_demand[-1])
    #higher_x_to_plot = round(sorted_dict_real_elec_demand[-1][1], -3) #round to 1'000
    plt.ylim(0, 3000)
    #plt.ylim(0, higher_x_to_plot)

    # -----------
    # Labelling
    # -----------
    font_additional_info = {
        'family': 'arial', 'color': 'black', 'weight': 'normal', 'size': 8}
    title_info = ('RMSE: {}, Region Nr: {}'.format(rmse_value, len(y_real_elec_demand)))

    plt.title(
        title_info,
        loc='left',
        fontdict=font_additional_info)

    plt.xlabel("Regions")
    plt.ylabel("Sub-regional yearly {} demand [GW]".format(fueltype_str))

    # --------
    # Legend
    # --------
    plt.legend(frameon=False)

    # Tight layout
    plt.margins(x=0)
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)
    plt.close()
