"""This file creates dummy data needed specifically for the energy_demand model
"""
import os
import numpy as np
from pkg_resources import Requirement
from pkg_resources import resource_filename
import configparser

from energy_demand.read_write import write_data
from energy_demand.read_write import data_loader
from energy_demand.basic import basic_functions
from energy_demand.scripts.s_rs_raw_shapes import run
from energy_demand.assumptions import general_assumptions
from energy_demand.basic import lookup_tables

def create_folders_to_file(path_to_file, attr_split):
    """
    """
    path = os.path.normpath(path_to_file)

    path_up_to_raw_folder = path.split(attr_split)[0]
    path_after_raw_folder = path.split(attr_split)[1]

    folders_to_create = path_after_raw_folder.split(os.sep)

    path_curr_folder = os.path.join(path_up_to_raw_folder, attr_split)

    for folder in folders_to_create[1:-1]: #Omit first entry and file
        path_curr_folder = os.path.join(path_curr_folder, folder)
        basic_functions.create_folder(path_curr_folder)

def dummy_sectoral_load_profiles(local_paths, path_main):
    """Create dummy sectoral load profiles

    Arguments
    ---------
    local_paths : dict
        Paths
    path_main : str
        Main path
    """
    create_folders_to_file(
        os.path.join(local_paths['ss_load_profile_txt'], "dumm"), "_processed_data")

    paths = data_loader.load_paths(path_main)

    dict_enduses, dict_sectors, _, _, _ = data_loader.load_fuels(paths)

    for enduse in dict_enduses['service']:
        for sector in dict_sectors['service']:

            joint_string_name = str(sector) + "__" + str(enduse)

            # Flat profiles
            load_peak_shape_dh = np.full((24), 1)
            shape_non_peak_y_dh = np.full((365, 24), 1/24)
            shape_non_peak_yd = np.full((365), 1/365)

            write_data.create_txt_shapes(
                joint_string_name,
                local_paths['ss_load_profile_txt'],
                load_peak_shape_dh,
                shape_non_peak_y_dh,
                shape_non_peak_yd)

def post_install_setup_minimum(args):
    """If not all data are available, this scripts allows to
    create dummy datas (temperature and service sector load profiles)

    Arguments
    ---------
    path_local_data : str
        Path to `energy_demand_data` folder
    path_energy_demand : str
        Path to energy demand python files
    """
    path_energy_demand = resource_filename(
        Requirement.parse("energy_demand"),
        os.path.join("energy_demand", "config_data"))

    path_local_data = args.local_data

    path_config_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'config', 'wrapperconfig.ini'))
            #os.path.dirname(__file__), '..', '..', '..', 'models', 'energy_demand', 'wrapperconfig.ini'))

    # Get config in dict and get correct type
    config = configparser.ConfigParser()
    config.read(path_config_file)
    config = basic_functions.convert_config_to_correct_type(config)

    # ==========================================
    # Post installation setup witout access to non publicy available data
    # ==========================================
    print("... running initialisation scripts with only publicly available data")

    # Load paths
    local_paths = data_loader.get_local_paths(path_local_data)

    # Create folders to input data
    raw_folder = os.path.join(path_local_data, 'energy_demand', '_raw_data')
    processed_folder = os.path.join(path_local_data, 'energy_demand', '_processed_data')

    basic_functions.create_folder(raw_folder)
    basic_functions.create_folder(processed_folder)
    basic_functions.create_folder(local_paths['path_post_installation_data'])
    basic_functions.create_folder(local_paths['load_profiles'])
    basic_functions.create_folder(local_paths['rs_load_profile_txt'])
    basic_functions.create_folder(local_paths['ss_load_profile_txt'])

    # Load data
    base_yr = 2015
    data = {}

    data['paths'] = data_loader.load_paths(path_energy_demand)

    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], lookup_enduses, lookup_sector_enduses = data_loader.load_fuels(data['paths'])

    # Assumptions
    data['assumptions'] = general_assumptions.Assumptions(
        lookup_enduses=lookup_enduses,
        lookup_sector_enduses=lookup_sector_enduses,
        base_yr=base_yr,
        weather_by=config['CONFIG']['user_defined_weather_by'],
        simulation_end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'])

    # Read in residential submodel shapes
    run(data['paths'], local_paths, base_yr)

    # ==========================================
    # Create not publica available files
    # ==========================================

    # --------
    # Dummy service sector load profiles
    # --------
    dummy_sectoral_load_profiles(
        local_paths, path_energy_demand)

    print("Successfully finished post installation setup with open source data")
