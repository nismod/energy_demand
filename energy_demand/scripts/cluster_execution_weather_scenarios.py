import os
import subprocess
from multiprocessing import Pool, cpu_count

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    run_name = 'h_max'
    name_config_path = run_name

    run_smif = False 

    # --------------------------
    # Weather realisation
    # --------------------------
    all_weather_reations = ["NF{}".format(i) for i in range(1, 101, 1)]
    weather_realisation = all_weather_reations[simulation_number]

    path_to_ini_file = "/soge-home/staff/cenv0553/energy_demand/local_run_config_file_cluster.ini"

    # Make run name_specifiv
    run_name = "{}_{}".format(run_name, simulation_number)

    # Run energy demand main.py
    if run_smif:
        # Run smif
        #bash_command = "smif -v run ed_constrained_pop-baseline16_econ-c16_fuel-c16"
        #os.system(bash_command)
        pass
    else:
        bash_command = "python energy_demand/energy_demand/main.py {} {} {} {}".format(
            path_to_ini_file,
            run_name,
            weather_realisation,
            name_config_path)

        os.system(bash_command)
    return 

# Simulation number
simulation_number = range(0, 101, 1)

if __name__ == "__main__":
    with Pool(int(cpu_count()/2)) as pool:
        pool.map(
            my_function,
            simulation_number,
            chunksize=1)
