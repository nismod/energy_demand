"""Region representation
"""
from energy_demand.geography import weather_station_location

class Region(object):
    """Region class

    Arguments
    ---------
    name : str
        Name of region
    rs_fuel_disagg : dict
        Nested dict by region, enduse => np.array, single dimension for fuel type
    ss_fuel_disagg : dict
        Nested dict by region, sector, enduse => np.array, single dimension for fuel type
    is_fuel_disagg : dict
        Nested dict by region, sector, enduse => np.array, single dimension for fuel type
    weather_regions : obj
        Weather regions

    Note
    ----
    All fuel is stored in the region class and the closest weather station
    is calculated and the technology and load profiles imported from
    this station
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
