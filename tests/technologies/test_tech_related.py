import numpy as np
from energy_demand.technologies import tech_related

def const_eff_yh():
    """Testing function
    """
    in_value = 1
    expected = np.ones((365, 24), dtype=float)

    # call function
    out_value = tech_related.const_eff_yh(in_value)

    assert out_value == expected

def get_fueltype_str():
    """Testing function
    """
    fueltypes_lu = {'gas': 100}
    in_value = 'gas'
    expected = 100

    # call function
    out_value = tech_related.get_fueltype_str(fueltypes_lu, in_value)

    assert out_value == expected

def get_fueltype_int():
    """Testing function
    """
    fueltypes_lu = {'gas': 100}
    in_value = 100
    expected = 'gas'

    # call function
    out_value = tech_related.get_fueltype_int(fueltypes_lu, in_value)

    assert out_value == expected
