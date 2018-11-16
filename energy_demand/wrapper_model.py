"""All necessary calculations in pre_simulate()
"""
import os
import logging
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

def read_yaml(file_path):
    """Parse yaml config file into plain data (lists, dicts and simple values)

    Parameters
    ----------
    file_path : str
        The path of the configuration file to parse
    """
    with open(file_path, 'r') as file_handle:
        return YAML(typ='unsafe').load(file_handle)

def write_yaml(data, file_path):
    """Write plain data to a file as yaml

    Parameters
    ----------
    data
        Data to write (should be lists, dicts and simple values)
    file_path : str
        The path of the configuration file to write
    """
    with open(file_path, 'w') as file_handle:
        yaml = YAML(typ='unsafe')
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        return yaml.dump(data, file_handle)

def load_data_before_simulation(
        data,
        simulation_yrs,
        config,
        curr_yr,
        pop_array_by_new,
        gva_array_by_new,
        gva_data
    ):
    # ---------
    # Configuration
    # -----------
    base_yr = config['CONFIG']['base_yr']
    weather_yr_scenario = config['CONFIG']['weather_yr_scenario']
    name_scenario = data['name_scenario_run']
    path_new_scenario = data['path_new_scenario']

    data['weather_station_count_nr'] = [] # Default value is '[]' to use all stations
    data['data_path'] = os.path.normpath(config['PATHS']['path_local_data'])
    data['processed_path'] = os.path.normpath(config['PATHS']['path_processed_data'])
    data['result_path'] = os.path.normpath(config['PATHS']['path_result_data'])
    data['paths'] = data_loader.load_paths(
        resource_filename(
            Requirement.parse("energy_demand"),
            os.path.join("energy_demand", "config_data")))

    # Downloaded (FTP) data
    data['local_paths'] = data_loader.get_local_paths(
        data['data_path'])

    # TODO REMOVE
    user_defined_config_path = os.path.join(
        config['PATHS']['path_local_data'],
        '00_user_defined_variables_SCENARIO',
        '03_paperI_scenarios',
        name_scenario)

    # ------------------------------------------------
    # Load Inputs
    # ------------------------------------------------
    data['enduses'], data['sectors'], data['fuels'], lookup_enduses, lookup_sector_enduses = data_loader.load_fuels(
        data['paths'])

    # ------------------------------------------------
    # Load Assumptions
    # ------------------------------------------------
    data['assumptions'] = general_assumptions.Assumptions(
        lookup_enduses=lookup_enduses,
        lookup_sector_enduses=lookup_sector_enduses,
        base_yr=base_yr,
        weather_by=config['CONFIG']['user_defined_weather_by'],
        simulation_end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
        curr_yr=curr_yr,
        simulated_yrs=simulation_yrs,
        paths=data['paths'],
        local_paths=data['local_paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        reg_nrs=len(data['regions']))

    # Load all temperature and weather station data
    data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(
        data['local_paths'],
        weather_yrs_scenario=[base_yr, weather_yr_scenario],
        save_fig=path_new_scenario)

    # --------------------------------------------
    # Make selection of weather stations and data
    # --------------------------------------------
    weather_stations_selection = {}
    temp_data_selection = {}
    if data['weather_station_count_nr'] != []:
        for year in [data['assumptions'].base_yr, weather_yr_scenario]:
            weather_stations_selection[year], station_id = weather_region.get_weather_station_selection(
                data['weather_stations'],
                counter=data['weather_station_count_nr'],
                weather_yr = weather_yr_scenario)
            temp_data_selection[year] = data['temp_data'][year][station_id]

            if year == weather_yr_scenario:
                data['simulation_name'] = str(weather_yr_scenario) + "__" + str(station_id)
    else:
        for year in [data['assumptions'].base_yr,  weather_yr_scenario]:
            weather_stations_selection[year] = data['weather_stations'][year]
            temp_data_selection[year] = data['temp_data'][year]

            if year == weather_yr_scenario:
                data['simulation_name'] = str(weather_yr_scenario) + "__" + "all_stations"

    # Replace weather station with selection
    data['weather_stations'] = weather_stations_selection
    data['temp_data'] = temp_data_selection

    # ------------------------------------------
    # Make selection of regions to model
    # ------------------------------------------
    if config['CRITERIA']['reg_selection']:
        
        region_selection = read_data.get_region_selection(
            os.path.join(data['local_paths']['local_path_datafolder'],
            "region_definitions",
            config['CRITERIA']['reg_selection_csv_name']))
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
        os.path.join(data['result_path'], name_scenario, data['simulation_name']))

    data['result_paths'] = data_loader.get_result_paths(path_folder_weather_yr)

    folders_to_create = [
        path_folder_weather_yr,
        data['result_paths']['data_results'],
        data['result_paths']['data_results_PDF'],
        data['result_paths']['data_results_validation'],
        data['result_paths']['data_results_model_runs']]
    for folder in folders_to_create:
        basic_functions.create_folder(folder)

    # ------------------------------------------------
    # Load load profiles of technologies
    # ------------------------------------------------
    data['tech_lp'] = data_loader.load_data_profiles(
        data['paths'],
        data['local_paths'],
        data['assumptions'].model_yeardays,
        data['assumptions'].model_yeardays_daytype)

    # ------------------------------------------------
    # SCENARIO DATA
    # ------------------------------------------------
    data['scenario_data']['population'][data['assumptions'].base_yr] = pop_array_by_new
    data['scenario_data']['gva_per_head'][data['assumptions'].base_yr] = gva_array_by_new
    data['scenario_data']['gva_industry'][data['assumptions'].base_yr] = gva_data

    # Obtain population data for disaggregation
    if config['CRITERIA']['MSOA_crit']:
        name_population_dataset = data['local_paths']['path_population_data_for_disaggregation_MSOA']
    else:
        name_population_dataset = data['local_paths']['path_population_data_for_disaggregation_LAD']
    data['pop_for_disag'] = data_loader.read_scenario_data(name_population_dataset)

    # ------------------------------------------------
    # Load building related data
    # ------------------------------------------------
    if config['CRITERIA']['virtual_building_stock_criteria']:
        data['scenario_data']['floor_area']['rs_floorarea'], data['scenario_data']['floor_area']['ss_floorarea'], data['service_building_count'], rs_regions_without_floorarea, ss_regions_without_floorarea = data_loader.floor_area_virtual_dw(
            data['regions'],
            data['sectors'],
            data['local_paths'],
            data['scenario_data']['population'][data['assumptions'].base_yr],
            base_yr=data['assumptions'].base_yr)

        # Add all areas with no floor area data
        data['assumptions'].update("rs_regions_without_floorarea", rs_regions_without_floorarea)
        data['assumptions'].update("ss_regions_without_floorarea", ss_regions_without_floorarea)
    else:
        # ------------------------------------------------
        # Load floor area directly from Newcastle
        # ------------------------------------------------
        #rs_floorarea = defaultdict(dict)
        #ss_floorarea = defaultdict(dict)
        pass

    # Load all standard variables of parameters
    default_streategy_vars = strategy_vars_def.load_param_assump(
        assumptions=data['assumptions'])

    # -----------------------------------------------------------------------------
    # Load standard smif parameters and generate standard single timestep narrative
    # for the year 2050 for all parameters
    # -----------------------------------------------------------------------------
    strategy_vars = strategy_vars_def.load_smif_parameters(
        assumptions=data['assumptions'],
        default_streategy_vars=default_streategy_vars)

    # -----------------------------------------
    # Read user defined stragey variable from csv files
    # TODO with smif update: Needs to be read in by SMIF and passed on directly to here
    # -----------------------------------------
    _user_defined_vars = data_loader.load_user_defined_vars(
        default_strategy_var=default_streategy_vars,
        path_csv=user_defined_config_path,
        simulation_base_yr=data['assumptions'].base_yr,
        simulation_end_yr=data['assumptions'].simulation_end_yr)

    logging.info("All user_defined parameters %s", _user_defined_vars.keys())

    # --------------------------------------------------------
    # Replace standard narratives with user defined narratives from .csv files
    # --------------------------------------------------------
    strategy_vars = data_loader.replace_variable(
        _user_defined_vars, strategy_vars)

    strategy_vars_out = strategy_vars_def.autocomplete_strategy_vars(
        strategy_vars, narrative_crit=True)

    data['assumptions'].update('strategy_vars', strategy_vars_out)

    # Update technologies after strategy definition
    technologies = general_assumptions.update_technology_assumption(
        data['assumptions'].technologies,
        data['assumptions'].strategy_vars['f_eff_achieved'],
        data['assumptions'].strategy_vars['gshp_fraction_ey'])
    data['assumptions'].technologies.update(technologies)

    return data

def before_simulation(
        data,
        config,
        simulation_yrs,
        pop_density
    ):
    """
    """
    # ------------------------------------------------
    # Disaggregate national energy demand to regional demands
    # ------------------------------------------------
    fuel_disagg = s_disaggregation.disaggr_demand(
        data,
        spatial_calibration=config['CRITERIA']['spatial_calibration'])

    # ------------------------------------------------
    # Calculate spatial diffusion factors
    #
    # Here the real values used for the spatial disaggregation (speec_con_max)
    # need to be defined. If not population density is used,
    # this needs to be replaced by any other values which are loaded from
    # a csv file in the form of: {{region_name: value}}
    # ------------------------------------------------
    f_reg, f_reg_norm, f_reg_norm_abs, crit_all_the_same = init_scripts.create_spatial_diffusion_factors(
        narrative_spatial_explicit_diffusion=data['assumptions'].strategy_vars['spatial_explicit_diffusion'],
        fuel_disagg=fuel_disagg,
        regions=data['regions'],
        real_values=pop_density,
        narrative_speed_con_max=data['assumptions'].strategy_vars['speed_con_max'])

    # ------------------------------------------------
    # Calculate parameter values for every region
    # ------------------------------------------------
    regional_vars = init_scripts.spatial_explicit_modelling_strategy_vars(
        data['assumptions'].strategy_vars,
        data['assumptions'].spatially_modelled_vars,
        data['regions'],
        fuel_disagg,
        f_reg,
        f_reg_norm,
        f_reg_norm_abs)
    data['assumptions'].update('strategy_vars', regional_vars)

    # ------------------------------------------------
    # Calculate parameter values for every simulated year
    # based on narratives. Also calculate annual parameters for
    # technologies diffused by switches.
    # ------------------------------------------------
    regional_vars, non_regional_vars = s_scenario_param.generate_annual_param_vals(
        data['regions'],
        data['assumptions'].strategy_vars,
        simulation_yrs)

    # ------------------------------------------------
    # Switches calculations
    # ------------------------------------------------
    annual_tech_diff_params = init_scripts.switch_calculations(
        simulation_yrs,
        data,
        f_reg,
        f_reg_norm,
        f_reg_norm_abs,
        crit_all_the_same)

    for region in data['regions']:
        regional_vars[region]['annual_tech_diff_params'] = annual_tech_diff_params[region]

    return regional_vars, non_regional_vars, fuel_disagg

def write_user_defined_results(
        criterias,
        result_paths,
        sim_obj,
        data,
        curr_yr,
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
            curr_yr,
            "ed_fueltype_regs_yh",
            result_paths['data_results_model_runs'],
            sim_obj.ed_fueltype_regs_yh,
            "result_tot_submodels_fueltypes")
        write_data.write_enduse_specific(
            curr_yr,
            result_paths['data_results_model_runs'],
            sim_obj.tot_fuel_y_enduse_specific_yh,
            "out_enduse_specific")
        write_data.write_lf(
            result_paths['data_results_model_runs'], "result_reg_load_factor_y",
            [curr_yr], sim_obj.reg_load_factor_y, 'reg_load_factor_y')
        write_data.write_lf(
            result_paths['data_results_model_runs'], "result_reg_load_factor_yd",
            [curr_yr], sim_obj.reg_load_factor_yd, 'reg_load_factor_yd')

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
            year=curr_yr,
            submodels_names=data['assumptions'].submodels_names)

        # Write out elec
        demand_supply_interaction.write_national_results(
            path_folder=result_paths,
            results_unconstrained=sim_obj.results_unconstrained,
            enduse_specific_results=sim_obj.tot_fuel_y_enduse_specific_yh,
            fueltype_str='electricity',
            fuelype_nr=tech_related.get_fueltype_int('electricity'),
            year=curr_yr,
            submodels_names=data['assumptions'].submodels_names)

    # ------------------------------------------------
    # Temporal Validation
    # ------------------------------------------------
    if (criterias['validation_criteria'] == True) and (
        curr_yr == data['assumptions'].base_yr) and (
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

def plots(
        data,
        curr_yr,
        fuel_disagg, 
        config
    ):
    """
    """
    # Spatial validation
    if (config['CRITERIA']['validation_criteria'] == True) and (
        curr_yr == data['assumptions'].base_yr) and (
            config['CRITERIA']['cluster_calc'] != True):
        lad_validation.spatial_validation_lad_level(
            fuel_disagg,
            data['result_paths'],
            data['paths'],
            data['regions'],
            data['reg_coord'],
            plot_crit=False)

    # Plot map with weather station
    if config['CRITERIA']['cluster_calc'] != True:
        data_loader.create_weather_station_map(
            data['weather_stations'][config['CONFIG']['weather_yr_scenario']],
            os.path.join(data['result_path'], 'weatherst_distr_weathyr_{}.pdf'.format(
                config['CONFIG']['weather_yr_scenario'])),
            path_shapefile=data['local_paths']['lad_shapefile'])
