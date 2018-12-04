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

from energy_demand.plotting import result_mapping
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(
        data_input,
        regions,
        simulation_yr_to_plot,
        population,
        fueltype_str,
        path_shapefile,
        fig_name
    ):
    """
    """
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

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

    regional_statistics_columns = [
        'name',
        'mean_peak_h',
        'diff_av_max',
        'mean_peak_h_pp',
        'diff_av_max_pp',
        'std_dev_average_every_h',
        'std_dev_peak_h_norm_pop']

    df_stats = pd.DataFrame(columns=regional_statistics_columns)

    for region_name, region_data in weather_yrs_data.items():

        # Convert regional data to dataframe
        region_data_array = np.array(region_data)
        df = pd.DataFrame(
            region_data_array,
            columns=range(8760))

        # Calculate regional statistics
        mean = df.mean(axis=0)
        std_dev = df.std(axis=0) #standard deviation across every hour

        # Get maximum per colum
        #max_every_h = df.max()
        #colum_max_h = max_every_h.argmax() #get colum (respesctively hour) of maximum value

        # Average standard deviation across every hour
        std_dev_average_every_h = np.std(list(std_dev))

        max_entry = df.max(axis=0) #maximum entry for every hour
        min_entry = df.min(axis=0) #maximum entry for every hour

        # Get hour number with maximum demand
        hour_nr_max = max_entry.argmax()
        hour_nr_min = min_entry.argmin()

        # standard deviation of peak hour
        std_dev_peak_h = std_dev[hour_nr_max]

        # Difference between average and max
        diff_av_max = max_entry[hour_nr_max] - mean[hour_nr_max]
        mean_peak_h = mean[hour_nr_max]

        # Convert GW to KW
        diff_av_max = diff_av_max * 1000000 #GW to KW
        mean_peak_h = mean_peak_h * 1000000 #GW to KW

        # Weight with population
        for region_nr, n in enumerate(regions):
            if region_name == n:
                nr_of_reg = region_nr
                break
        pop = population[nr_of_reg]

        # Divide standard deviation of peak hour by population
        # which gives measure of weather variability in peak hour
        std_dev_peak_h_norm_pop = std_dev_peak_h / pop

        diff_av_max_pp = diff_av_max / pop
        mean_peak_h_pp = mean_peak_h / pop

        line_entry = [[
            str(region_name),
            mean_peak_h,
            diff_av_max,
            mean_peak_h_pp,
            diff_av_max_pp,
            std_dev_average_every_h,
            std_dev_peak_h_norm_pop]]

        line_df = pd.DataFrame(
            line_entry, columns=regional_statistics_columns)
    
        df_stats = df_stats.append(line_df)

    print(df_stats['diff_av_max'].max())
    print(df_stats['mean_peak_h'].max())
    print(df_stats['std_dev_peak_h_norm_pop'].max())
    print("-")
    print(df_stats['diff_av_max_pp'].max())
    print(df_stats['diff_av_max_pp'].min())
    print("-")
    print(df_stats['mean_peak_h_pp'].max())
    print(df_stats['mean_peak_h_pp'].min())
    # ---------------
    # Create spatial maps
    # http://darribas.org/gds15/content/labs/lab_03.html
    # http://nbviewer.jupyter.org/gist/jorisvandenbossche/57d392c085901eb4981054402b37b6b1
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
    #bin_values = [0, 0.0025, 0.005, 0.0075, 0.01]
    #bin_values = [0, 0.02, 0.04, 0.06, 0.08, 0.1] #list(np.arange(0.0, 1.0, 0.1))

    # Field to plot
    field_to_plot = "diff_av_max_pp" # Difference between average and peak per person in KWh
    #field_to_plot = "diff_av_max"    # Difference between average and peak
    field_to_plot = 'std_dev_peak_h_norm_pop'

    nr_of_intervals = 6

    bin_values = result_mapping.get_reasonable_bin_values_II(
        data_to_plot=list(uk_gdf[field_to_plot]),
        nr_of_intervals=nr_of_intervals)
    print(float(uk_gdf[field_to_plot]))
    print("BINS " + str(bin_values))

    uk_gdf, cmap_rgb_colors, color_zero, min_value, max_value = user_defined_bin_classification(
        uk_gdf,
        field_to_plot, 
        bin_values=bin_values)

    # plot with face color attribute
    uk_gdf.plot(ax=ax, facecolor=uk_gdf['bin_color'], edgecolor='black', linewidth=0.5)

    #shp_gdp_merged.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    #ax = uk_gdf.plot(column='diff_av_max', scheme='QUANTILES', k=5, cmap='OrRd', linewidth=0.1)
    #uk_gdf[uk_gdf['name'] == 'E06000024'].plot(ax=ax, facecolor='green', edgecolor='black')
    #uk_gdf[uk_gdf['diff_av_max'] < 0.01].plot(ax=ax, facecolor='blue', edgecolor='black')

    # Get legend patches TODO IMPROVE
    # TODO IMRPVE: MAKE CORRECT ONE FOR NEW PROCESSING
    legend_handles = result_mapping.get_legend_handles(
        bin_values[1:-1],
        cmap_rgb_colors,
        color_zero,
        min_value,
        max_value)

    plt.legend(
        handles=legend_handles,
        title="tittel_elgend",
        prop={'size': 8},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False)

    # PLot bins on plot
    plt.text(
        0,
        -20,
        bin_values[:-1], #leave away maximum value
        fontsize=8)

    plt.tight_layout()
    plt.show()
    raise Exception
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
        cmap_diverging=None,
        cmap_sequential=None

    ):
    """Classify values according to bins

    Arguments
    ---------
    input_df : dataframe
        Dataframe to plot

    higher_as_bin : int
        Bin value of > than last bin
    cmap_sequential : str
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr',
        'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu',
        'PuBuGn', 'BuGn', 'YlGn'
    cmap_diverging : str
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn',
        'Spectral', 'coolwarm', 'bwr', 'seismic'

    Info
    -----
    Include 0 in min_max_plot == False
    Python colors:
    https://matplotlib.org/1.4.1/examples/color/colormaps_reference.html
    https://ocefpaf.github.io/python4oceanographers/blog/2015/08/24/choropleth/ 

    https://matplotlib.org/examples/color/colormaps_reference.html

    """
    # Check if largest value is large than last bin
    max_real_value = float(input_df[field_name].max())
    min_real_value = float(input_df[field_name].min())

    if max_real_value > 0 and min_real_value < 0:
        min_max_plot = True
    else:
        min_max_plot = False

    if not min_max_plot:

        # If only minus values
        if max_real_value < 0: #only min values
            if min_real_value > bin_values[0]:
                # add "higher as bin"
                bin_values.insert(0, min_real_value)
            elif bin_values[0] < min_real_value:
                crit_append_val = False
                raise Exception("The minimum user defined bin smaller is larger than minimum existing value")

            if not cmap_sequential:
                cmap, cmap_rgb_colors = norm_cmap(bin_values[:1], cmap='Purples') #'YlOrBr'
            else:
                cmap, cmap_rgb_colors = norm_cmap(bin_values[:1], cmap=cmap_sequential) #'YlOrBr'

        else: #only positive values
            if max_real_value > bin_values[-1]:
                # add "higher as bin"
                bin_values.append(max_real_value)
            elif bin_values[-1] > max_real_value:
                raise Exception("The maximum user defined bin value is larger than maximum value")
            if not cmap_sequential:
                cmap, cmap_rgb_colors = norm_cmap(bin_values[1:], cmap='Purples')
            else:
                cmap, cmap_rgb_colors = norm_cmap(bin_values[1:], cmap=cmap_sequential)

        # e.g. [0, 3, 6] --> generates (0, 3], and (3, 6] bin
        input_df['bin_color'] = pd.cut(input_df[field_name], bin_values, right=True, labels=cmap_rgb_colors)

        color_zero = 'grey' # default
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

        if not cmap_diverging:
            cmap, cmap_rgb_colors = norm_cmap(bin_values, cmap='coolwarm')
        else:
            cmap, cmap_rgb_colors = norm_cmap(bin_values, cmap=cmap_diverging)

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

    return input_df, cmap_rgb_colors, color_zero, min_real_value, max_real_value
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
