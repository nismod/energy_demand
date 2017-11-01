
"""Testing
"""
from energy_demand.profiles import load_profile
import sys
import numpy as np

def test_abs_to_rel():
    """Test
    """

    absolute_array = np.array([1,2,3])
    absolute_array2 = np.array([0,0,0])

    relative_array = load_profile.abs_to_rel(absolute_array)
    relative_array2 = load_profile.abs_to_rel(absolute_array2)

    expected_relative_array = np.array(
        [
            float(absolute_array[0]) / np.sum(absolute_array),
            float(absolute_array[1]) / np.sum(absolute_array),
            float(absolute_array[2]) / np.sum(absolute_array)
            ]
    )

    np.testing.assert_equal(np.round(relative_array,3), np.round(expected_relative_array, 3))
    np.testing.assert_equal(relative_array2, absolute_array2)

def test_calk_peak_h_dh():
    """testing
    """
    fuel_yh = np.zeros((2, 24)) #two fueltypes, 24 hours
    fuel_yh[1] = np.array([1,2,3,4,5,4,3,2,1,1,1,1,1,1,1,1,2,2,1,1,3,4,5,6])

    result = load_profile.calk_peak_h_dh(fuel_yh)

    assert result[0] == np.max(fuel_yh[0])
    assert result[1] == np.max(fuel_yh[1])

def test_LoadProfileStock():
    """testing
    """

    result = load_profile.LoadProfileStock("test_stock")

    expected = "test_stock"

    assert result.stock_name == expected

def test_LoadProfile():

    result = load_profile.LoadProfile(
        enduses=['heating'],
        unique_identifier="A123",
        shape_yd=np.zeros((365)),
        shape_yh=np.zeros((365, 24)),
        enduse_peak_yd_factor=0.7,
        shape_peak_dh=np.zeros((24)))

    assert result.enduses == ['heating']
