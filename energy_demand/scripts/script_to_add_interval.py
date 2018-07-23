"""Script to add interval on GVA and population file
"""
import os
import pandas as pd
print("...start script")

path_to_folder = "C://Users//cenv0553//ED//data//scenarios//MISTRAL_pop_gva//data"

# Get all folders with scenario run results (name of folder is scenario)
all_csv_folders = os.listdir(path_to_folder)

for folder_name in all_csv_folders:
    print("folder name: " + str(folder_name))

    try:
        all_files = os.listdir(os.path.join(path_to_folder, folder_name))
        for file_name in all_files:
            filename_split = file_name.split("__")

            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv') or (
                filename_split[0] == "population" and filename_split[1] == 'lad.csv') or (
                    filename_split[0] == "gva_per_head" and filename_split[1] == 'lad.csv'):

                file_path = os.path.join(path_to_folder, folder_name, file_name)
                print("Change file: " + str(file_path))

                # READ csv file
                gp_file = pd.read_csv(file_path)

                # Add new column
                gp_file['interval'] = 1

                # Convert years to integer
                gp_file['year'] = gp_file['year'].astype(int)

                # Save as file
                gp_file.to_csv(file_path, index=False) #Index prevents writing index rows

                # Script to generate different csv files per economic sector
    except:
        print("no valid file")
        pass

print("----------")
print("Finished adding a row to pop and csv files with interval == 1")
print("----------")
