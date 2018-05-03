"""Loads all necessary data
"""
import os
import csv
import logging
import configparser
import ast
from collections import defaultdict
import numpy as np
from energy_demand.read_write import read_data, read_weather_data
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions

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

    reg_nrs = int(config['SIM_PARAM']['reg_nrs'])
    regions = ast.literal_eval(config['REGIONS']['regions'])

    assumptions = {}
    assumptions['model_yearhours_nrs'] = int(config['SIM_PARAM']['model_yearhours_nrs'])
    assumptions['model_yeardays_nrs'] = int(config['SIM_PARAM']['model_yeardays_nrs'])
    assumptions['base_yr'] = int(config['SIM_PARAM']['base_yr'])
    assumptions['simulated_yrs'] = ast.literal_eval(config['SIM_PARAM']['simulated_yrs'])

    # -----------------
    # Other information
    # -----------------
    enduses = {}
    enduses['rs_enduses'] = ast.literal_eval(config['ENDUSES']['rs_enduses']) #convert string lists to list
    enduses['ss_enduses'] = ast.literal_eval(config['ENDUSES']['ss_enduses'])
    enduses['is_enduses'] = ast.literal_eval(config['ENDUSES']['is_enduses'])

    return enduses, assumptions, reg_nrs, regions

def read_national_real_elec_data(path_to_csv):
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

    Info
    -----
    Source: https://www.gov.uk/government/statistical-data-sets
    /regional-and-local-authority-electricity-
    consumption-statistics-2005-to-2011
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows) # Skip first row

        for row in rows:
            geocode = str.strip(row[2])                 # LA Code
            tot_consumption_unclean = row[3].strip()    # Total consumption
            national_fuel_data[geocode] = float(tot_consumption_unclean.replace(",", ""))

    return national_fuel_data

def read_national_real_gas_data(path_to_csv):
    """Read in national consumption from csv file

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
        -   Source: https://www.gov.uk/government/statistical-data-sets
            /gas-sales-and-numbers-of-customers-by-region-and-local-authority

        -   units are provided as GWh

        -   If for a LAD no information is provided,
            the energy demand is set to zero.
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows) # Skip first row

        for row in rows:
            geocode = str.strip(row[2])                 # 'LA Code'
            tot_consumption_unclean = row[3].strip()    # 'Total consumption'

            if tot_consumption_unclean == '-':
                total_consumption = 0 # No entry provided
            else:
                total_consumption = float(tot_consumption_unclean.replace(",", ""))

            national_fuel_data[geocode] = total_consumption

    return national_fuel_data

def floor_area_virtual_dw(
        regions,
        all_sectors,
        local_paths,
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
    all_sectors : dict
        All sectors
    local_paths : dict
        Paths
    base_yr : float
        Base year
    f_mixed_floorarea : float
        PArameter to redistributed mixed enduse

    Returns
    -------
    rs_floorarea : dict
        Residential floor area
    ss_floorarea : dict
        Service sector floor area
    """
    # --------------------------------------------------
    # Floor area for residential buildings for base year
    # --------------------------------------------------
    resid_footprint, non_res_flootprint, service_building_count = read_data.read_floor_area_virtual_stock(
        local_paths['path_floor_area_virtual_stock_by'],
        f_mixed_floorarea=f_mixed_floorarea)

    # -----------------
    # Calculate average floor area per person
    # of existing datasets. This is done to replace the missing
    # floor area data of LADs with estimated floor areas
    # -----------------
    rs_floorarea = defaultdict(dict)
    for region in regions:
        try:
            rs_floorarea[base_yr][region] = resid_footprint[region]
        except:
            logging.warning(
                "No virtual residential floor area for region %s ", region)

            #estimated_floor_area = average_pop
            rs_floorarea[base_yr][region] = 1234567899999999

    # --------------------------------------------------
    # Floor area for service sector buildings
    # TODO SO FAR THE SAME FOR EVERY SECTOR
    # --------------------------------------------------
    ss_floorarea_sector_by = {}
    ss_floorarea_sector_by[base_yr] = defaultdict(dict)
    for region in regions:
        for sector in all_sectors:
            try:
                ss_floorarea_sector_by[base_yr][region][sector] = non_res_flootprint[region]
            except:
                logging.warning("No virtual service floor area for region %s", region)
                ss_floorarea_sector_by[base_yr][region][sector] = 1234567899999999

    return dict(rs_floorarea), dict(ss_floorarea_sector_by), service_building_count

