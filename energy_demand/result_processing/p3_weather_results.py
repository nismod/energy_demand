"""Generate results for paper 3


Collect model run and create folder with follwing structure:

scenario / fueltype /       type           /   year.csv
                        average,p_05,           contains 8760 h
                
                


data.csv

                region_a    region_b    ...

    hour0
    hour1    
    ...
"""
import os
import numpy as np
import pandas as pd

from energy_demand.read_write import data_loader
from energy_demand.technologies import tech_related
from energy_demand.basic import basic_functions

# Folder paths
folder_to_create = "C:/__TEST"
path_results = "C:/Users/cenv0553/ED/results"

# Scenario definitions
scenarios = ['l_min', 'l_max', 'h_min', 'h_max']
fueltypes = ['electricity', 'gas', 'hydrogen']
folder_types = ['mean', 'quantile_05', 'quantile_95']
simulation_yrs = [2015, 2041]

# -----------------------
# Create folder structure
# -----------------------
basic_functions.create_folder(folder_to_create)
for scenario in scenarios:
    basic_functions.create_folder(os.path.join(folder_to_create, scenario))
    for fueltype in fueltypes:
        basic_functions.create_folder(os.path.join(folder_to_create, scenario, fueltype))
        for folder_type in folder_types:
            basic_functions.create_folder(os.path.join(folder_to_create, scenario, fueltype, folder_type))
print("Created folder")

# ----------------------
# Write to file
# ---------------------
all_scenarios = os.listdir(path_results)

for scenario in all_scenarios:
    print("... writing scenario {}".format(scenario), flush=True)

    # Over fueltype
    for fueltype_str in fueltypes:
        print("    ... writing fueltype {}".format(fueltype_str), flush=True)

        fueltype_int = tech_related.get_fueltype_int(fueltype_str)

        # Over years
        for simulation_yr in simulation_yrs:
            print("         ...writing simulation_yr {}".format(simulation_yr), flush=True)

            # --------
            # Calculate 
            # --------
            all_realizations = os.listdir(os.path.join(path_results, scenario))

            # Initialise dataframe
            path_ini_file = os.path.join(path_results, scenario, all_realizations[0])
            _, _, regions = data_loader.load_ini_param(path_ini_file)
            hours = range(8760)

            df_result_final_mean = pd.DataFrame(index=hours, columns=regions)
            df_result_final_05 = pd.DataFrame(index=hours, columns=regions)
            df_result_final_95 = pd.DataFrame(index=hours, columns=regions)

            df_result_region = pd.DataFrame()
            for region_nr, reg_name in enumerate(regions):
                print("         ...calculating region {}".format(reg_name), flush=True)

                for initialization in all_realizations:
                    path_results_fuel_8760 = os.path.join(path_results, scenario, initialization,
                        "simulation_results", "model_run_results_txt", "only_fueltype_reg_8760")

                    path_sim_yr = os.path.join(path_results_fuel_8760, "fueltype_reg_8760__{}.npy".format(simulation_yr))
                    full_result = np.load(path_sim_yr)

                    result_reg_8760 = list(full_result[fueltype_int][region_nr])
                    realisation_data = pd.DataFrame([result_reg_8760], columns=hours)
                    df_result_region = df_result_region.append(realisation_data)

                # Calculate statistics
                reg_mean = df_result_region.mean() # Calculate mean of region
                reg_05 = df_result_region.quantile(q=0.05) # Calculate 0.05 quantiles of region
                reg_95 = df_result_region.quantile(q=0.95) # Calculate 0.95 quantiles of region

                # Write out
                df_result_final_mean[reg_name] = reg_mean
                df_result_final_05[reg_name] = reg_05
                df_result_final_95[reg_name] = reg_95
        
            # -------------
            # Write results
            # -------------
            out_path_file_mean = os.path.join(path_results, scenario, fueltype_str, 'mean', "{}.csv".format(simulation_yr))
            out_path_file_05 = os.path.join(path_results, scenario, fueltype_str, 'quantile_05', "{}.csv".format(simulation_yr))
            out_path_file_95 = os.path.join(path_results, scenario, fueltype_str, 'quantile_95', "{}.csv".format(simulation_yr))

            df_result_final_mean.to_csv(out_path_file_mean)
            df_result_final_05.to_csv(out_path_file_05)
            df_result_final_95.to_csv(out_path_file_95)

print("--------")
print("Finished writing out simulation results")
print("--------")