"""Loads all necessary data"""
import os
import sys
from random import randint
import numpy as np
import energy_demand.data_loader_functions as df
import energy_demand.main_functions as mf
# import energy_demand.plot_functions as pf
#import matplotlib.pyplot as plt
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
    # ------------------------------------------------
    # Very basic look up tables
    # ------------------------------------------------
    # Fuel look-up table
    data['lu_fueltype'] = {
        'hybrid': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'heat_sold': 4,
        'bioenergy_waste':5,
        'hydrogen': 6,
        'coal': 7
        }

    #Daytypes
    data['day_type_lu'] = {
        0: 'weekend_day',
        1: 'working_day',
        2: 'coldest_day',
        3: 'warmest_day'
        }

    # Number of fueltypes
    data['nr_of_fueltypes'] = len(data['lu_fueltype'])

    # -----------------------------
    # Read in floor area of all regions and store in dict
    # TODO: REPLACE WITH Newcastle if ready
    # -----------------------------
    #REPLACE: Generate region_lookup from input data (MAybe read in region_lookup from shape?)
    data['lu_reg'] = {}
    for reg_name in data['population'][data['base_yr']]:
        data['lu_reg'][reg_name] = reg_name

    #TODO: FLOOR_AREA_LOOKUP:
    data['reg_floorarea_resid'] = {}
    for reg_name in data['population'][data['base_yr']]:
        data['reg_floorarea_resid'][reg_name] = 100000

    # Paths
    data['path_dict'] = {


        # Local paths
        # -----------
        'path_bd_e_load_profiles': os.path.join(data['local_data_path'], r'01-HES_data/HES_base_appliances_eletricity_load_profiles.csv'),
        'folder_path_weater_data': os.path.join(data['local_data_path'], r'16-Met_office_weather_data\midas_wxhrly_201501-201512.csv'),
        'folder_path_weater_stations': os.path.join(data['local_data_path'], r'16-Met_office_weather_data\excel_list_station_details.csv'),

        # Residential
        # -----------
        'path_main': path_main,
        'path_temp_txt': os.path.join(path_main, 'scenario_and_base_data/mean_temp_data'),

        'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),

        'path_hourly_gas_shape_resid': os.path.join(path_main, 'residential_model/SANSOM_residential_gas_hourly_shape.csv'),
        'path_hourly_gas_shape_hp': os.path.join(path_main, 'residential_model/SANSOM_residential_gas_hourly_shape_hp.csv'),
        'path_dwtype_age': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_floorarea.csv'),
        'path_reg_floorarea_resid': os.path.join(path_main, 'residential_model/data_residential_model_floorarea.csv'),
        'path_txt_service_tech_by_p': os.path.join(path_main, 'model_output/rs_service_tech_by_p.txt'),

        'path_shape_rs_cooling': os.path.join(path_main, 'residential_model/shape_residential_cooling.csv'),
        'path_out_stats_cProfile': os.path.join(path_main, '/model_output/stats_cProfile.txt'),

        # All technologies
        'path_technologies': os.path.join(path_main, 'scenario_and_base_data/technology_base_scenario.csv'),

        # Fuel switches
        'rs_path_fuel_switches': os.path.join(path_main, 'residential_model/switches_fuel_scenaric.csv'),
        'ss_path_fuel_switches': os.path.join(path_main, 'service_model/switches_fuel_scenaric.csv'),

        # Path to excel with ss service switch
        'rs_path_service_switch': os.path.join(path_main, 'residential_model/switches_service_scenaric.csv'),
        'ss_path_service_switch': os.path.join(path_main, 'service_model/switches_service_scenaric.csv'),

        # Paths to fuels
        'path_rs_fuel_raw_data_enduses': os.path.join(path_main, 'residential_model/data_residential_by_fuel_end_uses.csv'),
        'path_ss_fuel_raw_data_enduses': os.path.join(path_main, 'service_model/data_service_by_fuel_end_uses.csv'),

        # Paths to txt shapes
        'path_rs_txt_shapes': os.path.join(path_main, 'residential_model/txt_load_shapes'),
        'path_ss_txt_shapes': os.path.join(path_main, 'service_model/txt_load_shapes')
        }

    # ----------------------------------------------------------
    # Read in weather data and clean data
    # ----------------------------------------------------------

    # Weather stations
    data['weather_stations_raw'] = df.read_weather_stations_raw(data['path_dict']['folder_path_weater_stations']) # Read all weater stations properties

    # Weather data
    '''data['temperature_data_raw'] = df.read_weather_data_raw(data['path_dict']['folder_path_weater_data'], 9999) # Read in raw temperature data

    data['temperature_data'] = df.clean_weather_data_raw(data['temperature_data_raw'], 9999) # Clean weather data
    data['weather_stations'] = df.reduce_weather_stations(data['temperature_data'].keys(), data['weather_stations_raw']) # Reduce weater stations for which there is data provided
    print("Number of weater stations with cleaned data: " + str(len(data['weather_stations'].keys())))

    del data['weather_stations_raw'] # Delete raw data from data
    del data['temperature_data_raw'] # Delete raw data from data

    '''

    # SCRAP DUMMY DATA FOR FAST CALCULATION
    # -----------
    data['temperature_data'] = {}

    temp_y = np.zeros((365, 24))
    for day in range(365):
        temp_y[day] += randint(-5, 30)

    data['temperature_data'][9] = temp_y #np.zeros((365, 24)) #10 # DUMMY DATA WITH CONSTANT 10 DEGREES
    data['weather_stations'] = {}
    data['weather_stations'][9] = data['weather_stations_raw'][9]

    # ------------------------------------------
    # FUEL DATA
    # ------------------------------------------
    data['rs_fuel_raw_data_enduses'], data['rs_all_enduses'] = mf.read_csv_base_data_resid(data['path_dict']['path_rs_fuel_raw_data_enduses'])
    data['ss_fuel_raw_data_enduses'], data['all_service_sectors'], data['ss_all_enduses'] = mf.read_csv_base_data_service(data['path_dict']['path_ss_fuel_raw_data_enduses'], data['nr_of_fueltypes']) # Yearly end use data

    #ALL EXTERNAL ENDUSES?
    #ALL 

    # ------------------------------------------
    # RESIDENTIAL SECTOR
    # ------------------------------------------

    data['dwtype_lu'] = mf.read_csv_dict_no_header(data['path_dict']['path_dwtype_lu']) # Dwelling types lookup table

    # Technology shapes
    data['rs_shapes_heating_boilers_dh'] = mf.read_csv_float(data['path_dict']['path_hourly_gas_shape_resid']) # Boiler shape from Robert Sansom
    data['rs_shapes_heating_heat_pump_dh'] = mf.read_csv_float(data['path_dict']['path_hourly_gas_shape_hp']) # Heat pump shape
    data['rs_shapes_cooling_dh'] = mf.read_csv_float(data['path_dict']['path_shape_rs_cooling']) # ??

    #---
    #data['ss_shapes_heating_any_tech'] = 


    # ------------------------------------------
    # Read in raw fuel data of residential model
    # ------------------------------------------
    

    # Add fuel data of other model enduses to the fuel data table (E.g. ICT or wastewater) #TODO
    ###data = add_yearly_external_fuel_data(data, rs_fuel_raw_data_enduses) #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------
    # SERVICE SECTOR
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------

    # Read fuels

    # ---------------------------------------------------------------------------------------------
    # --- Generate load shapes
    # ---------------------------------------------------------------------------------------------
    # Otherwise already read out files are read in from txt files
    data = generate_data(data, data['rs_fuel_raw_data_enduses'], data['ss_fuel_raw_data_enduses'])

    # -- Read in load shapes from files (TPDO: Put in function)
    data = rs_collect_shapes_from_txts(data, data['path_dict']['path_rs_txt_shapes'])
    data = ss_collect_shapes_from_txts(data, data['path_dict']['path_ss_txt_shapes'])


    # -- From Carbon Trust (service sector data) read out enduse specific shapes --
    data['ss_all_tech_shapes_dh'] = {} 
    data['ss_all_tech_shapes_yd'] = {}

    for sector in data['ss_shapes_yd']:
        for enduse in data['ss_shapes_yd'][sector]:
            print("ENDU: " + str(enduse))
            data['ss_all_tech_shapes_dh'][enduse] = {}
            data['ss_all_tech_shapes_yd'][enduse] = {}

            # Add shapes
            data['ss_all_tech_shapes_dh'][enduse] = data['ss_shapes_dh'][sector][enduse]
            data['ss_all_tech_shapes_yd'][enduse] = data['ss_shapes_yd'][sector][enduse]
            break #only iterate first sector
    

   # ----------------------------------------
    # Convert units
    # ----------------------------------------
    # TODO: Check in what units external fuel data is provided
    '''for enduse in rs_fuel_raw_data_enduses:
        rs_fuel_raw_data_enduses[enduse] = mf.conversion_ktoe_gwh(rs_fuel_raw_data_enduses[enduse])
    #print("ENDUSES: " + str(rs_fuel_raw_data_enduses))
    '''

    # Residential Sector (TODO: REPLACE)
    data['rs_fuel_raw_data_enduses'] = data['rs_fuel_raw_data_enduses']
    data['ss_fuel_raw_data_enduses'] = data['ss_fuel_raw_data_enduses']

    # ---TESTS----------------------
    # Test if numer of fuel types is identical (Fuel lookup needs to have same dimension as end-use fuels)
    for end_use in data['rs_fuel_raw_data_enduses']:
        assert data['nr_of_fueltypes'] == len(data['rs_fuel_raw_data_enduses'][end_use]) # Fuel in fuel distionary does not correspond to len of input fuels

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
    for end_use in enduses:
        shape_peak_dh = df.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')))
        shape_non_peak_dh = df.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(end_use) + str("__") + str('shape_non_peak_dh') + str('.txt')))
        shape_peak_yd_factor = df.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
        shape_non_peak_yd = df.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))

        data['rs_shapes_dh'][end_use] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_dh': shape_non_peak_dh}
        data['rs_shapes_yd'][end_use] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

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

    # Read load shapes from txt files for enduses
    for sector in sectors:
        for end_use in enduses:
            joint_string_name = str(sector) + "__" + str(end_use)

            shape_peak_dh = df.read_txt_shape_peak_dh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_dh') + str('.txt')))
            shape_non_peak_dh = df.read_txt_shape_non_peak_yh(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_dh') + str('.txt')))
            shape_peak_yd_factor = df.read_txt_shape_peak_yd_factor(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
            shape_non_peak_yd = df.read_txt_shape_non_peak_yd(os.path.join(path_to_txts, str(joint_string_name) + str("__") + str('shape_non_peak_yd') + str('.txt')))

            data['ss_shapes_dh'][sector][end_use] = {'shape_peak_dh': shape_peak_dh, 'shape_non_peak_dh': shape_non_peak_dh}
            data['ss_shapes_yd'][sector][end_use] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

    return data

def generate_data(data, rs_raw_fuel, ss_raw_fuel):
    """Reads in raw data files and generates txt files

    HES data, Carbon Trust data area read in. This only needs to be run once

    Parameters
    -----------
    rs_raw_fuel : array
        Provided fuel input of rs
    ss_raw_fuel : array
        Provided fuel input of ss

    """
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
        'NOT_USED0': 7,
        'NOT_USED1':8,
        'NOT_USED2': 9,
        'NOT_USED3': 10
        }


    # HES data -- Generate generic load profiles (shapes) for all electricity appliances from HES data
    hes_data, hes_y_peak, _ = df.read_hes_data(data['path_dict']['path_bd_e_load_profiles'], len(appliances_HES_enduse_matching), data['day_type_lu'])

    # Assign read in raw data to the base year
    year_raw_values_hes = df.assign_hes_data_to_year(len(appliances_HES_enduse_matching), hes_data, data['base_yr'])

    # Load shape for all end_uses
    for end_use in rs_raw_fuel:
        print("Enduse:  " + str(end_use))

        if end_use not in appliances_HES_enduse_matching: #[:, 1]:
            print("Warning: The enduse {} is not defined in appliances_HES_enduse_matching, i.e. no generic shape is loades from HES data but enduse needs to be defined with technologies".format(end_use))
        else:
            # Generate HES load shapes
            shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd = df.get_hes_load_shapes(
                appliances_HES_enduse_matching,
                year_raw_values_hes,
                hes_y_peak,
                end_use
                )

            # Write .txt files
            df.create_txt_shapes(
                end_use,
                data['path_dict']['path_rs_txt_shapes'],
                shape_peak_dh,
                shape_non_peak_dh,
                shape_peak_yd_factor,
                shape_non_peak_yd,
                ""
                )

    # ==========================================
    # SERVICE MODEL - Load Carbon Trust data
    # ===========================================
    data['ss_shapes_dh'] = {}
    data['ss_shapes_yd'] = {}

    # Iterate sectors and read in shape
    for sector in data['all_service_sectors']:
        #print("Read in shape {}".format(sector))
        data['ss_shapes_dh'][sector] = {}
        data['ss_shapes_yd'][sector] = {}

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
        for end_use in ss_raw_fuel[sector]:
            #print("Enduse service: {}  in sector '{}'".format(end_use, sector))

            # Select shape depending on enduse
            if end_use in ['ss_water_heating', 'ss_space_heating', 'ss_other_gas']: #, 'ss_cooling_and_ventilation']:
                folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_gas')
            else:
                if end_use == 'ss_other_electricity':
                    folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\_all_elec')
                else:
                    folder_path = sector_folder_path_elec

            # -------------
            #TODO: SCRAP IMPROVE AND DOCUMENT (INSERT IF YOU WANT FAST VERSION)
            folder_path = os.path.join(data['local_data_path'], r'09_Carbon_Trust_advanced_metering_trial\Health')
            # -------------

            # Read in shape from carbon trust metering trial dataset #TODO: NOT SO FAST BECAUSE REad in multiple times
            shape_non_peak_dh, load_peak_shape_dh, shape_peak_yd_factor, shape_non_peak_yd = df.read_raw_carbon_trust_data(folder_path)

            # Assign shapes
            data['ss_shapes_dh'][sector][end_use] = {'shape_peak_dh': load_peak_shape_dh, 'shape_non_peak_dh': shape_non_peak_dh}
            data['ss_shapes_yd'][sector][end_use] = {'shape_peak_yd_factor': shape_peak_yd_factor, 'shape_non_peak_yd': shape_non_peak_yd}

            # Write shapes to txt
            joint_string_name = str(sector) + "__" + str(end_use)
            df.create_txt_shapes(joint_string_name, data['path_dict']['path_ss_txt_shapes'], load_peak_shape_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd, "")

    # ---------------------
    # Compare Jan and Jul
    # ---------------------
    #df.compare_jan_jul(main_dict_dayyear_absolute)

    # TODO: Add load shapes of external enduses (e.g. sewer treatment plants, )
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
