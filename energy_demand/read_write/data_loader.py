"""Loads all necessary data
"""
import os
import csv
import numpy as np
import logging
from energy_demand.read_write import read_data
from energy_demand.read_write import read_weather_data
from energy_demand.read_write import write_data
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_results

def load_basic_lookups():
    """
    Return
    ------
    lookups : dict
        Basied lookups and other very basic properties
    """
    lookups = {}

    lookups['dwtype'] = {
        0: 'detached',
        1: 'semi_detached',
        2: 'terraced',
        3: 'flat',
        4: 'bungalow'
        }

    lookups['fueltype'] = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'heat': 7
        }

    lookups['nr_of_fueltypes'] = int(len(lookups['fueltype']))

    return lookups

def dummy_data_generation(data):
    """TODO: REPLACE WITH NEWCASTLE DATA
    """
    data['all_sectors'] = [
        'community_arts_leisure',
        'education',
        'emergency_services',
        'health',
        'hospitality',
        'military',
        'offices',
        'retail',
        'storage',
        'other'
        ]
    # Load dummy LAC and pop
    dummy_pop_geocodes = load_LAC_geocodes_info(
        data['local_paths']['path_dummy_regions']
        )

    regions = {}
    coord_dummy = {}
    pop_dummy = {}
    rs_floorarea = {}
    ss_floorarea_sector_by_dummy = {}

    for geo_code, values in dummy_pop_geocodes.items():
        regions[geo_code] = values['label']
        coord_dummy[geo_code] = {'longitude': values['Y_cor'], 'latitude': values['X_cor']}

    # GVA
    gva_data = {}
    for year in range(data['sim_param']['base_yr'], data['sim_param']['end_yr'] + 1):
        gva_data[year] = {}
        for region_geocode in regions:
            gva_data[year][region_geocode] = 999

    # Population
    for year in range(data['sim_param']['base_yr'], data['sim_param']['end_yr'] + 1):
        _data = {}
        for reg_geocode in regions:
            _data[reg_geocode] = dummy_pop_geocodes[reg_geocode]['POP_JOIN']
        pop_dummy[year] = _data

    # Residenital floor area
    for year in range(data['sim_param']['base_yr'], data['sim_param']['end_yr'] + 1):
        rs_floorarea[year] = {}
        for region_geocode in regions:
            rs_floorarea[year][region_geocode] = pop_dummy[year][region_geocode] #USE FLOOR AREA

    # Dummy flor area
    for region_geocode in regions:
        ss_floorarea_sector_by_dummy[region_geocode] = {}
        for sector in data['all_sectors']:
            ss_floorarea_sector_by_dummy[region_geocode][sector] = pop_dummy[2015][region_geocode]

    data['rs_floorarea'] = rs_floorarea
    data['ss_floorarea'] = ss_floorarea_sector_by_dummy
    data['lu_reg'] = {}
    for region_name in regions:
        data['lu_reg'][region_name] = region_name

    #TODO: FLOOR_AREA_LOOKUP:
    data['reg_floorarea_resid'] = {}
    for region_name in pop_dummy[data['sim_param']['base_yr']]:
        data['reg_floorarea_resid'][region_name] = 100000

    data['GVA'] = gva_data
    data['input_regions'] = regions
    data['population'] = pop_dummy
    data['reg_coord'] = coord_dummy
    data['ss_sector_floor_area_by'] = ss_floorarea_sector_by_dummy

    return data

