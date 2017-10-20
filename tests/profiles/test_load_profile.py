
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
