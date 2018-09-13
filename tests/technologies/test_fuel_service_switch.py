"""
"""
import numpy as np
from energy_demand.technologies import fuel_service_switch
from energy_demand.read_write import read_data

def test_get_fuel_switches_enduse():

    service_switches = {'regA': [
        read_data.ServiceSwitch(
            enduse='heating',
            sector=None,
            technology_install='techA',
            service_share_ey=0.5,
            switch_yr=2020),
        read_data.ServiceSwitch(
            enduse='other',
            sector=None,
            technology_install='techB',
            service_share_ey=0.5,
            switch_yr=2020)]}

    out = fuel_service_switch.get_switches_of_enduse(
        switches=service_switches,
        enduse='heating')

    for reg, switches in out.items():
        for switch in switches:
            assert switch.enduse == 'heating'

    # --
    service_switches = {'regA': [
        read_data.ServiceSwitch(
            enduse='heating',
            sector=None,
            technology_install='techA',
            service_share_ey=0.5,
            switch_yr=2020),
        read_data.ServiceSwitch(
            enduse='other',
            sector=None,
            technology_install='techB',
            service_share_ey=0.5,
            switch_yr=2020)]}

    out = fuel_service_switch.get_switches_of_enduse(
        switches=service_switches,
        enduse='heating')

    for reg in out:
        for switch in out[reg]:
            assert switch.enduse == 'heating'

def test_switches_to_dict():
    """testing"""
    service_switches = {'regA': [
        read_data.ServiceSwitch(
            enduse='heating',
            sector=None,
            technology_install='techA',
            service_share_ey=0.5,
            switch_yr=2020),
        read_data.ServiceSwitch(
            enduse='heating',
            sector=None,
            technology_install='techB',
            service_share_ey=0.5,
            switch_yr=2020)]}

    out = fuel_service_switch.switches_to_dict(
        service_switches=service_switches)

    assert out['regA'] == {'techA': 0.5, 'techB': 0.5}

def test_get_switch_criteria():
    """testing
    """
    crit_switch_happening = {'heating': ['sectorA']}

    crit = fuel_service_switch.get_switch_criteria(
        enduse='heating',
        sector='sectorA',
        crit_switch_happening=crit_switch_happening,
        base_yr=2015,
        curr_yr=2015)

    assert crit == False

    crit = fuel_service_switch.get_switch_criteria(
        enduse='heating',
        sector='sectorA',
        crit_switch_happening=crit_switch_happening,
        base_yr=2015,
        curr_yr=2025)

    assert crit == True

    crit = fuel_service_switch.get_switch_criteria(
        enduse='heating',
        sector='sectorB',
        crit_switch_happening=crit_switch_happening,
        base_yr=2015,
        curr_yr=2025)

    assert crit == False

def test_sum_fuel_across_sectors():
    """
    """
    fuels = {'sectorA': np.ones(10), 'sectorB': np.ones(10)}
    sum = fuel_service_switch.sum_fuel_across_sectors(fuels)

    assert np.sum(sum) == 20

def test_create_switches_from_s_shares():

    enduse_switches = [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='techA',
        switch_yr=2050,
        service_share_ey=0.6)]

    out = fuel_service_switch.create_switches_from_s_shares(
        enduse='heating',
        s_tech_by_p={None: {'heating': {'techA': 0.2, 'techB': 0.8}}},
        switch_technologies=['techA'],
        specified_tech_enduse_by={'heating': ['techA', 'techB']},
        enduse_switches=enduse_switches,
        s_tot_defined=0.6,
        sector=None,
        switch_yr=2050)

    for switch in out:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 0.6
        if switch.technology_install == 'techB':
            assert switch.service_share_ey == 0.4

