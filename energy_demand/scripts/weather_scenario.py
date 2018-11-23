"""Script to prepare weather data
Load weather simulation data

1. Download yearly data from here: http://catalogue.ceda.ac.uk/uuid/0cea8d7aca57427fae92241348ae9b03

2. Extract data

3. Run this script to get only the relevant data

Links
------
http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/
"""
import os
import pytemperature
import xarray as xr
import numpy as np
import pandas as pd

from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data

path = "X:/nismod/data/energy_demand/J-MARIUS_data"
result_path = "X:/nismod/data/energy_demand/J-MARIUS_data"

def get_temp_data_from_nc(path_nc_file, attribute_to_keep):
    """Open c file, convert it into dataframe,
    clean it and extract attribute data
    """
    # Open as xarray
    x_array_data = xr.open_dataset(path_nc_file)

    # Convert to dataframe
    df = x_array_data.to_dataframe()

    # Add index as columns
    df = df.reset_index()

    # Drop unnecessary columns
    df = df.drop(['time_bnds', 'rotated_latitude_longitude', 'rlat', 'rlon', 'bnds', 'height'], axis=1)

    # Drop all missing value
    df = df.dropna(subset=[attribute_to_keep])

    return df

def convert_to_celcius(df, attribute_to_convert):
    """# Convert Kelvin to Celsius (# Kelvin to Celsius)
    """
    df[attribute_to_convert] = df[attribute_to_convert].apply(pytemperature.k2c)
    return df

def extend_360_day_to_365(df, attribute):
    """Add evenly distributed days across the 360 days

    Return
    ------
    out_list : list
        Returns list with days with the following attributes
        e.g. [[lat, long, yearday365, value]]
    """
    # Copy the following position of day in the 360 year
    days_to_duplicate = [60, 120, 180, 240, 300]
    out_list = []

    # Copy every sithieth day over the year and duplicate it. Do this five times --> get from 360 to 365 days
    day_cnt, day_cnt_365 = 0, 0

    for index, row in df.iterrows():
        day_cnt += 1

        # Copy extra day
        if day_cnt in days_to_duplicate:
            out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])
            day_cnt_365 += 1

        # Copy day
        day_cnt_365 += 1
        out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])

        # Reset counter if next weather station
        if day_cnt == 360:
            day_cnt = 0
            day_cnt_365 = 0

    return out_list

def write_wether_data(data_list):
    """Write weather data to array
    data_list : list
        [[lat, long, yearday365, value]]
    """
    station_coordinates = []

    assert not len(data_list) % 365 #Check if dividable by 365
    nr_stations = int(len(data_list) / 365)

    stations_data = np.zeros((nr_stations, 365))
    station_data = np.zeros((365))

    station_id_cnt = 0
    cnt = 0

    for row in data_list:
        station_data[cnt] = row[3]

        if cnt == 364:

            # 365 day data for weather station
            stations_data[station_id_cnt] = station_data

            # Weather station metadata
            station_lon = row[1]
            station_lat = row[0]

            station_id = "station_id_{}".format(station_id_cnt)
            '''station_coordinates[station_id] = {
                'longitude':station_lat,
                'latitude': station_lon}'''
            station_coordinates.append([station_id, station_lat, station_lon]) #ID, latitude, longitude

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = -1
        cnt += 1

    return station_coordinates, stations_data




def calc_HDD_from_min_max(t_min, t_max, base_temp):
    """Calculate hdd for every day and weather station

    The Meteorological Office equations


    """
    hdd_array = np.zeros((365))

    # Calculate hdd
    for yearday in range(365):
        case_met_equation = get_meterological_equation_case(t_min, t_max, base_temp)

    return hdd_array




