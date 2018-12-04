"""Loads all necessary data
"""
import os
import csv
import logging
import configparser
import ast
from collections import defaultdict
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

from energy_demand.basic import lookup_tables
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data, read_weather_data
from energy_demand.basic import conversions
from energy_demand.plotting import fig_lp
from energy_demand.basic import basic_functions
from energy_demand.read_write import narrative_related

def print_closest_and_region(stations_as_dict, region_to_plot, closest_region):
    """Function used to test if the closest weather region is assigned
    """

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world[world.name == "United Kingdom"].plot(
        color='white', edgecolor='black')

    # Plot all weather stations
    df = pd.DataFrame.from_dict(stations_as_dict, orient='index')
    df['Coordinates'] = list(zip(df.longitude, df.latitude))
    df['Coordinates'] = df['Coordinates'].apply(Point)
    gdf = gpd.GeoDataFrame(df, geometry='Coordinates')
    gdf.plot(ax=ax, color='blue')

    # Plot region coordinate
    df2 = pd.DataFrame.from_dict(region_to_plot, orient='index')
    df2['Coordinates'] = list(zip(df2.longitude, df2.latitude))
    df2['Coordinates'] = df2['Coordinates'].apply(Point)
    gdf_region = gpd.GeoDataFrame(df2, geometry='Coordinates')
    gdf_region.plot(ax=ax, color='red')

    # PLot closest weather station
    df3 = pd.DataFrame.from_dict(closest_region, orient='index')
    df3['Coordinates'] = list(zip(df3.longitude, df3.latitude))
    df3['Coordinates'] = df3['Coordinates'].apply(Point)
    gdf_closest = gpd.GeoDataFrame(df3, geometry='Coordinates')
    gdf_closest.plot(ax=ax, color='green')

    plt.legend()

def create_weather_station_map(
        stations_as_dict,
        fig_path,
        path_shapefile=False
    ):
    """Plot the spatial disribution of the weather stations

    https://geopandas.readthedocs.io/en/latest/gallery/create_geopandas_from_pandas.html

    df = pd.DataFrame(
        {'src_id': [...],
        'longitude': [...],
        'latitude': [...]})
    """
    if stations_as_dict == {}:
        print("No stations available to plot")
    else:
        # Convert dict to dataframe
        df = pd.DataFrame.from_dict(stations_as_dict, orient='index')

        df['Coordinates'] = list(zip(df.longitude, df.latitude))
        df['Coordinates'] = df['Coordinates'].apply(Point)

        if path_shapefile is False:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            ax = world[world.name == "United Kingdom"].plot(
                color='white', edgecolor='black')
        else:
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
        crs = {'init': 'epsg:4326'}
        gdf = gpd.GeoDataFrame(df, geometry='Coordinates') # crs=crs,
        gdf.plot(ax=ax, color='red')

        plt.savefig(fig_path)

        # ---------------------------------
        # Save coordinates as file
        # ---------------------------------
        station_infos = ["name, latitue, longitude"]
        fig_path = fig_path[:-4] + ".txt"
        for station in stations_as_dict:
            station_info = "{}, {}, {}".format(
                station,
                stations_as_dict[station]['latitude'],
                stations_as_dict[station]['longitude'])
            station_infos.append(station_info)

        write_data.write_list_to_txt(fig_path, station_infos)

def read_weather_stations_raw(path_to_csv):
    """Read in weather stations from csv file

    Parameter
    ---------
    path_to_csv : string
        Path to csv with stored weater station data

    Returns:
    --------
    weather_stations : dict
        Contains coordinates and station_id of weather stations

    Note
    ----
    Downloaded from MetOffice
    http://archive.ceda.ac.uk/cgi-bin/midas_stations/search_by_name.cgi.py?name=&minyear=&maxyear=&current=n&db=midas_stations&orderby=id (21-09-2018)
    """
    df_stations = pd.read_csv(path_to_csv)

    weather_stations = {}

    for _, row in df_stations.iterrows():

        # Filter out not fitting weather stations
        if float(row['Longitude']) < -8:
            pass
        elif float(row['Latitude']) < 50:
            pass
        else:
            weather_stations[int(row['src_id'])] = {
                'latitude' : float(row['Latitude']), #TODO CHANGE TO 'ltatitude
                'longitude': float(row['Longitude'])} #TODO CHANGE TO 'ltatitude

    return weather_stations

def replace_variable(_user_defined_vars, strategy_vars):
    """Replace default strategy variables with user
    defined variables

    Arguments
    ----------
    _user_defined_vars : dict
        User defined strategy variables
    strategy_vars : dict
        Default strategy variables

    Returns
    -------
    strategy_vars : dict
        Updated strategy variables with user defined inputs
    """
    for new_var, new_var_vals in _user_defined_vars.items():

        crit_single_dim = narrative_related.crit_dim_var(new_var_vals)

        if crit_single_dim:
            strategy_vars[new_var] = new_var_vals
        else:
            for sub_var_name, sector_sub_var in new_var_vals.items():

                if type(sector_sub_var) is dict:
                    strategy_vars[new_var][sub_var_name] = {}
                    for sector, sub_var in sector_sub_var.items():
                        strategy_vars[new_var][sub_var_name][sector] = sub_var
                else:
                    strategy_vars[new_var][sub_var_name] = sector_sub_var

            strategy_vars[new_var] = strategy_vars[new_var]
    return strategy_vars

