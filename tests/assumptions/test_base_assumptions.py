from energy_demand.assumptions import base_assumptions
from energy_demand.read_write import data_loader
import os

def test_load_assumptions():
    """
    """
    path_main = os.path.abspath("C://Users//cenv0553//nismod//models//energy_demand")
    path_main = os.path.join("//energy_demand", '/..')

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

    sim_param_expected, assumptions_expected = base_assumptions.load_assumptions(data['paths'], data['enduses'], data['lookups'], write_sim_param=True)

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
    return