def test_autocomplete_switches():
    """testing"""
    service_switches =  [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='techA',
        switch_yr=2050,
        service_share_ey=0.6)]
    defined_temporal_narrative_points = {'heating': [2050]}

    enduses = {'submodelA': ['heating']}
    sectors = {'submodelA': [None]}

    out = fuel_service_switch.autocomplete_switches(
        service_switches=service_switches,
        specified_tech_enduse_by={'heating': ['techA', 'techB', 'techC']},
        s_tech_by_p={None: {'heating': {'techA': 0.2, 'techB': 0.4, 'techC': 0.4}}},
        crit_all_the_same=True,
        enduses=enduses,
        sectors=sectors,
        regions=['regA'],
        f_diffusion=False,
        techs_affected_spatial_f=False,
        service_switches_from_capacity={'regA':[]})

    assert out[None]['heating']['regA'][2050]['techA'] == 0.6
    assert out[None]['heating']['regA'][2050]['techB'] == 0.2
    assert out[None]['heating']['regA'][2050]['techC'] == 0.2

    # ---
    service_switches = [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='techA',
        switch_yr=2050,
        service_share_ey=0.6)]

    out = fuel_service_switch.autocomplete_switches(
        service_switches=service_switches,
        specified_tech_enduse_by={'heating': ['techA', 'techB', 'techC']},
        s_tech_by_p={None: {'heating': {'techA': 0.2, 'techB': 0.4, 'techC': 0.4}}},
        crit_all_the_same=True,
        enduses=enduses,
        sectors=sectors,
        regions=['regA'],
        f_diffusion={'heating':{'regA':1.0, 'regB': 1.0}},
        techs_affected_spatial_f=['techA'],
        service_switches_from_capacity={'regA': [], 'regB': []})

    assert out[None]['heating']['regA'][2050]['techA'] == 0.6
    assert out[None]['heating']['regA'][2050]['techB'] == 0.2
    assert out[None]['heating']['regA'][2050]['techC'] == 0.2

def test_create_service_switch():
    """testing
    """
    installed_capacity = 100

    enduse = 'heating'

    capacity_switches = [read_data.CapacitySwitch(
        enduse='heating',
        technology_install='boiler_gas',
        switch_yr=2020,
        installed_capacity=installed_capacity)]

    capacity_switch = read_data.CapacitySwitch(
        enduse='heating',
        technology_install='boiler_gas',
        switch_yr=2020,
        installed_capacity=installed_capacity)

    assumptions = {
        'technologies':
            {'boiler_oil': read_data.TechnologyData(
                fueltype='oil',
                eff_by=1.0,
                eff_ey=1.0,
                year_eff_ey=2020,
                eff_achieved=1.0,
                diff_method='linear',
                market_entry=2010,
                tech_type='tech_heating',
                tech_max_share=1.0),
            'boiler_gas': read_data.TechnologyData(
                fueltype='gas',
                eff_by=1.0,
                eff_ey=1.0,
                year_eff_ey=2020,
                eff_achieved=1.0,
                diff_method='linear',
                market_entry=2010,
                tech_type='tech_heating',
                tech_max_share=1.0)
            },
        'rs_fuel_tech_p_by': {0: {'boiler_gas': 0.0}, 1: {'boiler_oil': 1.0}}
    }

    base_yr = 2015

    fuels = {0: 0, 1: 10} #array originally
    sector = None
    narrative_timesteps = [2020]

    results = fuel_service_switch.create_service_switch(
        narrative_timesteps,
        enduse,
        sector,
        capacity_switch,
        capacity_switches,
        assumptions['technologies'],
        assumptions['rs_fuel_tech_p_by'],
        base_yr,
        fuels)

    # Fuel share boiler_gas
    expected = 1 / (10 + installed_capacity) * installed_capacity

    for entry in results:
        if entry.technology_install == 'boiler_gas':
            assert expected == entry.service_share_ey

