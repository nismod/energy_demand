"""Tests for enduse functions
"""
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.read_write import read_data
from energy_demand.technologies import technological_stock
from energy_demand.profiles import load_profile

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
        shape_yd=np.full((365,24), 1 / 365),
        shape_yh=shape_yh,
        sectors=['test_sector'],
        f_peak_yd=1.0/365,
        shape_peak_dh=np.full((24), 1.0/24))

    fuel_new_y = np.zeros((3, ))
    fuel_new_y[2] = 100
    fuel_yh, fuel_peak_dh, fuel_peak_h = enduse_func.assign_lp_no_techs(
        enduse="test_enduse",
        sector="test_sector",
        load_profiles=lp_stock_obj,
        fuel_new_y=fuel_new_y)

    assert np.sum(fuel_yh) == 100
    assert np.sum(fuel_peak_dh) == 100 * (1.0/365)
    assert fuel_peak_h[2] == fuel_peak_dh[2][0]

def test_get_crit_switch():
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

    assert result2 == False

def test_get_peak_day():
    """testing
    """

    fuel_yh = np.zeros((8, 365, 24))
    fuel_yh[2][33] = 3

    result = enduse_func.get_peak_day_all_fueltypes(fuel_yh)

    expected = 33

    assert result == expected

def test_service_switch():
    """Test
    """
    # Install technology B and replace 50% of fueltype 0
    l_value = 1.0

    share_boilerA_by = 0.1
    share_boilerA_cy = 0.2 #1
    share_boilerB_by = 0.9
    share_boilerB_cy = 0.8

    base_yr = 2020
    curr_yr = 2060
    end_yr = 2060

    # ----- Calculate sigmoids

    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    ydataB = np.array([share_boilerB_by, share_boilerB_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata)

    fit_parameterB = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydataB)

    tot_s_yh_cy = {
        'boilerA': 365*24,
        'boilerB': 365*24, }#constant share of 1 in every hour

    s_tech_by_p = {
        "boilerA": share_boilerA_by,
        "boilerB": share_boilerB_by}

    all_technologies = ['boilerA', 'boilerB']

    sig_param_tech = {
            "boilerA": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value},
            "boilerB": {
                'midpoint': fit_parameterB[0],
                'steepness': fit_parameterB[1],
                'l_parameter': l_value}}

    result = enduse_func.calc_service_switch(
        s_tech_y_cy=tot_s_yh_cy,
        s_tech_by_p=s_tech_by_p,
        all_technologies=all_technologies,
        sig_param_tech=sig_param_tech,
        curr_yr=curr_yr)

    expected_tech_service_cy_p = {
        "boilerA": 365*24*2 * share_boilerA_cy, # * 0.5
        "boilerB": 365*24*2 * share_boilerB_cy} # * 0.5

    assert round(expected_tech_service_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_tech_service_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    # --------------------------------------------
    
    l_value = 1.0
    share_boilerA_by = 0.01
    share_boilerA_cy = 0.99

    share_boilerB_by = 0.99
    share_boilerB_cy = 0.01

    base_yr = 2020
    curr_yr = 2060
    end_yr = 2060

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    ydataB = np.array([share_boilerB_by, share_boilerB_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata)

    fit_parameterB = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydataB)

    s_tech_by_p = {
        "boilerA": share_boilerA_by,
        "boilerB": share_boilerB_by}

    sig_param_tech = {
        "boilerA": {
            'midpoint': fit_parameter[0],
            'steepness': fit_parameter[1],
            'l_parameter': l_value},
        "boilerB": {
            'midpoint': fit_parameterB[0],
            'steepness': fit_parameterB[1],
            'l_parameter': l_value},
        }

    result = enduse_func.calc_service_switch(
        tot_s_yh_cy,
        s_tech_by_p,
        all_technologies,
        sig_param_tech,
        curr_yr)

    half_time_factor = 1
    expected_tech_service_cy_p = {
        "boilerA": (365*24*2) * 0.99,
        "boilerB": (365*24*2) * 0.01}

    assert round(expected_tech_service_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_tech_service_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    # --------------------------------------------

    l_value = 1.0
    share_boilerA_by = 0.0001
    share_boilerB_by = 0.9999

    share_boilerA_cy = 0.9999
    share_boilerB_cy = 0.0001

    base_yr = 2020.0
    curr_yr = 2040.0
    end_yr = 2060.0

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    ydataB = np.array([share_boilerB_by, share_boilerB_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata)
    fit_parameterB = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydataB)

    s_tech_by_p = {
        "boilerA": share_boilerA_by,
        "boilerB": share_boilerB_by}

    enduse = "heating"
    sig_param_tech = {
        "boilerA": {
            'midpoint': fit_parameter[0],
            'steepness': fit_parameter[1],
            'l_parameter': l_value},
        "boilerB": {
            'midpoint': fit_parameterB[0],
            'steepness': fit_parameterB[1],
            'l_parameter': l_value},
    }

    result = enduse_func.calc_service_switch(
        tot_s_yh_cy,
        s_tech_by_p,
        all_technologies,
        sig_param_tech,
        curr_yr)

    expected_tech_service_cy_p = {
        "boilerA": 365*24*0.5*2,
        "boilerB": 365*24*0.5*2}

    assert round(expected_tech_service_cy_p["boilerA"], 1) == round(np.sum(result["boilerA"]), 1)
    assert round(expected_tech_service_cy_p["boilerB"], 1) == round(np.sum(result["boilerB"]), 1)

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
    base_yr = 2010
    curr_yr = 2015

    lf_improvement_ey = 0.5

    #all factors must be smaller than one
    loadfactor_yd_cy = np.zeros((2, 2)) #to fueltypes, two days
    loadfactor_yd_cy[0][0] = 0.2
    loadfactor_yd_cy[0][1] = 0.4
    loadfactor_yd_cy[1][0] = 0.1
    loadfactor_yd_cy[1][1] = 0.3
    yr_until_change = 2020

    result = enduse_func.calc_lf_improvement(
        lf_improvement_ey,
        base_yr,
        curr_yr,
        loadfactor_yd_cy,
        yr_until_change)

    expected = loadfactor_yd_cy + 0.25

    assert result[0][0] == expected[0][0]
    assert result[0][1] == expected[0][1]
    assert result[1][0] == expected[1][0]
    assert result[1][1] == expected[1][1]

def test_Enduse():
    """
    """
    pass

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

    sm_assump_strategy = {}
    sm_assump_strategy['smart_meter_yr_until_changed'] = 2020
    sm_assump_strategy['smart_meter_improvement_heating'] = 0.5 #50% improvement
    sm_assump_strategy['smart_meter_improvement_p'] = 1.0
    sm_assump = {}
    sm_assump['smart_meter_diff_params'] = {}
    sm_assump['smart_meter_diff_params']['sig_midpoint'] = 0
    sm_assump['smart_meter_diff_params']['sig_steepness'] = 1
    sm_assump['smart_meter_p_by'] = 0

    result = enduse_func.apply_smart_metering(
        enduse='heating',
        fuel_y=100,
        sm_assump=sm_assump,
        sm_assump_strategy=sm_assump_strategy,
        base_yr=2015,
        curr_yr=2020)

    assert result == 50

def test_fuel_to_service():
    """
    """
    enduse = 'heating'
    fuel_new_y = {0: 2000}
    enduse_techs = ['techA']
    fuel_fueltype_tech_p_by = {0 : {'techA': 1.0}}

    technologies = {'techA': read_data.TechnologyData()}
    technologies['techA'].fueltype_str = 'gas'
    technologies['techA'].eff_achieved = 1.0
    technologies['techA'].diff_method = 'linear'
    technologies['techA'].eff_by = 0.5
    technologies['techA'].eff_ey = 0.5
    technologies['techA'].year_eff_ey = 2020
    
    fueltypes = {'gas': 0} #, 'heat': 1}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        tech_list={'heating_non_const': [], 'heating_const': ['techA']},
        other_enduse_mode_info={'linear'},
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
        fuel_new_y=fuel_new_y,
        fuel_fueltype_tech_p_by=fuel_fueltype_tech_p_by,
        tech_stock=tech_stock,
        fueltypes=fueltypes,
        mode_constrained=True)

    assert service_tech['techA'] == 1000

    # ---
    fuel_fueltype_tech_p_by = {0: {}, 1 : {'techA': 1.0}} #'placeholder_tech': 1.0}}
    fuel_new_y = {0: 0, 1: 2000}
    fuel_tech_p_by = {0 : {}, 1: {'techA': 1.0}}
    fueltypes = {'gas': 0, 'heat': 1}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        tech_list={'heating_non_const': [], 'heating_const': ['techA']},
        other_enduse_mode_info={'linear'},
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
        fuel_new_y=fuel_new_y,
        fuel_fueltype_tech_p_by=fuel_fueltype_tech_p_by,
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

    fueltypes = {'gas': 0}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        tech_list={'heating_non_const': [], 'heating_const': ['techA']},
        other_enduse_mode_info={'linear'},
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})

    fuel_new_y, fuel_per_tech = enduse_func.service_to_fuel(
        "heating",
        {'techA': 100},
        tech_stock,
        len(fueltypes),
        fueltypes,
        True)

    assert fuel_per_tech['techA'] == 200
    assert fuel_new_y == np.array([200])

    # ----

    fueltypes = {'gas': 0, 'heat': 1}

    fuel_new_y, fuel_per_tech = enduse_func.service_to_fuel(
        "heating",
        {'techA': 100},
        tech_stock,
        len(fueltypes),
        fueltypes,
        False)

    assert fuel_per_tech['techA'] == 100
    assert fuel_new_y[1] == 100