# Load stiching table to create weather scenario
def weather_dat_prepare(data_path, result_path):
    """
    """
    # All folders
    '''
    all_files = os.listdir(path)
    folder_names = []
    for i in all_files:
        try:
            folder_names.append(int(i)) #get years
        except:
            pass
    '''
    folder_names = range(2020, 2049)
    folder_names = [2020, 2025, 2030, 2035, 2040, 2045, 2049]
    print("folder_name " + str(folder_names))

    # Create reulst folders
    result_folder = os.path.join(result_path, "_weather_data_cleaned")
    basic_functions.create_folder(result_folder)

    for folder_name in folder_names:

        year = folder_name

        # Create folder
        path_year = os.path.join(result_folder, str(year))
        basic_functions.create_folder(path_year)

        path_realizations = os.path.join(path, str(year))
        realization_names = os.listdir(path_realizations)

        for realization_name in realization_names:
            print("... processing {}  {}".format(str(year), str(realization_name)), flush=True)

            # Create folder
            path_realization = os.path.join(path_year, realization_name)
            basic_functions.create_folder(path_realization)
            
            # Data to extract
            path_tasmin = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmin_daily_g2_{}.nc'.format(realization_name, year))
            path_tasmax = os.path.join(path_realizations, realization_name, 'daily', 'WAH_{}_tasmax_daily_g2_{}.nc'.format(realization_name, year))
            
            # Load data
            print("     ..load data", flush=True)
            df_min = get_temp_data_from_nc(path_tasmin, 'tasmin')
            df_max = get_temp_data_from_nc(path_tasmax, 'tasmax')

            # Convert Kelvin to Celsius (# Kelvin to Celsius)
            print("     ..convert temp", flush=True)
            df_min = convert_to_celcius(df_min, 'tasmin')
            df_max = convert_to_celcius(df_max, 'tasmax')

            # Convert 360 day to 365 days
            print("     ..extend day", flush=True)
            list_min = extend_360_day_to_365(df_min, 'tasmin')
            list_max = extend_360_day_to_365(df_max, 'tasmax')

            # Write out single weather stations as numpy array
            print("     ..write out", flush=True)
            station_coordinates, stations_t_min = write_wether_data(list_min)
            station_coordinates, stations_t_max = write_wether_data(list_max)

            # Write to csv
            np.save(os.path.join(path_realization, "t_min.npy"), stations_t_min)
            np.save(os.path.join(path_realization, "t_max.npy"), stations_t_max)

            #write_data.write_yaml(station_coordinates, os.path.join(path_realization, "stations.yml"))
            columns = ['station_id', 'latitude', 'longitude']

            df = pd.DataFrame(station_coordinates, columns=columns)
            df.to_csv(os.path.join(path_realization, "stations.csv"), index=False)

    print("... finished cleaning weather data")

weather_dat_prepare(path, result_path)


'''
path_tasmax = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmax_daily_g2_2020.nc"
path_tasmin = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmin_daily_g2_2020.nc"

out_path = "C:/_scrap/test.csv"
out_path_station_names = "C:/_scrap/station_position.csv"

# Load data
df_max = get_temp_data_from_nc(path_tasmax, 'tasmax')
df_min = get_temp_data_from_nc(path_tasmin, 'tasmin')

# Convert Kelvin to Celsius (# Kelvin to Celsius)
df_max['tasmax'] = convert_to_celcius(df_max, 'tasmax')
df_min['tasmin'] = convert_to_celcius(df_min, 'tasmin')

# Convert 360 day to 365 days
list_max = extend_360_day_to_365(df_max, 'tasmax')
list_min = extend_360_day_to_365(df_min, 'tasmin')

# Write out single weather stations as numpy array
station_coordinates, stations_t_max = write_wether_data(list_max, list_max)
station_coordinates, stations_t_min = write_wether_data(list_max, list_min)

# Write out coordinates of weather data to csv
print(len(stations_t_max))
print(len(stations_t_min))
'''


# Convert weather station data to HDD days
'''for station_nr in enumerate(station_coordinates):

    t_min = stations_t_min[station_nr]
    t_max = stations_t_max[station_nr]

    calc_hdd_min_max(t_min, t_max)'''

    










raise Exception("ff")
'''ds_max = xr.open_dataset(tasmax)
ds_min = xr.open_dataset(tasmin)

df_max = ds_max.to_dataframe()
df_min= ds_min.to_dataframe()

# Add index as columns
df_max = df_max.reset_index()
df_min = df_min.reset_index()

# Drop columns
df_max = df_max.drop(['time_bnds', 'rotated_latitude_longitude', 'rlat', 'rlon', 'bnds', 'height'], axis=1)
df_min = df_min.drop(['time_bnds', 'rotated_latitude_longitude', 'rlat', 'rlon', 'bnds', 'height'], axis=1)

    
# Drop all missing value
df_max = df_max.dropna(subset=['tasmax'])
df_min = df_min.dropna(subset=['tasmin'])

# Convert Kelvin to Celsius (# Kelvin to Celsius)
df_max['tasmax'] = df_max['tasmax'].apply(pytemperature.k2c)
df_min['tasmin'] = df_min['tasmin'].apply(pytemperature.k2c)'''
'''
# Add evenly distributed days
# Copy every sithieth day over the year and duplicate it. Do this five times --> get from 360 to 365 days
min_vals = []
max_vals = []
longs = []
lats = []

# Convert days into yeardays
days_to_duplicate = [60, 120, 180, 240, 300]

day_cnt = 0
day_cnt_365 = 0
for index, row in df_max.iterrows():
    # Copy extra day
    if day_cnt in days_to_duplicate:
        max_vals.append(row['tasmax'])
        longs.append(row['lon'])
        lats.append(row['lat'])

    max_vals.append(row['tasmax']) 
    longs.append(row['lon'])
    lats.append(row['lat'])
    day_cnt += 1

day_cnt = 0
day_cnt_365 = 0
for index, row in df_min.iterrows():
    # Copy extra day
    if day_cnt in days_to_duplicate:
        min_vals.append(row['tasmin'])
        longs.append(row['lon'])
        lats.append(row['lat'])

    min_vals.append(row['tasmin']) 
    longs.append(row['lon'])
    lats.append(row['lat'])
    day_cnt += 1

station_id_positions = []

print("A")
#print(min_vals)
#print(max_vals)
print(len(min_vals))
print(len(max_vals))

nr_of_entries = len(min_vals)
cnt = 0
for i in range(nr_of_entries):
    print("o " + str(i))
    min_val = max_vals[cnt] 
    max_val = min_vals[cnt] 
    lon = longs[cnt]
    lat = lats[cnt]

    if cnt == 0:
        station_name = "station_{}_{}.csv".format(lon, lat)
        station = pd.DataFrame(columns=list('tasmax', 'tasmin'))
        path_station = "C:/_scrap/{}".format(station_name)

    station_row = pd.DataFrame([[lon, lat, min_val, max_val]], columns=list( 'tasmax', 'tasmin'))

    station.append(station_row)

    if cnt == 364:
        # Write station
        station.to_csv(station, path_station)
        station_id_positions.append([station_name, lon, lat])
        cnt = 0
    
    cnt +=1

# Write station 
def create_csv_file(path, rows):
    """

    """
    with open(path, 'w', newline='') as csvfile:

        filewriter = csv.writer(
            csvfile,
            delimiter=',',
            quotechar='|')

        for row in rows:
            filewriter.writerow(row)
            
create_csv_file(out_path_station_names,station_id_positions)



raise Exception
'''