def load_local_paths(path):
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
        'local_path_datafolder':
            path,
        'folder_raw_carbon_trust': os.path.join(
            path, '_raw_data', "G_Carbon_Trust_advanced_metering_trial"),
        'folder_path_weater_data': os.path.join(
            path, '_raw_data', 'H-Met_office_weather_data', 'midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(
            path, '_raw_data', 'H-Met_office_weather_data', 'excel_list_station_details.csv'),
        'path_floor_area_virtual_stock_by': os.path.join(
            path, '_raw_data', 'K-floor_area', 'floor_area_LAD_latest.csv'),
        'path_assumptions_db': os.path.join(
            path, '_processed_data', 'assumptions_from_db'),
        'data_processed': os.path.join(
            path, '_processed_data'),
        'lad_shapefile': os.path.join(
            path, '_raw_data', 'C_LAD_geography', 'same_as_pop_scenario', 'lad_2016_uk_simplified.shp'),
        'path_post_installation_data': os.path.join(
            path, '_processed_data', '_post_installation_data'),
        'data_processed_disaggregated': os.path.join(
            path, '_processed_data', '_post_installation_data', 'disaggregated'),
        'path_sigmoid_data': os.path.join(
            path, '_processed_data', 'sigmoid_data'),
        'dir_changed_weather_station_data': os.path.join(
            path, '_processed_data', '_post_installation_data', 'weather_station_data'),
        'changed_weather_station_data': os.path.join(
            path, '_processed_data', '_post_installation_data', 'weather_station_data', 'weather_stations.csv'),
        'dir_raw_weather_data': os.path.join(
            path, '_processed_data', '_post_installation_data', 'raw_weather_data'),
        'load_profiles': os.path.join(
            path, '_processed_data', '_post_installation_data', 'load_profiles'),
        'dir_disaggregated': os.path.join(
            path, '_processed_data', '_post_installation_data', 'disaggregated'),
        'rs_load_profile_txt': os.path.join(
            path, '_processed_data', '_post_installation_data', 'load_profiles', 'rs_submodel'),
        'ss_load_profile_txt': os.path.join(
            path, '_processed_data', '_post_installation_data', 'load_profiles', 'ss_submodel'),
        'dir_services': os.path.join(
            path, '_processed_data', 'services'),

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

