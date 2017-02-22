""" Functions for building stock"""

# pylint: disable=I0011,C0321,C0301,C0103, C0325


class House(object):
    """Class of a single dwelling or of a aggregated group of dwelling"""

    def __init__(self, coordinates, house_id, age, hlc, pop, floor_area, temp):
        """Returns a new dwelling object.

        Parameters
        ----------
        coordinates : float
            Coordinates
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
        self.age = age
        self.hlc = hlc
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
        3: [-0.0223, ],             # Data but not used
        4: [-0.0223, ],             # Data but not used
        5: [-0.0223, 48.261],       # Bungalow
        6: [-0.0223, 48.063]        # Terraced average
        }

    # Get linearly fitted value
    hlc = linear_fits_hlc[dw_type][0] * age + linear_fits_hlc[dw_type][1]
    return hlc
    