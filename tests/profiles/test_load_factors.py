from energy_demand.profiles import load_factors
import numpy as np

'''def test_peak_shaving_max_min():
    """Test
    """
    fuel_yh = np.zeros((8, 365, 24))
    # fill all first 100 days with one
    for day in range(100):
        fuel_yh[:][day] = 1
    average_yd = np.average(fuel_yh, axis=2)
    loadfactor_yd_cy_improved = 0.1

    result = load_factors.peak_shaving_max_min(
        loadfactor_yd_cy_improved, average_yd, fuel_yh)

    # expected
    # ---------
    lf_cy_improved_d, peak_shift_crit = calc_lf_improvement(
        enduse, sim_param, loadfactor_yd_cy, )
    load_factor_cy = average_yd / 
    fuel_yh_expected = np.zeros((8, 365, 24))
    
    for day in range(100):
        fuel_yh_expected[:][day] = 1


    assert result'''

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
