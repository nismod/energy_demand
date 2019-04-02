"""
Script to extract weather data from weather@home for supply model


1. Download yearly data from here: http://catalogue.ceda.ac.uk/uuid/0cea8d7aca57427fae92241348ae9b03

2. Extract data to folder

3. Configure path below

4. If you want to map 2015 base year data, add the remapped files in a folder:
    base_yr_remapped_weather_path
        /t_max_remapped.npy
        /t_min_remapped.npy
        /stations_2015_remapped.csv
    They can be generated with the script map_2015data_to_MARIUS.py

5. Run this script to get only the relevant data for all weather@home scenarios from 2020 - 2049:

    Daily mean wind speed
    Daily mean solar information

Links
------
http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/
https://medium.com/@rtjeannier/pandas-101-cont-9d061cb73bfc
"""
import os
from energy_demand.scripts.weather_at_home_data_processing import extract_weather_data
from energy_demand.scripts.weather_at_home_data_processing import create_realisation
from energy_demand.scripts.weather_at_home_data_processing import map_weather_data

# =================================
# Configuration
# =================================
path_extracted_files = "X:/nismod/data/energy_demand/J-MARIUS_data" # Path to folder with extracted files
path_stiching_table = "X:/nismod/data/energy_demand/J-MARIUS_data/stitching_table/stitching_table_nf.dat" # Path to stiching table
path_results = "X:/nismod/data/energy_supply/weather_files" # Path to store results
base_yr_remapped_weather_path = "X:/nismod/data/energy_demand/J-MARIUS_data/_weather_data_cleaned/2015_remapped"

# Energy supply data
result_folder = "C:/AAA/energy_supply"
path_input_coordinates = os.path.abspath("X:/nismod/data/energy_supply/regions_input_supply_model.csv") # Path to file with coordinates to map on to

# Energy demand data
result_folder ='_spatially_mapped_demand_data'
path_input_coordinates = os.path.abspath("X:/nismod/data/energy_supply/regions_energy_demand_model.csv") # Path to file with coordinates to map on to

extract_data = False
stich_together = False
append_closest_weather_data = True

if extract_data:
    # =================================
    # Extract shortwave and wind data, extends 360 to 365 days, writes coordinates
    # Note: As this script takes a long time to run, use multiple instance to run selected years
    # =================================
    extract_weather_data.weather_dat_prepare(
        path_extracted_files,
        path_results,
        years=[2035])
    print("... finished extracting data")

if stich_together:
    # =================================
    # Stich data together to create weather@home realization
    # =================================
    create_realisation.generate_weather_at_home_realisation(
        path_results=path_results,
        path_stiching_table=path_stiching_table,
        base_yr_remapped_weather_path=base_yr_remapped_weather_path,
        attributes=['t_min', 't_max', 'rsds', 'wss'],
        scenarios=range(0, 100))
    print("... finished creating realisations")

if append_closest_weather_data:
    # =================================
    # Assign spatial conversion and write out in form as necessary by supply team
    # =================================
    map_weather_data.spatially_map_data(
        path_results=path_results,
        result_out_path=result_folder,
        path_weather_at_home_stations=os.path.join(path_results, "_cleaned_csv"),
        path_input_coordinates=path_input_coordinates,
        attributes=['t_min', 't_max', 'rsds', 'wss'],
        scenarios=range(0, 100))
    print("... append closest weather information")
