"""Provides an entry point from the command line to the energy demand model
"""
from argparse import ArgumentParser
import energy_demand
from energy_demand.main import energy_demand_model
from energy_demand.read_write import data_loader
from energy_demand.assumptions import assumptions
import os

def run_model(args):
    """

    Notes
    -----
    - path_main is the path to the local data e.g. that stored in the package
    - local_data_path is the path to the restricted data which must be provided
    to the model

    """
    path_main = ''
    local_data_path = args.data_folder

    # Load data
    base_data = data_loader.load_paths(path_main, local_data_path)
    base_data = data_loader.load_fuels(base_data)
    base_data = data_loader.load_data_tech_profiles(base_data)
    base_data = data_loader.load_data_profiles(base_data)
    base_data['assumptions'] = assumptions.load_assumptions(base_data)
    base_data['weather_stations'], base_data['temperature_data'] = data_loader.load_data_temperatures(
        os.path.join(base_data['paths']['path_scripts_data'], 'weather_data')
        )

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

    parser_run = subparsers.add_parser('run',
                                       help='Run the model')
    parser_run.add_argument('-d', '--data_folder',
                            default='./data',
                            help='Path to the input data folder')
    parser_run.set_defaults(func=run_model)

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