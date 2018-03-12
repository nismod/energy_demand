"""Region Class
"""
from energy_demand.geography import weather_station_location

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
    rs_fuel_disagg : dict
        Nested dict by region, enduse => np.array, single dimension for fuel type
    ss_fuel_disagg : dict
        Nested dict by region, sector, enduse => np.array, single dimension for fuel type
    is_fuel_disagg : dict
        Nested dict by region, sector, enduse => np.array, single dimension for fuel type
    weather_regions : dict
        Weather regions

    Note
    ----
    *   The closest weather station is calculated
    """
    def __init__(
            self,
            name,
            longitude,
            latitude,
            rs_fuel_disagg,
            ss_fuel_disagg,
            is_fuel_disagg,
            weather_stations
        ):
        """Constructor
        """
        self.name = name
        self.longitude = longitude
        self.latitude = latitude

        # Fuels
        self.rs_enduses_fuel = rs_fuel_disagg
        self.ss_enduses_sectors_fuels = ss_fuel_disagg
        self.is_enduses_sectors_fuels = is_fuel_disagg

        # Get closest weather station
        self.closest_weather_region_id = weather_station_location.get_closest_station(
            longitude,
            latitude,
            weather_stations)
