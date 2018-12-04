"""Script to add interval on GVA and population file

Run script on 'data' folder in scenarios_not_extracted folder
"""
import os
import pandas as pd
import numpy as np
from energy_demand.basic import lookup_tables
from energy_demand.basic import basic_functions

def run(
        path_to_folder,
        path_MSOA_baseline,
        MSOA_calculations=False,
        geography_name='region'
    ):
    """
    path_to_folder : str
        Path to data folder
    path_MSOA_baseline : str
        Path to MSOA file with correct geography in csv
    """
    sectors_to_generate = [2, 3, 4, 5, 6, 8, 9, 29, 11, 12, 10, 15, 14, 19, 17, 40, 41, 28, 35, 23, 27]

    # Get all folders with scenario run results
    all_csv_folders = basic_functions.get_all_folders_files(path_to_folder)

    # Lookup of economic sectors
    LAD_MSOA_lu = lookup_tables.lad_msoa_mapping()

    base_yr = 2015
    end_yr = 2050

    # ---------------------------------------------------------------------------------------------------
    # Create scenario with CONSTANT (2015) population and CONSTANT GVA
    # ---------------------------------------------------------------------------------------------------
    '''
    empty_folder_name = os.path.join(path_to_folder, "constant_pop_gva")
    basic_functions.delete_folder(empty_folder_name)
    os.makedirs(empty_folder_name)
    wrote_out_pop, wroute_out_GVA = False, False #Do not change

    # Creat empty dataframe
    columns = ['timestep', 'sector', 'lad_uk_2016', 'value']
    
    # Get folder with standard scenario to get data for constant scenario
    for folder_name in ['pop-baseline16_econ-c16_fuel-c16']:

        all_files = os.listdir(os.path.join(path_to_folder, folder_name))

        # Scale for every year according to this distribution
        for file_name in all_files:
            filename_split = file_name.split("__")
            
            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv') or (
                filename_split[0] == "population" and filename_split[1] == 'lad.csv'):

                    file_path = os.path.join(path_to_folder, folder_name, file_name)
                    print("Change file: " + str(file_path))

                    # Read csv file
                    gp_file = pd.read_csv(file_path)

                    # Replace future pop with 2015 pop
                    gp_file_selection_2015 = gp_file.loc[gp_file['year'] == 2015] #Data of 2015

                    list_with_all_vals = []
                    for year in range(base_yr, end_yr + 1):
                        gp_file_selection_yr = gp_file_selection_2015
                        gp_file_selection_yr['year'] = year
                        list_with_all_vals += gp_file_selection_yr.values.tolist()
    
                    # Save as file
                    new_dataframe = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)
                    file_path_out = os.path.join(empty_folder_name, file_name)
                    new_dataframe.to_csv(file_path_out, index=False) #Index prevents writing index rows

                    # ---
                    # MSOA pop calculation
                    # ----
                    if MSOA_calculations:
                        if (filename_split[0] == "population" and filename_split[1] == 'lad.csv'):
                            
                            # Calculate relative pop percentage of ONS scenarios
                            msoa_principalDF = pd.read_csv(path_MSOA_baseline)

                            msoa_principalDF_selection_2015 = msoa_principalDF.loc[msoa_principalDF['year'] == 2015]
                            
                            # LADs and calculate factor per MSOA
                            factor_msoas = {}
                            for lad, msoas in LAD_MSOA_lu.items():
                                tot_pop_lad = 0
                                for msoa in msoas:
                                    tot_pop_lad += float(msoa_principalDF_selection_2015.loc[msoa_principalDF_selection_2015['region'] == msoa]['value'])
                                for msoa in msoas:
                                    pop_msoa = float(msoa_principalDF_selection_2015.loc[msoa_principalDF_selection_2015['region'] == msoa]['value'])
                                    factor_msoas[msoa] = pop_msoa / tot_pop_lad #calculate fator

                            list_with_all_vals = []

                            # READ csv file
                            gp_file = pd.read_csv(file_path)

                            pop_LADs_2015 = gp_file.loc[gp_file['year'] == 2015]

                            for index, row_lad in gp_file.iterrows():
                                lad = row_lad['region']
                                try:
                                    corresponding_msoas = LAD_MSOA_lu[lad]
                                except KeyError:
                                    # No match for northern ireland
                                    corresponding_msoas = [lad]

                                # Calculate population according to ONS 2015 #pop_LAD = row_lad['value']
                                pop_LAD_2015 = float(pop_LADs_2015.loc[gp_file['region'] == lad]['value']) #Base year pop
                                
                                for msoa_name in corresponding_msoas:
                                    try:
                                        pop_ONS_scale_factor = factor_msoas[msoa_name]
                                    except:
                                        pop_ONS_scale_factor = 1 # If not mapped
                                    
                                    pop_MSOA_ONS_scaled = pop_LAD_2015 * pop_ONS_scale_factor

                                    new_row = {
                                        'region': msoa_name,
                                        "year": row_lad['year'],
                                        "value": pop_MSOA_ONS_scaled,
                                        "interval": row_lad['interval']}

                                    list_with_all_vals.append(new_row)

                            msoaDF = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)
                            file_path_MSOA_out = os.path.join(empty_folder_name, "{}_{}.csv".format(file_name[:-4], "MSOA"))
                            msoaDF.to_csv(file_path_MSOA_out, index=False)

                    wrote_out_pop = True

            elif (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad.csv'):

                    file_path = os.path.join(path_to_folder, folder_name, file_name)
                    print("Change file: " + str(file_path))

                    gp_file = pd.read_csv(file_path)
        
                    # Add new column
                    gp_file['value'] = 1000

                    # Replace future pop with 2015 pop
                    gp_file_selection_2015 = gp_file.loc[gp_file['year'] == 2015] #Data of 2015

                    list_with_all_vals = []
                    for year in range(base_yr, end_yr + 1):
                        gp_file_selection_yr = gp_file_selection_2015
                        gp_file_selection_yr['year'] = year
                        list_with_all_vals += gp_file_selection_yr.values.tolist()

                    new_dataframe = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)

                    # Save as file
                    file_path_out = os.path.join(empty_folder_name, file_name)
                    new_dataframe.to_csv(file_path_out, index=False) #Index prevents writing index rows

                    # -----------------------------------------
                    # MSOA GVA calculations
                    # -----------------------------------------
                    if MSOA_calculations:
                        lads = list(gp_file.loc[gp_file['year'] == 2015]['region'])
                        list_with_all_vals = []

                        for lad in lads:
                            try:
                                corresponding_msoas = LAD_MSOA_lu[lad]
                            except KeyError:
                                corresponding_msoas = lad # No match for northern ireland

                            rows_msoa = gp_file.loc[gp_file['region'] == lad].values

                            for row_msoa in rows_msoa:
                                for msoa_name in corresponding_msoas:
                                    #row_msoa[0] = msoa_name
                                    new_row = {
                                        "region": msoa_name,
                                        "year": row_msoa[1],
                                        "value": row_msoa[2],
                                        "interval": row_msoa[3]}
                                    list_with_all_vals.append(new_row)
                                    #msoaDF = msoaDF.append(new_row, ignore_index=True)
                        # Convert list to dataframe
                        msoaDF = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)
                        file_path_MSOA_out = os.path.join(empty_folder_name, "{}_{}.csv".format(file_name[:-4], "MSOA"))
                        msoaDF.to_csv(file_path_MSOA_out, index=False)

                    wroute_out_GVA = True
            else:
                pass
        if wrote_out_pop == True and wroute_out_GVA == True:
            break

    print("... finished generating CONSTANT scenario")'''
    # ---------------------------------------------------------------------------------------------------
    # Add interval and create individual GVA data for selected sectors
    # ---------------------------------------------------------------------------------------------------
    columns = ['timestep', 'sector', geography_name, 'value']

    # Get all folders with scenario run results (name of folder is scenario)
    all_csv_folders_walk = os.walk(path_to_folder)
    for root, dirnames, filenames in all_csv_folders_walk:
        all_csv_folders = dirnames
        break

    for folder_name in all_csv_folders:
        print("folder name: " + str(folder_name), flush=True)
        all_files = os.listdir(os.path.join(path_to_folder, folder_name))

        for file_name in all_files:
            filename_split = file_name.split("__")

            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv') or (
                filename_split[0] == "population" and filename_split[1] == 'lad.csv') or (
                    filename_split[0] == "gva_per_head" and filename_split[1] == 'lad.csv'):

                file_path = os.path.join(path_to_folder, folder_name, file_name)
                gp_file = pd.read_csv(file_path)

                gp_file['year'] = gp_file['year'].astype(int)

                # Drop all rows with alls NaN entries
                gp_file = gp_file[np.isfinite(gp_file['value'])]

                # Select all entries with matching years
                gp_file = gp_file.loc[gp_file['year'].isin(range(base_yr, end_yr + 1))]

                # Rename columns
                gp_file = gp_file.rename(index=str, columns={"year": "timestep"})
                ##gp_file = gp_file.rename(index=str, columns={"region": geography_name})

                gp_file.to_csv(file_path, index=False)
    
                # ---  
                # MSOA pop calculation
                # ----
                if MSOA_calculations:
                    if (filename_split[0] == "population" and filename_split[1] == 'lad.csv'):
                        
                        # Calculate relative pop percentage of ONS scenarios
                        msoa_principalDF = pd.read_csv(path_MSOA_baseline)
                        msoa_principalDF_selection_2015 = msoa_principalDF.loc[msoa_principalDF['year'] == 2015]
                        
                        # LADs and calculate factor per MSOA
                        factor_msoas = {}
                        for lad, msoas in LAD_MSOA_lu.items():
                            tot_pop_lad = 0
                            for msoa in msoas:
                                tot_pop_lad += float(msoa_principalDF_selection_2015.loc[msoa_principalDF_selection_2015['region'] == msoa]['value'])
                            for msoa in msoas:
                                pop_msoa = float(msoa_principalDF_selection_2015.loc[msoa_principalDF_selection_2015['region'] == msoa]['value'])
                                factor_msoas[msoa] = pop_msoa / tot_pop_lad #calculate fator

                        list_with_all_vals = []
                        gp_file = pd.read_csv(file_path)

                        for index, row_lad in gp_file.iterrows():
                            lad = row_lad['region']
                            try:
                                corresponding_msoas = LAD_MSOA_lu[lad]
                            except KeyError:
                                corresponding_msoas = [lad] # No match for northern ireland

                            # Calculate population according to ONS 2015
                            pop_LAD = row_lad['value']

                            for msoa_name in corresponding_msoas:
                                try:
                                    pop_ONS_scale_factor = factor_msoas[msoa_name]
                                except:
                                    pop_ONS_scale_factor = 1 # If not mapped
                                
                                pop_MSOA_ONS_scaled = pop_LAD * pop_ONS_scale_factor

                                new_row = {
                                    'region': msoa_name,
                                    "timestep": row_lad['year'],
                                    "value": pop_MSOA_ONS_scaled}

                                list_with_all_vals.append(new_row)

                        msoaDF = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)
                        file_path_MSOA_out = os.path.join(path_to_folder, folder_name, "{}_{}.csv".format(file_name[:-4], "MSOA"))
                        msoaDF.to_csv(file_path_MSOA_out, index=False)
            else:
                pass

            # ----------------------------------------------------------
            # Script to generate sectors file
            # ----------------------------------------------------------
            if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad_sector.csv'):
                
                file_path = os.path.join(path_to_folder, folder_name, file_name)
                df = pd.read_csv(file_path)

                df = df.rename(
                    index=str,
                    columns={
                        "year": "timestep",
                        "economic_sector__gor": "sector"})

                # Drop columns
                try:
                    df = df.drop('interval', 1)
                except:
                    pass

                # Select all entries with matching sectors
                df = df.loc[df['sector'].isin(sectors_to_generate)]

                # Select all entries with matching years
                df = df.loc[df['timestep'].isin(range(base_yr, end_yr + 1))]

                # Reorder columns
                df = df[columns]

                # Write to csv
                file_path_sectors = os.path.join(path_to_folder, folder_name, "gva_per_head__lad_sectors.csv")
                df.to_csv(file_path_sectors, index=False)

            # -----------------------------------------
            # MSOA GVA calculations
            # -----------------------------------------
            if MSOA_calculations:
                if (filename_split[0] == "gva_per_head" and filename_split[1] == 'lad.csv'):
                    
                    list_with_all_vals = []

                    file_path = os.path.join(path_to_folder, folder_name, file_name)
                    lads = list(gp_file.loc[gp_file['year'] == 2015]['region'])

                    for lad in lads:
                        try:
                            corresponding_msoas = LAD_MSOA_lu[lad]
                        except KeyError:
                            # No match for northern ireland
                            corresponding_msoas = [lad]

                        rows_msoa = gp_file.loc[gp_file['region'] == lad]

                        for index, row_msoa in rows_msoa.iterrows():
                            for msoa_name in corresponding_msoas:
                                new_row = {
                                    "region": msoa_name,
                                    "timestep": row_msoa['year'],
                                    "value": row_msoa['value']}
                                list_with_all_vals.append(new_row)

                    # Convert list to dataframe
                    msoaDF = pd.DataFrame(list_with_all_vals, columns=gp_file.columns)

                    msoaDF = msoaDF.rename(index=str, columns={"region": geography_name})

                    file_path_MSOA_out = os.path.join(path_to_folder, folder_name, "{}_{}.csv".format(file_name[:-4], "MSOA"))
                    msoaDF.to_csv(file_path_MSOA_out, index=False)

    print("----------")
    print("Finished preparing NISMOD GVA and population files")
    print("----------")
