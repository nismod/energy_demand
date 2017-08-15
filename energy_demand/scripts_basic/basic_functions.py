"""very basic functions
"""
import numpy as np

def mimick_deepcopy(input_array):
    """
    """
    copy_array = np.zeros((input_array.shape))
    for i, fuel_row in enumerate(input_array):
        copy_array[i] = fuel_row
    return copy_array

def rmse(predictions, targets):
    """RMSE calculations
    """
    return np.sqrt(((predictions - targets) ** 2).mean())