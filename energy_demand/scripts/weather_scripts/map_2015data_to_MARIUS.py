"""Map UK MetOffice 2015 data to MARIUS grid
"""
import os

import pandas as pd
import numpy as np
from energy_demand.scripts.weather_scripts import weather_scenario
from energy_demand.geography import weather_station_location

def get_closest_station_met_office(
        latitude_reg,
        longitude_reg,
        weather_stations
    ):
    """
    """
    closest_dist = 99999999999

    for station_id in weather_stations:

        lat_to = weather_stations[station_id]["latitude"]
        long_to = weather_stations[station_id]["longitude"]

        dist_to_station = weather_station_location.calc_distance_two_points(
            lat_from=latitude_reg,
            long_from=longitude_reg,
            lat_to=lat_to,
            long_to=long_to)

        if dist_to_station < closest_dist:
            closest_dist = dist_to_station
            closest_id = station_id

    return closest_id


def map_2015_uk_to_MARIUS_grid(
        path_2015_uk_data,
        path_2015_uk_data_remaped,
        path_example_grid_min_datafile_MARIUS
    ):

    # ------------------------------------------------------------
    # Read in processed UK 2015 data per weather stations and data
    # ------------------------------------------------------------

    # Met Office t_min, t_max
    uk_met_office_stations_t_min_array = np.load(os.path.join(path_2015_uk_data, "2015_t_min.npy"))
    uk_met_office_stations_t_max_array = np.load(os.path.join(path_2015_uk_data, "2015_t_max.npy"))
    
    # Convert data into dict with uk met office station ID
    nr_of_uk_met_office_stations = uk_met_office_stations_t_min_array.shape[0]
    
    stations = pd.read_csv(os.path.join(path_2015_uk_data, "2015_stations.csv"))
    df_stations = stations.set_index(('station_id'))
    stations_2015_met_office = df_stations.to_dict('index')

    uk_met_office_stations_t_min = {}
    uk_met_office_stations_t_max = {}
    for station_array_nr in range(nr_of_uk_met_office_stations):
        station_id = stations.get_value(station_array_nr,'station_id')
        uk_met_office_stations_t_min[station_id] = uk_met_office_stations_t_min_array[station_array_nr]
        uk_met_office_stations_t_max[station_id] = uk_met_office_stations_t_max_array[station_array_nr]

    # ------------------------------------------------------------
    # Read in MARIUS grid weather stations
    # ------------------------------------------------------------
    data_list = weather_scenario.get_temp_data_from_nc(path_example_grid_min_datafile_MARIUS, 'tasmin')
    #list_min = weather_scenario.extend_360_day_to_365(data_list, 'tasmin')
    
    print("... reading in marius weather stations")
    #marius_station_coordinates, _ = weather_scenario.write_weather_data(list_min)
    # Coordinates and station id
    stations_marius = []
    print("NUMBE OF ROWS " + str(len(data_list)))
    cnt = 0
    station_id_cnt = 0
    for i  in data_list.index:
        if cnt == 359: #Originally only 360 days
            # Weather station metadata
            station_lon = data_list.get_value(i,'lon')
            station_lat = data_list.get_value(i,'lat')
            station_id = "station_id_{}".format(station_id_cnt)
            stations_marius.append([station_id, station_lat, station_lon]) #ID, latitude, longitude

            # Reset
            station_id_cnt += 1
            cnt = -1
        cnt += 1
    print("... finished read in marius weather stations")

    nr_of_marius_stations = len(stations_marius)

    # ------------------------------------------------------------
    # Map 2015 UK weather data to MARIUS grid
    # ------------------------------------------------------------
    mapped_marius_station_data_t_min = np.zeros((nr_of_marius_stations, 365))
    mapped_marius_station_data_t_max = np.zeros((nr_of_marius_stations, 365))

    # Iterate marius grid stations
    for station_array_nr, row in enumerate(stations_marius):

        # Marius weather station
        #marius_station_id = row[0]
        marius_station_lat = row[1]
        marius_station_lon = row[2]

        # Get closest Met Office weather station
        closest_uk_2015_met_office_station = get_closest_station_met_office(
            latitude_reg=marius_station_lat,
            longitude_reg=marius_station_lon,
            weather_stations=stations_2015_met_office)
        
        # Add station
        mapped_marius_station_data_t_min[station_array_nr] = uk_met_office_stations_t_min[closest_uk_2015_met_office_station]
        mapped_marius_station_data_t_max[station_array_nr] = uk_met_office_stations_t_max[closest_uk_2015_met_office_station]

    # ----------------------------------------------------------
    # Write out weather stations and data
    # ----------------------------------------------------------
    df = pd.DataFrame(stations_marius, columns=['station_id', 'latitude', 'longitude'])

    df.to_csv(os.path.join(path_2015_uk_data_remaped, "stations_2015.csv"), index=False)
    np.save(os.path.join(path_2015_uk_data_remaped, "t_min.npy"), mapped_marius_station_data_t_min)
    np.save(os.path.join(path_2015_uk_data_remaped, "t_max.npy"), mapped_marius_station_data_t_max)

# =========================
# Write 2015 weather station in MARIUS grid
# =========================
path_2015_uk_data = "X:/nismod/data/energy_demand/H-Met_office_weather_data/_complete_meteo_data_all_yrs_cleaned_min_max"
path_2015_uk_data_remaped = "X:/nismod/data/energy_demand/H-Met_office_weather_data/_complete_meteo_data_all_yrs_cleaned_min_max/2015_remapped"
path_example_grid_min_datafile_MARIUS = "X:/nismod/data/energy_demand/J-MARIUS_data/2020/m00d/daily/WAH_m00d_tasmin_daily_g2_2020.nc"

map_2015_uk_to_MARIUS_grid(
    path_2015_uk_data=path_2015_uk_data,
    path_2015_uk_data_remaped=path_2015_uk_data_remaped,
    path_example_grid_min_datafile_MARIUS=path_example_grid_min_datafile_MARIUS)



