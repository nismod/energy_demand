"""This file contains all functions to generate a flat load profile
"""
import numpy as np
from energy_demand.profiles import load_profile

def flat_shape(nr_of_days):
    """Create completely flat shape for peak and non-peak

    Arguments
    ---------
    nr_of_days : int
        Nr of modelled days

    Returns
    -------
    shape_peak_dh : array
        Dh shape for peak day
    shape_non_peak_y_dh : array
        Shape non peak dh
    shape_peak_yd_factor : float
        Factor peak yd (is only passed through)
    shape_non_peak_yd : array
        Shape yd for non peak
    """
    shape_peak_yd_factor = 1.0 / 365.0

    # linear shape_peak_dh
    shape_peak_dh = np.full((24), 1/24)

    # linear shape_non_peak_y_dh
    shape_non_peak_y_dh = np.zeros((nr_of_days, 24), dtype=float)

    # Flat shape, ever hour same amount
    shape_non_peak_y_dh = np.full((nr_of_days, 24), (1.0/24), dtype=float)

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((nr_of_days)) / nr_of_days

    shape_non_peak_yh = np.full((nr_of_days, 24), 1/(nr_of_days * 24), dtype=float)

    return shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh

class GenericFlatEnduse(object):
    """Class for generic enduses with flat shapes

    Generate flat shapes (i.e. same amount of fuel for every hour in a year)
    """
    def __init__(self, enduse_fuel, model_yeardays_nrs):
        self.fuel_new_y = enduse_fuel

        shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd, _ = flat_shape(model_yeardays_nrs)

        # Convert shape_peak_dh into fuel per day (Multiply average daily fuel demand for flat shape * peak factor)
        max_fuel_d = self.fuel_new_y * shape_peak_yd_factor

        # Yh fuel shape per fueltype (non-peak)
        self.fuel_yh = self.fuel_new_y[:,np.newaxis, np.newaxis] * (shape_non_peak_yd[:, np.newaxis] * shape_non_peak_y_dh) * (model_yeardays_nrs/365.0)

        # Dh fuel shape per fueltype (peak)  (shape of peak & maximum fuel per fueltype)
        self.fuel_peak_dh = shape_peak_dh * max_fuel_d[:, np.newaxis]

        # h fuel shape per fueltype (peak)
        self.fuel_peak_h = load_profile.calk_peak_h_dh(self.fuel_peak_dh)

        self.crit_flat_profile = False #WHY?TODO
