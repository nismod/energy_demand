"""Contains very basic functions
"""
import os
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

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str
        Name of folder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)
