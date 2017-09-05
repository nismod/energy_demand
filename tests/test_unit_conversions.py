import numpy as np
from energy_demand.basic import conversions

def test_conversion_ktoe_gwh():
    """Testing function
    """
    in_value = 10
    expected = in_value * 11.6300000

    # call function
    out_value = conversions.convert_ktoe_gwh(in_value)

    assert out_value == expected

def test_convert_kwh_gwh():
    """Testing function
    """
    in_value = 10
    expected = in_value *  0.000001

    # call function
    out_value = conversions.convert_kwh_gwh(in_value)

    assert out_value == expected

def test_convert_ktoe_twh():
    """Testing function
    """
    in_value = 10
    expected = in_value *  0.01163

    # call function
    out_value = conversions.convert_ktoe_twh(in_value)

    assert out_value == expected

def test_convert_mw_gwhh():
    """Testing function
    """
    megawatt_hour = 100
    number_of_hours = 1

    expected = (megawatt_hour * number_of_hours) / 1000.0

    # call function
    out_value = conversions.convert_mw_gwh(megawatt_hour, number_of_hours)

    assert out_value == expected

def test_convert_across_all_fueltypes():
    """Testing function
    """
    in_value = {'enduse': np.zeros((2))}
    in_value['enduse'][0] = 10
    in_value['enduse'][1] = 20

    expected = {'enduse': np.zeros((2))}
    expected['enduse'][0] = 10 * 11.6300000
    expected['enduse'][1] = 20 * 11.6300000

    # call function
    out_value = conversions.convert_across_all_fueltypes(in_value)

    np.testing.assert_array_almost_equal(out_value['enduse'][0], expected['enduse'][0])
    np.testing.assert_array_almost_equal(out_value['enduse'][1], expected['enduse'][1])

def test_convert_all_fueltypes_sector():
    """Testing function
    """
    in_value = {'enduse': {'sector': np.zeros((2))}}
    in_value['enduse']['sector'][0] = 10
    in_value['enduse']['sector'][1] = 20

    expected = {'enduse': {'sector': np.zeros((2))}}
    expected['enduse']['sector'][0] = 10 * 11.6300000
    expected['enduse']['sector'][1] = 20 * 11.6300000

    # call function
    out_value = conversions.convert_all_fueltypes_sector(in_value)

    np.testing.assert_array_almost_equal(out_value['enduse']['sector'][0], expected['enduse']['sector'][0])
    np.testing.assert_array_almost_equal(out_value['enduse']['sector'][1], expected['enduse']['sector'][1])
