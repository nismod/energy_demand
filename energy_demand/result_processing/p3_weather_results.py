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
import numpy as np

from energy_demand.basic import basic_functions

# 
folder_to_create = "C:/TEST"

basic_functions.create_folder(folder_to_create)

# Iterate scenario results
a = np.load("C:/_WEATHER_p3/h_max/h_max_1_result_local_Tue_Jan_15_20_40_47_2019/simulation_results/model_run_results_txt/only_total/tot_fueltype_reg__2015__.npy")
print("a")
print(a)
