"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
from energy_demand.geography import weather_station_location as wl

class Region(object):
    """Region class

    Arguments
    ---------
    region_name : str
        Unique identifyer of region_name
    data : dict
        Dictionary containing data

    Note
    ----
    - For each region_name, a technology stock is defined with help of regional temperature data technology specific
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(self, region_name, data, submodel_type, weather_regions):
        """Constructor
        """
        self.region_name = region_name

        # Fuels
        self.rs_enduses_fuel = data['rs_fuel_disagg'][region_name]
        self.ss_enduses_sectors_fuels = data['ss_fuel_disagg'][region_name]
        self.is_enduses_sectors_fuels = data['is_fuel_disagg'][region_name]
        self.ts_fuels = data['ts_fuel_disagg'][region_name]

        # Get closest weather station to `Region`
        closest_reg = wl.get_closest_station(
            data['reg_coord'][region_name]['longitude'],
            data['reg_coord'][region_name]['latitude'],
            data['weather_stations']
            )
        weather_reg_obj = self.get_weather_reg(
            weather_regions, closest_reg)

        # Get tech stocks and load profiles
        if submodel_type == 'rs_submodel':
            self.rs_tech_stock = weather_reg_obj.rs_tech_stock
            self.rs_load_profiles = weather_reg_obj.rs_load_profiles

            self.rs_heating_factor_y = weather_reg_obj.rs_heating_factor_y
            self.rs_cooling_factor_y = weather_reg_obj.rs_cooling_factor_y

        elif submodel_type == 'ss_submodel':
            self.ss_tech_stock = weather_reg_obj.ss_tech_stock
            self.ss_load_profiles = weather_reg_obj.ss_load_profiles

            self.ss_heating_factor_y = weather_reg_obj.ss_heating_factor_y
            self.ss_cooling_factor_y = weather_reg_obj.ss_cooling_factor_y

        elif submodel_type == 'is_submodel':
            self.is_tech_stock = weather_reg_obj.is_tech_stock
            self.is_load_profiles = weather_reg_obj.is_load_profiles

            self.is_heating_factor_y = weather_reg_obj.is_heating_factor_y
            self.is_cooling_factor_y = weather_reg_obj.is_cooling_factor_y

    def get_weather_reg(self, weather_regions, closest_reg):
        """Iterate list with weather regions and get weather region object

        Arguments
        ---------
        weather_regions : dict
            Weather regions
        closest_reg : str
            Station ID
        
        Return
        ------
        weather_region : object
            Weather region
        """
        for weather_region in weather_regions:
            if weather_region.weather_region_name == closest_reg:
                return weather_region
