"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
from energy_demand.scripts_geography import weather_station_location as wl

class Region(object):
    """Region class

    For every Region, a Region object needs to be generated.

    Parameters
    ----------
    region_name : str
        Unique identifyer of region_name
    data : dict
        Dictionary containing data

    Info
    -------------------------
    - For each region_name, a technology stock is defined with help of regional temperature data technology specific
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(self, region_name, data, submodel_type, RegionShapes):
        """Constructor
        """
        self.region_name = region_name

        # Fuels
        self.rs_enduses_fuel = data['rs_fueldata_disagg'][region_name]
        self.ss_enduses_sectors_fuels = data['ss_fueldata_disagg'][region_name]
        self.is_enduses_sectors_fuels = data['is_fueldata_disagg'][region_name]
        self.ts_fuels = data['ts_fueldata_disagg'][region_name]

        closest_station_id = wl.get_closest_station(data['reg_coordinates'][region_name]['longitude'], data['reg_coordinates'][region_name]['latitude'], data['weather_stations'])

        # Get weather region object (closest weather station to Region)
        weatherregion_object = self.get_correct_weather_point(RegionShapes, closest_station_id)

        # Get tech stocks and load profiles
        if submodel_type == 'rs_submodel':
            self.rs_tech_stock = weatherregion_object.rs_tech_stock
            self.rs_load_profiles = weatherregion_object.rs_load_profiles

            self.rs_heating_factor_y = weatherregion_object.rs_heating_factor_y
            self.rs_cooling_factor_y = weatherregion_object.rs_cooling_factor_y

            self.rs_load_profiles = weatherregion_object.rs_load_profiles

        if submodel_type == 'ss_submodel':
            self.ss_tech_stock = weatherregion_object.ss_tech_stock
            self.ss_load_profiles = weatherregion_object.ss_load_profiles

            self.ss_heating_factor_y = weatherregion_object.ss_heating_factor_y
            self.ss_cooling_factor_y = weatherregion_object.ss_cooling_factor_y

        if submodel_type == 'is_submodel':
            self.is_tech_stock = weatherregion_object.is_tech_stock
            self.is_load_profiles = weatherregion_object.is_load_profiles

            self.ss_heating_factor_y = weatherregion_object.ss_heating_factor_y
            self.ss_cooling_factor_y = weatherregion_object.ss_cooling_factor_y

    def get_correct_weather_point(self, RegionShapes, closest_station_id):
        """Iterate list with weather regions and get weather region object
        """
        for weather_region in RegionShapes:
            if weather_region.weather_region_name == closest_station_id:

                return weather_region
