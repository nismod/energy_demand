from energy_demand.assumptions import base_assumptions
from energy_demand.read_write import data_loader
import os

def test_load_assumptions():
    """
    """
    path_main = os.path.abspath("C://Users//cenv0553//nismod//models//energy_demand")
    path_main = os.path.join("")

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    
    sim_param_expected = {}
    sim_param_expected['base_yr'] = 2015
    sim_param_expected['simulated_yrs'] = [2015, 2020, 2025]
    sim_param_expected['curr_yr'] = 2015
    
    #assumptions_expected = base_assumptions.load_assumptions( TODO
    #   data['paths'], data['enduses'], data['lookups'], data['fuels'], sim_param_expected)

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
    return