def load_local_paths(path):
    """Create all local paths and folders
    """
    paths = {
        'path_bd_e_load_profiles': os.path.join(
            path, '_raw_data', 'A-HES_data', 'HES_base_appliances_eletricity_load_profiles.csv'),
        'folder_raw_carbon_trust': os.path.join(
            path, '_raw_data', "G_Carbon_Trust_advanced_metering_trial"),
        'folder_path_weater_data': os.path.join(
            path, '_raw_data', 'H-Met_office_weather_data', 'midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(
            path, '_raw_data', 'H-Met_office_weather_data', 'excel_list_station_details.csv'),
        'folder_validation_national_elec_data': os.path.join(
            path, '_raw_data', 'D-validation', '03_national_elec_demand_2015', 'elec_demand_2015.csv'),
        'path_dummy_regions': os.path.join(
            path, '_raw_data', 'B-census_data', 'regions_local_area_districts', '_quick_and_dirty_spatial_disaggregation', 'infuse_dist_lyr_2011_saved_short.csv'),
        'path_assumptions_db': os.path.join(
            path, '_processed_data', 'assumptions_from_db'),
        'rs_load_profile_txt': os.path.join(
            path, '_processed_data', 'load_profiles', 'rs_submodel'),
        'ss_load_profile_txt': os.path.join(
            path, '_processed_data', 'load_profiles', 'ss_submodel'),

        # Output Data
        'data_processed': os.path.join(
            path, '_processed_data'),
        'data_processed_disaggregated': os.path.join(
            path, '_processed_data', 'disaggregated'),
        'data_results': os.path.join(
            path, '_result_data'),
        'dir_changed_weather_data': os.path.join(
            path, '_processed_data', 'weather_data'),
        'path_processed_weather_data': os.path.join(
            path, '_processed_data', 'weather_data', 'weather_data.csv'),
        'changed_weather_station_data': os.path.join(
            path, '_processed_data', 'weather_data', 'weather_stations.csv'),
        'changed_weather_data': os.path.join(
            path, '_processed_data', 'weather_data', 'weather_data_changed_climate.csv'),
        'load_profiles': os.path.join(
            path, '_processed_data', 'load_profiles'),
        'rs_load_profiles': os.path.join(
            path, '_processed_data', 'load_profiles', 'rs_submodel'),
        'ss_load_profiles': os.path.join(
            path, '_processed_data', 'load_profiles', 'ss_submodel'),
        'dir_disattregated': os.path.join(
            path, '_processed_data', 'disaggregated'),
        'dir_services': os.path.join(
            path, '_processed_data', 'services'),
        'data_results_PDF': os.path.join(
            path, '_result_data', 'PDF')
        }

    # Create folders is they do not exist yet
    if not os.path.exists(paths['data_processed']):
        os.makedirs(paths['data_processed'])
    if not os.path.exists(paths['data_results']):
        os.makedirs(paths['data_results'])
    if not os.path.exists(paths['data_results_PDF']):
        os.makedirs(paths['data_results_PDF'])
    if not os.path.exists(paths['load_profiles']):
        os.makedirs(paths['load_profiles'])
    if not os.path.exists(paths['rs_load_profiles']):
        os.makedirs(paths['rs_load_profiles'])
    if not os.path.exists(paths['ss_load_profiles']):
        os.makedirs(paths['ss_load_profiles'])
    if not os.path.exists(paths['dir_disattregated']):
        os.makedirs(paths['dir_disattregated'])
    if not os.path.exists(paths['dir_services']):
        os.makedirs(paths['dir_services'])
    if not os.path.exists(paths['dir_changed_weather_data']):
        os.makedirs(paths['dir_changed_weather_data'])

    return paths

