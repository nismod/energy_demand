""" Contains the function `energy_demand_model` used for running the energy demand model 

    SMIF test
    Information about the integration framework: http://smif.readthedocs.io/

    Tools
    Profiling:  https://jiffyclub.github.io/snakeviz/
    python -m cProfile -o program.prof my_program.py
    snakeviz program.prof
    
    Development checklist
    https://nismod.github.io/docs/development-checklist.html
    https://nismod.github.io/docs/
    https://nismod.github.io/docs/smif-prerequisites.html#sector-modeller


MEthod to derive GVA/POP SERVICE FLOOR AREAS

1. Step
Get correlation between regional GVA and (regional floor area/reg pop) of every sector of base year
-- Get this correlation for every region and build national correlation

2. Step
Calculate future regional floor area demand based on GVA and pop projection 
info: fuels_yh is made multidmensional according to fueltype
TODO: REMOVEP EAK FACTORS
TODO: DISAGGREGATE SERVICE SECTOR HEATING DEMANDS WITH FLOOR AREA FOR SECTORS
TODO: BECUASE OF HYBRID SUM SWITCHES +=
TODO: remove tech_list
TODO: Write all metadata of model run restuls to txt
TODO: Related ed to houses & householdsize
TODO: data loading, load multiple years for real elec data
TODO: PEAK SHAPE vs PEAK FROM LOAD PROFILES
TODO: WHAT ABOU NON_RESIDENTIAL FLOOR AREA: FOR WHAT?
TODO: Spatial diffusion: Cap largest 5% of values and set to 1
TODO: CONTROL ALL PEAK RESULTS
TODO: REMOVE model_yeardays_nrs
TODO :CHECK LOAD PRIFILE TECH TYPE NAMES
TODO: shape_peak_yd_factor
TODO: REMOVE ALL PEAK RELATED STUFF
TODO: SMOOTH LINE https://stackoverflow.com/questions/25825946/generating-smooth-line-graph-using-matplotlib?lq=1
TODO: plotting. IMprove bins: test if outside bins (because plots wrongly outside)
TODO: CHECK DEMND MANAGEMENT PEAK FACTOR
"""
import os
import sys
import logging
import datetime
import numpy as np
from energy_demand import model
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import lookup_tables
from energy_demand.basic import conversions
from energy_demand.assumptions import non_param_assumptions
from energy_demand.assumptions import param_assumptions
from energy_demand.read_write import data_loader
from energy_demand.basic import logger_setup
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.basic import basic_functions

NR_OF_MODELLEd_REGIONS = 392

