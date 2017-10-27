"""Contains very basic functions
"""
import os
import logging
import shutil
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

def del_previous_results(path_folder, path_subfolder_keep):
    """Delete all model results from previous model run. Do not
    delete post installation setup files

    Arguments
    ---------
    path_folder : str
        Path to results of model run
    path_subfolder_keep : str
        Path of subfolder which must not be deleted
    """
    if os.path.exists(path_folder):

        all_files_and_folders = os.listdir(path_folder)

        # Iterate folders in data folders
        for entry in all_files_and_folders:
            path_subfolder = os.path.join(path_folder, entry)
            # Do not deleted post installation files
            if path_subfolder != path_subfolder_keep:
                shutil.rmtree(path_subfolder)
    else:
        logging.info("...Deleted previous scenario results")
        print("...Deleted previous scenario results")

def del_previous_setup(path_folder):
    """Delete all model results from previous model run

    Arguments
    ---------
    path : str
        Path to results of model run
    """
    if os.path.exists(path_folder):
        shutil.rmtree(path_folder)
    else:
        logging.info("...Deleted previous scenario results")
        print("...Deleted previous scenario results")
