"""This file creates a .zip folder with all the necessary data files to run HIRE
for a specific version
"""
import os
import zipfile
#from energy_demand.basic import basic_functions

def zipdir(path, zip_handler):
    """Zip a whole directory
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_handler.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file),
                    os.path.join(path, '..')))

    return zip_handler

def zipit(dir_list, zip_name):
    """Zip a list with directories
    """
    zip_handler = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dir_to_zip in dir_list:
        print("... zipping folder: {}".format(dir))
        zip_handler = zipdir(dir_to_zip, zip_handler)

    # Close zip
    zip_handler.close()

def package_data(version_name, data_folder_path):
    """
    """
    print("... start packaging data")

    # Names
    zip_name_full = os.path.join(data_folder_path, "{}_{}".format(version_name, "full.zip"))
    zip_name_minimum = os.path.join(data_folder_path, "{}_{}".format(version_name, "minimum.zip"))

    # Files to folders
    files_to_add = ['units.txt']

    # Zip minimum files
    _raw_folders_data_minimal = [
        '_raw_data_minimal',
        'coefficients',
        'initial_conditions',
        'interval_definitions',
        'interventions',
        'narratives',
        'planning',
        'region_definitions',
        'scenarios_not_extracted',
        'strategies']

    # Zip maximum files
    _raw_folders_data_full = [
        '_raw_data',
        'coefficients',
        'initial_conditions',
        'interval_definitions',
        'interventions',
        'narratives',
        'planning',
        'region_definitions',
        'scenarios_not_extracted',
        'strategies']

    paths_minimal = []
    for folder in _raw_folders_data_minimal:
        path_folder = os.path.join(data_folder_path, folder) 
        paths_minimal.append(path_folder)

    paths_full = []
    for folder in _raw_folders_data_full:
        path_folder = os.path.join(data_folder_path, folder)
        paths_full.append(path_folder)

    '''# Get all folders in data_folder_path
    #all_folders, all_files = basic_functions.get_all_folders_files(data_folder_path)

    # Folders to ignore
    folders_not_to_copy = []

    # All folders to zip
    folder_paths = []

    for folder_name in _raw_folders_data_full:
        if folder_name in folders_not_to_copy:
            pass
        else:
            folder_path = os.path.join(data_folder_path, folder_name)
            folder_paths.append(folder_path)'''
    # Zip minimal
    zipit(
        dir_list=paths_minimal,
        zip_name=zip_name_minimum)

    # Zip full
    zipit(
        dir_list=paths_full,
        zip_name=zip_name_full)

    # Append file
    zip_handler_minimum = zipfile.ZipFile(os.path.join(data_folder_path, zip_name_minimum), "a")
    zip_handler_full = zipfile.ZipFile(os.path.join(data_folder_path, zip_name_full), "a")
    
    for file_to_add in files_to_add:
        full_file_path = os.path.join(data_folder_path, 'units.txt')
        zip_handler_full.write(full_file_path, arcname=file_to_add)
        zip_handler_minimum.write(full_file_path, arcname=file_to_add)

    zip_handler_full.close()
    zip_handler_minimum.close()

    print("Finished packaging data for Version {}".format(version_name))

#if __name__ == '__main__':
print("START")
package_data(
    version_name="v_045_1_in_progress",
    data_folder_path="C:/Users/cenv0553/ed/data")
