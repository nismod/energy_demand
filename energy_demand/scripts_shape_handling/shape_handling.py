"""Functions related to load profiles
"""
import numpy as np

def eff_heat_pump(m_slope, h_diff, intersect):
    """Calculate efficiency of heat pump

    Parameters
    ----------
    m_slope : float
        Slope of heat pump
    h_diff : float
        Temperature difference
    intersect : float
        Extrapolated intersect at temp diff of 10 degree (which is treated as efficiency)

    Returns
    efficiency_hp : float
        Efficiency of heat pump

    Notes
    -----
    Because the efficieny of heat pumps is temperature dependent, the efficiency needs to
    be calculated based on slope and intersect which is provided as input for temp difference 10
    and treated as efficiency

    The intersect at temp differenc 10 is for ASHP about 6, for GSHP about 9
    """
    efficiency_hp = m_slope * h_diff + (intersect + (-1 * m_slope*10))

    return efficiency_hp

def absolute_to_relative(absolute_array):
    """Convert absolute numbers in an array to relative

    If the total sum is zero, return an array with zeros and raise a warning

    Parameters
    ----------
    absolute_array : array
        Contains absolute numbers in it

    Returns
    -------
    relative_array : array
        Contains relative numbers


    """
    # If the total sum is zero, return same array
    if np.sum(absolute_array) == 0:
        relative_array = absolute_array
        #print("Warning: The sum was zero")
    else:
        #relative_array = np.divide(1, np.sum(absolute_array)) * absolute_array
        relative_array = np.nan_to_num(np.divide(1, np.sum(absolute_array)) * absolute_array)

    #assert np.sum(absolute_array) > 0
    return relative_array

def convert_dh_yd_to_yh(shape_yd, shape_y_dh):
    """Convert yd shape and shape for every day (y_dh) into yh

    Parameters
    ----------
    shape_yd : array
        Array with yd shape
    shape_y_dh : array
        Array with y_dh shape

    Return
    ------
    shape_yh : array
        Array with yh shape
    """
    shape_yh = np.zeros((365, 24))
    for day, value_yd in enumerate(shape_yd):
        shape_yh[day] = value_yd * shape_y_dh[day]

    return shape_yh

def get_hybrid_fuel_shapes_y_dh(fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, tech_low_high_p, eff_low_tech, eff_high_tech):
    """Calculate y_dh fuel shapes for hybrid technologies for every day in a year

    Depending on the share of service each hybrid technology in every hour,
    the daily fuelshapes of each technology are taken for every hour respectively

    #TODO: IMPROVE DESCRITPION

    Parameters
    ----------
    fuel_shape_boilers_y_dh : array
        Fuel shape of low temperature technology (boiler technology)
    fuel_shape_hp_y_dh : array
        Fuel shape of high temp technology (y_dh) (heat pump technology)
    tech_low_high_p : array
        Share of service of technology in every hour (heat pump technology)
    eff_low_tech : array
        Efficiency of low temperature technology
    eff_high_tech : array
        Efficiency of high temperature technology

    Return
    ------
    fuel_shapes_hybrid_y_dh : array
        Fuel shape (y_dh) for hybrid technology

    Example
    --------
    E.g. 0-12, 16-24:   TechA
         12-16          TechA 50%, TechB 50%

    The daily shape is taken for TechA for 0-12 and weighted according to efficency
    Between 12 and Tech A and TechB are taken with 50% shares and weighted with either efficiency

    Info
    ----
    In case no fuel is provided for a day 'fuel_shapes_hybrid_y_dh' for this day is zero. Therfore
    the total sum of 'fuel_shapes_hybrid_y_dh not necessarily 365.
    """
    fuel_shapes_hybrid_y_dh = np.zeros((365, 24))

    for day in range(365):
        dh_fuel_hybrid = np.zeros(24)
        for hour in range(24):

            # Shares of each technology for every hour
            low_p = tech_low_high_p['low'][day][hour]
            high_p = tech_low_high_p['high'][day][hour]

            # Efficiencies to weight dh shape
            eff_low = eff_low_tech[day][hour]
            eff_high = eff_high_tech[day][hour]

            # Calculate fuel for every hour
            if low_p == 0:
                fuel_boiler = 0
            else:
                fuel_boiler = low_p * fuel_shape_boilers_y_dh[day][hour] #SHARK / eff_low

            if high_p == 0:
                fuel_hp = 0
            else:
                fuel_hp = high_p * fuel_shape_hp_y_dh[day][hour] #SHARK / eff_high

            '''print("****hour")
            print(low_p)
            print(high_p)
            print(eff_low)
            print(eff_high)
            print(fuel_shape_boilers_y_dh[day][hour])
            print(fuel_shape_hp_y_dh[day][hour])
            print(np.divide(low_p * fuel_shape_boilers_y_dh[day][hour], eff_low))
            print(np.divide(high_p * fuel_shape_hp_y_dh[day][hour], eff_high))
            print("iff")
            print(fuel_boiler)
            print(fuel_hp)
            '''

            # Weighted hourly dh shape with efficiencies
            dh_fuel_hybrid[hour] = fuel_boiler + fuel_hp

        # Normalise dh shape
        fuel_shapes_hybrid_y_dh[day] = absolute_to_relative(dh_fuel_hybrid)

        ########
        '''plt.plot(dh_shape_hybrid)
        plt.show()
        '''
    # Testing
    #np.testing.assert_array_almost_equal(
    # np.sum(fuel_shapes_hybrid_y_dh),
    # 365, decimal=4, err_msg='Error in shapes')

    return fuel_shapes_hybrid_y_dh
