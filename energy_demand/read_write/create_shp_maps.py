#http://darribas.org/gds15/content/labs/lab_03.html
#https://stackoverflow.com/questions/31755886/choropleth-map-from-geopandas-geodatafame

import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import pysal as ps
from pysal.contrib.viz import mapping as maps

print("---start")

# Load shapefile
shapefile_link = 'C:/Users/cenv0553/nismod/data_energy_demand/_MULT2/a/_result_data/result_shapefiles/fuel_y.shp'
#shapefile_link = 'C:/Users/cenv0553/nismod/data_energy_demand/_raw_data/C_LAD_geography/lad_2016.shp'
lads_shapes = gpd.read_file(shapefile_link)

print("TYPE " + str(type(lads_shapes)))

# ---------------------------
# Add clumn with data
# ---------------------------
# 1. Create a GeoDataFrame with joing attribute and values
#http://geopandas.org/mergingdata.html
merge_data = {
    'join_attribute_col1': [9999, 9999],
    'geo_code': ['W06000016', 'S12000013']}

merge_dataframe = pd.DataFrame(data=merge_data)
print(merge_dataframe)
print("..")

lads_shapes.merge(merge_dataframe, on='geo_code')

print("MERGED")
# ---------------------------
# PLots
# ---------------------------

fig_map, ax = plt.subplots(1, figsize=(5, 10))
#ax = lads_shapes.plot(axes=ax)
ax = plot_dataframe(lads_shapes, column='CRIME', scheme='QUANTILES', k=3, colormap='OrRd', legend=True)
fig_map.suptitle('testtile')

lims = plt.axis('equal') #Make that not distorted

plt.show()

#ax = plot_dataframe(lads_shapes, column='CRIME', scheme='QUANTILES', k=3, colormap='OrRd', legend=True)
print("finished")