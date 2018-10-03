"""Fig 2 figure
"""
import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import mstats
import pandas as pd
import geopandas as gpd
from scipy import stats
from shapely.geometry import Point
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.colors import Normalize

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
    # ---------------
    # Create spatial maps
    # http://darribas.org/gds15/content/labs/lab_03.html
    #http://nbviewer.jupyter.org/gist/jorisvandenbossche/57d392c085901eb4981054402b37b6b1
    # ---------------
    # Load uk shapefile
    uk_shapefile = gpd.read_file(path_shapefile)

    # Merge stats to geopanda
    shp_gdp_merged = uk_shapefile.merge(
        df_stats,
        on='name')

    # Assign projection
    crs = {'init': 'epsg:27700'} #27700: OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(shp_gdp_merged, crs=crs)

    ax = uk_gdf.plot()

    # Assign bin colors according to defined cmap and whether
    # plot with min_max values or only min/max values
    uk_gdf = user_defined_bin_classification(
        uk_gdf,
        "diff_av_max",
        bin_values=[0, 0.01])
    
    uk_gdf.plot(ax=ax, facecolor=uk_gdf['bin_color'], edgecolor='black')
    plt.show()
    #shp_gdp_merged.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    #ax = uk_gdf.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    

    #uk_gdf[uk_gdf['name'] == 'E06000024'].plot(ax=ax, facecolor='green', edgecolor='black')
    #uk_gdf[uk_gdf['diff_av_max'] < 0.01].plot(ax=ax, facecolor='blue', edgecolor='black')


    #plt.show()
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

def norm_cmap(values, cmap, vmin=None, vmax=None):
    """
    Normalize and set colormap

    Parameters
    ----------
    values : Series or array to be normalized
    cmap : matplotlib Colormap
    normalize : matplotlib.colors.Normalize
    cm : matplotlib.cm
    vmin : Minimum value of colormap. If None, uses min(values).
    vmax : Maximum value of colormap. If None, uses max(values).

    Returns
    -------
    n_cmap : mapping of normalized values to colormap (cmap)

    Source
    ------
    https://ocefpaf.github.io/python4oceanographers/blog/2015/08/24/choropleth/
    """
    mn = vmin or min(values)
    mx = vmax or max(values)
    norm = Normalize(vmin=mn, vmax=mx)
    n_cmap = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

    rgb_colors = [n_cmap.to_rgba(value) for value in values]

    return n_cmap, rgb_colors

def plot_colors(rgb_colors):
    """function to plot colors
    """
    nr_dots = len(rgb_colors)

    dots = []
    x = []
    y = []
    for i in range(nr_dots):
        x.append(i + 20)
        y.append(i + 20)
    
    #plt.scatter(x, y, c=cmap, s=50)
    plt.scatter(x, y, c=rgb_colors, s=50)

    plt.show()

