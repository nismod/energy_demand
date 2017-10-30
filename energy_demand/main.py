'''
Energy Demand Model
===================
- run in constrained mode
- run with same weather shape and same fuel input --> flat line expected

Development checklist: https://nismod.github.io/docs/development-checklist.html
https://nismod.github.io/docs/
TODO: REplace 1 and zero by fueltypes test_fuel_switch 
TODO: Simplify load profiles (they are non-regional now)
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
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import conversions
from energy_demand.profiles import generic_shapes
from energy_demand.validation import lad_validation
from energy_demand.plotting import plotting_results
from energy_demand.basic import logger_setup
from energy_demand.read_write import write_data
from energy_demand.basic import basic_functions
from energy_demand.technologies import fuel_service_switch

def energy_demand_model(data, fuel_in=0, fuel_in_elec=0):
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
        data=data)

    logging.info("Fuel input:          " + str(fuel_in))
    logging.info("================================================")
    logging.info("Simulation year:     " + str(model_run_object.curr_yr))
    logging.info("Number of regions    " + str(len(data['lu_reg'])))
    logging.info("Fuel input:          " + str(fuel_in))
    logging.info("Fuel output:         " + str(np.sum(model_run_object.reg_enduses_fueltype_y)))
    logging.info("FUEL DIFFERENCE:     " + str(round(
        (np.sum(model_run_object.reg_enduses_fueltype_y) - fuel_in), 4)))
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
    if len(sys.argv) != 2:
        print("Please provide a local data path:")
        print("    python main.py ../energy_demand_data\n")
        print("... Defaulting to C:/DATA_NISMODII/data_energy_demand")
        local_data_path = os.path.abspath('C:/DATA_NISMODII/data_energy_demand')
    else:
        local_data_path = sys.argv[1]

    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_energy_demand.log"))
    logging.info("... start local energy demand calculations")

    # Run settings
    instrument_profiler = True
    print_criteria = True
    validation_criteria = False

    # Load data
    data = {}
    data['print_criteria'] = print_criteria
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()

    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'], data['assumptions'] = base_assumptions.load_assumptions(
        data['paths'], data['enduses'], data['lookups'], write_sim_param=True)

    #NEW ABSOLUTE assumptions['rs_service_switches']
    data['assumptions'] = fuel_service_switch.generate_fuel_switches_from_absolute(
        data['paths'],
        data['enduses'],
        data['assumptions'], data['fuels'], data['sim_param'])
    #print("---------")
    #print(data['assumptions']['rs_service_switches'])
    #prnt("l.")

    data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])
    data['assumptions'] = base_assumptions.update_assumptions(data['assumptions'])
    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])
    data = data_loader.dummy_data_generation(data)
    data['scenario_data'] = {'gva': data['gva'], 'population': data['population']}

    logging.info("Start Energy Demand Model with python version: " + str(sys.version))
    logging.info("Info model run")
    logging.info("Nr of Regions " + str(len(data['lu_reg'])))

    # In order to load these data, the initialisation scripts need to be run
    logging.info("... Load data from script calculations")
    data = read_data.load_script_data(data)

    #--------------------
    # Folder cleaning
    #--------------------
    logging.info("... delete previous model run results")
    basic_functions.del_previous_setup(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results_PDF'])

    for sim_yr in data['sim_param']['sim_period']:
        data['sim_param']['curr_yr'] = sim_yr

        logging.debug("SIMULATION RUN--------------:  " + str(sim_yr))
        fuel_in, fuel_in_elec = testing.test_function_fuel_sum(data)

        #-------------PROFILER
        if instrument_profiler:
            profiler = Profiler(use_signal=False)
            profiler.start()

        # Main model run function
        model_run_object = energy_demand_model(
            data,
            fuel_in,
            fuel_in_elec)

        if instrument_profiler:
            profiler.stop()
            logging.debug("Profiler Results")
            print(profiler.output_text(unicode=True, color=True))

        # Take attributes from model object run
        out_to_supply = model_run_object.fuel_indiv_regions_yh
        out_enduse_specific = model_run_object.tot_fuel_y_enduse_specific_h
        tot_peak_enduses_fueltype = model_run_object.tot_peak_enduses_fueltype
        tot_fuel_y_max_enduses = model_run_object.tot_fuel_y_max_enduses
        reg_enduses_fueltype_y = model_run_object.reg_enduses_fueltype_y
        rs_reg_load_factor_h = model_run_object.rs_reg_load_factor_h

        # -------------------------------------------
        # Write annual results to txt files
        # -------------------------------------------
        logging.info("... Start writing results to file")

        write_data.write_model_result_to_txt(
            sim_yr, data['local_paths']['data_results_model_runs'], out_to_supply)
        write_data.write_model_result_to_txt_enduse(
            sim_yr, data['local_paths']['data_results_model_runs'], out_enduse_specific)
        write_data.write_model_result_to_txt_maxresults(
            sim_yr, data['local_paths']['data_results_model_runs'], tot_peak_enduses_fueltype)
        write_data.write_load_factors(
            data['local_paths']['data_results_model_runs'], "result_load_factors", [sim_yr], rs_reg_load_factor_h)

        logging.info("... Finished writing results to file")

        # ------------------------------------------------
        # Validation base year: Hourly temporal validation
        # ------------------------------------------------
        if validation_criteria: # == True:

            # Add electricity for transportation sector
            fuel_electricity_year_validation = 385
            fuel_national_tranport = np.zeros((data['lookups']['fueltypes_nr']), dtype=float)
            fuel_national_tranport[data['lookups']['fueltype']['electricity']] = conversions.ktoe_to_gwh(
                fuel_electricity_year_validation) #Elec demand from ECUK for transport sector
            model_object_transport = generic_shapes.GenericFlatEnduse(
                fuel_national_tranport, data['assumptions']['model_yeardays_nrs'])

            lad_validation.temporal_validation(
                data,
                model_run_object.reg_enduses_fueltype_y + model_object_transport.fuel_yh)

            # --------------------------------------------
            # Validation base year: Spatial disaggregation
            # --------------------------------------------
            lad_validation.spatial_validation(
                data, model_run_object.reg_enduses_fueltype_y + model_object_transport.fuel_yh,
                model_run_object.tot_peak_enduses_fueltype + model_object_transport.fuel_peak_dh)

    # --------------------------------------------
    # Reading in results from different model runs
    # --------------------------------------------
    logging.info("... Reading in results")

    results_every_year = read_data.read_model_result_from_txt(
        data['lookups']['fueltype'],
        data['lookups']['fueltypes_nr'],
        len(data['lu_reg']),
        data['local_paths']['data_results_model_runs'])

    results_enduse_every_year = read_data.read_enduse_specific_model_result_from_txt(
        data['lookups']['fueltypes_nr'],
        data['local_paths']['data_results_model_runs'])

    tot_fuel_y_max = read_data.read_max_results(
        data['local_paths']['data_results_model_runs'])

    load_factors_y = read_data.read_lf_y(
        os.path.join(data['local_paths']['data_results_model_runs'], "result_load_factors"))

    logging.info("... Reading in results finished")

    # ------------------------------
    # Plotting
    # ------------------------------
    logging.info("... plotting results")

    plotting_results.run_all_plot_functions(
        results_every_year,
        results_enduse_every_year,
        tot_fuel_y_max,
        data,
        load_factors_y)

    logging.info("... Finished running Energy Demand Model")
