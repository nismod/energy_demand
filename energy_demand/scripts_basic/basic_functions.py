"""very basic functions
"""
import numpy as np

def rmse(predictions, targets):
    """RMSE calculations
    """
    return np.sqrt(((predictions - targets) ** 2).mean())
