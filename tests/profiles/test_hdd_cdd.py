"""testing
"""
from energy_demand.profiles import hdd_cdd
import numpy as np

def test_calc_hdd():
    """testing
    """
    t_base = 15 #degree
    temp_yh = np.zeros((365, 24))
    
    for day in range(365):
        for hour in range(24):
            temp_yh[day][hour] = np.random.randint(-4, 30)

    result = hdd_cdd.calc_hdd(t_base, temp_yh)

    temp_yh[temp_yh > t_base] = t_base

    expected = np.sum(t_base - temp_yh) / 24

    # positive values
    assert round(np.sum(result), 3) == round(expected, 3)

def test_calc_cdd():
    """testing
    """
    t_base = 15 #degree
    temp_yh = np.zeros((365, 24))

    for day in range(365):
        for hour in range(24):
            temp_yh[day][hour] = np.random.randint(-4, 30)

    result = hdd_cdd.calc_cdd(t_base, temp_yh)

    temp_yh[temp_yh < t_base] = t_base

    expected = np.sum(temp_yh -t_base) / 24

    # positive values
    assert round(np.sum(result), 3) == round(expected, 3)

def test_sigm_temp():
    """
    """
    assumptions = {}
    assumptions['smart_meter_assump'] = {}
    assumptions['smart_meter_assump']['smart_meter_diff_params'] = {}
    assumptions['smart_meter_assump']['smart_meter_diff_params']['sig_midpoint'] = 0
    assumptions['smart_meter_assump']['smart_meter_diff_params']['sig_steeppness'] = 1
    yr_until_changed = 2020

    end_yr_t_base = 13
    assumptions['rs_t_base_heating'] = {}
    assumptions['rs_t_base_heating']['rs_t_base_heating_base_yr'] = 15
    assumptions['strategy_variables']['rs_t_base_heating']['rs_t_base_heating_future_yr'] = end_yr_t_base

    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    result = hdd_cdd.sigm_temp(
        sim_param,
        assumptions['smart_meter_assump']['smart_meter_diff_params'],
        assumptions['strategy_variables']['rs_t_base_heating']['rs_t_base_heating_future_yr'],
        assumptions['rs_t_base_heating']['rs_t_base_heating_base_yr'],
        yr_until_changed)

    expected = end_yr_t_base
    assert result == expected

def test_get_hdd_country():
    """testing
    """
    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    weather_stations = {
        "weater_station_A": {
            'station_latitude': 55.8695,
            'station_longitude': -4.4}}

    regions = ['reg_A', 'reg_B']

    temp_data = {
        "weater_station_A": np.zeros((365, 24)) + 12}

    base_temp_diff_params = {}
    base_temp_diff_params['sig_midpoint'] = 0
    base_temp_diff_params['sig_steeppness'] = 1
    base_temp_diff_params['yr_until_changed'] = 2020
    

    reg_coord = {
        "reg_A": {
            'latitude': 59.02999742,
            'longitude': -3.4},
        "reg_B": {
            'latitude': 57.02999742,
            'longitude': -4.4}}

    t_base_heating_future_yr = 15.5
    t_base_heating_base_yr = 15.5

    result = hdd_cdd.get_hdd_country(
        sim_param,
        regions,
        temp_data,
        base_temp_diff_params,
        t_base_heating_future_yr,
        t_base_heating_base_yr,
        reg_coord,
        weather_stations)
    
    expected = {
        "reg_A": (15.5 - 12.0) * 8760 / 24,
        "reg_B": (15.5 - 12.0) * 8760 / 24}

    assert result['reg_A'] == expected['reg_A']
    assert result['reg_B'] == expected['reg_B']

def test_get_cdd_country():
    """testing
    """
    sim_param = {
        'base_yr': 2015,
        'curr_yr': 2020}

    weather_stations = {
        "weater_station_A": {
            'station_latitude': 55.8695,
            'station_longitude': -4.4}}

    regions = ['reg_A', 'reg_B']

    temp_data = {
        "weater_station_A": np.zeros((365, 24)) + 20}

    base_temp_diff_params = {}
    base_temp_diff_params['sig_midpoint'] = 0
    base_temp_diff_params['sig_steeppness'] = 1
    base_temp_diff_params['yr_until_changed'] = 2020

    reg_coord = {
        "reg_A": {
            'latitude': 59.02999742,
            'longitude': -3.4},
        "reg_B": {
            'latitude': 57.02999742,
            'longitude': -4.4}}

    t_base_heating_base_yr = 15.5
    t_base_heating_future_yr = 15.5

    result = hdd_cdd.get_cdd_country(
        sim_param,
        regions,
        temp_data,
        base_temp_diff_params,
        t_base_heating_base_yr,
        t_base_heating_future_yr,
        reg_coord,
        weather_stations)

    expected = {
        "reg_A": (20 - 15.5) * 8760 / 24,
        "reg_B": (20 - 15.5) * 8760 / 24}

    assert result['reg_A'] == expected['reg_A']
    assert result['reg_B'] == expected['reg_B']

def test_calc_reg_hdd():
    """testing
    """
    t_base_heating = 15.5

    temperatures = np.zeros((365, 24)) + 12

    model_yeardays = range(365)

    result_hdd_d, result_shape = hdd_cdd.calc_reg_hdd(temperatures, t_base_heating, model_yeardays)

    assert np.sum(result_hdd_d) == (15.5 - 12) * 8760 / 24
    assert round(np.sum(result_shape), 3) == round(1.0, 3)

def test_calc_reg_cdd():
    """testing
    """
    t_base_heating = 15.5

    temperatures = np.zeros((365, 24)) + 20

    model_yeardays = range(365)

    result_hdd_d, result_shape = hdd_cdd.calc_reg_cdd(temperatures, t_base_heating, model_yeardays)

    assert np.sum(result_hdd_d) == (20 - 15.5) * 8760 / 24
    assert round(np.sum(result_shape), 3) == round(1.0, 3)
