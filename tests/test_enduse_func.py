"""Tests for enduse functions
"""
import numpy as np
from energy_demand import enduse_func
from energy_demand.scripts import s_generate_sigmoid
from energy_demand.plotting import plotting_program

'''def test_calc_fuel_tech_yh():
    
    enduse_func.calc_fuel_tech_yh(
        enduse='heating',
        sector=,
        enduse_techs,
        enduse_fuel_tech,
        tech_stock,
        load_profiles)
    pass'''

def test_get_crit_switch():
    """
    """
    mode_constrained = True
    fuelswitches = [{'enduse': 'heating'}]

    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    result = enduse_func.get_crit_switch(
        'heating', fuelswitches, sim_param, mode_constrained)
    
    assert result == False
    
    mode_constrained = False
    fuelswitches = [{'enduse': 'heating'}]

    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    result2 = enduse_func.get_crit_switch(
        'heating', fuelswitches, sim_param, mode_constrained)
    assert result2 == True

def test_get_peak_day():
    """
    """

    fuel_yh = np.zeros((8, 365, 24))
    fuel_yh[2][33] = 3

    result = enduse_func.get_peak_day(fuel_yh)

    expected = 33

    assert result == expected

def test_service_switch():
    """Test
    """
    # Install technology B and replace 50% of fueltype 0
    l_value = 0.9
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
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    tot_service_yh_cy = np.full((365, 24), 1.0) #constant share of 1 in every hour
    service_tech_by_p = {"boilerA": share_boilerA_by, "boilerB": share_boilerB_by}
    tech_increase_service = ["boilerA"]
    tech_decrease_service = ["boilerB"]
    tech_constant_service = []

    enduse = "heating"
    sig_param_tech = {
        enduse :{
            "boilerA": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }

    result = enduse_func.service_switch(
        enduse,
        tot_service_yh_cy,
        service_tech_by_p,
        tech_increase_service,
        tech_decrease_service,
        tech_constant_service,
        sig_param_tech,
        curr_yr)

    expected_service_tech_cy_p = {
        "boilerA": 365*24 * share_boilerA_cy, # * 0.5
        "boilerB": 365*24 * share_boilerB_cy} # * 0.5
    #print(round(expected_service_tech_cy_p["boilerA"], 3))
    #print(round(np.sum(result["boilerA"]), 3))
    #print(round(expected_service_tech_cy_p["boilerB"], 3) )
    #print(round(np.sum(result["boilerB"]), 3))
    assert round(expected_service_tech_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_service_tech_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    # --------------------------------------------
    l_value = 1.0
    share_boilerA_by = 0
    share_boilerA_cy = 1

    share_boilerB_by = 1
    share_boilerB_cy = 0

    base_yr = 2020
    curr_yr = 2060
    end_yr = 2060

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    tot_service_yh_cy = np.full((365, 24), 1.0) #constant share of 1 in every hour
    service_tech_by_p = {"boilerA": share_boilerA_by, "boilerB": share_boilerB_by}
    tech_increase_service = ["boilerA"]
    tech_decrease_service = ["boilerB"]
    tech_constant_service = []

    enduse = "heating"
    sig_param_tech = {
        enduse :{
            "boilerA": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }

    result = enduse_func.service_switch(
        enduse,
        tot_service_yh_cy,
        service_tech_by_p,
        tech_increase_service,
        tech_decrease_service,
        tech_constant_service,
        sig_param_tech,
        curr_yr)

    half_time_factor = 1
    expected_service_tech_cy_p = {
        "boilerA": 365*24,
        "boilerB": 0}

    assert round(expected_service_tech_cy_p["boilerA"], 3) == round(np.sum(result["boilerA"]), 3)
    assert round(expected_service_tech_cy_p["boilerB"], 3) == round(np.sum(result["boilerB"]), 3)

    # --------------------------------------------

    l_value = 1.0
    share_boilerA_by = 0.0001
    share_boilerB_by = 0.9999

    share_boilerA_cy = 0.9999
    share_boilerB_cy = 0.0000

    base_yr = 2020.0
    curr_yr = 2040.0
    end_yr = 2060.0

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerA_by, share_boilerA_cy])
    assert l_value >= share_boilerA_cy

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    #plot sigmoid curve
    #plotting_program.plotout_sigmoid_tech_diff(l_value, "GG", "DD", xdata, ydata, fit_parameter, False)

    tot_service_yh_cy = np.full((365, 24), 1.0) #constant share of 1 in every hour
    service_tech_by_p = {"boilerA": share_boilerA_by, "boilerB": share_boilerB_by}
    tech_increase_service = ["boilerA"]
    tech_decrease_service = ["boilerB"]
    tech_constant_service = []

    enduse = "heating"
    sig_param_tech = {
        enduse :{
            "boilerA": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }

    result = enduse_func.service_switch(
        enduse,
        tot_service_yh_cy,
        service_tech_by_p,
        tech_increase_service,
        tech_decrease_service,
        tech_constant_service,
        sig_param_tech,
        curr_yr)

    expected_service_tech_cy_p = {
        "boilerA": 365*24*0.5,
        "boilerB": 365*24*0.5}

    assert round(expected_service_tech_cy_p["boilerA"], 1) == round(np.sum(result["boilerA"]), 1)
    assert round(expected_service_tech_cy_p["boilerB"], 1) == round(np.sum(result["boilerB"]), 1)

def test_fuel_switch():
    """
    """
    # Example: Replace fueltype 1 by 50% with boilerB
    base_yr = 2020.0
    curr_yr = 2040.0 # 2060
    end_yr = 2060.0

    share_boilerA_by = 0.5
    share_boilerB_by = 1 - share_boilerA_by
    
    fueltype_boilerA = 0
    fueltype_boilerB = 1
    share_fuel_consumption_switched = 0.5
    l_value = 1.0

    share_boilerA_ey = share_boilerA_by - (share_boilerA_by * share_fuel_consumption_switched)
    share_boilerB_ey = 1 - share_boilerA_ey

    installed_tech = ['boilerB']

    tot_service_yh_cy = np.ones((365, 24)) # Absolute total yh energy service per technology and fueltype

    # Service distribution by
    service_tech = {
        'boilerA': np.ones((365, 24)) * share_boilerA_by,
        'boilerB': np.ones((365, 24)) * share_boilerB_by}

    # Fraction of energy service per fueltype and technology (within every fueltype sums up to one)
    service_fueltype_tech_cy_p = {
        fueltype_boilerA: {'boilerA': 1.0}, 
        fueltype_boilerB: {'boilerB': 1.0}}

    # Fraction of service per fueltype (within every fueltype sums up to one)
    service_fueltype_cy_p = {
        fueltype_boilerA: 1.0,
        fueltype_boilerB: 1.0} #share of fuels

    fuel_switches = [{
        'enduse' : 'heating',
        'enduse_fueltype_replace' : fueltype_boilerA,
        'technology_install': 'boilerB',
        'year_fuel_consumption_switched': end_yr,
        'share_fuel_consumption_switched': share_fuel_consumption_switched,
        'max_theoretical_switch' : l_value}]

    fuel_tech_p_by = {0: {'boilerA': 1.0}, 1: {'boilerB': 1.0}} #share of fuels

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerB_by, share_boilerB_ey])
    assert l_value >= share_boilerB_ey

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    sig_param_tech = {
        'heating' :{
            "boilerB": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }
    #plot sigmoid curve
    #plotting_program.plotout_sigmoid_tech_diff(l_value, "GG", "DD", xdata, ydata, fit_parameter, False)

    expected = enduse_func.fuel_switch(
        'heating',
        installed_tech,
        sig_param_tech,
        tot_service_yh_cy,
        service_tech,
        service_fueltype_tech_cy_p,
        service_fueltype_cy_p,
        fuel_switches,
        fuel_tech_p_by,
        curr_yr
        )
    # for 20204: 0.0134 because of fit (which is not as good as 0.625)
    boilerA_cy = np.sum(expected["boilerA"])
    boilerB_cy = np.sum(expected["boilerB"])
    '''print(boilerA_cy)
    print(8760 * (1 - (0.5 + (0.134))))
    print(boilerB_cy)
    print(8760 * (0.5 + (0.134)))'''
    assert round(boilerA_cy, 0) == round(8760 * (1 - (0.5 + (0.134))), 0)
    assert round(boilerB_cy, 0) == round(8760 * (0.5 + (0.134)), 0)

    # --------------------------------------------------------
    base_yr = 2020.0
    curr_yr = 2060.0 # 2060
    end_yr = 2060.0

    share_boilerA_by = 0.5
    share_boilerB_by = 1 - share_boilerA_by
    
    fueltype_boilerA = 0
    fueltype_boilerB = 1
    share_fuel_consumption_switched = 0.5
    l_value = 1.0

    share_boilerA_ey = share_boilerA_by - (share_boilerA_by * share_fuel_consumption_switched)
    share_boilerB_ey = 1 - share_boilerA_ey

    installed_tech = ['boilerB']

    tot_service_yh_cy = np.ones((365, 24)) # Absolute total yh energy service per technology and fueltype

    # Service distribution by
    service_tech = {
        'boilerA': np.ones((365, 24)) * share_boilerA_by,
        'boilerB': np.ones((365, 24)) * share_boilerB_by}

    # Fraction of energy service per fueltype and technology (within every fueltype sums up to one)
    service_fueltype_tech_cy_p = {
        fueltype_boilerA: {'boilerA': 1.0}, 
        fueltype_boilerB: {'boilerB': 1.0}}

    # Fraction of service per fueltype (within every fueltype sums up to one)
    service_fueltype_cy_p = {
        fueltype_boilerA: 1.0,
        fueltype_boilerB: 1.0} #share of fuels

    fuel_switches = [{
        'enduse' : 'heating',
        'enduse_fueltype_replace' : fueltype_boilerA,
        'technology_install': 'boilerB',
        'year_fuel_consumption_switched': end_yr,
        'share_fuel_consumption_switched': share_fuel_consumption_switched,
        'max_theoretical_switch' : l_value}]

    fuel_tech_p_by = {0: {'boilerA': 1.0}, 1: {'boilerB': 1.0}} #share of fuels

    # ----- Calculate sigmoids
    xdata = np.array([base_yr, end_yr])
    ydata = np.array([share_boilerB_by, share_boilerB_ey])
    assert l_value >= share_boilerB_ey

    # fit parameters
    fit_parameter = s_generate_sigmoid.calc_sigmoid_parameters(
        l_value,
        xdata,
        ydata,
        fit_crit_a=200,
        fit_crit_b=0.001)

    sig_param_tech = {
        'heating' :{
            "boilerB": {
                'midpoint': fit_parameter[0],
                'steepness': fit_parameter[1],
                'l_parameter': l_value}
        }
    }
    #plot sigmoid curve
    #plotting_program.plotout_sigmoid_tech_diff(l_value, "GG", "DD", xdata, ydata, fit_parameter, False)

    expected = enduse_func.fuel_switch(
        'heating',
        installed_tech,
        sig_param_tech,
        tot_service_yh_cy,
        service_tech,
        service_fueltype_tech_cy_p,
        service_fueltype_cy_p,
        fuel_switches,
        fuel_tech_p_by,
        curr_yr
        )
    #
    boilerA_cy = np.sum(expected["boilerA"])
    boilerB_cy = np.sum(expected["boilerB"])
    assert round(boilerA_cy, 0) == 8760 * 0.25
    assert round(boilerB_cy, 0) == 8760 * 0.75

def test_convert_service_to_p():
    """Testing
    """
    tot_service_y = 8760
    service_fueltype_tech = {
        0:{
        'techA': 8760 * 0.5,
        'techB': 8760 * 0.5}
        }

    expected = enduse_func.convert_service_to_p(tot_service_y, service_fueltype_tech)

    assert expected['techA'] == 0.5
    assert expected['techB'] == 0.5

def test_convert_service_tech_to_p():
    """testing
    """
    service = {
        0: {'techA': 50, 'techB': 50},
        1: {'techC': 50, 'techD': 150}}

    expected = enduse_func.convert_service_tech_to_p(service)
    print(expected)
    assert expected[0]['techA'] == 50.0 / 100
    assert expected[0]['techB'] == 50.0 / 100
    assert expected[1]['techC'] == 50.0 / 200
    assert expected[1]['techD'] == 150.0 / 200

def test_calc_lf_improvement():
    """
    """
    base_yr = 2010
    curr_yr = 2015
    sim_period_yrs = 11
    sim_param = {'base_yr': base_yr, 'curr_yr': curr_yr, 'sim_period_yrs': sim_period_yrs}
    lf_improvement_ey = {'heating': 0.5} #50% improvement

    #all factors must be smaller than one
    loadfactor_yd_cy = np.zeros((2, 2)) #to fueltypes, two days
    loadfactor_yd_cy[0][0] = 0.2
    loadfactor_yd_cy[0][1] = 0.4
    loadfactor_yd_cy[1][0] = 0.1
    loadfactor_yd_cy[1][1] = 0.3

    result, crit = enduse_func.calc_lf_improvement('heating', sim_param, loadfactor_yd_cy, lf_improvement_ey)

    expected = loadfactor_yd_cy + 0.25

    assert crit == True
    assert result[0][0] == expected[0][0]
    assert result[0][1] == expected[0][1]
    assert result[1][0] == expected[1][0]
    assert result[1][1] == expected[1][1]

def test_Enduse():
    """
    """
    '''enduse_funct.Enduse(
        region_name="testregion",
        data,
        enduse,
        sector,
        fuel,
        tech_stock,
        heating_factor_y,
        cooling_factor_y,
        fuel_switches,
        service_switches,
        fuel_tech_p_by,
        tech_increased_service,
        tech_decreased_share,
        tech_constant_share,
        installed_tech,
        sig_param_tech,
        enduse_overall_change_ey,
        regional_lp_stock
        )'''
    pass

def test_get_enduse_tech():
    """Testing
    """
    fuel_tech_p_by = {
        0: {'techA': 0.4, 'techB': 0.6},
        1: {'techC': 0.4, 'techD': 0.6}}
    result = enduse_func.get_enduse_tech(fuel_tech_p_by)
    expected = ['techA', 'techB', 'techC', 'techD']
    assert expected[0] in result
    assert expected[1] in result
    assert expected[2] in result
    assert expected[3] in result

    fuel_tech_p_by = {
        0: {'techA': 0.4, 'techB': 0.6},
        1: {'dummy_tech': 0.4, 'techD': 0.6}}
    result = enduse_func.get_enduse_tech(fuel_tech_p_by)
    expected = []
    assert expected == result
