import sys, os
from pprint import pprint
import building_stock_functions as bf
from main_functions import read_csv
import numpy as np
# pylint: disable=I0011,C0321,C0301,C0103, C0325


def virtual_building_stock(data):
    """Creates a virtual building stock based on base year data and assumptions

    Parameters
    ----------
    data : dict
        Base data

    Returns
    -------
    dw_stock_old : list
        List containing dwelling objects of existing buildings

    dw_stock_new : list
        List containing dwelling objects of new buildings

    Notes
    -----
    The header row is always skipped.
    """
    uniqueID = 100000
    dw_stock_old, dw_stock_new = [], [] # Initialise

    #get_assumption_age_distribution
    base_year = data['global_variables']['base_year']

    dwtype_distr = data['dwtype_distr'][base_year]             # Distribution of dwelling types        2015.0: {'semi_detached': 26.0, 'terraced': 28.3, 'flat': 20.3, 'detached': 16.6, 'bungalow': 8.8}
    dwtype_age_distr = data['dwtype_age_distr'][base_year]     # Age distribution of dwelling types    {2015: {1918: 20.8, 1928: 36.3, 1949: 29.4, 1968: 8.0, 1995: 5.4}} # year, average_age, percent
    dwtype_floor_area = data['dwtype_floor_area']              # Floor area [m2]                       {'semi_detached': 96.0, 'terraced': 82.5, 'flat': 61.0, 'detached': 147.0, 'bungalow': 77.0}
    reg_floor_area = data['reg_floor_area']                    # Floor Area in a region
    dw_lu = data['dwtype_lu']
    global_variables = data['global_variables']
    reg_lu = data['reg_lu']                                    # Regions
    reg_pop = data['reg_pop']
    print(dwtype_distr)
    print("---")
    print(dwtype_age_distr)
    print("---")
    print(dwtype_floor_area)
    print("-tt--")
    print(reg_floor_area)
    print("oo")
    print(dw_lu)

    # Iterate regions
    for reg_id in reg_lu:

        # Read base data
        reg_id_floor_area_by = reg_floor_area[reg_id]       # Read in floor area
        reg_id_dw_nr = data['reg_dw_nr'][reg_id]            # Read in nr of dwellings
        print("reg_floor_area: " + str(reg_id_floor_area_by))
        print("reg_dw_nr: " + str(reg_id_dw_nr))

        floor_area_p_by = p_floor_area_dwtype(dw_lu, dwtype_distr, dwtype_floor_area, reg_id_dw_nr) # Percent of floor area of base year (is the same for all old buildings)

        # --Scenario drivers
        # base year
        reg_id_pop_by = reg_pop[reg_id]                     # Read in population
        reg_id_floor_area_pp_by = reg_id_floor_area_by / reg_id_pop_by   # Floor area per person [m2/person]
        reg_id_floor_area_by_pd = reg_id_floor_area_by / reg_id_dw_nr    # Floor area per dwelling [m2/dwelling]

        # current year
        reg_id_pop_cy = reg_id_pop_by * 1.5                             ### #TODO: get new population
        reg_id_floor_area_pp_cy = reg_id_floor_area_pp_by * 1.05        ### #TODO: get new reg_id_floor_area_pp_by
        reg_id_floor_area_by_pd_cy = reg_id_floor_area_by_pd * 0.1      ### #TODO: get new reg_id_floor_area_by_pd

        # Population
        #pop_new_dw = reg_id_pop_cy - reg_id_pop_by

        # Calculate total floor area
        total_floor_area_cy = reg_id_floor_area_pp_cy * reg_id_pop_cy
        total_floor_area_new_area = total_floor_area_cy - (reg_id_floor_area_pp_by * reg_id_pop_by) # tot new floor area - area base year = New needed floor area

        print(" Current floor area:       " + str(total_floor_area_cy))
        print(" New needed floor area:    " + str(total_floor_area_new_area))

        # Calculate total number of dwellings (existing build + need for new ones)
        dw_new = total_floor_area_new_area / reg_id_floor_area_by_pd # Needed new buildings
        total_nr_dw = reg_id_dw_nr + dw_new # floor area / buildings

        print("New buildings:       " + str(dw_new))
        print("total_nr_dw:       " + str(total_nr_dw))



        # ---- old buildings
        # Distribute old dwellings according to dwelling distribution
        # ITerate dwelling types
        for dw in dw_lu:
            dw_type_id = dw
            dw_type_name = dw_lu[dw]
            print("Dwelling type: " + str(dw_type_name))

            percent_dw_type = dwtype_distr[dw_type_name] / 100              # Percentage of dwelling type
            print("percentage of dwelling type: " + str(percent_dw_type))

            dw_type_floor_area = floor_area_p_by[dw_type_name] * total_floor_area_cy
            print("Floor area of dwelling types: " + str(dw_type_floor_area))

            ## Get scenario parameter?? TODO:
            ## percent_dw_type = percent_dw_type??

            dw_type_dw_nr = percent_dw_type * reg_id_dw_nr # Nr of existing dwellings dw type
            print("Nr of Dwelling of tshi type: " + str(dw_type_dw_nr))

            # Distribute according to age
            for dwtype_age_id in dwtype_age_distr:
                print(" Age class, dwelling type " + str(dwtype_age_id))
                age_class_p = dwtype_age_distr[dwtype_age_id] / 100 # Percent of dw of age class

                # Floor area of dwelling_class_age
                dw_type_age_class_floor_area = dw_type_floor_area * age_class_p # Distribute proportionally floor area
                print("dw_type_age_class_floor_area: " + str(dw_type_age_class_floor_area))
                print(reg_id_floor_area_pp_by)

                # Pop
                _pop_2015_dwelling_type_age_class = dw_type_age_class_floor_area / reg_id_floor_area_pp_by # Distribed with floor area..could do better
                print("_pop_2015_dwelling_type_age_class: " + str(_pop_2015_dwelling_type_age_class))

                # --- create building object
                _hlc = bf.get_hlc(dw_type_id, float(dwtype_age_id))

                dw_stock_old.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, float(dwtype_age_id), _hlc, _pop_2015_dwelling_type_age_class, dw_type_age_class_floor_area, 9999))
                uniqueID += 1

        # ------------ new buildings
        for dw in dw_lu:
            dw_type_id = dw
            dw_type_name = dw_lu[dw]

            percent_dw_type = dwtype_distr[dw_type_name] / 100              # Percentage of dwelling type (TODO: Nimm scneario value)

            print("Floor area of new buildings per dwelling types: " + str(total_floor_area_new_area))

            dw_type_dw_nr_new = percent_dw_type * dw_new # Nr of existing dwellings dw type new
            print("Nr of Dwelling of tshi type: " + str(dw_type_dw_nr_new))

            # Floor area of dwelling_class_age
            dw_type_age_class_floor_area_new = total_floor_area_new_area * age_class_p # Distribute proportionally floor area
            print("dw_type_age_class_floor_area_new: " + str(dw_type_age_class_floor_area_new))

            # Pop
            _pop_2015_dwelling_type_age_class_new = dw_type_age_class_floor_area_new / reg_id_floor_area_pp_cy # Distribed with floor area..could do better
            print("_pop_2015_dwelling_type_age_class: " + str(_pop_2015_dwelling_type_age_class_new))

            # Get age of building construction
            sim_period = range(global_variables['base_year'], global_variables['current_year'] + 1, 1) #base year, current year + 1, iteration step
            nr_sim_y = len(sim_period)
            for simulation_year in sim_period:
                dw_age = simulation_year
                _hlc = bf.get_hlc(dw_type_id, dw_age)

                # --- create building object
                dw_stock_new.append(bf.Dwelling(['X', 'Y'], dw_type_id, uniqueID, simulation_year, _hlc, _pop_2015_dwelling_type_age_class_new/nr_sim_y, dw_type_age_class_floor_area/nr_sim_y, 9999))
                uniqueID += 1

    print("....")
    for h in dw_stock_old:
        print(h.__dict__)
    print(".............")
    for i in dw_stock_new:
        print(i.__dict__)

    return dw_stock_old, dw_stock_new



