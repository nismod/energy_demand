
"""Script to run after installation of HIRE

Script function which are executed after model installation and
"""
import os
import zipfile
import configparser

from energy_demand.basic import basic_functions
from energy_demand.assumptions import general_assumptions
from energy_demand.scripts import s_rs_raw_shapes
from energy_demand.scripts import s_ss_raw_shapes
from energy_demand.read_write import data_loader
from energy_demand.basic import lookup_tables
from energy_demand.scripts.smif_data_related import script_data_preparation_MISTRAL_pop_gva


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
    print("... start running initialisation scripts", flush=True)

    path_config_file = args.config_file
    config = data_loader.read_config_file(path_config_file)

    local_data_path = config['PATHS']['path_local_data']
    base_yr = config['CONFIG']['base_yr']

    data = {}
    data['paths'] = config['CONFIG_DATA']
    data['local_paths'] = config['DATA_PATHS']
    data['result_paths'] = basic_functions.get_result_paths(config['PATHS']['path_result_data'])
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], lookup_enduses, \
        lookup_sector_enduses = data_loader.load_fuels(data['paths'])

    data['assumptions'] = general_assumptions.Assumptions(
        lookup_enduses=lookup_enduses,
        lookup_sector_enduses=lookup_sector_enduses,
        base_yr=base_yr,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'])

    # Delete all previous data from previous model runs
    basic_functions.del_previous_setup(data['local_paths']['data_processed'])
    basic_functions.del_previous_setup(data['result_paths']['data_results'])
    basic_functions.del_previous_setup(data['local_paths']['path_post_installation_data'])

    # Create folders and subfolder for data_processed
    folders_to_create = [
        data['local_paths']['data_processed'],
        data['local_paths']['path_post_installation_data'],
        data['local_paths']['load_profiles'],
        data['local_paths']['rs_load_profile_txt'],
        data['local_paths']['ss_load_profile_txt']]

    for folder in folders_to_create:
        basic_functions.create_folder(folder)

    print("... Read in residential submodel load profiles", flush=True)
    s_rs_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        base_yr)

    print("... Read in service submodel load profiles", flush=True)
    s_ss_raw_shapes.run(
        data['paths'],
        data['local_paths'],
        data['lookups'])

    print("... successfully finished setup")
