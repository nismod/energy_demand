"""Tests for enduse functions
"""
import numpy as np
from energy_demand import enduse_func

from energy_demand.read_write import read_data
from energy_demand.technologies import technological_stock
from energy_demand.profiles import load_profile

def test_enduse():
    """testing"""
    out = enduse_func.Enduse(
        submodel_name ='test_name',
        region='test',
        scenario_data='test',
        assumptions='test',
        load_profiles='test',
        base_yr='test',
        curr_yr='test',
        enduse='test',
        sector='test',
        fuel=np.zeros((7, 0)),
        tech_stock='test',
        heating_factor_y='test',
        cooling_factor_y='test',
        fuel_tech_p_by='test',
        criterias='test',
        strategy_vars='test',
        fueltypes_nr='test',
        fueltypes='test')

    assert out.flat_profile_crit == True

def test_assign_lp_no_techs():
    """Testing
    """
    lp_stock_obj = load_profile.LoadProfileStock("test_stock")

    # Shape
    _a = np.zeros((365, 24))
    _b = np.array(range(365))
    shape_yh = _a + _b[:, np.newaxis]
    shape_yh = shape_yh / float(np.sum(range(365)) * 24)

    lp_stock_obj.add_lp(
        unique_identifier="A123",
        technologies=['placeholder_tech'],
        enduses=['test_enduse'],
        shape_yd=np.full((365, 24), 1 / 365),
        shape_yh=shape_yh,
        sectors=['test_sector'],
        model_yeardays=list(range(365)),
        shape_y_dh=False)

    fuel_y = np.zeros((3))
    fuel_y[2] = 100
    fuel_yh = enduse_func.assign_lp_no_techs(
        enduse="test_enduse",
        sector="test_sector",
        load_profiles=lp_stock_obj,
        fuel_y=fuel_y,
        make_all_flat=False)

    assert np.sum(fuel_yh) == 100

'''def test_get_crit_switch():
    """
    """
    mode_constrained = True

    fuelswitches = [read_data.FuelSwitch(
        enduse='heating')]

    result = enduse_func.get_crit_switch(
        'heating',
        None,
        fuelswitches,
        2015,
        2020,
        mode_constrained)

    assert result == True

    # -----
    mode_constrained = False

    result2 = enduse_func.get_crit_switch(
        'heating',
        None,
        fuelswitches,
        2015,
        2020,
        mode_constrained)

    assert result2 == False'''

def test_get_peak_day():
    """testing
    """

    fuel_yh = np.zeros((8, 365, 24))
    fuel_yh[2][33] = 3

    result = enduse_func.get_peak_day_all_fueltypes(fuel_yh)

    expected = 33

    assert result == expected

