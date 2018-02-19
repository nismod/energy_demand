"""Loads all necessary data
"""
import os
import csv
import logging
import numpy as np
import configparser
import ast
from collections import defaultdict
from datetime import date
from energy_demand.read_write import read_data, read_weather_data
from energy_demand.basic import conversions
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions

def load_basic_lookups():
    """Definition of basic lookups or other related information

    Return
    ------
    lookups : dict
        Lookup information and other very basic properties
    """
    lookups = {}

    lookups['dwtype'] = {
        0: 'detached',
        1: 'semi_detached',
        2: 'terraced',
        3: 'flat',
        4: 'bungalow'}

    lookups['fueltypes'] = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'biomass': 4,
        'hydrogen': 5,
        'heat': 6}

    lookups['fueltypes_nr'] = int(len(lookups['fueltypes']))

    return lookups

def load_sim_param_ini(path):
    """Load simulation parameter run information

    Arguments
    ---------
    path : str
        Path to `ini` file

    Returns
    -------
    sim_param : dict
        Simulation parameters
    enduses : dict
        Enduses
    assumptions : dict
        Assumptions
    reg_nrs : dict
        Number of regions
    lu_reg : dict
        Regions
    """
    config = configparser.ConfigParser()

    config.read(os.path.join(path, 'model_run_sim_param.ini'))

    reg_nrs = int(config['SIM_PARAM']['reg_nrs'])
    lu_reg = ast.literal_eval(config['REGIONS']['lu_reg'])
    sim_param = {}
    sim_param['base_yr'] = int(config['SIM_PARAM']['base_yr'])
    sim_param['simulated_yrs'] = ast.literal_eval(config['SIM_PARAM']['simulated_yrs'])

    assumptions = {}
    assumptions['model_yearhours_nrs'] = int(config['SIM_PARAM']['model_yearhours_nrs'])
    assumptions['model_yeardays_nrs'] = int(config['SIM_PARAM']['model_yeardays_nrs'])

    # -----------------
    # Other information
    # -----------------
    enduses = {}
    enduses['rs_all_enduses'] = ast.literal_eval(config['ENDUSES']['rs_all_enduses']) #convert string lists to list
    enduses['ss_all_enduses'] = ast.literal_eval(config['ENDUSES']['ss_all_enduses'])
    enduses['is_all_enduses'] = ast.literal_eval(config['ENDUSES']['is_all_enduses'])

    return sim_param, enduses, assumptions, reg_nrs, lu_reg

def read_national_real_elec_data(path_to_csv):
    """Read in national consumption from csv file. The unit
    in the original csv is in GWh per region per year.
    TODO: UPDATE VALUES
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
    Source: https://www.gov.uk/government/statistical-data-sets/regional-and-local-authority-electricity-consumption-statistics-2005-to-2011
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            geocode = str.strip(row[2])
            tot_consumption_unclean = row[7].strip()
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
    TODO: UNIT GWh?
    Info
    -----
    Source: https://www.gov.uk/government/statistical-data-sets
    /gas-sales-and-numbers-of-customers-by-region-and-local-authority

    If for a LAD no information is provided,
    the energy demand is set to zero.
    """
    national_fuel_data = {}
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            geocode = str.strip(row[3])
            tot_consumption_unclean = row[10].strip()

            if tot_consumption_unclean == '-':
                total_consumption = 0 # No entry provided
            else:
                total_consumption = float(tot_consumption_unclean.replace(",", ""))

            national_fuel_data[geocode] = total_consumption

    return national_fuel_data

