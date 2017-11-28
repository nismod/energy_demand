"""Script functions which are executed after
model installation and after each scenario definition
"""
import os
import logging
from pkg_resources import Requirement
from pkg_resources import resource_filename
from energy_demand.read_write import data_loader
from energy_demand.assumptions import non_param_assumptions
from energy_demand.assumptions import param_assumptions
from energy_demand.scripts import s_raw_weather_data
from energy_demand.scripts import s_rs_raw_shapes
from energy_demand.scripts import s_ss_raw_shapes
from energy_demand.scripts import s_fuel_to_service
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.scripts import s_disaggregation
from energy_demand.basic import basic_functions
from energy_demand.basic import logger_setup
from energy_demand.basic import date_prop

def post_install_setup(args):
    """Run initialisation scripts

    Arguments
    ----------
    args : object
        Arguments defined in ``./cli/__init__.py``

    Note
    ----
    Only needs to be executed once after the energy_demand
    model has been installed
    """
    print("... start running initialisation scripts")

    # Paths
    path_main = resource_filename(Requirement.parse("energy_demand"), "")
    local_data_path = args.data_energy_demand

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_post_install_setup.log"))
    logging.info("... start local energy demand calculations")

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], data['all_sectors'] = data_loader.load_fuels(
        data['paths'], data['lookups'])

    #TODO NEEDED HERE?
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015
    data['sim_param']['simulated_yrs'] = [2015, 2020, 2025]

    # Assumptions
    data['assumptions'] = non_param_assumptions.load_non_param_assump(
        data['sim_param']['base_yr'], data['paths'], data['enduses'], data['lookups'])

    param_assumptions.load_param_assump(data['paths'], data['assumptions'])

    data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
    data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)
    data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(data['assumptions']['technologies'], data['assumptions']['strategy_variables']['eff_achiev_f'])

    # Delete all previous data from previous model runs
    basic_functions.del_previous_setup(data['local_paths']['data_processed'])
    basic_functions.del_previous_setup(data['local_paths']['data_results'])

    # Create folders and subfolder for data_processed
    basic_functions.create_folder(data['local_paths']['data_processed'])
    basic_functions.create_folder(data['local_paths']['path_post_installation_data'])
    basic_functions.create_folder(data['local_paths']['dir_raw_weather_data'])
    basic_functions.create_folder(data['local_paths']['dir_changed_weather_station_data'])
    basic_functions.create_folder(data['local_paths']['load_profiles'])
    basic_functions.create_folder(data['local_paths']['rs_load_profiles'])
    basic_functions.create_folder(data['local_paths']['ss_load_profiles'])
    basic_functions.create_folder(data['local_paths']['dir_disattregated'])

    # Read in temperature data from raw files
    s_raw_weather_data.run(data)

    # Read in residential submodel shapes
    s_rs_raw_shapes.run(data)

    # Read in service submodel shapes
    s_ss_raw_shapes.run(data)

    logging.info("... finished post_install_setup")
    print("... finished post_install_setup")
    return

