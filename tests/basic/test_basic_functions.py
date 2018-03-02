"""testing
"""
import numpy as np
from energy_demand.basic import basic_functions

def test_get_month_from_string():
    """Testing
    """
    assert basic_functions.get_month_from_string("Jan") == 1
    assert basic_functions.get_month_from_string("Feb") == 2
    assert basic_functions.get_month_from_string("Mar") == 3
    assert basic_functions.get_month_from_string("Apr") == 4
    assert basic_functions.get_month_from_string("May") == 5
    assert basic_functions.get_month_from_string("Jun") == 6
    assert basic_functions.get_month_from_string("Jul") == 7
    assert basic_functions.get_month_from_string("Aug") == 8
    assert basic_functions.get_month_from_string("Sep") == 9
    assert basic_functions.get_month_from_string("Oct") == 10
    assert basic_functions.get_month_from_string("Nov") == 11
    assert basic_functions.get_month_from_string("Dec") == 12

def test_array_to_dict():
    """Testing
    """
    result_array = np.ones((3)) + 2
    result_array[2] = 44

    regions = ["A", "B", "C"]
    result = basic_functions.array_to_dict(result_array, regions)

    expected = {"A": 3, "B": 3, "C": 44}
    assert result == expected
