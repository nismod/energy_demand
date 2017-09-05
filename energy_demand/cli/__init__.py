"""Provides an entry point from the command line to the energy demand model
"""
import os
import sys
from pkg_resources import Requirement
from pkg_resources import resource_filename
from argparse import ArgumentParser
import energy_demand
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions
from energy_demand.scripts.init_scripts import post_install_setup
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.read_write import read_data
from energy_demand.dwelling_stock import dw_stock
from energy_demand.plotting import plotting_results

def init_scenario(args):
    """
    """
    data_energy_demand = args.data_energy_demand
    scenario_initalisation(data_energy_demand)

def run_model(args):
    """
    Main function to run the energy demand model from the command line

    Notes
    -----
    - path_main is the path to the local data e.g. that stored in the package
    - local_data_path is the path to the restricted data which must be provided
    to the model

    #NOTE: TO RUN FROM COMMAND LINE
    """
    #Subfolder where module is installed
    path_main_data = resource_filename(Requirement.parse("energy_demand"), "data")
    path_main = os.path.join(path_main_data, '../')
    local_data_path = args.data_folder

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.load_local_paths(local_data_path)
    data = data_loader.load_fuels(data)
    data = data_loader.load_data_tech_profiles(data)
    data = data_loader.load_data_profiles(data)
    data['sim_param'], data['assumptions'] = assumptions.load_assumptions(data)
    data['assumptions'] = assumptions.update_assumptions(data['assumptions'])
    
    data['weather_stations'], data['temperature_data'] = data_loader.load_data_temperatures(
        data['local_paths']
        )
    data = data_loader.dummy_data_generation(data)

    # Load data from script calculations
    data = read_data.load_script_data(data)

    # Generate dwelling stocks over whole simulation period
    data['rs_dw_stock'] = dw_stock.rs_dw_stock(data['lu_reg'], data)
    data['ss_dw_stock'] = dw_stock.ss_dw_stock(data['lu_reg'], data)

    _, results = energy_demand_model(data)

    print("... Result section")
    #results.all_submodels_sum_uk_specfuelype_enduses_y[2]

    results_every_year = [results]

    print("Finished energy demand model from command line execution")

def parse_arguments():
    """Parse command line arguments

    Returns
    =======
    :class:`argparse.ArgumentParser`

    """
    parser = ArgumentParser(description='Command line tools for energy_demand')
    parser.add_argument('-V', '--version',
                        action='version',
                        version="energy_demand " + energy_demand.__version__,
                        help='show the current version of energy_demand')

    subparsers = parser.add_subparsers()

    # Run main model
    parser_run = subparsers.add_parser(
        'run',
        help='Run the model'
        )
    parser_run.add_argument(
        '-d',
        '--data_folder',
        default='./processed_data',
        help='Path to the input data folder'
        )
    parser_run.set_defaults(func=run_model)

    # Initialisation of energy demand model (processing raw files)
    parser_init = subparsers.add_parser(
        'post_install_setup',
        help='Executes the raw reading functions'
        )
    parser_init.add_argument(
        '-d',
        '--data_energy_demand',
        default='./energy_demand_data',
        help='Path to the input data folder'
        )

    parser_init.set_defaults(func=post_install_setup)

    # Scenario initialisation
    scenario_init = subparsers.add_parser(
        'scenario_initialisation',
        help='Needs to be initialised')

    scenario_init.add_argument(
        '-d',
        '--data_energy_demand',
        default='./data_energy_demand',
        help='Path to main data folder'
        )

    scenario_init.set_defaults(func=init_scenario)

    return parser

def main(arguments=None):
    """Parse args and run
    """
    parser = parse_arguments()
    args = parser.parse_args(arguments)

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main(sys.argv[1:])
