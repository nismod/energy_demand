"""This file creates dummy data needed specifically for the energy_demand model
"""
import os
from datetime import date

from energy_demand.read_write import write_data
from energy_demand.read_write import data_loader
from energy_demand.basic import basic_functions
from energy_demand.basic import date_prop


def dummy_raw_weather_station(local_paths):
    """Write dummy weater station for a single weather station
    """
    create_folders_to_file(local_paths['folder_path_weater_stations'], "_raw_data")

    rows = [['station_Nr_999 	Dummy Weater Station 		GOONHILLY:BLABLA. BLABLA 	BLABLA BLABLA 	01-09-2001 	BLABLA 	50.035 	-5.20803 	TR12 7 	']]

    write_data.create_csv_file(
        local_paths['folder_path_weater_stations'],
        rows)

def dummy_raw_weather_data(local_paths):
    """Write dummy temperature for a single weather station
    """
    create_folders_to_file(local_paths['folder_path_weater_data'], "_raw_data")

    list_dates = date_prop.fullyear_dates(
        start=date(2015, 1, 1),
        end=date(2015, 12, 31))

    rows = []
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
        local_paths['folder_path_weater_data'],
        rows)

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

def dummy_sectoral_load_profiles(local_paths):
    """
    """
    create_folders_to_file(local_paths['path_employment_statistics'], "_processed_data")




def main(path_output_results):
    """
    """

    # Create folders to input data
    raw_folder = os.path.join(path_output_results, '_raw_data')
    processed_folder = os.path.join(path_output_results, '_processed_data')
    basic_functions.create_folder(raw_folder)
    basic_functions.create_folder(processed_folder)

    # Load paths
    local_paths = data_loader.load_local_paths(path_output_results)

    # --------
    # Generate dummy temperatures
    # --------
    dummy_raw_weather_data(local_paths)

    # --------
    # Generate dummy weather stations
    # --------
    dummy_raw_weather_station(local_paths)
    
    # --------
    # Dummy service sector load profiles
    # --------
    dummy_sectoral_load_profiles(local_paths)

    print("Finished generating dummy data")

main("C:/_DUMMY")



