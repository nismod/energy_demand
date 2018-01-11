"""
Energy Demand Model
===================
Contains the function `energy_demand_model` which is used
to run the energy demand model

Development checklist: https://nismod.github.io/docs/development-checklist.html
https://nismod.github.io/docs/
https://nismod.github.io/docs/smif-prerequisites.html#sector-modeller
# Implement that e.g. 2015 - 2030 one technology and 2030 - 2050 another technology
# backcasting
# Industry INFO about efficiencies & technologies: Define strategy variables
# Cooling?
# convert documentation in rst?
# CORRECT OUTPUTS (per tech)
# Potentiall load other annual profiles?
averaged_temp
"""
import os
import sys
import logging
import numpy as np
from energy_demand import model
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
        [fueltype : region : timestep]
    model_run_object : dict
        Object of a yearly model run

    Note
    ----
    This function is executed in the wrapper
    """
    fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydrogen, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
        data, data['criterias']['mode_constrained'],
        data['assumptions']['enduse_space_heating'])

    model_run_object = model.EnergyDemandModel(
        regions=data['lu_reg'],
        data=data)

    for fueltype in data['lookups']['fueltypes']:
        print("Fueltype: {}   {}".format(fueltype, np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes'][fueltype]])))

    print("Fuel input:          " + str(fuel_in))
    print("================================================")
    print("Simulation year:     " + str(model_run_object.curr_yr))
    print("Number of regions    " + str(data['reg_nrs']))
    print("Total fuel input:    " + str(fuel_in))
    print("Total output:        " + str(np.sum(model_run_object.ed_fueltype_national_yh)))
    print("Total difference:    " + str(round((np.sum(model_run_object.ed_fueltype_national_yh) - fuel_in), 4)))
    print("-----------")
    print("oil fuel in:         " + str(fuel_in_oil))
    print("oil fuel out:        " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']])))
    print("oil diff:            " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']]), 4) - fuel_in_oil))
    print("-----------")
    print("biomass fuel in:     " + str(fuel_in_biomass))
    print("biomass fuel out:    " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']])))
    print("biomass diff:        " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']]), 4) - fuel_in_biomass))
    print("-----------")
    print("solid_fuel fuel in:  " + str(fuel_in_solid_fuel))
    print("solid_fuel fuel out: " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']])))
    print("solid_fuel diff:     " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']]), 4) - fuel_in_solid_fuel))
    print("-----------")
    print("elec fuel in:        " + str(fuel_in_elec))
    print("elec fuel out:       " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']])))
    print("ele fuel diff:       " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']]), 4) - fuel_in_elec))
    print("-----------")
    print("gas fuel in:         " + str(fuel_in_gas))
    print("gas fuel out:        " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']])))
    print("gas diff:            " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']]), 4) - fuel_in_gas))
    print("-----------")
    print("hydro fuel in:       " + str(fuel_in_hydrogen))
    print("hydro fuel out:      " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']])))
    print("hydro diff:          " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']]), 4) - fuel_in_hydrogen))
    print("-----------")
    print("TOTAL HEATING        " + str(tot_heating))
    print("heat fuel in:        " + str(fuel_in_heat))
    print("heat fuel out:       " + str(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']])))
    print("heat diff:           " + str(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']]), 4) - fuel_in_heat))
    print("-----------")
    print("Diff elec %:         " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']]), 4))) * fuel_in_elec))
    print("Diff gas %:          " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']]), 4))) * fuel_in_gas))
    print("Diff oil %:          " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']]), 4))) * fuel_in_oil))
    print("Diff solid_fuel %:   " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']]), 4))) * fuel_in_solid_fuel))
    print("Diff hydrogen %:     " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']]), 4))) * fuel_in_hydrogen))
    print("Diff biomass %:      " + str((1/(round(np.sum(model_run_object.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']]), 4))) * fuel_in_biomass))
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
        ##local_data_path = os.path.abspath('C:/Users/cenv0553/nismod/data_energy_demand')
    else:
        local_data_path = sys.argv[1]

    # -------------- SCRAP
    from pyinstrument import Profiler
    from energy_demand.assumptions import non_param_assumptions
    from energy_demand.assumptions import param_assumptions
    from energy_demand.read_write import data_loader
    from energy_demand.basic import logger_setup
    from energy_demand.read_write import write_data
    from energy_demand.read_write import read_data
    from energy_demand.basic import basic_functions
    from energy_demand.basic import date_prop

    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_local_run.log"))

    # Run settings
    instrument_profiler = True

    # Load data
    data = {}
    data['criterias'] = {}
    data['criterias']['mode_constrained'] = True #constrained_by_technologies
    data['criterias']['plot_HDD_chart'] = False
    data['criterias']['virtual_building_stock_criteria'] = True
    data['criterias']['spatial_exliclit_diffusion'] = True

    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015
    data['sim_param']['curr_yr'] = data['sim_param']['base_yr']
    data['sim_param']['simulated_yrs'] = [2015, 2050]

    data['lu_reg'] = data_loader.load_LAC_geocodes_info(os.path.join(local_data_path, '_raw_data', 'B-census_data', 'regions_local_area_districts', '_quick_and_dirty_spatial_disaggregation', 'infuse_dist_lyr_2011_saved.csv'))

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

    data['reg_coord'] = {}
    for reg in data['lu_reg']:
        data['reg_coord'][reg] = {'longitude': 52.58, 'latitude': -1.091}

    # ------------------------------
    # Assumptions
    # ------------------------------
    # Parameters not defined within smif
    data['assumptions'] = non_param_assumptions.load_non_param_assump(
        data['sim_param']['base_yr'], data['paths'], data['enduses'], data['lookups'])

    # Parameters defined within smif
    param_assumptions.load_param_assump(data['paths'], data['assumptions'])

    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

    data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions']['model_yeardays'], data['assumptions']['model_yeardays_daytype'])
    data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
        data['assumptions']['technologies'],
        data['assumptions']['strategy_variables']['eff_achiev_f'],
        data['assumptions']['strategy_variables']['split_hp_gshp_to_ashp_ey'])

    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])

    data['reg_nrs'] = len(data['lu_reg'])

    # ------------------------------
    if data['criterias']['virtual_building_stock_criteria']:
        rs_floorarea, ss_floorarea = data_loader.virtual_building_datasets(
            data['lu_reg'],
            data['sectors']['all_sectors'],
            data['local_paths'])

    #Scenario data
    data['scenario_data'] = {
        'gva': data['gva'],
        'population': data['population'],
        'floor_area': {
            'rs_floorarea': rs_floorarea,
            'ss_floorarea': ss_floorarea}}

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
    basic_functions.create_folder(data['local_paths']['data_results'], "model_run_pop")

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
        fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydro, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
            data,
            data['criterias']['mode_constrained'],
            data['assumptions']['enduse_space_heating'])

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

        # --------------------
        # Result unconstrained
        # --------------------

        #supply_results = model_run_object.ed_fueltype_regs_yh #TODO: NEEDED?
        supply_results_unconstrained = model_run_object.ed_fueltype_submodel_regs_yh #TODO: NEEDED?

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

        # Write unconstrained results
        write_data.write_supply_results(['rs_submodel', 'ss_submodel', 'is_submodel'], sim_yr, path_runs, supply_results_unconstrained, "supply_results")

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

        # -------------------------------------------
        # Write population files of simulation year
        # -------------------------------------------
        pop_array_reg = np.zeros((len(data['lu_reg'])))
        for reg_array_nr, reg in enumerate(data['lu_reg']):
            pop_array_reg[reg_array_nr] = data['scenario_data']['population'][sim_yr][reg]

        write_data.write_pop(
            sim_yr,
            data['local_paths']['data_results'],
            pop_array_reg)
        logging.info("... Finished writing results to file")

    logging.info("... Finished running Energy Demand Model")
    print("... Finished running Energy Demand Model")
