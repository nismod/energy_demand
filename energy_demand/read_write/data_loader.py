"""Loads all necessary data
"""
import os
import csv
import numpy as np
from energy_demand.read_write import read_data
from energy_demand.read_write import read_weather_data
from energy_demand.read_write import write_data
from energy_demand.basic import unit_conversions
from energy_demand.plotting import plotting_results

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
    # Load dummy LAC and pop (Full List is : infuse_dist_lyr_2011.csv  otherwise infuse_dist_lyr_2011_saved.)
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

    # -----------------------------
    # Read in floor area of all regions and store in dic# TODO: REPLACE WITH Newcastle if ready
    # -----------------------------
    #REPLACE: Generate region_lookup from input data (Maybe read in region_lookup from shape?)
    data['lu_reg'] = {} #TODO: DO NOT READ REGIONS FROM POP BUT DIRECTLY
    for region_name in regions:
        data['lu_reg'][region_name] = region_name

    #TODO: FLOOR_AREA_LOOKUP:
    data['reg_floorarea_resid'] = {}
    for region_name in pop_dummy[data['sim_param']['base_yr']]:
        data['reg_floorarea_resid'][region_name] = 100000
    
    data['GVA'] = gva_data
    data['input_regions'] = regions
    data['population'] = pop_dummy
    data['reg_coordinates'] = coord_dummy
    data['ss_sector_floor_area_by'] = ss_floorarea_sector_by_dummy

    return data

