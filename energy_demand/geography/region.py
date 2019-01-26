"""Region Class
"""
import numpy as np

from energy_demand.geography import weather_station_location

class Region(object):
    """Region class

    Arguments
    ---------
    name : str
        Name of region
    weather_region_id : str
        ID of closest weather station
    longitude : float
        Longitude coordinate
    latitude : float
        Latitude coordinate
    fuel_disagg : dict
        Nested dict by region, enduse => np.array, single dimension for fuel type
    weather_stations : dict
        Weather stations of current weather year
    weather_stations_by : dict
        Weather stations of base weather year
    weather_reg_cy : dict
        Weather station region objects of current weather year
    weather_reg_by : dict
        Weather station region objects of current weather year

    Note
    ----
    The closest weather station is calculated
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

        # Visual testing purposes
        #from energy_demand.read_write import data_loader
        #data_loader.print_closest_and_region(
        #    weather_stations,
        #    {name: {'latitude': latitude, 'longitude': longitude}},
        #    {self.closest_weather_reg: weather_stations[self.closest_weather_reg]})
