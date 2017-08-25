'''
Energy Demand Model
=================

Contains all calculation steps necessary to run the
energy demand module.

The model has been developped within the MISTRAL
project. A previous model has been developped within
NISMOD by Pranab et al..(MOREINFO) HIRE develops this model
further into a high temporal and spatial model.abs

Key contributers are:
    - Sven Eggimann
    - Nick Eyre
    -

    note,tip,warning,

More information can be found here:

    - Eggimann et al. (2018): Paper blablabla

build, git, docs, .eggs, .coverage, .cache, hire, scripts, data

pip install autopep8
autopep8 -i myfile.py # <- the -i flag makes the changes "in-place"
import time   fdf
#print("..TIME A: {}".format(time.time() - start)) 

TODO: REMOVE HEAT BOILER
'''
import os
import sys
from datetime import date
import numpy as np
import energy_demand.energy_model as energy_model
from energy_demand.assumptions import assumptions
from energy_demand.read_write import data_loader
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.disaggregation import national_disaggregation
from energy_demand.building_stock import building_stock_generator
from energy_demand.technologies import diffusion_technologies as diffusion
from energy_demand.technologies import fuel_service_switch
from energy_demand.calculations import enduse_scenario
from energy_demand.basic import testing_functions as testing
from energy_demand.basic import date_handling
from energy_demand.validation import lad_validation
from energy_demand.validation import elec_national_data
from energy_demand.plotting import plotting_results
from energy_demand.read_write import read_weather_data
print("Start Energy Demand Model with python version: " + str(sys.version))
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
#!python3.6

def energy_demand_model(data):
    """Main function of energy demand model to calculate yearly demand

    Parameters
    ----------
    data : dict
        Data container

    Returns
    -------
    result_dict : dict
        A nested dictionary containing all data for energy supply model with
        timesteps for every hour in a year.
        [fuel_type : region : timestep]
    model_run_object : dict
        Object of a yearly model run

    Note
    ----
    This function is executed in the wrapper

    Quetsiosn for Tom
    ----------------
    - Cluster?
    - scripts in ed?
    - path rel/abs
    - nested scripts
    """

    # -------------------------
    # Model main function
    # --------------------------
    fuel_in, fuel_in_elec, _ = testing.test_function_fuel_sum(data)

    # Add all region instances as an attribute (region name) into the class `EnergyModel`
    model_run_object = energy_model.EnergyModel(
        region_names=data['lu_reg'],
        data=data,
    )

    # ----------------------------
    # Summing
    # ----------------------------
    fueltot = model_run_object.sum_uk_fueltypes_enduses_y # Total fuel of country

    print("================================================")
    print("Number of regions    " + str(len(data['lu_reg'])))
    print("Fuel input:          " + str(fuel_in))
    print("Fuel output:         " + str(fueltot))
    print("FUEL DIFFERENCE:     " + str(round((fueltot - fuel_in), 4)))
    print("elec fuel in:        " + str(fuel_in_elec))
    print("elec fuel out:       " + str(np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2])))
    print("ele fueld diff:      " + str(round(fuel_in_elec - np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2]), 4))) #ithout transport
    print("================================================")
    for fff in range(8):
        print("FF: " + str(np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[fff])))
    # # --- Write to csv and YAML Convert data according to region and fueltype
    #result_dict = read_data.convert_out_format_es(data, model_run_object, ['rs_submodel', 'ss_submodel', 'is_submodel', 'ts_submodel'])
    ###write_data.write_final_result(data, result_dict, model_run_object.curr_yr, data['lu_reg'], False)

    print("...finished energy demand model simulation")
    return _, model_run_object

