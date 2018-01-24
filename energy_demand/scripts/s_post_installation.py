
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
    path_main = resource_filename(Requirement.parse("energy_demand"), "")
    local_data_path = args.data_energy_demand

    # Initialise logger
    logger_setup.set_up_logger(os.path.join(local_data_path, "logging_post_install_setup.log"))
    logging.info("... start local energy demand calculations")

    # Load data
    data = {}
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
        data['paths'], data['lookups'])

    # Assumptions
    data['assumptions'] = non_param_assumptions.load_non_param_assump(
        data['sim_param']['base_yr'],
        data['paths'],
        data['enduses'],
        data['lookups']['fueltypes'],
        data['lookups']['fueltypes_nr'])

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
    basic_functions.create_folder(data['local_paths']['dir_disaggregated'])

    # Read in residential submodel shapes
    s_rs_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        data['sim_param']['base_yr'])

    # Read in service submodel shapes
    s_ss_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        data['lookups'])

    # Read in temperature data from raw files
    s_raw_weather_data.run(
        data['local_paths'])

    logging.info("... finished post_install_setup")
    print("... finished post_install_setup")
    return

# ------run locally
#'''
class ClassTest():
    def __init__(self, data_energy_demand):
	    self.data_energy_demand = data_energy_demand
#in_obj = ClassTest("C://Users//cenv0553//nismod//data_energy_demand")
in_obj = ClassTest("C://DATA_NISMODII//data_energy_demand")
post_install_setup(in_obj)
#'''