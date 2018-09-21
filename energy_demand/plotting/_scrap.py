import pandas as pd
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt

df = pd.DataFrame(
    {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
     'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
     'Latitude': [-34.58, -15.78, -33.45, 4.60, 10.48],
     'Longitude': [-58.66, -47.91, -70.66, -74.08, -66.86]})

df['Coordinates'] = list(zip(df.Longitude, df.Latitude))


df['Coordinates'] = df['Coordinates'].apply(Point)

gdf = geopandas.GeoDataFrame(df, geometry='Coordinates')

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))


# We restrict to South America.
#ax = world[world.continent == 'South America'].plot(
#    color='white', edgecolor='black')
ax = world[world.name == "United Kingdom"].plot(
    color='white', edgecolor='black')
#uk =  world[world.name == "United Kingdom"]

# We can now plot our GeoDataFrame.
gdf.plot(ax=ax, color='red')

plt.show()

print("aa")
