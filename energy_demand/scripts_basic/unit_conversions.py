"""Conversion of units
"""
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
    data_gwh = data_ktoe * 0.0116300000
    return data_gwh
