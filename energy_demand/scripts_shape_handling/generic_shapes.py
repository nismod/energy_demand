"""Flat shape definition
"""
import numpy as np
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
    shape_non_peak_dh : array
        Shape non peak dh
    shape_peak_yd_factor : float
        Factor peak yd (is only passed through)
    shape_non_peak_yd : array
        Shape yd for non peak
    """
    # linear shape_peak_dh
    shape_peak_dh = np.full((24), 1 / 24) #np.ones((24)) / 24

    # linear shape_non_peak_dh
    shape_non_peak_dh = np.zeros((365, 24))

    # Flat shape, ever hour same amount
    shape_non_peak_dh = np.full((365, 24), (1.0 / 24))

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((365)) / 365

    shape_non_peak_yh = np.full((365, 24), 1/8760)

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh
