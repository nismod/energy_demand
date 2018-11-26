import os
import numpy as np
import pandas as pd

def create_annual_weather_file(
        path,
        path_out_stations,
        year,
        weather_scenario_name
    ):
    """Create annual weather file

    write csv file
    """
    # Read files
    path_stations = os.path.join(path, "{}_stations.csv".format(year))
    path_t_min = os.path.join(path, "{}_t_min.npy".format(year))
    path_t_max = os.path.join(path, "{}_t_max.npy".format(year))
    df_stations = pd.read_csv(path_stations)
    stations = df_stations['station_id'].values.tolist()
    t_min = np.load(path_t_min)
    t_max = np.load(path_t_max)

    out_csv = []
    for station_cnt, station_id in enumerate(stations):
        t_min_station = t_min[station_cnt]
        t_max_station = t_max[station_cnt]
        for yearday in range(365):
            out_csv.append([year, station_id, weather_scenario_name, yearday, t_min_station[yearday], t_max_station[yearday]])

    out_csv_array = np.array(out_csv)
    return out_csv_array

def collect_multi_year_weather(path, path_out, year):
    
    weather_scenario_name = os.path.join(path_out, "weather_temps_{}".format(year))
    path_out_csv = os.path.join(weather_scenario_name + ".csv")

    out_csv_array = create_annual_weather_file(
        path,
        path_out,
        year=2015,
        weather_scenario_name=weather_scenario_name)
        
    columns = ['timestep', 'station_id', 'stiching_name', 'yearday', 't_min', 't_max',]
    df = pd.DataFrame(out_csv_array, columns=columns)
    df.to_csv(path_out_csv, index=False)


path = "X:/nismod/data/energy_demand/H-Met_office_weather_data/_complete_meteo_data_all_yrs_cleaned_min_max"
path_out = "X:/nismod/data/energy_demand/H-Met_office_weather_data/_complete_meteo_data_all_yrs_cleaned_min_max"

collect_multi_year_weather(
    path,
    path_out,
    year=2015)