def load_paths(path):
    """Load all paths and create folders

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
        'path_dwtype': os.path.join(
            path, 'data', 'submodel_residential', 'lookup_dwelling_type.csv'),
        'path_hourly_gas_shape_resid': os.path.join(
            path, 'data', 'submodel_residential', 'SANSOM_residential_gas_hourly_shape.csv'),
        'path_dwtype_age': os.path.join(
            path, 'data', 'submodel_residential', 'data_submodel_residential_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(
            path, 'data', 'submodel_residential', 'data_submodel_residential_dwtype_floorarea.csv'),
        'path_reg_floorarea_resid': os.path.join(
            path, 'data', 'submodel_residential', 'data_submodel_residential_floorarea.csv'),

        # Path for model outputs
        'path_txt_service_tech_by_p': os.path.join(
            path, 'model_output', 'rs_service_tech_by_p.txt'),
        'path_out_stats_cProfile': os.path.join(
            path, 'model_output', 'stats_cProfile.txt'),

        # Path to all technologies
        'path_technologies': os.path.join(
            path, 'data', 'scenario_and_base_data', 'technology_base_scenario.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(
            path, 'data', 'submodel_residential', 'switches_fuel_scenaric.csv'),
        'ss_path_fuel_switches': os.path.join(
            path, 'data', 'submodel_service', 'switches_fuel_scenaric.csv'),
        'is_path_fuel_switches': os.path.join(
            path, 'data', 'submodel_industry', 'switches_fuel_scenaric.csv'),

        # Path to service switches
        'rs_path_service_switch': os.path.join(
            path, 'data', 'submodel_residential', 'switches_service_scenaric.csv'),
        'ss_path_service_switch': os.path.join(
            path, 'data', 'submodel_service', 'switches_service_scenaric.csv'),
        'is_path_industry_switch': os.path.join(
            path, 'data', 'submodel_industry', 'switches_industry_scenaric.csv'),

        # Paths to fuel raw data
        'rs_fuel_raw_data_enduses': os.path.join(
            path, 'data', 'submodel_residential', 'data_residential_by_fuel_end_uses.csv'),
        'ss_fuel_raw_data_enduses': os.path.join(
            path, 'data', 'submodel_service', 'data_service_by_fuel_end_uses.csv'),
        'is_fuel_raw_data_enduses': os.path.join(
            path, 'data', 'submodel_industry', 'data_industry_by_fuel_end_uses.csv'),

        # Technologies load shapes
        #'path_hourly_gas_shape_hp': os.path.join(
        # path, 'data', 'submodel_residential', 'SANSOM_residential_gas_hourly_shape_hp.csv'),
        'path_hourly_elec_shape_hp': os.path.join(
            path, 'data', 'submodel_residential', 'LOVE_elec_shape_dh_hp.csv'),

        'path_shape_rs_cooling': os.path.join(
            path, 'data', 'submodel_residential', 'shape_residential_cooling.csv'),
        'path_shape_ss_cooling': os.path.join(
            path, 'data', 'submodel_service', 'shape_service_cooling.csv'),
        'path_shape_rs_space_heating_primary_heating': os.path.join(
            path, 'data', 'submodel_residential', 'HES_base_appliances_eletricity_load_profiles_primary_heating.csv'),
        'path_shape_rs_space_heating_secondary_heating': os.path.join(
            path, 'data', 'submodel_residential', 'HES_base_appliances_eletricity_load_profiles_secondary_heating.csv')
        }

    return paths

def load_data_tech_profiles(tech_load_profiles, paths):
    """Load technology specific load profiles

    Arguments
    ----------
    data : dict
        Data container

    Returns
    ------
    data : dict
        Data container containing new load profiles
    """
    tech_load_profiles = {}

    # Boiler shape from Robert Sansom
    tech_load_profiles['rs_lp_heating_boilers_dh'] = read_data.read_load_shapes_tech(
        paths['path_hourly_gas_shape_resid']) #Regular day, weekday, weekend

    # Heat pump shape from Love et al. (2017)
    tech_load_profiles['rs_lp_heating_hp_dh'] = read_data.read_load_shapes_tech(
        paths['path_hourly_elec_shape_hp'])

    tech_load_profiles['rs_shapes_cooling_dh'] = read_data.read_csv_float(paths['path_shape_rs_cooling']) # ??
    tech_load_profiles['ss_shapes_cooling_dh'] = read_data.read_csv_float(paths['path_shape_ss_cooling']) # ??
    #plotting_results.plot_load_profile_dh(data['rs_lp_heating_boilers_dh'][0] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_lp_heating_boilers_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_lp_heating_boilers_dh'][2] * 45.8)

    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater)
    tech_load_profiles['rs_lp_storage_heating_dh'] = read_data.read_load_shapes_tech(
        paths['path_shape_rs_space_heating_primary_heating'])
    tech_load_profiles['rs_lp_second_heating_dh'] = read_data.read_load_shapes_tech(
        paths['path_shape_rs_space_heating_secondary_heating'])

    '''plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_storage_heating_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_storage_heating_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_storage_heating_dh'][2] * 45.8)
    plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_second_heating_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_second_heating_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['tech_load_profiles']['rs_lp_second_heating_dh'][2] * 45.8)
    '''
    return tech_load_profiles

def load_data_profiles(paths, local_paths):
    """Collect load profiles from txt files

    Arguments
    ----------
    data : dict
        Data container
    """
    tech_load_profiles = {}

    # ---------------------------------------
    # Load technology specific load profiles
    # ---------------------------------------
    tech_load_profiles = load_data_tech_profiles(
        tech_load_profiles,
        paths
        )

    logging.debug("... read in load shapes from txt files")
    tech_load_profiles['rs_shapes_dh'], tech_load_profiles['rs_shapes_yd'] = rs_collect_shapes_from_txts(
        local_paths['rs_load_profile_txt'])

    tech_load_profiles['ss_shapes_dh'], tech_load_profiles['ss_shapes_yd'] = ss_collect_shapes_from_txts(
        local_paths['ss_load_profile_txt'])

    # -- From Carbon Trust (service sector data) read out enduse specific shapes
    tech_load_profiles['ss_all_tech_shapes_dh'], tech_load_profiles['ss_all_tech_shapes_yd'] = ss_read_out_shapes_enduse_all_tech(
        tech_load_profiles['ss_shapes_dh'], tech_load_profiles['ss_shapes_yd'])

    return tech_load_profiles

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
    temperature_data : dict
        Temperatures
    """
    weather_stations = read_weather_data.read_weather_station_script_data(
        paths['changed_weather_station_data'])
    temperature_data = read_weather_data.read_weather_data_script_data(
        paths['changed_weather_data'])

    return weather_stations, temperature_data

