'''
Energy Demand Model
===================
- run in constrained mode
- run with same weather shape and same fuel input --> flat line expected
- Test why lf in summer is higher than in winter
Development checklist: https://nismod.github.io/docs/development-checklist.html
https://nismod.github.io/docs/
https://nismod.github.io/docs/smif-prerequisites.html#sector-modeller
'''
import os
import sys
import logging
import numpy as np
from energy_demand import energy_model
from energy_demand.basic import testing_functions as testing

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
    fuel_in, fuel_in_elec, fuel_in_gas = testing.test_function_fuel_sum(data)

    model_run_object = energy_model.EnergyModel(
        region_names=data['lu_reg'],
        data=data)

    print("Fuel input:          " + str(fuel_in))
    print("================================================")
    print("Simulation year:     " + str(model_run_object.curr_yr))
    print("Number of regions    " + str(data['reg_nrs']))
    print("Fuel input:          " + str(fuel_in))
    print("Fuel output:         " + str(np.sum(model_run_object.ed_fueltype_national_yh)))
    print("FUEL DIFFERENCE:     " + str(round((np.sum(model_run_object.ed_fueltype_national_yh) - fuel_in), 4)))
    print("--")
    print("elec fuel in:        " + str(fuel_in_elec))
    print("elec fuel out:       " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']])))
    print("ele fuel diff:       " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']]), 4) - fuel_in_elec))
    print("--")
    print("gas fuel in:         " + str(fuel_in_gas))
    print("gas fuel out:        " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['gas']])))
    print("gas diff:            " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['gas']]), 4) - fuel_in_gas))
    print("--")
    print("Diff elec %:         " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['electricity']]), 4))) * fuel_in_elec))
    print("Diff gas %:          " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltype']['gas']]), 4))) * fuel_in_gas))
    print("================================================")

    logging.info("...finished running energy demand model simulation")

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

    # -------------- SCRAP
    from pyinstrument import Profiler
    from energy_demand.assumptions import non_param_assumptions, param_assumptions
    from energy_demand.read_write import data_loader
    from energy_demand.validation import lad_validation
    from energy_demand.basic import logger_setup
    from energy_demand.read_write import write_data, read_data
    from energy_demand.basic import basic_functions
    from energy_demand.basic import date_prop

    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_local_run.log"))

    # Run settings
    instrument_profiler = True
    validation_criteria = False
    virtual_building_stock_criteria = True

    # Load data
    data = {}
    data['criterias'] = {}
    data['criterias']['plot_HDD_chart'] = False
    data['criterias']['virtual_building_stock_criteria'] = virtual_building_stock_criteria

    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], data['all_sectors'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015
    data['sim_param']['simulated_yrs'] = [2015, 2018, 2025, 2050]

    # ------------------------------
    # Assumptions
    # ------------------------------
    # Parameters not defined within smif
    data['assumptions'] = non_param_assumptions.load_non_param_assump(
        data['sim_param']['base_yr'], data['paths'], data['enduses'], data['lookups'], data['fuels'])

    # Parameters defined within smif
    param_assumptions.load_param_assump(data['paths'], data['assumptions'])

    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

    data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions']['model_yeardays'], data['assumptions']['model_yeardays_daytype'])
    data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(data['assumptions']['technologies'], data['assumptions']['eff_achiev_f']['factor_achieved'])
    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])

    data['lu_reg'] = data_loader.load_LAC_geocodes_info(data['local_paths']['path_dummy_regions'])
    data['reg_nrs'] = len(data['lu_reg'])

    # ------------------------------
    data['rs_floorarea_2015_virtual_bs'], data['ss_floorarea_sector_2015_virtual_bs'] = data_loader.virtual_building_datasets(data['lu_reg'], data['all_sectors'])
    
    # GVA
    gva_data = {}
    for year in range(2015, 2101):
        gva_data[year] = {}
        for region_geocode in data['lu_reg']:
            gva_data[year][region_geocode] = 999
    data['gva'] = gva_data

    # Population
    pop_dummy = {}
    for year in range(2015, 2101):
        _data = {}
        for reg_geocode in data['lu_reg']:
            _data[reg_geocode] = data['lu_reg'][reg_geocode]['POP_JOIN']
        pop_dummy[year] = _data
    data['population'] = pop_dummy

    # Residenital floor area
    rs_floorarea = {}
    for year in range(2015, 2101):
        rs_floorarea[year] = {}
        for region_geocode in data['lu_reg']:
            rs_floorarea[year][region_geocode] = 10000
    data['rs_floorarea_newcastle'] = rs_floorarea

    data['coord_dummy'] = {}
    for reg in data['lu_reg']:
        data['coord_dummy'][reg] = {'longitude': 52.58, 'latitude': -1.091}

    #Scenario data
    data['scenario_data'] = {
        'gva': data['gva'],
        'population': data['population'],
        'floor_area': {
            'rs_floorarea_newcastle': data['rs_floorarea_newcastle']}}

    logging.info("Start Energy Demand Model with python version: " + str(sys.version))
    logging.info("Info model run")
    logging.info("Nr of Regions " + str(data['reg_nrs']))

    # In order to load these data, the initialisation scripts need to be run
    logging.info("... Load data from script calculations")
    data = read_data.load_script_data(data)

    #-------------------
    # Folder cleaning
    #--------------------
    logging.info("... delete previous model run results")
    basic_functions.del_previous_setup(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results_PDF'])

    # Create .ini file with simulation information
    write_data.write_simulation_inifile(
        data['local_paths']['data_results'],
        data['sim_param'],
        data['enduses'],
        data['assumptions'],
        data['reg_nrs'],
        data['lu_reg'])

    for sim_yr in data['sim_param']['simulated_yrs']:
        data['sim_param']['curr_yr'] = sim_yr

        logging.info("Simulation for year --------------:  " + str(sim_yr))
        fuel_in, fuel_in_elec, fuel_in_gas = testing.test_function_fuel_sum(data)

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
        supply_results = model_run_object.ed_fueltype_regs_yh
        ed_fueltype_regs_yh = model_run_object.ed_fueltype_regs_yh
        out_enduse_specific = model_run_object.tot_fuel_y_enduse_specific_h
        tot_peak_enduses_fueltype = model_run_object.tot_peak_enduses_fueltype
        tot_fuel_y_max_enduses = model_run_object.tot_fuel_y_max_enduses
        ed_fueltype_national_yh = model_run_object.ed_fueltype_national_yh

        reg_load_factor_y = model_run_object.reg_load_factor_y
        reg_load_factor_yd = model_run_object.reg_load_factor_yd
        reg_load_factor_winter = model_run_object.reg_load_factor_seasons['winter']
        reg_load_factor_spring = model_run_object.reg_load_factor_seasons['spring']
        reg_load_factor_summer = model_run_object.reg_load_factor_seasons['summer']
        reg_load_factor_autumn = model_run_object.reg_load_factor_seasons['autumn']

        # -------------------------------------------
        # Write annual results to txt files
        # -------------------------------------------
        logging.info("... Start writing results to file")
        path_runs = data['local_paths']['data_results_model_runs']

        write_data.write_supply_results(
            sim_yr, path_runs, supply_results, "supply_results")
        write_data.write_enduse_specific(
            sim_yr, path_runs, out_enduse_specific, "out_enduse_specific")
        write_data.write_max_results(
            sim_yr, path_runs, "result_tot_peak_enduses_fueltype", tot_peak_enduses_fueltype, "tot_peak_enduses_fueltype")
        write_data.write_lf(
            path_runs, "result_reg_load_factor_y", [sim_yr], reg_load_factor_y, 'reg_load_factor_y')
        write_data.write_lf(
            path_runs, "result_reg_load_factor_yd", [sim_yr], reg_load_factor_yd, 'reg_load_factor_yd')

        write_data.write_lf(path_runs, "result_reg_load_factor_winter", [sim_yr], reg_load_factor_winter, 'reg_load_factor_winter')
        write_data.write_lf(path_runs, "result_reg_load_factor_spring", [sim_yr], reg_load_factor_spring, 'reg_load_factor_spring')
        write_data.write_lf(path_runs, "result_reg_load_factor_summer", [sim_yr], reg_load_factor_summer, 'reg_load_factor_summer')
        write_data.write_lf(path_runs, "result_reg_load_factor_autumn", [sim_yr], reg_load_factor_autumn, 'reg_load_factor_autumn')

        logging.info("... Finished writing results to file")

    logging.info("... Finished running Energy Demand Model")
