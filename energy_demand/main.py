"""Allows to run HIRE locally outside the SMIF framework

    Tools
    # -------
    Profiling:  https://jiffyclub.github.io/snakeviz/
    python -m cProfile -o program.prof main.py
    snakeviz program.prof
"""
import os
import sys
import time
import logging
import numpy as np
from energy_demand import model
from energy_demand.basic import testing_functions
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import non_param_assumptions
from energy_demand.assumptions import param_assumptions
from energy_demand.read_write import data_loader
from energy_demand.basic import logger_setup
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.basic import basic_functions
from energy_demand.scripts import s_disaggregation

def energy_demand_model(regions, data, assumptions):
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
    modelrun_obj : dict
        Object of a yearly model run

    Note
    ----
    This function is executed in the wrapper
    """
    modelrun = model.EnergyDemandModel(
        regions=regions, #data['regions'],
        data=data,
        assumptions=assumptions)

    # Calculate base year demand
    fuels_in = testing_functions.test_function_fuel_sum(
        data,
        data['fuel_disagg'],
        data['criterias']['mode_constrained'],
        assumptions.enduse_space_heating)

    # Log model results
    write_data.logg_info(modelrun, fuels_in, data)
    logging.info("...finished running energy demand model simulation")
    return modelrun

if __name__ == "__main__":
    """
    """
    data = {}

    # Paths
    if len(sys.argv) != 2:
        print("Please provide a local data path:")
        #local_data_path = os.path.abspath(
        #    os.path.join(
        #        os.path.dirname(__file__), "..", "..", "data"))

        local_data_path = os.path.abspath('C:/users/cenv0553/ED/data')
    else:
        local_data_path = sys.argv[1]

    path_main = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', "energy_demand/config_data"))

    # Initialise logger
    #logger_setup.set_up_logger(os.path.join(local_data_path, "..", "logging_local_run.log"))
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_local_run.log"))

    # Load data
    data['criterias'] = {}
    data['criterias']['mode_constrained'] = True                    # True: Technologies are defined in ED model and fuel is provided, False: Heat is delievered not per technologies
    data['criterias']['virtual_building_stock_criteria'] = True     # True: Run virtual building stock model

    fast_model_run = False
    if fast_model_run == True:
        data['criterias']['write_to_txt'] = False
        data['criterias']['beyond_supply_outputs'] = False
        data['criterias']['validation_criteria'] = False    # For validation, the mode_constrained must be True
        data['criterias']['plot_tech_lp'] = False
        data['criterias']['plot_crit'] = False
        data['criterias']['crit_plot_enduse_lp'] = False
        data['criterias']['plot_HDD_chart'] = False
        data['criterias']['writeYAML'] = False
    else:
        data['criterias']['write_to_txt'] = True
        data['criterias']['beyond_supply_outputs'] = True
        data['criterias']['validation_criteria'] = True
        data['criterias']['plot_tech_lp'] = False
        data['criterias']['plot_crit'] = False
        data['criterias']['crit_plot_enduse_lp'] = True
        data['criterias']['plot_HDD_chart'] = False
        data['criterias']['writeYAML'] = True #set to false

    # ----------------------------
    # Model running configurations
    # ----------------------------
    simulated_yrs = [2015]
    name_scenario_run = "_result_data_{}".format(str(time.ctime()).replace(":", "_").replace(" ", "_"))

    # Paths
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.get_local_paths(local_data_path)
    data['result_paths'] = data_loader.get_result_paths(
        os.path.join(os.path.join(local_data_path, "..", "results"), name_scenario_run))

    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

    data['regions'] = data_loader.load_regions_localmodelrun(
        os.path.join(local_data_path, 'region_definitions', 'regions_local_modelrun.csv'))

    data['reg_nrs'] = len(data['regions'])

    data['population'] = data_loader.read_scenario_data(
        os.path.join(local_data_path, 'scenarios', 'uk_pop_high_migration_2015_2050.csv'))

    data['gva'] = data_loader.read_scenario_data(
        os.path.join(local_data_path, 'scenarios', 'gva_sven.csv'))

    data['industry_gva'] = "TST"

    #Dummy data
    pop_density = {}
    data['reg_coord'] = {}
    for reg in data['regions']:
        data['reg_coord'][reg] = {'longitude': 52.58, 'latitude': -1.091}
        pop_density[reg] = 1
    data['pop_density'] = pop_density

    # ------------------------------
    # Assumptions
    # ------------------------------
    # Parameters not defined within smif
    data['assumptions'] = non_param_assumptions.Assumptions(
        base_yr=2015,
        curr_yr=2015,
        simulated_yrs=simulated_yrs,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        fueltypes=data['lookups']['fueltypes'],
        fueltypes_nr=data['lookups']['fueltypes_nr'])

    # Parameters defined within smif
    strategy_variables = param_assumptions.load_param_assump(
        data['paths'], data['local_paths'], data['assumptions'])
    data['assumptions'].update('strategy_variables', strategy_variables)

    data['tech_lp'] = data_loader.load_data_profiles(
        data['paths'], data['local_paths'],
        data['assumptions'].model_yeardays,
        data['assumptions'].model_yeardays_daytype,
        data['criterias']['plot_tech_lp'])

    technologies = non_param_assumptions.update_technology_assumption(
        data['assumptions'].technologies,
        data['assumptions'].strategy_variables['f_eff_achieved']['scenario_value'],
        data['assumptions'].strategy_variables['gshp_fraction_ey']['scenario_value'])
    data['technologies'] = technologies

    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])

    # ------------------------------

    if data['criterias']['virtual_building_stock_criteria']:
        rs_floorarea, ss_floorarea, data['service_building_count'], rs_regions_without_floorarea, ss_regions_without_floorarea = data_loader.floor_area_virtual_dw(
            data['regions'],
            data['sectors']['all_sectors'],
            data['local_paths'],
            data['population'][data['assumptions'].base_yr],
            data['assumptions'].base_yr)

        # Add all areas with no floor area data
        data['assumptions'].update("rs_regions_without_floorarea", rs_regions_without_floorarea)
        data['assumptions'].update("ss_regions_without_floorarea", ss_regions_without_floorarea)
    # Lookup table to import industry sectoral gva
    lookup_tables.industrydemand_name_sic2007()

    #Scenario data
    data['scenario_data'] = {
        'gva': data['gva'],
        'population': data['population'],
        'industry_gva': data['industry_gva'],
        'floor_area': {
            'rs_floorarea': rs_floorarea,
            'ss_floorarea': ss_floorarea}}

    print("Start Energy Demand Model with python version: " + str(sys.version))
    print("Info model run")
    print("Nr of Regions " + str(data['reg_nrs']))

    # --------------------
    # Disaggregate fuel
    # --------------------
    data['fuel_disagg'] = s_disaggregation.disaggregate_demand(data)

    # In order to load these data, the initialisation scripts need to be run
    print("... Load data from script calculations")
    data = read_data.load_script_data(data)

    #-------------------
    # Folder cleaning
    #--------------------
    print("... delete previous model run results")
    basic_functions.del_previous_setup(data['result_paths']['data_results'])
    basic_functions.create_folder(data['result_paths']['data_results'])
    basic_functions.create_folder(data['result_paths']['data_results_PDF'])
    basic_functions.create_folder(data['result_paths']['data_results_model_run_pop'])

    # Create .ini file with simulation information
    write_data.write_simulation_inifile(data['result_paths']['data_results'], data)

    for sim_yr in data['assumptions'].simulated_yrs:
        setattr(data['assumptions'], 'curr_yr', sim_yr)

        print("Simulation for year --------------:  " + str(sim_yr))
        fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydro, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing_functions.test_function_fuel_sum(
            data,
            data['fuel_disagg'],
            data['criterias']['mode_constrained'],
            data['assumptions'].enduse_space_heating)

        # Main model run function
        modelrun_obj = energy_demand_model(data, data['assumptions'])

        # --------------------
        # Result unconstrained
        #
        # Sum according to first element in array (sectors)
        # which aggregtes over the sectors
        # ---
        supply_results_unconstrained = sum(modelrun_obj.results_unconstrained[:, ])

        # Write out all calculations which are not used for SMIF
        if data['criterias']['beyond_supply_outputs']:

            ed_fueltype_regs_yh = modelrun_obj.ed_fueltype_regs_yh
            out_enduse_specific = modelrun_obj.tot_fuel_y_enduse_specific_yh
            tot_fuel_y_max_enduses = modelrun_obj.tot_fuel_y_max_enduses
            ed_fueltype_national_yh = modelrun_obj.ed_fueltype_national_yh

            reg_load_factor_y = modelrun_obj.reg_load_factor_y
            reg_load_factor_yd = modelrun_obj.reg_load_factor_yd
            reg_load_factor_winter = modelrun_obj.reg_seasons_lf['winter']
            reg_load_factor_spring = modelrun_obj.reg_seasons_lf['spring']
            reg_load_factor_summer = modelrun_obj.reg_seasons_lf['summer']
            reg_load_factor_autumn = modelrun_obj.reg_seasons_lf['autumn']

            # -------------------------------------------
            # Write annual results to txt files
            # -------------------------------------------
            print("... Start writing results to file")
            path_runs = data['result_paths']['data_results_model_runs']

            write_data.write_supply_results(
                sim_yr,
                "result_tot_yh",
                path_runs,
                modelrun_obj.ed_fueltype_regs_yh,
                "result_tot_submodels_fueltypes")
            write_data.write_enduse_specific(
                sim_yr,
                path_runs,
                out_enduse_specific,
                "out_enduse_specific")
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_y",
                [sim_yr],
                reg_load_factor_y,
                'reg_load_factor_y')
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_yd",
                [sim_yr],
                reg_load_factor_yd,
                'reg_load_factor_yd')
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_winter",
                [sim_yr],
                reg_load_factor_winter,
                'reg_load_factor_winter')
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_spring",
                [sim_yr],
                reg_load_factor_spring,
                'reg_load_factor_spring')
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_summer",
                [sim_yr],
                reg_load_factor_summer,
                'reg_load_factor_summer')
            write_data.write_lf(
                path_runs,
                "result_reg_load_factor_autumn",
                [sim_yr],
                reg_load_factor_autumn,
                'reg_load_factor_autumn')

            # -------------------------------------------
            # Write population files of simulation year
            # -------------------------------------------
            pop_array_reg = np.zeros((len(data['regions'])), dtype="float")
            for reg_array_nr, reg in enumerate(data['regions']):
                pop_array_reg[reg_array_nr] = data['scenario_data']['population'][sim_yr][reg]

            write_data.write_scenaric_population_data(
                sim_yr,
                data['result_paths']['model_run_pop'],
                pop_array_reg)
            print("... Finished writing results to file")

    print("-------------------------")
    print("... Finished running HIRE")
    print("-------------------------")
