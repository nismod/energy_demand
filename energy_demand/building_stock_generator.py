
"""
#Spatial unit
-Make possible also for postodes...


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





def get_hlc(dw_type, age):
    """ Calculates the linearly derived hlc
    Source: Table 3.17 ECUK Tables

    Arguments
    =========
    -dw_type      [int]   Dwelling type
    -age          [int]   Age of dwelling

    Returns
    =========
    -hlc       Heat loss coefficient [W/m2 * K]
    """

    # Dict with linear fits for all different dwelling types { dw_type: [slope, constant]}
    linear_fits_hlc = {
        0: [-0.0223, 48.292],       # Detached
        1: [-0.0223, 48.251],       # Semi-Detached
        2: [-0.0223, 48.063],       # Terraced Average
        3: [-0.0223, ],             # Data but not used
        4: [-0.0223, ],             # Data but not used
        5: [-0.0223, 48.261],       # Bungalow
        6: [-0.0223, 48.063]        # Terraced average
        }

    # Get linearly fitted value
    hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]

    return hlc

class House(object):
    """Dwellings

    """

    def __init__(self, coordinates, house_id, age, hlc, pop, floor_area, temp):
        """Return a new Truck object.

        Arguments
        =========
        -coordinates    coordinates
        -age            [date]  Age af dwelling
        -hlc            [float] Heat loss coefficient
        -pop            [float] Household size for dwelling
        -floor_area     [float] Floor area of dwelling
        -temp           Climate variable


        """
        self.house_id = house_id
        self.coordinates = coordinates
        self.age = age
        self.hlc = hlc
        self.pop = pop
        self.floor_area = floor_area
        self.temp = temp


    def scenario_driver_water_heating(self):
        """calc scenario driver with population and heat loss coefficient """

        return self.pop

    def scenario_driver_lighting(self):
        """calc scenario driver with population and floor area"""

        return self.floor_area * self.pop

    def scenario_driver_space_heating(self):
        """calc scenario driver with population and floor area"""

        return self.floor_area * self.pop * self.temp * self.hlc

class Town_region(object):
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

from pprint import pprint


a = Town_region("Testname", 10).S_D


