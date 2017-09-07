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
    data['fuels'] = data_loader.load_fuels(data)
    data['sim_param'], data['assumptions'] = assumptions.load_assumptions(data)
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
    if data:
        run_locally = False
    else:
        run_locally = True

    path_main = resource_filename(Requirement.parse("energy_demand"), "")

    if run_locally is True:
        data = {}
        data['print_criteria'] = True #Print criteria
        data['paths'] = data_loader.load_paths(path_main)
        data['local_paths'] = data_loader.load_local_paths(path_data_energy_demand)
        data['lookups'] = data_loader.load_basic_lookups()
        data['fuels'] = data_loader.load_fuels(data)
        data['sim_param'], data['assumptions'] = assumptions.load_assumptions(data)
        data['assumptions'] = assumptions.update_assumptions(data['assumptions'])
        data = data_loader.dummy_data_generation(data)
    else:
        pass

    from energy_demand.scripts import s_change_temp
    s_change_temp.run(data['local_paths'], data['assumptions'], data['sim_param'])

    if run_locally is True:
        data['weather_stations'], data['temp_data'] = data_loader.load_temp_data(
            data['local_paths'])
    else:
        pass

    from energy_demand.scripts import s_fuel_to_service
    s_fuel_to_service.run(data)

    from energy_demand.scripts import s_generate_sigmoid
    s_generate_sigmoid.run(data)

    from energy_demand.scripts import s_disaggregation
    s_disaggregation.run(data)

    logging.debug("...  finished scenario_initalisation")
    return
