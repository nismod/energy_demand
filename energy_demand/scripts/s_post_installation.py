
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

    # Input data preparation
    print("Generate additional data", flush=True)

    # Extract NISMOD population data
    path_to_zip_file = os.path.join(local_data_path,"population-economic-smif-csv-from-nismod-db.zip")
    path_extraction = os.path.join(local_data_path, 'scenarios', "MISTRAL_pop_gva")
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(path_extraction)
    zip_ref.close()

    # Complete gva and pop data for every sector
    path_pop = os.path.join(local_data_path, "scenarios", "MISTRAL_pop_gva", "data")
    path_geography = os.path.join(local_data_path, "scenarios", "uk_pop_principal_2015_2050_MSOA_england.csv")
    geography_name = "lad_uk_2016"

    # All MISTRAL scenarios to prepare with correct config
    scenarios_to_generate = [] #'pop-baseline16_econ-c16_fuel-c16', 'pop-f_econ-c_fuel-c', 'pop-d_econ-c_fuel-c',]

    script_data_preparation_MISTRAL_pop_gva.run(
        path_to_folder=path_pop,
        path_MSOA_baseline=path_geography,
        MSOA_calculations=False,
        geography_name=geography_name,
        scenarios_to_generate=scenarios_to_generate)

    print("... successfully finished setup")
    return
