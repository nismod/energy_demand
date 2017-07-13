"""generate generic load profile
"""
import numpy as np

def generic_flat_shape():
    """Create flat shape #TODO: SHAPE FACTORS
    """
    # linear shape_peak_dh
    shape_peak_dh = np.ones((24))
    shape_peak_dh = shape_peak_dh / 24

    # linear shape_non_peak_dh
    shape_non_peak_dh = np.zeros((365, 24))

    for i in range(365):
        shape_non_peak_dh[i] = np.ones((24)) / 24

    # shape_peak_yd_factor
    shape_peak_yd_factor = 1.2

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((365)) / 365

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd


'''#
def generic_flat_shape():
    
    # linear shape_peak_dh
    shape_peak_dh = np.ones((24))
    shape_peak_dh = shape_peak_dh / 24

    # linear shape_non_peak_dh = np.zeros((365, 24))
    shape_non_peak_dh = np.zeros((365, 24))

    for i in shape_non_peak_dh:
        i = np.ones((24)) / 24

    # shape_peak_yd_factor
    shape_peak_yd_factor = 1.2

    # linear shape_non_peak_yd
    shape_non_peak_yd = np.ones((365)) / 365

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd


import numpy as np
from scipy.optimize import leastsq
import pylab as plt

# INput parameters
time_max = 14
time_min = 5

load_factor = 2

max_value = 10
min_value = 5

# Create linear approx
#data = [0.8,0.2]


def sin_function(x, A, w, t, phase):
    y = A * np.sin(w * t + phase)
    return y

N = 24 # number of data points
t = np.linspace(
    0,
    2*np.pi,
    N)

data = 1.0 * np.sin(t)


guess_mean = np.mean(data)
guess_std = 3*np.std(data)/(2**0.5)
guess_phase = 0

data_own = []
for i in range(24):
    data_own.append(
        sing(i, 2, 2 )
    )


data_first_guess = guess_std*np.sin(t+guess_phase) + guess_mean

# Define the function to optimize, in this case, we want to minimize the difference
# between the actual data and our "guessed" parameters
#optimize_func = lambda x: x[0]*np.sin(t+x[1]) + x[2] - data

#est_std, est_phase, est_mean = leastsq(optimize_func, [guess_std, guess_phase, guess_mean])[0]

# recreate the fitted curve using the optimized parameters
#data_fit = est_std  *np.sin(t + est_phase) + est_mean

plt.plot(data, '.')

plt.plot(data_own, label='first data_own')
#plt.plot(data_fit, label='after fitting')
#plt.plot(data_first_guess, label='first guess')
plt.legend()
plt.show()
'''