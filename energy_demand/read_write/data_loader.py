"""Loads all necessary data
"""
import os
import sys
from random import randint
import numpy as np
from energy_demand.read_write import read_data
from energy_demand.read_write import read_weather_data
from energy_demand.read_write import write_data
from energy_demand.profiles import generic_shapes as generic_shapes
from energy_demand.basic import unit_conversions
from energy_demand.plotting import plotting_results
import csv

def load_paths(path_main, local_data_path):
    
    print("..load paths data")
    # ------------------------------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------------------------------

    path_dict = {
        # Local paths
        'path_bd_e_load_profiles': os.path.join(local_data_path, r'01-HES_data', 'HES_base_appliances_eletricity_load_profiles.csv'),
        'folder_path_weater_data': os.path.join(local_data_path, r'16-Met_office_weather_data', 'midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(local_data_path, r'16-Met_office_weather_data', 'excel_list_station_details.csv'),

        'folder_validation_national_elec_data': os.path.join(local_data_path, r'04-validation', '03_national_elec_demand_2015', 'elec_demand_2015.csv'),

        # Residential
        # -----------
        'path_main': path_main,

        'path_scripts_data': os.path.join(path_main, 'data', 'data_scripts'),
        'path_assumptions_db': os.path.join(path_main, 'data', 'data_scripts', 'assumptions_from_db'),
        # Paths to txt shapes
        'path_rs_load_profile_txt': os.path.join(path_main, 'data', 'data_scripts', 'load_profiles', 'rs_submodel'),
        'path_ss_load_profile_txt': os.path.join(path_main, 'data', 'data_scripts', 'load_profiles', 'ss_submodel'),

        # Path for building stock assumptions
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
        'path_shape_rs_space_heating_secondary_heating': os.path.join(path_main, 'data', 'submodel_residential', 'HES_base_appliances_eletricity_load_profiles_secondary_heating.csv'),
        }

    return path_dict

def load_data_tech_profiles(data):
    """
    """
    # ------------------------------------------
    # Specific technology shapes
    # ------------------------------------------
    # Boiler shape from Robert Sansom
    data['rs_shapes_heating_boilers_dh'] = read_data.read_csv_load_shapes_technology(
        data['path_dict']['path_hourly_gas_shape_resid']) #Regular day, weekday, weekend

    # Heat pump shape from Love et al. (2017)
    data['rs_shapes_heating_heat_pump_dh'] = read_data.read_csv_load_shapes_technology(
        data['path_dict']['path_hourly_elec_shape_hp'])

    data['rs_shapes_cooling_dh'] = read_data.read_csv_float(data['path_dict']['path_shape_rs_cooling']) # ??
    data['ss_shapes_cooling_dh'] = read_data.read_csv_float(data['path_dict']['path_shape_ss_cooling']) # ??
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][0] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][2] * 45.8)

    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater)
    data['rs_profile_heating_storage_dh'] = read_data.read_csv_load_shapes_technology(
        data['path_dict']['path_shape_rs_space_heating_primary_heating'])
    data['rs_profile_heating_second_heating_dh'] = read_data.read_csv_load_shapes_technology(
        data['path_dict']['path_shape_rs_space_heating_secondary_heating'])

    '''plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_storage_dh'][2] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][0] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][1] * 45.8)
    plotting_results.plot_load_profile_dh(data['rs_profile_heating_second_heating_dh'][2] * 45.8)
    '''
    return data

# pylint: disable=I0011,C0321,C0301,C0103, C0325
def load_data_profiles(data):
    """
    """
    # --------------------
    # Collect load profiles from txt files (needs to be preprocssed with scripts)
    # --------------------
    print("...read in load shapes from txt files")
    data = rs_collect_shapes_from_txts(data, data['path_dict']['path_rs_load_profile_txt'])

    data = ss_collect_shapes_from_txts(data, data['path_dict']['path_ss_load_profile_txt'])

    # -- From Carbon Trust (service sector data) read out enduse specific shapes
    data['ss_all_tech_shapes_dh'], data['ss_all_tech_shapes_yd'] = ss_read_out_shapes_enduse_all_tech(
        data['ss_shapes_dh'], data['ss_shapes_yd'])

    return data

def load_data_temperatures(path_scripts_data):
    print("..load temperature data")

    # ----------------------------------------------------------
    # Read in cleaned temperature and weather station data
    # ----------------------------------------------------------
    weather_stations = read_weather_data.read_weather_station_script_data(
        os.path.join(path_scripts_data, 'weather_stations.csv'))
    temperature_data = read_weather_data.read_weather_data_script_data(
        os.path.join(path_scripts_data, 'weather_data.csv'))

    return weather_stations, temperature_data

def load_fuels(data):
    # ------------------------------------------
    # Load ECUK fuel data
    # ------------------------------------------

    # Residential Sector (ECUK Table XY and Table XY )
    data['rs_fuel_raw_data_enduses'], data['rs_all_enduses'] = read_data.read_csv_base_data_resid(
        data['path_dict']['path_rs_fuel_raw_data_enduses'])

    # Service Sector (ECUK Table XY)
    data['ss_fuel_raw_data_enduses'], data['ss_sectors'], data['ss_all_enduses'] = read_data.read_csv_base_data_service(
        data['path_dict']['path_ss_fuel_raw_data_enduses'],
        data['nr_of_fueltypes'])
    print("RS Sectors: {}".format(data['ss_sectors']))
    print(data['ss_all_enduses'])
    # Industry fuel (ECUK Table 4.04)
    data['is_fuel_raw_data_enduses'], data['is_sectors'], data['is_all_enduses'] = read_data.read_csv_base_data_industry(data['path_dict']['path_is_fuel_raw_data_enduses'], data['nr_of_fueltypes'], data['lu_fueltype'])
    print("RS Sectors: {}".format(data['is_sectors']))

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

def load_data_lookup_data(data):
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------
    data : dict
        Dict with own data
    path_main : str
        Path to all data of model run which are not provided externally by wrapper

    Returns
    -------
    data : list
        Returns a list where storing all data
    """
    print("..load other data")

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

    # Dwelling types lookup table
    data['dwtype_lu'] = {
        0: 'detached',
        1: 'semi_detached',
        2: 'terraced',
        3: 'flat',
        4: 'bungalow'
        }

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

def load_LAC_geocodes_info():
    """Import local area unit district codes

    Read csv file and create dictionary with 'geo_code'

    PROVIDED IN UNIT?? (KWH I guess)
    Note
    -----
    - no LAD without population must be included
    """
    path_to_csv = r'Y:\01-Data_NISMOD\data_energy_demand\02-census_data\regions_local_area_districts\_quick_and_dirty_spatial_disaggregation\infuse_dist_lyr_2011_saved_short.csv'

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row
        data = {}

        # Iterate rows
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
