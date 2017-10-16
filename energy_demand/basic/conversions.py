"""Conversion of units
"""
from collections import defaultdict
import numpy as np

def ktoe_to_gwh(data_ktoe):
    """Conversion of ktoe to gwh

    Arguments
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

def kwh_to_gwh(kwh):
    """"Conversion of MW to GWh

    Input
    -----
    kwh : float
        Kilowatthours

    Return
    ------
    gwh : float
        Gigawatthours
    """
    gwh = kwh * 0.000001

    return gwh

def mw_to_gwh(megawatt, number_of_hours):
    """"Conversion of MW to GWh

    Input
    -----
    kwh : float
        Kilowatthours
    number_of_hours : float
        Number of hours

    Return
    ------
    gwh : float
        Gigawatthours

    """
    # Convert MW to MWh
    megawatt_hour = megawatt * number_of_hours

    # Convert mwth to gwh
    gigawatthour = megawatt_hour / 1000.0

    return gigawatthour

def ktoe_to_twh(data_ktoe):
    """Conversion of ktoe to TWh

    Arguments
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

def convert_fueltypes(fuel_dict):
    """Iterature ktoe in fueltypes and convert to GWh

    Arguments
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

        # apply converting function along row
        fuel_converted[enduse] = np.apply_along_axis(func1d=ktoe_to_gwh, axis=0, arr=fuels)

    return fuel_converted

def convert_fueltypes_sectors(fuel_dict):
    """Iterate fueltypes and convert ktoe to gwh

    Arguments
    ----------
    fuel_dict : array
        Fuel per fueltype

    Returns
    -------
    fuel_converted : array
        Array with converted fuel per fueltype
    """
    fuel_converted = defaultdict(dict)

    for enduse in fuel_dict:
        for sector, fuels in fuel_dict[enduse].items():
            fuel_converted[enduse][sector] = np.apply_along_axis(
                func1d=ktoe_to_gwh, axis=0, arr=fuels)

    return fuel_converted
