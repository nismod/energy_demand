"""Fig 2 figure
"""
import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import mstats
import pandas as pd
import geopandas as gpd
from scipy import stats
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt
from collections import defaultdict

from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(
        data_input,
        regions,
        fueltype_str,
        simulation_yr_to_plot,
        path_shapefile,
        fig_name
    ):
    """
    """
    # Select period and fueltype
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    columns = range(8760)
    # -----------------------------------------------------------
    # Iterate overall weather_yrs and store data in dataframe
    # (columns = timestep, rows: value of year)
    # -----------------------------------------------------------

    # List of selected data for every weather year and region (which is then converted to array)
    weather_yrs_data = defaultdict(dict)

    print("Weather yrs: " + str(list(data_input.keys())), flush=True)

    for weather_yr, data_weather_yr in data_input.items():

        # Weather year specific data for every region
        regions_fuel = data_weather_yr[simulation_yr_to_plot][fueltype_int]     # Select fueltype

        for region_nr, region_name in enumerate(regions):
            try:
                weather_yrs_data[region_name].append(regions_fuel[region_nr])
            except (KeyError, AttributeError):
                weather_yrs_data[region_name] = [regions_fuel[region_nr]]

    regional_statistics_columns = ['name', 'mean_peak_h', 'diff_av_max'] #'std', 'diff_av_max']
    df_stats = pd.DataFrame(columns=regional_statistics_columns)

    for region_name, region_data in weather_yrs_data.items():

        # Convert regional data to dataframe
        region_data_array = np.array(region_data)
        df = pd.DataFrame(region_data_array, columns=columns)

        # Calculate regional statistics
        mean = df.mean(axis=0)
        #std =  df.std(axis=0) #8760
        max_entry = df.max(axis=0) #maximum entry for every hour
        min_entry = df.min(axis=0) #maximum entry for every hour

        # Get hour number with maximum demand
        hour_nr_max = max_entry.argmax()
        hour_nr_min = min_entry.argmin()

        # Difference between average and max
        diff_av_max = max_entry[hour_nr_max] - mean[hour_nr_max]
        mean_peak_h = mean[hour_nr_max]

        # Weight with population

        line_entry = [[
            str(region_name),
            mean_peak_h,
            #std,
            diff_av_max]]

        line_df = pd.DataFrame(line_entry, columns=regional_statistics_columns)
        df_stats = df_stats.append(line_df)

    print("tt") #TODO IMPROVE
    # CREATE MAPS

    # Load uk shapefile
    uk_shapefile = geopandas.read_file(path_shapefile)

    # Merge stats to geopanda
    shp_gdp_merged = uk_shapefile.merge(
        df_stats,
        on='name')
    
    print("ff")
    print(shp_gdp_merged['name'])
    # Assign correct projection
    crs = {'init': 'epsg:27700'} #27700 == OSGB_1936_British_National_Grid
    uk_gdf = geopandas.GeoDataFrame(shp_gdp_merged, crs=crs)
    uk_gdf = uk_gdf.to_crs({'init' :'epsg:4326'})
    #ax = uk_gdf.plot(color='white', edgecolor='black')

    #shp_gdp_merged.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    ax = shp_gdp_merged.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)

    # --------
    # http://darribas.org/gds15/content/labs/lab_03.html
    #http://nbviewer.jupyter.org/gist/jorisvandenbossche/57d392c085901eb4981054402b37b6b1

    shp_gdp_merged[shp_gdp_merged['name'] == 'E06000024'].plot(ax=ax, facecolor='green')
    #for poly in shp_gdp_merged['geometry']:
    #    shp_gdp_merged.plotting.plot_multipolygon(ax, poly, facecolor='black', linewidth=0.025)
    '''for index, row in shp_gdp_merged.iterrows():
        poly = row['geometry']

        if row['name'] == 'E06000024':
            poly.plot()
            #gpd.plot(ax, poly, alpha=1, facecolor='red', linewidth=0)
            #gpd.plotting.plot_multipolygon(ax, poly, alpha=1, facecolor='red', linewidth=0)'''
    plt.show()
    raise Exception
    plt.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='best',
        frameon=False,
        shadow=True)

    plt.show()

    plt.savefig(fig_name)
    plt.close()


def uk_choropleth_map(input_df, path_shapefile, fig_path):
    """Create map with LADs
    df = pd.DataFrame(
        {'src_id': [...],
        'longitude': [...],
        'latitude': [...]})
    """
    # Convert dict to dataframe
    #df = pd.DataFrame.from_dict(input_df, orient='index')

    #df['Coordinates'] = list(zip(df.longitude, df.latitude))
    #df['Coordinates'] = df['Coordinates'].apply(Point)

    # Load uk shapefile
    uk_shapefile = geopandas.read_file(path_shapefile)

    # Assign correct projection
    crs = {'init': 'epsg:27700'} #27700 == OSGB_1936_British_National_Grid
    uk_gdf = geopandas.GeoDataFrame(uk_shapefile, crs=crs)

    # Transform
    uk_gdf = uk_gdf.to_crs({'init' :'epsg:4326'})

    # Plot
    ax = uk_gdf.plot(color='white', edgecolor='black')

    # print coordinates
    #world.plot(column='gdp_per_cap', cmap='OrRd', scheme='quantiles');

    plt.savefig(fig_path)
