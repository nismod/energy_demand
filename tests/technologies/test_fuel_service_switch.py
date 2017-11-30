"""
"""
from energy_demand.technologies import fuel_service_switch
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.read_write import read_data

def test_create_service_switch():
    """testing
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
        if entry.technology_install == 'boiler_gas':
            assert expected == entry.service_share_ey

def test_capacity_installations():
    """
    """
    other_enduse_mode_info = {
        'diff_method': 'linear',
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1}}

    technologies = {'techA': read_data.TechnologyData(
        fuel_type='oil',
        eff_by= 1.0,
        eff_ey= 1.0,
        year_eff_ey=2020,
        eff_achieved=1.0,
        diff_method='linear',
        market_entry=2010,
        tech_list='tech_heating',
        tech_max_share=1.0)}

    capacity_switches = [
        read_data.CapacitySwitch(
            enduse='heating',
            technology_install='techA',
            switch_yr=2050,
            installed_capacity=200
        )
    ]

    result_service_switches, crit_switch = fuel_service_switch.capacity_installations(
        service_switches=[],
        capacity_switches=capacity_switches,
        technologies=technologies,
        other_enduse_mode_info=other_enduse_mode_info,
        fuels={'heating': {0: 100}},
        fuel_shares_enduse_by={'heating': {0: {'techA': 1.0}}},
        base_yr=2015)

    for switch in result_service_switches:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 1.0
    assert crit_switch == True

    #---------------
    
    technologies = {
        'techA': read_data.TechnologyData(
            fuel_type='oil',
            eff_by= 1.0,
            eff_ey= 1.0,
            year_eff_ey=2020,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=2010,
            tech_list='tech_heating',
            tech_max_share=1.0),
        'techB': read_data.TechnologyData(
            fuel_type='oil',
            eff_by= 1.0,
            eff_ey= 1.0,
            year_eff_ey=2020,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=2010,
            tech_list='tech_heating',
            tech_max_share=1.0),
        }

    capacity_switches = [
            read_data.CapacitySwitch(
                enduse='heating',
                technology_install='techA',
                switch_yr=2050,
                installed_capacity=200
            )
        ]

    result_service_switches, crit_switch = fuel_service_switch.capacity_installations(
        service_switches=result_service_switches,
        capacity_switches=capacity_switches,
        technologies=technologies,
        other_enduse_mode_info=other_enduse_mode_info,
        fuels={'heating': {0: 100}},
        fuel_shares_enduse_by={'heating': {0: {'techA': 0.5, 'techB': 0.5}}},
        base_yr=2015)

    for switch in result_service_switches:
        if switch.technology_install == 'techA':
            assert round(switch.service_share_ey, 3) == round((1 / (300)) * 250, 3)
        if switch.technology_install == 'techB':
            assert round(switch.service_share_ey, 3) == round((1 / (300)) * 50, 3)
    assert crit_switch == True

def helper_reduce_service_switches():
    """
    """
    service_switches = [read_data.ServiceSwitch(
        'heating',
        'techA',
        0.5,
        2020)]

    specified_tech_enduse_by = {'heating': ['techA', 'techB']}
    service_tech_by_p = {'heating': {'techA': 0.8, 'techB': 0.2}}

    service_switches = fuel_service_switch.helper_reduce_service_switches(
        service_switches=service_switches,
        specified_tech_enduse_by=specified_tech_enduse_by,
        service_tech_by_p=service_tech_by_p)
    
    for switch in service_switches:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 0.5
        
        if switch.technology_install == 'techB':
            assert switch.service_share_ey == 0.5
    #---

    service_switches = [read_data.ServiceSwitch(
        'heating',
        'techA',
        0.3,
        2020)]

    specified_tech_enduse_by = {'heating': ['techA', 'techB', 'techC']}
    service_tech_by_p = {'heating': {'techA': 0.6, 'techB': 0.2,'techC': 0.1}}

    service_switches = fuel_service_switch.helper_reduce_service_switches(
        service_switches=service_switches,
        specified_tech_enduse_by=specified_tech_enduse_by,
        service_tech_by_p=service_tech_by_p)
    
    for switch in service_switches:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 0.3
        
        if switch.technology_install == 'techB':
            assert switch.service_share_ey == 0.7 * (2.0 / 3.0)
        if switch.technology_install == 'techC':
            assert switch.service_share_ey == 0.7 * (1.0 / 3.0)
