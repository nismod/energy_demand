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
    predictions : array
        Model prediction (real value)
    targets : array
        Moodelled value
    """
    return np.sqrt(((predictions - targets) ** 2).mean())

def array_to_dict(result_array, lu_reg):
    """Convert an array with regions to dict
    with region as key

    Arguments
    ---------
    result_array : array
        Results in region_array
    lu_reg : list
        List with all regions (order is the same)

    Returns
    --------
    result_dict : dict
        reg, value
    """
    result_dict = {}
    for reg_array_nr, region in enumerate(lu_reg):
        result_dict[region] = result_array[reg_array_nr]

    return result_dict

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)

def delete_folder(path_folder):
    """Delete folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if os.path.exists(path_folder):
        shutil.rmtree(path_folder)

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
        logging.info("... deleted previous scenario results")
    else:
        pass

def del_previous_setup(path_folder):
    """Delete all model results from previous model run

    Arguments
    ---------
    path_folder : str
        Path to results of model run
    """
    if os.path.exists(path_folder):
        shutil.rmtree(path_folder, ignore_errors=True)
        logging.info("... deleted previous scenario results")
    else:
        pass

def del_file(path_file):
    """Delete all model results from previous model run

    Arguments
    ---------
    path_folder : str
        Path to results of model run
    """
    if os.path.isfile(path_file):
        os.remove(path_file)
        logging.info("... deleted previous scenario results")
    else:
        pass

def get_month_from_string(month_string):
    """Convert string month to int month with Jan == 1

    Argument
    --------
    month_string : str
        Month given as a string

    Returns
    --------
    month : int
        Month as an integer (jan = 1, dez = 12)
    """
    if month_string == 'Jan':
        month = 1
    elif month_string == 'Feb':
        month = 2
    elif month_string == 'Mar':
        month = 3
    elif month_string == 'Apr':
        month = 4
    elif month_string == 'May':
        month = 5
    elif month_string == 'Jun':
        month = 6
    elif month_string == 'Jul':
        month = 7
    elif month_string == 'Aug':
        month = 8
    elif month_string == 'Sep':
        month = 9
    elif month_string == 'Oct':
        month = 10
    elif month_string == 'Nov':
        month = 11
    elif month_string == 'Dec':
        month = 12

    return int(month)

def get_month_from_int(month_int):
    """Convert inger month to string month with Jan == 1

    Argument
    --------
    month_int : str
        Month given as a integer

    Returns
    --------
    month : int
        Month as an integer (jan = 1, dez = 12)
    """
    if month_int == 1:
        month_str = 'Jan'
    elif month_int == 2:
        month_str = 'Feb'
    elif month_int == 3:
        month_str = 'Mar'
    elif month_int == 4:
        month_str = 'Apr'
    elif month_int == 5:
        month_str = 'May'
    elif month_int == 6:
        month_str = 'Jun'
    elif month_int == 7:
        month_str = 'Jul'
    elif month_int == 8:
        month_str = 'Aug'
    elif month_int == 9:
        month_str = 'Sep'
    elif month_int == 10:
        month_str = 'Oct'
    elif month_int == 11:
        month_str = 'Nov'
    elif month_int == 12:
        month_str = 'Dec'

    return str(month_str)
