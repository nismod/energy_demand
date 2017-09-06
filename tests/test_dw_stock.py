"""Testing functions ``dwelling_stock`` ``dw_stock``
"""
from energy_demand.dwelling_stock import dw_stock

def test_get_scenario_driver_enduse():
    """Testing
    """
    scenario_drivers = {'heating': ['population']}
    classobject1 = dw_stock.Dwelling(
        2015,
        "UK",
        {'longitude': 10, 'latitude': 10},
        1000,
        ['heating'],
        scenario_drivers,
        population=2.2
    )
    dwellings = [classobject1, classobject1]
    dw_stock_object = dw_stock.DwellingStock('bern', dwellings, ['heating'])

    expected = 4.4

    # call function
    out_value = dw_stock_object.get_scenario_driver_enduse('population')

    assert out_value == expected

def test_dwelling():
    """Testing
    """
    scenario_drivers = {'heating': ['population']}
    classobject = dw_stock.Dwelling(
        2015,
        "UK",
        {'longitude': 10, 'latitude': 10},
        1000,
        ['heating'],
        scenario_drivers,
        population=2.2
    )

    # Driver
    expected = 2.2

    # call function
    classobject.calc_scenario_driver(scenario_drivers)

    out_value = classobject.heating

    assert out_value == expected
