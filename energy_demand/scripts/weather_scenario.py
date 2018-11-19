"""
Load weather simulation data

http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf

Near future data
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/

http://joehamman.com/2013/10/12/plotting-netCDF-data-with-Python/

"""
import csv
import pandas as pd
import pytemperature
import xarray as xr
import numpy as np

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

    #columns = df.columns
    #df_365 = pd.DataFrame(columns=columns)

    out_list = []
    # Copy every sithieth day over the year and duplicate it. Do this five times --> get from 360 to 365 days
    vals = []
    day_cnt, day_cnt_365 = 0, 0

    for index, row in df.iterrows():
        day_cnt += 1
        # Create row into dataframe
        #df_row = pd.DataFrame([list(row)], columns=columns)
    
        # Copy extra day
        if day_cnt in days_to_duplicate:
            #df_row['time'] = day_cnt_365 # Add yearday
            #df_365 = df_365.append(df_row)
            out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])
            day_cnt_365 += 1

        # Copy day
        day_cnt_365 += 1
        #df_row['time'] = day_cnt_365 # Add yearday
        #df_365 = df_365.append(df_row)
        out_list.append([row['lat'], row['lon'], day_cnt_365, row[attribute]])
   
        # Reset counter if next weather station
        if day_cnt == 360:
            day_cnt = 0
            day_cnt_365 = 0

    return out_list

def write_wether_data(list_max, data_list):
    """Write weather data to array
    """
    station_coordinates = {}

    assert not len(list_max) % 365 #Check if dividable by 365
    nr_stations = int(len(list_max) / 365)
    print("Nr of stations:" + str(nr_stations))

    stations_data = np.zeros((nr_stations, 365))
    station_data = np.zeros((365))

    station_id_cnt = 0
    cnt = 0
    for data_entry in data_list:
        print("data_entry" + str(data_entry))
        print(cnt)
        station_data[cnt] = data_entry

        if cnt == 364:
            # Data of weather station
            stations_data[station_id_cnt] = station_data

            # Weather station metadata
            station_lon = data_entry['lon']
            station_lat = data_entry['lat']

            station_id = "station_id_{}".format(station_id_cnt)
            station_coordinates[station_id] = {
                'longitude':station_lat,
                'latitude': station_lon}

            # Reset
            station_data = np.zeros((365))
            station_id_cnt += 1
            cnt = 0

    return station_coordinates, stations_data

def get_meterological_equation_case(t_min, t_max, t_base):
    """Get Case number to calculate hdd with Meteorological Office
    equations
    """
    d_base_min = t_base - t_min
    d_base_max = d_base_max - t_base

    # Condition i
    if t_max <= t_base:
        return 1
    elif (t_min < t_base) and ((t_max - t_base) < (t_base - t_min)):
        return 2
    elif (t_max > t_base) and ((t_max - t_base) > (t_base - t_min)):
        return 3
    elif t_min >= t_base:
        return 4
    else:
        raise Exception("Error in calculating methorological office equation case")

def calc_met_equation_hdd(case, t_max, t_min, t_base):
    """
    """
    if case == 1:
        hdd = t_base - 0.5 * (t_max + t_min)
    elif case == 2:
        hdd = 0.5 * (t_base - t_min) - 0.25 * (t_max - t_base)
    elif case == 3:
        hdd = 0,25 * (t_base - t_min)
    else:
        hdd = 0
    return hdd

def calc_HDD_from_min_max(t_min, t_max, base_temp):
    """Calculate hdd for every day and weather station

    The Meteorological Office equations


    """
    hdd_array = np.zeros((365))

    # Calculate hdd
    for yearday in range(365):
        case_met_equation = get_meterological_equation_case(t_min, t_max, base_temp)

    return hdd_array

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
print("---")
print(len(stations_t_max))
print(len(stations_t_min))

# Convert weather station data to HDD days
for station_nr in enumerate(station_coordinates):

    t_min = stations_t_min[station_nr]
    t_max = stations_t_max[station_nr]

    case_nr = get_meterological_equation_case(
        t_min,
        t_max,
        t_base)

    hdd = calc_met_equation_hdd(
        case_nr,
        t_min,
        t_max)
    


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
'''
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