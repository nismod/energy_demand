
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

    def __init__(self, coordinates, house_id, age, hlc, pop):
        """Return a new Truck object.

        Arguments
        =========
        -coordinates    coordinates
        -age            [date]  Age af dwelling
        -hlc            [float] Heat loss coefficient
        -pop            [float] Household size for dwelling
        -


        """
        self.house_id = house_id
        self.coordinates = coordinates
        self.age = age
        self.hlc = hlc
        self.pop = pop

    def scenario_driver(self):
        """calc scenario driver with population and """

        return self.pop * self.hlc

class Town_region(object):
    """Region with dwellings in it

    """

    def __init__(self, NAME):
        self.Name = NAME

    n = 100

    l = []
    for i in range(n):
        l.append(House(i, 99, 1, 0.8, i))


Town()
