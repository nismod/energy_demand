import os
import subprocess
from multiprocessing import Pool, cpu_count
import numpy as np

from energy_demand.read_write import read_weather_data

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    run_name = '_low'
    all_weather_stations = False

    same_weather_yr = True
    defined_weather_yr = 2015

    run_smif = False 

    # --------------------------
    # Get all weather yrs with data (maybe read existing years from data folder)
    # and select weather yr
    # --------------------------
    path_to_weather_data = "/soge-home/staff/cenv0553/data/_raw_data/A-temperature_data/cleaned_weather_stations_data"
    weather_yrs_stations = read_weather_data.get_all_station_per_weather_yr(path_to_weather_data, min_nr_of_stations=30)
    weather_yrs = list(weather_yrs_stations.keys())
    print("all weather yrs:         " + str(weather_yrs))
    print("Total nr of stations:    " + str(len(weather_yrs)))

    if same_weather_yr:
        weather_yr = defined_weather_yr
    else:
        weather_yr = weather_yrs[simulation_number]

    # --------------------------
    # Select weather station
    # --------------------------
    if all_weather_stations:
        weather_station_cnt = [] #All stationssimulation_number
    else:
        weather_station_cnt = simulation_number

    # Make run name_specifiv
    run_name = "{}_{}".format(run_name, simulation_number)

    # Run energy demand main.py
    if run_smif:
        # Run smif
        #bash_command = "smif -v run ed_constrained_pop-baseline16_econ-c16_fuel-c16"
        #os.system(bash_command)
        pass
    else:
        bash_command = "python energy_demand/energy_demand/main.py {} {} {}".format(run_name, weather_yr, weather_station_cnt)
        os.system(bash_command)
    return 

# WEather years
simulation_number = range(10)

if __name__ == "__main__":
    with Pool(int(cpu_count()/2)) as pool:
        pool.map(
            my_function,
            simulation_number,
            chunksize=1)

'''
for i in range(2):

    print("run " + str(i))

    # Activate virtual environement
    bashCommand = "activate ed"
    os.system(bashCommand)

    # Run smif
    bashCommand = "smif -v run ed_constrained_pop-baseline16_econ-c16_fuel-c16"
    os.system(bashCommand)

    #process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
'''
'''
#import this
from multiprocessing import Pool, cpu_count

#import any other packages 
import numpy as np


def         my_function(simulation_number):  
print('simulation_number')
                return 


simulation_list = [1,2,3,4,5,6,7,8,9,10]

if __name__ == "__main__":
    with Pool(int(cpu_count()/2)) as pool:
         pool.map(my_function,simulation_list,chunksize=1)
#import sh
#sh.cd('C:/Users/cenv0553/ed')

#print(sh.pwd())

#stream = os.popen("cd C:/Users/cenv0553/ed")
'''