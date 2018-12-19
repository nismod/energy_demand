"""Testing
"""
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import general_assumptions
from energy_demand.read_write import data_loader
'''
def test_load_non_param_assump():
    """
    """
    config_file = "C:/Users/cenv0553/ED/energy_demand/local_run_config_file.ini"
    config = data_loader.read_config_file(config_file)

    # Load data
    data = {}
    paths = config['CONFIG_DATA']
    lu = lookup_tables.basic_lookups()

    data['local_paths'] = config['DATA_PATHS']

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
    config_file = "C:/Users/cenv0553/ED/energy_demand/local_run_config_file.ini"
    config = data_loader.read_config_file(config_file)

    # Load data
    config_data = config['CONFIG_DATA']
    data_loader.load_fuels(config_data)

    sim_param_expected = {}
    sim_param_expected['base_yr'] = 2015

    # Dummy test
    assert sim_param_expected['base_yr'] == 2015
'''