"""Testing
"""
import os
from pkg_resources import resource_filename
from pkg_resources import Requirement
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import general_assumptions
from energy_demand.read_write import data_loader
from pkg_resources import resource_filename
from pkg_resources import Requirement

def test_load_non_param_assump():
    """
    """
    path_main = resource_filename(
        Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    paths = data_loader.load_paths(path_main)
    lu = lookup_tables.basic_lookups()

    data['local_paths'] = data_loader.get_local_paths(path_main)


    enduses, sectors, _, lookup_enduses, lookup_sector_enduses = data_loader.load_fuels(paths)

    general_assumptions.Assumptions(
        lookup_enduses=lookup_enduses,
        lookup_sector_enduses=lookup_sector_enduses,
        base_yr=2015,
        curr_yr=None,
        paths=paths,
        enduses=enduses,
        sectors=sectors)

def test_load_param_assump():
    """
    """
    path_main = resource_filename(
        Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], _, _ = data_loader.load_fuels(data['paths'])

    sim_param_expected = {}
    sim_param_expected['base_yr'] = 2015

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
    return
