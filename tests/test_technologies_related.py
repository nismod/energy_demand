import numpy as np
from energy_demand.technologies import technologies_related

def const_eff_yh():
    """Testing function
    """
    in_value = 1
    expected = np.ones((365, 24))

    # call function
    out_value = technologies_related.const_eff_yh(in_value)

    assert out_value == expected

def get_fueltype_str():
    """Testing function
    """
    fueltypes_lu = {'gas': 100}
    in_value = 'gas'
    expected = 100

    # call function
    out_value = technologies_related.get_fueltype_str(fueltypes_lu, in_value)

    assert out_value == expected

def get_fueltype_str():
    """Testing function
    """
    fueltypes_lu = {'gas': 100}
    in_value = 100
    expected = 'gas'

    # call function
    out_value = technologies_related.get_fueltype_str(fueltypes_lu, in_value)

    assert out_value == expected