def load_local_user_defined_vars(
        default_strategy_var,
        path_csv,
        simulation_base_yr,
        simulation_end_yr
    ):
    """Load all strategy variables from file

    Arguments
    ---------
    default_strategy_var : dict
        default strategy var
    path_csv : str
        Path to folder with all user defined parameters
    simulation_base_yr : int
        Simulation base year

    Returns
    -------
    strategy_vars_as_narratives : dict
        Single or multidimensional parameters with fully autocompleted narratives
    """
    all_csv_in_folder = os.listdir(path_csv)

    # Files to ignore in this folder
    files_to_ignores = [
        'switches_capacity.csv',
        'switches_fuel.csv',
        'switches_service.csv',
        '_README_config_data.txt']

    strategy_vars_as_narratives = {}

    for file_name in all_csv_in_folder:
        if file_name in files_to_ignores:
            pass
        else:
            # Strategy variable name
            var_name = file_name[:-4] #remove ".csv"

            try:
                raw_file_content = pd.read_csv(os.path.join(path_csv, file_name))

                default_streategy_var = default_strategy_var[var_name]

                # Alternative loading
                strategy_vars_as_narratives[var_name] = narrative_related.read_user_defined_param(
                    raw_file_content,
                    simulation_base_yr=simulation_base_yr,
                    simulation_end_yr=simulation_end_yr,
                    default_streategy_var=default_streategy_var,
                    var_name=var_name)

            except KeyError:
                raise Exception("The user defined variable '{}' is not defined in model", var_name)

    return strategy_vars_as_narratives

def load_ini_param(path):
    """Load simulation parameter run information

    Arguments
    ---------
    path : str
        Path to `ini` file

    Returns
    -------
    enduses : dict
        Enduses
    assumptions : dict
        Assumptions
    reg_nrs : dict
        Number of regions
    regions : dict
        Regions
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(path, 'model_run_sim_param.ini'))

    regions = ast.literal_eval(config['REGIONS']['regions'])

    assumptions = {}
    assumptions['reg_nrs'] = int(config['SIM_PARAM']['reg_nrs'])
    assumptions['base_yr'] = int(config['SIM_PARAM']['base_yr'])
    assumptions['sim_yrs'] = ast.literal_eval(config['SIM_PARAM']['sim_yrs'])

    # -----------------
    # Other information
    # -----------------
    enduses = {}
    enduses['residential'] = ast.literal_eval(config['ENDUSES']['residential'])
    enduses['service'] = ast.literal_eval(config['ENDUSES']['service'])
    enduses['industry'] = ast.literal_eval(config['ENDUSES']['industry'])

    return enduses, assumptions, regions

def load_MOSA_pop(path_to_csv):
    """
    Load MPSA population
    """
    pop_data = defaultdict(dict)

    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows)

        for row in rows:
            lad_code = str.strip(row[read_data.get_position(headings, 'Local authority code')])
            MSOA_code = row[read_data.get_position(headings, 'MSOA Code')].strip()
            pop = float(row[read_data.get_position(headings, 'Persons')].strip().replace(",", ""))

            pop_data[lad_code][MSOA_code] = pop

    return pop_data

def read_lad_demands(path_to_csv):
    """Read in national consumption from csv file. The unit
    in the original csv is in GWh per region per year.

    Arguments
    ---------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    national_fuel_data : dict
        geocode, total consumption

    Source
    -----
    https://www.gov.uk/government/statistical-data-sets
    /regional-and-local-authority-gas-
    consumption-statistics-2005-to-2011
    https://www.gov.uk/government/statistical-data-sets
    /regional-and-local-authority-electricity-
    consumption-statistics-2005-to-2011
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows)

        for row in rows:
            geocode = str.strip(row[read_data.get_position(headings, 'LA Code')])
            tot_consumption_unclean = row[read_data.get_position(headings, 'Total consumption')].strip()

            if tot_consumption_unclean == '-':
                pass
            else:
                try:
                    national_fuel_data[geocode] = float(tot_consumption_unclean.replace(",", ""))
                except:
                    # no data provided
                    logging.debug("No validation data available for region %s", geocode)

    return national_fuel_data

