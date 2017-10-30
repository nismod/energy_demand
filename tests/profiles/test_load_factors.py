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
        for hour in range(12,24):
            fuel_yh[fueltype][0][hour] = 0.5
    average_yd = np.average(fuel_yh, axis=2)
    loac_factor_improvement = 0.1
    loadfactor_yd_cy_improved = (0.75 / 1) + loac_factor_improvement

    result = load_factors.peak_shaving_max_min(
        loadfactor_yd_cy_improved, average_yd, fuel_yh)

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
    fuel_yh = np.ones((8, 2, 24)) #Two day example
    fuel_yh[2][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[2][0][i] = 5
    for i in range(12,24):
        fuel_yh[2][1][i] = 10

    result, result2 = load_factors.calc_lf_d(fuel_yh)

    expected = np.zeros((8, 2))
    expected[2][0] = np.average(fuel_yh[2][0]) / np.max(fuel_yh[2][0])
    expected[2][1] = np.average(fuel_yh[2][1]) / np.max(fuel_yh[2][1])

    assert expected[2][0] == result[2][0]
    assert expected[2][1] == result[2][1]

def test_calc_lf_y():
    """Test
    """
    # fueltype, days, hours
    fuel_yh = np.ones((8, 2, 24)) #Two day example
    fuel_yh[2][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[2][0][i] = 5
    for i in range(12, 24):
        fuel_yh[2][1][i] = 10

    result = load_factors.calc_lf_y(fuel_yh)

    expected = np.zeros((8))
    expected[0] = np.average(fuel_yh[0]) / np.max(fuel_yh[0])
    expected[2] = np.average(fuel_yh[2]) / np.max(fuel_yh[2])

    assert expected[0] == result[0]
    assert expected[2] == result[2]
