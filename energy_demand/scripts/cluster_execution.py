import os
import subprocess

# Import multi processing tools
from multiprocessing import Pool, cpu_count

#import any other packages 
import numpy as np

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    # Run smif
    #bash_command = "smif -v run ed_constrained_pop-baseline16_econ-c16_fuel-c16"
    #os.system(bash_command)

    all_weather_stations = True

    weather_yrs = [1961, 1962, 1963]

    weather_yr = weather_yrs[simulation_number]

    if all_weather_stations:
        weather_station_cnt = [] #All stationssimulation_number
    else:
        weather_station_cnt = simulation_number

    # Run energy demand main.py
    bash_command = "python energy_demand/energy_demand/main.py {} {}".format(weather_yr, weather_station_cnt)
    os.system(bash_command)

    return 

# WEather years
simulation_number = [1, 2] #,3,4,5,6,7,8,9,10]

if __name__ == "__main__":
    with Pool(int(cpu_count()/2)) as pool:
        pool.map(
            my_function,
            simulation_number,
            chunksize=10)

'''
for i in range(2):

    print("run " + str(i))
    print("---")

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
'''

'''
#import sh
#sh.cd('C:/Users/cenv0553/ed')

#print(sh.pwd())

#stream = os.popen("cd C:/Users/cenv0553/ed")

'''