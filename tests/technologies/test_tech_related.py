import numpy as np
from energy_demand.technologies import tech_related

def test_calc_hp_eff():
    """Testing function
    """

    temp_yh = np.zeros((365, 24)) + 10

    efficiency_intersect = 10
    t_base_heating = 15.5

    # call function
    out_value = tech_related.calc_hp_eff(
        temp_yh,
        efficiency_intersect,
        t_base_heating)

    float_value = 1.0
    expected = type(float_value)
    assert type(out_value) == expected

'''def test_eff_heat_pump():
    """
    """
    t_base = 15.5
    temp_yh = np.zeros((365, 24)) + 5
    temp_diff = t_base - temp_yh

    efficiency_intersect = 6 #Efficiency of hp at temp diff of 10 degrees

    out_value = tech_related.eff_heat_pump(temp_diff, efficiency_intersect)

    values_every_h = -0.08 * temp_diff + (efficiency_intersect - (-0.8))
    expected = np.mean(temp_diff )
    assert out_value == expected'''

#test_eff_heat_pump()

def test_get_fueltype_str():
    """Testing function
    """
    fueltypes_lu = {'gas': 1}
    in_value = 1
    expected = 'gas'

    # call function
    out_value = tech_related.get_fueltype_str(fueltypes_lu, in_value)

    assert out_value == expected

def test_get_fueltype_int():
    """Testing function
    """
    fueltypes_lu = {'gas': 1}
    in_value = 'gas'
    expected = 1

    # call function
    out_value = tech_related.get_fueltype_int(fueltypes_lu, in_value)

    assert out_value == expected