def test_capacity_switch():
    """Testing
    """
    technologies = {'techA': read_data.TechnologyData(
        fueltype='oil',
        eff_by=1.0,
        eff_ey=1.0,
        year_eff_ey=2020,
        eff_achieved=1.0,
        diff_method='linear',
        market_entry=2010,
        tech_type='tech_heating',
        tech_max_share=1.0)}

    capacity_switches ={"regA": [
        read_data.CapacitySwitch(
            enduse='heating',
            technology_install='techA',
            switch_yr=2050,
            installed_capacity=200)]}

    narrative_timesteps = {'heating': [2050]}
    regions = ["regA"]
    result_service_switches = fuel_service_switch.capacity_switch(
        narrative_timesteps=narrative_timesteps,
        regions=regions,
        capacity_switches=capacity_switches,
        technologies=technologies,
        fuels={'heating': {0: 100}},
        fuel_shares_enduse_by={'heating': {0: {'techA': 1.0}}},
        base_yr=2015)

    for region in regions:
        for switch in result_service_switches[region]:
            if switch.technology_install == 'techA':
                assert switch.service_share_ey == 1.0

    #---------------

    technologies = {
        'techA': read_data.TechnologyData(
            fueltype='oil',
            eff_by=1.0,
            eff_ey=1.0,
            year_eff_ey=2020,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=2010,
            tech_type='tech_heating',
            tech_max_share=1.0),
        'techB': read_data.TechnologyData(
            fueltype='oil',
            eff_by=1.0,
            eff_ey=1.0,
            year_eff_ey=2020,
            eff_achieved=1.0,
            diff_method='linear',
            market_entry=2010,
            tech_type='tech_heating',
            tech_max_share=1.0)}

    capacity_switches = {"regA":[
        read_data.CapacitySwitch(
            enduse='heating',
            technology_install='techA',
            switch_yr=2050,
            installed_capacity=200)
    ]}

    result_service_switches = fuel_service_switch.capacity_switch(
        narrative_timesteps=narrative_timesteps,
        regions=regions,
        capacity_switches=capacity_switches,
        technologies=technologies,
        fuels={'heating': {0: 100}},
        fuel_shares_enduse_by={'heating': {0: {'techA': 0.5, 'techB': 0.5}}},
        base_yr=2015)

    for region in regions:
        for switch in result_service_switches[region]:
            if switch.technology_install == 'techA':
                assert round(switch.service_share_ey, 3) == round((1 / (300)) * 250, 3)
            if switch.technology_install == 'techB':
                assert round(switch.service_share_ey, 3) == round((1 / (300)) * 50, 3)
test_capacity_switch()
def autocomplete_switches():
    """Testing
    """
    service_switches = [read_data.ServiceSwitch(
        'heating',
        'techA',
        0.5,
        2020)]

    specified_tech_enduse_by = {'heating': ['techA', 'techB']}
    s_tech_by_p = {'heating': {'techA': 0.8, 'techB': 0.2}}

    service_switches = fuel_service_switch.autocomplete_switches(
        service_switches=service_switches,
        specified_tech_enduse_by=specified_tech_enduse_by,
        s_tech_by_p=s_tech_by_p)
    
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
    s_tech_by_p = {'heating': {'techA': 0.6, 'techB': 0.2,'techC': 0.1}}

    service_switches = fuel_service_switch.autocomplete_switches(
        service_switches=service_switches,
        specified_tech_enduse_by=specified_tech_enduse_by,
        s_tech_by_p=s_tech_by_p)

    for switch in service_switches:
        if switch.technology_install == 'techA':
            assert switch.service_share_ey == 0.3
        if switch.technology_install == 'techB':
            assert switch.service_share_ey == 0.7 * (2.0 / 3.0)
        if switch.technology_install == 'techC':
            assert switch.service_share_ey == 0.7 * (1.0 / 3.0)

def test_get_share_s_tech_ey():
    """testing"""

    service_switches = [read_data.ServiceSwitch(
        enduse='heating',
        sector=None,
        technology_install='techA',
        service_share_ey=0.3,
        switch_yr=2020)]

    # --
    service_switches = {'regA': [read_data.ServiceSwitch(
        enduse='heating',
        sector=None,
        technology_install='techA',
        service_share_ey=0.3,
        switch_yr=2020)]}

    specified_tech_enduse_by = {'regA': {'heating': ['techA', 'techB', 'techC']}}

    defined_temporal_narrative_points = [2020] 
    result = fuel_service_switch.get_share_s_tech_ey(
        service_switches=service_switches,
        specified_tech_enduse_by=specified_tech_enduse_by)

    assert result['heating']['regA'][2020]['techA'] == 0.3
