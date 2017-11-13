"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
import configparser
from datetime import date
from collections import defaultdict
from smif.model.sector_model import SectorModel
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.cli import run_model
from energy_demand.dwelling_stock import dw_stock
from energy_demand.read_write import read_data
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import base_assumptions
from energy_demand.basic import date_prop
from pkg_resources import Requirement, resource_filename

# must match smif project name for Local Authority Districts
REGION_SET_NAME = 'lad_2016' #TODO
NR_OF_MODELLEd_REGIONS = 10

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """

    def array_to_dict(self, input_array):
        """Convert array to dict

        Arguments
        ---------
        input_array : numpy.ndarray
            timesteps, regions, interval

        Returns
        -------
        output_dict : dict
            timesteps, region, interval

        """
        output_dict = defaultdict(dict)
        for t_idx, timestep in enumerate(self.timesteps):
            for r_idx, region in enumerate(self.get_region_names(REGION_SET_NAME)):
                output_dict[timestep][region] = input_array[t_idx, r_idx, 0]

        return output_dict

    def before_model_run(self):
        """Runs prior to any ``simulate()`` step

        Writes scenario data out into the scenario files

        Saves useful data into the ``self.user_data`` dictionary for access
        in the ``simulate()`` method

        Data is accessed using the `get_scenario_data()` method is provided
        as a numpy array with the dimensions timesteps-by-regions-by-intervals.

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        data = {}

        data['print_criteria'] = False

        # -----------------------------
        # Paths
        # -----------------------------
        path_main = resource_filename(Requirement.parse("energy_demand"), "")

        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        self.user_data['data_path'] = config['PATHS']['path_local_data']
        self.processed_path = config['PATHS']['path_processed_data']
        self.result_path = config['PATHS']['path_result_data']

        # Add to data container for scenario initialisation
        data['paths'] = data_loader.load_paths(path_main)

        data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])

        # ---------------------
        # Simulation parameters
        # ---------------------
        data['sim_param'] = {}
        data['sim_param']['base_yr'] = 2015 #REPLACE
        data['sim_param']['curr_yr'] = data['sim_param']['base_yr']
        self.user_data['base_yr'] = data['sim_param']['base_yr']

        # -----------------------------
        # Region related informatiom
        # -----------------------------
        data['lu_reg'] = self.get_region_names(REGION_SET_NAME)
        #data['reg_coord'] = regions.get_region_centroids(REGION_SET_NAME) #TO BE IMPLEMENTED BY THE SMIF GUYS
        data['reg_coord'] = data_loader.get_dummy_coord_region(data['lu_reg'], data['local_paths']) #REMOVE IF CORRECT DATA IN

        # SCRAP REMOVE: ONLY SELECT NR OF MODELLED REGIONS
        data['lu_reg'] = data['lu_reg'][:NR_OF_MODELLEd_REGIONS]
        print("Modelled for a nuamer of regions: " + str(len(data['lu_reg'])))

        data = data_loader.dummy_data_generation(data, data['lu_reg'])

        # -----------------------------
        # Obtain external scenario data
        # -----------------------------
        # Population
        pop_array = self.get_scenario_data('population') #maybe only cy and by data
        data['population'] = self.array_to_dict(pop_array['population'])

        # GVA
        gva_array = self.get_scenario_data('gva')
        data['gva'] = self.array_to_dict(gva_array['gva'])

        #Scenario data
        data['scenario_data'] = {
            'gva': data['gva'],
            'population': data['population']}

        '''# Building stock related data

        # --Residential Floor Area
        floor_array = self.get_scenario_data('floor_area_rs_detached_pre1930')
        floor_array = self.get_scenario_data('floor_area_rs_detached_1930-1950')
        floor_array = self.get_scenario_data('floor_area_rs_detached_1950-1970')
        floor_array = self.get_scenario_data('floor_area_rs_detached_1950-1990')
        floor_array = self.get_scenario_data('floor_area_rs_detached_newer2010')

        floor_array = self.get_scenario_data('floor_area_rs_semi_detached_pre1930')
        floor_array = self.get_scenario_data('floor_area_rs_semi_detached_1930-1950')
        floor_array = self.get_scenario_data('floor_area_rs_semi_detached_1950-1970')
        floor_array = self.get_scenario_data('floor_area_rs_semi_detached_1950-1990')
        floor_array = self.get_scenario_data('floor_area_rs_semi_detached_newer2010')

        floor_array = self.get_scenario_data('floor_area_rs_terrassed_pre1930')
        floor_array = self.get_scenario_data('floor_area_rs_terrassed_1930-1950')
        floor_array = self.get_scenario_data('floor_area_rs_terrassed_1950-1970')
        floor_array = self.get_scenario_data('floor_area_rs_terrassed_1950-1990')
        floor_array = self.get_scenario_data('floor_area_rs_terrassed_newer2010')

        floor_array = self.get_scenario_data('floor_area_rs_flat_pre1930')
        floor_array = self.get_scenario_data('floor_area_rs_flat_1930-1950')
        floor_array = self.get_scenario_data('floor_area_rs_flat_1950-1970')
        floor_array = self.get_scenario_data('floor_area_rs_flat_1950-1990')
        floor_array = self.get_scenario_data('floor_area_rs_flat_newer2010')

        floor_array = self.get_scenario_data('floor_area_rs_bungalow_pre1930')
        floor_array = self.get_scenario_data('floor_area_rs_bungalow_1930-1950')
        floor_array = self.get_scenario_data('floor_area_rs_bungalow_1950-1970')
        floor_array = self.get_scenario_data('floor_area_rs_bungalow_1950-1990')
        floor_array = self.get_scenario_data('floor_area_rs_bungalow_newer2010')

        # --Service
        floor_array = self.get_scenario_data('floor_area_ss_community_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_education_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_emergency_pre1930') #not provided, calc % of rest
        floor_array = self.get_scenario_data('floor_area_ss_health_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_hospitality_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_military_pre1930') #not provided, calc % of rest
        floor_array = self.get_scenario_data('floor_area_ss_offices_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_retail_pre1930')
        floor_array = self.get_scenario_data('floor_area_ss_storage_pre1930') #not provided, calc % of rest
        floor_array = self.get_scenario_data('floor_area_ss_rest_pre1930') # assign 
        #...

        data['rs_floorarea'] = self.array_to_dict(floor_array)
        #data['ss_floorarea'] = self.array_to_dict(floor_array)
        data['reg_floorarea_resid'] = self.array_to_dict(floor_array)
        #self.user_data['ss_floorarea'] = self.array_to_dict(floor_array)
        self.user_data['reg_floorarea_resid'] = self.array_to_dict(floor_array)'''

        # ---------------------
        # Energy demand specific input which needs to be read in
        # ---------------------
        data['lookups'] = data_loader.load_basic_lookups()
        data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
        
        # Assumptions
        data['assumptions'] = base_assumptions.load_non_parameter_assumptions(data['sim_param']['base_yr'], data['paths'])
        base_assumptions.load_assumptions(data['paths'], data['assumptions'], data['enduses'], data['lookups'], data['fuels'], data['sim_param'])
        data['assumptions'] = read_data.read_param_yaml(data['paths']['yaml_parameters'])

        data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

        data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])
        
        # ------------------------
        # Pass along to simulate()
        # ------------------------
        self.user_data['temp_data'] = data['temp_data']
        self.user_data['gva'] = self.array_to_dict(gva_array['gva'])
        self.user_data['population'] = self.array_to_dict(pop_array['population'])

        # --------------------
        # Initialise scenario
        # --------------------
        self.user_data['fts_cont'], self.user_data['sgs_cont'], self.user_data['sd_cont'] = scenario_initalisation(
            self.user_data['data_path'], data)

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, timestep, data=None):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        timestep : int
            The name of the current timestep
        data : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Notes
        -----
        1. Get scenario data

        Population data is required as a nested dict::

            data[year][region_geocode]

        GVA is the same::

            data[year][region_geocode]

        Floor area::

            data[year][region_geoode][sector]

        2. Run initialise scenarios
        3. For each timestep, run the model

        Data is provided to these methods in the format::

            {'parameter_name': value_array}

        where ``value_array`` is a regions-by-intervals numpy array.

        """
        data = {}

        path_main = resource_filename(Requirement.parse("energy_demand"), "")

        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        # Go two levels down
        path, folder = os.path.split(path_main)
        path_nismod, folder = os.path.split(path)
        self.user_data['data_path'] = os.path.join(path_nismod, 'data_energy_demand')

        # --------------------
        # Simulation parameters
        # --------------------
        data['sim_param'] = {}
        data['sim_param']['base_yr'] = self.user_data['base_yr'] # Base year definition
        data['sim_param']['curr_yr'] = timestep                  # Read in current year from smif
        data['sim_param']['simulated_yrs'] = self.timesteps      # Read in all simulated years from smif

        # ---------
        # Scenario data
        # ---------
        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])

        data['print_criteria'] = False
        data['scenario_data'] = {
            'gva': self.user_data['gva'],
            'population':  self.user_data['population']}

        # ---------
        # Replace data in data with data provided from wrapper or before_model_run
        # Write data from smif to data container from energy demand model
        # ---------
        data['lu_reg'] = self.get_region_names(REGION_SET_NAME)
        #data['reg_coord'] = regions.get_region_centroids(REGION_SET_NAME) #TO BE IMPLEMENTED BY THE SMIF GUYS
        data['lu_reg'] = data['lu_reg'][:NR_OF_MODELLEd_REGIONS]
        print("Modelled for a nuamer of regions: " + str(len(data['lu_reg'])))

        #REPLACE BY SMIF INPUT
        data['reg_coord'] = data_loader.get_dummy_coord_region(data['lu_reg'], data['local_paths'])

        data['lookups'] = data_loader.load_basic_lookups()
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

        # ED related stuff

        #Assumptions
        data['assumptions'] = base_assumptions.load_non_parameter_assumptions(data['sim_param']['base_yr'], data['paths'])
        base_assumptions.load_assumptions(data['paths'], data['assumptions'], data['enduses'], data['lookups'], data['fuels'], data['sim_param'])
        data['assumptions'] = read_data.read_param_yaml(data['paths']['yaml_parameters'])
        
        data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

        data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])
        data['weather_stations'], _ = data_loader.load_temp_data(data['local_paths'])

        # Update: Necessary updates after external data definition
        data['assumptions']['technologies'] = base_assumptions.update_assumptions(data['assumptions']['technologies'], data['assumptions']['eff_achieving_factor']['factor_achieved']) #Maybe write s_script

        # -----------------------
        # Load data from scripts (replacing #data = read_data.load_script_data(data))
        # -----------------------
        # fts_cont['ss_service_tech_by_p'], fts_cont['ss_service_fueltype_tech_by_p'], fts_cont['ss_service_fueltype_by_p']
        # Insert from script calculations which are stored in memory
        data['temp_data'] = self.user_data['temp_data']
        data['assumptions']['rs_service_tech_by_p'] = self.user_data['fts_cont']['rs_service_tech_by_p']
        data['assumptions']['ss_service_tech_by_p'] = self.user_data['fts_cont']['ss_service_tech_by_p']
        data['assumptions']['is_service_tech_by_p'] = self.user_data['fts_cont']['is_service_tech_by_p']
        data['assumptions']['rs_service_fueltype_by_p'] = self.user_data['fts_cont']['rs_service_fueltype_by_p']
        data['assumptions']['ss_service_fueltype_by_p'] = self.user_data['fts_cont']['ss_service_fueltype_by_p']
        data['assumptions']['is_service_fueltype_by_p'] = self.user_data['fts_cont']['is_service_fueltype_by_p']
        data['assumptions']['rs_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['rs_service_fueltype_tech_by_p']
        data['assumptions']['ss_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['ss_service_fueltype_tech_by_p']
        data['assumptions']['is_service_fueltype_tech_by_p'] = self.user_data['fts_cont']['is_service_fueltype_tech_by_p']
        data['assumptions']['rs_tech_increased_service'] = self.user_data['sgs_cont']['rs_tech_increased_service']
        data['assumptions']['ss_tech_increased_service'] = self.user_data['sgs_cont']['ss_tech_increased_service']
        data['assumptions']['is_tech_increased_service'] = self.user_data['sgs_cont']['is_tech_increased_service']
        data['assumptions']['rs_tech_decreased_share'] = self.user_data['sgs_cont']['rs_tech_decreased_share']
        data['assumptions']['ss_tech_decreased_share'] = self.user_data['sgs_cont']['ss_tech_decreased_share']
        data['assumptions']['is_tech_decreased_share'] = self.user_data['sgs_cont']['is_tech_decreased_share']
        data['assumptions']['rs_tech_constant_share'] = self.user_data['sgs_cont']['rs_tech_constant_share']
        data['assumptions']['ss_tech_constant_share'] = self.user_data['sgs_cont']['ss_tech_constant_share']
        data['assumptions']['is_tech_constant_share'] = self.user_data['sgs_cont']['is_tech_constant_share']
        data['assumptions']['rs_sig_param_tech'] = self.user_data['sgs_cont']['rs_sig_param_tech']
        data['assumptions']['ss_sig_param_tech'] = self.user_data['sgs_cont']['ss_sig_param_tech']
        data['assumptions']['is_sig_param_tech'] = self.user_data['sgs_cont']['is_sig_param_tech']
        data['assumptions']['rs_installed_tech'] = self.user_data['sgs_cont']['rs_installed_tech']
        data['assumptions']['ss_installed_tech'] = self.user_data['sgs_cont']['ss_installed_tech']
        data['assumptions']['is_installed_tech'] = self.user_data['sgs_cont']['is_installed_tech']
        data['rs_fuel_disagg'] = self.user_data['sd_cont']['rs_fuel_disagg']
        data['ss_fuel_disagg'] = self.user_data['sd_cont']['ss_fuel_disagg']
        data['is_fuel_disagg'] = self.user_data['sd_cont']['is_fuel_disagg']

        # Copy from before_model_run()
        data['lu_reg'] = self.get_region_names(REGION_SET_NAME)

        data['lu_reg'] = data['lu_reg'][:NR_OF_MODELLEd_REGIONS]
        # =========DUMMY DATA
        data = data_loader.dummy_data_generation(data, data['lu_reg'])
        # =========DUMMY DATA

        # ---------------------------------------------
        # Create .ini file with simulation information
        # ---------------------------------------------
        '''write_data.write_simulation_inifile(
            data['local_paths']['data_results'],
            data['sim_param'],
            data['enduses'],
            data['assumptions'],
            data['reg_nrs'])'''

        # ---------
        # Run model
        # ---------
        results = energy_demand_model(data)

        # ------------------------------------
        # Write results output for supply
        # ------------------------------------
        supply_results = results.ed_fueltype_regs_yh

        logging.info("... finished wrapper calculations")
        return results

    def extract_obj(self, results):
        """Implement this method to return a scalar value objective function

        This method should take the results from the output of the `simulate`
        method, process the results, and return a scalar value which can be
        used as the objective function

        Arguments
        =========
        results : :class:`dict`
            The results from the `simulate` method

        Returns
        =======
        float
            A scalar component generated from the simulation model results
        """
        pass
