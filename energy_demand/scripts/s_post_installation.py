
"""Script to run after installation of HIRE

Script function which are executed after model installation and
"""
import os
import logging
from pkg_resources import Requirement
from pkg_resources import resource_filename
from energy_demand.assumptions import non_param_assumptions
from energy_demand.scripts import s_raw_weather_data
from energy_demand.scripts import s_rs_raw_shapes
from energy_demand.scripts import s_ss_raw_shapes
from energy_demand.read_write import data_loader
from energy_demand.basic import logger_setup
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables

def post_install_setup(args):
    """Run this function after installing the energy_demand
    model with smif and putting the data folder with all necessary
    data into a local drive. This scripts only needs to be
    executed once after the energy_demand model has been installed

    Arguments
    ----------
    args : object
        Arguments defined in ``./cli/__init__.py``
    """
    print("... start running initialisation scripts")

    # Paths
    path_main = resource_filename(
        Requirement.parse("energy_demand"),
        os.path.join("energy_demand", "config_data"))

    path_results = resource_filename(Requirement.parse("energy_demand"), "results")
    local_data_path = args.local_data

    # Initialise logger
    logger_setup.set_up_logger(
        os.path.join(local_data_path, "logging_post_install_setup.log"))
    logging.info("... start local energy demand calculations")

    # Load data
    base_yr = 2015

    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['result_paths'] = data_loader.load_result_paths(path_results)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
        data['paths'], data['lookups'])

    data['assumptions'] = non_param_assumptions.Assumptions(
        base_yr=base_yr,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        fueltypes=data['lookups']['fueltypes'],
        fueltypes_nr=data['lookups']['fueltypes_nr'])

    # Delete all previous data from previous model runs
    basic_functions.del_previous_setup(data['local_paths']['data_processed'])
    basic_functions.del_previous_setup(data['result_paths']['data_results'])

    # Create folders and subfolder for data_processed
    basic_functions.create_folder(data['local_paths']['data_processed'])
    basic_functions.create_folder(data['local_paths']['path_post_installation_data'])
    basic_functions.create_folder(data['local_paths']['dir_raw_weather_data'])
    basic_functions.create_folder(data['local_paths']['dir_changed_weather_station_data'])
    basic_functions.create_folder(data['local_paths']['load_profiles'])
    basic_functions.create_folder(data['local_paths']['rs_load_profile_txt'])
    basic_functions.create_folder(data['local_paths']['ss_load_profile_txt'])
    basic_functions.create_folder(data['local_paths']['dir_disaggregated'])

    logging.info("... Read in residential submodel load profiles")
    s_rs_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        base_yr)

    logging.info("... Read in temperature data from raw files")
    s_raw_weather_data.run(
        data['local_paths'])

    logging.info("... Read in service submodel load profiles")
    s_ss_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        data['lookups'])

    print("... successfully finished setup")
    return