def virtual_building_datasets(lu_reg, all_sectors, local_paths):
    """Load necessary data for virtual building stock
    in case the link to the building stock model in
    Newcastle is not used

    Arguments
    ---------
    lu_reg : dict
        Regions
    all_sectors : dict
        All sectors

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
    resid_footprint, non_res_flootprint = read_data.read_floor_area_virtual_stock(
        local_paths['path_floor_area_virtual_stock_by'])

    rs_floorarea = defaultdict(dict)
    for year in range(2015, 2101):
        for reg_geocode in lu_reg:
            try:
                rs_floorarea[year][reg_geocode] = resid_footprint[reg_geocode]
            except:
                #logging.warning("No virtual residential floor area for region %s %s", reg_geocode, year)
                rs_floorarea[year][reg_geocode] = 1

    # --------------------------------------------------
    # Floor area for service sector buildings
    # --------------------------------------------------
    # No sector specific floorarea
    ss_floorarea_sector_by = {}
    for year in range(2015, 2101):
        ss_floorarea_sector_by[year] = defaultdict(dict)
        for reg_geocode in lu_reg:
            for sector in all_sectors:
                try:
                    ss_floorarea_sector_by[year][reg_geocode][sector] = non_res_flootprint[reg_geocode]
                except:
                    #logging.warning("No virtual service floor area for region %s %s", reg_geocode, year)
                    ss_floorarea_sector_by[year][reg_geocode][sector] = 1

    '''
    ss_floorarea_sector_by = {}
    for year in range(2015, 2101):
        ss_floorarea_sector_by[year] = defaultdict(dict)
        for reg_geocode in lu_reg:
            for sector in all_sectors:
                ss_floorarea_sector_by[year][reg_geocode][sector] = 10000
    '''
    ss_floorarea = dict(ss_floorarea_sector_by)

    return dict(rs_floorarea), dict(ss_floorarea)

def load_local_paths(path):
    """Create all local paths

    Argument
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
        'path_val_nat_elec_data': os.path.join(
            path, '_raw_data', 'D-validation', '03_national_elec_demand_2015', 'elec_demand_2015.csv'),
        'path_val_subnational_elec': os.path.join(
            path, '_raw_data', 'D-validation', '01_subnational_elec_demand', 'data_2015_elec.csv'),
        'path_val_subnational_gas': os.path.join(
            path, '_raw_data', 'D-validation', '02_subnational_gas_demand', 'data_2015_gas.csv'),
        'path_floor_area_virtual_stock_by': os.path.join(
            path, '_raw_data', 'K-floor_area', 'floor_area_by.csv'),
        'path_assumptions_db': os.path.join(
            path, '_processed_data', 'assumptions_from_db'),
        'data_processed': os.path.join(
            path, '_processed_data'),
        'data_results': os.path.join(
            path, '_result_data'),
        'data_results_model_run_pop': os.path.join(
            path, '_result_data', 'model_run_pop'),
        'lad_shapefile': os.path.join(
            path, '_raw_data', 'C_LAD_geography', 'lad_2016.shp'),
        'path_post_installation_data': os.path.join(
            path, '_processed_data', '_post_installation_data'),
        'data_processed_disaggregated': os.path.join(
            path, '_processed_data', '_post_installation_data', 'disaggregated'),
        'path_sigmoid_data': os.path.join(
            path, '_processed_data', 'sigmoid_data'),
        'data_results_model_runs': os.path.join(
            path, '_result_data', 'model_run_results_txt'),
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
        'data_results_PDF': os.path.join(
            path, '_result_data', 'PDF_results'),
        'data_results_validation': os.path.join(
            path, '_result_data', 'PDF_validation'),
        'model_run_pop': os.path.join(
            path, '_result_data', 'model_run_pop'),
        'data_results_shapefiles': os.path.join(
            path, '_result_data', 'result_shapefiles')}

    return paths

def load_paths(path):
    """Load all paths

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

        # Path for dwelling stock assumptions
        'path_hourly_gas_shape_resid': os.path.join(
            path, 'config_data', 'submodel_residential', 'lp_gas_boiler_dh_SANSOM.csv'),

        # Path to all technologies
        'path_technologies': os.path.join(
            path, 'config_data', 'technology_definition.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(
            path, 'config_data', 'submodel_residential', 'switches_fuel.csv'),
        'ss_path_fuel_switches': os.path.join(
            path, 'config_data', 'submodel_service', 'switches_fuel.csv'),
        'is_path_fuel_switches': os.path.join(
            path, 'config_data', 'submodel_industry', 'switches_fuel.csv'),

        # Path to service switches
        'rs_path_service_switch': os.path.join(
            path, 'config_data', 'submodel_residential', 'switches_service.csv'),
        'ss_path_service_switch': os.path.join(
            path, 'config_data', 'submodel_service', 'switches_service.csv'),
        'is_path_industry_switch': os.path.join(
            path, 'config_data', 'submodel_industry', 'switches_industry.csv'),

        # Path to capacity installations
        'rs_path_capacity_installation': os.path.join(
            path, 'config_data', 'submodel_residential', 'capacity_installations.csv'),
        'ss_path_capacity_installation': os.path.join(
            path, 'config_data', 'submodel_service', 'capacity_installations.csv'),
        'is_path_capacity_installation': os.path.join(
            path, 'config_data', 'submodel_industry', 'capacity_installations.csv'),

        # Paths to fuel raw data
        'rs_fuel_raw_data_enduses': os.path.join(
            path, 'config_data', 'submodel_residential', 'rs_fuel.csv'),
        'ss_fuel_raw_data_enduses': os.path.join(
            path, 'config_data', 'submodel_service', 'ss_fuel.csv'),
        'is_fuel_raw_data_enduses': os.path.join(
            path, 'config_data', 'submodel_industry', 'is_fuel.csv'),

        # Load profiles
        'lp_rs': os.path.join(
            path, 'config_data', 'rs_submodel', 'HES_lp.csv'),

        # Technologies load shapes
        'lp_elec_hp_dh': os.path.join(
            path, 'config_data', 'submodel_residential', 'lp_elec_hp_dh_LOVE.csv'),
        'lp_all_microCHP_dh': os.path.join(
            path, 'config_data', 'submodel_residential', 'lp_all_microCHP_dh_SANSOM.csv'),
        'path_shape_rs_cooling': os.path.join(
            path, 'config_data', 'submodel_residential', 'shape_residential_cooling.csv'),
        'path_shape_ss_cooling': os.path.join(
            path, 'config_data', 'ss_submodel', 'shape_service_cooling.csv'),
        'lp_elec_storage_heating': os.path.join(
            #path, 'config_data', 'submodel_residential', 'lp_elec_storage_heating_HES.csv'), # Worst
            #path, 'config_data', 'submodel_residential', 'lp_elec_storage_heating_Bossmann.csv'), # Better
            path, 'config_data', 'submodel_residential', 'lp_elec_storage_heating_HESReport.csv'), # Best
        'lp_elec_secondary_heating': os.path.join(
            path, 'config_data', 'submodel_residential', 'lp_elec_secondary_heating_HES.csv'),

        # Census data
        'path_employment_statistics': os.path.join(
            path, 'config_data', '04-census_data', 'LAD_census_data.csv'),

        'yaml_parameters': os.path.join(path, 'yaml_parameters.yml'),
        'yaml_parameters_default': os.path.join(path, 'yaml_parameters_default.yml'),
        'yaml_parameters_keynames_constrained': os.path.join(path, 'yaml_parameters_keynames_constrained.yml'),
        'yaml_parameters_keynames_unconstrained': os.path.join(path, 'yaml_parameters_keynames_unconstrained.yml'),
        'yaml_parameters_scenario': os.path.join(path, 'yaml_parameters_scenario.yml')
        }

    return paths

def load_tech_profiles(tech_lp, paths, local_paths, plot_tech_lp=False):
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

def load_data_profiles(paths, local_paths, model_yeardays, model_yeardays_daytype, plot_tech_lp):
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
    logging.debug("... read in load shapes from txt files")

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
        'rs_lp_heating_hp_dh', tech_lp, model_yeardays_daytype)

    # Storage heater
    tech_lp['rs_profile_storage_heater_y_dh'] = get_shape_every_day(
        'rs_lp_storage_heating_dh', tech_lp, model_yeardays_daytype)

    # Electric heating
    tech_lp['rs_profile_elec_heater_y_dh'] = get_shape_every_day(
        'rs_lp_second_heating_dh', tech_lp, model_yeardays_daytype)

    # Boilers
    tech_lp['rs_profile_boilers_y_dh'] = get_shape_every_day(
        'rs_lp_heating_boilers_dh', tech_lp, model_yeardays_daytype)

    # Micro CHP
    tech_lp['rs_profile_chp_y_dh'] = get_shape_every_day(
        'rs_lp_heating_CHP_dh', tech_lp, model_yeardays_daytype)

    # Service Cooling tech
    tech_lp['ss_profile_cooling_y_dh'] = get_shape_every_day(
        'ss_shapes_cooling_dh', tech_lp, model_yeardays_daytype)

    return tech_lp

def get_shape_every_day(tech, tech_lp, model_yeardays_daytype):
    """Generate yh shape based on the daytype of
    every day in year. This function iteraes every day
    of the base year and assigns daily profiles depending
    on the daytype for every day

    Arguments
    ---------
    tech : str
        Technology
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
    lp_holiday = tech_lp[tech]['holiday'] / np.sum(tech_lp[tech]['holiday'])
    lp_workday = tech_lp[tech]['workday'] / np.sum(tech_lp[tech]['workday'])

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
    rs_fuel_raw_data_enduses, enduses['rs_all_enduses'] = read_data.read_fuel_rs(
        paths['rs_fuel_raw_data_enduses'])

    # Service Sector
    ss_fuel_raw_data_enduses, sectors['ss_sectors'], enduses['ss_all_enduses'] = read_data.read_fuel_ss(
        paths['ss_fuel_raw_data_enduses'],
        lookups['fueltypes_nr'])

    # Industry fuel
    is_fuel_raw_data_enduses, sectors['is_sectors'], enduses['is_all_enduses'] = read_data.read_fuel_is(
        paths['is_fuel_raw_data_enduses'], lookups['fueltypes_nr'], lookups['fueltypes'])

    # Iterate enduses per sudModel and flatten list
    enduses['all_enduses'] = []
    for enduse in enduses.values():
        enduses['all_enduses'] += enduse

    # Convert units
    fuels['rs_fuel_raw_data_enduses'] = conversions.convert_fueltypes_ktoe_GWh(
        rs_fuel_raw_data_enduses)
    fuels['ss_fuel_raw_data_enduses'] = conversions.convert_fueltypes_sectors_ktoe_gwh(
        ss_fuel_raw_data_enduses)
    fuels['is_fuel_raw_data_enduses'] = conversions.convert_fueltypes_sectors_ktoe_gwh(
        is_fuel_raw_data_enduses)

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
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row
        data = {}

        for row in read_lines:
            values_line = {}
            for number, value in enumerate(row[1:], 1):
                try:
                    values_line[_headings[number]] = float(value)
                except ValueError:
                    values_line[_headings[number]] = str(value)

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
        _headings = next(lines) # Skip first row

        for line in lines:
            geocode = str.strip(line[2])

            # Iterate fields and copy values
            for counter, heading in enumerate(_headings[4:], 4):
                heading_split = heading.split(":")
                category_unclean = str.strip(heading_split[1])
                category_full_name = str.strip(category_unclean.split(" ")[0]).replace(" ", "_")
                category_nr = category_full_name.split("_")[0]

                data[geocode][category_nr] = float(line[counter])

    logging.info("... loaded employment statistics")
    return dict(data)