def load_fuels(paths, lookups):
    """Load in ECUK fuel data

    Arguments
    ---------
    paths : dict
        Paths container
    lookups : dict
        Look-ups
    
    """
    enduses = {}
    sectors = {}
    fuels = {}
    # Residential Sector (ECUK Table XY and Table XY) 
    rs_fuel_raw_data_enduses, enduses['rs_all_enduses'] = read_data.read_base_data_resid(
        paths['rs_fuel_raw_data_enduses'])

    # Service Sector (ECUK Table XY)
    ss_fuel_raw_data_enduses, sectors['ss_sectors'], enduses['ss_all_enduses'] = read_data.read_csv_data_service(
        paths['ss_fuel_raw_data_enduses'],
        lookups['nr_of_fueltypes'])

    # Industry fuel (ECUK Table 4.04)
    is_fuel_raw_data_enduses, sectors['is_sectors'], enduses['is_all_enduses'] = read_data.read_csv_base_data_industry(
        paths['is_fuel_raw_data_enduses'], lookups['nr_of_fueltypes'], lookups['fueltype'])

    # Convert units
    fuels['rs_fuel_raw_data_enduses'] = conversions.convert_fueltypes(rs_fuel_raw_data_enduses)
    fuels['ss_fuel_raw_data_enduses'] = conversions.convert_fueltypes_sectors(ss_fuel_raw_data_enduses)
    fuels['is_fuel_raw_data_enduses'] = conversions.convert_fueltypes_sectors(is_fuel_raw_data_enduses)

    #TODO
    fuel_national_tranport = np.zeros((lookups['nr_of_fueltypes']))

    #Elec demand from ECUK for transport sector
    fuel_national_tranport[2] = conversions.convert_ktoe_gwh(385)

    fuels['ts_fuel_raw_data_enduses'] = fuel_national_tranport

    return enduses, sectors, fuels