def test_apply_service_switch():
    """Test
    """
    share_boilerA_cy = 0.2
    share_boilerB_cy = 0.8

    base_yr = 2020
    curr_yr = 2050
    end_yr = 2050

    tot_s_yh_cy = {
        'boilerA': 365*24,
        'boilerB': 365*24, }#constant share of 1 in every hour

    all_technologies = ['boilerA', 'boilerB']

    annual_tech_diff_params = {
        'test_enduse': {
            'test_sector': {
                'boilerA': {2050: share_boilerA_cy},
                'boilerB': {2050: share_boilerB_cy}
            }
        }}

    crit_switch_happening = {'test_enduse': ['test_sector']}

    result = enduse_func.apply_service_switch(
        enduse='test_enduse',
        s_tech_y_cy=tot_s_yh_cy,
        all_technologies=all_technologies,
        curr_yr=curr_yr,
        base_yr=base_yr,
        sector='test_sector',
        annual_tech_diff_params=annual_tech_diff_params,
        crit_switch_happening=crit_switch_happening)

    expected_tech_service_cy_p = {
        "boilerA": 365*24*2 * share_boilerA_cy,
        "boilerB": 365*24*2 * share_boilerB_cy}

    assert round(expected_tech_service_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_tech_service_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    # --------------------------------------------

    share_boilerA_cy = 0.99
    share_boilerB_cy = 0.01

    annual_tech_diff_params = {
        'test_enduse': {
            'test_sector': {
                'boilerA': {2050: share_boilerA_cy},
                'boilerB': {2050: share_boilerB_cy}
            }
        }}

    result = enduse_func.apply_service_switch(
        enduse='test_enduse',
        s_tech_y_cy=tot_s_yh_cy,
        all_technologies=all_technologies,
        curr_yr=curr_yr,
        annual_tech_diff_params=annual_tech_diff_params,
        base_yr=base_yr,
        sector='test_sector',
        crit_switch_happening=crit_switch_happening)

    half_time_factor = 1
    expected_tech_service_cy_p = {
        "boilerA": (365*24*2) * share_boilerA_cy,
        "boilerB": (365*24*2) * share_boilerB_cy}

    assert round(expected_tech_service_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_tech_service_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

def test_convert_service_to_p():
    """Testing
    """
    tot_s_y = 8760
    s_fueltype_tech = {
        0: {
            'techA': 8760 * 0.5,
            'techB': 8760 * 0.5}
        }

    expected = enduse_func.convert_service_to_p(tot_s_y, s_fueltype_tech)

    assert expected['techA'] == 0.5
    assert expected['techB'] == 0.5

def test_calc_lf_improvement():
    """
    """
    param_lf_improved_cy = 0.25

    #all factors must be smaller than one
    loadfactor_yd_cy = np.zeros((2, 2)) #to fueltypes, two days
    loadfactor_yd_cy[0][0] = 0.2
    loadfactor_yd_cy[0][1] = 0.4
    loadfactor_yd_cy[1][0] = 0.1
    loadfactor_yd_cy[1][1] = 0.3

    result = enduse_func.calc_lf_improvement(
        param_lf_improved_cy=param_lf_improved_cy,
        loadfactor_yd_cy=loadfactor_yd_cy)

    expected = loadfactor_yd_cy + 0.25

    assert result[0][0] == expected[0][0]
    assert result[0][1] == expected[0][1]
    assert result[1][0] == expected[1][0]
    assert result[1][1] == expected[1][1]

def test_get_enduse_tech():
    """Testing
    """
    fuel_tech_p_by = {
        0: {'techA': 0.4, 'techB': 0.6},
        1: {'techC': 0.4, 'techD': 0.6}}
    result = enduse_func.get_enduse_techs(
        fuel_tech_p_by,
        )

    expected = ['techA', 'techB', 'techC', 'techD']
    assert expected[0] in result
    assert expected[1] in result
    assert expected[2] in result
    assert expected[3] in result

    fuel_tech_p_by = {
        0: {'techA': 0.4, 'techB': 0.6},
        1: {'placeholder_tech': 0.4, 'techD': 0.6}}
    result = enduse_func.get_enduse_techs(fuel_tech_p_by)
    expected = []
    assert expected == result

def test_apply_smart_metering():
    """Testing"""

    sm_assump = {
        'savings_smart_meter': {
            'heating': 0.5}, #50 is saved by smart meter
        'smart_meter_p_by': 0}

    strategy_vars = {}
    strategy_vars['smart_meter_improvement_p'] = {2015: 0, 2020: 0.5}

    result = enduse_func.apply_smart_metering(
        enduse='heating',
        fuel_y=100,
        sm_assump=sm_assump,
        strategy_vars=strategy_vars,
        curr_yr=2020)

    assert result == 75

def test_fuel_to_service():
    """
    """
    enduse = 'heating'
    fuel_y = {0: 2000}
    enduse_techs = ['techA']
    fuel_tech_p_by = {0 : {'techA': 1.0}}

    technologies = {'techA': read_data.TechnologyData()}
    technologies['techA'].fueltype_str = 'gas'
    technologies['techA'].eff_achieved = 1.0
    technologies['techA'].diff_method = 'linear'
    technologies['techA'].eff_by = 0.5
    technologies['techA'].eff_ey = 0.5
    technologies['techA'].year_eff_ey = 2020
    
    fueltypes = {'electricity': 0, 'gas': 1} #, 'heat': 1}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})

    tot_s_y, service_tech = enduse_func.fuel_to_service(
        enduse=enduse,
        fuel_y=fuel_y,
        fuel_tech_p_by=fuel_tech_p_by,
        tech_stock=tech_stock,
        fueltypes=fueltypes,
        mode_constrained=True)

    assert service_tech['techA'] == 1000

    # ---
    fuel_tech_p_by = {0: {}, 1 : {'techA': 1.0}} #'placeholder_tech': 1.0}}
    fuel_y = {0: 0, 1: 2000}
    fuel_tech_p_by = {0 : {}, 1: {'techA': 1.0}}
    fueltypes = {'gas': 0, 'heat': 1}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})

    tot_s_y, service_tech = enduse_func.fuel_to_service(
        enduse=enduse,
        fuel_y=fuel_y,
        fuel_tech_p_by=fuel_tech_p_by,
        tech_stock=tech_stock,
        fueltypes=fueltypes,
        mode_constrained=False) #Difference

    assert service_tech['techA'] == 2000