'''









from netCDF4 import Dataset
import numpy as np

def get_values(path, attribute_to_read):

    fh = Dataset(path, mode='r')

    # Variablees
   # all_vars = fh.variables.keys()

    # Coordinates of grid
    longitudes = fh.variables['lon'][:]
    latitudes = fh.variables['lat'][:]

    # Grid info
    nr_grid_x = longitudes.shape[0]
    nr_grid_y = longitudes.shape[1]
    nr_of_stations = nr_grid_x * nr_grid_y
    print("nr_of_stations " + str(nr_of_stations))

    # Temperature values
    attribute_360_year = fh.variables[attribute_to_read][:]

    fh.close()
    return attribute_360_year, longitudes, latitudes, nr_grid_x, nr_grid_y

# Files
tasmax = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmax_daily_g2_2020.nc"
tasmin = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmin_daily_g2_2020.nc"

tasmax_360_year, longitudes, latitudes, nr_grid_x, nr_grid_y = get_values(tasmax, 'tasmax')
tasmin_360_year, longitudes, latitudes, nr_grid_x, nr_grid_y = get_values(tasmin, 'tasmin')

stations = {}
cnt = 0
for x_pos in range(nr_grid_x):
    for y_pos in range(nr_grid_y):
        station_id = cnt

        station_longitude = longitudes[x_pos][y_pos]
        station_latitude = latitudes[x_pos][y_pos]

        # Get every day in years
        station_daily_max_t = tasmax_360_year[:, x_pos, y_pos]
        station_daily_min_t = tasmin_360_year[:, x_pos, y_pos]
        print("AAAAAAA")
        print(station_daily_min_t)
        stations[station_id] = {
            'latitude': station_latitude,
            'longitude': station_longitude,
            '360_day_max': station_daily_max_t,
            '360_day_min': station_daily_min_t}
        cnt += 1

for i in stations:
    print(stations[i])

'''

'''
fh.close()

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

from netCDF4 import Dataset

# Get some parameters for the Stereographic Projection
lon_0 = lons.mean()
lat_0 = lats.mean()

m = Basemap(width=5000000,height=3500000,
            resolution='l',projection='stere',\
            lat_ts=40,lat_0=lat_0,lon_0=lon_0)
# Because our lon and lat variables are 1D,
# use meshgrid to create 2D arrays
# Not necessary if coordinates are already in 2D arrays.
lon, lat = np.meshgrid(lons, lats)
xi, yi = m(lon, lat)


# Plot Data
cs = m.pcolor(xi,yi,np.squeeze(tmax))

# Add Grid Lines
m.drawparallels(np.arange(-80., 81., 10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180., 181., 10.), labels=[0,0,0,1], fontsize=10)

# Add Coastlines, States, and Country Boundaries
m.drawcoastlines()
m.drawstates()
m.drawcountries()

# Add Colorbar
cbar = m.colorbar(cs, location='bottom', pad="10%")
cbar.set_label(tmax_units)

# Add Title
plt.title('DJF Maximum Temperature')

plt.show()
'''
'''

# http://www.ceda.ac.uk/static/media/uploads/ncas-reading-2015/10_read_netcdf_python.pdf
# Convert 
path = "C:/_WEATHERDATA/nf-2020"
path = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmax_daily_g2_2020.nc"


dataset = Dataset(path)



print("--------")
v = dataset.variables.keys()
print(v)
var = dataset.__dict__
for i in v:
    print("ii " + str(i))
    print(dataset.variables[i])
print(dataset.run_start_year)
print(dataset.rotated_latitude_longitude())
print("AA")'''