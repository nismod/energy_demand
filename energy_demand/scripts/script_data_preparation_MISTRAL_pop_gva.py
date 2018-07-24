"""Script to add interval on GVA and population file
"""
import os
import pandas as pd
print("...start script")

path_to_folder = "C://Users//cenv0553//ED//data//scenarios//MISTRAL_pop_gva//data"

sectors_to_generate = [2,3,4,5,6,8,9,29,11,12,10,15,14,19,17,40,41,28,35,23,27]


# Get all folders with scenario run results (name of folder is scenario)
all_csv_folders = os.listdir(path_to_folder)

# ---------------------------------------------------------
# Create scenario with constant population and constant GVA
# ---------------------------------------------------------
empty_folder_name = os.path.join(path_to_folder, "constant_pop_gva")
os.makedirs(empty_folder_name)

wrote_out_pop = False
wroute_out_GVA = False
for folder_name in all_csv_folders:
    try:
        all_files = os.listdir(os.path.join(path_to_folder, folder_name))

        for file_name in all_files:
            filename_split = file_name.split("__")
            
            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv') or (
                filename_split[0] == "population" and filename_split[1] == 'lad.csv'):

                    file_path = os.path.join(path_to_folder, folder_name, file_name)
                    print("Change file: " + str(file_path))

                    # READ csv file
                    gp_file = pd.read_csv(file_path)

                    # Add new column
                    gp_file['value'] = 1000

                    # Save as file
                    file_path_out = os.path.join(empty_folder_name, file_name)
                    gp_file.to_csv(file_path_out, index=False) #Index prevents writing index rows
                    wrote_out_pop = True

            elif (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad.csv'):

                    file_path = os.path.join(path_to_folder, folder_name, file_name)
                    print("Change file: " + str(file_path))

                    # READ csv file
                    gp_file = pd.read_csv(file_path)
        
                    # Add new column
                    gp_file['value'] = 1000
                    
                    # Save as file
                    file_path_out = os.path.join(empty_folder_name, file_name)
                    gp_file.to_csv(file_path_out, index=False) #Index prevents writing index rows

                    wroute_out_GVA = True
            else:
                pass
        if wrote_out_pop == True and wroute_out_GVA == True:
            break
    except:
        pass

# -----------
# Add interval and create individual GVA data
# -----------
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

            else:
                pass
            
            # ----------------------------------------------------------
            # Script to generate different csv files per economic sector
            # ----------------------------------------------------------
            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv'):
     
                file_path = os.path.join(path_to_folder, folder_name, file_name)

                # READ csv file
                gp_file = pd.read_csv(file_path)
    
                # Iterate sector
                for sector_nr in sectors_to_generate:

                    # Create empty df
                    new_df = pd.DataFrame(columns=gp_file.columns)

                    # Select all entries where in 'economic_sector__gor' is sector
                    new_df_selection = gp_file.loc[gp_file['economic_sector__gor'] == sector_nr]

                    file_path_sector_specific = os.path.join(
                        path_to_folder, folder_name, "gva_per_head__lad_sector__{}.csv".format(sector_nr))

                    # Generate sector specific CSV
                    new_df_selection.to_csv(file_path_sector_specific, index=False) #Index prevents writing index rows

            else:
                pass
    except:
        print("no valid file")
        pass

print("----------")
print("Finished adding a row to pop and csv files with interval == 1")
print("----------")
