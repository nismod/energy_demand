"""
"""
import os
from energy_demand.basic import lookup_tables
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.assumptions import non_param_assumptions
from energy_demand.assumptions import param_assumptions
from energy_demand.read_write import data_loader, read_data
from pkg_resources import resource_filename
from pkg_resources import Requirement

def test_assign_by_fuel_tech_p():
    """
    """
    path_main = resource_filename(
        Requirement.parse("energy_demand"), os.path.join("energy_demand", "config_data"))

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    data['local_paths'] = data_loader.load_local_paths(path_main)

    #Load assumptions
    base_yr = 2015

    data['assumptions'] = non_param_assumptions.Assumptions(
        base_yr=base_yr,
        curr_yr=None,
        simulated_yrs=None,
        paths=data['paths'],
        enduses=data['enduses'],
        sectors=data['sectors'],
        fueltypes=data['lookups']['fueltypes'],
        fueltypes_nr=data['lookups']['fueltypes_nr'])

    param_assumptions.load_param_assump(data['paths'], data['local_paths'], data['assumptions'])

    rs_fuel_tech_p_by, ss_fuel_tech_p_by, is_fuel_tech_p_by  = assumptions_fuel_shares.assign_by_fuel_tech_p( 
        data['enduses'],
        data['sectors'],
        data['lookups']['fueltypes'],
        data['lookups']['fueltypes_nr'])
