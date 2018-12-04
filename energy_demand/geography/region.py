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
    *   The closest weather station is calculated
    """
    def __init__(
            self,
            name,
            longitude,
            latitude,
            region_fuel_disagg,
            weather_reg_cy,
            weather_reg_by
        ):
        """Constructor
        """
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.fuels = region_fuel_disagg

        # =================
        # Calculate Weather Correction factor in relation to base year
        #
        # Because the number of HDD and CDD may be different for different
        # weather years, a linear relationship between energy demand
        # related to heating and cooling is assumed and a weather
        # correction factor is calculated based on HDD and CDD calculations
        # for the weather base year and the actual weather data depending
        # on the closest weather region
        # =================

        # Climate correction factor (hdd)

        # Residential
        factor = np.sum(weather_reg_cy.rs_hdd_by) / np.sum(weather_reg_by.rs_hdd_by)
        if np.isnan(factor):
            f_climate_hdd_rs = 1
        else:
            f_climate_hdd_rs = factor

        # Service
        factor = np.sum(weather_reg_cy.ss_hdd_by) / np.sum(weather_reg_by.ss_hdd_by)
        if np.isnan(factor):
            f_climate_hdd_ss = 1
        else:
            f_climate_hdd_ss = factor

        # Industry
        factor = np.sum(weather_reg_cy.is_hdd_by) / np.sum(weather_reg_by.is_hdd_by)

        if np.isnan(factor):
            f_climate_hdd_is = 1
        else:
            f_climate_hdd_is = factor

        # Climate correction factor (cdd)
        factor = np.sum(weather_reg_cy.ss_cdd_by) / np.sum(weather_reg_by.ss_cdd_by)
        #f_climate_cdd_is = np.sum(weather_reg_cy.is_cdd_by) / np.sum(weather_reg_by.is_cdd_by)
        if np.isnan(factor):
            f_climate_cdd_ss = 1
        else:
            f_climate_cdd_ss = factor

        self.f_weather_correction = {
            'residential': {'hdd': f_climate_hdd_rs, 'cdd': None},
            'service': {'hdd': f_climate_hdd_ss, 'cdd': f_climate_cdd_ss},
            'industry': {'hdd': f_climate_hdd_is, 'cdd': None}}

        # Visual testing purposes
        #from energy_demand.read_write import data_loader
        #data_loader.print_closest_and_region(
        #    weather_stations,
        #    {name: {'latitude': latitude, 'longitude': longitude}},
        #    {self.closest_weather_reg: weather_stations[self.closest_weather_reg]})
