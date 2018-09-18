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

    enduses, sectors, _ = data_loader.load_fuels(
        lu['submodels_names'], paths, lu['fueltypes_nr'])

    general_assumptions.Assumptions(
        base_yr=2015,
        curr_yr=None,
        simulated_yrs=None,
        paths=paths,
        enduses=enduses,
        sectors=sectors,
        fueltypes=lu['fueltypes'],
        fueltypes_nr=lu['fueltypes_nr'])

def test_load_param_assump():
    """
    """
    path_main = resource_filename(
        Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
        data['lookups']['submodels_names'], data['paths'], data['lookups']['fueltypes_nr'])

    sim_param_expected = {}
    sim_param_expected['base_yr'] = 2015

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
    return