def test_apply_heat_recovery():
    """Testing"""
    other_enduse_mode_info = {}
    other_enduse_mode_info['other_enduse_mode_info'] = {}
    other_enduse_mode_info['other_enduse_mode_info']['sigmoid'] = {}
    other_enduse_mode_info['other_enduse_mode_info']['sigmoid']['sig_midpoint'] = 0
    other_enduse_mode_info['other_enduse_mode_info']['sigmoid']['sig_steepness'] = 1

    result, result_tech = enduse_func.apply_heat_recovery(
        enduse='heating',
        strategy_variables={'heat_recoved__heating': 0.5, 'heat_recovered_yr_until_changed': 2020},
        enduse_overall_change=other_enduse_mode_info,
        service=100,
        service_techs={'techA': 100},
        base_yr=2015,
        curr_yr=2020)

    assert result == 50
    assert result_tech == {'techA': 50}

def test_apply_climate_chante():
    """Testing"""

    result = enduse_func.apply_climate_change(
        enduse='heating',
        fuel_new_y=200,
        cooling_factor_y=1.5,
        heating_factor_y=1.5,
        enduse_space_heating=['heating'],
        enduse_space_cooling=['cooling'])

    assert result == 300
    result = enduse_func.apply_climate_change(
        enduse='cooling',
        fuel_new_y=200,
        cooling_factor_y=1.5,
        heating_factor_y=1.5,
        enduse_space_heating=['heating'],
        enduse_space_cooling=['cooling'])

    assert result == 300

