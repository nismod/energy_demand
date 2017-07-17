"""Loads all necessary data"""
import os
import sys
from random import randint
import numpy as np
from energy_demand.scripts_data import read_data
from energy_demand.scripts_data import rs_read_data
from energy_demand.scripts_data import ss_read_data
from energy_demand.scripts_data import read_weather_data
from energy_demand.scripts_data import write_data
from energy_demand.scripts_shape_handling import generic_shapes as generic_shapes
from energy_demand.scripts_basic import unit_conversions
from energy_demand.scripts_plotting import plotting_results
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_data(path_main, data):
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
    print("... load data")
    # ------------------------------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------------------------------
    data['path_dict'] = {

        # Local paths
        # -----------
        'path_bd_e_load_profiles': os.path.join(data['local_data_path'], r'01-HES_data/HES_base_appliances_eletricity_load_profiles.csv'),
        'folder_path_weater_data': os.path.join(data['local_data_path'], r'16-Met_office_weather_data\midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(data['local_data_path'], r'16-Met_office_weather_data\excel_list_station_details.csv'),

        'folder_validation_national_elec_data': os.path.join(data['local_data_path'], r'04-validation\03_national_elec_demand_2015\elec_demand_2015.csv'),


        # Residential
        # -----------
        'path_main': path_main,

        # Path for building stock assumptions
        'path_dwtype_lu': os.path.join(path_main, 'submodel_residential/lookup_dwelling_type.csv'),
        'path_hourly_gas_shape_resid': os.path.join(path_main, 'submodel_residential/SANSOM_residential_gas_hourly_shape.csv'),
        'path_dwtype_age': os.path.join(path_main, 'submodel_residential/data_submodel_residential_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'submodel_residential/data_submodel_residential_dwtype_floorarea.csv'),
        'path_reg_floorarea_resid': os.path.join(path_main, 'submodel_residential/data_submodel_residential_floorarea.csv'),

        # Path for model outputs
        'path_txt_service_tech_by_p': os.path.join(path_main, 'model_output/rs_service_tech_by_p.txt'),
        'path_out_stats_cProfile': os.path.join(path_main, '/model_output/stats_cProfile.txt'),

        # Path to all technologies
        'path_technologies': os.path.join(path_main, 'scenario_and_base_data/technology_base_scenario.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(path_main, 'submodel_residential/switches_fuel_scenaric.csv'),
        'ss_path_fuel_switches': os.path.join(path_main, 'submodel_service/switches_fuel_scenaric.csv'),
        'is_path_fuel_switches': os.path.join(path_main, 'submodel_industry/switches_fuel_scenaric.csv'),

        # Path to service switches
        'rs_path_service_switch': os.path.join(path_main, 'submodel_residential/switches_service_scenaric.csv'),
        'ss_path_service_switch': os.path.join(path_main, 'submodel_service/switches_service_scenaric.csv'),
        'is_path_industry_switch': os.path.join(path_main, 'submodel_industry/switches_industry_scenaric.csv'),

        # Paths to fuel raw data
        'path_rs_fuel_raw_data_enduses': os.path.join(path_main, 'submodel_residential/data_residential_by_fuel_end_uses.csv'),
        'path_ss_fuel_raw_data_enduses': os.path.join(path_main, 'submodel_service/data_service_by_fuel_end_uses.csv'),
        'path_is_fuel_raw_data_enduses': os.path.join(path_main, 'submodel_industry/data_industry_by_fuel_end_uses.csv'),

        # Paths to txt shapes
        'path_rs_txt_shapes': os.path.join(path_main, 'submodel_residential/txt_load_shapes'),
        'path_ss_txt_shapes': os.path.join(path_main, 'submodel_service/txt_load_shapes'),
        'path_is_txt_shapes': os.path.join(path_main, 'submodel_industry/txt_load_shapes'),

        #Technologies load shapes
        'path_hourly_gas_shape_hp': os.path.join(path_main, 'submodel_residential/SANSOM_residential_gas_hourly_shape_hp.csv'),
        'path_shape_rs_cooling': os.path.join(path_main, 'submodel_residential/shape_residential_cooling.csv'),
        'path_shape_rs_space_heating_primary_heating': os.path.join(path_main, 'submodel_residential/HES_base_appliances_eletricity_load_profiles_primary_heating.csv'),
        'path_shape_rs_space_heating_secondary_heating': os.path.join(path_main, 'submodel_residential/HES_base_appliances_eletricity_load_profiles_secondary_heating.csv'),

        }

    # ------------------------------------------------
    # Very basic look up tables
    # ------------------------------------------------
    # Fuel look-up table
    data['lu_fueltype'] = {
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'biomass': 5,
        'hydrogen': 6,
        'other': 7
        }

    # Daytypes
    data['day_type_lu'] = {
        0: 'weekend_day',
        1: 'working_day',
        2: 'coldest_day',
        3: 'warmest_day'
        }

    # Number of fueltypes
    data['nr_of_fueltypes'] = len(data['lu_fueltype'])

    # Dwelling types lookup table
    data['dwtype_lu'] = read_data.read_csv_dict_no_header(data['path_dict']['path_dwtype_lu'])

    # -----------------------------
    # Read in floor area of all regions and store in dict
    # TODO: REPLACE WITH Newcastle if ready
    # -----------------------------
    #REPLACE: Generate region_lookup from input data (Maybe read in region_lookup from shape?)
    data['lu_reg'] = {}
    for reg_name in data['population'][data['base_yr']]:
        data['lu_reg'][reg_name] = reg_name

    #TODO: FLOOR_AREA_LOOKUP:
    data['reg_floorarea_resid'] = {}
    for reg_name in data['population'][data['base_yr']]:
        data['reg_floorarea_resid'][reg_name] = 100000

    # ----------------------------------------------------------
    # Read in weather data and clean data
    # ----------------------------------------------------------

    # Temperature data
    if data['factcalculationcrit'] == True: #Scrap, eigentlich True
        print("read in fake weater data")

        temp_scrap = [12, 9, 10, 17, 23, 18903, 54, 67, 52, 19172, 30270, 103, 44, 105, 79, 113, 117, 132, 137, 145, 32, 150, 177, 161, 170, 18974, 23417, 908, 1039, 24125, 1007, 212, 17336, 1033, 987, 268, 1023, 19260, 235, 251, 1046, 1055, 1060, 1078, 1070, 1076, 1083, 1074, 1085, 16589, 30523, 315, 17314, 342, 16596, 346, 17344, 358, 373, 56486, 1145, 1171, 1137, 17309, 1090, 1144, 30690, 513, 56958, 527, 57199, 556, 381, 384, 386, 370, 405, 56216, 393, 16725, 1161, 1180, 1190, 643, 583, 409, 421, 432, 1198, 1209, 16611, 669, 24996, 657, 19187, 595, 461, 440, 1215, 1226, 1255, 676, 674, 692, 605, 613, 17176, 709, 471, 19188, 498, 504, 1346, 1285, 19206, 886, 888, 889, 847, 862, 869, 30620, 697, 708, 726, 16588, 743, 775, 1386, 1395, 1393, 1415, 1336, 1378, 1383, 1302, 1319, 842, 876, 779, 858, 795, 811, 1572, 1575, 57063, 1543, 56963, 1435, 1448, 1467, 1450, 1534, 48, 56905, 17089, 17090, 17091, 56370, 56906, 17094, 56907, 56908, 24089, 17097, 17098, 17099, 24090, 17101, 24275, 56909, 17102, 19211, 66, 14093, 56451, 110, 111, 114, 1585, 55827, 148, 159, 160, 195, 253, 1588, 285, 289, 57254, 16031, 310, 326, 339, 30750, 360, 367, 56986, 382, 61843, 4911, 30476, 413, 426, 61915, 435, 436, 442, 455, 456, 458, 481, 487, 516, 25726, 525, 529, 534, 61973, 542, 554, 19204, 30529, 578, 56424, 596, 24102, 57093, 607, 61948, 622, 61949, 634, 651, 61844, 658, 660, 10268, 691, 695, 711, 719, 723, 742, 56904, 744, 16769, 23450, 19159, 830, 61846, 25727, 855, 57247, 56962, 61847, 868, 17224, 918, 940, 1605, 1603, 982, 1005, 1035, 13343, 19203, 1067, 1073, 1080, 16851, 1111, 1112, 1119, 1125, 1132, 1166, 1204, 1205, 1221, 1223, 1238, 1249, 1272, 1276, 56939, 1326, 1345, 1352, 1367, 61743, 61737, 1609, 61744, 57250, 1418, 1431, 56937, 1452, 19192, 1488, 1502, 1504, 1507, 1517, 1523, 1529, 24103, 56810, 593, 1135, 1267, 18912, 1101, 466, 18929, 18923, 18927, 18931, 18919, 4, 116, 971, 246, 1006, 18909, 18936, 484, 18930, 18920, 18942, 1607, 725, 18925, 18937, 18908, 854, 25315, 38, 50, 60, 55890, 64, 55896, 118, 19193, 56463, 176, 181, 208, 30810, 214, 226, 15381, 237, 249, 262, 56130, 279, 286, 30747, 300, 17182, 347, 359, 57266, 4934, 445, 454, 55536, 509, 2515, 535, 56423, 539, 606, 609, 636, 638, 61908, 671, 24218, 688, 720, 757, 782, 818, 825, 843, 7621, 878, 883, 24795, 926, 57118, 949, 996, 13298, 1066, 25618, 61875, 24793, 1105, 25318, 1141, 1149, 56339, 1217, 1222, 30448, 1243, 9280, 9092, 1304, 1314, 1324, 8898, 1362, 23510, 8231, 1412, 1494, 1508, 1551, 600, 18921, 18911, 18946, 18941, 1574, 18918, 18913, 18916, 403, 863, 963, 1371, 25353, 759, 15045, 1291, 18914, 972, 25069, 18907, 219, 232, 18985, 439, 915, 1148, 57233, 457, 395, 1611, 1214, 1606, 24998, 18915, 56229, 30286, 3, 1489, 40, 19259, 1245, 17177, 1563, 1047, 61938, 61986, 30127, 407, 1475, 1530, 61937, 954, 62004, 808, 2710, 57268, 14444, 980, 57267, 62031, 62033, 16612, 62039, 267, 30084, 2, 62034, 62015, 8605, 62057, 9529, 62037]

        data['weather_stations_raw'] = read_weather_data.read_weather_stations_raw(data['path_dict']['folder_path_weater_stations'], temp_scrap)
        print(data['weather_stations_raw'][9])
        data['temperature_data'] = {}
        temp_y = np.zeros((365, 24))
        for day in range(365):
            temp_y[day] += randint(-5, 30)
        data['temperature_data'][9] = temp_y #np.zeros((365, 24)) #10 # DUMMY DATA WITH CONSTANT 10 DEGREES
        data['weather_stations'] = {}
        data['weather_stations'][9] = data['weather_stations_raw'][9]
    else:
        print("...read in weather data")
        # Read in raw temperature data
        data['temperature_data_raw'] = read_weather_data.read_weather_data_raw(data['path_dict']['folder_path_weater_data'], 9999)

        # Clean raw temperature data
        data['temperature_data'] = read_weather_data.clean_weather_data_raw(data['temperature_data_raw'], 9999)

        # Weather stations
        data['weather_stations'] = read_weather_data.read_weather_stations_raw(data['path_dict']['folder_path_weater_stations'], data['temperature_data'].keys())
        #print("...number of weater stations with cleaned data: " + str(len(data['weather_stations'].keys())))

        # Print out all x y of weater data
        '''for weather_station_nr in data['weather_stations']:
            print("Weaterstation {}  X and Y:  {} {}".format(weather_station_nr, data['weather_stations'][weather_station_nr]['station_latitude'], data['weather_stations'][weather_station_nr]['station_longitude']))
        '''
        del data['temperature_data_raw']

    # ------------------------------------------
    # Load ECUK fuel data
    # ------------------------------------------

    # Residential Sector (Table XY and Table XY )
    data['rs_fuel_raw_data_enduses'], data['rs_all_enduses'] = read_data.read_csv_base_data_resid(data['path_dict']['path_rs_fuel_raw_data_enduses'])

    # Service Sector
    data['ss_fuel_raw_data_enduses'], data['ss_sectors'], data['ss_all_enduses'] = read_data.read_csv_base_data_service(data['path_dict']['path_ss_fuel_raw_data_enduses'], data['nr_of_fueltypes']) # Yearly end use data

    # Industry fuel (Table 4.04)
    data['is_fuel_raw_data_enduses'], data['is_sectors'], data['is_all_enduses'] = read_data.read_csv_base_data_industry(data['path_dict']['path_is_fuel_raw_data_enduses'], data['nr_of_fueltypes'], data['lu_fueltype'])


    # ----------------------------------------
    # Convert units
    # ----------------------------------------
    data['rs_fuel_raw_data_enduses'] = unit_conversions.convert_across_all_fueltypes(data['rs_fuel_raw_data_enduses'])
    data['ss_fuel_raw_data_enduses'] = unit_conversions.convert_all_fueltypes_sector(data['ss_fuel_raw_data_enduses'])
    data['is_fuel_raw_data_enduses'] = unit_conversions.convert_all_fueltypes_sector(data['is_fuel_raw_data_enduses'])

    # ------------------------------------------
    # Specific technology shapes
    # ------------------------------------------
    # Regular day, weekday, weekend (across all months)
    data['rs_shapes_heating_boilers_dh'] = read_data.read_csv_float(data['path_dict']['path_hourly_gas_shape_resid']) # Boiler shape from Robert Sansom
    data['rs_shapes_heating_heat_pump_dh'] = read_data.read_csv_float(data['path_dict']['path_hourly_gas_shape_hp']) # Heat pump shape
    data['rs_shapes_cooling_dh'] = read_data.read_csv_float(data['path_dict']['path_shape_rs_cooling']) # ??

    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][0] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_heating_boilers_dh'][2] * 45.8)
    #print("=============")
    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater)
    data['rs_shapes_space_heating_storage_heater_elec_heating_dh'] = read_data.read_csv_float(data['path_dict']['path_shape_rs_space_heating_primary_heating'])
    data['rs_shapes_space_heating_second_elec_heating_dh'] = read_data.read_csv_float(data['path_dict']['path_shape_rs_space_heating_secondary_heating'])

    #plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_storage_heater_elec_heating_dh'][0] * 45.8)
    ##plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_storage_heater_elec_heating_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_storage_heater_elec_heating_dh'][2] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_second_elec_heating_dh'][0] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_second_elec_heating_dh'][1] * 45.8)
    #plotting_results.plot_load_profile_dh(data['rs_shapes_space_heating_second_elec_heating_dh'][2] * 45.8)

    ###data = add_yearly_external_fuel_data(data, rs_fuel_raw_data_enduses) #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE

    # Generate load shapes
    if data['factcalculationcrit'] == False: #False

        # Read raw files - Generate data from raw files
        data = load_shapes_from_raw(data, data['rs_all_enduses'], data['ss_all_enduses'], data['is_all_enduses'], data['is_sectors'])

        # Read txt files - Generate data from txt files
        data = rs_collect_shapes_from_txts(data, data['path_dict']['path_rs_txt_shapes'])
        data = ss_collect_shapes_from_txts(data, data['path_dict']['path_ss_txt_shapes'])
        data = is_collect_shapes_from_txts(data, data['path_dict']['path_is_txt_shapes'],  data['is_sectors'], data['is_all_enduses'])

    else:
        print("...read in load shapes from txt files")
        # Read txt files - Generate data from txt files
        data = rs_collect_shapes_from_txts(data, data['path_dict']['path_rs_txt_shapes'])
        data = ss_collect_shapes_from_txts(data, data['path_dict']['path_ss_txt_shapes'])
        data = is_collect_shapes_from_txts(data, data['path_dict']['path_is_txt_shapes'], data['is_sectors'], data['is_all_enduses'])

    # -- From Carbon Trust (service sector data) read out enduse specific shapes
    data['ss_all_tech_shapes_dh'], data['ss_all_tech_shapes_yd'] = ss_read_out_shapes_enduse_all_tech(data['ss_shapes_dh'], data['ss_shapes_yd'])

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
        enduse = file_name.split("__")[0] # two dashes because individual enduses may contain a single slash
        enduses.add(enduse)

    # Read load shapes from txt files for enduses
    for enduse in enduses:
        shape_peak_dh = write_data.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_peak_dh') + str('.txt')))
        shape_non_peak_dh = write_data.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_non_peak_dh') + str('.txt')))
        shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
        shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(enduse) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        data['rs_shapes_dh'][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_dh': shape_non_peak_dh}
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
        enduse = file_name.split("__")[1] # two dashes because individual enduses may contain a single slash
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
            print("Read in txt file sector: {}  enduse: {}  {}".format(sector, enduse, joint_string_name))

            shape_peak_dh = write_data.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_dh = write_data.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_dh') + str('.txt')))
            shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
            shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            data['ss_shapes_dh'][sector][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_dh': shape_non_peak_dh}
            data['ss_shapes_yd'][sector][enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return data

def is_collect_shapes_from_txts(data, path_to_txts, is_sectors, is_enduses):
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

    # IF NO REAL DATA ARE READ IN; ALSO DIRECTL GENERATED HERE
    
    print("...read in raw industry data") 
    data['is_shapes_yd'] = {}
    data['is_shapes_dh'] = {}
    for sector in is_sectors:
        data['is_shapes_yd'][sector] = {}
        data['is_shapes_dh'][sector] = {}
        for enduse in is_enduses:
            print("Create industry shapes   {}    {}".format(sector, enduse))
            data['is_shapes_yd'][sector][enduse] = {}
            data['is_shapes_dh'][sector][enduse] = {}

            # Industry Sector specific shape_peak_yd_factor
            shape_peak_yd_factor = 1 #TODO: MAYBE SPECIFY FOR DIFFERENT SECTORS

            # Generate generic shape
            data['is_shapes_dh'][sector][enduse]['shape_peak_dh'], data['is_shapes_dh'][sector][enduse]['shape_non_peak_dh'], data['is_shapes_yd'][sector][enduse]['shape_peak_yd_factor'], data['is_shapes_yd'][sector][enduse]['shape_non_peak_yd'] = generic_shapes.generic_flat_shape(shape_peak_yd_factor)


    '''
    # Iterate folders and get all sectors and enduse from file names
    all_csv_in_folder = os.listdir(path_to_txts)

    enduses = set([])
    sectors = set([])
    for file_name in all_csv_in_folder:
        sector = file_name.split("__")[0]
        enduse = file_name.split("__")[1] # two dashes because individual enduses may contain a single slash
        enduses.add(enduse)
        sectors.add(sector)

    data['is_shapes_dh'] = {}
    data['is_shapes_yd'] = {}

    # Read load shapes from txt files for enduses
    for sector in sectors:
        data['is_shapes_dh'][sector] = {}
        data['is_shapes_yd'][sector] = {}

        for enduse in enduses:
            print("Read in txt file sector: {}  enduse: {}".format(sector, enduse))
            joint_string_name = str(sector) + "__" + str(enduse)

            shape_peak_dh = write_data.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_dh = write_data.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_dh') + str('.txt')))
            shape_peak_yd_factor = write_data.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
            shape_non_peak_yd = write_data.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            data['is_shapes_dh'][sector][enduse] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_dh': shape_non_peak_dh}
            data['is_shapes_yd'][sector][enduse] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}
    '''
    return data

def load_shapes_from_raw(data, rs_enduses, ss_enduses, is_enduses, is_sectors):
    """Reads in raw data files and generates txt files

    HES data, Carbon Trust data area read in. This only needs to be run once

    Parameters
    -----------
    rs_enduses : array
        Residential enduses
    ss_raw_fuel : array
        Provided fuel input of ss

    """
    print("...read in raw data")

    # ==========================================
    # Submodel Industry Data
    # ===========================================
    data['is_shapes_yd'] = {}
    data['is_shapes_dh'] = {}
    for sector in is_sectors:
        data['is_shapes_yd'][sector] = {}
        data['is_shapes_dh'][sector] = {}
        for enduse in is_enduses:
            data['is_shapes_yd'][sector][enduse] = {}
            data['is_shapes_dh'][sector][enduse] = {}

            # Industry Sector specific shape_peak_yd_factor
            shape_peak_yd_factor = 1 #TODO: MAYBE SPECIFY

            # Generate generic shape (so far flat)
            shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd = generic_shapes.generic_flat_shape(shape_peak_yd_factor)

            # Write txt files
            write_data.create_txt_shapes(
                enduse,
                data['path_dict']['path_is_txt_shapes'],
                shape_peak_dh,
                shape_non_peak_dh,
                shape_peak_yd_factor,
                shape_non_peak_yd
                )

    # ===========================================-
    # RESIDENTIAL MODEL - LOAD HES DATA
    # ===========================================
    appliances_HES_enduse_matching = {
        'rs_cold': 0,
        'rs_cooking': 1,
        'rs_lighting': 2,
        'rs_consumer_electronics': 3,
        'rs_home_computing': 4,
        'rs_wet': 5,
        'rs_water_heating': 6,
        'NOT_USED_heating': 7,
        'NOT_USED_other':8,
        'NOT_USED_unkown': 9,
        'NOT_USED_showers': 10
        }

    # HES data -- Generate generic load profiles (shapes) for all electricity appliances from HES data
    hes_data, hes_y_peak, _ = rs_read_data.read_hes_data(data['path_dict']['path_bd_e_load_profiles'], len(appliances_HES_enduse_matching), data['day_type_lu'])

    # Assign read in raw data to the base year
    year_raw_values_hes = rs_read_data.assign_hes_data_to_year(len(appliances_HES_enduse_matching), hes_data, data['base_yr'])

    # Load shape for all enduses
    for enduse in rs_enduses:

        if enduse not in appliances_HES_enduse_matching:
            print("Warning: The enduse {} is not defined in appliances_HES_enduse_matching, i.e. no generic shape is loades from HES data but enduse needs to be defined with technologies".format(enduse))
        else:
            # Generate HES load shapes
            shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd = rs_read_data.get_hes_load_shapes(
                appliances_HES_enduse_matching,
                year_raw_values_hes,
                hes_y_peak,
                enduse
                )

            # Write txt files
            write_data.create_txt_shapes(
                enduse,
                data['path_dict']['path_rs_txt_shapes'],
                shape_peak_dh,
                shape_non_peak_dh,
                shape_peak_yd_factor,
                shape_non_peak_yd
                )

    # ==========================================
    # SERVICE MODEL - Load Carbon Trust data (Could be writte nfaster because rea in multiple times)
    # ===========================================

    # Iterate sectors and read in shape
    for sector in data['ss_sectors']:

        # Match electricity shapes for every sector
        if sector == 'community_arts_leisure':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Community')
        elif sector == 'education':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Education')
        elif sector == 'emergency_services':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
        elif sector == 'health':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Health')
        elif sector == 'hospitality':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
        elif sector == 'military':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
        elif sector == 'offices':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Offices')
        elif sector == 'retail':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Retail')
        elif sector == 'storage':
            sector_folder_path_elec = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
        else:
            sys.exit("Error: The sector {} could not be assigned a service sector electricity shape".format(sector))

        # ------------------------------------------------------
        # Assign same shape across all enduse for service sector
        # ------------------------------------------------------
        for enduse in ss_enduses:
            #print("Enduse service: {}  in sector '{}'".format(enduse, sector))

            # Select shape depending on enduse
            if enduse in ['ss_water_heating', 'ss_space_heating', 'ss_other_gas']: #, 'ss_cooling_and_ventilation']: #TODO: IMPROVE
                folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_gas')
            else:
                if enduse == 'ss_other_electricity':
                    folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
                else:
                    folder_path = sector_folder_path_elec

            #SCRAp---remove
            if data['factcalculationcrit']:
                folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Health')
            else:
                pass

            # Read in shape from carbon trust metering trial dataset
            shape_non_peak_dh, load_peak_shape_dh, shape_peak_yd_factor, shape_non_peak_yd = ss_read_data.read_raw_carbon_trust_data(folder_path)

            # Write shapes to txt
            joint_string_name = str(sector) + "__" + str(enduse)
            write_data.create_txt_shapes(joint_string_name, data['path_dict']['path_ss_txt_shapes'], load_peak_shape_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd)

    # ---------------------
    # Compare Jan and Jul
    # ---------------------
    #ss_read_data.compare_jan_jul(main_dict_dayyear_absolute)
    
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
    for ext_enduse in data['external_enduses_resid']: # Add external enduse
        enduses.append(ext_enduse)

    for enduse in rs_fuel_raw_data_enduses: # Add resid enduses
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

    Info
    ----
    The first setor is selected and all shapes of the enduses of this
    sector read out. Because all enduses exist for each sector,
    it does not matter from which sector the shapes are talen from
    """
    ss_all_tech_shapes_dh = {}
    ss_all_tech_shapes_yd = {}

    for sector in ss_shapes_yd:
        for enduse in ss_shapes_yd[sector]:
            ss_all_tech_shapes_dh[enduse] = {}
            ss_all_tech_shapes_yd[enduse] = {}

            # Add shapes
            ss_all_tech_shapes_dh[enduse] = ss_shapes_dh[sector][enduse]
            ss_all_tech_shapes_yd[enduse] = ss_shapes_yd[sector][enduse]
        #only iterate first sector as all enduses are the same in all sectors
        break

    return ss_all_tech_shapes_dh, ss_all_tech_shapes_yd
