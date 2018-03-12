"""

    Energy Demand Model
    ===================
    Contains the function `energy_demand_model` which is used
    to run the energy demand model 


    ---------------------
    SMIF
    ---------------------
    Information about the integration framework: http://smif.readthedocs.io/

    ---------------------
    Tools
    ---------------------
    Profiling:  https://jiffyclub.github.io/snakeviz/

    ---------------------
    Development checklist
    ---------------------
    https://nismod.github.io/docs/development-checklist.html
    https://nismod.github.io/docs/
    https://nismod.github.io/docs/smif-prerequisites.html#sector-modeller

    # Implement that e.g. 2015 - 2030 one technology and 2030 - 2050 another technology
    # backcasting
    # Industry INFO about efficiencies & technologies: Define strategy variables

    INTERFACE QUESTIONS
    ------------------
    - Virtual dwelling stock data?
    - fuel switches?
    - Sub-sectoral GVA

============================================
MEthod to derive GVA/POP SERVICE FLOOR AREAS
============================================

1. Step
Get correlation between regional GVA and (regional floor area/reg pop) of every sector of base year
-- Get this correlation for every region and build national correlation

2. Step
Calculate future regional floor area demand based on GVA and pop projection

NICETOHAVE
- Convert paths dict to objects

TODOS
TODO: LOAD IN SCENARIO PARAMETERS IN INITIAL_SETUP FUNCTION IN RUn file
TODO: Write function to test wheter swichtes are possible (e.g. that not more from one technology to another is replaced than possible)
TODO: Improve industry related demand --> define strategies
TODO: Related ed to houses & householdsize
TODO: SENSITIVITY
TODO: data loading, load multiple years for real elec data
TODO: Load different temp --> for different years
TODO: THECK VARIALBES IN HOUSEHOLD MODEL
TODO: FUEL; SERVICE SWITHC AS INPUT¨
TODO: REMOVE SEPEARATE PEAK CALUCLATIONS AND SHAPES
TODO: PEAK SHAPE vs PEAK FROM LOAD PROFILES
TODO: IF spatial explicity, still very slow
TODO: HYBRID TECHNOLOGIES?
TODO: UPDate all fuel data with new ECUK DATA
TODO: TEST IS SECTOR TECH SWITCH
TODO: STORE RESULTS PER ANNUAL YEAR AND GENERATE FUNCTION TO COLLECT PLOTS AND CREATE GIF
TODO: get_position for all readings of csv file
TODO: WHAT ABOU NON_RESIDENTIAL FLOOR AREA: FOR WHAT?
TODO: REMOVE PEAK SHAPES
TODO: SPATIAL DISAGGREGATION FACTORS RESID/NONRESID SHARE
TODO: INTERFACE AND 
TODO: SO FAR ALSO ALL SERVICE ENDUSES ARE MULTIPLIED
TODO: DWELLING DENSITY FOR EVERY LAD
RURAL URBAN : http://www.gov.scot/Topics/Statistics/About/Methodology/UrbanRuralClassification/Urban-Rural-Classification-2011-12/2011-2012-Urban-Rural-Lookups
"""
import os
import sys
import logging
import datetime
import numpy as np
from energy_demand import model
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import lookup_tables

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
    modelrun_obj : dict
        Object of a yearly model run

    Note
    ----
    This function is executed in the wrapper
    """
    modelrun_obj = model.EnergyDemandModel(
        regions=data['regions'],
        data=data)

    # ----------------
    # Information
    # ----------------
    fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydrogen, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
        data,
        data['criterias']['mode_constrained'],
        data['assumptions']['enduse_space_heating'])

    from energy_demand.basic import conversions
    print("================================================")
    print("Simulation year:     " + str(modelrun_obj.curr_yr))
    print("Number of regions    " + str(data['reg_nrs']))
    print(" -- ")
    print(" TOTAL KTOE:         " + str(conversions.gwh_to_ktoe(fuel_in)))
    print(" -- ")
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
    print("Diff elec %:         " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['electricity']]))) * fuel_in_elec, 4)))
    print("Diff gas %:          " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['gas']]))) * fuel_in_gas, 4)))
    print("Diff oil %:          " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['oil']]))) * fuel_in_oil, 4)))
    print("Diff solid_fuel %:   " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['solid_fuel']]))) * fuel_in_solid_fuel, 4)))
    print("Diff hydrogen %:     " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['hydrogen']]))) * fuel_in_hydrogen, 4)))
    print("Diff biomass %:      " + str(round((1/(np.sum(modelrun_obj.ed_fueltype_national_yh[data['lookups']['fueltypes']['biomass']]))) * fuel_in_biomass, 4)))
    print("================================================")

    logging.info("...finished running energy demand model simulation")
    #prnt(":")
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
        ##local_data_path = os.path.abspath('C:/Users/cenv0553/nismod/data_energy_demand')
    else:
        local_data_path = sys.argv[1]

    # -------------- SCRAP
    from energy_demand.assumptions import non_param_assumptions
    from energy_demand.assumptions import param_assumptions
    from energy_demand.read_write import data_loader
    from energy_demand.basic import logger_setup
    from energy_demand.read_write import write_data
    from energy_demand.read_write import read_data
    from energy_demand.basic import basic_functions
    from energy_demand.basic import date_prop
    from energy_demand.profiles import hdd_cdd

    path_main = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..")

    # Initialise logger
    logger_setup.set_up_logger(
        os.path.join(local_data_path, "logging_local_run.log"))

    # Load data
    data = {}
    data['criterias'] = {}
    data['criterias']['mode_constrained'] = True               # Whether model is run in constrained mode or not
    data['criterias']['plot_HDD_chart'] = False                 # Wheather HDD chart is plotted or not
    data['criterias']['virtual_building_stock_criteria'] = True # Wheater model uses a virtual dwelling stock or not
    data['criterias']['spatial_exliclit_diffusion'] = True      # Wheater spatially epxlicit diffusion or not
    data['criterias']['write_to_txt'] = True                   # Wheater results are written to txt files
    data['criterias']['beyond_supply_outputs'] = True           # Wheater all results besides integraded smif run are calculated
    data['criterias']['plot_tech_lp'] = True                    # Wheater all individual load profils are plotted

    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015
    data['sim_param']['curr_yr'] = data['sim_param']['base_yr']
    data['sim_param']['simulated_yrs'] = [2015, 2016, 2030, 2050]

    # local scrap
    data['regions'] = data_loader.load_LAC_geocodes_info(
        os.path.join(local_data_path, '_raw_data', '_quick_and_dirty_spatial_disaggregation', 'infuse_dist_lyr_2011_saved.csv'))
    
    # GVA
    gva_data = {}
    for year in range(2015, 2101):
        gva_data[year] = {}
        for region_geocode in data['regions']:
            gva_data[year][region_geocode] = 999
    data['gva'] = gva_data

    # Population
    pop_dummy = {}
    for year in range(2015, 2101):
        _data = {}
        for reg_geocode in data['regions']:
            _data[reg_geocode] = data['regions'][reg_geocode]['POP_JOIN']
        pop_dummy[year] = _data
    data['population'] = pop_dummy

    data['reg_coord'] = {}
    for reg in data['regions']:
        data['reg_coord'][reg] = {'longitude': 52.58, 'latitude': -1.091}

    data['regions'] = list(data['regions'].keys())

    # ------------------------------
    # Assumptions
    # ------------------------------
    # Parameters not defined within smif
    data['assumptions'] = non_param_assumptions.load_non_param_assump(
        data['sim_param']['base_yr'],
        data['paths'],
        data['enduses'],
        data['sectors'],
        data['lookups']['fueltypes'],
        data['lookups']['fueltypes_nr'])

    # Parameters defined within smif
    data['assumptions']['strategy_variables'] = param_assumptions.load_param_assump(
        data['paths'], data['assumptions'])

    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=data['sim_param']['base_yr'])
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_daytype(year_to_model=2015)

    data['tech_lp'] = data_loader.load_data_profiles(
        data['paths'], data['local_paths'],
        data['assumptions']['model_yeardays'],
        data['assumptions']['model_yeardays_daytype'],
        data['criterias']['plot_tech_lp'])
    data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
        data['assumptions']['technologies'],
        data['assumptions']['strategy_variables']['f_eff_achieved']['scenario_value'],
        data['assumptions']['strategy_variables']['split_hp_gshp_to_ashp_ey']['scenario_value'])

    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])

    data['reg_nrs'] = len(data['regions'])

    # ----------------------------------
    # Calculating COOLING CDD PARAMETER
    # ----------------------------------
    data['assumptions']['cdd_weekend_cfactors'] = hdd_cdd.calc_weekend_corr_f(
        data['assumptions']['model_yeardays_daytype'],
        data['assumptions']['f_ss_cooling_weekend'])

    data['assumptions']['ss_weekend_f'] = hdd_cdd.calc_weekend_corr_f(
        data['assumptions']['model_yeardays_daytype'],
        data['assumptions']['f_ss_weekend'])

    data['assumptions']['is_weekend_f'] = hdd_cdd.calc_weekend_corr_f(
        data['assumptions']['model_yeardays_daytype'],
        data['assumptions']['f_is_weekend'])

    # ------------------------------
    if data['criterias']['virtual_building_stock_criteria']:
        rs_floorarea, ss_floorarea = data_loader.floor_area_virtual_dw(
            data['regions'],
            data['sectors']['all_sectors'],
            data['local_paths'],
            data['sim_param']['base_yr'],
            f_mixed_floorarea=data['assumptions']['f_mixed_floorarea'])

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
    data = read_data.load_script_data(data) #SCENARIO INITIALISATION

    #-------------------
    # Folder cleaning
    #--------------------
    print("... delete previous model run results")
    basic_functions.del_previous_setup(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['data_results_PDF'])
    basic_functions.create_folder(data['local_paths']['data_results_model_run_pop'])

    # Create .ini file with simulation information
    write_data.write_simulation_inifile(
        data['local_paths']['data_results'],
        data['sim_param'],
        data['enduses'],
        data['assumptions'],
        data['reg_nrs'],
        data['regions'])

    for sim_yr in data['sim_param']['simulated_yrs']:
        data['sim_param']['curr_yr'] = sim_yr

        print("Simulation for year --------------:  " + str(sim_yr))
        fuel_in, fuel_in_biomass, fuel_in_elec, fuel_in_gas, fuel_in_heat, fuel_in_hydro, fuel_in_solid_fuel, fuel_in_oil, tot_heating = testing.test_function_fuel_sum(
            data,
            data['criterias']['mode_constrained'],
            data['assumptions']['enduse_space_heating'])

        a = datetime.datetime.now()

        # Main model run function
        modelrun_obj = energy_demand_model(
            data,
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
            tot_peak_enduses_fueltype = modelrun_obj.tot_peak_enduses_fueltype
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
            path_runs = data['local_paths']['data_results_model_runs']

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
                write_data.write_max_results(
                    sim_yr,
                    path_runs,
                    "result_tot_peak_enduses_fueltype",
                    tot_peak_enduses_fueltype,
                    "tot_peak_enduses_fueltype")
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
