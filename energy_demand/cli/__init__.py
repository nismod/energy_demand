"""Provides an entry point from the command line to the energy demand model
"""
from pkg_resources import Requirement, resource_filename
from argparse import ArgumentParser
import os
import sys
import energy_demand
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions
from energy_demand.scripts._execute_all_scripts import post_install_setup
from energy_demand.scripts._execute_all_scripts import scenario_initalisation
from energy_demand.read_write import read_data
from energy_demand.dwelling_stock import dw_stock

def run_model(args):
    """

    Notes
    -----
    - path_main is the path to the local data e.g. that stored in the package
    - local_data_path is the path to the restricted data which must be provided
    to the model

    """
    #Subfolder where module is installed
    path_main = resource_filename(Requirement.parse("energy_demand"), "")
    local_data_path = args.data_folder

    print("POATHMAIN: " + str(path_main))
    print("local_data_path: " + str(local_data_path))

    # Load data
    base_data = {}
    base_data['paths'] = data_loader.load_paths(path_main)
    base_data = data_loader.load_fuels(base_data)
    base_data = data_loader.load_data_tech_profiles(base_data)
    base_data = data_loader.load_data_profiles(base_data)
    base_data['assumptions'] = assumptions.load_assumptions(base_data)
    base_data['weather_stations'], base_data['temperature_data'] = data_loader.load_data_temperatures(
        os.path.join(base_data['paths']['path_processed_data'], 'weather_data')
        )

    # >>>>>>>>>>>>>>>DUMMY DATA GENERATION
    base_data = data_loader.dummy_data_generation(base_data)
    # <<<<<<<<<<<<<<<<<< FINISHED DUMMY GENERATION DATA

    # Load data from script calculations
    base_data = read_data.load_script_data(base_data)
    
    # Generate dwelling stocks over whole simulation period
    base_data['rs_dw_stock'] = dw_stock.rs_dw_stock(base_data['lu_reg'], base_data)
    base_data['ss_dw_stock'] = dw_stock.ss_dw_stock(base_data['lu_reg'], base_data)

    _, results = energy_demand_model(base_data)

    print(results)

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
    parser_init = subparsers.add_parser(
        'scenario_initialisation',
        help='Needs to be initialised')

    parser_init.add_argument(
        '-d2',
        '--data_energy_demand',
        default='./data_energy_demand', #_processed_data',
        help='path to main data folder' #'Path to the processed data folder'
        )

    parser_init.set_defaults(func=scenario_initalisation)
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