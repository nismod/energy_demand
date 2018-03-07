"""The sector model wrapper for smif to run the energy demand model test
"""
import os
import logging
import configparser
import numpy as np
import datetime
from datetime import date
from collections import defaultdict
from smif.model.sector_model import SectorModel
from pkg_resources import Requirement, resource_filename
from pyproj import Proj, transform

from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.technologies import tech_related
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
from energy_demand.profiles import hdd_cdd
from energy_demand.basic import lookup_tables

# must match smif project name for Local Authority Districts
NR_OF_MODELLEd_REGIONS = 391 #391 # uk: 391, england.: 380
WRITEOUTSMIFRESULTS = False

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)

        self.user_data = {}

    def before_model_run(self, data_handle):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)
        """
        data = defaultdict(dict)

        p_mixed_resid = 0.2       # TODO: Spatial calibration factor for virtual dwelling stock

        # -----------
        # INFORMATION:
        # you only running smif, use the following configuration: fast_smif_run == True
        # -----------
        data['criterias']['mode_constrained'] = True                    # True: Technologies are defined in ED model and fuel is provided, False: Heat is delievered not per technologies
        data['criterias']['virtual_building_stock_criteria'] = True     # True: Run virtual building stock model
        data['criterias']['spatial_exliclit_diffusion'] = False         # True: Spatial explicit calculations
        data['criterias']['writeYAML'] = True                          # True: Write YAML parameters

        fast_smif_run = False

        if fast_smif_run == True:
            data['criterias']['write_to_txt'] = False
            data['criterias']['beyond_supply_outputs'] = False
            data['criterias']['validation_criteria'] = False
            data['criterias']['plot_tech_lp'] = False
            data['criterias']['plot_crit'] = False
            data['criterias']['crit_plot_enduse_lp'] = False
            data['criterias']['plot_HDD_chart'] = False
        elif fast_smif_run == False:
            data['criterias']['write_to_txt'] = True
            data['criterias']['beyond_supply_outputs'] = True
            data['criterias']['validation_criteria'] = True
            data['criterias']['plot_tech_lp'] = False
            data['criterias']['plot_crit'] = False
            data['criterias']['crit_plot_enduse_lp'] = False
            data['criterias']['plot_HDD_chart'] = False

        data['sim_param']['base_yr'] = data_handle.timesteps[0]
        data['sim_param']['curr_yr'] = data_handle.timesteps[0]
        self.user_data['base_yr'] = data['sim_param']['base_yr']

        # -----------------------------
        # Paths
        # -----------------------------
        path_main = resource_filename(Requirement.parse("energy_demand"), "")

        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))
        self.user_data['data_path'] = config['PATHS']['path_local_data']
        self.processed_path = config['PATHS']['path_processed_data']
        self.result_path = config['PATHS']['path_result_data']

        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])

        # -----------------------------
        # Region related info
        # -----------------------------
        region_set_name = self.regions.names[0]

        data['regions'] = self.get_region_names(region_set_name)

        reg_centroids = self.get_region_centroids(region_set_name)
        data['reg_coord'] = self.get_long_lat_decimal_degrees(reg_centroids)

        # SCRAP REMOVE: ONLY SELECT NR OF MODELLED REGIONS
        data['regions'] = data['regions'][:NR_OF_MODELLEd_REGIONS]

        logging.info("Modelled for a number of regions: " + str(len(data['regions'])))
        data['reg_nrs'] = len(data['regions'])

        # ---------------------
        # Energy demand specific input which need to generated or read in
        # ---------------------
        data['lookups'] = lookup_tables.basic_lookups()
        data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(data['local_paths'])
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
            data['paths'], data['lookups'])

        # -----------------------------
        # Obtain external base year scenario data
        # -----------------------------
        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva')
        #industry_gva_by = data_handle.get_base_timestep_data('industry_gva')

        pop_dict = {}
        gva_dict = {}
        gva_industry_dict = {}

        for r_idx, region in enumerate(data['regions']):
            pop_dict[region] = pop_array_by[r_idx, 0]
            gva_dict[region] = gva_array_by[r_idx, 0]
            #gva_industry_dict[region] = industry_gva_by[r_idx, 0]

        data['population'][data['sim_param']['base_yr']] = pop_dict
        data['gva'][data['sim_param']['base_yr']] = gva_dict
        #data['industry_gva'][data['sim_param']['base_yr']] = gva_industry_dict
        data['industry_gva'] = "TST"

        # Get building related data
        if data['criterias']['virtual_building_stock_criteria']:
            rs_floorarea, ss_floorarea = data_loader.floor_area_virtual_dw(
                data['regions'],
                data['sectors']['all_sectors'],
                data['local_paths'],
                base_yr=data['sim_param']['base_yr'],
                p_mixed_resid=p_mixed_resid)
        else:
            pass
            # Load floor area from newcastle
            #rs_floorarea = defaultdict(dict)
            #ss_floorarea = defaultdict(dict)

        # --------------
        # Scenario data
        # --------------
        data['scenario_data'] = {
            'gva': data['gva'],
            'population': data['population'],
            'industry_gva': data['industry_gva'],
            'floor_area': {
                'rs_floorarea': rs_floorarea,
                'ss_floorarea': ss_floorarea
                }
        }

        # ------------
        # Load assumptions
        # ------------
        data['assumptions'] = non_param_assumptions.load_non_param_assump(
            data['sim_param']['base_yr'],
            data['paths'],
            data['enduses'],
            data['sectors'],
            data['lookups']['fueltypes'],
            data['lookups']['fueltypes_nr'])
        data['assumptions']['seasons'] = date_prop.read_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_model_yeardays_daytype(
            year_to_model=2015)

        # ----------------------------------
        # Calculate correction factors
        # ----------------------------------
        data['assumptions']['cdd_weekend_cfactors'] = hdd_cdd.calc_weekend_corr_f(
            data['assumptions']['model_yeardays_daytype'],
            data['assumptions']['ss_t_cooling_weekend_factor'])

        data['assumptions']['ss_weekend_f'] = hdd_cdd.calc_weekend_corr_f(
            data['assumptions']['model_yeardays_daytype'],
            data['assumptions']['ss_weekend_factor'])

        data['assumptions']['is_weekend_f'] = hdd_cdd.calc_weekend_corr_f(
            data['assumptions']['model_yeardays_daytype'],
            data['assumptions']['is_weekend_factor'])

        # ------------
        # Load load profiles of technologies
        # ------------
        data['tech_lp'] = data_loader.load_data_profiles(
            data['paths'],
            data['local_paths'],
            data['assumptions']['model_yeardays'],
            data['assumptions']['model_yeardays_daytype'],
            data['criterias']['plot_tech_lp'])

        # ---------------------
        # Convert capacity switches to service switches
        # ---------------------
        data['assumptions'] = fuel_service_switch.capacity_to_service_switches(
            data['assumptions'], data['fuels'], data['sim_param']['base_yr'])

        # ------------------------
        # Load all SMIF parameters and replace data dict
        # ------------------------
        parameters = data_handle.get_parameters()
        data['assumptions'] = self.load_smif_parameters(
            parameters,
            data['assumptions'])

        # Update technologies after strategy definition
        data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
            data['assumptions']['technologies'],
            data['assumptions']['strategy_variables']['eff_achiev_f'],
            data['assumptions']['strategy_variables']['split_hp_gshp_to_ashp_ey'])

        # ------------------------
        # Pass along to simulate()
        # ------------------------
        self.user_data['gva'] = data['gva']
        self.user_data['industry_gva'] = data['industry_gva']
        self.user_data['population'] = data['population']
        self.user_data['rs_floorarea'] = rs_floorarea
        self.user_data['ss_floorarea'] = ss_floorarea
        self.user_data['data_pass_along'] = {}
        self.user_data['data_pass_along']['criterias'] = data['criterias']
        self.user_data['data_pass_along']['temp_data'] = data['temp_data']
        self.user_data['data_pass_along']['weather_stations'] = data['weather_stations']
        self.user_data['data_pass_along']['tech_lp'] = data['tech_lp']
        self.user_data['data_pass_along']['lookups'] = data['lookups']
        self.user_data['data_pass_along']['assumptions'] = data['assumptions']
        self.user_data['data_pass_along']['enduses'] = data['enduses']
        self.user_data['data_pass_along']['sectors'] = data['sectors']
        self.user_data['data_pass_along']['fuels'] = data['fuels']
        self.user_data['data_pass_along']['reg_coord'] = data['reg_coord']
        self.user_data['data_pass_along']['regions'] = data['regions']
        self.user_data['data_pass_along']['reg_nrs'] = data['reg_nrs']

        # --------------------
        # Initialise scenario
        # --------------------
        logging.info("... Initialise function execution")
        self.user_data['init_cont'], self.user_data['fuel_disagg'] = scenario_initalisation(
            self.user_data['data_path'], data)

    def initialise(self, initial_conditions):
        pass

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
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

        Returns
        =======
        supply_results : dict
            key: name defined in sector models
                value: np.zeros((len(reg), len(intervals)) )
        """
        logging.info("... start simulate() function in wrapper")
        time_start = datetime.datetime.now()

        # Init default dict
        data = defaultdict(dict)

        # Paths
        path_main = resource_filename(Requirement.parse("energy_demand"), "")

        # Ini info
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        # ---------------------------------------------
        # Paths
        # ---------------------------------------------
        # Go two levels down
        path, folder = os.path.split(path_main)
        path_nismod, folder = os.path.split(path)
        self.user_data['data_path'] = os.path.join(path_nismod, 'data_energy_demand')

        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(self.user_data['data_path'])

        data['sim_param']['base_yr'] = self.user_data['base_yr']    # Base year definition
        data['sim_param']['curr_yr'] = data_handle.current_timestep # Read in current year from smif
        data['sim_param']['simulated_yrs'] = self.timesteps         # Read in all simulated years from smif

        # ---------------------------------------------
        # Load data from scripts (Get simulation parameters from before_model_run()
        # ---------------------------------------------
        data = self.pass_to_simulate(
            data, self.user_data['data_pass_along'])
        data = self.pass_to_simulate(
            data, self.user_data['fuel_disagg'])
        data['assumptions'] = self.pass_to_simulate(
            data['assumptions'], self.user_data['init_cont'])

        # Update: Necessary updates after external data definition
        data['assumptions']['technologies'] = non_param_assumptions.update_assumptions(
            data['assumptions']['technologies'],
            data['assumptions']['strategy_variables']['eff_achiev_f'],
            data['assumptions']['strategy_variables']['split_hp_gshp_to_ashp_ey'])

        # ---------------------------------------------
        # Scenario data
        # ---------------------------------------------
        pop_array_current = data_handle.get_data('population')  # of simulation year
        gva_array_current = data_handle.get_data('gva')         # of simulation year

        gva_dict_current = {}
        pop_dict_current = {}

        for r_idx, region in enumerate(data['regions']):
            pop_dict_current[region] = pop_array_current[r_idx, 0]
            gva_dict_current[region] = gva_array_current[r_idx, 0]

        pop_dict = {}
        pop_dict[data['sim_param']['base_yr']] = self.user_data['population'][data_handle.base_timestep] # by
        pop_dict[data['sim_param']['curr_yr']] = pop_dict_current # Get population of cy

        gva_dict = {}
        gva_dict[data['sim_param']['base_yr']] = self.user_data['gva'][data_handle.base_timestep] # by
        gva_dict[data['sim_param']['curr_yr']] = gva_dict_current # Get gva of cy

        gva_industry_dict = {}
        #gva_industry_dict[data['sim_param']['base_yr']] = self.user_data['gva'][data_handle.base_timestep] # by
        #gva_industry_cy[data['sim_param']['curr_yr']] = gva_dict_current # Get gva of cy'''

        data['scenario_data'] = {
            'gva': gva_dict,
            'population': pop_dict,
            'industry_gva': gva_industry_dict,

            # Only add newcastle floorarea here
            'floor_area': {
                'rs_floorarea': self.user_data['rs_floorarea'],
                'ss_floorarea': self.user_data['ss_floorarea']}}

        # ---------------------------------------------
        # Create .ini file with simulation info
        # ---------------------------------------------
        write_data.write_simulation_inifile(
            data['local_paths']['data_results'],
            data['sim_param'],
            data['enduses'],
            data['assumptions'],
            data['reg_nrs'],
            data['regions'])

        # ---------------------------------------------
        # Run energy demand model
        # ---------------------------------------------
        sim_obj = energy_demand_model(data)

        # ------------------------------------------------
        # Validation base year: Hourly temporal validation
        # ------------------------------------------------
        if data['criterias']['validation_criteria'] == True and data_handle.current_timestep == data['sim_param']['base_yr']:
            lad_validation.tempo_spatial_validation(
                data['sim_param']['base_yr'],
                data['assumptions']['model_yearhours_nrs'],
                data['assumptions']['model_yeardays_nrs'],
                data['scenario_data'],
                sim_obj.ed_fueltype_national_yh,
                sim_obj.ed_fueltype_regs_yh,
                sim_obj.tot_peak_enduses_fueltype,
                data['lookups']['fueltypes'],
                data['lookups']['fueltypes_nr'],
                data['local_paths'],
                data['paths'],
                data['regions'],
                data['reg_coord'],
                data['assumptions']['seasons'],
                data['assumptions']['model_yeardays_daytype'],
                data['criterias']['plot_crit'])

        # -------------------------------------------
        # Write annual results to txt files
        # -------------------------------------------
        if data['criterias']['write_to_txt']:
            #tot_fuel_y_max_enduses = sim_obj.tot_fuel_y_max_enduses
            logging.info("... Start writing results to file")

            # ------------------------
            # Plot individual enduse
            # ------------------------
            if data['criterias']['crit_plot_enduse_lp'] and data_handle.current_timestep == 2015:

                # Maybe move to result folder in a later step
                path_folder_lp = os.path.join(data['local_paths']['data_results'], 'individual_enduse_lp')
                basic_functions.delete_folder(path_folder_lp)
                basic_functions.create_folder(path_folder_lp)

                winter_week = list(range(
                    date_prop.date_to_yearday(2015, 1, 12), date_prop.date_to_yearday(2015, 1, 19))) #Jan
                spring_week = list(range(
                    date_prop.date_to_yearday(2015, 5, 11), date_prop.date_to_yearday(2015, 5, 18))) #May
                summer_week = list(range(
                    date_prop.date_to_yearday(2015, 7, 13), date_prop.date_to_yearday(2015, 7, 20))) #Jul
                autumn_week = list(range(
                    date_prop.date_to_yearday(2015, 10, 12), date_prop.date_to_yearday(2015, 10, 19))) #Oct

                # Plot electricity
                for enduse, ed_yh in sim_obj.tot_fuel_y_enduse_specific_yh.items():
                    plotting_results.plot_enduse_yh(
                        name_fig="individ__{}".format(enduse),
                        path_result=path_folder_lp,
                        ed_yh=ed_yh[data['lookups']['fueltypes']['electricity']],
                        days_to_plot=winter_week)

            write_data.write_supply_results(
                data_handle.current_timestep,
                "result_tot_yh",
                data['local_paths']['data_results_model_runs'],
                sim_obj.ed_fueltype_regs_yh,
                "result_tot_submodels_fueltypes")
            write_data.write_enduse_specific(
                data_handle.current_timestep,
                data['local_paths']['data_results_model_runs'],
                sim_obj.tot_fuel_y_enduse_specific_yh,
                "out_enduse_specific")
            write_data.write_max_results(
                data_handle.current_timestep, data['local_paths']['data_results_model_runs'],
                "result_tot_peak_enduses_fueltype", sim_obj.tot_peak_enduses_fueltype,
                "tot_peak_enduses_fueltype")
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_y",
                [data_handle.current_timestep], sim_obj.reg_load_factor_y, 'reg_load_factor_y')
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_yd",
                [data_handle.current_timestep], sim_obj.reg_load_factor_yd, 'reg_load_factor_yd')
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_winter",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['winter'], 'reg_load_factor_winter')
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_spring",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['spring'], 'reg_load_factor_spring')
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_summer",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['summer'], 'reg_load_factor_summer')
            write_data.write_lf(
                data['local_paths']['data_results_model_runs'], "result_reg_load_factor_autumn",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['autumn'], 'reg_load_factor_autumn')
            logging.info("... finished writing results to file")

        # ------------------------------------
        # Write results output for supply
        # ------------------------------------
        # Form of np.array(fueltype, sectors, region, periods)
        results_unconstrained = sim_obj.ed_submodel_fueltype_regs_yh
        #write_data.write_supply_results(
        # ['rs_submodel', 'ss_submodel', 'is_submodel'],timestep, data['local_paths']['data_results_model_runs'], results_unconstrained, "results_unconstrained")

        # Form of {constrained_techs: np.array(fueltype, sectors, region, periods)}
        results_constrained = sim_obj.ed_techs_submodel_fueltype_regs_yh
        #write_data.write_supply_results(
        # ['rs_submodel', 'ss_submodel', 'is_submodel'], timestep, data['local_paths']['data_results_model_runs'], results_unconstrained, "results_constrained")

        # --------------------------------------------------------
        # Reshape day and hours to yearhous (from (365, 24) to 8760)
        # --------------------------------------------------------
        # Reshape ed_techs_submodel_fueltype_regs_yh
        supply_sectors = ['residential', 'service', 'industry']

        results_constrained_reshaped = {}
        for heating_tech, submodel_techs in results_constrained.items():
            results_constrained_reshaped[heating_tech] = submodel_techs.reshape(
                len(supply_sectors),
                data['reg_nrs'],
                data['lookups']['fueltypes_nr'],
                8760)
        results_constrained = results_constrained_reshaped

        results_unconstrained = results_unconstrained.reshape(
            len(supply_sectors),
            data['reg_nrs'],
            data['lookups']['fueltypes_nr'],
            8760)

        # -------------------------------------
        # Generate dict for supply model
        # -------------------------------------
        if data['criterias']['mode_constrained']:
            supply_results = constrained_results(
                data['regions'],
                results_constrained,
                results_unconstrained,
                supply_sectors,
                data['lookups']['fueltypes'],
                data['assumptions']['technologies'],
                model_yearhours_nrs=8760)

            # Generate YAML file with keynames for `sector_model`
            if data['criterias']['writeYAML']:
                write_data.write_yaml_output_keynames(
                    data['paths']['yaml_parameters_keynames_constrained'], supply_results.keys())
        else:
            supply_results = unconstrained_results(
                data['regions'],
                results_unconstrained,
                supply_sectors,
                data['lookups']['fueltypes'],
                model_yearhours_nrs=8760)

            # Generate YAML file with keynames for `sector_model`
            if data['criterias']['writeYAML']:
                write_data.write_yaml_output_keynames(
                    data['paths']['yaml_parameters_keynames_unconstrained'], supply_results.keys())

        _total_scrap = 0
        for key in supply_results:
            _total_scrap += np.sum(supply_results[key])
        print("FINALSUM: " + str(_total_scrap))

        time_end = datetime.datetime.now()
        print("... Total Time: " + str(time_end - time_start))

        # ------
        # Write population data of current year to file
        # ------
        write_data.write_scenaric_population_data(
            data_handle.current_timestep,
            data['local_paths']['data_results_model_run_pop'],
            pop_array_current)

        # ------------------------------------
        # Write results to smif
        # ------------------------------------
        if WRITEOUTSMIFRESULTS:
            for key_name, result_to_txt in supply_results.items():
                if NR_OF_MODELLEd_REGIONS != 391:
                    # do not write out resutls
                    logging.warning("NO SMIF RESULT FILE ARE WRITTEN OUT")
                else:
                    print(
                        "write out results set {} {}".format(
                            key_name,
                            result_to_txt.shape))

                    data_handle.set_results(
                        key_name,
                        result_to_txt)
                    print("finished writing result")


        print("... finished wrapper execution")
        return supply_results

    def extract_obj(self, results):
        return 0

    def pass_to_simulate(self, dict_to_copy_into, dict_to_pass_along):
        """Pass dict defined in before_model_run() to simlate() function
        by copying key and values

        Arguments
        ---------
        dict_to_copy_into : dict
            Dict to copy values into
        dict_to_pass_along : dict
            Dictionary which needs to be copied and passed along
        """
        for key, value in dict_to_pass_along.items():
            dict_to_copy_into[key] = value

        return dict(dict_to_copy_into)

    def load_smif_parameters(self, data_handle, assumptions):
        """Get all model parameters from smif (`data_handle`) depending
        on narrative and replace in assumption dict

        Arguments
        ---------
        data_handle : dict
            Dict with all data_handle
        assumptions : dict
            Assumptions

        Returns
        -------
        assumptions : dict
            Assumptions with added strategy variables
        """
        strategy_variables = {}

        # Get all parameter names
        all_strategy_variables = self.parameters.keys()

        # Get variable from dict and reassign and delete from data_handle
        for var_name in all_strategy_variables:

            # Get narrative variable from input data_handle dict
            strategy_variables[var_name] = data_handle[var_name]

        # Add to assumptions
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

            inProj = Proj(init='epsg:27700') # OSGB_1936_British_National_Grid
            outProj = Proj(init='epsg:4326') #WGS 84 projection

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

