
"""Script to run after installation of HIRE

Script function which are executed after model installation and
"""
import os
import zipfile
import configparser
from pkg_resources import Requirement
from pkg_resources import resource_filename

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

    path_main = resource_filename(
        Requirement.parse("energy_demand"),
        os.path.join("energy_demand", "config_data"))

    path_config_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'config', 'wrapperconfig.ini'))

    path_results = resource_filename(Requirement.parse("energy_demand"), "results")
    local_data_path = args.local_data

    config = configparser.ConfigParser()
    config.read(path_config_file)
    config = basic_functions.convert_config_to_correct_type(config)

    base_yr = config['CONFIG']['base_yr']

    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.get_local_paths(local_data_path)
    data['result_paths'] = data_loader.get_result_paths(path_results)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], lookup_enduses, lookup_sector_enduses = data_loader.load_fuels(
        paths=data['paths'])

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
    path_to_zip_file = os.path.join(local_data_path, "population-economic-smif-csv-from-nismod-db.zip")
    path_extraction = os.path.join(local_data_path, 'scenarios', "MISTRAL_pop_gva")
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(path_extraction)
    zip_ref.close()

    # Complete gva and pop data for every sector
    data_pop = os.path.join(local_data_path, "scenarios", "MISTRAL_pop_gva", "data")
    path_geography = os.path.join(local_data_path, "scenarios", "uk_pop_principal_2015_2050_MSOA_england.csv")
    geography_name = "region" # "lad_uk_2016"

    script_data_preparation_MISTRAL_pop_gva.run(
        path_to_folder=data_pop,
        path_MSOA_baseline=path_geography,
        MSOA_calculations=False,
        geography_name=geography_name)

    print("... successfully finished setup")
    return

'''
local_data_path = "C:/Users/cenv0553/ed/data"
# Complete gva and pop data for every sector
data_pop = os.path.join(local_data_path, "scenarios", "MISTRAL_pop_gva_TEST", "data")
path_geography = os.path.join(local_data_path, "scenarios", "uk_pop_principal_2015_2050_MSOA_england.csv")
geography_name = "region" # "lad_uk_2016"

script_data_preparation_MISTRAL_pop_gva.run(
    path_to_folder=data_pop,
    path_MSOA_baseline=path_geography,
    MSOA_calculations=False)

print("... successfully finished setup")'''