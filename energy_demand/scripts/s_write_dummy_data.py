"""This file creates dummy data needed specifically for the energy_demand model
"""
import os
import numpy as np
from pkg_resources import Requirement
from pkg_resources import resource_filename
from energy_demand.read_write import write_data
from energy_demand.read_write import data_loader
from energy_demand.basic import basic_functions
from energy_demand.scripts.s_rs_raw_shapes import run
from energy_demand.assumptions import non_param_assumptions
from energy_demand.scripts import s_raw_weather_data
from energy_demand.basic import lookup_tables

def dummy_raw_weather_station(local_paths):
    """Write dummy weater station for a single weather station
    """
    create_folders_to_file(local_paths['folder_path_weater_stations'], "_raw_data")

    rows = [
        ['headers', 'headers', 'headers'],
        ['station_Nr_999', '50.035', '-5.20803']]

    write_data.create_csv_file(
        local_paths['changed_weather_station_data'],
        rows)

def dummy_raw_weather_data(local_paths):
    """Write dummy temperature for a single weather station
    """
    create_folders_to_file(local_paths['dir_raw_weather_data'], "_processed_data")
    '''
    from datetime import date
    from energy_demand.basic import date_prop

    create_folders_to_file(local_paths['folder_path_weater_data'], "_raw_data")

    list_dates = date_prop.fullyear_dates(
        start=date(2015, 1, 1),
        end=date(2015, 12, 31))

    rows = [] #[['headers']*40]
    for date_day in list_dates:

        year = date_day.year
        day = date_day.day
        month = date_day.month

        empty_list = ['empty']*40

        day_temp = [8,8,8,8, 9,9,9,9, 12,12,12,12, 16,16,16,16, 10,10,10,10, 7,7,7,7]

        for hour in range(24):
            empty_list[0] = str('{}/{}/{} 00:00'.format(day, month, year))
            empty_list[15] = str('station_Nr_999')
            empty_list[35] = str('{}'.format(day_temp[hour]))  # air temp
            rows.append(empty_list)

    write_data.create_csv_file(
        os.path.join(local_paths['folder_path_weater_data']),
        rows)'''
    temp_data = {}

    temp_data['station_Nr_999'] = np.zeros((365, 24))

    for i in range(365):
        temp_data['station_Nr_999'][i] = [
            8, 8, 8, 8, 9, 9, 9, 9, 12, 12, 12, 12, 16, 16, 16, 16, 10, 10, 10, 10, 7, 7, 7, 7]

    s_raw_weather_data.write_weather_data(
        local_paths['dir_raw_weather_data'], 
        temp_data)

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
    """
    """
    create_folders_to_file(os.path.join(local_paths['ss_load_profile_txt'], "dumm"), "_processed_data")

    paths = data_loader.load_paths(path_main)
    lu = lookup_tables.basic_lookups()

    dict_enduses, dict_sectors, dict_fuels = data_loader.load_fuels(paths, lu)

    for enduse in dict_enduses['ss_enduses']:
        for sector in dict_sectors['ss_sectors']:

            joint_string_name = str(sector) + "__" + str(enduse)

            # Flat profiles
            load_peak_shape_dh = np.full((24), 1)
            shape_non_peak_y_dh = np.full((365, 24), 1/24)
            shape_peak_yd_factor = 1.0
            shape_non_peak_yd = np.full((365), 1/365)

            write_data.create_txt_shapes(
                joint_string_name,
                local_paths['ss_load_profile_txt'],
                load_peak_shape_dh,
                shape_non_peak_y_dh,
                shape_peak_yd_factor,
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

    # ==========================================
    # Post installation setup witout access to non publicy available data
    # ==========================================
    print("... running initialisation scripts with only publicly available data")

    # Load paths
    local_paths = data_loader.load_local_paths(path_local_data)

    # Create folders to input data
    raw_folder = os.path.join(path_local_data, '_raw_data')
    processed_folder = os.path.join(path_local_data, '_processed_data')

    basic_functions.create_folder(raw_folder)
    basic_functions.create_folder(processed_folder)
    basic_functions.create_folder(local_paths['path_post_installation_data'])
    basic_functions.create_folder(local_paths['dir_raw_weather_data'])
    basic_functions.create_folder(local_paths['dir_changed_weather_station_data'])
    basic_functions.create_folder(local_paths['load_profiles'])
    basic_functions.create_folder(local_paths['rs_load_profile_txt'])
    basic_functions.create_folder(local_paths['ss_load_profile_txt'])
    basic_functions.create_folder(local_paths['dir_disaggregated'])

    # Load data
    base_yr = 2015
    data = {}

    data['paths'] = data_loader.load_paths(path_energy_demand)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
        data['paths'], data['lookups'])

    # Assumptions
    data['assumptions'] = non_param_assumptions.Assumptions(
        base_yr=base_yr,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        fueltypes=data['lookups']['fueltypes'],
        fueltypes_nr=data['lookups']['fueltypes_nr'])

    # Read in residential submodel shapes
    run(data['paths'], local_paths, base_yr)

    # ==========================================
    # Create not publica available files
    # ==========================================

    # --------
    # Generate dummy weather stations
    # --------
    dummy_raw_weather_station(local_paths)

    # --------
    # Generate dummy temperatures
    # --------
    dummy_raw_weather_data(local_paths)

    # --------
    # Dummy service sector load profiles
    # --------
    dummy_sectoral_load_profiles(local_paths, path_energy_demand)

    print("Successfully finished post installation setup with open source data")
