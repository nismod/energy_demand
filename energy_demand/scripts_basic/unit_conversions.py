"""Conversion of units
"""
import numpy as np

def convert_mw_gwh(megawatt, number_of_hours):
    """"Conversion of MW to GWh
    """
    # Convert MW to MWh
    megawatt_hour = megawatt * number_of_hours

    # Convert mwth to gwh
    gigawatthour = megawatt_hour / 1000.0

    return gigawatthour

def convert_ktoe_gwh(data_ktoe):
    """Conversion of ktoe to gwh
    TESTED_PYTEST
    Parameters
    ----------
    data_ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in GWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    data_gwh = data_ktoe * 11.6300000

    return data_gwh

def convert_ktoe_twh(data_ktoe):
    """Conversion of ktoe to TWh

    Parameters
    ----------
    data_ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in TWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    data_twh = data_ktoe * 0.01163

    return data_twh

def convert_across_all_fueltypes(fuel_dict):
    """Iterature ktoe in fueltypes and convert to GWh

    Parameters
    ----------
    fuel_dict : dict
        Dictionary with stored ktoe for different fueltypes

    Returns
    -------
    fuel_converted : dict
        Dictionary with converted energy demand in GWh
    """
    fuel_converted = {}

    for enduse, fuels in fuel_dict.items():
        nr_of_fueltypes = len(fuels)
        fuel_converted[enduse] = np.zeros((nr_of_fueltypes))

        for fueltype in range(nr_of_fueltypes):
            fuel_converted[enduse][fueltype] = convert_ktoe_gwh(fuels[fueltype])

    return fuel_converted

def convert_all_fueltypes_sector(fuel_dict):
    """Iterate fueltypes and convert ktoe to gwh

    Parameters
    ----------
    fuel_dict : array
        Fuel per fueltype
    Returns
    -------
    fuel_converted : array
        Array with converted fuel per fueltype
    """
    fuel_converted = {}

    for enduse in fuel_dict:
        fuel_converted[enduse] = {}
        for sector, fuels in fuel_dict[enduse].items():
            nr_of_fueltypes = len(fuels)
            fuel_converted[enduse][sector] = np.zeros((nr_of_fueltypes))

            for fueltype in range(nr_of_fueltypes):
                fuel_converted[enduse][sector][fueltype] = convert_ktoe_gwh(fuels[fueltype])

    return fuel_converted