def test_calc_fuel_tech_y():
    """Testing
    """
    technologies = {'techA': read_data.TechnologyData()}
    technologies['techA'].fueltype_str = 'gas'
    technologies['techA'].eff_achieved = 1.0
    technologies['techA'].diff_method = 'linear'
    technologies['techA'].eff_by = 0.5
    technologies['techA'].eff_ey = 0.5
    technologies['techA'].year_eff_ey = 2020
    fueltypes = {'gas': 0}

    tech_stock = technological_stock.TechStock(
        name="name",
        technologies=technologies,
        tech_list={'heating_non_const': [], 'heating_const': ['techA']},
        other_enduse_mode_info={'linear'},
        base_yr=2015,
        curr_yr=2020,
        fueltypes=fueltypes,
        temp_by=np.ones((365, 24)) + 10,
        temp_cy=np.ones((365, 24)) + 10,
        t_base_heating_by=15.5,
        potential_enduses=['heating'],
        t_base_heating_cy=15.5,
        enduse_technologies={'heating': ['techA']})
    
    result = enduse_func.calc_fuel_tech_y(
        enduse='heating',
        tech_stock=tech_stock,
        fuel_tech_y={'techA': 100},
        fueltypes_nr=2,
        fueltypes={'heat': 1, 'gas': 0},
        mode_constrained=False)

    assert result[1] == 100

    result = enduse_func.calc_fuel_tech_y(
        enduse='heating',
        tech_stock=tech_stock,
        fuel_tech_y={'techA': 100},
        fueltypes_nr=2,
        fueltypes={'heat': 1, 'gas': 0},
        mode_constrained=True)

    assert result[0] == 100

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
        tech_list={'heating_non_const': [], 'heating_const': ['techA']},
        other_enduse_mode_info={'linear'},
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

    lp_stock_obj.add_lp(
        unique_identifier="A123",
        technologies=['techA'],
        enduses=['heating'],
        shape_yd=np.full((365,24), 1 / 365),
        shape_yh=shape_yh,
        sectors=['sectorA'],
        f_peak_yd=1.0/365,
        shape_peak_dh=np.full((24), 1.0/24))

    fuel = 200
    results = enduse_func.calc_fuel_tech_yh(
        enduse='heating',
        sector='sectorA',
        enduse_techs=['techA'],
        enduse_fuel_tech={'techA': fuel},
        load_profiles=lp_stock_obj,
        fueltypes_nr=2,
        fueltypes=fueltypes,
        mode_constrained=False,
        model_yeardays_nrs=365)

    assert results[1][3][0] == 3.0 / float(np.sum(range(365)) * 24) * 200

    # ---
    results = enduse_func.calc_fuel_tech_yh(
        enduse='heating',
        sector='sectorA',
        enduse_techs=['techA'],
        enduse_fuel_tech={'techA': fuel},
        load_profiles=lp_stock_obj,
        fueltypes_nr=2,
        fueltypes=fueltypes,
        model_yeardays_nrs=365,
        mode_constrained=True)

    assert results['techA'][3][0] == 3.0 / float(np.sum(range(365)) * 24) * 200

