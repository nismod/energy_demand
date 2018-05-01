import numpy as np
from energy_demand.basic import conversions

def test_conversion_ktoe_gwh():
    """Testing function
    """
    in_value = 10
    expected = in_value * 11.6300000

    # call function
    out_value = conversions.ktoe_to_gwh(in_value)

    assert out_value == expected

def test_kwh_to_gwh():
    """Testing function
    """
    in_value = 10
    expected = in_value *  0.000001

    # call function
    out_value = conversions.kwh_to_gwh(in_value)

    assert out_value == expected

def test_ktoe_to_twh():
    """Testing function
    """
    in_value = 10
    expected = in_value *  0.01163

    # call function
    out_value = conversions.ktoe_to_twh(in_value)

    assert out_value == expected

def test_mw_to_gwhh():
    """Testing function
    """
    megawatt_hour = 100
    number_of_hours = 1

    expected = (megawatt_hour * number_of_hours) / 1000.0

    # call function
    out_value = conversions.mw_to_gwh(megawatt_hour, number_of_hours)

    assert out_value == expected

def test_convert_fueltypes_ktoe_GWh():
    """Testing function
    """
    in_value = {'enduse': np.zeros((2))}
    in_value['enduse'][0] = 10
    in_value['enduse'][1] = 20

    expected = {'enduse': np.zeros((2))}
    expected['enduse'][0] = 10 * 11.6300000
    expected['enduse'][1] = 20 * 11.6300000

    # call function
    out_value = conversions.convert_fueltypes_ktoe_gwh(in_value)

    np.testing.assert_array_almost_equal(out_value['enduse'][0], expected['enduse'][0])
    np.testing.assert_array_almost_equal(out_value['enduse'][1], expected['enduse'][1])

def test_convert_fueltypes_sectors_ktoe_gwh():
    """Testing function
    """
    in_value = {'enduse': {'sector': np.zeros((2))}}
    in_value['enduse']['sector'][0] = 10
    in_value['enduse']['sector'][1] = 20

    expected = {'enduse': {'sector': np.zeros((2))}}
    expected['enduse']['sector'][0] = 10 * 11.6300000
    expected['enduse']['sector'][1] = 20 * 11.6300000

    # call function
    out_value = conversions.convert_fueltypes_sectors_ktoe_gwh(in_value)

    np.testing.assert_array_almost_equal(out_value['enduse']['sector'][0], expected['enduse']['sector'][0])
    np.testing.assert_array_almost_equal(out_value['enduse']['sector'][1], expected['enduse']['sector'][1])
