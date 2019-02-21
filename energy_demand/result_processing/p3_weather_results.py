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
import copy

from energy_demand.read_write import data_loader
from energy_demand.technologies import tech_related
from energy_demand.basic import date_prop, basic_functions
from energy_demand import enduse_func

# Folder paths
path_out = "C:/__DATA_RESULTS_FINAL"                          # Folder to store results
path_results = "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final"

# Scenario definitions
all_scenarios = ['h_max']#, 'h_min', 'l_max', 'l_min']
fueltypes = ['electricity', 'gas', 'hydrogen']
folder_types = ['mean', 'pos_two_sigma', 'neg_two_sigma']
simulation_yrs = range(2015, 2051, 5)

# -----------------------
# Create folder structure
# -----------------------
basic_functions.create_folder(path_out)
for scenario in all_scenarios:
    basic_functions.create_folder(os.path.join(path_out, scenario))
    for fueltype in fueltypes:
        basic_functions.create_folder(os.path.join(path_out, scenario, fueltype))
        for folder_type in folder_types:
            basic_functions.create_folder(os.path.join(path_out, scenario, fueltype, folder_type))
print("Created folder structure")

# ----------------------
# Write to file
# ---------------------
for scenario in all_scenarios:
    all_realizations = os.listdir(os.path.join(path_results, scenario))
    print("...scenario {}".format(scenario), flush=True)

    for simulation_yr in simulation_yrs:

        print("     ...simulation_yr {}".format(simulation_yr), flush=True)
        # ----------------------------------
        # Container to load all realizations initially for speed up
        # ----------------------------------
        container_all_initialisations = []
        for initialization in all_realizations:

            path_sim_yr = os.path.join(
                path_results,
                scenario,
                initialization,
                "simulation_results",
                "model_run_results_txt",
                "only_fueltype_reg_8760",
                "fueltype_reg_8760__{}.npy".format(simulation_yr))
            print("       ... loading scenario: {}".format(initialization), flush=True)

            full_result = np.load(path_sim_yr)
            container_all_initialisations.append(full_result)

            # Check peak
            fueltype_int = tech_related.get_fueltype_int('electricity')
            national_hourly_demand = np.sum(full_result[fueltype_int], axis=0)
            peak_day_electricity, _ = enduse_func.get_peak_day_single_fueltype(national_hourly_demand)
            selected_hours = date_prop.convert_yearday_to_8760h_selection(peak_day_electricity)
            print("PEAK electricity: " + str(np.max(national_hourly_demand[selected_hours])))

        for fueltype_str in fueltypes:
            print("         ...fueltype {}".format(fueltype_str), flush=True)
            fueltype_int = tech_related.get_fueltype_int(fueltype_str)

            # --------
            # Calculate 
            # --------
            path_ini_file = os.path.join(path_results, scenario, all_realizations[0])
            _, _, regions = data_loader.load_ini_param(path_ini_file)
            hours = range(8760)

            df_result_final_mean = pd.DataFrame(index=hours, columns=regions)
            df_result_pos_two_sigma = pd.DataFrame(index=hours, columns=regions)
            df_result_neg_two_sigma = pd.DataFrame(index=hours, columns=regions)

            df_result_region_empty = pd.DataFrame(columns=hours)

            for region_nr, reg_name in enumerate(regions):
                #print("         ...calculating region {}".format(reg_name), flush=True)

                #df_result_region = pd.DataFrame(columns=hours)
                df_result_region = copy.copy(df_result_region_empty)

                '''for cnt, initialization in enumerate(all_realizations):

                    path_sim_yr = os.path.join(
                        path_results,
                        scenario,
                        initialization,
                        "simulation_results",
                        "model_run_results_txt",
                        "only_fueltype_reg_8760",
                        "fueltype_reg_8760__{}.npy".format(simulation_yr))

                    full_result = np.load(path_sim_yr)'''

                for cnt, full_result in enumerate(container_all_initialisations):
                    result_reg_8760 = list(full_result[fueltype_int][region_nr])

                    #Slow
                    #realisation_data = pd.DataFrame([result_reg_8760], columns=hours)
                    #df_result_region = df_result_region.append(realisation_data)

                    #Faster
                    df_result_region.loc[cnt] = result_reg_8760

                # Calculate statistics
                reg_mean = df_result_region.mean() # Calculate mean of region
                std_dev = df_result_region.mean() # Calculate mean of region
                #reg_05 = df_result_region.quantile(q=0.05) # Calculate 0.05 quantiles of region
                #reg_95 = df_result_region.quantile(q=0.95) # Calculate 0.95 quantiles of region

                # Number of sigma
                nr_of_sigma = 2
                pos_two_sigma = reg_mean + (nr_of_sigma * std_dev)
                neg_two_sigma = reg_mean - (nr_of_sigma * std_dev)

                # Store in final dataframe
                df_result_final_mean[reg_name] = reg_mean
                df_result_pos_two_sigma[reg_name] = pos_two_sigma
                df_result_neg_two_sigma[reg_name] = neg_two_sigma

                #df_result_final_05[reg_name] = reg_05
                #df_result_final_95[reg_name] = reg_95
        
            # -------------
            # Write results
            # -------------
            out_path_file_mean = os.path.join(path_out, scenario, fueltype_str, 'mean', "{}.csv".format(simulation_yr))
            out_path_file_05 = os.path.join(path_out, scenario, fueltype_str, 'pos_two_sigma', "{}.csv".format(simulation_yr))
            out_path_file_95 = os.path.join(path_out, scenario, fueltype_str, 'neg_two_sigma', "{}.csv".format(simulation_yr))

            df_result_final_mean.to_csv(out_path_file_mean)
            df_result_pos_two_sigma.to_csv(out_path_file_05)
            df_result_neg_two_sigma.to_csv(out_path_file_95)
            #df_result_final_05.to_csv(out_path_file_05)
            #df_result_final_95.to_csv(out_path_file_95)

print("--------")
print("Finished writing out simulation results")
print("--------")