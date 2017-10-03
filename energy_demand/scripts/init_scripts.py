"""Script functions which are executed after model installation and
after each scenario definition
"""
import logging
from pkg_resources import Requirement
from pkg_resources import resource_filename
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions

def post_install_setup(args):
    """Run initialisation scripts

    Arguments
    ----------
    args : object
        Arguments defined in ``./cli/__init__.py``

    Note
    ----
    Only needs to be executed once after the energy_demand
    model has been installed
    """
    logging.debug("... start running initialisation scripts")

    # Paths
    path_main = resource_filename(Requirement.parse("energy_demand"), "")
    local_data_path = args.data_energy_demand

    # Load data
    data = {}
    data['print_criteria'] = True #Print criteria
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['sim_param'], data['assumptions'] = assumptions.load_assumptions(data, write_sim_param=True)
    data['assumptions'] = assumptions.update_assumptions(data['assumptions'])

    # Read in temperature data from raw files
    from energy_demand.scripts import s_raw_weather_data
    s_raw_weather_data.run(data)

    # Read in residenital submodel shapes
    from energy_demand.scripts import s_rs_raw_shapes
    s_rs_raw_shapes.run(data)

    # Read in service submodel shapes
    from energy_demand.scripts import s_ss_raw_shapes
    s_ss_raw_shapes.run(data)

    logging.debug("... finished post_install_setup")