def test_apply_specific_change():
    """testing
    """
    enduse_overall_change_strategy = {}
    enduse_overall_change_strategy['enduse_change__{}'.format('heating')] = 2.0
    enduse_overall_change_strategy['enduse_specific_change_yr_until_changed'] = 2020
    enduse_overall_change = {}
    enduse_overall_change['other_enduse_mode_info'] = {}
    enduse_overall_change['other_enduse_mode_info']['diff_method'] = 'linear'

    fuel_y = np.array([100])
    result = enduse_func.apply_specific_change(
        enduse='heating',
        fuel_y=fuel_y,
        enduse_overall_change=enduse_overall_change,
        enduse_overall_change_strategy=enduse_overall_change_strategy,
        base_yr=2015,
        curr_yr=2020)

    assert result == fuel_y * enduse_overall_change_strategy['enduse_change__heating']

def test_get_enduse_configuration():
    """Testing
    """
    fuel_switches = [read_data.FuelSwitch(
        enduse='heating',
        fueltype_replace="",
        technology_install='boilerB',
        switch_yr=2020,
        fuel_share_switched_ey=""
    )]

    service_switches = [read_data.ServiceSwitch(
        technology_install='boilerA',
        switch_yr=2050)]

    mode_constrained, crit_switch_service = enduse_func.get_enduse_configuration(
        mode_constrained=False,
        enduse='heating',
        sector=None,
        enduse_space_heating=['heating'],
        base_yr=2015,
        curr_yr=2020,
        service_switches=service_switches)

    assert mode_constrained == False

    # If constrained mode, no switches
    assert crit_switch_service == False

    # ---
    service_switches = [read_data.ServiceSwitch(
        enduse='heating',
        technology_install='boilerA',
        switch_yr=2050)]

    mode_constrained, crit_switch_service = enduse_func.get_enduse_configuration(
        mode_constrained=True,
        enduse='heating',
        sector=None,
        enduse_space_heating=['heating'],
        base_yr=2015,
        curr_yr=2020,
        service_switches=service_switches)

    assert mode_constrained == True

    # If constrained mode, no switches
    assert crit_switch_service == True

    # ---

    fuel_switches = [read_data.FuelSwitch(
        enduse='heating',
        fueltype_replace="",
        technology_install='boilerB',
        switch_yr=2020,
        fuel_share_switched_ey=""
    )]

    service_switches = []

    mode_constrained, crit_switch_service = enduse_func.get_enduse_configuration(
        mode_constrained=False,
        enduse='heating',
        sector=False,
        enduse_space_heating=['heating'],
        base_yr=2015,
        curr_yr=2020,
        service_switches=service_switches)

    assert mode_constrained == False
    assert crit_switch_service == False

