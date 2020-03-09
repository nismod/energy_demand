"""Contains very basic functions
"""
import os
import shutil
import numpy as np
from pyproj import CRS, Transformer

def get_result_paths(folder_path):
    """Joins results subfolders to ``folder_path`` and returns a dict

    Arguments
    ---------
    folder_path : str
        Path of scenario run results

    Returns
    -------
    path_dict : dict
        Dict with all sub_folder paths
    """
    path_dict = {
        'data_results': folder_path,
        'data_results_model_run_pop': os.path.join(folder_path, 'model_run_pop'),
        'data_results_validation': os.path.join(folder_path, 'PDF_validation'),
        'data_results_model_run_results_txt': os.path.join(folder_path, 'model_run_results_txt'),
        'data_results_PDF': os.path.join(folder_path, 'PDF_results')}

    return path_dict

def dict_depth(dictionary):
    """Get depth of nested dict
    """
    if isinstance(dictionary, dict):
        return 1 + (max(map(dict_depth, dictionary.values())) if dictionary else 0)

    return 0

def test_if_sector(dict_to_test, fuel_as_array=False):
    """Test if a dictionary contains also sector information

    Arguments
    ---------
    dict_to_test : dict
        Dict with info to test

    Returns
    -------
    crit_sector_data : bool
        Criteria wheter nested or not

    Example
    -------
    {0: 23, 1: 3434}} --> False
    {'sector': {0: 23, 1: 3434}} --> True
    """
    get_dict_depth = dict_depth(dict_to_test)

    if fuel_as_array: # if given as array, one level less
        if get_dict_depth == 1:
            crit_sector_data = False
        elif get_dict_depth == 2:
            crit_sector_data = True
    else:
        if get_dict_depth == 2:
            crit_sector_data = False
        elif get_dict_depth == 3:
            crit_sector_data = True

    return crit_sector_data

def round_down(num, divisor):
    """Round down
    """
    return num - (num%divisor)

def get_all_folders_files(path):
    """Return all folders and file names in a list

    Input
    -----
    path : str
        Path to folder

    Returns
    --------
    all_folders : list
        All folders in a folder
    filenames : list
        All file names in a list
    """
    folders_walk = os.walk(path)
    for root, dirnames, filenames in folders_walk:
        all_folders = list(dirnames)
        #all_files = list(filenames)
        break

    return all_folders #, all_files

def assign_array_to_dict(array_in, regions):
    """Convert array to dict with same order as region list

    Input
    -----
    regions : list
        List with specific order of regions
    array_in : array
        Data array with data like the order of the region list

    Returns
    -------
    dict_out : dict
        Dictionary of array_in
    """
    dict_out = {}
    for r_idx, region in enumerate(regions):
        dict_out[region] = array_in[r_idx, 0]

    return dict_out

def get_long_lat_decimal_degrees(reg_centroids):
    """Project coordinates from shapefile to get
    decimal degrees (from OSGB_1936_British_National_Grid to
    WGS 84 projection).

    Arguments
    ---------
    reg_centroids : dict
        Centroid information read in from shapefile via smif

    Return
    -------
    reg_coord : dict
        Contains long and latidue for every region in decimal degrees

    Info
    ----
    http://spatialreference.org/ref/epsg/wgs-84/
    """
    reg_coord = {}

    crs_4326 = CRS.from_epsg(4326) # WGS 84 projection
    crs_27700 = CRS.from_epsg(27700) # OSGB_1936_British_National_Grid
    t = Transformer.from_crs(crs_27700, crs_4326)

    for centroid in reg_centroids:
        # Convert to decimal degrees
        long_dd, lat_dd = t.transform(
            centroid['geometry']['coordinates'][0],
            centroid['geometry']['coordinates'][1]
        )
        reg_coord[centroid['properties']['name']] = {}
        reg_coord[centroid['properties']['name']]['latitude'] = lat_dd
        reg_coord[centroid['properties']['name']]['longitude'] = long_dd

    return reg_coord

def rmse(predictions, actual_values):
    """Root-mean-square deviation or
    Root-mean-square-erro (RMSE) calculations

    Arguments
    ----------
    predictions : array
        Model prediction (real value)
    actual_values : array
        Moodelled value

    Returns
    -------
    rmse : array
        root-mean-square deviation

    Info
    -----

        Alternative way

        from sklearn.metrics import mean_squared_error
        from math import sqrt

        rms = sqrt(mean_squared_error(y_actual, y_predicted))
    """
    return np.sqrt(((predictions - actual_values) ** 2).mean())

def array_to_dict(result_array, regions):
    """Convert an array with regions to dict
    with region as key

    Arguments
    ---------
    result_array : array
        Results in region_array
    regions : list
        List with all regions (order is the same)

    Returns
    --------
    result_dict : dict
        reg, value
    """
    result_dict = {}
    for reg_array_nr, region in enumerate(regions):
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
    else:
        pass

def get_month_from_string(month_string):
    """Convert string month to int month with Jan == 1

    Arguments
    ----------
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

    Arguments
    ---------
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

def remove_element_from_list(input_list, element):
    """Remove element in list

    Arguments
    ---------
    input_list : list
        List with elements
    element : any
        Element to remove

    Returns
    -------
    list_new : list
        List where element is removed
    """
    list_new = []
    for i in input_list:
        if i == element:
            _ = 0
        else:
            list_new.append(i)

    return list_new
