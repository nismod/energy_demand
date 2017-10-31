"""
"""
from energy_demand.geography import weather_region
import numpy as np

def test_get_shape_peak_yd_factor():

    demand_yd = np.zeros((365))
    for day in range(365):
        demand_yd[day] = np.random.randint(0, 30)

    result = weather_region.get_shape_peak_yd_factor(
        demand_yd)

    expected = (1 / np.sum(demand_yd)) * np.max(demand_yd)

    assert result == expected

test_get_shape_peak_yd_factor()