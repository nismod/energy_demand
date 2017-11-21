"""
"""
from energy_demand.technologies import fuel_service_switch
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.read_write import read_data

def test_create_service_switch():
    """
    """
    installed_capacity = 100

    enduses = ['heating']

    capacity_switches = [read_data.CapacitySwitch(
        enduse='heating',
        technology_install='boiler_gas',
        switch_yr=2020,
        installed_capacity=installed_capacity
        )]

    assumptions = {
        'technologies':
                {'boiler_oil': read_data.TechnologyData(
                        fuel_type='oil',
                        eff_by= 1.0,
                        eff_ey= 1.0,
                        year_eff_ey=2020,
                        eff_achieved=1.0,
                        diff_method='linear',
                        market_entry=2010,
                        tech_list='tech_heating',
                        tech_max_share=1.0),
                'boiler_gas': read_data.TechnologyData(
                    fuel_type='gas',
                    eff_by=1.0,
                    eff_ey= 1.0,
                    year_eff_ey=2020,
                    eff_achieved=1.0,
                    diff_method='linear',
                    market_entry=2010,
                    tech_list='tech_heating',
                    tech_max_share=1.0)
                },
        'other_enduse_mode_info': {'diff_method': 'linear', 'sigmoid': {'sig_midpoint': 0,'sig_steeppness': 1}},
        'rs_fuel_tech_p_by': {'heating': {0: {'boiler_gas': 0.0}, 1 :{'boiler_oil': 1.0}}}
    }

    base_yr = 2015

    fuel_by = {0: 0, 1: 10}
    fuels = {'heating': fuel_by}

    results = fuel_service_switch.create_service_switch(
        enduses,
        capacity_switches,
        assumptions['technologies'],
        assumptions['other_enduse_mode_info'],
        assumptions['rs_fuel_tech_p_by'],
        base_yr,
        fuels)

    # Fuel share boiler_gas
    expected = 1 / (sum(fuels['heating'].values()) + installed_capacity) * installed_capacity

    for entry in results:
        if entry['technology_install'] == 'boiler_gas':
            assert expected == entry['service_share_ey']
