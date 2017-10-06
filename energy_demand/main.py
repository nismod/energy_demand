'''
Energy Demand Model
=================
'''
import os
import sys
import logging
import numpy as np
from pyinstrument import Profiler
import energy_demand.energy_model as energy_model
from energy_demand.assumptions import base_assumptions
from energy_demand.read_write import data_loader
from energy_demand.read_write import read_data
from energy_demand.dwelling_stock import dw_stock
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import date_handling
from energy_demand.validation import lad_validation
from energy_demand.validation import elec_national_data
from energy_demand.plotting import plotting_results
from energy_demand.basic import logger_setup as log
#pylint: disable=W1202

def energy_demand_model(data):
    """Main function of energy demand model to calculate yearly demand

    Arguments
    ----------
    data : dict
        Data container

    Returns
    -------
    result_dict : dict
        A nested dictionary containing all data for energy supply model with
        timesteps for every hour in a year.
        [fuel_type : region : timestep]
    model_run_object : dict
        Object of a yearly model run

    Note
    ----
    This function is executed in the wrapper
    """
    fuel_in, fuel_in_elec, _ = testing.test_function_fuel_sum(data)

    # Add all region instances as an attribute (region name) into the class `EnergyModel`
    model_run_object = energy_model.EnergyModel(
        region_names=data['lu_reg'],
        data=data
        )

    # Total annual fuel of all regions
    fueltot = model_run_object.reg_enduses_fueltype_y

    # Fuel per region
    logging.info("================================================")
    logging.info("Simulation year:     " + str(model_run_object.curr_yr))
    logging.info("Number of regions    " + str(len(data['lu_reg'])))
    logging.info("Fuel input:          " + str(fuel_in))
    logging.info("Fuel output:         " + str(np.sum(fueltot)))
    logging.info("FUEL DIFFERENCE:     " + str(round((np.sum(fueltot) - fuel_in), 4)))
    logging.info("elec fuel in:        " + str(fuel_in_elec))
    logging.info("elec fuel out:       " + str(np.sum(model_run_object.reg_enduses_fueltype_y[2])))
    logging.info("ele fueld diff:      " + str(round(fuel_in_elec - np.sum(model_run_object.reg_enduses_fueltype_y[2]), 4)))
    logging.info("================================================")
    for fff in range(8):
        logging.debug("FF: " + str(np.sum(model_run_object.reg_enduses_fueltype_y[fff])))

    logging.debug("...finished energy demand model simulation")
    return model_run_object

