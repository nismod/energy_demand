"""This file contains all functions to generate a flat load profile
"""
import numpy as np

def flat_shape(nr_of_days=365):
    """Create completely flat shape for peak and non-peak

    Arguments
    ---------
    nr_of_days : int
        Nr of modelled days

    Returns
    -------
    shape_peak_dh : array
        Dh shape for peak day
    flat_shape_y_dh : array
        Shape non peak dh
    flat_shape_yd : array
        Shape yd for non peak
    """
    flat_shape_yd = np.ones((nr_of_days), dtype="float") / nr_of_days

    flat_shape_yh = np.full((nr_of_days, 24), 1/(nr_of_days * 24), dtype="float")

    # Flat shape, ever hour same amount
    flat_shape_y_dh = np.full((nr_of_days, 24), (1.0/24), dtype="float")

    return flat_shape_yd, flat_shape_yh, flat_shape_y_dh

class GenericFlatEnduse(object):
    """Class for creating generic enduses with flat shapes,
    i.e. same amount of fuel for every hour in a year.

    Arguments
    ---------
    enduse_fuel : float
        Yearly total fuel
    """
    def __init__(self, enduse_fuel):

        _, flat_shape_yh, _ = flat_shape()

        # Yh fuel shape per fueltype (non-peak)
        self.fuel_yh = enduse_fuel[:, np.newaxis, np.newaxis] * flat_shape_yh[np.newaxis, :, :]

        self.flat_profile_crit = True
