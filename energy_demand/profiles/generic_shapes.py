"""Flat shape definition
"""
import numpy as np
from energy_demand.profiles import load_profile
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def generic_flat_shape(shape_peak_yd_factor=1/365):
    """Create completely flat shape for peak and non-peak

    Parameters
    ---------
    shape_peak_yd_factor : float
        Factor for peak yd

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
    # linear shape_peak_dh
    shape_peak_dh = np.full((24), 1 / 24)

    # linear shape_non_peak_y_dh
    shape_non_peak_y_dh = np.zeros((365, 24))

    # Flat shape, ever hour same amount
    shape_non_peak_y_dh = np.full((365, 24), (1.0 / 24))

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((365)) / 365

    shape_non_peak_yh = np.full((365, 24), 1/8760)

    return shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh

class genericFlatEnduse(object):
    """Class for generic enduses with flat shapes

    Generate flat shapes (i.e. same amount of fuel for every hour in a year)
    """
    def __init__(self, enduse_fuel):
        self.fuel_new_y = enduse_fuel

        shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd, _ = generic_flat_shape()

        # Convert shape_peak_dh into fuel per day (Multiply average daily fuel demand for flat shape * peak factor)
        max_fuel_d = self.fuel_new_y * shape_peak_yd_factor

        # Yh fuel shape per fueltype (non-peak)
        self.fuel_yh = np.zeros((self.fuel_new_y.shape[0], 365, 24))
        for fueltype in range(len(enduse_fuel)):
            self.fuel_yh[fueltype] = (shape_non_peak_yd[:, np.newaxis] * shape_non_peak_y_dh) * self.fuel_new_y[fueltype]

        # Dh fuel shape per fueltype (peak)  (shape of peak & maximum fuel per fueltype)
        self.fuel_peak_dh = shape_peak_dh * max_fuel_d[:, np.newaxis]

        # h fuel shape per fueltype (peak)
        self.fuel_peak_h = load_profile.calk_peak_h_dh(self.fuel_peak_dh)

        self.crit_flat_profile = False
