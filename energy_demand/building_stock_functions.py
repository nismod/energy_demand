""" Functions for building stock"""

# pylint: disable=I0011,C0321,C0301,C0103, C0325


class Dwelling(object):
    """Class of a single dwelling or of a aggregated group of dwelling"""

    def __init__(self, coordinates, dwtype, house_id, age, pop, floor_area, temp):
        """Returns a new dwelling object.

        Parameters
        ----------
        coordinates : float
            coordinates
        dwtype : int
            Dwelling type id
        age :   int
            Age of dwelling
        hlc : float
            Heat loss coefficient
        dw_pop : float
            Dwelling population
        floor_area : float
            Floor area of dwelling
        temp : float
            Climate variable...(tbd)

        """
        self.house_id = house_id
        self.coordinates = coordinates
        self.dwtype = dwtype
        self.age = age
        self.hlc = get_hlc(dwtype, age) # Calculate heat loss coefficient with age and dwelling type
        self.pop = pop
        self.floor_area = floor_area
        self.temp = temp

    def scenario_driver_water_heating(self):
        """calc scenario driver with population and heat loss coefficient"""
        return self.pop

    def scenario_driver_lighting(self):
        """calc scenario driver with population and floor area"""
        return self.floor_area * self.pop

    def scenario_driver_space_heating(self):
        """calc scenario driver with population and floor area"""
        return self.floor_area * self.pop * self.temp * self.hlc

def get_hlc(dw_type, age):
    """Calculates the linearly derived hlc

    Parameters
    ----------
    dw_type : int
        Dwelling type
    age : int
        Age of dwelling

    Returns
    -------
    hls : Heat loss coefficient [W/m2 * K]

    Notes
    -----
    Source: Table 3.17 ECUK Tables
    """
    # Dict with linear fits for all different dwelling types { dw_type: [slope, constant]}
    linear_fits_hlc = {
        0: [-0.0223, 48.292],       # Detached
        1: [-0.0223, 48.251],       # Semi-Detached
        2: [-0.0223, 48.063],       # Terraced Average
        3: [-0.0223, 47.02],        # Flats
        4: [-0.0223, 48.261],       # Bungalow
        }

    # Get linearly fitted value
    hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]
    return hlc

class BuildingStockRegion(object):
    """Class of the building stock in a region"""

    def __init__(self, region_ID, dwelling_list):
        """Returns a new building stock region object.

        Parameters
        ----------
        region_ID : float
            Region ID of building stock
        dwelling_list : list
            List containing all dwelling objects
        """
        self.region_ID = region_ID
        self.dwelling_list = dwelling_list

    def get_tot_pop(self):
        """ Get total population"""
        totpop = 0
        for dwelling in self.dwelling_list:
            totpop += dwelling.pop()
        return totpop

    def get_sum_scenario_driver_water_heating(self):
        """ Sum all scenario driver for water heating"""
        sum_driver = 0
        for dwelling in self.dwelling_list:
            sum_driver += dwelling.scenario_driver_water_heating()
        return sum_driver

    def get_sum_scenario_driver_space_heating(self):
        """ Sum all scenario driver for space heating"""
        sum_driver = 0
        for dwelling in self.dwelling_list:
            sum_driver += dwelling.scenario_driver_space_heating()
        return sum_driver

    def get_sum_scenario_driver_lighting(self):
        """ Sum all scenario driver for lighting heating"""
        sum_driver = 0
        for dwelling in self.dwelling_list:
            sum_driver += dwelling.scenario_driver_lighting()
        return sum_driver

