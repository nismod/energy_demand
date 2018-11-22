"""
"""
import os
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import fuel_shares
from energy_demand.assumptions import general_assumptions
from energy_demand.assumptions import strategy_vars_def
from energy_demand.read_write import data_loader
from pkg_resources import resource_filename
from pkg_resources import Requirement

'''def test_assign_by_fuel_tech_p():
    """
    """
    path_main = resource_filename(
        Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'], _, _ = data_loader.load_fuels(
        data['lookups']['submodels_names'], data['paths'], data['lookups']['fueltypes_nr'])

    data['local_paths'] = data_loader.get_local_paths(path_main)

    #Load assumptions
    base_yr = 2015

    data['assumptions'] = general_assumptions.Assumptions(
        submodels_names=['a'],
        base_yr=base_yr,
        curr_yr=None,
        sim_yrs=None,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        fueltypes=data['lookups']['fueltypes'],
        fueltypes_nr=data['lookups']['fueltypes_nr'])

    strategy_vars_def.load_param_assump(data['paths'], data['local_paths'], data['assumptions'])

    fuel_tech_p_by = fuel_shares.assign_by_fuel_tech_p( 
        data['enduses'],
        data['sectors'],
        data['lookups']['fueltypes'],
        data['lookups']['fueltypes_nr'])
'''