def energy_demand_model(data, assumptions, fuel_in=0, fuel_in_elec=0):
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
    modelrun_obj = model.EnergyDemandModel(
        regions=data['regions'],
        data=data,
        assumptions=assumptions)

    # Calculate base year demand
    fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydrogen, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
        data,
        data['fuel_disagg'],
        data['criterias']['mode_constrained'],
        assumptions.enduse_space_heating)

    print("================================================")
    print("Simulation year:     " + str(modelrun_obj.curr_yr))
    print("Number of regions    " + str(data['reg_nrs']))
    print(" TOTAL KTOE:         " + str(conversions.gwh_to_ktoe(fuel_in)))

    print("-----------------")
    print("[GWh] Total fuel input:    " + str(fuel_in))
    print("[GWh] Total output:        " + str(np.sum(modelrun_obj.ed_fueltype_national_yh)))
    print("[GWh] Total difference:    " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh) - fuel_in), 4)))
    print("-----------")
    print("[GWh] oil fuel in:         " + str(fuel_in_oil))
    print("[GWh] oil fuel out:        " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']])))
    print("[GWh] oil diff:            " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']]) - fuel_in_oil, 4)))
    print("-----------")
    print("[GWh] biomass fuel in:     " + str(fuel_in_biomass))
    print("[GWh] biomass fuel out:    " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']])))
    print("[GWh] biomass diff:        " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']]) - fuel_in_biomass, 4)))
    print("-----------")
    print("[GWh] solid_fuel fuel in:  " + str(fuel_in_solid_fuel))
    print("[GWh] solid_fuel fuel out: " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']])))
    print("[GWh] solid_fuel diff:     " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']]) - fuel_in_solid_fuel, 4)))
    print("-----------")
    print("[GWh] elec fuel in:        " + str(fuel_in_elec))
    print("[GWh] elec fuel out:       " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']])))
    print("[GWh] ele fuel diff:       " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']]) - fuel_in_elec, 4)))
    print("-----------")
    print("[GWh] gas fuel in:         " + str(fuel_in_gas))
    print("[GWh] gas fuel out:        " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']])))
    print("[GWh] gas diff:            " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']]) - fuel_in_gas, 4)))
    print("-----------")
    print("[GWh] hydro fuel in:       " + str(fuel_in_hydrogen))
    print("[GWh] hydro fuel out:      " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']])))
    print("[GWh] hydro diff:          " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']]) - fuel_in_hydrogen, 4)))
    print("-----------")
    print("TOTAL HEATING        " + str(tot_heating))
    print("[GWh] heat fuel in:        " + str(fuel_in_heat))
    print("[GWh] heat fuel out:       " + str(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']])))
    print("[GWh] heat diff:           " + str(round(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['heat']]) - fuel_in_heat, 4)))
    print("-----------")
    print("Diff elec %:         " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']])/ fuel_in_elec), 4)))
    print("Diff gas %:          " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']])/ fuel_in_gas), 4)))
    print("Diff oil %:          " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']])/ fuel_in_oil), 4)))
    print("Diff solid_fuel %:   " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']])/ fuel_in_solid_fuel), 4)))
    print("Diff hydrogen %:     " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']])/ fuel_in_hydrogen), 4)))
    print("Diff biomass %:      " + str(round((np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']])/ fuel_in_biomass), 4)))
    print("================================================")

    logging.info("...finished running energy demand model simulation")
    return modelrun_obj

if __name__ == "__main__":
    """
    """
    # Paths
    if len(sys.argv) != 2:
        print("Please provide a local data path:")
        print("    python main.py ../energy_demand_data\n")
        print("... Defaulting to C:/DATA_NISMODII/data_energy_demand")
        local_data_path = os.path.abspath('C:/DATA_NISMODII/data_energy_demand')
        local_data_path = os.path.abspath('C:/users/cenv0553/ED/data')
    else:
        local_data_path = sys.argv[1]

    # -------------- SCRAP

    path_main = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', "energy_demand/config_data"))

    # Initialise logger
    logger_setup.set_up_logger(
        os.path.join(local_data_path, "logging_local_run.log"))

    # Load data
    data = {}
    data['criterias'] = {}
    data['criterias']['mode_constrained'] = True                # Whether model is run in constrained mode or not
    data['criterias']['plot_HDD_chart'] = False                 # Wheather HDD chart is plotted or not
    data['criterias']['virtual_building_stock_criteria'] = True # Wheater model uses a virtual dwelling stock or not
    data['criterias']['write_to_txt'] = True                    # Wheater results are written to txt files
    data['criterias']['beyond_supply_outputs'] = False           # Wheater all results besides integraded smif run are calculated
    data['criterias']['plot_tech_lp'] = True                    # Wheater all individual load profils are plotted
    simulated_yrs = [2015]

    # Paths
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)

    result_path = os.path.dirname(__file__).split("energy_demand\\energy_demand")[0]
    data['result_paths'] = data_loader.load_result_paths(os.path.join(result_path, '_result_data'))

    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

    # local scrap
    data['regions'] = data_loader.load_LAC_geocodes_info(
        os.path.join(
            local_data_path, 'region_definitions', 'same_as_scenario_data', 'infuse_dist_lyr_2011_saved.csv'))

    # GVA
    gva_data = {}
    for year in range(2015, 2101):
        gva_data[year] = {}
        for region_geocode in data['regions']:
            gva_data[year][region_geocode] = 999
    data['gva'] = gva_data

    # Population
    pop_dummy = {}
    pop_density = {}
    for year in range(2015, 2101):
        _data = {}
        for reg_geocode in data['regions']:
            _data[reg_geocode] = data['regions'][reg_geocode]['POP_JOIN']
        pop_dummy[year] = _data

    data['population'] = pop_dummy
    
    data['reg_coord'] = {}
    for reg in data['regions']:
        data['reg_coord'][reg] = {'longitude': 52.58, 'latitude': -1.091}
        pop_density[reg] = 1
    data['regions'] = list(data['regions'].keys())
    data['pop_density'] = pop_density

    # ------------------------------
    # Assumptions
    # ------------------------------
    # Parameters not defined within smif
    data['assumptions']  = non_param_assumptions.Assumptions(
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

    data['reg_nrs'] = len(data['regions'])

    # ------------------------------
    if data['criterias']['virtual_building_stock_criteria']:
        rs_floorarea, ss_floorarea, data['service_building_count'] = data_loader.floor_area_virtual_dw(
            data['regions'],
            data['sectors']['all_sectors'],
            data['local_paths'],
            data['assumptions'].base_yr)

    # Lookup table to import industry sectoral gva
    lookup_tables.industrydemand_name_sic2007()

    data['industry_gva'] = "TST"

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
    write_data.write_simulation_inifile(
        data['result_paths']['data_results'],
        data['enduses'],
        data['assumptions'],
        data['reg_nrs'],
        data['regions'])

    for sim_yr in data['assumptions'].simulated_yrs:
        setattr(data['assumptions'], 'curr_yr', sim_yr)

        print("Simulation for year --------------:  " + str(sim_yr))
        fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydro, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
            data,
            data['fuel_disagg'],
            data['criterias']['mode_constrained'],
            data['assumptions'].enduse_space_heating)

        a = datetime.datetime.now()

        # Main model run function
        modelrun_obj = energy_demand_model(
            data,
            data['assumptions'],
            fuel_in,
            fuel_in_elec)

        # --------------------
        # Result unconstrained
        #
        # Sum according to first element in array (sectors)
        # which aggregtes over the sectors
        # ---
        supply_results_unconstrained = sum(modelrun_obj.ed_submodel_fueltype_regs_yh[:,])

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

            # Write unconstrained results
            if data['criterias']['write_to_txt']:
                #TODO NOT USED SO FAR
                '''write_data.write_supply_results(
                    sim_yr,
                    data['regions'],
                    "supply_results",
                    path_runs,
                    supply_results_unconstrained,
                    "supply_results")'''
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
                pop_array_reg = np.zeros((len(data['regions'])))
                for reg_array_nr, reg in enumerate(data['regions']):
                    pop_array_reg[reg_array_nr] = data['scenario_data']['population'][sim_yr][reg]

                write_data.write_scenaric_population_data(
                    sim_yr,
                    data['local_paths']['model_run_pop'],
                    pop_array_reg)
                print("... Finished writing results to file")

    b = datetime.datetime.now()
    print("TOTAL TIME: " + str(b-a))

    print("... Finished running Energy Demand Model")
