import os
import subprocess
from multiprocessing import Pool, cpu_count
import numpy as np
from energy_demand.read_write import read_weather_data

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    # Run smif
    run_commands = [
        "smif run energy_demand_constrained_A",
        "smif run energy_demand_constrained_A_dm_water",
        "smif run energy_demand_constrained_A_dm_water_space",

        "smif run energy_demand_constrained_B",
        "smif run energy_demand_constrained_B_dm_water",
        "smif run energy_demand_constrained_B_dm_water_space",

        "smif run energy_demand_constrained_C",
        "smif run energy_demand_constrained_C_dm_water",
        "smif run energy_demand_constrained_C_dm_water_space",

        "smif run energy_demand_constrained_D",
        "smif run energy_demand_constrained_D_dm_water",
        "smif run energy_demand_constrained_D_dm_water_space"]

    os.system(run_commands[simulation_number])

    return

simulation_number = range(1) #all scenarios

if __name__ == "__main__":
    with Pool(int(cpu_count()/2)) as pool:
        pool.map(
            my_function,
            simulation_number,
            chunksize=1)

'''
for i in range(2):


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