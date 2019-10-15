import os
import subprocess
from multiprocessing import Pool, cpu_count

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    run_name = 'l_min' #h_min, h_max, l_max, l_min
    name_config_path = run_name

    run_smif = False 

    # --------------------------
    # Weather realisation
    # --------------------------
    all_weather_reations = ["NF{}".format(i) for i in range(1, 101, 1)]
    weather_realisation = all_weather_reations[simulation_number]

    path_to_ini_file = "C:/HIRE/energy_demand/local_run_config_file.ini"

    # Make run name_specifiv
    run_name = "{}_{}".format(run_name, simulation_number)

    # Run energy demand main.py
    if run_smif:
        # Run smif
        #bash_command = "smif -v run ed_constrained_pop-baseline16_econ-c16_fuel-c16"
        #os.system(bash_command)
        pass
    else:
        bash_command = "python C:/HIRE/energy_demand/energy_demand/main.py {} {} {} {}".format(
            path_to_ini_file,
            run_name,
            weather_realisation,
            name_config_path)

        os.system(bash_command)
    return 

# Simulation number
#simulation_number = range(0, 101, 1)
simulation_number = range(0, 3, 1)
nr_of_pools = 3 #int(cpu_count()/2)

if __name__ == "__main__":
    with Pool(nr_of_pools) as pool:
        pool.map(
            my_function,
            simulation_number,
            chunksize=1)
