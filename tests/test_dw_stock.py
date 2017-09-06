"""Testing functions ``dwelling_stock`` ``dw_stock``
"""
from energy_demand.dwelling_stock import dw_stock

'''def test_get_scenario_driver_enduse():
    """Testing
    """

    classobject = DwellingStock()
    
    expected
    # call function
    out_value = classobject.get_scenario_driver_enduse('heating')

    assert out_value == expected
'''

def test_dwelling():
    """Testing
    """
    classobject = dw_stock.Dwelling(
        2015,
        "UK",
        {'long': 10, 'lat': 10},
        1000,
        ['heating'],
        {'heating': 2.2}
    )

    # Driver
    expected = 2.2

    # call function
    out_object = classobject.calc_scenario_driver('heating')
    out_value = out_object.heating

    assert out_value == expected
