"""Conversion of units
"""
from collections import defaultdict
import numpy as np

def gwh_to_twh(gwh):
    """Convert GWh to TWh

    Arguments
    ---------
    gwh : float
        GWh

    Returns
    -------
    twh : str
        TWh
    """
    twh = gwh / 1000.0
    return twh

def ktoe_to_gwh(ktoe):
    """Conversion of ktoe to gwh. As ECUK input
    ktoe per year are provided, which are converted
    into GWh per year.

    Arguments
    ----------
    ktoe : float
        Energy demand in ktoe

    Returns
    -------
    gwh : float
        Energy demand in GWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    gwh = ktoe * 11.6300000

    return gwh

def gwh_to_ktoe(gwh):
    """Conversion of gwh to ktoe

    Arguments
    ----------
    ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in GWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    ktoe = gwh / 11.6300000

    return ktoe

def kwh_to_gwh(kwh):
    """"Conversion of MW to GWh

    Arguments
    ---------
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

    Arguments
    ---------
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

def ktoe_to_twh(ktoe):
    """Conversion of ktoe to TWh

    Arguments
    ----------
    ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in TWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    data_twh = ktoe * 0.01163

    return data_twh

def convert_fueltypes_ktoe_gwh(fuel_dict):
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
        fuel_converted[enduse] = np.apply_along_axis(
            func1d=ktoe_to_gwh, axis=0, arr=fuels)

    return fuel_converted

def convert_fueltypes_sectors_ktoe_gwh(fuel_dict):
    """Iterate fueltypes and convert ktoe to gwh

    Arguments
    ----------
    fuel_dict : array
        Fuel per fueltype

    Returns
    -------
    fuel_converted : dict
        Array with converted fuel per fueltype
    """
    fuel_converted = defaultdict(dict)

    for enduse in fuel_dict:
        for sector, fuels in fuel_dict[enduse].items():
            fuel_converted[enduse][sector] = np.apply_along_axis(
                func1d=ktoe_to_gwh, axis=0, arr=fuels)

    return dict(fuel_converted)
