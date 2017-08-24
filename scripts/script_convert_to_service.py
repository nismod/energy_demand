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


pip install autopep8
autopep8 -i myfile.py # <- the -i flag makes the changes "in-place"
import time   fdf
#print("..TIME A: {}".format(time.time() - start)) 
'''
#path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-7])
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
    base_data = {}

    # ------------------------------------------------------------------
    # Execute only once before executing energy demand module for a year
    # ------------------------------------------------------------------
    instrument_profiler = True

    data_external = {}
    data_external['sim_param'] = {}
    data_external['sim_param']['base_yr'] = 2015
    data_external['sim_param']['end_yr'] = 2020
    data_external['sim_param']['sim_years_intervall'] = 5 # Make calculation only every X year
    data_external['sim_param']['sim_period'] = range(data_external['sim_param']['base_yr'], data_external['sim_param']['end_yr']  + 1, data_external['sim_param']['sim_years_intervall'])

    data_external['sim_param']['sim_period_yrs'] = int(data_external['sim_param']['end_yr']  + 1 - data_external['sim_param']['base_yr'])

    data_external['sim_param']['curr_yr'] = data_external['sim_param']['base_yr']
    data_external['sim_param']['list_dates'] = date_handling.fullyear_dates(
        start=date(data_external['sim_param']['base_yr'], 1, 1),
        end=date(data_external['sim_param']['base_yr'], 12, 31))


    # DUMMY DATA GENERATION----------------------
    #'''
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
    for i in range(data_external['sim_param']['base_yr'], data_external['sim_param']['end_yr'] + 1):
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
    #'''

    data_external['input_regions'] = regions
    data_external['population'] = pop_dummy
    data_external['reg_coordinates'] = coord_dummy
    data_external['ss_sector_floor_area_by'] = ss_floorarea_sector_by_dummy
    data_external['input_regions'] = regions

    base_data['mode_constrained'] = False #mode_constrained: True --> Technologies are defined in ED model, False: heat is delievered

    # ----------------------------------------
    # Model calculations outside main function
    # ----------------------------------------
    print("... start model calculations outside main function")

    # -------
    # In constrained mode, no technologies are defined in ED and heat demand is provided not for technologies
    # If unconstrained mode (False), heat demand is provided per technology
    # ---------
    # Copy external data into data container
    for dataset_name, external_data in data_external.items():
        base_data[str(dataset_name)] = external_data

    # Paths
    
    #path_main = os.path.join(os.path.dirname(__file__)[:-7]) #Remove 'energy_demand'
    path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-7])
    local_data_path = r'Y:\01-Data_NISMOD\data_energy_demand'

    #------------------------------
    # WRITE ASSUMPTIONS TO CSV
    #------------------------------
    path_assump_sim_param = os.path.join(path_main, r"data\data_scripts\assumptions_from_db\assumptions_sim_param.csv")
    write_data.write_out_sim_param(path_assump_sim_param, data_external['sim_param'])

    print("..finished reading out assumptions to csv")

    # ---------
    # Load data
    # ---------
    base_data['path_dict'] = data_loader.load_paths(path_main, local_data_path)
    base_data = data_loader.load_data_profiles(base_data)
    base_data['weather_stations'], base_data['temperature_data'] = data_loader.load_data_temperatures(
        base_data['path_dict']['path_scripts_data'])
    base_data = data_loader.load_data_tech_profiles(base_data)
    base_data = data_loader.load_data(base_data)

    # Load assumptions
    base_data['assumptions'] = assumptions.load_assumptions(base_data)

    #TODO: Prepare all dissagregated data for [region][sector][]
    base_data['driver_data'] = {}

    # ---------------------
    # SCRIPTS REPLACEMENTS
    # ---------------------
    # Change temperature data according to simple assumptions about climate change
    ### REPLACED base_data['temperature_data'] = enduse_scenario.change_temp_climate_change(base_data)
    base_data['temperature_data'] = read_weather_data.read_changed_weather_data_script_data(
        os.path.join(base_data['path_dict']['path_scripts_data'], 'weather_data_changed_climate.csv'),
        data_external['sim_param']['sim_period'])

    print("... sigmoid calculations")

    # RESIDENTIAL: Convert base year fuel input assumptions to energy service
    base_data['assumptions']['rs_service_tech_by_p'], base_data['assumptions']['rs_service_fueltype_tech_by_p'], base_data['assumptions']['rs_service_fueltype_by_p'] = fuel_service_switch.get_service_fueltype_tech(
        base_data['assumptions']['technology_list'],
        base_data['assumptions']['hybrid_technologies'],
        base_data['lu_fueltype'],
        base_data['assumptions']['rs_fuel_tech_p_by'],
        base_data['rs_fuel_raw_data_enduses'],
        base_data['assumptions']['technologies']
        )