def scenario_initalisation(path_data_energy_demand, data=False):
    """Scripts which need to be run for every different scenario

    Arguments
    ----------
    path_data_energy_demand : str
        Path to the energy demand data folder

    Note
    ----
    Only needs to be executed once for each scenario (not for every
    simulation year)

    The ``path_data_energy_demand`` is the path to the main
    energy demand data folder

    If no data is provided, dummy data is generated TODO
    """
    if data == False:
        run_locally = True
        logging.debug("run_locally".format(run_locally))
    else:
        run_locally = False
        logging.debug("run_asf".format(run_locally))

    path_main = resource_filename(Requirement.parse("energy_demand"), "")

    if run_locally is True:

        data = {}
        data['print_criteria'] = True #Print criteria
        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(path_data_energy_demand)
        data['lookups'] = data_loader.load_basic_lookups()
        data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
        data['sim_param'], data['assumptions'] = assumptions.load_assumptions(data, write_sim_param=True)
        data['assumptions'] = assumptions.update_assumptions(data['assumptions'])
        data = data_loader.dummy_data_generation(data)
    else:
        pass

    # ----------------------------------------------
    from energy_demand.scripts import s_change_temp
    if run_locally is True:
        s_change_temp.run(data['local_paths'], data['assumptions'], data['sim_param'])
        data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(
            data['local_paths'])
    else:
        temperature_data = s_change_temp.read_weather_data_script_data(data['local_paths']['path_processed_weather_data'])
        assumptions_temp_change = data['assumptions']['climate_change_temp_diff_month']
        temp_climate_change = s_change_temp.change_temp_climate_change(temperature_data, assumptions_temp_change, data['sim_param'])

    # ----------------------------------------------
    from energy_demand.scripts import s_fuel_to_service
    if run_locally is True:
        s_fuel_to_service.run(data)
    else:
        fts_cont = {}
        # RESIDENTIAL: Convert base year fuel input assumptions to energy service
        fts_cont['rs_service_tech_by_p'], fts_cont['rs_service_fueltype_tech_by_p'], fts_cont['rs_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
            data['assumptions']['tech_list'],
            data['assumptions']['hybrid_technologies'],
            data['lookups']['fueltype'],
            data['assumptions']['rs_fuel_tech_p_by'],
            data['fuels']['rs_fuel_raw_data_enduses'],
            data['assumptions']['technologies']
            )

        # SERVICE: Convert base year fuel input assumptions to energy service
        fuels_aggregated_across_sectors = s_fuel_to_service.ss_sum_fuel_enduse_sectors(
            data['fuels']['ss_fuel_raw_data_enduses'],
            data['enduses']['ss_all_enduses'],
            data['lookups']['nr_of_fueltypes'])

        fts_cont['ss_service_tech_by_p'], fts_cont['ss_service_fueltype_tech_by_p'], fts_cont['ss_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
            data['assumptions']['tech_list'],
            data['assumptions']['hybrid_technologies'],
            data['lookups']['fueltype'],
            data['assumptions']['ss_fuel_tech_p_by'],
            fuels_aggregated_across_sectors,
            data['assumptions']['technologies']
            )

        # INDUSTRY
        fuels_aggregated_across_sectors = s_fuel_to_service.ss_sum_fuel_enduse_sectors(
            data['fuels']['is_fuel_raw_data_enduses'],
            data['enduses']['is_all_enduses'],
            data['lookups']['nr_of_fueltypes'])

        fts_cont['is_service_tech_by_p'], fts_cont['is_service_fueltype_tech_by_p'], fts_cont['is_service_fueltype_by_p'] = s_fuel_to_service.get_service_fueltype_tech(
            data['assumptions']['tech_list'],
            data['assumptions']['hybrid_technologies'],
            data['lookups']['fueltype'],
            data['assumptions']['is_fuel_tech_p_by'],
            fuels_aggregated_across_sectors,
            data['assumptions']['technologies']
            )

    # ----------------------------------------------
    from energy_demand.scripts import s_generate_sigmoid
    if run_locally is True:
        s_generate_sigmoid.run(data)
    else:
        sgs_cont = {}

        # Read in Services
        rs_service_tech_by_p = fts_cont['rs_service_tech_by_p']
        ss_service_tech_by_p = fts_cont['ss_service_tech_by_p']
        is_service_tech_by_p = fts_cont['is_service_tech_by_p']
        rs_service_fueltype_by_p = fts_cont['rs_service_fueltype_by_p']
        ss_service_fueltype_by_p = fts_cont['ss_service_fueltype_by_p']
        is_service_fueltype_by_p = fts_cont['is_service_fueltype_by_p']

        # Calculate technologies with more, less and constant service based on service switch assumptions
        sgs_cont['rs_tech_increased_service'], sgs_cont['rs_tech_decreased_share'], sgs_cont['rs_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
            rs_service_tech_by_p,
            data['assumptions']['rs_share_service_tech_ey_p'])
        sgs_cont['ss_tech_increased_service'], sgs_cont['ss_tech_decreased_share'], sgs_cont['ss_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
            ss_service_tech_by_p,
            data['assumptions']['ss_share_service_tech_ey_p'])
        sgs_cont['is_tech_increased_service'], sgs_cont['is_tech_decreased_share'], sgs_cont['is_tech_constant_share'] = s_generate_sigmoid.get_tech_future_service(
            is_service_tech_by_p,
            data['assumptions']['is_share_service_tech_ey_p'])

        # Calculate sigmoid diffusion curves based on assumptions about fuel switches

        # --Residential
        sgs_cont['rs_installed_tech'], sgs_cont['rs_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
            data,
            data['assumptions']['rs_service_switches'],
            data['assumptions']['rs_fuel_switches'],
            data['enduses']['rs_all_enduses'],
            sgs_cont['rs_tech_increased_service'],
            data['assumptions']['rs_share_service_tech_ey_p'],
            data['assumptions']['rs_enduse_tech_maxL_by_p'],
            rs_service_fueltype_by_p,
            rs_service_tech_by_p,
            data['assumptions']['rs_fuel_tech_p_by']
            )

        # --Service
        sgs_cont['ss_installed_tech'], sgs_cont['ss_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
            data,
            data['assumptions']['ss_service_switches'],
            data['assumptions']['ss_fuel_switches'],
            data['enduses']['ss_all_enduses'],
            sgs_cont['ss_tech_increased_service'],
            data['assumptions']['ss_share_service_tech_ey_p'],
            data['assumptions']['ss_enduse_tech_maxL_by_p'],
            ss_service_fueltype_by_p,
            ss_service_tech_by_p,
            data['assumptions']['ss_fuel_tech_p_by']
            )

        # --Industry
        sgs_cont['is_installed_tech'], sgs_cont['is_sig_param_tech'] = s_generate_sigmoid.get_sig_diffusion(
            data,
            data['assumptions']['is_service_switches'],
            data['assumptions']['is_fuel_switches'],
            data['enduses']['is_all_enduses'],
            sgs_cont['is_tech_increased_service'],
            data['assumptions']['is_share_service_tech_ey_p'],
            data['assumptions']['is_enduse_tech_maxL_by_p'],
            is_service_fueltype_by_p,
            is_service_tech_by_p,
            data['assumptions']['is_fuel_tech_p_by']
            )

    # ----------------------------------------------
    from energy_demand.scripts import s_disaggregation
    if run_locally is True:
        s_disaggregation.run(data)
    else:
        sd_cont = {}

        data = s_disaggregation.disaggregate_base_demand(data)
        sd_cont['rs_fuel_disagg'] = data['rs_fuel_disagg']
        sd_cont['ss_fuel_disagg'] = data['ss_fuel_disagg']
        sd_cont['is_fuel_disagg'] = data['is_fuel_disagg']
        sd_cont['ts_fuel_disagg'] = data['ts_fuel_disagg']

    logging.debug("...  finished scenario_initalisation")
    if run_locally == False:
        return temp_climate_change, fts_cont, sgs_cont, sd_cont
    else:
        return