def scenario_initalisation(path_data_ed, data=False):
    """Scripts which need to be run for every different scenario.
    Only needs to be executed once for each scenario (not for every
    simulation year)

    Arguments
    ----------
    path_data_ed : str
        Path to the energy demand data folder
    """
    logging.info("... start running sceario_initialisation scripts")

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(path_data_ed, "scenario_init.log"))

    # --------------------------------------------
    # Delete processed data from former model runs
    # --------------------------------------------
    logging.info("... delete previous model run results")
    basic_functions.del_previous_results(
        data['local_paths']['data_processed'],
        data['local_paths']['path_post_installation_data'])
    basic_functions.del_previous_setup(data['local_paths']['data_results'])

    # Create folders
    basic_functions.create_folder(data['local_paths']['data_results'])
    basic_functions.create_folder(data['local_paths']['dir_services'])
    basic_functions.create_folder(data['local_paths']['path_sigmoid_data'])
    basic_functions.create_folder(data['local_paths']['data_results_PDF'])
    basic_functions.create_folder(data['local_paths']['data_results'], "model_run_pop")
    basic_functions.create_folder(data['local_paths']['data_results_validation'])

    # ---------------------------------------
    # Load local datasets for disaggregateion
    # ---------------------------------------
    data['scenario_data']['employment_statistics'] = data_loader.read_employment_statistics(
        data['local_paths']['path_employment_statistics'])

    # -------------------
    # Convert fuel to service (s_fuel_to_service)
    # -------------------
    fts_cont = {}
    # RESIDENTIAL: Convert base year fuel input assumptions to energy service
    fts_cont['rs_service_tech_by_p'], fts_cont['rs_service_fueltype_tech_by_p'], fts_cont['rs_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['lookups']['fueltype'],
        data['assumptions']['rs_fuel_tech_p_by'],
        data['fuels']['rs_fuel_raw_data_enduses'],
        data['assumptions']['technologies'])

    # SERVICE: Convert base year fuel input assumptions to energy service
    fuels_aggregated_across_sectors = s_fuel_to_service.ss_sum_fuel_enduse_sectors(
        data['fuels']['ss_fuel_raw_data_enduses'],
        data['enduses']['ss_all_enduses'],
        data['lookups']['fueltypes_nr'])

    fts_cont['ss_service_tech_by_p'], fts_cont['ss_service_fueltype_tech_by_p'], fts_cont['ss_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['lookups']['fueltype'],
        data['assumptions']['ss_fuel_tech_p_by'],
        fuels_aggregated_across_sectors,
        data['assumptions']['technologies'])

    # INDUSTRY
    fuels_aggregated_across_sectors = s_fuel_to_service.ss_sum_fuel_enduse_sectors(
        data['fuels']['is_fuel_raw_data_enduses'],
        data['enduses']['is_all_enduses'],
        data['lookups']['fueltypes_nr'])

    fts_cont['is_service_tech_by_p'], fts_cont['is_service_fueltype_tech_by_p'], fts_cont['is_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['lookups']['fueltype'],
        data['assumptions']['is_fuel_tech_p_by'],
        fuels_aggregated_across_sectors,
        data['assumptions']['technologies'])

    # -------------------
    # Generate sigmoid curves (s_generate_sigmoid)
    # -------------------
    sgs_cont = {}

    # Read in Services
    rs_service_tech_by_p = fts_cont['rs_service_tech_by_p']
    ss_service_tech_by_p = fts_cont['ss_service_tech_by_p']
    is_service_tech_by_p = fts_cont['is_service_tech_by_p']
    rs_service_fueltype_by_p = fts_cont['rs_service_fueltype_by_p']
    ss_service_fueltype_by_p = fts_cont['ss_service_fueltype_by_p']
    is_service_fueltype_by_p = fts_cont['is_service_fueltype_by_p']

    # Calculate technologies with more, less and constant service based on service switch assumptions
    sgs_cont['rs_tech_increased_service'], sgs_cont['rs_tech_decreased_share'], sgs_cont['rs_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
        rs_service_tech_by_p,
        data['assumptions']['rs_share_service_tech_ey_p'])
    sgs_cont['ss_tech_increased_service'], sgs_cont['ss_tech_decreased_share'], sgs_cont['ss_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
        ss_service_tech_by_p,
        data['assumptions']['ss_share_service_tech_ey_p'])
    sgs_cont['is_tech_increased_service'], sgs_cont['is_tech_decreased_share'], sgs_cont['is_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
        is_service_tech_by_p,
        data['assumptions']['is_share_service_tech_ey_p'])

    # Calculate sigmoid diffusion curves based on assumptions about fuel switches

    # --Residential
    sgs_cont['rs_installed_tech'], sgs_cont['rs_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
        data['sim_param']['base_yr'],
        data['assumptions']['technologies'],
        data['assumptions']['rs_service_switches'],
        data['assumptions']['rs_fuel_switches'],
        data['enduses']['rs_all_enduses'],
        sgs_cont['rs_tech_increased_service'],
        data['assumptions']['rs_share_service_tech_ey_p'],
        rs_service_fueltype_by_p,
        rs_service_tech_by_p,
        data['assumptions']['rs_fuel_tech_p_by'])

    # --Service
    sgs_cont['ss_installed_tech'], sgs_cont['ss_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
        data['sim_param']['base_yr'],
        data['assumptions']['technologies'],
        data['assumptions']['ss_service_switches'],
        data['assumptions']['ss_fuel_switches'],
        data['enduses']['ss_all_enduses'],
        sgs_cont['ss_tech_increased_service'],
        data['assumptions']['ss_share_service_tech_ey_p'],
        ss_service_fueltype_by_p,
        ss_service_tech_by_p,
        data['assumptions']['ss_fuel_tech_p_by'])

    # --Industry
    sgs_cont['is_installed_tech'], sgs_cont['is_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
        data['sim_param']['base_yr'],
        data['assumptions']['technologies'],
        data['assumptions']['is_service_switches'],
        data['assumptions']['is_fuel_switches'],
        data['enduses']['is_all_enduses'],
        sgs_cont['is_tech_increased_service'],
        data['assumptions']['is_share_service_tech_ey_p'],
        is_service_fueltype_by_p,
        is_service_tech_by_p,
        data['assumptions']['is_fuel_tech_p_by'])

    # -------------------
    # Disaggregate
    # -------------------
    sd_cont = {}
    sd_cont['rs_fuel_disagg'], sd_cont['ss_fuel_disagg'], sd_cont['is_fuel_disagg'] = s_disaggregation.disaggregate_base_demand(
        data['lu_reg'],
        data['sim_param']['base_yr'],
        data['sim_param']['curr_yr'],
        data['fuels'],
        data['scenario_data'],
        data['assumptions'],
        data['reg_coord'],
        data['weather_stations'],
        data['temp_data'],
        data['sectors'],
        data['all_sectors'],
        data['enduses'])

    logging.info("... finished scenario_initalisation")
    return fts_cont, sgs_cont, sd_cont
