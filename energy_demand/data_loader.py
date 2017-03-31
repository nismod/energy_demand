"""Loads all necessary data"""
import os
import csv
#import unittest
import matplotlib.pyplot as plt
import numpy as np
import energy_demand.data_loader_functions as df
import energy_demand.main_functions as mf
import energy_demand.plot_functions as pf

# pylint: disable=I0011,C0321,C0301,C0103, C0325

def load_data(path_main, data_ext):
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

    # Data container
    data = {}
    data['path_main'] = path_main

    path_dict = {
        # Residential
        # -----------
        'path_main': path_main,
        'path_temp_txt': os.path.join(path_main, 'scenario_and_base_data/mean_temp_data'),
        'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
        'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
        'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances_HES.csv'),
        'path_fuel_type_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_fuel_types.csv'),
        'path_day_type_lu': os.path.join(path_main, 'residential_model/lookup_day_type.csv'),
        'path_bd_e_load_profiles': os.path.join(path_main, 'residential_model/HES_base_appliances_eletricity_load_profiles.csv'),
        'path_temp_2015': os.path.join(path_main, 'residential_model/SNCWV_YEAR_2015.csv'),
        'path_hourly_gas_shape_resid': os.path.join(path_main, 'residential_model/SANSOM_residential_gas_hourly_shape.csv'),
        #'path_dwtype_dist': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_distribution.csv'),
        'path_dwtype_age': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_floorarea.csv'),
        'path_reg_floorarea': os.path.join(path_main, 'residential_model/data_residential_model_floorarea.csv'),
        'path_reg_dw_nr': os.path.join(path_main, 'residential_model/data_residential_model_nr_dwellings.csv'),
        'path_data_residential_by_fuel_end_uses': os.path.join(path_main, 'residential_model/data_residential_by_fuel_end_uses.csv'),
        'path_lu_appliances_HES_matched': os.path.join(path_main, 'residential_model/lookup_appliances_HES_matched.csv'),
        'path_txt_shapes_resid': os.path.join(path_main, 'residential_model/txt_load_shapes')

        # Service
        # -----------
        #'path_temp_2015_service': os.path.join(path_main, 'service_model/CSV_YEAR_2015_service.csv')
        }

    data['path_dict'] = path_dict



    # ------------------------------------------
    # RESIDENTIAL SECTOR
    # ------------------------------------------

    # REGION LOOKUP: Generate region_lookup from input data #TODO: how to store data? (MAybe read in region_lookup from shape?)
    # TODO: Will change if data externally loaded---------------------------
    reg_lu_dict = {}
    for reg_name in data_ext['population'][data_ext['glob_var']['base_year']]:
        reg_lu_dict[reg_name] = reg_name
    data['reg_lu'] = reg_lu_dict

    #FLOOR_AREA_LOOKUP:
    reg_floor_area = {}
    for reg_name in data_ext['population'][data_ext['glob_var']['base_year']]:
        reg_lu_dict[reg_name] = 100000
    data['reg_floorarea'] = reg_lu_dict


    # Read in wheater data for different reiongs TODO #(days_per_month, 0.71, t_base, t_mean)
    data['temp_mean'] = mf.read_txt_t_base_by(data['path_dict']['path_temp_txt'], 2015)

    # Lookup data
    #data['reg_lu'] = mf.read_csv_dict_no_header(path_dict['path_pop_reg_lu'])                # Region lookup table
    data['dwtype_lu'] = mf.read_csv_dict_no_header(path_dict['path_dwtype_lu'])              # Dwelling types lookup table
    data['app_type_lu'] = mf.read_csv(path_dict['path_lookup_appliances'])                   # Appliances types lookup table
    data['fuel_type_lu'] = mf.read_csv_dict_no_header(path_dict['path_fuel_type_lu'])        # Fuel type lookup
    data['day_type_lu'] = mf.read_csv(path_dict['path_day_type_lu'])                         # Day type lookup

    #fuel_bd_data = read_csv_float(path_dict['path_base_data_fuel'])               # All disaggregated fuels for different regions
    data['path_temp_2015'] = mf.read_csv(path_dict['path_temp_2015'])                         # csv_temp_2015 #TODO: Delete because loaded in read_shp_heating_gas
    data['hourly_gas_shape'] = mf.read_csv_float(path_dict['path_hourly_gas_shape_resid'])         # Load hourly shape for gas from Robert Sansom #TODO: REmove because in read_shp_heating_gas

    #path_dwtype_age = read_csv_float(['path_dwtype_age'])
    #data['dwtype_distr'] = mf.read_csv_nested_dict(path_dict['path_dwtype_dist'])      # dISTRIBUTION of dwelligns base year #TODO: REMOVE AND ONLY LOAD YEAR 2015
    data['dwtype_age_distr'] = mf.read_csv_nested_dict(path_dict['path_dwtype_age'])
    #= mf.read_csv_dict(path_dict['path_dwtype_floorarea_dw_type'])
    #data['reg_floorarea'] = mf.read_csv_dict_no_header(path_dict['path_reg_floorarea'])
    data['reg_dw_nr'] = mf.read_csv_dict_no_header(path_dict['path_reg_dw_nr'])

    # load shapes
    data['dict_shp_enduse_h_resid'] = {}
    data['dict_shp_enduse_d_resid'] = {}

    # Data new approach
    data_residential_by_fuel_end_uses = mf.read_csv_base_data_resid(path_dict['path_data_residential_by_fuel_end_uses']) # Yearly end use data

    scrap = 0
    for enduse in data_residential_by_fuel_end_uses:
        scrap += np.sum(data_residential_by_fuel_end_uses[enduse])
    print("scrap FUELS READ IN FROM EXCEL: " + str(scrap))




    # Add the yearly fuel data of the external Wrapper to the enduses (RESIDENTIAL HERE) #TODO
    ###data = add_yearly_external_fuel_data(data, data_ext, data_residential_by_fuel_end_uses) #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE


    # Create dictionary with all enduses based on provided fuel data (after loading in external enduses)
    data['resid_enduses'] = {}
    if 'external_enduses_resid' in data_ext:
        for ext_enduse in data_ext['external_enduses_resid']: # Add external enduse
            data['resid_enduses'][ext_enduse] = ext_enduse

    for enduse in data_residential_by_fuel_end_uses: # Add resid enduses
        data['resid_enduses'][enduse] = enduse

    data['lu_appliances_HES_matched'] = mf.read_csv(path_dict['path_lu_appliances_HES_matched'])

    # SERVICE SECTOR
    # --------------
    #data['csv_temp_2015_service'] = mf.read_csv(path_dict['path_temp_2015_service']) # csv_temp_2015 #TODO: Dele
    data['dict_shp_enduse_h_service'] = {}
    data['dict_shp_enduse_d_service'] = {}

    # ----------------------------------------
    # --Convert loaded data into correct units
    # ----------------------------------------

    # Fuel residential
    for enduse in data_residential_by_fuel_end_uses:
        data_residential_by_fuel_end_uses[enduse] = mf.conversion_ktoe_gwh(data_residential_by_fuel_end_uses[enduse])

    data['data_residential_by_fuel_end_uses'] = data_residential_by_fuel_end_uses

    # --- Generate load_shapes ##TODO
    data = generate_data(data) # Otherwise already read out files are read in from txt files

    # -- Read in load shapes from files #TODO: Make that the correct txt depending on whetaer scenario are read in or out
    data = collect_shapes_from_txts(data)


    print("TEST A")
    print(data['dict_shp_enduse_d_resid']['heating']['shape_d_peak'])

    # ---TESTS----------------------
    # Test if numer of fuel types is identical (Fuel lookup needs to have same dimension as end-use fuels)
    for end_use in data['data_residential_by_fuel_end_uses']:
        assert len(data['fuel_type_lu']) == len(data['data_residential_by_fuel_end_uses'][end_use]) # Fuel in fuel distionary does not correspond to len of input fuels

    scrap = 0
    for enduse in data['data_residential_by_fuel_end_uses']:
        scrap += np.sum(data_residential_by_fuel_end_uses[enduse])
    print("scrap FUELS FINAL FOR OUT: " + str(scrap))

    return data

