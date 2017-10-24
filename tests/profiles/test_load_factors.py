from energy_demand.profiles import load_factors
import numpy as np

def test_daily_load_factors():
    """Test
    """
    fuel_yh = np.ones((8, 2, 24)) #Two day example
    fuel_yh[2][1] = np.array((range(24)))
    for i in range(12):
        fuel_yh[2][0][i] = 5
    for i in range(12,24):
        fuel_yh[2][1][i] = 10

    result, result2 = load_factors.daily_load_factors(fuel_yh)

    expected = np.zeros((8, 2))
    expected[2][0] = np.average(fuel_yh[2][0]) / np.max(fuel_yh[2][0])
    expected[2][1] = np.average(fuel_yh[2][1]) / np.max(fuel_yh[2][1])

    assert expected[2][0] == result[2][0]
    assert expected[2][1] == result[2][1]

#test_daily_load_factors()
