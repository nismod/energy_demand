"""
Load weather simulation data

http://data.ceda.ac.uk//badc//weather_at_home/data/marius_time_series/CEDA_MaRIUS_Climate_Data_Description.pdf

Near future data
http://data.ceda.ac.uk/badc/weather_at_home/data/marius_time_series/near_future/data/

http://joehamman.com/2013/10/12/plotting-netCDF-data-with-Python/

"""
import pandas as pd
import pytemperature
import xarray as xr

tasmax = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmax_daily_g2_2020.nc"
tasmin = "C:/_WEATHERDATA/nf-2020/2020/m00m/daily/WAH_m00m_tasmin_daily_g2_2020.nc"

out_path = "C:/_scrap/test.csv"
out_path_station_names = "C:/_scrap/station_position.csv"
ds_max = xr.open_dataset(tasmax)
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
df_min['tasmin'] = df_min['tasmin'].apply(pytemperature.k2c)

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