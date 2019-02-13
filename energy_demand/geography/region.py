"""Region Class
"""
class Region(object):
    """Region class

    Arguments
    ---------
    name : str
        Name of region
    longitude : float
        Longitude coordinate
    latitude : float
        Latitude coordinate
    region_fuel_disagg : dict
        Nested dict by region, enduse => np.array, single dimension for fuel type
    """
    def __init__(
            self,
            name,
            longitude,
            latitude,
            region_fuel_disagg
        ):
        """Constructor
        """
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.fuels = region_fuel_disagg
