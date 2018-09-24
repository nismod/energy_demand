"""This file creates a .zip folder with all the necessary data files to run HIRE
for a specific version
"""
import os
import sys
import zipfile
from energy_demand.basic import basic_functions

def zipdir(path, zip_handler):
    """Zip a whole directory
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_handler.write(
                filename=os.path.join(root, file),
                arcname=os.path.relpath(
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

def package_data(
        version_name,
        data_folder_path#="C:/Users/cenv0553/ed/data"
    ):
    """
    verions_name : str
        Name of version
    data_folder_path : str
        Path to store packaged data
    """
    print("... start packaging data version: {}".format(version_name), flush=True)

    # Delete all processes files
    path_folder = os.path.join(data_folder_path, "scenarios", "MISTRAL_pop_gva")
    basic_functions.delete_folder(path_folder)

    # Names
    zip_name_full = os.path.join(data_folder_path, "{}_{}".format(version_name, "full.zip"))
    zip_name_minimum = os.path.join(data_folder_path, "{}_{}".format(version_name, "minimum.zip"))

    # Files to folders
    files_to_add = [
        'units.txt',
        'population-economic-smif-csv-from-nismod-db.zip',
        'population-economic-tables-nismod-db.zip']

    # Zip minimum files
    _raw_folders_data_minimal = [
        'coefficients',
        'initial_conditions',
        'interval_definitions',
        'interventions',
        'narratives',
        'planning',
        'region_definitions',
        'scenarios',
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
        'scenarios',
        'strategies']

    paths_minimal = []
    for folder in _raw_folders_data_minimal:
        path_folder = os.path.join(data_folder_path, folder)
        paths_minimal.append(path_folder)

    paths_full = []
    for folder in _raw_folders_data_full:
        path_folder = os.path.join(data_folder_path, folder)
        paths_full.append(path_folder)

    # Zip minimal
    zipit(
        dir_list=paths_minimal,
        zip_name=zip_name_minimum)

    # Add renamed folder
    folder_to_add = os.path.join(data_folder_path, '_raw_data_minimal')
    renamed_folder = '_raw_data'

    zip_handler_minimum = zipfile.ZipFile(os.path.join(data_folder_path, zip_name_minimum), "a")

    for root, dirs, files in os.walk(folder_to_add):
        for file in files:

            # New path
            inter_folderes = root.split("_raw_data_minimal\\")
            new_path = os.path.join(renamed_folder, inter_folderes[1], file)

            zip_handler_minimum.write(
                filename=os.path.join(root, file),
                arcname=new_path)

    # Close zip
    zip_handler_minimum.close()

    # Zip full
    zipit(
        dir_list=paths_full,
        zip_name=zip_name_full)

    # ------------
    # Append individual files
    # ------------
    zip_handler_minimum = zipfile.ZipFile(os.path.join(data_folder_path, zip_name_minimum), "a")
    zip_handler_full = zipfile.ZipFile(os.path.join(data_folder_path, zip_name_full), "a")

    for file_to_add in files_to_add:
        full_file_path = os.path.join(data_folder_path, 'units.txt')
        zip_handler_full.write(full_file_path, arcname=file_to_add)
        zip_handler_minimum.write(full_file_path, arcname=file_to_add)

    zip_handler_full.close()
    zip_handler_minimum.close()

    print("Finished packaging data for Version {}".format(version_name))


if __name__ == '__main__':
    """Provide version name and path to data folder

    E.g.:

    python ../generate_data_version.py v_6_1 C:/path_to_data
    """
    # Map command line arguments to function arguments.
    package_data(*sys.argv[1:])
