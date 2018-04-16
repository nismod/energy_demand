"""Testing
"""
import os
from pkg_resources import resource_filename
from pkg_resources import Requirement
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import non_param_assumptions
from energy_demand.read_write import data_loader
from pkg_resources import resource_filename
from pkg_resources import Requirement

def test_load_non_param_assump():
    """
    """
    path_main = resource_filename(Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    paths = data_loader.load_paths(path_main)
    lu = lookup_tables.basic_lookups()
    enduses, sectors, _ = data_loader.load_fuels(paths, lu)

    non_param_assumptions.Assumptions(
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
    path_main = resource_filename(Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

    sim_param_expected = {}
    sim_param_expected['base_yr'] = 2015

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
    return
