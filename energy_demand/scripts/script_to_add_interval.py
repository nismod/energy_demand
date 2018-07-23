"""Script to add interval on GVA and population file
"""
import os
import pandas as pd

path_to_folder = "C://Users//cenv0553//ED//data//scenarios//population-economic-smif-csv-from-nismod-db"

# Get all folders with scenario run results (name of folder is scenario)
all_csv_folders = os.listdir(path_to_folder)

for folder_name in all_csv_folders:

    try:

        all_files = os.listdir(os.path.join(path_to_folder, folder_name))
        for file_name in all_files:
            filename_split = file_name.split("__")

            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv') or (
                filename_split[0] == "population" and filename_split[1] == 'lad.csv'):

                file_path = os.path.join(path_to_folder, folder_name, file_name)

                # READ csv file
                gp_file = pd.read_csv(file_path)

                # Add new column
                gp_file['interval'] = 1

                # Save as file
                gp_file.to_csv(file_path)
    except:
        pass # no folder

