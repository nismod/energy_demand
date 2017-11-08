"""
"""
from energy_demand.technologies import fuel_service_switch
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid

def test_create_service_switch():
    """
    """
    fuel_capacity_installed = 100

    enduses = ['heating']
    capacity_switches = [{
        'enduse': 'heating',
        'technology_install': 'boiler_gas',
        'market_entry': 2015,
        'year_fuel_consumption_switched': 2020,
        'fuel_capacity_installed': fuel_capacity_installed,
        'enduse_by_dict': 'rs_fuel_tech_p_by',
        'fuels': 'rs_fuel_raw_data_enduses'
    }]
    assumptions = {
        'technologies': {
                'boiler_oil': {
                    'fueltype': 'oil',
                    'eff_by':  1.0,
                    'eff_ey':  1.0,
                    'year_eff_ey': 2020,
                    'eff_achieved':	1.0,
                    'diff_method':	'linear',
                    'market_entry':	2010,
                    'tech_list': 'tech_heating',
                    'tech_assum_max_share': 1.0},

                'boiler_gas': {
                    'fueltype': 'gas',
                    'eff_by': 1.0,
                    'eff_ey':  1.0,
                    'year_eff_ey': 2020,
                    'eff_achieved':	1.0,
                    'diff_method':	'linear',
                    'market_entry':	2010,
                    'tech_list': 'tech_heating',
                    'tech_assum_max_share': 1.0},
                },
        'other_enduse_mode_info': {'diff_method': 'linear', 'sigmoid': {'sig_midpoint': 0,'sig_steeppness': 1}},
        'rs_fuel_tech_p_by': {'heating': {0: {'boiler_gas': 0.0}, 1 :{'boiler_oil': 1.0}}}
    }

    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    fuel_by = {0: 0, 1: 10}
    fuels = {'heating': fuel_by}

    results = fuel_service_switch.create_service_switch(
        enduses,
        capacity_switches,
        assumptions['technologies'],
        assumptions['other_enduse_mode_info'],
        assumptions['rs_fuel_tech_p_by'],
        sim_param,
        fuels)

    # Fuel share boiler_gas
    expected = 1 / (sum(fuels['heating'].values()) + fuel_capacity_installed) * fuel_capacity_installed

    for entry in results:
        if entry['tech'] == 'boiler_gas':
            assert expected == entry['service_share_ey']
