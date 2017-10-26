"""Compare gas/elec demand on Local Authority Districts with modelled demand
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import os
import sys
import operator
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions
from energy_demand.validation import elec_national_data
from energy_demand.read_write import data_loader
from energy_demand.basic import date_handling
import logging

def temporal_validation(data, reg_enduses_fueltype_y):
    """
            # Validation of national electrictiy demand for base year
        # Compare total gas and electrictiy
        # load with Elexon Data for Base year for different regions
    """
    # -------------------------------
    # Yeardays to plot for validation
    # -------------------------------
    winter_week = list(range(date_handling.date_to_yearday(2015, 1, 12), date_handling.date_to_yearday(2015, 1, 19))) #Jan
    spring_week = list(range(date_handling.date_to_yearday(2015, 5, 11), date_handling.date_to_yearday(2015, 5, 18))) #May
    summer_week = list(range(date_handling.date_to_yearday(2015, 7, 13), date_handling.date_to_yearday(2015, 7, 20))) #Jul
    autumn_week = list(range(date_handling.date_to_yearday(2015, 10, 12), date_handling.date_to_yearday(2015, 10, 19))) #Oct
    days_to_plot = winter_week + spring_week + summer_week + autumn_week
    #days_to_plot = list(range(0, 365))

    val_elec_data_2015_INDO, val_elec_data_2015_ITSDO = elec_national_data.read_raw_elec_2015_data(
        data['local_paths']['folder_validation_national_elec_data'])

    diff_factor_TD_ECUK_Input = (1.0 / np.sum(val_elec_data_2015_INDO)) * np.sum(reg_enduses_fueltype_y[data['lookups']['fueltype']['electricity']])
            
    INDO_factoreddata = diff_factor_TD_ECUK_Input * val_elec_data_2015_INDO

    logging.debug("FACTOR: %s", diff_factor_TD_ECUK_Input)
    logging.debug("Loaded validation data elec demand. ND:  %s  TSD: %s", np.sum(val_elec_data_2015_INDO), np.sum(val_elec_data_2015_ITSDO))
    logging.debug("--ECUK Elec_demand  %s ", np.sum(reg_enduses_fueltype_y[data['lookups']['fueltype']['electricity']]))
    logging.debug("--ECUK Gas Demand   %s", np.sum(reg_enduses_fueltype_y[data['lookups']['fueltype']['gas']]))
    logging.debug("CORRECTED DEMAND:  %s", np.sum(INDO_factoreddata))

    # Compare different models
    elec_national_data.compare_results(
        'plot_figure_01.pdf',
        data,
        val_elec_data_2015_INDO,
        val_elec_data_2015_ITSDO,
        INDO_factoreddata,
        reg_enduses_fueltype_y[2],
        'all_submodels',
        days_to_plot)

    logging.debug("FUEL gwh TOTAL  val_elec_data_2015_INDO:  {} val_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(val_elec_data_2015_INDO), np.sum(val_elec_data_2015_ITSDO), np.sum(model_run_object.reg_enduses_fueltype_y[2])))
    logging.debug("FUEL ktoe TOTAL  val_elec_data_2015_INDO: {} val_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(val_elec_data_2015_INDO)/11.63, np.sum(val_elec_data_2015_ITSDO)/11.63, np.sum(model_run_object.reg_enduses_fueltype_y[2])/11.63))

    return

def spatial_validation(data, reg_enduses_fueltype_y, tot_peak_enduses_fueltype):
    """Validate national demand
    """
    logging.info("Spatial Validation of electrictiy demand")

    # Add electricity data to region info
    data['reg_coord'], _ = data_loader.get_national_electricity_data(
        data['local_paths'], data['reg_coord'])

    val_elec_data_2015_INDO, val_elec_data_2015_ITSDO = elec_national_data.read_raw_elec_2015_data(
        data['local_paths']['folder_validation_national_elec_data'])

    compare_lad_regions(
        'compare_lad_regions.pdf',
        data,
        data['reg_coord'],
        reg_enduses_fueltype_y,
        data['lookups']['fueltypes_nr'],
        data['lookups']['fueltype'],
        data['lu_reg']
        )

    # ---------------------------------------------------
    # Validation of national electrictiy demand for peak
    # ---------------------------------------------------
    logging.debug("...compare peak from data")
    peak_month = 2 #Feb
    peak_day = 18 #Day
    elec_national_data.compare_peak(
        "peak_comparison_01.pdf",
        data,
        val_elec_data_2015_INDO,
        reg_enduses_fueltype_y[peak_month][peak_day]
        )

    logging.debug("...compare peak from max peak factors")
    elec_national_data.compare_peak(
        "peak_comparison_02.pdf",
        data,
        val_elec_data_2015_INDO,
        tot_peak_enduses_fueltype[data['lookups']['fueltype']['electricity']])

    # ---------------------------------------------------
    # Validate boxplots for every hour
    # ---------------------------------------------------
    elec_national_data.compare_results_hour_boxplots(
        "hourly_boxplots_01.pdf",
        data,
        val_elec_data_2015_INDO,
        reg_enduses_fueltype_y[data['lookups']['fueltype']['electricity']])
    

    # TODO: VALIDATE GAS DEMAND

    return

def compare_lad_regions(fig_name, data, reg_coord, model_run_object, fueltypes_nr, lu_fueltypes, lu_reg):
    """Compare gas/elec demand for LADs

    Arguments
    ----------
    lad_infos_shapefile : dict
        Infos of shapefile (dbf / csv)
    model_run_object : object
        Model run results

    Note
    -----
    SOURCE OF LADS:
    """
    logging.debug("..Validation of spatial disaggregation")
    result_dict = {}
    result_dict['REAL_electricity_demand'] = {}
    result_dict['modelled_electricity_demand'] = {}

    # Match ECUK sub-regional demand with geocode
    for region_name in lu_reg:

        # Iterate loaded data
        for reg_geocode in reg_coord:
            if reg_geocode == region_name:

                # --Sub Regional Electricity #TODO: CHECK UNIT
                result_dict['REAL_electricity_demand'][region_name] = reg_coord[reg_geocode]['elec_tot15']

                all_fueltypes_reg_demand = model_run_object.get_regional_yh(fueltypes_nr, reg_geocode, data['assumptions']['model_yeardays_nrs'])
                result_dict['modelled_electricity_demand'][region_name] = np.sum(all_fueltypes_reg_demand[lu_fueltypes['electricity']])

    # -----------------
    # Sort results according to size
    # -----------------
    result_dict['modelled_electricity_demand_sorted'] = {}

    # --Sorted sub regional electricity demand
    sorted_dict_REAL_elec_demand = sorted(result_dict['REAL_electricity_demand'].items(), key=operator.itemgetter(1))

    # -------------------------------------
    # Plot
    # -------------------------------------
    nr_of_labels = len(sorted_dict_REAL_elec_demand)

    x_values = []
    for i in range(nr_of_labels):
        x_values.append(0 + i*0.2)

    y_values_REAL_electricity_demand = []
    y_values_modelled_electricity_demand = []

    labels = []
    for sorted_region in sorted_dict_REAL_elec_demand:
        y_values_REAL_electricity_demand.append(result_dict['REAL_electricity_demand'][sorted_region[0]])
        y_values_modelled_electricity_demand.append(result_dict['modelled_electricity_demand'][sorted_region[0]])
        labels.append(sorted_region)

    # RMSE calculations
    rmse_value = basic_functions.rmse(
        np.array(y_values_modelled_electricity_demand),
        np.array(y_values_REAL_electricity_demand))

    # ----------------------------------------------
    # Plot
    # ----------------------------------------------
    plt.figure(figsize=plotting_program.cm2inch(17, 10))
    plt.margins(x=0) #remove white space

    plt.plot(x_values, y_values_REAL_electricity_demand, 'ro', markersize=1, color='green', label='Sub-regional demand (real)')
    plt.plot(x_values, y_values_modelled_electricity_demand, 'ro', markersize=1, color='red', label='Disaggregated demand (modelled)')

    #plt.xticks(x_values, labels, rotation=90)
    plt.ylim(0, 6000)

    title_left = ('Comparison of sub-regional electricity demand (RMSE: {}, number of areas= {})'.format(rmse_value, len(y_values_REAL_electricity_demand)))
    plt.title(title_left, loc='left')
    plt.xlabel("Regions")
    plt.ylabel("Sub-regional yearly electricity demand [GW]")
    plt.legend()

    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], fig_name))

    if data['print_criteria']:
        plt.show()
    else:
        pass

    return