# -----------Calculate the share of total floor area beloinging to each dwelling type-----------
def p_floor_area_dwtype(dw_lookup, dw_dist, dw_floor_area, reg_id_dw_nr):
    """ Calculates the percentage of floor area  belonging to each dwelling type
    depending on average floor area per dwelling type
    dw_lookup - dwelling types
    dw_dist   - distribution of dwellin types
    dw_floor_area - floor area per type
    reg_id_dw_nr - number of total dwlling

    returns a dict with percentage of each total floor area for each dwtype (must be 1.0 in tot)
    """

    total_floor_area_cy = 0
    dw_floor_area_p = {} # Initialise percent of total floor area per dwelling type

    for dw_id in dw_lookup:
        dw_name = dw_lookup[dw_id]

        # Get number of building of dwellin type
        percent_buildings_dw = (dw_dist[dw_name])/100
        nr_dw_typXY = reg_id_dw_nr * percent_buildings_dw

        # absolute usable floor area per dwelling type
        fl_type = nr_dw_typXY * dw_floor_area[dw_name]

        # sum total area
        total_floor_area_cy += fl_type
        dw_floor_area_p[dw_name] = fl_type # add absolute are ato dict

    # Convert absolute values into percentages
    for i in dw_floor_area_p:
        dw_floor_area_p[i] = (1/total_floor_area_cy)*dw_floor_area_p[i]

    return dw_floor_area_p


"""
# (1) Distribution of dwellings per type
# (2) Age distribution of dwellings
# (3) Average floor area per type
# (4) Renovations?
# (5) New houses

dwelling_number = 1000
house_id = ""
coordinates = []

age = age
        self.hlc = hlc
        self.pop = pop
        self.floor_area = floor_area
        self.temp = temp


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
- total_floor_area_cy
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
