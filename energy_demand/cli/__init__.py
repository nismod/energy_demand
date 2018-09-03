"""Provides an entry point from the command line to the energy demand model
"""
import os
import sys
from argparse import ArgumentParser
from pkg_resources import Requirement
from pkg_resources import resource_filename
import energy_demand
from energy_demand.read_write import data_loader
from energy_demand.assumptions import general_assumptions
from energy_demand.scripts.s_post_installation import post_install_setup
from energy_demand.scripts.s_write_dummy_data import post_install_setup_minimum
from energy_demand.scripts.init_scripts import switch_calculations
from energy_demand.read_write import read_data
from energy_demand.dwelling_stock import dw_stock
from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions
from energy_demand.basic import date_prop

def parse_arguments():
    """Parse command line arguments

    Returns
    =======
    :class:`argparse.ArgumentParser`

    """
    parser = ArgumentParser(description='Command line tools for energy_demand')
    parser.add_argument('-V', '--version',
                        action='version',
                        version="energy_demand" + energy_demand.__version__,
                        help='show the current version of energy_demand')

    subparsers = parser.add_subparsers()

    # Initialisation of energy demand model (processing raw files)
    parser_init = subparsers.add_parser(
        'setup',
        help='Executes the raw reading functions')

    parser_init.add_argument(
        '-d',
        '--local_data',
        default='./data',
        help='Path to the local data folder')

    parser_init.set_defaults(func=post_install_setup)

    # Initialisation of energy demand model (processing raw files)
    parser_init2 = subparsers.add_parser(
        'minimal_setup',
        help='Executes the minimum dummy raw reading functions')

    parser_init2.add_argument(
        '-d',
        '--local_data',
        default='./data',
        help='Path to the local data folder')

    parser_init2.set_defaults(func=post_install_setup_minimum)

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
