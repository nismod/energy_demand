"""
"""
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.assumptions import base_assumptions
from energy_demand.read_write import data_loader
import os

def test_assign_by_fuel_tech_p():
    """DUMMY OS FAR
    """
    path_main = os.path.abspath("C://Users//cenv0553//nismod//models//energy_demand")
    path_main = os.path.join("")

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = data_loader.load_basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])

    #Load assumptions
    data['sim_param'] = {}
    data['sim_param']['base_yr'] = 2015

    data['sim_param']['simulated_yrs'] = [2015, 2020, 2025]
    data['sim_param']['curr_yr'] = 2015
    
    data['assumptions'] = base_assumptions.load_assumptions(
        data['paths'], data['enduses'], data['lookups'], data['fuels'], data['sim_param'])

    result = assumptions_fuel_shares.assign_by_fuel_tech_p(
        data['assumptions'], data['enduses'], data['lookups'])

    # Dummy test
    assert result['test'] == 'test'
