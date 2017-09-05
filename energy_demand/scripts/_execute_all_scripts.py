"""Script functions which are executed after model installation and 
after each scenario definition
"""
from pkg_resources import Requirement, resource_filename

def post_install_setup(args):
    """Run initialisation scripts

    Parameters
    ----------
    args : object
        Arguments defined in ``./cli/__init__.py``

    Note
    ----
    Only needs to be executed once after the energy_demand
    model has been installed
    """
    print("...  start running initialisation scripts")

    #Subfolder where module is installed
    path_main = resource_filename(Requirement.parse("energy_demand"), "") 
    local_data_path = args.data_energy_demand #Energy demand data folder

    # Read in temperature data from raw files
    from energy_demand.scripts import s_raw_weather_data
    s_raw_weather_data.run(local_data_path)

    # Read in residenital submodel shapes
    from energy_demand.scripts import s_rs_raw_shapes
    s_rs_raw_shapes.run(path_main, local_data_path)

    # Read in service submodel shapes
    from energy_demand.scripts import s_ss_raw_shapes
    s_ss_raw_shapes.run(path_main, local_data_path)

def scenario_initalisation(args):
    """Scripts which need to be run for every different scenario

    Parameters
    ----------
    args : object
        Arguments defined in ``./cli/__init__.py``

    Note
    ----
    Only needs to be executed once for each scenario (not for every
    simulation year)

    The ``path_data_processed`` must be in the local path provided to
    post_install_setup
    """
    path_main = resource_filename(Requirement.parse("energy_demand"), "")

    data_energy_demand = args.data_energy_demand
    print("PATH MAIN: " + str(path_main))
    print("processed_data_path: " + str(data_energy_demand))

    from energy_demand.scripts import s_change_temp
    s_change_temp.run(path_main, data_energy_demand)

    from energy_demand.scripts import s_fuel_to_service
    s_fuel_to_service.run(path_main, data_energy_demand)

    from energy_demand.scripts import s_generate_sigmoid
    s_generate_sigmoid.run(path_main, data_energy_demand)

    from energy_demand.scripts import s_disaggregation
    s_disaggregation.run(path_main, data_energy_demand)

    print("...  finished running scripts for the specified scenario")
    return
