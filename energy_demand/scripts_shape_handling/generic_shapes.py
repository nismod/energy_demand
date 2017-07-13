import numpy as np

def generic_flat_shape(shape_peak_yd_factor):
    """Create flat shape #TODO: SHAPE FACTORS

    This is a completly flat profile

    """
    # linear shape_peak_dh
    shape_peak_dh = np.ones((24))
    shape_peak_dh = shape_peak_dh / 24

    # linear shape_non_peak_dh
    shape_non_peak_dh = np.zeros((365, 24))

    for i in range(365):
        shape_non_peak_dh[i] = np.ones((24)) / 24

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((365)) / 365

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd

# SIGMOID S