def rs_collect_shapes_from_txts(txt_path):
    """All pre-processed load shapes are read in from .txt files without accesing raw files

    This loads HES files for residential sector

    Arguments
    ----------
    data : dict
        Data
    txt_path : float
        Path to folder with stored txt files

    Return
    ------
    data : dict TODO
        Data
    """
    rs_shapes_dh = {}
    rs_shapes_yd = {}

    # Iterate folders and get all enduse
    all_csv_in_folder = os.listdir(txt_path)

    enduses = set([])
    for file_name in all_csv_in_folder:
        # two dashes because individual enduses may contain a single slash
        enduse = file_name.split("__")[0]
        enduses.add(enduse)

    # Read load shapes from txt files for enduses
    for enduse in enduses:
        shape_peak_dh = write_data.read_txt_shape_peak_dh(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_peak_dh') + str('.txt')))
        shape_non_peak_y_dh = write_data.read_txt_shape_non_peak_yh(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
        shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
        shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(
            os.path.join(txt_path, str(enduse) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        rs_shapes_dh[enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_y_dh': shape_non_peak_y_dh}
        rs_shapes_yd[enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return rs_shapes_dh, rs_shapes_yd

def ss_collect_shapes_from_txts(txt_path):
    """Collect service shapes from txt files for every setor and enduse

    Arguments
    ----------
    txt_path : string
        Path to txt shapes files

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

    ss_shapes_dh = {}
    ss_shapes_yd = {}

    # Read load shapes from txt files for enduses
    for sector in sectors:
        ss_shapes_dh[sector] = {}
        ss_shapes_yd[sector] = {}

        for enduse in enduses:
            joint_string_name = str(sector) + "__" + str(enduse)
            #logging.debug("...Read in txt file sector: {}  enduse: {}  {}".format(sector, enduse, joint_string_name))
            shape_peak_dh = write_data.read_txt_shape_peak_dh(
                os.path.join(txt_path, str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_y_dh = write_data.read_txt_shape_non_peak_yh(
                os.path.join(txt_path, str(joint_string_name) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
            shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(
                os.path.join(txt_path, str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
            shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(
                os.path.join(txt_path, str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            ss_shapes_dh[sector][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_y_dh': shape_non_peak_y_dh}
            ss_shapes_yd[sector][enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return ss_shapes_dh, ss_shapes_yd

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

def ss_read_out_shapes_enduse_all_tech(ss_shapes_dh, ss_shapes_yd):
    """Iterate carbon trust dataset and read out shapes for enduses

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

    for sector in ss_shapes_yd:
        for enduse in ss_shapes_yd[sector]:
            ss_all_tech_shapes_dh[enduse] = ss_shapes_dh[sector][enduse]
            ss_all_tech_shapes_yd[enduse] = ss_shapes_yd[sector][enduse]
        break #only iterate first sector as all enduses are the same in all sectors
    #TODO: IS YD NEEDED?
    return ss_all_tech_shapes_dh, ss_all_tech_shapes_yd

def load_LAC_geocodes_info(path_to_csv):
    """Import local area unit district codes

    Read csv file and create dictionary with 'geo_code'

    PROVIDED IN UNIT?? (KWH I guess)
    Note
    -----
    - no LAD without population must be included
    """
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row
        data = {}

        for row in read_lines:
            values_line = {}
            for nr, value in enumerate(row[1:], 1):
                try:
                    values_line[_headings[nr]] = float(value)
                except ValueError: #SHARK
                    values_line[_headings[nr]] = str(value)

            # Add entry with geo_code
            data[row[0]] = values_line

    return data