def load_result_paths(path):
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
            path, 'spatial_results')}

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
            path, '08-technologies', 'technology_definition.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(
            path, '07-switches', 'rs_switches_fuel.csv'),
        'ss_path_fuel_switches': os.path.join(
            path, '07-switches', 'ss_switches_fuel.csv'),
        'is_path_fuel_switches': os.path.join(
            path, '07-switches', 'is_switches_fuel.csv'),

        # Path to service switches
        'rs_path_service_switch': os.path.join(
            path, '07-switches', 'rs_switches_service.csv'),
        'ss_path_service_switch': os.path.join(
            path, '07-switches', 'ss_switches_service.csv'),
        'is_path_industry_switch': os.path.join(
            path, '07-switches', 'is_switches_service.csv'),

        # Path to capacity installations
        'rs_path_capacity_installation': os.path.join(
            path, '07-switches', 'rs_capacity_installations.csv'),
        'ss_path_capacity_installation': os.path.join(
            path, '07-switches', 'ss_capacity_installations.csv'),
        'is_path_capacity_installation': os.path.join(
            path, '07-switches', 'is_capacity_installations.csv'),

        # Paths to fuel raw data
        'rs_fuel_raw': os.path.join(
            path, '06-fuels', 'rs_fuel.csv'),
        'ss_fuel_raw': os.path.join(
            path, '06-fuels', 'ss_fuel.csv'),
        'is_fuel_raw': os.path.join(
            path, '06-fuels', 'is_fuel.csv'),

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
            #path, '03-load_profiles', 'rs_submodel', 'lp_elec_storage_heating_HES.csv'), # Worst
            #path, '03-load_profiles', 'rs_submodel', 'lp_elec_storage_heating_Bossmann.csv'), # Better TRY TODO
            path, '03-load_profiles', 'rs_submodel', 'lp_elec_storage_heating_HESReport.csv'), # Best

            # Combination of HES Report and Bossmann (50%, 50%)
            #path, '03-load_profiles', 'rs_submodel', 'lp_elec_storage_heating_combined.csv'), # Best
    
        'lp_elec_secondary_heating': os.path.join(
            # different per daytype
            path, '03-load_profiles', 'rs_submodel', 'lp_elec_secondary_heating_HES.csv'),

            # All the same
            #path, '03-load_profiles', 'rs_submodel', 'lp_elec_secondary_heating_HES_all_same.csv'),

        # Census data
        'path_employment_statistics': os.path.join(
            path, '04-census_data', 'LAD_census_data.csv'),

        # Validation datasets
        'path_val_subnational_elec': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec.csv'),
        'path_val_subnational_elec_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_domestic.csv'),
        'path_val_subnational_elec_non_residential': os.path.join(
            path, '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_non_domestic.csv'),
        'path_val_subnational_gas': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas.csv'),
        'path_val_subnational_gas_residential': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_domestic.csv'),
        'path_val_subnational_gas_non_residential': os.path.join(
            path, '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_non_domestic.csv'),
        'path_val_nat_elec_data': os.path.join(
            path, '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')}

    return paths

