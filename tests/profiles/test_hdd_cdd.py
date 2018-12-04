"""testing
"""
from energy_demand.profiles import hdd_cdd
import numpy as np

def calc_weekend_corr_f():
    """Testing
    """
    wkend_factor = 0.5
    model_yeardays_daytype = ['working_day', 'holiday']
    result = hdd_cdd.calc_weekend_corr_f(
        model_yeardays_daytype=model_yeardays_daytype,
        wkend_factor=wkend_factor)

    assert result[0] == 1.0
    assert result[1] == wkend_factor

def test_effective_temps():
    """Testing
    """
    temp_yh = np.zeros((365, 24))

    for day in range(365):
        for hour in range(24):
            temp_yh[day][hour] = np.random.randint(-4, 30)

    result = hdd_cdd.effective_temps(temp_yh, nr_day_to_av=1)

    expected = (temp_yh[0] + temp_yh[1]) / 2

    expected2 = (expected + temp_yh[2]) / 2

    # positive values
    np.testing.assert_array_equal(result[1], expected)

    np.testing.assert_array_equal(result[2], expected2)

def test_calc_hdd():
    """testing
    """
    t_base = 15 #degree
    temp_yh = np.zeros((365, 24))
    
    for day in range(365):
        for hour in range(24):
            temp_yh[day][hour] = np.random.randint(-4, 30)
    
    # Test with hourly input data
    result = hdd_cdd.calc_hdd(t_base, temp_yh, nr_day_to_av=0, crit_temp_min_max=False)

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

    result = hdd_cdd.calc_cdd(t_base, temp_yh, nr_day_to_av=0)

    temp_yh[temp_yh < t_base] = t_base

    expected = np.sum(temp_yh - t_base) / 24

    # positive values
    assert round(np.sum(result), 3) == round(expected, 3)

def test_get_hdd_country():
    """testing
    """

    base_yr = 2015
    curr_yr = 2020

    weather_stations = {
        "weater_station_A": {
            'latitude': 55.8695,
            'longitude': -4.4}}

    regions = ['reg_A', 'reg_B']

    temp_data = {
        "weater_station_A": np.zeros((365, 24)) + 12}

    base_temp_diff_params = {}
    base_temp_diff_params['sig_midpoint'] = 0
    base_temp_diff_params['sig_steepness'] = 1
    base_temp_diff_params['yr_until_changed'] = 2020

    reg_coord = {
        "reg_A": {
            'latitude': 59.02999742,
            'longitude': -3.4},
        "reg_B": {
            'latitude': 57.02999742,
            'longitude': -4.4}}

    t_base_heating_base_yr = 15.5

    result = hdd_cdd.get_hdd_country(
        t_base_heating_base_yr,
        regions,
        temp_data,
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
    weather_stations = {
        "weater_station_A": {
            'latitude': 55.8695,
            'longitude': -4.4}}

    regions = ['reg_A', 'reg_B']

    temp_data = {
        "weater_station_A": np.zeros((365, 24)) + 20}

    base_temp_diff_params = {}
    base_temp_diff_params['sig_midpoint'] = 0
    base_temp_diff_params['sig_steepness'] = 1
    base_temp_diff_params['yr_until_changed'] = 2020

    reg_coord = {
        "reg_A": {
            'latitude': 59.02999742,
            'longitude': -3.4},
        "reg_B": {
            'latitude': 57.02999742,
            'longitude': -4.4}}

    t_base_heating_base_yr = 15.5

    result = hdd_cdd.get_cdd_country(
        t_base_heating_base_yr,
        regions,
        temp_data,
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
