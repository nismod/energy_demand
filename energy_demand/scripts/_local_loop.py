import os
import subprocess

# Import multi processing tools
from multiprocessing import Pool, cpu_count

#import any other packages 
import numpy as np

def my_function(simulation_number):  
    print('simulation_number ' + str(simulation_number))

    all_weather_stations = True

    '''weather_yrs = [
        1961,1962, 1963, 1965, 1966, 1967, 1969, 1970, 1971,
            1973, 1974, 1975, 1977, 1978, 1979, 1981,
            1983, 1985, 1986, 1987, 
            1989, 1990, 1991, 1993,
            1994, 1995, 1997, 1998, 1999, 2001, 2002, 2003,
            2005, 2006,2007, 2009, 2010, 2011, 2013, 2014]'''
        
    weather_yrs = range(1960, 2016)

    weather_yr = weather_yrs[simulation_number]

    if all_weather_stations:
        weather_station_cnt = [] #All stationssimulation_number
    else:
        weather_station_cnt = simulation_number

    # Run energy demand main.py
    bash_command1 = "cd C:/Users/cenv0553/ed"

    bash_command = "python energy_demand/energy_demand/main.py {}".format(weather_yr)

    os.system(bash_command)
    print("======================")
    print("Finished model run simulation: weather_yr: {} weather_station_cnt: {}".format(weather_yr, weather_station_cnt))
    print("======================")

# ===============================
simulation_number = range(40)

for i in simulation_number:
    my_function(i)