def constrained_results(
        regions,
        results_constrained,
        results_unconstrained,
        supply_sectors,
        fueltypes,
        technologies,
        model_yearhours_nrs
    ):
    """Prepare results for energy supply model for
    constrained model running mode (no heat is provided but
    technology specific fuel use).
    The results for the supply model are provided aggregated
    as follows:

        { "submodel_fueltype_tech": np.array(regions, timesteps)}

    Because SMIF only takes results in the
    form of {key: np.aray(regions, timesteps)}, the key
    needs to contain information about submodel, fueltype,
    and technology. Also these key must be defined in
    the `submodel_model` configuration file.

    Arguments
    ----------
    regions : dict
        Regions
    results_constrained : dict
        Aggregated results in form
        {technology: np.array((sector, region, fueltype, timestep))}
    results_unconstrained : array
        Restuls of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    supply_sectors : list
        Names of sectors fur supply model
    fueltypes : dict
        Fueltype lookup
    technologies : dict
        Technologies
    model_yearhours_nrs : int
        Number of modelled hours in a year

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}
    """
    supply_results = {}

    # ----------------------------------------
    # Add all constrained technologies
    # Aggregate according to submodel, fueltype, technology, region, timestep
    # ----------------------------------------
    for submodel_nr, submodel in enumerate(supply_sectors):
        for tech, fuel_tech in results_constrained.items():
            fueltype_str = technologies[tech].fueltype_str
            fueltype_int = technologies[tech].fueltype_int

            # ----
            # Technological simplifications because of different technology definition
            # ----
            tech_simplified = model_tech_simplification(tech)

            # Generate key name (must be defined in `sector_models`)
            key_name = "{}_{}_{}".format(submodel, fueltype_str, tech_simplified)

            if key_name in supply_results.keys():

                # Iterate over reigons and add fuel (Do not replace by +=)
                for region_nr, _ in enumerate(regions):
                    supply_results[key_name][region_nr] = supply_results[key_name][region_nr] + fuel_tech[submodel_nr][region_nr][fueltype_int]
            else:
                supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))
                for region_nr, _ in enumerate(regions):
                    supply_results[key_name][region_nr] = fuel_tech[submodel_nr][region_nr][fueltype_int]

    # --------------------------------
    # Add all technologies of restricted enduse (heating)
    # --------------------------------
    constrained_ed = np.zeros((results_unconstrained.shape))

    # Calculate tech fueltype specific to fuel of constrained technologies
    for tech, fuel_tech in results_constrained.items():
        constrained_ed += fuel_tech

    # Substract constrained fuel from nonconstrained (total) fuel
    non_heating_ed = results_unconstrained - constrained_ed

    # ---------------------------------
    # Add non_heating for all fueltypes
    # ---------------------------------
    for submodel_nr, submodel in enumerate(supply_sectors):
        for fueltype_str, fueltype_int in fueltypes.items():

            if fueltype_str == 'heat':
                pass #Do not add non_heating demand for fueltype heat
            else:
                # Generate key name (must be defined in `sector_models`)
                key_name = "{}_{}_{}".format(
                    submodel, fueltype_str, "non_heating")

                # Iterate regions and add fuel
                supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))
                for region_nr, _ in enumerate(regions):
                    supply_results[key_name][region_nr] = non_heating_ed[submodel_nr][region_nr][fueltype_int]

    logging.info("Prepared results for energy supply model in constrained mode")
    return dict(supply_results)

