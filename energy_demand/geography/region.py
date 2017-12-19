"""Region representation
"""

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
    weather_region : obj
        weather_reg_obj weather region of Region

    Note
    ----
    All fuel is stored in the region class and the closest weather station
    is calculated and the technology and load profiles imported from
    this station
    """
    def __init__(
            self,
            name,
            rs_fuel_disagg,
            ss_fuel_disagg,
            is_fuel_disagg,
            weather_region
        ):
        """Constructor
        """
        self.name = name

        # Fuels
        self.rs_enduses_fuel = rs_fuel_disagg
        self.ss_enduses_sectors_fuels = ss_fuel_disagg
        self.is_enduses_sectors_fuels = is_fuel_disagg

        # Get tech stocks and load profiles

        #Residential submodel
        self.rs_tech_stock = weather_region.rs_tech_stock
        self.rs_load_profiles = weather_region.rs_load_profiles

        self.rs_heating_factor_y = weather_region.rs_heating_factor_y
        self.rs_cooling_factor_y = weather_region.rs_cooling_factor_y

        #Service submodel
        self.ss_tech_stock = weather_region.ss_tech_stock
        self.ss_load_profiles = weather_region.ss_load_profiles

        self.ss_heating_factor_y = weather_region.ss_heating_factor_y
        self.ss_cooling_factor_y = weather_region.ss_cooling_factor_y

        #Industry submodel
        self.is_tech_stock = weather_region.is_tech_stock
        self.is_load_profiles = weather_region.is_load_profiles

        self.is_heating_factor_y = weather_region.is_heating_factor_y
        self.is_cooling_factor_y = weather_region.is_cooling_factor_y
