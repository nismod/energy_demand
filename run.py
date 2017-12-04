"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
import configparser
import numpy as np
from datetime import date
from collections import defaultdict
from smif.model.sector_model import SectorModel
from pkg_resources import Requirement, resource_filename
from pyproj import Proj, transform

from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.cli import run_model
from energy_demand.dwelling_stock import dw_stock
from energy_demand.read_write import read_data
from energy_demand.read_write import write_data
from energy_demand.read_write import data_loader
from energy_demand.main import energy_demand_model
from energy_demand.assumptions import param_assumptions
from energy_demand.assumptions import non_param_assumptions
from energy_demand.basic import date_prop
from energy_demand.basic import logger_setup
from energy_demand.validation import lad_validation
from energy_demand.technologies import fuel_service_switch

# must match smif project name for Local Authority Districts
REGION_SET_NAME = 'lad_uk_2016'
NR_OF_MODELLEd_REGIONS = 391 # uk: 391, england.: 380
PROFILER = False

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

        return dict(output_dict)

    def before_model_run(self, data=None):
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
        data = defaultdict(dict, data)

        # Criteria
        data['criterias']['virtual_building_stock_criteria'] = True     # True: Run virtual building stock model
        data['criterias']['plot_HDD_chart'] = False                     # True: Plotting of HDD vs gas chart
        data['criterias']['validation_criteria'] = False                # True: Plot validation plots
        data['criterias']['mode_constrained'] = False                   # True: Technologies are defined in ED model and fuel is provided, False: Heat is delievered not per technologies

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

        data['sim_param']['base_yr'] = 2015 #REPLACE
        data['sim_param']['curr_yr'] = data['sim_param']['base_yr']
        self.user_data['base_yr'] = data['sim_param']['base_yr']

        # -----------------------------
        # Region related informatiom
        # -----------------------------
        data['lu_reg'] = self.get_region_names(REGION_SET_NAME)

        reg_centroids = self.get_region_centroids(REGION_SET_NAME)
        data['reg_coord'] = self.get_long_lat_decimal_degrees(reg_centroids)

        # SCRAP REMOVE: ONLY SELECT NR OF MODELLED REGIONS
        data['lu_reg'] = data['lu_reg'][:NR_OF_MODELLEd_REGIONS]
        logging.info("Modelled for a number of regions: " + str(len(data['lu_reg'])))
        data['reg_nrs'] = len(data['lu_reg'])

        # ---------------------
        # Energy demand specific input which need to generated or read in
        # ---------------------
        data['lookups'] = data_loader.load_basic_lookups()
        data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
            data['paths'], data['lookups'])

        # -----------------------------
        # Obtain external scenario data
        # -----------------------------
        pop_array = self.get_scenario_data('population')
        data['population'] = self.array_to_dict(pop_array)

        gva_array = self.get_scenario_data('gva')
        data['gva'] = self.array_to_dict(gva_array)

        # Get building related data
        if data['criterias']['virtual_building_stock_criteria']:
            rs_floorarea, ss_floorarea = data_loader.virtual_building_datasets(
                data['lu_reg'], data['sectors']['all_sectors'], data)
        else:
            pass
            # Floor areas TODO LOAD FROM NEWCASTLE
            #rs_floorarea = defaultdict(dict)
            #ss_floorarea = defaultdict(dict)

        #Scenario data
        data['scenario_data'] = {
            'gva': data['gva'],
            'population': data['population'],
            'floor_area': {
                'rs_floorarea': rs_floorarea,
                'ss_floorarea': ss_floorarea
                }
        }

        # ------------
        # Assumptions
        # ------------
        data['assumptions'] = non_param_assumptions.load_non_param_assump(
            data['sim_param']['base_yr'], data['paths'], data['enduses'], data['lookups'])
        data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)

        data['tech_lp'] = data_loader.load_data_profiles(
            data['paths'],
            data['local_paths'],
            data['assumptions']['model_yeardays'],
            data['assumptions']['model_yeardays_daytype'])
    
        # ---------------------
        # Convert capacity switches to service switches
        # ---------------------
        data['assumptions']['rs_service_switches'], data['assumptions']['crit_capacity_switch'] = fuel_service_switch.capacity_installations(
            data['assumptions']['rs_service_switches'],
            data['assumptions']['capacity_switches']['rs_capacity_switches'],
            data['assumptions']['technologies'],
            data['assumptions']['enduse_overall_change']['other_enduse_mode_info'],
            data['fuels']['rs_fuel_raw_data_enduses'],
            data['assumptions']['rs_fuel_tech_p_by'],
            data['sim_param']['base_yr'])

        data['assumptions']['ss_service_switches'], data['assumptions']['crit_capacity_switch'] = fuel_service_switch.capacity_installations(
            data['assumptions']['ss_service_switches'],
            data['assumptions']['capacity_switches']['ss_capacity_switches'],
            data['assumptions']['technologies'],
            data['assumptions']['enduse_overall_change']['other_enduse_mode_info'],
            data['fuels']['ss_fuel_raw_data_enduses'],
            data['assumptions']['ss_fuel_tech_p_by'],
            data['sim_param']['base_yr'])

        data['assumptions']['is_service_switches'], data['assumptions']['crit_capacity_switch'] = fuel_service_switch.capacity_installations(
            data['assumptions']['is_service_switches'],
            data['assumptions']['capacity_switches']['is_capacity_switches'],
            data['assumptions']['technologies'],
            data['assumptions']['enduse_overall_change']['other_enduse_mode_info'],
            data['fuels']['is_fuel_raw_data_enduses'],
            data['assumptions']['is_fuel_tech_p_by'],
            data['sim_param']['base_yr'])

        # ------------------------
        # Load all SMIF parameters and replace data dict
        # ------------------------
        data['assumptions'] = self.load_smif_parameters(
            data['paths']['yaml_parameters_complete'],
            data,
            data['assumptions'])

        logging.info(data['assumptions']['strategy_variables'])
        # Update: Necessary updates after external data definition
        data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
            data['assumptions'],
            data['assumptions']['technologies'],
            data['assumptions']['strategy_variables']['eff_achiev_f'])

        # ------------------------
        # Pass along to simulate()
        # ------------------------
        self.user_data['criterias'] = data['criterias']
        self.user_data['temp_data'] = data['temp_data']
        self.user_data['weather_stations'] = data['weather_stations']
        self.user_data['gva'] = self.array_to_dict(gva_array)
        self.user_data['population'] = self.array_to_dict(pop_array)
        self.user_data['rs_floorarea'] = rs_floorarea
        self.user_data['ss_floorarea'] = ss_floorarea

        # --------------------
        # Initialise scenario
        # --------------------
        self.user_data['fts_cont'], self.user_data['sgs_cont'], self.user_data['sd_cont'], self.user_data['switches_cont'] = scenario_initalisation(
            self.user_data['data_path'], data)

        # ------
        # Write population scenario data to txt files for this scenario run
        # ------
        for t_idx, timestep in enumerate(self.timesteps):
            write_data.write_pop(
                timestep,
                data['local_paths']['data_results'],
                pop_array[t_idx])

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

        Returns
        =======

        """
        # Convert data to default dict
        data = defaultdict(dict, data)

        # Paths
        path_main = resource_filename(Requirement.parse("energy_demand"), "")

        # Ini info
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        # Go two levels down
        path, folder = os.path.split(path_main)
        path_nismod, folder = os.path.split(path)
        self.user_data['data_path'] = os.path.join(path_nismod, 'data_energy_demand')

        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])

        # Logger
        logger_setup.set_up_logger(os.path.join(data['local_paths']['data_results'], "logger_smif_run.log"))

        # --------------------
        # Get simulation parameters from before_model_run()
        # --------------------
        data['criterias'] = self.user_data['criterias']

        data['sim_param']['base_yr'] = self.user_data['base_yr'] # Base year definition
        data['sim_param']['curr_yr'] = timestep                  # Read in current year from smif
        data['sim_param']['simulated_yrs'] = self.timesteps      # Read in all simulated years from smif

        # Region related information
        data['lu_reg'] = self.get_region_names(REGION_SET_NAME)
        data['lu_reg'] = data['lu_reg'][:NR_OF_MODELLEd_REGIONS] # Select only certain number of regions #TODO: REMOVE
        reg_centroids = self.get_region_centroids(REGION_SET_NAME)
        data['reg_coord'] = self.get_long_lat_decimal_degrees(reg_centroids)
        data['reg_nrs'] = len(data['lu_reg'])

        # ---------------
        # Energy demand model related parameters
        # ---------------
        data['lookups'] = data_loader.load_basic_lookups()
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
        data['assumptions'] = non_param_assumptions.load_non_param_assump(
            data['sim_param']['base_yr'], data['paths'], data['enduses'], data['lookups'])
    
        # ------------------------
        # Load all SMIF parameters and replace data dict
        # ------------------------
        data['assumptions'] = self.load_smif_parameters(
            data['paths']['yaml_parameters_complete'], data, data['assumptions'])

        data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_datype(year_to_model=2015)
        data['tech_lp'] = data_loader.load_data_profiles(
            data['paths'],
            data['local_paths'],
            data['assumptions']['model_yeardays'],
            data['assumptions']['model_yeardays_daytype'])

        # Update: Necessary updates after external data definition
        data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
            data['assumptions'],
            data['assumptions']['technologies'],
            data['assumptions']['strategy_variables']['eff_achiev_f'])

        # ---------
        # Scenario data
        # ---------
        data['scenario_data'] = {
            'gva': self.user_data['gva'],
            'population':  self.user_data['population'],

            # Only add newcastle floorarea here
            'floor_area': {
                'rs_floorarea': self.user_data['rs_floorarea'],
                'ss_floorarea': self.user_data['ss_floorarea']}
            }

        # -----------------------
        # Load data from scripts
        # -----------------------
        # Insert from script calculations which are stored in memory
        data['temp_data'] = self.user_data['temp_data']
        data['weather_stations'] = self.user_data['weather_stations']
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


        data['assumptions']['rs_service_switches'] = self.user_data['switches_cont']['rs_service_switches']
        data['assumptions']['ss_service_switches'] = self.user_data['switches_cont']['ss_service_switches']
        data['assumptions']['is_service_switches'] = self.user_data['switches_cont']['is_service_switches']

        data['assumptions']['rs_share_service_tech_ey_p'] = self.user_data['switches_cont']['rs_share_service_tech_ey_p']
        data['assumptions']['ss_share_service_tech_ey_p'] = self.user_data['switches_cont']['ss_share_service_tech_ey_p']
        data['assumptions']['is_share_service_tech_ey_p'] = self.user_data['switches_cont']['is_share_service_tech_ey_p']
        # ---------------------------------------------
        # Create .ini file with simulation information
        # ---------------------------------------------
        write_data.write_simulation_inifile(
            data['local_paths']['data_results'],
            data['sim_param'],
            data['enduses'],
            data['assumptions'],
            data['reg_nrs'],
            data['lu_reg'])

        # ---------
        # Run main model run function
        # ---------

        # Profiler
        if PROFILER:
            profiler = Profiler(use_signal=False)
            profiler.start()

        model_run_object = energy_demand_model(data)

        if PROFILER:
            profiler.stop()
            logging.debug("Profiler Results")
            print(profiler.output_text(unicode=True, color=True))

        # ------------------------------------
        # Write results output for supply
        # ------------------------------------
        supply_results = model_run_object.ed_fueltype_regs_yh

        # -----------------
        # Write to txt files
        # -----------------
        ed_fueltype_regs_yh = model_run_object.ed_fueltype_regs_yh
        out_enduse_specific = model_run_object.tot_fuel_y_enduse_specific_h
        tot_peak_enduses_fueltype = model_run_object.tot_peak_enduses_fueltype
        tot_fuel_y_max_enduses = model_run_object.tot_fuel_y_max_enduses
        ed_fueltype_national_yh = model_run_object.ed_fueltype_national_yh

        reg_load_factor_y = model_run_object.reg_load_factor_y
        reg_load_factor_yd = model_run_object.reg_load_factor_yd
        reg_load_factor_winter = model_run_object.reg_load_factor_seasons['winter']
        reg_load_factor_spring = model_run_object.reg_load_factor_seasons['spring']
        reg_load_factor_summer = model_run_object.reg_load_factor_seasons['summer']
        reg_load_factor_autumn = model_run_object.reg_load_factor_seasons['autumn']

        # ------------------------------------------------
        # Validation base year: Hourly temporal validation
        # ------------------------------------------------
        if data['criterias']['validation_criteria'] == True and timestep == data['sim_param']['base_yr']:
            lad_validation.tempo_spatial_validation(
                data['sim_param']['base_yr'],
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'],
                data['scenario_data'],
                model_run_object.ed_fueltype_national_yh,
                ed_fueltype_regs_yh,
                model_run_object.tot_peak_enduses_fueltype,
                data['lookups'],
                data['local_paths'],
                data['lu_reg'],
                data['reg_coord'],
                data['assumptions']['seasons'],
                data['assumptions']['model_yeardays_daytype'])

        # -------------------------------------------
        # Write annual results to txt files
        # -------------------------------------------
        logging.info("... Start writing results to file")
        path_runs = data['local_paths']['data_results_model_runs']

        write_data.write_supply_results(timestep, path_runs, supply_results, "supply_results")
        write_data.write_enduse_specific(timestep, path_runs, out_enduse_specific, "out_enduse_specific")
        write_data.write_max_results(timestep, path_runs, "result_tot_peak_enduses_fueltype", tot_peak_enduses_fueltype, "tot_peak_enduses_fueltype")
        write_data.write_lf(path_runs, "result_reg_load_factor_y", [timestep], reg_load_factor_y, 'reg_load_factor_y')
        write_data.write_lf(path_runs, "result_reg_load_factor_yd", [timestep], reg_load_factor_yd, 'reg_load_factor_yd')
        write_data.write_lf(path_runs, "result_reg_load_factor_winter", [timestep], reg_load_factor_winter, 'reg_load_factor_winter')
        write_data.write_lf(path_runs, "result_reg_load_factor_spring", [timestep], reg_load_factor_spring, 'reg_load_factor_spring')
        write_data.write_lf(path_runs, "result_reg_load_factor_summer", [timestep], reg_load_factor_summer, 'reg_load_factor_summer')
        write_data.write_lf(path_runs, "result_reg_load_factor_autumn", [timestep], reg_load_factor_autumn, 'reg_load_factor_autumn')

        logging.info("... finished wrapper calculations")
        #prnt(":")
        return {'model_name': supply_results}

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

    def load_smif_parameters(self, path_all_strategy_params, data, assumptions):
        """Get all model parameters from smif and replace in data dict

        Arguments
        =========
        path_all_strategy_params : dict
            Path to yaml file where all strategy variables
            are defined
        data : dict
            Dict with all data
        assumptions : dict
            Assumptions

        Returns
        =========
        assumptions : dict
            Assumptions with added strategy variables
        """
        strategy_variables = {}

        # Get all parameter names
        all_strategy_variables = self.parameters.keys()

        # Get variable from dict and reassign and delete from data
        for var_name in all_strategy_variables:
            strategy_variables[var_name] = data[var_name]
            logging.info("Load strategy parameter: {}".format(var_name))
            del data[var_name]

        # Add to assumptoins
        assumptions['strategy_variables'] = strategy_variables

        return assumptions

    def get_long_lat_decimal_degrees(self, reg_centroids):
        """Project coordinates from shapefile to get
        decimal degrees (from OSGB_1936_British_National_Grid to
        WGS 84 projection). Info: #http://spatialreference.org/ref/epsg/wgs-84/

        Arguments
        ---------
        reg_centroids : dict
            Centroid information read in from shapefile via smif

        Return
        -------
        reg_coord : dict
            Contains long and latidue for every region in decimal degrees
        """
        reg_coord = {}
        for centroid in reg_centroids:

            # OSGB_1936_British_National_Grid
            inProj = Proj(init='epsg:27700')

            #WGS 84 projection
            outProj = Proj(init='epsg:4326')

            # Convert to decimal degrees
            long_dd, lat_dd = transform(
                inProj,
                outProj,
                centroid['geometry']['coordinates'][0], #longitude
                centroid['geometry']['coordinates'][1]) #latitude

            reg_coord[centroid['properties']['name']] = {}
            reg_coord[centroid['properties']['name']]['longitude'] = long_dd
            reg_coord[centroid['properties']['name']]['latitude'] = lat_dd

        return reg_coord
