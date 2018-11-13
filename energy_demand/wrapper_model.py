"""All necessary calculations in pre_simulate()
"""
import os
import logging
from collections import defaultdict
from pkg_resources import Requirement, resource_filename
from ruamel.yaml import YAML

from energy_demand.read_write import data_loader
from energy_demand.basic import basic_functions
from energy_demand.scripts import init_scripts
from energy_demand.read_write import write_data
from energy_demand.assumptions import strategy_vars_def
from energy_demand.assumptions import general_assumptions
from energy_demand.validation import lad_validation
from energy_demand.scripts import s_disaggregation
from energy_demand.basic import demand_supply_interaction
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.scripts import s_scenario_param
from energy_demand.geography import weather_region

def write_yaml(data_to_dump, file_path):
    yaml = YAML()
    yaml.dump(data_to_dump, file_path)

def read_yaml(file_path):
    yaml = YAML() #typ='safe')   # default, if not specfied, is 'rt' (round-trip)
    yaml.load(file_path)
    return yaml

def write_jason(data_to_dump, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(data_to_dump, outfile)

def read_jason(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data

def load_general_data(
        data_handle,
        name_scenario,
        region_set_name,
        result_path
    ):
    """
    """
    general_data = {}
    general_data['criterias'] = {}
    general_data['criterias']['mode_constrained'] = True                      # True: Technologies are defined in ED model and fuel is provided, False: Heat is delievered not per technologies
    general_data['criterias']['virtual_building_stock_criteria'] = True       # True: Run virtual building stock model
    general_data['criterias']['validation_criteria'] = True                   # Validation is performed

    general_data['criterias']['write_txt_additional_results'] = True          # Additional results are written to file
    general_data['criterias']['write_out_national'] = False                   # National rseults for modassar

    # Configuration if simulated regions is not the same as shapefile regions
    general_data['criterias']['reg_selection'] = False
    general_data['criterias']['MSOA_crit'] = False
    general_data['criterias']['reg_selection_csv_name'] = "msoa_regions_ed.csv" # CSV file stored in 'region' folder with simulated regions
    general_data['criterias']['spatial_calibration'] = False
    general_data['criterias']['cluster_calc'] = False

    general_data['regions'] = data_handle.get_region_names(region_set_name)


    general_data['name_scenario_run'] = name_scenario

    path_new_scenario = os.path.join(result_path, name_scenario)
    general_data['path_new_scenario'] = path_new_scenario
    general_data['result_paths'] = data_loader.get_result_paths(path_new_scenario)

    # Delete previous model results
    basic_functions.del_previous_setup(general_data['result_paths']['data_results'])
    basic_functions.create_folder(path_new_scenario)

    folders_to_create = [
        general_data['result_paths']['data_results_model_run_pop'],
        general_data['result_paths']['data_results_validation']]
    for folder in folders_to_create:
        basic_functions.create_folder(folder)

    return general_data

def before_simulation(
        self,
        general_data,
        config,
        name_scenario,
        path_new_scenario,
        curr_yr,
        pop_array_by_new,
        gva_array_by_new,
        pop_density,
        gva_data
    ):
    """
    """
    # ---------
    # Configuration
    # -----------
    self.user_data['weather_yr_scenario'] = int(config['CONFIG']['weather_yr_scenario'])        # Default only run for base year
    self.user_data['weather_station_count_nr'] = []                                             # Default value is '[]' to use all stations

    self.user_data['data']['data_path'] = os.path.normpath(config['PATHS']['path_local_data'])
    self.user_data['data']['processed_path'] = os.path.normpath(config['PATHS']['path_processed_data'])
    self.user_data['data']['result_path'] = os.path.normpath(config['PATHS']['path_result_data'])
    self.user_data['data']['paths'] = data_loader.load_paths(
        resource_filename(
            Requirement.parse("energy_demand"),
            os.path.join("energy_demand", "config_data")))

    # Downloaded (FTP) data
    self.user_data['data']['local_paths'] = data_loader.get_local_paths(
        self.user_data['data']['data_path'])

    # TODO REMOVE
    user_defined_config_path = os.path.join(
        str(config['PATHS']['path_local_data']),
        '00_user_defined_variables_SCENARIO',
        '03_paperI_scenarios',
        name_scenario)

    # -----------------------------
    # Region related info
    # -----------------------------
    self.user_data['data']['regions'] = general_data['regions']
    self.user_data['data']['reg_coord'] = general_data['reg_cord']

    # ------------------------------------------------
    # Load Inputs
    # ------------------------------------------------
    self.user_data['data']['enduses'], self.user_data['data']['sectors'], self.user_data['data']['fuels'], lookup_enduses, lookup_sector_enduses = data_loader.load_fuels(
        self.user_data['data']['paths'])

    # ------------------------------------------------
    # Load Assumptions
    # ------------------------------------------------
    self.user_data['data']['assumptions'] = general_assumptions.Assumptions(
        lookup_enduses=lookup_enduses,
        lookup_sector_enduses=lookup_sector_enduses,
        base_yr=int(config['CONFIG']['base_yr']),
        weather_by=int(config['CONFIG']['user_defined_weather_by']),
        simulation_end_yr=int(config['CONFIG']['user_defined_simulation_end_yr']),
        curr_yr=curr_yr,
        simulated_yrs=self.timesteps,
        paths=self.user_data['data']['paths'],
        local_paths=self.user_data['data']['local_paths'],
        enduses=self.user_data['data']['enduses'],
        sectors=self.user_data['data']['sectors'],
        reg_nrs=len(general_data['regions']))

    # ------------------------------------------------
    # Load load profiles of technologies
    # ------------------------------------------------
    self.user_data['data']['tech_lp'] = data_loader.load_data_profiles(
        self.user_data['data']['paths'],
        self.user_data['data']['local_paths'],
        self.user_data['data']['assumptions'].model_yeardays,
        self.user_data['data']['assumptions'].model_yeardays_daytype)

    # ------------------------------------------------
    # Load base year scenario data
    # ------------------------------------------------
    self.user_data['data']['scenario_data'] = defaultdict(dict)

    if self.timesteps[0] != self.user_data['data']['assumptions'].base_yr:
        raise Exception("The first defined year in model config does not correspond to the hardcoded base year")

    self.user_data['data']['scenario_data']['population'][self.user_data['data']['assumptions'].base_yr] = pop_array_by_new
    self.user_data['data']['scenario_data']['gva_per_head'][self.user_data['data']['assumptions'].base_yr] = gva_array_by_new

    # Load sector specific GVA data, if available
    self.user_data['data']['scenario_data']['gva_industry'][self.user_data['data']['assumptions'].base_yr] = gva_data

    # Obtain population data for disaggregation
    if general_data['criterias']['MSOA_crit']:
        name_population_dataset = self.user_data['data']['local_paths']['path_population_data_for_disaggregation_MSOA']
    else:
        name_population_dataset = self.user_data['data']['local_paths']['path_population_data_for_disaggregation_LAD']
    self.user_data['data']['pop_for_disag'] =  data_loader.read_scenario_data(name_population_dataset)

    # ------------------------------------------------
    # Load building related data
    # ------------------------------------------------
    if general_data['criterias']['virtual_building_stock_criteria']:
        self.user_data['data']['scenario_data']['floor_area']['rs_floorarea'], self.user_data['data']['scenario_data']['floor_area']['ss_floorarea'], self.user_data['data']['service_building_count'], rs_regions_without_floorarea, ss_regions_without_floorarea = data_loader.floor_area_virtual_dw(
            general_data['regions'],
            self.user_data['data']['sectors'],
            self.user_data['data']['local_paths'],
            self.user_data['data']['scenario_data']['population'][self.user_data['data']['assumptions'].base_yr],
            base_yr=self.user_data['data']['assumptions'].base_yr)

        # Add all areas with no floor area data
        self.user_data['data']['assumptions'].update("rs_regions_without_floorarea", rs_regions_without_floorarea)
        self.user_data['data']['assumptions'].update("ss_regions_without_floorarea", ss_regions_without_floorarea)
    else:
        # ------------------------------------------------
        # Load floor area directly from Newcastle
        # ------------------------------------------------
        #rs_floorarea = defaultdict(dict)
        #ss_floorarea = defaultdict(dict)
        pass

    # ----------------------------------------------
    # Calculate population density for base year
    # ----------------------------------------------
    self.user_data['data']['pop_density'] = pop_density

    # Load all standard variables of parameters
    default_streategy_vars = strategy_vars_def.load_param_assump(
        assumptions=self.user_data['data']['assumptions'])

    # -----------------------------------------------------------------------------
    # Load standard smif parameters and generate standard single timestep narrative
    # for the year 2050 for all parameters
    # -----------------------------------------------------------------------------
    strategy_vars = strategy_vars_def.load_smif_parameters(
        #data_handle,
        assumptions=self.user_data['data']['assumptions'],
        default_streategy_vars=default_streategy_vars)

    # -----------------------------------------
    # Read user defined stragey variable from csv files
    # TODO with smif update: Needs to be read in by SMIF and passed on directly to here
    # -----------------------------------------
    _user_defined_vars = data_loader.load_user_defined_vars(
        default_strategy_var=default_streategy_vars,
        path_csv=user_defined_config_path,
        simulation_base_yr=self.user_data['data']['assumptions'].base_yr,
        simulation_end_yr=self.user_data['data']['assumptions'].simulation_end_yr)

    logging.info("All user_defined parameters %s", _user_defined_vars.keys())

    # --------------------------------------------------------
    # Replace standard narratives with user defined narratives from .csv files
    # --------------------------------------------------------
    strategy_vars = data_loader.replace_variable(
        _user_defined_vars, strategy_vars)

    strategy_vars_out = strategy_vars_def.autocomplete_strategy_vars(
        strategy_vars, narrative_crit=True)

    self.user_data['data']['assumptions'].update('strategy_vars', strategy_vars_out)

    # Update technologies after strategy definition
    technologies = general_assumptions.update_technology_assumption(
        self.user_data['data']['assumptions'].technologies,
        self.user_data['data']['assumptions'].strategy_vars['f_eff_achieved'],
        self.user_data['data']['assumptions'].strategy_vars['gshp_fraction_ey'])
    self.user_data['data']['technologies'].update(technologies)

    # Load all temperature and weather station data
    self.user_data['data']['weather_stations'], self.user_data['data']['temp_data'] = data_loader.load_temp_data(
        self.user_data['data']['local_paths'],
        weather_yrs_scenario=[self.user_data['data']['assumptions'].base_yr, self.user_data['weather_yr_scenario']],
        save_fig=path_new_scenario)

    # --------------------------------------------
    # Make selection of weather stations and data
    # --------------------------------------------
    weather_stations_selection = {}
    temp_data_selection = {}
    if self.user_data['weather_station_count_nr'] != []:
        for year in [self.user_data['data']['assumptions'].base_yr, self.user_data['weather_yr_scenario']]:
            weather_stations_selection[year], station_id = weather_region.get_weather_station_selection(
                self.user_data['data']['weather_stations'],
                counter=self.user_data['weather_station_count_nr'],
                weather_yr = self.user_data['weather_yr_scenario'])
            temp_data_selection[year] = self.user_data['data']['temp_data'][year][station_id]

            if year ==  self.user_data['weather_yr_scenario']:
                self.user_data['simulation_name'] = str( self.user_data['weather_yr_scenario']) + "__" + str(station_id)
    else:
        for year in [self.user_data['data']['assumptions'].base_yr,  self.user_data['weather_yr_scenario']]:
            weather_stations_selection[year] = self.user_data['data']['weather_stations'][year]
            temp_data_selection[year] = self.user_data['data']['temp_data'][year]

            if year == self.user_data['weather_yr_scenario']:
                self.user_data['simulation_name'] = str(self.user_data['weather_yr_scenario']) + "__" + "all_stations"

    # Replace weather station with selection
    self.user_data['data']['weather_stations'] = weather_stations_selection
    self.user_data['data']['temp_data'] = temp_data_selection

    # Plot map with weather station
    if general_data['criterias']['cluster_calc'] != True:
        data_loader.create_weather_station_map(
            self.user_data['data']['weather_stations'][self.user_data['weather_yr_scenario']],
            os.path.join(self.user_data['data']['result_path'], 'weatherst_distr_weathyr_{}.pdf'.format( self.user_data['weather_yr_scenario'])),
            path_shapefile=self.user_data['data']['local_paths']['lad_shapefile'])

    # ------------------------------------------------
    # Disaggregate national energy demand to regional demands
    # ------------------------------------------------
    self.user_data['data']['fuel_disagg'] = s_disaggregation.disaggr_demand(
        self.user_data['data'],
        spatial_calibration=general_data['criterias']['spatial_calibration'])

    # ------------------------------------------------
    # Calculate spatial diffusion factors
    #
    # Here the real values used for the spatial disaggregation (speec_con_max)
    # need to be defined. If not population density is used,
    # this needs to be replaced by any other values which are loaded from
    # a csv file in the form of: {{region_name: value}}
    # ------------------------------------------------
    real_values = self.user_data['data']['pop_density']

    f_reg, f_reg_norm, f_reg_norm_abs, crit_all_the_same = init_scripts.create_spatial_diffusion_factors(
        narrative_spatial_explicit_diffusion=self.user_data['data']['assumptions'].strategy_vars['spatial_explicit_diffusion'],
        fuel_disagg=self.user_data['data']['fuel_disagg'],
        regions=general_data['regions'],
        real_values=real_values,
        narrative_speed_con_max=self.user_data['data']['assumptions'].strategy_vars['speed_con_max'])

    # ------------------------------------------------
    # Calculate parameter values for every region
    # ------------------------------------------------
    regional_vars = init_scripts.spatial_explicit_modelling_strategy_vars(
        self.user_data['data']['assumptions'].strategy_vars,
        self.user_data['data']['assumptions'].spatially_modelled_vars,
        general_data['regions'],
        self.user_data['data']['fuel_disagg'],
        f_reg,
        f_reg_norm,
        f_reg_norm_abs)
    self.user_data['data']['assumptions'].update('strategy_vars', regional_vars)

    # ------------------------------------------------
    # Calculate parameter values for every simulated year
    # based on narratives. Also calculate annual parameters for
    # technologies diffused by switches.
    # ------------------------------------------------
    regional_vars, non_regional_vars = s_scenario_param.generate_annual_param_vals(
        general_data['regions'],
        self.user_data['data']['assumptions'].strategy_vars,
        self.timesteps)

    # ------------------------------------------------
    # Switches calculations
    # ------------------------------------------------
    annual_tech_diff_params = init_scripts.switch_calculations(
        self.timesteps,
        self.user_data['data'],
        f_reg,
        f_reg_norm,
        f_reg_norm_abs,
        crit_all_the_same)

    # Add to regional_vars
    for region in general_data['regions']:
        regional_vars[region]['annual_tech_diff_params'] = annual_tech_diff_params[region]

    return regional_vars, non_regional_vars

def load_data(
        self,
        data,
        curr_yr,
        data_handle,
        general_data,
        path_new_scenario,
        name_scenario
    ):
    """
    """


    # Set current year
    data['assumptions'].update('curr_yr', curr_yr)

    # Update technological efficiencies for specific year according to narrative
    data['technologies'] = general_assumptions.update_technology_assumption(
        technologies=data['assumptions'].technologies,
        narrative_f_eff_achieved=data['assumptions'].non_regional_vars['f_eff_achieved'][curr_yr],
        narrative_gshp_fraction_ey=data['assumptions'].non_regional_vars['gshp_fraction_ey'][curr_yr],
        crit_narrative_input=False)

    # --------------------------------------------
    # Load scenario data for current year
    # --------------------------------------------
    pop_array_cy = data_handle.get_data('population')   # of simulation year
    gva_array_cy = data_handle.get_data('gva_per_head') # of simulation year

    data['scenario_data']['population'][curr_yr] = basic_functions.assign_array_to_dict(
        pop_array_cy, data['regions'])
    data['scenario_data']['gva_per_head'][curr_yr] = basic_functions.assign_array_to_dict(
        gva_array_cy, data['regions'])

    # Write population data to file
    write_data.write_scenaric_population_data(
        data_handle.current_timestep,
        os.path.join(path_new_scenario, 'model_run_pop'),
        pop_array_cy[:, 0])

    # Sector specific GVA data
    data['scenario_data']['gva_industry'][curr_yr] = load_gva_sector(
            data_handle=data_handle,
            regions=data['regions'],
            sectors_to_load=[2, 3, 4, 5, 6, 8, 9, 29, 11, 12, 10, 15, 14, 19, 17, 40, 41, 28, 35, 23, 27],
            MSOA_crit=False,
            simulate=False)

    # ------------------------------------------------
    # Spatial Validation
    # ------------------------------------------------
    if (general_data['criterias']['validation_criteria'] == True) and (
        data_handle.current_timestep == data['assumptions'].base_yr) and (
            general_data['criterias']['cluster_calc'] != True):
        lad_validation.spatial_validation_lad_level(
            data['fuel_disagg'],
            general_data['result_paths'],
            data['paths'],
            data['regions'],
            data['reg_coord'],
            plot_crit=False)

    # ------------------------------------------
    # Make selection of regions to model
    # ------------------------------------------
    if general_data['criterias']['reg_selection']:
        
        region_selection = read_data.get_region_selection(
            os.path.join(self.user_data['data']['local_paths']['local_path_datafolder'],
            "region_definitions",
            general_data['criterias']['reg_selection_csv_name']))
        #region_selection = ['E02003237', 'E02003238']
        setattr(data['assumptions'], 'reg_nrs', len(region_selection))
    else:
        region_selection = data['regions']

    # Create .ini file with simulation parameter
    write_data.write_simulation_inifile(
        path_new_scenario, data, region_selection)

    # -------------------------------------------
    # Weather year specific initialisations
    # -------------------------------------------
    path_folder_weather_yr = os.path.join(
        os.path.join(self.user_data['data']['result_path'],
        name_scenario,
        self.user_data['simulation_name']))

    data['result_paths'] = data_loader.get_result_paths(path_folder_weather_yr)

    folders_to_create = [
        path_folder_weather_yr,
        general_data['result_paths']['data_results'],
        general_data['result_paths']['data_results_PDF'],
        general_data['result_paths']['data_results_validation'],
        general_data['result_paths']['data_results_model_runs']]
    for folder in folders_to_create:
        basic_functions.create_folder(folder)

    return region_selection, data

def write_user_defined_results(
        criterias,
        result_paths,
        sim_obj,
        data,
        data_handle,
        region_selection
    ):
    """
    Write annual results to files
    """

    logging.info("... Start writing results to file")
    if criterias['write_txt_additional_results']:
        # Write full results (Note: Results in very large data written to file)
        ##write_data.write_full_results(
        ##    data_handle.current_timestep,
        ##    data['result_paths']['data_results_model_runs'],
        ##    sim_obj.ed_submodel_enduse_fueltype_regs_yh, #TODO CHANGED FORMAT
        ##    "out_enduse_specific")
        write_data.write_supply_results(
            data_handle.current_timestep,
            "ed_fueltype_regs_yh",
            result_paths['data_results_model_runs'],
            sim_obj.ed_fueltype_regs_yh,
            "result_tot_submodels_fueltypes")
        write_data.write_enduse_specific(
            data_handle.current_timestep,
            result_paths['data_results_model_runs'],
            sim_obj.tot_fuel_y_enduse_specific_yh,
            "out_enduse_specific")
        write_data.write_lf(
            result_paths['data_results_model_runs'], "result_reg_load_factor_y",
            [data_handle.current_timestep], sim_obj.reg_load_factor_y, 'reg_load_factor_y')
        write_data.write_lf(
            result_paths['data_results_model_runs'], "result_reg_load_factor_yd",
            [data_handle.current_timestep], sim_obj.reg_load_factor_yd, 'reg_load_factor_yd')

    # ----------------------------------------------------------------------------------------
    # Write out national demand for every fueltype (used for first sending of demand data)
    # ----------------------------------------------------------------------------------------
    if criterias['write_out_national']:

        # Write out gas
        demand_supply_interaction.write_national_results(
            path_folder=result_paths,
            results_unconstrained=sim_obj.results_unconstrained,
            enduse_specific_results=sim_obj.tot_fuel_y_enduse_specific_yh,
            fueltype_str='gas',
            fuelype_nr=tech_related.get_fueltype_int('gas'),
            year=data_handle.current_timestep,
            submodels_names=data['assumptions'].submodels_names)

        # Write out elec
        demand_supply_interaction.write_national_results(
            path_folder=result_paths,
            results_unconstrained=sim_obj.results_unconstrained,
            enduse_specific_results=sim_obj.tot_fuel_y_enduse_specific_yh,
            fueltype_str='electricity',
            fuelype_nr=tech_related.get_fueltype_int('electricity'),
            year=data_handle.current_timestep,
            submodels_names=data['assumptions'].submodels_names)

    # ------------------------------------------------
    # Temporal Validation
    # ------------------------------------------------
    if (criterias['validation_criteria'] == True) and (
        data_handle.current_timestep == data['assumptions'].base_yr) and (
           ['cluster_calc'] != True):
        lad_validation.spatio_temporal_val(
            sim_obj.ed_fueltype_national_yh,
            sim_obj.ed_fueltype_regs_yh,
            result_paths,
            data['paths'],
            region_selection,
            data['assumptions'].seasons,
            data['assumptions'].model_yeardays_daytype,
            plot_crit=False)

def load_gva_sector(
        data_handle,
        regions,
        sectors_to_load,
        MSOA_crit,
        simulate=False
    ):
    """Load sector specific GVA

    Arguments
    ---------
    data_handle : object
        Data handler
    pop_array : array
        Population
    regions : list
        Regions
    sectors_to_load : list
        Sectors which are loaded
    MSOA_crit : bool
        Criteria wheter modelled on MSOA level or LAD level
    simulate : bool
        Criteria wheter run in simulate() or not
    """
    sector_data = {}
    if MSOA_crit:
        logging.info("Don't load sector GVA {}")
    else:
        for gva_sector_nr in sectors_to_load:
            try:
                logging.info("... Loading GVA data for sector_Nr {}".format(gva_sector_nr))
                if simulate:
                    gva_sector_data = data_handle.get_data(
                        'gva_per_head_sector__{}'.format(gva_sector_nr))
                else:
                    gva_sector_data = data_handle.get_base_timestep_data(
                        'gva_per_head_sector__{}'.format(gva_sector_nr))

                sector_data[gva_sector_nr] = basic_functions.assign_array_to_dict(
                    gva_sector_data, regions)
            except KeyError:
                # In case no data could be loaded, generate constant dummy data
                raise Exception("Could not load data %s", 'gva_per_head_sector__{}'.format(gva_sector_nr))

    return sector_data