"""testing
"""
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