def unconstrained_results(
        regions,
        results_unconstrained,
        supply_sectors,
        fueltypes,
        model_yearhours_nrs
    ):
    """Prepare results for energy supply model for
    unconstrained model running mode (heat is provided).
    The results for the supply model are provided aggregated
    for every submodel, fueltype, region, timestep

    Note
    -----
    Because SMIF only takes results in the
    form of {key: np.aray(regions, timesteps)}, the key
    needs to contain information about submodel and fueltype

    Also these key must be defined in the `submodel_model`
    configuration file

    Arguments
    ----------
    regions : dict
        Regions
    results_unconstrained : array
        Results of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    supply_sectors : list
        Names of sectors for supply model
    fueltypes : dict
        Fueltype lookup
    model_yearhours_nrs : int
        Number of modelled hours in a year

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}
    """
    supply_results = {}

    # Iterate submodel and fueltypes
    for submodel_nr, submodel in enumerate(supply_sectors):
        for fueltype_str, fueltype_int in fueltypes.items():

            # Generate key name (must be defined in `sector_models`)
            key_name = "{}_{}".format(submodel, fueltype_str)

            supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))

            for region_nr, _ in enumerate(regions):
                supply_results[key_name][region_nr] = results_unconstrained[submodel_nr][region_nr][fueltype_int]

    logging.info("Prepared results for energy supply model in unconstrained mode")
    return supply_results

def model_tech_simplification(tech):
    """This function aggregated different technologies
    which are not defined in supply model

    Arguments
    ---------
    tech : str
        Technology

    Returns
    -------
    tech_newly_assigned : str
        Technology newly assigned
    """
    # Assign condensing boiler to regular boilers
    if tech == 'boiler_condensing_gas':
        tech_newly_assigned = 'boiler_gas'
    elif tech == 'boiler_condensing_oil':
        tech_newly_assigned = 'boiler_oil'
    elif tech == 'storage_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    elif tech == 'secondary_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    else:
        tech_newly_assigned = tech

    return tech_newly_assigned