def read_elec_data_msoa(path_to_csv):
    """Read in msoa consumption from csv file. The unit
    in the original csv is in kWh per region per year.

    Arguments
    ---------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    national_fuel_data : dict
        geocode, total consumption

    Info
    -----
    Source: https://www.gov.uk/government/statistical-data-sets
    /regional-and-local-authority-electricity-
    consumption-statistics-2005-to-2011
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows)

        for row in rows:
            geocode = str.strip(row[read_data.get_position(headings, 'msoa_code')])
            tot_consumption_unclean = row[read_data.get_position(headings, 'tot_conump_kWh')].strip()
            national_fuel_data[geocode] = float(tot_consumption_unclean.replace(",", ""))

    return national_fuel_data

def floor_area_virtual_dw(
        regions,
        sectors,
        local_paths,
        population,
        base_yr,
        f_mixed_floorarea=0.5
    ):
    """Load necessary data for virtual building stock
    in case the link to the building stock model in
    Newcastle is not used

    Arguments
    ---------
    regions : dict
        Regions
    sectors : dict
        All sectors
    local_paths : dict
        Paths
    base_yr : float
        Base year
    f_mixed_floorarea : float
        PArameter to redistributed mixed enduse
    regions_without_floorarea : float
        Regions with missing floor area info
    Returns
    -------
    rs_floorarea : dict
        Residential floor area
    ss_floorarea : dict
        Service sector floor area
    """
    # ------
    # Get average floor area per perons
    # Based on Roberts et al. (2011) , an average one bedroom home for 2 people has 46 m2.
    # Roberts et al. (2011): The Case for Space: the size of England’s new homes.
    # -----
    rs_avearge_floor_area_pp = 23   # [m2] Assumed average residential area per person
    ss_avearge_floor_area_pp = 23   # [m2] Assumed average service area per person

    # --------------------------------------------------
    # Floor area for residential buildings for base year
    # from newcasle dataset
    # --------------------------------------------------
    resid_footprint, non_res_flootprint, service_building_count = read_data.read_floor_area_virtual_stock(
        local_paths['path_floor_area_virtual_stock_by'],
        f_mixed_floorarea=f_mixed_floorarea)

    # -----------------
    # Calculate average floor area per person
    # of existing datasets. This is done to replace the missing
    # floor area data of LADs with estimated floor areas
    # -----------------
    rs_regions_without_floorarea = []
    rs_floorarea = defaultdict(dict)
    for region in regions:
        try:
            rs_floorarea[base_yr][region] = resid_footprint[region]
        except KeyError:
            ##print("No virtual residential floor area for region %s ", region)

            # Calculate average floor area
            rs_floorarea[base_yr][region] = rs_avearge_floor_area_pp * population[region]
            rs_regions_without_floorarea.append(region)

    # --------------------------------------------------
    # Floor area for service sector buildings
    # --------------------------------------------------
    ss_floorarea_sector_by = {}
    ss_regions_without_floorarea = set([])
    ss_floorarea_sector_by[base_yr] = defaultdict(dict)
    for region in regions:
        for sector in sectors['service']:
            try:
                ss_floorarea_sector_by[base_yr][region][sector] = non_res_flootprint[region]
            except KeyError:

                #logging.debug("No virtual service floor area for region %s", region)

                # Calculate average floor area if no data is available
                ss_floor_area_cy = ss_avearge_floor_area_pp * population[region]
                ss_floorarea_sector_by[base_yr][region][sector] = ss_floor_area_cy
                ss_regions_without_floorarea.add(region)

    return dict(rs_floorarea), dict(ss_floorarea_sector_by), service_building_count, rs_regions_without_floorarea, list(ss_regions_without_floorarea)

def get_local_paths(path):
    """Create all local paths

    Arguments
    --------
    path : str
        Path of local folder with data used for model

    Return
    -------
    paths : dict
        All local paths used in model
    """
    paths = {
        'local_path_datafolder': path,

        # Path to user defined strategy vars
        'path_strategy_vars': os.path.join(
            path, 'energy_demand', '00_user_defined_variables'),

        'path_population_data_for_disaggregation_LAD': os.path.join(
            path, 'energy_demand', '_raw_data', 'J-population_disagg_by', 'uk_pop_principal_2015_2050.csv'), #ONS principal projection
        'path_population_data_for_disaggregation_MSOA': os.path.join(
            path, 'energy_demand', '_raw_data', 'J-population_disagg_by', 'uk_pop_principal_2015_2050_MSOA_lad.csv'), #ONS principal projection
        'folder_raw_carbon_trust': os.path.join(
            path, 'energy_demand', '_raw_data', "G_Carbon_Trust_advanced_metering_trial"),
        'folder_path_weater_stations': os.path.join(
            path, 'energy_demand', '_raw_data', 'A-temperature_data', 'cleaned_weather_stations.csv'),
        'path_floor_area_virtual_stock_by': os.path.join(
            path, 'energy_demand', '_raw_data', 'K-floor_area', 'floor_area_LAD_latest.csv'),
        'path_assumptions_db': os.path.join(
            path, 'energy_demand', '_processed_data', 'assumptions_from_db'),
        'data_processed': os.path.join(
            path, 'energy_demand', '_processed_data'),
        'lad_shapefile': os.path.join(
            path, 'energy_demand', '_raw_data', 'C_LAD_geography', 'same_as_pop_scenario', 'lad_2016_uk_simplified.shp'),
        'path_post_installation_data': os.path.join(
            path, 'energy_demand', '_processed_data'),
        'weather_data': os.path.join(
            path, 'energy_demand', '_raw_data', 'A-temperature_data', 'cleaned_weather_stations_data'),
        'load_profiles': os.path.join(
            path, 'energy_demand', '_processed_data', 'load_profiles'),
        'rs_load_profile_txt': os.path.join(
            path, 'energy_demand', '_processed_data', 'load_profiles', 'rs_submodel'),
        'ss_load_profile_txt': os.path.join(
            path, 'energy_demand', '_processed_data', 'load_profiles', 'ss_submodel'),
        'yaml_parameters': os.path.join(
            path, '..', 'config', 'yaml_parameters.yml'),
        'yaml_parameters_constrained': os.path.join(
            path, '..', 'config', 'yaml_parameters_constrained.yml'),
        'yaml_parameters_keynames_constrained': os.path.join(
            path, '..', 'config', 'yaml_parameters_keynames_constrained.yml'),
        'yaml_parameters_keynames_unconstrained': os.path.join(
            path, '..', 'config', 'yaml_parameters_keynames_unconstrained.yml'),
        'yaml_parameters_scenario': os.path.join(
            path, '..', 'config', 'yaml_parameters_scenario.yml')}

    return paths

def get_result_paths(path):
    """Load all result paths

    Arguments
    --------
    path : str
        Path to result folder

    Return
    -------
    paths : dict
        All result paths used in model
    """
    paths = {
        'data_results':
            path,
        'data_results_model_run_pop': os.path.join(
            path, 'model_run_pop'),
        'data_results_model_runs': os.path.join(
            path, 'model_run_results_txt'),
        'data_results_PDF': os.path.join(
            path, 'PDF_results'),
        'data_results_validation': os.path.join(
            path, 'PDF_validation'),
        'model_run_pop': os.path.join(
            path, 'model_run_pop'),
        'data_results_shapefiles': os.path.join(
            path, 'spatial_results'),
        'individual_enduse_lp': os.path.join(
            path, 'individual_enduse_lp')}

    return paths

def load_paths(path):
    """Load all paths of the installed config data

    Arguments
    ----------
    path : str
        Main path

    Return
    ------
    out_dict : dict
        Data container containing dics
    """
    paths = {
        'path_main': path,

        # Path to all technologies
        'path_technologies': os.path.join(
            path, '05-technologies', 'technology_definition.csv'),

        # Paths to fuel raw data
        'rs_fuel_raw': os.path.join(
            path, '02-fuel_base_year', 'rs_fuel.csv'),
        'ss_fuel_raw': os.path.join(
            path, '02-fuel_base_year', 'ss_fuel.csv'),
        'is_fuel_raw': os.path.join(
            path, '02-fuel_base_year', 'is_fuel.csv'),

        # Load profiles
        'lp_rs': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'HES_lp.csv'),

        # Technologies load shapes
        'path_hourly_gas_shape_resid': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'lp_gas_boiler_dh_SANSOM.csv'),
        'lp_elec_hp_dh': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'lp_elec_hp_dh_LOVE.csv'),
        'lp_all_microCHP_dh': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'lp_all_microCHP_dh_SANSOM.csv'),
        'path_shape_rs_cooling': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'shape_residential_cooling.csv'),
        'path_shape_ss_cooling': os.path.join(
            path, '03-load_profiles', 'ss_submodel', 'shape_service_cooling.csv'),
        'lp_elec_storage_heating': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'lp_elec_storage_heating_HESReport.csv'),
        'lp_elec_secondary_heating': os.path.join(
            path, '03-load_profiles', 'rs_submodel', 'lp_elec_secondary_heating_HES.csv'),

        # Census data
        'path_employment_statistics': os.path.join(
            path, '04-census_data', 'LAD_census_data.csv'),

        # Validation datasets
        'val_subnational_elec': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec.csv'),
        'val_subnational_elec_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_domestic.csv'),
        'val_subnational_elec_non_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_non_domestic.csv'),
        'val_subnational_elec_msoa_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'MSOA_domestic_electricity_2015_cleaned.csv'),
        'val_subnational_elec_msoa_non_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'MSOA_non_dom_electricity_2015_cleaned.csv'),
        'val_subnational_gas': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas.csv'),
        'val_subnational_gas_residential': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_domestic.csv'),
        'val_subnational_gas_non_residential': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_non_domestic.csv'),
        'val_nat_elec_data': os.path.join(
            path, '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')}

    return paths

def load_tech_profiles(
        tech_lp,
        paths,
        local_paths,
        plot_tech_lp=True
    ):
    """Load technology specific load profiles

    Arguments
    ----------
    tech_lp : dict
        Load profiles
    paths : dict
        Paths
    local_paths : dict
        Local paths
    plot_tech_lp : bool
        Criteria wheter individual tech lp are
        saved as figure to separte folder

    Returns
    ------
    data : dict
        Data container containing new load profiles
    """
    tech_lp = {}

    # Boiler load profile from Robert Sansom
    tech_lp['rs_lp_heating_boilers_dh'] = read_data.read_load_shapes_tech(
        paths['path_hourly_gas_shape_resid'])

    # CHP load profile from Robert Sansom
    tech_lp['rs_lp_heating_CHP_dh'] = read_data.read_load_shapes_tech(
        paths['lp_all_microCHP_dh'])

    # Heat pump load profile from Love et al. (2017)
    tech_lp['rs_lp_heating_hp_dh'] = read_data.read_load_shapes_tech(
        paths['lp_elec_hp_dh'])

    #tech_lp['rs_shapes_cooling_dh'] = read_data.read_load_shapes_tech(paths['path_shape_rs_cooling']) #Not implemented
    tech_lp['ss_shapes_cooling_dh'] = read_data.read_load_shapes_tech(paths['path_shape_ss_cooling'])

    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater)
    tech_lp['rs_lp_storage_heating_dh'] = read_data.read_load_shapes_tech(
        paths['lp_elec_storage_heating'])
    tech_lp['rs_lp_second_heating_dh'] = read_data.read_load_shapes_tech(
        paths['lp_elec_secondary_heating'])

    # --------------------------------------------
    # Print individualtechnology load profiles of technologies
    # --------------------------------------------
    if plot_tech_lp:

        # Maybe move to result folder in a later step
        path_folder_lp = os.path.join(local_paths['local_path_datafolder'], 'individual_lp')
        basic_functions.create_folder(path_folder_lp)

        # Boiler
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_workday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_holiday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_peakday"))

        # CHP
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_workday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_holiday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_peakday"))

        # HP
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_workday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_holiday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_peakday"))

        # Stroage heating
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_workday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_holiday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_peakday"))

        # Direct electric heating
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_workday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_holiday"))
        fig_lp.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_peakday"))

    return tech_lp

def load_data_profiles(
        paths,
        local_paths,
        model_yeardays,
        model_yeardays_daytype,
    ):
    """Collect load profiles from txt files

    Arguments
    ----------
    paths : dict
        Paths
    local_paths : dict
        Loal Paths
    model_yeardays : int
        Number of modelled yeardays
    model_yeardays_daytype : int
        Daytype of every modelled day
    """
    tech_lp = {}

    # ------------------------------------
    # Technology specific load profiles
    # ------------------------------------
    tech_lp = load_tech_profiles(
        tech_lp,
        paths,
        local_paths,
        plot_tech_lp=False) # Plot individual load profiles

    # Load enduse load profiles
    tech_lp['rs_shapes_dh'], tech_lp['rs_shapes_yd'] = rs_collect_shapes_from_txts(
        local_paths['rs_load_profile_txt'], model_yeardays)

    tech_lp['ss_shapes_dh'], tech_lp['ss_shapes_yd'] = ss_collect_shapes_from_txts(
        local_paths['ss_load_profile_txt'], model_yeardays)

    # -- From Carbon Trust (service sector data) read out enduse specific shapes
    tech_lp['ss_all_tech_shapes_dh'], tech_lp['ss_all_tech_shapes_yd'] = ss_read_shapes_enduse_techs(
        tech_lp['ss_shapes_dh'], tech_lp['ss_shapes_yd'])

    # ------------------------------------------------------------
    # Calculate yh load profiles for individual technologies
    # ------------------------------------------------------------

    # Heat pumps by Love
    tech_lp['rs_profile_hp_y_dh'] = get_shape_every_day(
        tech_lp['rs_lp_heating_hp_dh'], model_yeardays_daytype)

    # Storage heater
    tech_lp['rs_profile_storage_heater_y_dh'] = get_shape_every_day(
        tech_lp['rs_lp_storage_heating_dh'], model_yeardays_daytype)

    # Electric heating
    tech_lp['rs_profile_elec_heater_y_dh'] = get_shape_every_day(
        tech_lp['rs_lp_second_heating_dh'], model_yeardays_daytype)

    # Boilers
    tech_lp['rs_profile_boilers_y_dh'] = get_shape_every_day(
        tech_lp['rs_lp_heating_boilers_dh'], model_yeardays_daytype)

    # Micro CHP
    tech_lp['rs_profile_chp_y_dh'] = get_shape_every_day(
        tech_lp['rs_lp_heating_CHP_dh'], model_yeardays_daytype)

    # Service Cooling tech
    tech_lp['ss_profile_cooling_y_dh'] = get_shape_every_day(
        tech_lp['ss_shapes_cooling_dh'], model_yeardays_daytype)

    return tech_lp

def get_shape_every_day(tech_lp, model_yeardays_daytype):
    """Generate yh shape based on the daytype of
    every day in year. This function iteraes every day
    of the base year and assigns daily profiles depending
    on the daytype for every day

    Arguments
    ---------
    tech_lp : dict
        Technology load profiles
    model_yeardays_daytype : list
        List with the daytype of every modelled day

    Return
    ------
    load_profile_y_dh : dict
        Fuel profiles yh (total sum for a fully ear is 365,
        i.e. the load profile is given for every day)
    """
    # Load profiles for a single day
    lp_holiday = tech_lp['holiday'] / np.sum(tech_lp['holiday'])
    lp_workday = tech_lp['workday'] / np.sum(tech_lp['workday'])

    load_profile_y_dh = np.zeros((365, 24), dtype="float")

    for day_array_nr, day_type in enumerate(model_yeardays_daytype):
        if day_type == 'holiday':
            load_profile_y_dh[day_array_nr] = lp_holiday
        else:
            load_profile_y_dh[day_array_nr] = lp_workday

    return load_profile_y_dh

def  load_weather_stations_df(path_stations):
    """Read Weather stations from file
    """
    out_stations = {}
    stations = pd.read_csv(path_stations)

    for i in stations.index:
        station_id = stations.at[i,'station_id']
        latitude = stations.at[i,'latitude']
        longitude = stations.at[i,'longitude']

        out_stations[station_id] = {
            'latitude' : float(latitude),
            'longitude': float(longitude)}

    return out_stations

def load_weather_stations_csv(path_stations):
    """Read Weather stations from file
    """
    out_stations = {}
    stations = pd.read_csv(path_stations)

    for i in stations.index:
        station_id = stations.at[i, 'station_id']
        latitude = stations.at[i, 'latitude']
        longitude = stations.at[i, 'longitude']

        out_stations[station_id] = {
            'latitude' : float(latitude),
            'longitude': float(longitude)}

    return out_stations

def load_temp_data(
        local_paths,
        sim_yrs,
        weather_realisation,
        path_weather_data,
        same_base_year_weather=False,
        crit_temp_min_max=False
    ):
    """Read in cleaned temperature and weather station data

    Arguments
    ----------
    local_paths : dict
        Local local_paths
    weather_yr_scenario : list
        Years to use temperatures
    same_base_year_weather : bool
        Criteria whether the base year weather is used for full simulation

    Returns
    -------
    weather_stations : dict
        Weather stations
    temp_data : dict
        Temperaturesv
    crit_temp_min_max : dict
        True: Hourly temperature data are provided
        False: min and max temperature are provided

    t_yrs_stations : dict
        Temperatures {sim_yr: {stations:  {t_min: np.array(365), t_max: np.array(365)}}}

    Info
    ----
    PAarquest file http://pandas.pydata.org/pandas-docs/stable/io.html#io-parquet
    """
    print("... loading temperatures", flush=True)

    load_np = False
    load_parquet = True
    load_csv = False

    temp_data_short = defaultdict(dict)
    weather_stations_with_data = defaultdict(dict)

    if crit_temp_min_max:

        # ------------------
        # Read stations
        # ------------------
        path_stations = os.path.join(path_weather_data, "stations_{}.csv".format(weather_realisation))

        weather_stations_with_data = load_weather_stations_csv(path_stations)

        # ------------------
        # Read temperatures
        # ------------------
        if load_np:
            path_temp_data = os.path.join(path_weather_data, "weather_data_{}.npy".format(weather_realisation))
            full_data = np.load(path_temp_data)

            # Convert npy to dataframe
            df_full_data = pd.DataFrame(
                full_data,
                columns=['timestep', 'station_id', 'stiching_name', 'yearday', 't_min', 't_max'])

        if load_parquet:
            path_temp_data = os.path.join(path_weather_data, "weather_data_{}.parquet".format(weather_realisation))
            df_full_data = pd.read_parquet(path_temp_data, engine='pyarrow')
        if load_csv:
            path_temp_data = os.path.join(path_weather_data, "weather_data_{}.csv".format(weather_realisation))
            df_full_data = pd.read_csv(path_temp_data)

        for sim_yr in sim_yrs:

            if same_base_year_weather:
                sim_yr = sim_yrs[0]
            else:
                pass
            print("    ... year: {}".format(sim_yr), flush=True)

            # Select all station values
            df_timestep = df_full_data.loc[df_full_data['timestep'] == sim_yr]

            for station_id in weather_stations_with_data:

                df_timestep_station = df_timestep.loc[df_timestep['station_id'] == station_id]

                # Remove extrated rows to speed up process
                df_timestep = df_timestep.drop(list(df_timestep_station.index))

                t_min = list(df_timestep_station['t_min'].values)
                t_max = list(df_timestep_station['t_max'].values)

                temp_data_short[sim_yr][station_id] = {
                    't_min': np.array(t_min),
                    't_max': np.array(t_max)}

        return dict(weather_stations_with_data), dict(temp_data_short)
    else:
        # Reading in hourly temperature data
        weather_stations = read_weather_stations_raw(
            local_paths['folder_path_weater_stations'])

        for weather_yr_scenario in sim_yrs:
            temp_data = read_weather_data.read_weather_data_script_data(
                local_paths['weather_data'], weather_yr_scenario)

            for station in weather_stations:
                try:
                    _ = temp_data[station]

                    # Remove all non-uk stations
                    if weather_stations[station]['longitude'] > 2 or weather_stations[station]['longitude'] < -8.5:
                        pass
                    else:
                        temp_data_short[weather_yr_scenario][station] = temp_data[station]
                except:
                    logging.debug("no data for weather station " + str(station))

            for station_id in temp_data_short[weather_yr_scenario].keys():
                try:
                    weather_stations_with_data[station_id] = weather_stations[station_id]
                except:
                    del temp_data_short[weather_yr_scenario][station_id]

            logging.info(
                "Info: Number of weather stations: {} weather_yr_scenario: Number of temp data: {}, weather_yr_scenario: {}".format(
                    len(weather_stations_with_data), len(temp_data_short[weather_yr_scenario]), weather_yr_scenario))

        return dict(weather_stations_with_data), dict(temp_data_short)

def load_fuels(paths):
    """Load in ECUK fuel data, enduses and sectors

    Sources:
        Residential:    Table 3.02, Table 3.08
        Service:        Table 5.5a
        Industry:       Table 4.04

    Arguments
    ---------
    paths : dict
        Paths container

    Returns
    -------
    enduses : dict
        Enduses for every submodel
    sectors : dict
        Sectors for every submodel
    fuels : dict
        yearly fuels for every submodel
    enduses_lookup : dict
        Lookup of end uses
    lookup_sector_enduses : dict
        Sector enduse lookup
    """
    submodels_names = lookup_tables.basic_lookups()['submodels_names']
    fueltypes_nr = lookup_tables.basic_lookups()['fueltypes_nr']

    enduses, sectors, fuels = {}, {}, {}
    enduses_lookup = {}

    # -------------------------------
    # submodels_names[0]: Residential SubmodelSubmodel
    # -------------------------------
    rs_fuel_raw, sectors[submodels_names[0]], enduses[submodels_names[0]] = read_data.read_fuel_rs(
        paths['rs_fuel_raw'])

    # -------------------------------
    # submodels_names[1]: Service Submodel
    # -------------------------------
    ss_fuel_raw, sectors[submodels_names[1]], enduses[submodels_names[1]] = read_data.read_fuel_ss(
        paths['ss_fuel_raw'], fueltypes_nr)

    # -------------------------------
    # submodels_names[2]: Industry
    # -------------------------------
    is_fuel_raw, sectors[submodels_names[2]], enduses[submodels_names[2]] = read_data.read_fuel_is(
        paths['is_fuel_raw'], fueltypes_nr)

    # Convert energy input units
    fuels[submodels_names[0]] = conversions.convert_fueltypes_sectors_ktoe_gwh(rs_fuel_raw)
    fuels[submodels_names[1]] = conversions.convert_fueltypes_sectors_ktoe_gwh(ss_fuel_raw)
    fuels[submodels_names[2]] = conversions.convert_fueltypes_sectors_ktoe_gwh(is_fuel_raw)

    # Aggregate fuel across sectors
    fuels['aggr_sector_fuels'] = {}
    for submodel in enduses:
        for enduse in enduses[submodel]:
            fuels['aggr_sector_fuels'][enduse] = sum(fuels[submodel][enduse].values())

    cnt = 0
    for submodel in enduses:
        for enduse in enduses[submodel]:
            enduses_lookup[enduse] = cnt
            cnt += 1

    lookup_sector_enduses = {}
    for submodel_nr, submodel in enumerate(enduses):
        lookup_sector_enduses[submodel_nr] = []
        for enduse in enduses[submodel]:
            enduse_nr = enduses_lookup[enduse]
            lookup_sector_enduses[submodel_nr].append(enduse_nr)

    return enduses, sectors, fuels, enduses_lookup, lookup_sector_enduses

def rs_collect_shapes_from_txts(txt_path, model_yeardays):
    """All pre-processed load shapes are read in from .txt files
    without accessing raw files

    This loads HES files for residential sector

    Arguments
    ----------
    data : dict
        Data
    txt_path : float
        Path to folder with stored txt files

    Return
    ------
    rs_shapes_dh : dict
        Residential yh shapes
    rs_shapes_yd : dict
        Residential yd shapes
    """
    rs_shapes_dh = {}
    rs_shapes_yd = {}

    # Iterate folders and get all enduse
    all_csv_in_folder = os.listdir(txt_path)

    enduses = set([])
    for file_name in all_csv_in_folder:
        enduse = file_name.split("__")[0]
        enduses.add(enduse)

    # Read load shapes from txt files for enduses
    for enduse in enduses:
        shape_peak_dh = read_data.read_np_array_from_txt(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_peak_dh') + str('.txt')))
        shape_non_peak_y_dh = read_data.read_np_array_from_txt(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
        shape_non_peak_yd = read_data.read_np_array_from_txt(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        # Select only modelled days (nr_of_days, 24)
        shape_non_peak_y_dh_selection = shape_non_peak_y_dh[model_yeardays]
        shape_non_peak_yd_selection = shape_non_peak_yd[model_yeardays]

        rs_shapes_dh[enduse] = {
            'shape_peak_dh': shape_peak_dh,
            'shape_non_peak_y_dh': shape_non_peak_y_dh_selection}

        rs_shapes_yd[enduse] = {
            'shape_non_peak_yd': shape_non_peak_yd_selection}

    return rs_shapes_dh, rs_shapes_yd

def ss_collect_shapes_from_txts(txt_path, model_yeardays):
    """Collect service shapes from txt files for every setor and enduse

    Arguments
    ----------
    txt_path : string
        Path to txt shapes files
    model_yeardays : array
        Modelled yeardays

    Return
    ------
    data : dict
        Data
    """
    # Iterate folders and get all sectors and enduse from file names
    all_csv_in_folder = os.listdir(txt_path)

    enduses = set([])
    sectors = set([])
    for file_name in all_csv_in_folder:
        sector = file_name.split("__")[0]
        enduse = file_name.split("__")[1]
        enduses.add(enduse)
        sectors.add(sector)

    ss_shapes_dh = defaultdict(dict)
    ss_shapes_yd = defaultdict(dict)

    # Read load shapes from txt files for enduses
    for enduse in enduses:
        for sector in sectors:
            joint_string_name = str(sector) + "__" + str(enduse)

            shape_peak_dh = read_data.read_np_array_from_txt(
                os.path.join(
                    txt_path,
                    str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_y_dh = read_data.read_np_array_from_txt(
                os.path.join(
                    txt_path,
                    str(joint_string_name) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
            shape_non_peak_yd = read_data.read_np_array_from_txt(
                os.path.join(
                    txt_path,
                    str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            # -----------------------------------------------------------
            # Select only modelled days (nr_of_days, 24)
            # -----------------------------------------------------------
            shape_non_peak_y_dh_selection = shape_non_peak_y_dh[model_yeardays]
            shape_non_peak_yd_selection = shape_non_peak_yd[model_yeardays]

            ss_shapes_dh[enduse][sector] = {
                'shape_peak_dh': shape_peak_dh,
                'shape_non_peak_y_dh': shape_non_peak_y_dh_selection}

            ss_shapes_yd[enduse][sector] = {
                'shape_non_peak_yd': shape_non_peak_yd_selection}

    return dict(ss_shapes_dh), dict(ss_shapes_yd)

def create_enduse_dict(data, rs_fuel_raw_data_enduses):
    """Create dictionary with all residential enduses and store in data dict

    For residential model

    Arguments
    ----------
    data : dict
        Main data dictionary

    rs_fuel_raw_data_enduses : dict
        Raw fuel data from external enduses (e.g. other models)

    Returns
    -------
    enduses : list
        Ditionary with residential enduses
    """
    enduses = []
    for ext_enduse in data['external_enduses_resid']:
        enduses.append(ext_enduse)

    for enduse in rs_fuel_raw_data_enduses:
        enduses.append(enduse)

    return enduses

def ss_read_shapes_enduse_techs(ss_shapes_dh, ss_shapes_yd):
    """Iterate carbon trust dataset and read out shapes for enduses.

    Arguments
    ----------
    ss_shapes_yd : dict
        Data

    Returns
    -------

    Read out enduse shapes to assign fuel shape for specific technologies
    in service sector. Because no specific shape is provided for service sector,
    the overall enduse shape is used for all technologies

    Note
    ----
    The first setor is selected and all shapes of the enduses of this
    sector read out. Because all enduses exist for each sector,
    it does not matter from which sector the shapes are talen from
    """
    ss_all_tech_shapes_dh = {}
    ss_all_tech_shapes_yd = {}

    for enduse in ss_shapes_yd:
        for sector in ss_shapes_yd[enduse]:
            ss_all_tech_shapes_dh[enduse] = ss_shapes_dh[enduse][sector]
            ss_all_tech_shapes_yd[enduse] = ss_shapes_yd[enduse][sector]
            break #only iterate first sector as all enduses are the same in all sectors

    return ss_all_tech_shapes_dh, ss_all_tech_shapes_yd

def read_scenario_data(path_to_csv):
    """
    """
    data = {}

    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows) # Skip first row
        for row in rows:

            region = str(row[read_data.get_position(headings, 'region')])
            year = int(float(row[read_data.get_position(headings, 'timestep')]))
            value = float(row[read_data.get_position(headings, 'value')])

            try:
                data[year][region] = value
            except KeyError:
                data[year] = {}
                data[year][region] = value

    return data

def read_scenario_data_gva(path_to_csv, all_dummy_data=False):
    """Function to read in GVA locally

    IF no value, provide with dummy value "1"

    if all_dummy_data == True, then all is dummy data and
    constant over time
    """
    out_dict = {}

    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows)
        for row in rows:

            # --------------
            # All dummy data
            # --------------
            if all_dummy_data:
                region = str(row[read_data.get_position(headings, 'region')])
                for year_dummy in range(2015, 2051):

                    for sector_dummy in range(1, 47):
                        dummy_sector_value = 1

                        try:
                            out_dict[year_dummy][region][sector_dummy] = dummy_sector_value
                        except KeyError:
                            out_dict[year_dummy] = defaultdict(dict)
                            out_dict[year_dummy][region][sector_dummy] = dummy_sector_value

            else:
                if row[read_data.get_position(headings, 'timestep')] == '': #No data provided
                    region = str(row[read_data.get_position(headings, 'region')])
                    for year_dummy in range(2015, 2051):
                        for sector_dummy in range(1, 47):
                            dummy_sector_value = 1
                            out_dict[year_dummy][region][sector_dummy] = dummy_sector_value
                else:
                    region = str(row[read_data.get_position(headings, 'region')])
                    year = int(float(row[read_data.get_position(headings, 'timestep')]))
                    value = float(row[read_data.get_position(headings, 'value')])
                    economic_sector__gor = float(row[read_data.get_position(headings, 'economic_sector__gor')])
                try:
                    out_dict[year][region][economic_sector__gor] = value
                except KeyError:
                    out_dict[year] = defaultdict(dict)
                    out_dict[year][region][economic_sector__gor] = value

    # Convert to regular dict
    for key, value in out_dict.items():
        out_dict[key] = dict(value)

    return out_dict

def read_employment_stats(path_to_csv):
    """Read in employment statistics per LAD.

    This dataset provides 2011 estimates that classify usual
    residents aged 16 to 74 in employment the week before
    the census in United Kingdom by industry.

    Outputs
    -------
    data : dict
        geocode, Nr_of_category

    Infos
    ------
    Industry: All categories: Industry
    Industry: A Agriculture, forestry and fishing
    Industry: B Mining and quarrying
    Industry: C Manufacturing
    Industry: C10-12 Manufacturing: Food, beverages and tobacco
    Industry: C13-15 Manufacturing: Textiles, wearing apparel and leather and related products
    Industry: C16,17 Manufacturing: Wood, paper and paper products
    Industry: C19-22 Manufacturing: Chemicals, chemical products, rubber and plastic
    Industry: C23-25 Manufacturing: Low tech
    Industry: C26-30 Manufacturing: High tech
    Industry: C18, 31, 32 Manufacturing: Other
    Industry: D Electricity, gas, steam and air conditioning supply
    Industry: E Water supply, sewerage, waste management and remediation activities
    Industry: F Construction
    Industry: G Wholesale and retail trade; repair of motor vehicles and motor cycles
    Industry: H Transport and storage
    Industry: I Accommodation and food service activities
    Industry: J Information and communication
    Industry: K Financial and insurance activities
    Industry: L Real estate activities
    Industry: M Professional, scientific and technical activities
    Industry: N Administrative and support service activities
    Industry: O Public administration and defence; compulsory social security
    Industry: P Education
    Industry: Q Human health and social work activities
    Industry: R,S Arts, entertainment and recreation; other service activities
    Industry: T Activities of households as employers; undifferentiated goods - and services - producing activities of households for own use
    Industry: U Activities of extraterritorial organisations and bodies
    """
    data = defaultdict(dict)

    with open(path_to_csv, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        headings = next(lines) # Skip first row

        for line in lines:
            geocode = str.strip(line[2])

            # Iterate fields and copy values
            for counter, heading in enumerate(headings[4:], 4):
                heading_split = heading.split(":")
                category_unclean = str.strip(heading_split[1])
                category_full_name = str.strip(category_unclean.split(" ")[0]).replace(" ", "_")
                category_nr = category_full_name.split("_")[0]

                data[geocode][category_nr] = float(line[counter])

    logging.info("... loaded employment statistics")
    return dict(data)