if __name__ == "__main__":
    """
    """

    # Paths
    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    local_data_path = os.path.join(r'C:\Data_NISMOD', 'data_energy_demand')

    # Initialise logger
    log.set_up_logger(os.path.join(local_data_path, "logging_energy_demand.log"))
    logging.info("... start local energy demand calculations")

    # Run settings
    instrument_profiler = True
    print_criteria = True


    # Load data
    data = {}
    data['print_criteria'] = print_criteria
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'], data['assumptions'] = base_assumptions.load_assumptions(data, write_sim_param=True)
    data['tech_load_profiles'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])
    data['assumptions'] = base_assumptions.update_assumptions(data['assumptions'])
    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])
    data = data_loader.dummy_data_generation(data)

    logging.info("Start Energy Demand Model with python version: " + str(sys.version))
    logging.info("Info model run")
    logging.info("Nr of Regions " + str(len(data['lu_reg'])))

    # In order to load these data, the initialisation scripts need to be run
    logging.info("... Load data from script calculations")
    data = read_data.load_script_data(data) 

    logging.info("... Generate dwelling stocks over whole simulation period")
    data['rs_dw_stock'] = dw_stock.rs_dw_stock(data['lu_reg'], data)
    data['ss_dw_stock'] = dw_stock.ss_dw_stock(data['lu_reg'], data)

    results_every_year = []
    for sim_yr in data['sim_param']['sim_period']:
        data['sim_param']['curr_yr'] = sim_yr

        logging.debug("-------------------------- ")
        logging.debug("SIM RUN:  " + str(sim_yr))
        logging.debug("-------------------------- ")

        #-------------PROFILER
        if instrument_profiler:
            profiler = Profiler(use_signal=False)
            profiler.start()

        model_run_object = energy_demand_model(data)

        if instrument_profiler:
            profiler.stop()
            logging.debug("Profiler Results")
            print(profiler.output_text(unicode=True, color=True))

        results_every_year.append(model_run_object)

        # FUEL PER REGION
        out_to_supply = model_run_object.fuel_indiv_regions_yh
        
        # ----------------------
        # CLUSTER CALCULATIONS
        # ----------------------
        # Write out result of year (Year_Region.txt)

        # ---------------------------------------------------
        # Validation of national electrictiy demand for base year
        # ---------------------------------------------------
        winter_week = list(range(date_handling.date_to_yearday(2015, 1, 12), date_handling.date_to_yearday(2015, 1, 19))) #Jan
        spring_week = list(range(date_handling.date_to_yearday(2015, 5, 11), date_handling.date_to_yearday(2015, 5, 18))) #May
        summer_week = list(range(date_handling.date_to_yearday(2015, 7, 13), date_handling.date_to_yearday(2015, 7, 20))) #Jul
        autumn_week = list(range(date_handling.date_to_yearday(2015, 10, 12), date_handling.date_to_yearday(2015, 10, 19))) #Oct

        days_to_plot = winter_week + spring_week + summer_week + autumn_week
        days_to_plot_full_year = list(range(0, 365))

        # ------------------------------
        # Compare total gas and electrictiy
        # load with Elexon Data for Base year for different regions
        # ------------------------------
        temporal_validation = False
        if temporal_validation == True:
            validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO = elec_national_data.read_raw_elec_2015_data(
                data['local_paths']['folder_validation_national_elec_data'])

            logging.debug("Loaded validation data elec demand. ND:  {}   TSD: {}".format(np.sum(validation_elec_data_2015_INDO), np.sum(validation_elec_data_2015_ITSDO)))
            logging.debug("--ECUK Elec_demand  {} ".format(np.sum(model_run_object.reg_enduses_fueltype_y[2])))
            logging.debug("--ECUK Gas Demand   {} ".format(np.sum(model_run_object.reg_enduses_fueltype_y[1])))
            diff_factor_TD_ECUK_Input = (1.0 / np.sum(validation_elec_data_2015_INDO)) * np.sum(model_run_object.reg_enduses_fueltype_y[2]) # 1.021627962194478
            logging.debug("FACTOR: " + str(diff_factor_TD_ECUK_Input))

            INDO_factoreddata = diff_factor_TD_ECUK_Input * validation_elec_data_2015_INDO
            logging.debug("CORRECTED DEMAND:  {} ".format(np.sum(INDO_factoreddata)))

            # Compare different models
            elec_national_data.compare_results('plot_figure_01.pdf', data, validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.reg_enduses_fueltype_y[2], 'all_submodels', days_to_plot_full_year)

            logging.debug("FUEL gwh TOTAL  validation_elec_data_2015_INDO:  {} validation_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(validation_elec_data_2015_INDO), np.sum(validation_elec_data_2015_ITSDO), np.sum(model_run_object.reg_enduses_fueltype_y[2])))
            logging.debug("FUEL ktoe TOTAL  validation_elec_data_2015_INDO: {} validation_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(validation_elec_data_2015_INDO)/11.63, np.sum(validation_elec_data_2015_ITSDO)/11.63, np.sum(model_run_object.reg_enduses_fueltype_y[2])/11.63))

        # ---------------------------------------------------
        # Validation of spatial disaggregation
        # ---------------------------------------------------
        spatial_validation = False
        if spatial_validation == True:
            lad_infos_shapefile = data_loader.load_LAC_geocodes_info(
                data['local_paths']['path_dummy_regions']
            )
            lad_validation.compare_lad_regions(
                'compare_lad_regions.pdf',
                data,
                lad_infos_shapefile,
                model_run_object,
                data['lookups']['nr_of_fueltypes'],
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
                validation_elec_data_2015_INDO,
                model_run_object.reg_enduses_fueltype_y[peak_month][peak_day]
                )

            logging.debug("...compare peak from max peak factors")
            elec_national_data.compare_peak(
                "peak_comparison_02.pdf",
                data,
                validation_elec_data_2015_INDO,
                model_run_object.tot_peak_enduses_fueltype[2])

            # ---------------------------------------------------
            # Validate boxplots for every hour
            # ---------------------------------------------------
            elec_national_data.compare_results_hour_boxplots(
                "hourly_boxplots_01.pdf",
                data,
                validation_elec_data_2015_INDO,
                model_run_object.reg_enduses_fueltype_y[2])

    # ------------------------------
    # Plotting
    # ------------------------------
    
    # Plot load factors
    ##pf.plot_load_curves_fueltype(results_every_year, data)

    # Plot total fuel (y) per fueltype
    plotting_results.plt_fuels_enduses_y("fig_tot_all_enduse01.pdf", results_every_year, data, 'rs_tot_fuels_all_enduses_y')
    plotting_results.plt_fuels_enduses_y("fig_tot_all_enduse02.pdf", results_every_year, data, 'rs_tot_fuels_all_enduses_y')

    # Plot peak demand (h) per fueltype
    plotting_results.plt_fuels_peak_h(results_every_year, data, 'tot_fuel_y_max_allenduse_fueltyp')

    # Plot a full week
    plotting_results.plt_fuels_enduses_week("fig_tot_all_enduse03.pdf", results_every_year, data, 'rs_tot_fuels_all_enduses_y', data['assumptions']['nr_ed_modelled_dates'])
    plotting_results.plt_fuels_enduses_week("fig_tot_all_enduse04.pdf", results_every_year, data, 'rs_tot_fuels_all_enduses_y', data['assumptions']['nr_ed_modelled_dates'])

    # Plot all enduses
    plotting_results.plt_stacked_enduse("figure_stacked_country_final.pdf", data, results_every_year, data['enduses']['rs_all_enduses'], 'tot_fuel_y_enduse_specific_h')
    
    logging.debug("... Finished running Energy Demand Model")