#run_data_collection = False #Scrap
# ---------------------------------------------------
# All pre-processed load shapes are read in from .txt files
# ---------------------------------------------------
def collect_shapes_from_txts(data):
    """Rread in load shapes from text without accesing raw files"""

    # ----------------------------------------------------------------------
    # RESIDENTIAL MODEL txt files
    # ----------------------------------------------------------------------
    # Iterate folders and get all enduse
    path_txt_shapes = data['path_dict']['path_txt_shapes_resid']
    all_csv_in_folder = os.listdir(path_txt_shapes)

    # Read all enduses from files
    enduses = []
    for file_name in all_csv_in_folder:
        enduse = file_name.split("__")[0] # two dashes because individual enduses may contain a single slash
        if enduse not in enduses:
            enduses.append(enduse)

    # Read load shapes from txt files
    for end_use in enduses:
        shape_h_peak = df.read_txt_shape_h_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_h_peak') + str('.txt')))
        shape_h_non_peak = df.read_txt_shape_h_non_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_h_non_peak') + str('.txt')))
        shape_d_peak = df.read_txt_shape_d_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_d_peak') + str('.txt')))
        shape_d_non_peak = df.read_txt_shape_d_non_peak(os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_d_non_peak') + str('.txt')))
        data['dict_shp_enduse_h_resid'][end_use] = {'shape_h_peak': shape_h_peak, 'shape_h_non_peak': shape_h_non_peak}
        data['dict_shp_enduse_d_resid'][end_use] = {'shape_d_peak': shape_d_peak, 'shape_d_non_peak': shape_d_non_peak}

    # ----------------------------------------------------------------------
    # SERVICE MODEL .txt files
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Industry MODEL .txt files
    # ----------------------------------------------------------------------

    return data

def generate_data(data):
    """This function loads all that which does not neet to be run every time"""

    base_year_load_data = 2015

    # ===========================================-
    # RESIDENTIAL MODEL
    # ===========================================
    path_txt_shapes = data['path_dict']['path_txt_shapes_resid']

    # HES data -- Generate generic load profiles (shapes) for all electricity appliances from HES data [ % ]
    hes_data, hes_y_peak, _ = df.read_hes_data(data)
    year_raw_values_hes = df.assign_hes_data_to_year(data, hes_data, base_year_load_data)

    # Load shape for all end_uses
    for end_use in data['data_residential_by_fuel_end_uses']:
        if end_use not in data['lu_appliances_HES_matched'][:, 1]: #Enduese not in HES data
            continue

        # Get HES load shapes
        shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.get_hes_end_uses_shape(data, year_raw_values_hes, hes_y_peak, _, end_use)
        df.create_txt_shapes(end_use, path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, "") # Write shapes to txt

    # Robert Sansom, Yearly peak from CSWV - Residential Gas demand, Daily shapes
    wheater_scenarios = ['actual'] #, 'max_cold', 'min_warm'# Different wheater scenarios to iterate #TODO: MAybe not necessary to read in indivdual shapes for different wheater scneario

    # Iterate wheater scenarios
    for wheater_scen in wheater_scenarios:
        shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.read_shp_heating_gas(data, 'residential', wheater_scen) # Composite Wheater Variable for residential gas heating
        df.create_txt_shapes('heating', path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, wheater_scen) # Write shapes to txt

    # TODO:
    # Add load shapes of external enduses (e.g. sewer treatment plants, )




    # ===========================================
    # SERVICE MODEL DATA GENERATION
    # ===========================================

    # ----------------------------
    # Service Gas demand, Daily shapes taken from Robert Sansom, Yearly peak from CSWV
    # ----------------------------
    #CSV Service
    #shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak = df.read_shp_heating_gas(data, 'service', 'actual') # Composite Wheater Variable for residential gas heating
    #df.create_txt_shapes('heating_service', path_txt_shapes, shape_h_peak, shape_h_non_peak, shape_d_peak, shape_d_non_peak, _) # Write shapes to txt
    # ---------------------
    # Load Carbon Trust data - electricity for non-residential
    # ---------------------


    # ENDUSE XY
    #folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\_all_elec' #Community _OWN_SEWAGE Education
    #out_dict_av, out_dict_not_av, hourly_shape_of_maximum_days, main_dict_dayyear_absolute = df.read_raw_carbon_trust_data(data, folder_path)

    '''

    # Percentages for every day:
    jan_yearday = range(0, 30)
    jul_yearday = range(181, 212)
    jan = {k: [] for k in range(24)}
    jul = {k: [] for k in range(24)}

    # Read out for the whole months of jan and ful
    for day in main_dict_dayyear_absolute:
        for h in main_dict_dayyear_absolute[day]:
            if day in jan_yearday:
                jan[h].append(main_dict_dayyear_absolute[day][h])
            if day in jul_yearday:
                jul[h].append(main_dict_dayyear_absolute[day][h])
    #print(jan)
    # Average the montly entries
    for i in jan:
        print("Nr of datapoints in Jan for hour: " + str(len(jan[i])))
        jan[i] = sum(jan[i]) / len(jan[i])

    for i in jul:
        print("Nr of datapoints in Jul for hour:" + str(len(jul[i])))
        jul[i] = sum(jul[i]) / len(jul[i])

    # Test HEATING_ELEC SHARE DIFFERENCE JAN and JUN [daytype][_month][_hr]
    jan = np.array(list(jan.items())) #convert to array
    jul = np.array(list(jul.items())) #convert to array
    jul_percent_of_jan = (100/jan[:, 1]) * jul[:, 1]

    x_values = range(24)
    y_values = list(jan[:, 1]) # to get percentages
    plt.plot(x_values, list(jan[:, 1]), label="Jan")
    plt.plot(x_values, list(jul[:, 1]), label="Jul")
    plt.plot(x_values, list(jul_percent_of_jan), label="% dif of Jan - Jul")
    plt.legend()
    plt.show()

    print("ARRA")
    print(np.sum(jan[:, 1]))
    print(np.sum(jul[:, 1]))
    #print(jan)
    #print("  --  ")
    #print(jul)
    #print("---hh--")

    #--- if JAn = 100%
    jul_percent_of_jan = (100/jan[:, 1]) * jul[:, 1]
    for h ,i in enumerate(jul_percent_of_jan):
        print("h: " + str(h) + "  %" + str(i) + "   Diff: " + str(100-i))

    pf.plot_load_shape_d_non_resid(jan)
    print("TEST: " + str(jan-jul))

    # Read in CWV for non-residential

    # Get yearly profiles
    enduse = 'WHATEVERENDUSE'
    year_data = df.assign_carbon_trust_data_to_year(data, enduse, out_dict_av, base_year_load_data) #TODO: out_dict_av is percentages of day sum up to one

    #out_dict_av [daytype, month, ...] ---> Calculate yearly profile with averaged monthly profiles
    '''
    # ENDUSE XY
    #folder_path = r'C:\Users\cenv0553\Dropbox\00-Office_oxford\07-Data\09_Carbon_Trust_advanced_metering_trial_(owen)\__OWN_SEWAGE' #Community _OWN_SEWAGE

    return data
