"""testing load_factors.py
"""
from energy_demand.profiles import load_factors
import numpy as np

def test_peak_shaving_max_min():
    """Test
    """
    fuel_yh = np.zeros((2, 1, 24)) #tow fueltypes one day
    # fill all first 100 days with one
    for fueltype in range(2):
        for hour in range(12):
            fuel_yh[fueltype][0][hour] = 1
        for hour in range(12, 24):
            fuel_yh[fueltype][0][hour] = 0.5
    average_yd = np.average(fuel_yh, axis=2)
    loac_factor_improvement = 0.1
    loadfactor_yd_cy_improved = (0.75 / 1) + loac_factor_improvement

    result = load_factors.peak_shaving_max_min(
        loadfactor_yd_cy_improved, average_yd, fuel_yh, mode_constrained=False)

    # ---------
    # expected
    # ---------
    max_daily_demand_allowed = 0.75 / (0.75 + 0.1)

    fuel_yh_expected = np.zeros((2, 1, 24))

    area_to_shift = (1 - max_daily_demand_allowed) * 12

    for fueltype in range(2):
        for hour in range(12):
            fuel_yh_expected[fueltype][0][hour] = max_daily_demand_allowed
        for hour in range(12, 24):
            fuel_yh_expected[fueltype][0][hour] = 0.5 + (area_to_shift / 12)

    np.testing.assert_equal(result, fuel_yh_expected)

def test_calc_lf_d():
    """Test
    """
    fuel_yh = np.ones((2, 2, 24)) #tow fueltype, Two day example

    fuel_yh[1][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[1][0][i] = 5
    for i in range(12, 24):
        fuel_yh[1][1][i] = 10
    average_per_day = np.average(fuel_yh, axis=2)

    result = load_factors.calc_lf_d(fuel_yh, average_per_day, mode_constrained=False)

    expected = np.zeros((2, 2))
    expected[1][0] = np.average(fuel_yh[1][0]) / np.max(fuel_yh[1][0]) * 100
    expected[1][1] = np.average(fuel_yh[1][1]) / np.max(fuel_yh[1][1]) * 100

    assert expected[1][0] == result[1][0]
    assert expected[1][1] == result[1][1]

def test_calc_lf_y():
    """Test
    """
    # fueltype, days, hours
    fuel_yh = np.ones((8, 365, 24)) #Two day example
    fuel_yh[2][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[2][0][i] = 5
    for i in range(12, 24):
        fuel_yh[2][1][i] = 10

    result = load_factors.calc_lf_y(fuel_yh)

    expected = np.zeros((8))
    expected[0] = np.average(fuel_yh[0]) / np.max(fuel_yh[0]) * 100
    expected[2] = np.average(fuel_yh[2]) / np.max(fuel_yh[2]) * 100

    assert expected[0] == result[0]
    assert expected[2] == result[2]

def test_calc_lf_season():
    """Test
    """
    # fueltype, days, hours
    fuel_yh = np.ones((8, 3, 24))
    seasons = {'seasonA': [1, 2]}  #Two day example, seasonA is second and third day

    fuel_yh[2][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[2][0][i] = 5
    for i in range(12, 24):
        fuel_yh[2][1][i] = 10
    average_per_day = np.average(fuel_yh, axis=2)

    result = load_factors.calc_lf_season(seasons, fuel_yh, average_per_day)

    expected = {'seasonA': np.zeros((8))}
    expected['seasonA'][2] = np.average(fuel_yh[2]) / np.max(fuel_yh[2][1:3]) * 100

    #if within seasons
    #expected['seasonA'][2] = np.average(fuel_yh[2][1:3]) / np.max(fuel_yh[2][1:3]) * 100
    assert expected['seasonA'][2] == result['seasonA'][2]