def test_service_to_fuel():
    """Testing"""
    technologies = {'techA': read_data.TechnologyData()}
    technologies['techA'].fueltype_str = 'gas'
    technologies['techA'].eff_achieved = 1.0
    technologies['techA'].diff_method = 'linear'
    technologies['techA'].eff_by = 0.5
    technologies['techA'].eff_ey = 0.5
    technologies['techA'].year_eff_ey = 2020

    fueltypes = {'electricity': 0, 'gas': 1}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})

    fuel_y, fuel_per_tech = enduse_func.service_to_fuel(
        "heating",
        {'techA': 100},
        tech_stock,
        len(fueltypes),
        fueltypes,
        True)

    assert fuel_per_tech['techA'] == 200
    assert fuel_y[0] == 0
    assert fuel_y[1] == 200
    # ----

    fueltypes = {'gas': 0, 'heat': 1}

    fuel_y, fuel_per_tech = enduse_func.service_to_fuel(
        "heating",
        {'techA': 100},
        tech_stock,
        len(fueltypes),
        fueltypes,
        False)

    assert fuel_per_tech['techA'] == 100
    assert fuel_y[1] == 100

def test_apply_heat_recovery():
    """Testing"""

    result, result_tech = enduse_func.apply_heat_recovery(
        enduse='heating',
        strategy_vars={'heat_recovered': {'heating': {2015: 0, 2020: 0.5}}},
        service=100,
        service_techs={'techA': 100},
        curr_yr=2020)

    assert result == 50
    assert result_tech == {'techA': 50}

def test_apply_climate_chante():
    """Testing"""

    result = enduse_func.apply_climate_change(
        enduse='heating',
        fuel_y=200,
        cooling_factor_y=1.5,
        heating_factor_y=1.5,
        enduse_space_heating=['heating'],
        enduse_space_cooling=['cooling'])

    assert result == 300
    result = enduse_func.apply_climate_change(
        enduse='cooling',
        fuel_y=200,
        cooling_factor_y=1.5,
        heating_factor_y=1.5,
        enduse_space_heating=['heating'],
        enduse_space_cooling=['cooling'])

    assert result == 300

