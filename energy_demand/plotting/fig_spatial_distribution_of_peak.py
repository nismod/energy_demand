"""
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.basic import basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions
from energy_demand.plotting import result_mapping
from energy_demand.plotting import fig_p2_weather_val

def run_fig_spatial_distribution_of_peak(
        scenarios,
        path_to_folder_with_scenarios,
        path_shapefile,
        sim_yrs,
        field_to_plot,
        unit,
        fig_path,
        fueltype_str='electricity'
    ):
    """
    """
    weather_yrs = []
    calculated_yrs_paths = []
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    for scenario in scenarios:
        path_scenario = os.path.join(path_to_folder_with_scenarios, scenario)
        all_result_folders = os.listdir(path_scenario)

        for result_folder in all_result_folders:
            try:
                split_path_name = result_folder.split("__")
                weather_yr = int(split_path_name[0])
                weather_yrs.append(weather_yr)
                tupyle_yr_path = (weather_yr, os.path.join(path_scenario))
                calculated_yrs_paths.append(tupyle_yr_path)
            except ValueError:
                pass

    for simulation_yr in sim_yrs:
        container = {}
        container['abs_demand_in_peak_h_pp'] = {}
        container['abs_demand_in_peak_h'] = {}
        container['p_demand_in_peak_h'] = {}

        for weather_yr, path_data_ed in calculated_yrs_paths:
            print("... prepare data {} {}".format(weather_yr, path_data_ed))

            path_to_weather_yr = os.path.join(path_data_ed, "{}__{}".format(weather_yr, 'all_stations'))

            data = {}
            data['lookups'] = lookup_tables.basic_lookups()
            data['enduses'], data['assumptions'], regions = data_loader.load_ini_param(os.path.join(path_data_ed))
            data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
            data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

            # Population 
            population_data = read_data.read_scenaric_population_data(os.path.join(path_data_ed, 'model_run_pop'))

            results_container = read_data.read_in_results(
                os.path.join(path_to_weather_yr, 'model_run_results_txt'),
                data['assumptions']['seasons'],
                data['assumptions']['model_yeardays_daytype'])

            # ---------------------------------------------------
            # Calculate hour with national peak demand
            # This may be different depending on the weather yr
            # ---------------------------------------------------
            ele_regions_8760 = results_container['ed_fueltype_regs_yh'][simulation_yr][fueltype_int]
            sum_all_regs_fueltype_8760 = np.sum(ele_regions_8760, axis=0) # Sum for every hour

            max_day = int(basic_functions.round_down((np.argmax(sum_all_regs_fueltype_8760) / 24), 1))
            max_h = np.argmax(sum_all_regs_fueltype_8760)
            max_demand = np.max(sum_all_regs_fueltype_8760)

            # Calculate the national peak demand in GW
            national_peak_GW = np.max(sum_all_regs_fueltype_8760)

            # ------------------------------------------------------
            # Calculate the contribution of the regional peak demand
            # ------------------------------------------------------
            demand_in_peak_h = ele_regions_8760[:, max_h]

            if unit == 'GW':
                container['abs_demand_in_peak_h'][weather_yr] = demand_in_peak_h
            elif unit == 'kW':
                container['abs_demand_in_peak_h'][weather_yr] = demand_in_peak_h * 1000000 # Convert to KWh
            else:
                # Use GW as default
                container['abs_demand_in_peak_h'][weather_yr] = demand_in_peak_h

            container['abs_demand_in_peak_h_pp'][weather_yr] = demand_in_peak_h / population_data[simulation_yr]
    
            # Relative fraction of regional demand in relation to peak
            container['p_demand_in_peak_h'][weather_yr] = (demand_in_peak_h / national_peak_GW ) * 100 # given as percent

            print("=================================")
            print("{}  {}  {}  {}".format(
                simulation_yr,
                weather_yr,
                np.sum(ele_regions_8760),
                national_peak_GW))

        # --------------
        # Create dataframe with all weather yrs calculatiosn for every region
            
        #               region1, region2, region3
        # weather yr1
        # weather yr2
        # --------------
        # Convert regional data to dataframe
        abs_demand_in_peak_h_pp = np.array(list(container['abs_demand_in_peak_h_pp'].values()))
        abs_demand_peak_h = np.array(list(container['abs_demand_in_peak_h'].values()))
        p_demand_peak_h = np.array(list(container['p_demand_in_peak_h'].values()))

        # Absolute demand
        df_abs_peak_demand = pd.DataFrame(
            abs_demand_peak_h,
            columns=regions,
            index=list(container['abs_demand_in_peak_h'].keys()))

        # Relative demand
        df_p_peak_demand = pd.DataFrame(
            p_demand_peak_h,
            columns=regions,
            index=list(container['p_demand_in_peak_h'].keys()))
        
        df_abs_demand_in_peak_h_pp = pd.DataFrame(
            abs_demand_in_peak_h_pp,
            columns=regions,
            index=list(container['abs_demand_in_peak_h_pp'].keys()))

        # Absolute peak value - mean
        max_peak_h_across_weather_yrs = df_abs_peak_demand.max()
        average_across_weather_yrs = df_abs_peak_demand.mean()
        diff_peak_h_minus_mean = max_peak_h_across_weather_yrs - average_across_weather_yrs

        for index, row in df_p_peak_demand.iterrows():
            print("Weather yr: {} Total p: {}".format(index, np.sum(row)))
            assert round(np.sum(row), 4) == 100.0

        # ----------------------------
        # Calculate standard deviation
        # ----------------------------
        std_deviation_df_abs_demand_in_peak_h_pp = df_abs_demand_in_peak_h_pp.std()
        std_deviation_abs_demand_peak_h = df_abs_peak_demand.std()
        std_deviation_p_demand_peak_h = df_p_peak_demand.std()

        print("=========")
        print("National stats")
        print("=========")
        print("Sum of std of absolut peak demand:  " + str(np.sum(std_deviation_abs_demand_peak_h)))

        # --------------------
        # Create map
        # --------------------
        regional_statistics_columns = [
            'name',
            'std_deviation_p_demand_peak_h',
            'std_deviation_abs_demand_peak_h',
            'std_deviation_df_abs_demand_in_peak_h_pp',
            'diff_peak_h_minus_mean']

        df_stats = pd.DataFrame(columns=regional_statistics_columns)

        for region_name in regions:

            # 'name', 'absolute_GW', 'p_GW_peak'
            line_entry = [[
                region_name,
                std_deviation_p_demand_peak_h[region_name],
                std_deviation_abs_demand_peak_h[region_name],
                std_deviation_df_abs_demand_in_peak_h_pp[region_name],
                diff_peak_h_minus_mean[region_name],
                ]]

            line_df = pd.DataFrame(line_entry, columns=regional_statistics_columns)
            df_stats = df_stats.append(line_df)

        # Load uk shapefile
        uk_shapefile = gpd.read_file(path_shapefile)

        # Merge stats to geopanda
        shp_gdp_merged = uk_shapefile.merge(
            df_stats,
            on='name')

        # Assign projection
        crs = {'init': 'epsg:27700'} #27700: OSGB_1936_British_National_Grid
        uk_gdf = gpd.GeoDataFrame(shp_gdp_merged, crs=crs)

        ax = uk_gdf.plot(
            figsize=basic_plot_functions.cm2inch(25, 20))

        nr_of_intervals = 6

        bin_values = result_mapping.get_reasonable_bin_values_II(
            data_to_plot=list(uk_gdf[field_to_plot]),
            nr_of_intervals=nr_of_intervals)
        # Maual bins
        #bin_values = [0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
        print(float(uk_gdf[field_to_plot].max()))
        print("BINS " + str(bin_values))

        uk_gdf, cmap_rgb_colors, color_zero, min_value, max_value = fig_p2_weather_val.user_defined_bin_classification(
            uk_gdf,
            field_to_plot,
            bin_values=bin_values)

        # plot with face color attribute
        uk_gdf.plot(
            ax=ax,
            facecolor=uk_gdf['bin_color'],
            edgecolor='black',
            linewidth=0.5)

        legend_handles = result_mapping.add_simple_legend(
            bin_values,
            cmap_rgb_colors,
            color_zero)

        plt.legend(
            handles=legend_handles,
            title="{}  [{}]".format(field_to_plot, unit),
            prop={'size': 8},
            #loc='upper center', bbox_to_anchor=(0.5, -0.05),
            loc='center left', bbox_to_anchor=(1, 0.5),
            frameon=False)

        # PLot bins on plot
        '''plt.text(
            -20,
            -20,
            bin_values[:-1], #leave away maximum value
            fontsize=8)'''

        plt.tight_layout()

        fig_out_path = os.path.join(fig_path, str(field_to_plot) + "__" + str(simulation_yr) + ".pdf")
        plt.savefig(fig_out_path)