def load_local_paths(local_path):
    """Create all local paths and folders
    """
    paths = {
        'path_bd_e_load_profiles': os.path.join(local_path, '_raw_data', 'A-HES_data', 'HES_base_appliances_eletricity_load_profiles.csv'),
        'folder_raw_carbon_trust': os.path.join(local_path, '_raw_data', "G_Carbon_Trust_advanced_metering_trial"),
        'folder_path_weater_data': os.path.join(local_path, '_raw_data', 'H-Met_office_weather_data', 'midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(local_path, '_raw_data', 'H-Met_office_weather_data', 'excel_list_station_details.csv'),
        'folder_validation_national_elec_data': os.path.join(local_path, '_raw_data', 'D-validation', '03_national_elec_demand_2015', 'elec_demand_2015.csv'),
        'path_dummy_regions': os.path.join(local_path, '_raw_data', 'B-census_data', 'regions_local_area_districts', '_quick_and_dirty_spatial_disaggregation', 'infuse_dist_lyr_2011_saved_short.csv'),
        
        'path_assumptions_db': os.path.join(local_path, '_processed_data', 'assumptions_from_db'),
        
        'path_rs_load_profile_txt': os.path.join(local_path, '_processed_data', 'load_profiles', 'rs_submodel'),
        'path_ss_load_profile_txt': os.path.join(local_path, '_processed_data', 'load_profiles', 'ss_submodel'),

        # Output Data
        'path_data_processed': os.path.join(local_path, '_processed_data'),
        'path_data_results': os.path.join(local_path, '_result_data'),
        'path_processed_weather_data': os.path.join(local_path, '_processed_data', 'weather_data','weather_data.csv'),
        'path_changed_weather_station_data': os.path.join(local_path, '_processed_data', 'weather_data', 'weather_stations.csv'),
        'path_changed_weather_data': os.path.join(local_path, '_processed_data', 'weather_data', 'weather_data_changed_climate.csv'),

        'path_load_profiles': os.path.join(local_path, '_processed_data', 'load_profiles'),
        'path_rs_load_profiles': os.path.join(local_path, '_processed_data', 'load_profiles', 'rs_submodel'),
        'path_ss_load_profiles': os.path.join(local_path, '_processed_data', 'load_profiles', 'ss_submodel'),
        'path_dir_changed_weather_data': os.path.join(local_path, '_processed_data', 'weather_data'),
        
        'path_dir_disattregated': os.path.join(local_path, '_processed_data', 'disaggregated'),
        'path_dir_services': os.path.join(local_path, '_processed_data', 'services') 
        }

    # Create folders is they do not exist yet
    if not os.path.exists(paths['path_data_processed']):
        os.makedirs(paths['path_data_processed'])
    if not os.path.exists(paths['path_data_results']):
        os.makedirs(paths['path_data_results'])
    if not os.path.exists(paths['path_load_profiles']):
        os.makedirs(paths['path_load_profiles'])
    if not os.path.exists(paths['path_rs_load_profiles']):
        os.makedirs(paths['path_rs_load_profiles'])
    if not os.path.exists(paths['path_ss_load_profiles']):
        os.makedirs(paths['path_ss_load_profiles'])
    if not os.path.exists(paths['path_dir_disattregated']):
        os.makedirs(paths['path_dir_disattregated'])
    if not os.path.exists(paths['path_dir_services']):
        os.makedirs(paths['path_dir_services'])
    if not os.path.exists(paths['path_dir_changed_weather_data']):
        os.makedirs(paths['path_dir_changed_weather_data'])

    return paths

def load_paths(path_main):
    """Load all paths and create folders

    Parameters
    ----------
    path_main : str
        Main path

    Return
    ------
    out_dict : dict
        Data container containing dics
    """
    paths = {

        # Residential
        'path_main': path_main,

        # Path for dwelling stock assumptions
        'path_dwtype_lu': os.path.join(path_main, 'data', 'submodel_residential', 'lookup_dwelling_type.csv'),
        'path_hourly_gas_shape_resid': os.path.join(path_main, 'data', 'submodel_residential', 'SANSOM_residential_gas_hourly_shape.csv'),
        'path_dwtype_age': os.path.join(path_main, 'data', 'submodel_residential', 'data_submodel_residential_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'data', 'submodel_residential', 'data_submodel_residential_dwtype_floorarea.csv'),
        'path_reg_floorarea_resid': os.path.join(path_main, 'data', 'submodel_residential', 'data_submodel_residential_floorarea.csv'),

        # Path for model outputs
        'path_txt_service_tech_by_p': os.path.join(path_main, 'model_output', 'rs_service_tech_by_p.txt'),
        'path_out_stats_cProfile': os.path.join(path_main, 'model_output', 'stats_cProfile.txt'),

        # Path to all technologies
        'path_technologies': os.path.join(path_main, 'data', 'scenario_and_base_data', 'technology_base_scenario.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(path_main, 'data', 'submodel_residential', 'switches_fuel_scenaric.csv'),
        'ss_path_fuel_switches': os.path.join(path_main, 'data', 'submodel_service', 'switches_fuel_scenaric.csv'),
        'is_path_fuel_switches': os.path.join(path_main, 'data', 'submodel_industry', 'switches_fuel_scenaric.csv'),

        # Path to service switches
        'rs_path_service_switch': os.path.join(path_main, 'data', 'submodel_residential', 'switches_service_scenaric.csv'),
        'ss_path_service_switch': os.path.join(path_main, 'data', 'submodel_service', 'switches_service_scenaric.csv'),
        'is_path_industry_switch': os.path.join(path_main, 'data', 'submodel_industry', 'switches_industry_scenaric.csv'),

        # Paths to fuel raw data
        'path_rs_fuel_raw_data_enduses': os.path.join(path_main, 'data', 'submodel_residential', 'data_residential_by_fuel_end_uses.csv'),
        'path_ss_fuel_raw_data_enduses': os.path.join(path_main, 'data', 'submodel_service', 'data_service_by_fuel_end_uses.csv'),
        'path_is_fuel_raw_data_enduses': os.path.join(path_main, 'data', 'submodel_industry', 'data_industry_by_fuel_end_uses.csv'),

        # Technologies load shapes
        #'path_hourly_gas_shape_hp': os.path.join(path_main, 'data', 'submodel_residential', 'SANSOM_residential_gas_hourly_shape_hp.csv'),
        'path_hourly_elec_shape_hp': os.path.join(path_main, 'data', 'submodel_residential', 'LOVE_elec_shape_dh_hp.csv'),

        'path_shape_rs_cooling': os.path.join(path_main, 'data', 'submodel_residential', 'shape_residential_cooling.csv'),
        'path_shape_ss_cooling': os.path.join(path_main, 'data', 'submodel_service', 'shape_service_cooling.csv'),
        'path_shape_rs_space_heating_primary_heating': os.path.join(path_main, 'data', 'submodel_residential', 'HES_base_appliances_eletricity_load_profiles_primary_heating.csv'),
        'path_shape_rs_space_heating_secondary_heating': os.path.join(path_main, 'data', 'submodel_residential', 'HES_base_appliances_eletricity_load_profiles_secondary_heating.csv')
        }

    return paths

def load_data_tech_profiles(data):
    """TODO
    """
    # ------------------------------------------
    # Specific technology shapes
    # ------------------------------------------
    # Boiler shape from Robert Sansom
    data['rs_shapes_heating_boilers_dh'] = read_data.read_csv_load_shapes_technology(
        data['paths']['path_hourly_gas_shape_resid']) #Regular day, weekday, weekend

    # Heat pump shape from Love et al. (2017)
    data['rs_shapes_heating_heat_pump_dh'] = read_data.read_csv_load_shapes_technology(
        data['paths']['path_hourly_elec_shape_hp'])

    data['rs_shapes_cooling_dh'] = read_data.read_csv_float(data['paths']['path_shape_rs_cooling']) # ??
    data['ss_shapes_cooling_dh'] = read_data.read_csv_float(data['paths']['path_shape_ss_cooling']) # ??
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][0] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][2] * 45.8)

    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater)
    data['rs_profile_heating_storage_dh'] = read_data.read_csv_load_shapes_technology(
        data['paths']['path_shape_rs_space_heating_primary_heating'])
    data['rs_profile_heating_second_heating_dh'] = read_data.read_csv_load_shapes_technology(
        data['paths']['path_shape_rs_space_heating_secondary_heating'])

    '''plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][2] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][2] * 45.8)
    '''
    return data

