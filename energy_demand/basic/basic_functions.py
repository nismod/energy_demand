"""Contains very basic functions
"""
import numpy as np

def rmse(predictions, targets):
    """RMSE calculations

    Arguments
    ----------
    predictions : any
        Model prediction (real value)
    targets : any
        Moodelled value
    """
    return np.sqrt(((predictions - targets) ** 2).mean())
