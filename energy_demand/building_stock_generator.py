import sys
import os
from pprint import pprint
import building_stock_functions as bf
from main_functions import read_csv

# pylint: disable=I0011,C0321,C0301,C0103, C0325

# Read in
# ---------------------------------------------------------------
path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' # Remove
path_pop_reg_lu = os.path.join(path_main, 'residential_model/energy_fact_file_housing_stock_age.csv')

dw_age_distribution = read_csv(path_pop_reg_lu, float)
print(dw_age_distribution)
print("re")
# Assumptions

# (1) Distribution of dwellings per type
# (2) Age distribution of dwellings
# (3) Average floor area per type

dwelling_number = 1000
house_id = ""
coordinates = []
'''
age = age
        self.hlc = hlc
        self.pop = pop
        self.floor_area = floor_area
        self.temp = temp
'''
"""
#Spatial unit
-Make possible also for postcodes...


# Information about distribution of buildints


#Steps
1. Calculate base stock
2. Calculate new building stock based on demographics
3.

# Input from real world
# ---------------------
- nr_dwellings
- total_floor_area
- distribution of dwelling types
- total population
- XY coordinates
- Pop_ID
-


# Generate Real World Building Stock
ID, X, Y,

# Average population per dwelling type

# Average floor area per dwelling type
"""









'''class Town_region(object):
    """Region with dwellings in it

    """

    def __init__(self, town_name, nr_houses):
        self.town_name = town_name      # Town Name
        self.nr_houses = nr_houses      # Number of houses
        self.INPUTARGUMENTSBUILDINGS = INPUTARGUMENTSBUILDINGS
        # Create town
        building_list = []
        for i in range(self.nr_houses):
            _house = INPUTARGUMENTSBUILDINGS[i]House([23,23], 2323, 1983, 0.7, 10,)
            building_list.append(_house)
        self.building_list = building_list

    def S_D(self):
        SUM_DRIVERS = 0
        for _house in self.building_list:
            SUM_DRIVERS += _house.scenario_driver()
        print("SS: " + str(SUM_DRIVERS))
        return SUM_DRIVERS
'''


#
"""
__dict__
"""
#a = Town_region("Testname", 10).S_D