# Run
if __name__ == "__main__":
    print('start_main')

    # ------------------------------------------------------------------
    # Execute only once before executing energy demand module for a year
    # ------------------------------------------------------------------
    instrument_profiler = True

    path_main = os.path.dirname(os.path.abspath(__file__))[:-13] #Remove 'energy_demand'
    print("PATHMAIN: " + str(path_main))
    local_data_path = r'Y:\01-Data_NISMOD\data_energy_demand'
    base_data = data_loader.load_paths(path_main, local_data_path)

    # Load data
    base_data = data_loader.load_fuels(base_data)
    base_data = data_loader.load_data_tech_profiles(base_data)
    base_data['assumptions'] = assumptions.load_assumptions(base_data)


    # DUMMY DATA GENERATION----------------------
    base_data['all_sectors'] = ['community_arts_leisure', 'education', 'emergency_services', 'health', 'hospitality', 'military', 'offices', 'retail', 'storage', 'other']

    # Load dummy LAC and pop
    dummy_pop_geocodes = data_loader.load_LAC_geocodes_info()

    regions = {}
    coord_dummy = {}
    pop_dummy = {}
    rs_floorarea = {}
    ss_floorarea_sector_by_dummy = {}

    for geo_code, values in dummy_pop_geocodes.items():
        regions[geo_code] = values['label'] # Label for region
        coord_dummy[geo_code] = {'longitude': values['Y_cor'], 'latitude': values['X_cor']}

    # Population
    for i in range(base_data['sim_param']['base_yr'], base_data['sim_param']['end_yr'] + 1):
        _data = {}
        for reg_geocode in regions:
            _data[reg_geocode] = dummy_pop_geocodes[reg_geocode]['POP_JOIN']
        pop_dummy[i] = _data

    # Residenital floor area
    for region_geocode in regions:
        rs_floorarea[region_geocode] = pop_dummy[2015][region_geocode] #USE FLOOR AREA

    # Dummy flor area
    for region_geocode in regions:
        ss_floorarea_sector_by_dummy[region_geocode] = {}
        for sector in base_data['all_sectors']:
            ss_floorarea_sector_by_dummy[region_geocode][sector] = pop_dummy[2015][region_geocode]

    base_data['rs_floorarea'] = rs_floorarea
    base_data['ss_floorarea'] = ss_floorarea_sector_by_dummy

    # -----------------------------
    # Read in floor area of all regions and store in dict
    # TODO: REPLACE WITH Newcastle if ready
    # -----------------------------
    #REPLACE: Generate region_lookup from input data (Maybe read in region_lookup from shape?)
    base_data['lu_reg'] = {} #TODO: DO NOT READ REGIONS FROM POP BUT DIRECTLY
    for region_name in regions:
        base_data['lu_reg'][region_name] = region_name

    #TODO: FLOOR_AREA_LOOKUP:
    base_data['reg_floorarea_resid'] = {}
    for region_name in pop_dummy[base_data['sim_param']['base_yr']]:
        base_data['reg_floorarea_resid'][region_name] = 100000
    #'''

    base_data['input_regions'] = regions
    base_data['population'] = pop_dummy
    base_data['reg_coordinates'] = coord_dummy
    base_data['ss_sector_floor_area_by'] = ss_floorarea_sector_by_dummy


    #------------------------------
    # WRITE ASSUMPTIONS TO CSV
    #------------------------------
    '''write_data.write_out_sim_param(
        os.path.join(path_main,'data', 'data_scripts', 'assumptions_from_db', 'assumptions_sim_param.csv'),
            base_data['sim_param'])'''

    print("..finished reading out assumptions to csv")

    # ------------------------------------------------------
    # Load data and assumptions
    # ------------------------------------------------------
    
    
    base_data = data_loader.load_data_profiles(base_data)
    base_data['weather_stations'], base_data['temperature_data'] = data_loader.load_data_temperatures(
        os.path.join(base_data['path_dict']['path_scripts_data'], 'weather_data')
        )

    

    #TODO: Prepare all dissagregated data for [region][sector][]
    base_data['driver_data'] = {}

    # ---------------------
    # Load data from script calculations
    # ---------------------
    #read_script_data()
    print("... sigmoid calculations")

    # Read in Services (from script data)
    base_data['assumptions']['rs_service_tech_by_p'] = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_tech_by_p.csv'))
    base_data['assumptions']['ss_service_tech_by_p'] = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_tech_by_p.csv'))
    base_data['assumptions']['is_service_tech_by_p'] = read_data.read_service_data_service_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_tech_by_p.csv'))

    base_data['assumptions']['rs_service_fueltype_by_p'] = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_fueltype_by_p.csv'))
    base_data['assumptions']['ss_service_fueltype_by_p'] = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_fueltype_by_p.csv'))
    base_data['assumptions']['is_service_fueltype_by_p'] = read_data.read_service_fueltype_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_fueltype_by_p.csv'))
    
    base_data['assumptions']['rs_service_fueltype_tech_by_p'] = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'rs_service_fueltype_tech_by_p.csv'))
    base_data['assumptions']['ss_service_fueltype_tech_by_p'] = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'ss_service_fueltype_tech_by_p.csv'))
    base_data['assumptions']['is_service_fueltype_tech_by_p'] = read_data.read_service_fueltype_tech_by_p(os.path.join(base_data['path_dict']['path_scripts_data'], 'services', 'is_service_fueltype_tech_by_p.csv'))

    # Read technologies with more, less and constant service based on service switch assumptions (from script data)
    base_data['assumptions']['rs_tech_increased_service'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'rs_tech_increased_service.csv'))
    base_data['assumptions']['ss_tech_increased_service'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'ss_tech_increased_service.csv'))
    base_data['assumptions']['is_tech_increased_service'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'is_tech_increased_service.csv'))

    base_data['assumptions']['rs_tech_decreased_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'rs_tech_increased_service.csv'))
    base_data['assumptions']['ss_tech_decreased_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'ss_tech_increased_service.csv'))
    base_data['assumptions']['is_tech_decreased_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'is_tech_increased_service.csv'))

    base_data['assumptions']['rs_tech_constant_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'rs_tech_increased_service.csv'))
    base_data['assumptions']['ss_tech_constant_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'ss_tech_increased_service.csv'))
    base_data['assumptions']['is_tech_constant_share'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'is_tech_increased_service.csv'))

    # Read in sigmoid technology diffusion parameters (from script data)
    base_data['assumptions']['rs_sig_param_tech'] = read_data.read_sig_param_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'rs_sig_param_tech.csv'))
    base_data['assumptions']['ss_sig_param_tech'] = read_data.read_sig_param_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'ss_sig_param_tech.csv'))
    base_data['assumptions']['is_sig_param_tech'] = read_data.read_sig_param_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'is_sig_param_tech.csv'))

    # Read in installed technologies (from script data)
    base_data['assumptions']['rs_installed_tech'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'rs_installed_tech.csv'))
    base_data['assumptions']['ss_installed_tech'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'ss_installed_tech.csv'))
    base_data['assumptions']['is_installed_tech'] = read_data.read_installed_tech(os.path.join(base_data['path_dict']['path_scripts_data'], 'is_installed_tech.csv'))

    # Read data after apply climate change (from script data)
    base_data['temperature_data'] = read_weather_data.read_changed_weather_data_script_data(
        os.path.join(base_data['path_dict']['path_scripts_data'], 'weather_data', 'weather_data_changed_climate.csv'),
        base_data['sim_param']['sim_period'])

    # Write out txt file with service shares for each technology per enduse
    ##write_data.write_out_txt(base_data['path_dict']['path_txt_service_tech_by_p'], base_data['assumptions']['rs_service_tech_by_p'])
    #print("... a file has been generated which shows the shares of each technology per enduse")

    # ---------------------------------------------
    # Disaggregate national data into regional data
    # ---------------------------------------------
    base_data = national_disaggregation.disaggregate_base_demand(base_data)

    # ---------------------------------------------
    # Generate building stocks over whole simulation period
    # ---------------------------------------------
    base_data['rs_dw_stock'] = building_stock_generator.rs_build_stock(base_data)
    base_data['ss_dw_stock'] = building_stock_generator.ss_build_stock(base_data)

    # If several years are run:
    results_every_year = []

    for sim_yr in base_data['sim_param']['sim_period']:
        base_data['sim_param']['curr_yr'] = sim_yr

        print("-------------------------- ")
        print("SIM RUN:  " + str(sim_yr))
        print("-------------------------- ")

        #-------------PROFILER
        if instrument_profiler:
            from pyinstrument import Profiler
            profiler = Profiler(use_signal=False)
            profiler.start()

        _, model_run_object = energy_demand_model(base_data)

        if instrument_profiler:
            profiler.stop()
            print(profiler.output_text(unicode=True, color=True))

        results_every_year.append(model_run_object)

        # ---------------------------------------------------
        # Validation of national electrictiy demand for base year
        # ---------------------------------------------------
        #'''
        winter_week = list(range(date_handling.convert_date_to_yearday(2015, 1, 12), date_handling.convert_date_to_yearday(2015, 1, 19))) #Jan
        spring_week = list(range(date_handling.convert_date_to_yearday(2015, 5, 11), date_handling.convert_date_to_yearday(2015, 5, 18))) #May
        summer_week = list(range(date_handling.convert_date_to_yearday(2015, 7, 13), date_handling.convert_date_to_yearday(2015, 7, 20))) #Jul
        #spring_week = list(range(date_handling.convert_date_to_yearday(2015, 5, 18), date_handling.convert_date_to_yearday(2015, 5, 26))) #May
        #summer_week = list(range(date_handling.convert_date_to_yearday(2015, 7, 20), date_handling.convert_date_to_yearday(2015, 7, 28))) #Jul
        autumn_week = list(range(date_handling.convert_date_to_yearday(2015, 10, 12), date_handling.convert_date_to_yearday(2015, 10, 19))) #Oct

        days_to_plot = winter_week + spring_week + summer_week + autumn_week
        days_to_plot_full_year = list(range(0, 365))

        # ---------------------------------------------------------------------------------------------
        # Compare total gas and electrictiy shape with Elexon Data for Base year for different regions
        # ---------------------------------------------------------------------------------------------
        validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO = elec_national_data.read_raw_elec_2015_data(base_data['path_dict']['folder_validation_national_elec_data'])

        print("Loaded validation data elec demand. ND:  {}   TSD: {}".format(np.sum(validation_elec_data_2015_INDO), np.sum(validation_elec_data_2015_ITSDO)))
        print("--ECUK Elec_demand  {} ".format(np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2])))
        print("--ECUK Gas Demand   {} ".format(np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[1])))
        diff_factor_TD_ECUK_Input = (1.0 / np.sum(validation_elec_data_2015_INDO)) * np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2]) # 1.021627962194478
        print("FACTOR: " + str(diff_factor_TD_ECUK_Input))

        INDO_factoreddata = diff_factor_TD_ECUK_Input * validation_elec_data_2015_INDO
        print("CORRECTED DEMAND:  {} ".format(np.sum(INDO_factoreddata)))

        #GET SPECIFIC REGION

        # Compare different models
        elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2], 'all_submodels', days_to_plot_full_year)
        elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2], 'all_submodels', days_to_plot)
        elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.rs_sum_uk_specfuelype_enduses_y[2], 'rs_model', days_to_plot)
        #elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.ss_sum_uk_specfuelype_enduses_y[2], 'ss_model', days_to_plot)
        #elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.is_sum_uk_specfuelype_enduses_y[2], 'is_model', days_to_plot)
        #elec_national_data.compare_results(validation_elec_data_2015_INDO, validation_elec_data_2015_ITSDO, INDO_factoreddata, model_run_object.ts_sum_uk_specfuelype_enduses_y[2], 'ts_model', days_to_plot)

        print("FUEL gwh TOTAL  validation_elec_data_2015_INDO:  {} validation_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(validation_elec_data_2015_INDO), np.sum(validation_elec_data_2015_ITSDO), np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2])))
        print("FUEL ktoe TOTAL  validation_elec_data_2015_INDO: {} validation_elec_data_2015_ITSDO: {}  MODELLED DATA:  {} ".format(np.sum(validation_elec_data_2015_INDO)/11.63, np.sum(validation_elec_data_2015_ITSDO)/11.63, np.sum(model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2])/11.63))

        # ---------------------------------------------------
        # Validation of spatial disaggregation
        # ---------------------------------------------------
        lad_infos_shapefile = data_loader.load_LAC_geocodes_info()
        lad_validation.compare_lad_regions(lad_infos_shapefile, model_run_object, base_data['nr_of_fueltypes'], base_data['lu_fueltype'], base_data['lu_reg'])

        # ---------------------------------------------------
        # Validation of national electrictiy demand for peak
        # ---------------------------------------------------
        print("...compare peak from data")
        peak_month = 2 #Feb
        peak_day = 18 #Day
        elec_national_data.compare_peak(
            validation_elec_data_2015_INDO,
            model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[peak_month][peak_day]
            )

        print("...compare peak from max peak factors")
        elec_national_data.compare_peak(
            validation_elec_data_2015_INDO,
            model_run_object.peak_all_models_all_enduses_fueltype[2]) #for electricity only

        # ---------------------------------------------------
        # Validate boxplots for every hour
        # ---------------------------------------------------
        elec_national_data.compare_results_hour_boxplots(
            validation_elec_data_2015_INDO,
            model_run_object.all_submodels_sum_uk_specfuelype_enduses_y[2])

    # ------------------------------
    # Plotting
    # ------------------------------
    # Plot load factors
    ##pf.plot_load_curves_fueltype(results_every_year, base_data)

    # Plot total fuel (y) per enduse
    plotting_results.plot_stacked_Country_end_use(base_data, results_every_year, base_data['rs_all_enduses'], 'rs_tot_fuel_y_enduse_specific_h')
    plotting_results.plot_stacked_Country_end_use(base_data, results_every_year, base_data['ss_all_enduses'], 'ss_tot_fuel_enduse_specific_h')

    # Plot total fuel (y) per fueltype
    plotting_results.plot_fuels_tot_all_enduses(results_every_year, base_data, 'rs_tot_fuels_all_enduses_y')
    plotting_results.plot_fuels_tot_all_enduses(results_every_year, base_data, 'rs_tot_fuels_all_enduses_y')

    # Plot peak demand (h) per fueltype
    plotting_results.plot_fuels_peak_hour(results_every_year, base_data, 'rs_tot_fuel_y_max_allenduse_fueltyp')
    plotting_results.plot_fuels_peak_hour(results_every_year, base_data, 'ss_tot_fuel_y_max_allenduse_fueltyp')

    # Plot a full week
    plotting_results.plot_fuels_tot_all_enduses_week(results_every_year, base_data, 'rs_tot_fuels_all_enduses_y')
    plotting_results.plot_fuels_tot_all_enduses_week(results_every_year, base_data, 'rs_tot_fuels_all_enduses_y')

    # Plot all enduses
    plotting_results.plot_stacked_Country_end_use(base_data, results_every_year, base_data['rs_all_enduses'], 'all_models_tot_fuel_y_enduse_specific_h')

    print("Finished running Energy Demand Model")

'''
def get_scenario_drivers(all_potential_scenario_drivers):
    """Prepare data for scenario drivers
    """
    reg_scenario_drivers[region_name][self.base_yr][scenario_driver]
    reg_scenario_drivers = {}

    for driver in all_potential_scenario_drivers:
            
        if driver == 'GVA':
                reg_scenario_drivers[driver]
        #if driver ==
    #data['driver_data']
    return reg_scenario_drivers
'''