def load_tech_profiles(tech_lp, paths, local_paths, plot_tech_lp=True):
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
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_workday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_holiday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_boilers_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heating_boilers_peakday"))

        # CHP
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_workday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_holiday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_hp_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heatpump_peakday"))

        # HP
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_workday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_holiday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_heating_CHP_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("heating_CHP_peakday"))

        # Stroage heating
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_workday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_holiday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_storage_heating_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("storage_heating_peakday"))

        # Direct electric heating
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['workday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_workday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['holiday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_holiday"))
        plotting_results.plot_lp_dh(
            tech_lp['rs_lp_second_heating_dh']['peakday'] * 100,
            path_folder_lp,
            "{}".format("secondary_heating_peakday"))

    return tech_lp

def load_data_profiles(
        paths,
        local_paths,
        model_yeardays,
        model_yeardays_daytype,
        plot_tech_lp
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
    plot_tech_lp : bool
        Criteria wheter to plot out individual load profiles of techs
    """
    tech_lp = {}

    # ------------------------------------
    # Technology specific load profiles
    # ------------------------------------
    tech_lp = load_tech_profiles(
        tech_lp,
        paths,
        local_paths,
        plot_tech_lp)

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

    load_profile_y_dh = np.zeros((365, 24), dtype=float)

    for day_array_nr, day_type in enumerate(model_yeardays_daytype):
        if day_type == 'holiday':
            load_profile_y_dh[day_array_nr] = lp_holiday
        else:
            load_profile_y_dh[day_array_nr] = lp_workday

    return load_profile_y_dh

def load_temp_data(paths):
    """Read in cleaned temperature and weather station data

    Arguments
    ----------
    paths : dict
        Local paths

    Returns
    -------
    weather_stations : dict
        Weather stations
    temp_data : dict
        Temperatures
    """
    weather_stations = read_weather_data.read_weather_station_script_data(
        paths['changed_weather_station_data'])

    temp_data = read_weather_data.read_weather_data_script_data(
        paths['dir_raw_weather_data'])

    return weather_stations, temp_data

def load_fuels(paths, lookups):
    """Load in ECUK fuel data, enduses and sectors

    Sources:
        Residential:    Table 3.02, Table 3.08
        Service:        Table 5.5a
        Industry:       Table 4.04

    Arguments
    ---------
    paths : dict
        Paths container
    lookups : dict
        Lookups

    Returns
    -------
    enduses : dict
        Enduses for every submodel
    sectors : dict
        Sectors for every submodel
    fuels : dict
        yearly fuels for every submodel
    """
    enduses = {}
    sectors = {}
    fuels = {}

    # Residential Sector
    rs_fuel_raw_data_enduses, enduses['rs_enduses'] = read_data.read_fuel_rs(
        paths['rs_fuel_raw'])

    # Service Sector
    ss_fuel_raw, sectors['ss_sectors'], enduses['ss_enduses'] = read_data.read_fuel_ss(
        paths['ss_fuel_raw'],
        lookups['fueltypes_nr'])

    # Industry fuel
    is_fuel_raw, sectors['is_sectors'], enduses['is_enduses'] = read_data.read_fuel_is(
        paths['is_fuel_raw'], lookups['fueltypes_nr'], lookups['fueltypes'])

    # Iterate enduses per sudModel and flatten list
    enduses['all_enduses'] = []
    for enduse in enduses.values():
        enduses['all_enduses'] += enduse

    # Convert units
    fuels['rs_fuel_raw'] = conversions.convert_fueltypes_ktoe_gwh(
        rs_fuel_raw_data_enduses)
    fuels['ss_fuel_raw'] = conversions.convert_fueltypes_sectors_ktoe_gwh(
        ss_fuel_raw)
    fuels['is_fuel_raw'] = conversions.convert_fueltypes_sectors_ktoe_gwh(
        is_fuel_raw)

    sectors['all_sectors'] = [
        'community_arts_leisure',
        'education',
        'emergency_services',
        'health',
        'hospitality',
        'military',
        'offices',
        'retail',
        'storage',
        'other']

    return enduses, sectors, fuels

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
        shape_peak_yd_factor = float(read_data.read_np_array_from_txt(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_peak_yd_factor') + str('.txt'))))
        shape_non_peak_yd = read_data.read_np_array_from_txt(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        # Select only modelled days (nr_of_days, 24)
        shape_non_peak_y_dh_selection = shape_non_peak_y_dh[[model_yeardays]]
        shape_non_peak_yd_selection = shape_non_peak_yd[[model_yeardays]]

        rs_shapes_dh[enduse] = {
            'shape_peak_dh': shape_peak_dh,
            'shape_non_peak_y_dh': shape_non_peak_y_dh_selection}

        rs_shapes_yd[enduse] = {
            'shape_peak_yd_factor': shape_peak_yd_factor,
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
            shape_peak_yd_factor = float(read_data.read_np_array_from_txt(
                os.path.join(
                    txt_path,
                    str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt'))))
            shape_non_peak_yd = read_data.read_np_array_from_txt(
                os.path.join(
                    txt_path,
                    str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            # -----------------------------------------------------------
            # Select only modelled days (nr_of_days, 24)
            # -----------------------------------------------------------
            shape_non_peak_y_dh_selection = shape_non_peak_y_dh[[model_yeardays]]
            shape_non_peak_yd_selection = shape_non_peak_yd[[model_yeardays]]

            ss_shapes_dh[enduse][sector] = {
                'shape_peak_dh': shape_peak_dh,
                'shape_non_peak_y_dh': shape_non_peak_y_dh_selection}

            ss_shapes_yd[enduse][sector] = {
                'shape_peak_yd_factor': shape_peak_yd_factor,
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

def load_LAC_geocodes_info(path_to_csv):
    """FIGURE FUNCTION Import local area unit district codes

    Read csv file and create dictionary with 'geo_code'

    Note
    -----
    - no LAD without population must be included
    - PROVIDED IN UNIT?? (KWH I guess)
    """
    with open(path_to_csv, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        headings = next(rows) # Skip first row
        data = {}

        for row in rows:
            values_line = {}
            for number, value in enumerate(row[1:], 1):
                try:
                    values_line[headings[number]] = float(value)
                except ValueError:
                    values_line[headings[number]] = str(value)

            # Add entry with geo_code
            data[row[0]] = values_line

    return data

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