def user_defined_bin_classification(
        input_df,
        field_name,
        bin_values,
    ):
    """Classify values according to bins
    and plot

    Arguments
    ---------
    input_df : dataframe
        Dataframe to plot
    
    higher_as_bin : int
        Bin value of > than last bin
    
    Info
    -----
    Include 0 in min_max_plot == False
    Python colors:
    https://matplotlib.org/1.4.1/examples/color/colormaps_reference.html
    https://ocefpaf.github.io/python4oceanographers/blog/2015/08/24/choropleth/ 

    https://matplotlib.org/examples/color/colormaps_reference.html

    """
    # Check if largest value is large than last bin
    max_real_value = input_df[field_name].max()
    min_real_value = input_df[field_name].min()

    if max_real_value > 0 and min_real_value < 0:
        min_max_plot = True
    else:
        min_max_plot = False
    # Get correct colors
    if not min_max_plot:

        # IF only minus values
        if max_real_value > 0: #only min values
            if min_real_value > bin_values[0]:
                # add "higher as bin"
                bin_values.insert(0, min_real_value)
            elif bin_values[0] < min_real_value:
                crit_append_val = False
                raise Exception("The minimum user defined bin smaller is larger than minimum existing value")

            # Sequential: 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
            cmap, cmap_rgb_colors = norm_cmap(
                bin_values[:1], #Remove 0 bin from colors
                cmap='YlOrBr')

        else: #only positive values
            if max_real_value > bin_values[-1]:
                # add "higher as bin"
                bin_values.append(max_real_value)
            elif bin_values[-1] > max_real_value:
                raise Exception("The maximum user defined bin value is larger than maximum value")

            # Sequential: 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
            cmap, cmap_rgb_colors = norm_cmap(
                bin_values[1:], #Remove 0 bin from colors
                cmap='YlOrBr')

        # e.g. [0, 3, 6] --> generates (0, 3], and (3, 6] bin
        input_df['bin_color'] = pd.cut(input_df[field_name], bin_values, right=True, labels=cmap_rgb_colors)

    else:

        if max_real_value < bin_values[-1]:
            raise Exception("The maximum user defined bin value is larger than maximum value")
        elif min_real_value > bin_values[0]:
            raise Exception("The minimum user defined bin smaller is larger than minimum existing value")
        else:
            pass

        # Add minimum and maximum value
        bin_values.append(max_real_value)
        bin_values.insert(0, min_real_value)

        # Diverging: 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'
        cmap, cmap_rgb_colors = norm_cmap(bin_values, cmap='coolwarm')

        # Reclassify zero value
        positive_bin_colors = []
        minus_bin_colors = []
        minus_bins = []
        positive_bins = [0]

        for cnt, i in enumerate(bin_values):
            if i < 0:
                minus_bin_colors.append(cmap_rgb_colors[cnt])
                minus_bins.append(i)
            elif i == 0:
                color_zero = cmap_rgb_colors[cnt]
            else:
                positive_bin_colors.append(cmap_rgb_colors[cnt])
                positive_bins.append(i)
        minus_bins.append(0)

        # ----
        # Classify
        # ----
        # Classify values in dataframe and assign color value as "bin" column
        minus_dataframe = input_df[field_name][input_df[field_name] < 0].to_frame()
        zero_dataframe = input_df[field_name][input_df[field_name] == 0].to_frame()
        plus_dataframe = input_df[field_name][input_df[field_name] > 0].to_frame()

        # e.g. [0, 3, 6] --> generates (0, 3], and (3, 6] bin
        minus_dataframe['bin_color'] = pd.cut(minus_dataframe[field_name], minus_bins, right=False, labels=minus_bin_colors)
        zero_dataframe['bin_color'] = [color_zero for _ in range(len(zero_dataframe))] #create list with zero color
        plus_dataframe['bin_color'] = pd.cut(plus_dataframe[field_name], positive_bins, right=True, labels=positive_bin_colors)
        
        # Add bins
        input_df = minus_dataframe.append(zero_dataframe)
        input_df = input_df.append(plus_dataframe)

    return input_df
    '''ax = input_df.plot()

    # Calculate color values

    #uk_gdf[uk_gdf['name'] == 'E06000024'].plot(ax=ax, facecolor='green', edgecolor='black')
    #uk_gdf[uk_gdf['diff_av_max'] < 0.01].plot(ax=ax, facecolor='blue', edgecolor='black')
    # Convert dict to dataframe
    #df = pd.DataFrame.from_dict(input_df, orient='index')

    #df['Coordinates'] = list(zip(df.longitude, df.latitude))
    #df['Coordinates'] = df['Coordinates'].apply(Point)

    # Load uk shapefile
    uk_shapefile = gpd.read_file(path_shapefile)

    # Assign correct projection
    crs = {'init': 'epsg:27700'} #27700 == OSGB_1936_British_National_Grid
    uk_gdf = gpd.GeoDataFrame(uk_shapefile, crs=crs)

    # Transform
    uk_gdf = uk_gdf.to_crs({'init' :'epsg:4326'})

    # Plot
    ax = uk_gdf.plot(color='white', edgecolor='black')

    # print coordinates
    #world.plot(column='gdp_per_cap', cmap='OrRd', scheme='quantiles');

    plt.savefig(fig_path)'''