def test_calc_fuel_tech_yh():
    """Testing
    """
    fueltypes = {'gas': 0, 'heat': 1}

    technologies = {'techA': read_data.TechnologyData()}
    technologies['techA'].fueltype_str = 'gas'
    technologies['techA'].eff_achieved = 1.0
    technologies['techA'].diff_method = 'linear'
    technologies['techA'].eff_by = 0.5
    technologies['techA'].eff_ey = 0.5
    technologies['techA'].year_eff_ey = 2020

    '''tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})'''

    lp_stock_obj = load_profile.LoadProfileStock("test_stock")

    _a = np.zeros((365, 24))
    _b = np.array(range(365))
    shape_yh = _a + _b[:, np.newaxis]
    shape_yh = shape_yh / float(np.sum(range(365)) * 24)
    model_yeardays = list(range(365))

    lp_stock_obj.add_lp(
        unique_identifier="A123",
        technologies=['techA'],
        enduses=['heating'],
        shape_yd=np.full((365,24), 1 / 365),
        shape_yh=shape_yh,
        sectors=['sectorA'],
        shape_y_dh=np.full((365), 1/365),
        model_yeardays=model_yeardays)

    fuel = 200
    results = enduse_func.calc_fuel_tech_yh(
        enduse='heating',
        sector='sectorA',
        enduse_techs=['techA'],
        fuel_tech_y={'techA': fuel},
        load_profiles=lp_stock_obj,
        fueltypes_nr=2,
        fueltypes=fueltypes,
        mode_constrained=False)

    assert results[1][3][0] == 3.0 / float(np.sum(range(365)) * 24) * 200

    # ---
    results = enduse_func.calc_fuel_tech_yh(
        enduse='heating',
        sector='sectorA',
        enduse_techs=['techA'],
        fuel_tech_y={'techA': fuel},
        load_profiles=lp_stock_obj,
        fueltypes_nr=2,
        fueltypes=fueltypes,
        mode_constrained=True)

    assert results['techA'][3][0] == 3.0 / float(np.sum(range(365)) * 24) * 200

def test_apply_enduse_sector_specific_change():
    """testing
    """
    strategy_vars = {'generic_enduse_change': {'heating': {2015: 0, 2020: 2.0}}}
    strategy_vars['generic_enduse_change']['heating']['param_info'] = {}
    strategy_vars['generic_enduse_change']['heating']['param_info']['sector'] = 'heating'

    fuel_y = np.array([100])
    result = enduse_func.apply_enduse_sector_specific_change(
        sector=True,
        enduse='heating',
        fuel_y=fuel_y,
        strategy_vars=strategy_vars,
        curr_yr=2020)

    assert result == fuel_y * (1 + strategy_vars['generic_enduse_change']['heating'][2020])

def test_get_enduse_configuration():
    """Testing
    """
    fuel_switches = [read_data.FuelSwitch(
        enduse='heating',
        fueltype_replace="",
        technology_install='boilerB',
        switch_yr=2020,
        fuel_share_switched_ey="")]

    service_switches = [read_data.ServiceSwitch(
        technology_install='boilerA',
        switch_yr=2050)]

    mode_constrained = enduse_func.get_enduse_configuration(
        mode_constrained=False,
        enduse='heating',
        enduse_space_heating=['heating'])

    assert mode_constrained == False

    # ---
    service_switches = [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='boilerA',
        switch_yr=2050)]

    mode_constrained = enduse_func.get_enduse_configuration(
        mode_constrained=True,
        enduse='heating',
        enduse_space_heating=['heating'])

    assert mode_constrained == True

    # ---
    fuel_switches = [read_data.FuelSwitch(
        enduse='heating',
        fueltype_replace="",
        technology_install='boilerB',
        switch_yr=2020,
        fuel_share_switched_ey=""
    )]

    service_switches = []

    mode_constrained = enduse_func.get_enduse_configuration(
        mode_constrained=False,
        enduse='heating',
        enduse_space_heating=['heating'])

    assert mode_constrained == False

def test_apply_cooling():
    """testing
    """
    strategy_vars = {'cooled_floorarea': {'cooling_enduse': {2015: 0, 2020: 0.5}}}

    assump_cooling_floorarea = 0.25
    fuel_y = np.array([100])

    result = enduse_func.apply_cooling(
        enduse='cooling_enduse',
        fuel_y=fuel_y,
        strategy_vars=strategy_vars,
        cooled_floorarea_p_by=assump_cooling_floorarea,
        curr_yr=2020)

    assert np.sum(result) == np.sum(fuel_y) * strategy_vars['cooled_floorarea']['cooling_enduse'][2020] / assump_cooling_floorarea