def test_apply_cooling():
    """testing
    """
    other_enduse_mode_info = {}
    other_enduse_mode_info['sigmoid'] = {}
    other_enduse_mode_info['sigmoid']['sig_midpoint'] = 0
    other_enduse_mode_info['sigmoid']['sig_steepness'] = 1

    strategy_variables = {}
    strategy_variables['cooled_floorarea_yr_until_changed'] = 2020
    strategy_variables['cooled_floorarea__{}'.format('cooling_enduse')] = 0.5

    assump_cooling_floorarea = 0.25
    fuel_y = np.array([100])

    result = enduse_func.apply_cooling(
        enduse='cooling_enduse',
        fuel_y=fuel_y,
        strategy_variables=strategy_variables,
        cooled_floorarea_p_by=assump_cooling_floorarea,
        other_enduse_mode_info=other_enduse_mode_info,
        base_yr=2015,
        curr_yr=2020)

    assert np.sum(result) == np.sum(fuel_y) * strategy_variables['cooled_floorarea__{}'.format('cooling_enduse')] / assump_cooling_floorarea

def test_test():
    """Test
    """
    # Install technology B and replace 50% of fueltype 0
    tot_service = 3724.1471455
    s_tech_by_p = {
        'boiler_solid_fuel': 0.0,
        'boiler_gas': 0.97611092943131095,
        'boiler_electricity': 0.017996039327478529,
        'heat_pumps_electricity': 0.0030527472564444167,
        'district_heating_electricity': 0.0,
        'boiler_oil': 0.0028402839847661808,
        'boiler_biomass': 0.0, 'boiler_hydrogen': 0.0, 'heat_pumps_hydrogen': 0.0}

    s_tech_y_cy = {}
    for tech in s_tech_by_p.keys():
        s_tech_y_cy[tech] = s_tech_by_p[tech] * tot_service

    tech_decrease_service = {
        'boiler_gas': 0.076246771740129615}

    tech_constant_service = {
        'boiler_solid_fuel': 0.0,
        'boiler_electricity': 0.12775323519770218,
        'district_heating_electricity': 0.0,
        'boiler_oil': 0.089723510057254471,
        'boiler_biomass': 0.0,
        'boiler_hydrogen': 0.0,
        'heat_pumps_hydrogen': 0.0}

    tech_increase_service = {'heat_pumps_electricity': 0.70627648300491375}
    sig_param_tech = {
        'heat_pumps_electricity': {
            'midpoint': 36.713854146192347, 'steepness': 0.16754533086981224, 'l_parameter': 0.78252325474504336}}
    curr_yr = 2050

    result = enduse_func.calc_service_switch(
        s_tech_y_cy=s_tech_y_cy,
        s_tech_by_p=s_tech_by_p,
        all_technologies=tech_increase_service, #s_tech_by_p.keys(),
        sig_param_tech=sig_param_tech,
        curr_yr=curr_yr)
    summe = 0.70627648300491375 * 3724.1471455
    assert result['heat_pumps_electricity'] == summe
