'''
Energy Demand Model
===================
The industry heating is identical to service heating
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
from energy_demand.basic import conversions
from energy_demand.profiles import generic_shapes
from energy_demand.validation import lad_validation
from energy_demand.plotting import plotting_results
from energy_demand.basic import logger_setup as log
from energy_demand.read_write import write_data

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
    model_run_object = energy_model.EnergyModel(
        region_names=data['lu_reg'],
        data=data
        )

    # Total annual fuel of all regions
    fueltot = model_run_object.reg_enduses_fueltype_y

    # Print out calculations
    fuel_in, fuel_in_elec = testing.test_function_fuel_sum(data)
    logging.info("Fuel input:          " + str(fuel_in))
    logging.info("================================================")
    logging.info("Simulation year:     " + str(model_run_object.curr_yr))
    logging.info("Number of regions    " + str(len(data['lu_reg'])))
    logging.info("Fuel input:          " + str(fuel_in))
    logging.info("Fuel output:         " + str(np.sum(fueltot)))
    logging.info("FUEL DIFFERENCE:     " + str(round((np.sum(fueltot) - fuel_in), 4)))
    logging.info("elec fuel in:        " + str(fuel_in_elec))
    logging.info("elec fuel out:       " + str(np.sum(model_run_object.reg_enduses_fueltype_y[data['lookups']['fueltype']['electricity']])))
    logging.info("ele fueld diff:      " + str(round(fuel_in_elec - np.sum(model_run_object.reg_enduses_fueltype_y[data['lookups']['fueltype']['electricity']]), 4)))
    logging.info("================================================")
    logging.debug("...finished energy demand model simulation")
    return model_run_object

if __name__ == "__main__":
    """
    """
    # Paths
    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    local_data_path = os.path.join(r'C:\DATA_NISMODII', 'data_energy_demand')

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
    data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])
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
            logging.info(profiler.output_text(unicode=True, color=True))

        # FUEL PER REGION
        out_to_supply = model_run_object.fuel_indiv_regions_yh
        out_enduse_specific = model_run_object.tot_fuel_y_enduse_specific_h

        # ----------------------
        # Write annual results to txt files
        # ----------------------
        write_data.write_model_result_to_txt(
            sim_yr,
            data['local_paths']['data_results_model_runs'],
            out_to_supply)

        #Write fuel per enduse (for all regions)
        write_data.write_model_result_to_txt_enduse(
            sim_yr,
            data['local_paths']['data_results_model_runs'],
            out_enduse_specific)

        # ---------------------------------------------------
        # Validation base year: Hourly temporal validation
        # ---------------------------------------------------
        fuel_electricity_year_validation = 385
        fuel_national_tranport = np.zeros((data['lookups']['fueltypes_nr']))
        fuel_national_tranport[data['lookups']['fueltype']['electricity']] = conversions.ktoe_to_gwh(
            fuel_electricity_year_validation) #Elec demand from ECUK for transport sector
        model_object_transport = generic_shapes.GenericFlatEnduse(
            fuel_national_tranport, data['assumptions']['model_yeardays_nrs'])

        ##lad_validation.temporal_validation(data, model_run_object.reg_enduses_fueltype_y + model_object_transport.fuel_yh)

        # ---------------------------------------------------
        # Validation base year: Spatial disaggregation
        # ---------------------------------------------------
        ##lad_validation.spatial_validation(data, model_run_object + model_object_transport.fuel_yh)

    # -------------------------------------------------------
    # Reading in results from different model runs
    # -------------------------------------------------------
    results_every_year = read_data.read_model_result_from_txt(
        data['lookups']['fueltype'], data['lookups']['fueltypes_nr'],
        len(data['lu_reg']),
        data['local_paths']['data_results_model_runs'])

    results_enduse_every_year = read_data.read_enduse_specific_model_result_from_txt(
        data['lookups']['fueltype'], data['lookups']['fueltypes_nr'],
        data['local_paths']['data_results_model_runs'])

    logging.debug("... Reading in results finished")
    # ------------------------------
    # Plotting
    # ------------------------------
    plotting_results.run_all_plot_functions(
        results_every_year,
        results_enduse_every_year,
        data)

    logging.debug("... Finished running Energy Demand Model")