def load_data_profiles(data):
    """
    """
    # --------------------
    # Collect load profiles from txt files (needs to be preprocssed with scripts)
    # --------------------
    print("...read in load shapes from txt files")
    data = rs_collect_shapes_from_txts(data, data['paths']['path_rs_load_profile_txt'])

    data = ss_collect_shapes_from_txts(data, data['paths']['path_ss_load_profile_txt'])

    # -- From Carbon Trust (service sector data) read out enduse specific shapes
    data['ss_all_tech_shapes_dh'], data['ss_all_tech_shapes_yd'] = ss_read_out_shapes_enduse_all_tech(
        data['ss_shapes_dh'], data['ss_shapes_yd'])

    return data

def load_data_temperatures(local_paths):
    """Read in cleaned temperature and weather station data

    Parameters
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
        local_paths['path_changed_weather_station_data'])
    temperature_data = read_weather_data.read_weather_data_script_data(
        local_paths['path_changed_weather_data'])

    return weather_stations, temperature_data

def load_fuels(data):
    """
    """
    # ------------------------------------------
    # Load ECUK fuel data
    # ------------------------------------------
    data['lu_fueltype'] = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'heat': 7
        }

    data['nr_of_fueltypes'] = int(len(data['lu_fueltype']))

    # Residential Sector (ECUK Table XY and Table XY )
    data['rs_fuel_raw_data_enduses'], data['rs_all_enduses'] = read_data.read_csv_base_data_resid(
        data['paths']['path_rs_fuel_raw_data_enduses'])

    # Service Sector (ECUK Table XY)
    data['ss_fuel_raw_data_enduses'], data['ss_sectors'], data['ss_all_enduses'] = read_data.read_csv_data_service(
        data['paths']['path_ss_fuel_raw_data_enduses'],
        data['nr_of_fueltypes'])

    # Industry fuel (ECUK Table 4.04)
    data['is_fuel_raw_data_enduses'], data['is_sectors'], data['is_all_enduses'] = read_data.read_csv_base_data_industry(data['paths']['path_is_fuel_raw_data_enduses'], data['nr_of_fueltypes'], data['lu_fueltype'])

    # ----------------------------------------
    # Convert units
    # ----------------------------------------
    data['rs_fuel_raw_data_enduses'] = unit_conversions.convert_across_all_fueltypes(data['rs_fuel_raw_data_enduses'])
    data['ss_fuel_raw_data_enduses'] = unit_conversions.convert_all_fueltypes_sector(data['ss_fuel_raw_data_enduses'])
    data['is_fuel_raw_data_enduses'] = unit_conversions.convert_all_fueltypes_sector(data['is_fuel_raw_data_enduses'])

    #TODO
    fuel_national_tranport = np.zeros((data['nr_of_fueltypes']))

    #Elec demand from ECUK for transport sector
    fuel_national_tranport[2] = unit_conversions.convert_ktoe_gwh(385)

    #fuel_national_tranport[2] = 385
    data['ts_fuel_raw_data_enduses'] = fuel_national_tranport

    return data

def rs_collect_shapes_from_txts(data, path_to_txts):
    """All pre-processed load shapes are read in from .txt files without accesing raw files

    This loads HES files for residential sector

    Parameters
    ----------
    data : dict
        Data
    path_to_txts : float
        Path to folder with stored txt files

    Return
    ------
    data : dict
        Data
    """
    data['rs_shapes_dh'] = {}
    data['rs_shapes_yd'] = {}

    # Iterate folders and get all enduse
    all_csv_in_folder = os.listdir(path_to_txts)

    enduses = set([])
    for file_name in all_csv_in_folder:
        # two dashes because individual enduses may contain a single slash
        enduse = file_name.split("__")[0]
        enduses.add(enduse)

    # Read load shapes from txt files for enduses
    for enduse in enduses:
        shape_peak_dh = write_data.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_peak_dh') + str('.txt')))
        shape_non_peak_y_dh = write_data.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
        shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
        shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        data['rs_shapes_dh'][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_y_dh': shape_non_peak_y_dh}
        data['rs_shapes_yd'][enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return data

def ss_collect_shapes_from_txts(data, path_to_txts):
    """Collect service shapes from txt files for every setor and enduse

    Parameters
    ----------
    path_to_txts : string
        Path to txt shapes files

    Return
    ------
    data : dict
        Data
    """
    # Iterate folders and get all sectors and enduse from file names
    all_csv_in_folder = os.listdir(path_to_txts)

    enduses = set([])
    sectors = set([])
    for file_name in all_csv_in_folder:
        sector = file_name.split("__")[0]
        enduse = file_name.split("__")[1]
        enduses.add(enduse)
        sectors.add(sector)

    data['ss_shapes_dh'] = {}
    data['ss_shapes_yd'] = {}

    # Read load shapes from txt files for enduses
    for sector in sectors:
        data['ss_shapes_dh'][sector] = {}
        data['ss_shapes_yd'][sector] = {}

        for enduse in enduses:
            joint_string_name = str(sector) + "__" + str(enduse)
            #print("...Read in txt file sector: {}  enduse: {}  {}".format(sector, enduse, joint_string_name))
            shape_peak_dh = write_data.read_txt_shape_peak_dh(
                os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_y_dh = write_data.read_txt_shape_non_peak_yh(
                os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
            shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(
                os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
            shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(
                os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            data['ss_shapes_dh'][sector][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_y_dh': shape_non_peak_y_dh}
            data['ss_shapes_yd'][sector][enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return data

def create_enduse_dict(data, rs_fuel_raw_data_enduses):
    """Create dictionary with all residential enduses and store in data dict

    For residential model

    Parameters
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

    Parameters
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

            # Add shapes
            ss_all_tech_shapes_dh[enduse] = ss_shapes_dh[sector][enduse]
            ss_all_tech_shapes_yd[enduse] = ss_shapes_yd[sector][enduse]
        #only iterate first sector as all enduses are the same in all sectors
        break

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
                except:
                    values_line[_headings[nr]] = str(value)

            # Add entry with geo_code
            data[row[0]] = values_line

    return data
