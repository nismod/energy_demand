"""The technological stock for every simulation year"""
import numpy as np
from energy_demand.scripts_technologies import technologies_related
#pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213

class TechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(self, stock_name, data, temp_by, temp_cy, t_base_heating, potential_enduses, t_base_heating_cy, enduse_technologies):
        """Constructor of technologies for residential sector

        Parameters
        ----------
        data : dict
            All data
        technologies : list
            Technologies of technology stock
        temp_cy : int
            Temperatures of current year

        Notes
        -----
        -   The shapes are given for different enduse as technology may be used in different enduses and either
            a technology specific shape is assigned or an overall enduse shape
        """
        self.stock_name = stock_name

        self.stock_technologies = self.create_tech_stock(
            data,
            temp_by,
            temp_cy,
            t_base_heating,
            t_base_heating_cy,
            potential_enduses,
            enduse_technologies
            )

    @classmethod
    def create_tech_stock(cls, data, temp_by, temp_cy, t_base_heating, t_base_heating_cy, enduses, technologies):
        """Create technologies and add to technology list
        """
        stock_technologies = []

        for enduse in enduses:
            for technology_name in technologies[enduse]:
                #print("         ...{}   {}".format(sector, technology))

                tech_type = technologies_related.get_tech_type(technology_name, data['assumptions']['technology_list'])

                if tech_type == 'hybrid_tech':
                    # Create hybrid technology object
                    tech_object = HybridTechnology(
                        enduse,
                        technology_name,
                        data,
                        temp_by,
                        temp_cy,
                        t_base_heating,
                        t_base_heating_cy,
                        )

                else:
                    tech_object = Technology(
                        enduse,
                        technology_name,
                        data,
                        temp_by,
                        temp_cy,
                        t_base_heating,
                        t_base_heating_cy,
                        tech_type
                    )

                stock_technologies.append(tech_object)

        return stock_technologies

    def get_tech_attr(self, enduse, tech_name, attribute_to_get):
        """Get a technology attribute from a technology object stored in a list

        Parameters
        ----------
        enduse : string
            Enduse to read technology specified for this enduse
        tech_name : string
            List with stored technologies
        attribute_to_get : string
            Attribute of technology to get

        Return
        -----
        tech_attribute : attribute
            Technology attribute
        """
        for tech_object in self.stock_technologies:
            if tech_object.tech_name == tech_name and tech_object.enduse == enduse:
                tech_attribute = getattr(tech_object, str(attribute_to_get))

                return tech_attribute

class Technology(object):
    """Technology Class

    Notes
    -----
    The attribute `shape_peak_yd_factor` is initiated with dummy data and only filled with real data
    in the `Region` Class. The reason is because this factor depends on regional temperatures

    The daily and hourly shape of the fuel used by this Technology
    is initiated with zeros in the 'Technology' attribute. Within the `Region` Class these attributes
    are filled with real values.

    Only the yd shapes are provided on a technology level and not dh shapes
    """
    def __init__(self, enduse, tech_name, data, temp_by, temp_cy, t_base_heating, t_base_heating_cy, tech_type):
        """Contructor of Technology

        Parameters
        ----------
        tech_name : str
            Technology Name
        data : dict
            All internal and external provided data
        temp_cy : array
            Temperatures of current year
        """
        self.enduse = enduse
        self.tech_name = tech_name
        self.market_entry = data['assumptions']['technologies'][tech_name]['market_entry']
        self.tech_type = tech_type
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']

        # Shares of fueltype for every hour for single fueltype
        self.fueltypes_yh_p_cy = self.set_constant_fueltype(data['assumptions']['technologies'][tech_name]['fuel_type'], data['nr_of_fueltypes'])

        # --------------------------------------------------------------
        # Base and current year efficiencies depending on technology type
        # --------------------------------------------------------------
        if self.tech_type == 'heat_pump':
            self.eff_by = technologies_related.get_heatpump_eff(
                temp_by,
                data['assumptions']['hp_slope_assumption'],
                data['assumptions']['technologies'][tech_name]['eff_by'],
                t_base_heating)

            self.eff_cy = technologies_related.get_heatpump_eff(
                temp_cy,
                data['assumptions']['hp_slope_assumption'],
                technologies_related.calc_eff_cy(
                    data['assumptions']['technologies'][tech_name]['eff_by'],
                    tech_name,
                    data['base_sim_param'],
                    data['assumptions'],
                    self.eff_achieved_factor,
                    self.diff_method
                    ),
                t_base_heating_cy)
        else:
            self.eff_by = technologies_related.const_eff_yh(data['assumptions']['technologies'][tech_name]['eff_by'])
            self.eff_cy = technologies_related.const_eff_yh(
                technologies_related.calc_eff_cy(
                    data['assumptions']['technologies'][tech_name]['eff_by'],
                    tech_name,
                    data['base_sim_param'],
                    data['assumptions'],
                    self.eff_achieved_factor,
                    self.diff_method)
            )

        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_per_type_yd = technologies_related.convert_yh_to_yd_fueltype_shares(
            data['nr_of_fueltypes'],
            self.fueltypes_yh_p_cy
            )

    @staticmethod
    def set_constant_fueltype(fueltype, len_fueltypes):
        """Create dictionary with constant single fueltype

        Parameters
        ----------
        fueltype : int
            Single fueltype for defined technology
        len_fueltypes : int
            Number of fueltypes

        Return
        ------
        fueltypes_yh : array
            Fraction of fueltype for every hour and for all fueltypes

        Note
        ----
        The array is defined with 1.0 fraction for the input fueltype. For all other fueltypes,
        the fraction is defined as zero.

        Example
        -------
        array[fueltype_input][day][hour] = 1.0 # This specific hour is served with fueltype_input by 100%
        """
        # Initiat fuel dict and set per default as 0 percent
        fueltypes_yh = np.zeros((len_fueltypes, 365, 24))

        # Insert for the single fueltype for every hour the share to 1.0
        fueltypes_yh[fueltype] = 1.0

        return fueltypes_yh

class HybridTechnology(object):
    """Hybrid technology which consist of two different technologies

    Parameters
    ----------
    enduse : string
        Enduse
    tech_name : string
        Name of hybrid technology
    data : dict
        Data
    temp_by : array
        Temperature base year
    temp_cy : array
        Temperature current year  
    t_base_heating_by : flaot
        Base temperature heating
    t_base_heating_cy : flaot
        Base temperature heating

    Returns
    -------
    enduse : TODO



    Info
    -----
    - The higher temperature technology is always an electric heat pump
    - The lower temperature (used for peak)
    """
    def __init__(self, enduse, tech_name, data, temp_by, temp_cy, t_base_heating_by, t_base_heating_cy):
        """
        """
        self.enduse = enduse
        self.tech_name = tech_name

        self.tech_low_temp = data['assumptions']['technologies'][tech_name]['tech_low_temp']
        self.tech_high_temp = data['assumptions']['technologies'][tech_name]['tech_high_temp']

        self.tech_low_temp_fueltype = data['assumptions']['technologies'][self.tech_low_temp]['fuel_type']
        self.tech_high_temp_fueltype = data['assumptions']['technologies'][self.tech_high_temp]['fuel_type']

        self.eff_tech_low_by = technologies_related.const_eff_yh(data['assumptions']['technologies'][self.tech_low_temp]['eff_by'])
        self.eff_tech_high_by = technologies_related.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumption'], data['assumptions']['technologies'][self.tech_high_temp]['eff_by'], t_base_heating_by)

        # Consider efficiency improvements
        eff_tech_low_cy = technologies_related.calc_eff_cy(
            data['assumptions']['technologies'][self.tech_low_temp]['eff_by'],
            self.tech_low_temp,
            data['base_sim_param'],
            data['assumptions'],
            data['assumptions']['technologies'][self.tech_low_temp]['eff_achieved'],
            data['assumptions']['technologies'][self.tech_low_temp]['diff_method']
            )

        eff_tech_high_cy = technologies_related.calc_eff_cy(
            data['assumptions']['technologies'][self.tech_high_temp]['eff_by'],
            self.tech_high_temp,
            data['base_sim_param'],
            data['assumptions'],
            data['assumptions']['technologies'][self.tech_high_temp]['eff_achieved'],
            data['assumptions']['technologies'][self.tech_high_temp]['diff_method']
            )

        # Efficiencies
        self.eff_tech_low_cy = technologies_related.const_eff_yh(eff_tech_low_cy) #constant eff of low temp tech
        self.eff_tech_high_cy = technologies_related.get_heatpump_eff(temp_cy, data['assumptions']['hp_slope_assumption'], eff_tech_high_cy, t_base_heating_cy)

        # Get fraction of service for hybrid technologies for every hour

        self.service_distr_hybrid_h_p = self.service_hybrid_tech_low_high_h_p(
            temp_cy,
            data['assumptions']['technologies'][tech_name]['hybrid_cutoff_temp_low'],
            data['assumptions']['technologies'][tech_name]['hybrid_cutoff_temp_high']
            )

        # Shares of fueltype for every hour for multiple fueltypes
        self.fueltypes_yh_p_cy = self.calc_hybrid_fueltypes_p(
            data['nr_of_fueltypes'],
            self.tech_low_temp_fueltype,
            self.tech_high_temp_fueltype)

        self.eff_by = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by)

        # Current year efficiency (weighted according to service for hybrid technologies)
        self.eff_cy = self.calc_hybrid_eff(self.eff_tech_low_cy, self.eff_tech_high_cy)

        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_per_type_yd = technologies_related.convert_yh_to_yd_fueltype_shares(data['nr_of_fueltypes'], self.fueltypes_yh_p_cy)

    def service_hybrid_tech_low_high_h_p(self, temp_cy, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
        """Calculate fraction of service for every hour within each hour

        Within every hour the fraction of service provided by the low-temp technology
        and the high-temp technology is calculated

        Parameters
        ----------
        temp_cy : array
            Temperature of current year
        hybrid_cutoff_temp_low : int
            Temperature cut-off criteria (blow this temp, 100% service provided by lower temperature technology)
        hybrid_cutoff_temp_high : int
            Temperature cut-off criteria (above this temp, 100% service provided by higher temperature technology)

        Return
        ------
        tech_low_high_p : dict
            Share of lower and higher service fraction for every hour
        """
        tech_low_high_p = {
            'low': np.zeros((365, 24)),
            'high': np.zeros((365, 24))
            }

        for day, temp_d in enumerate(temp_cy):
            for hour, temp_h in enumerate(temp_d):

                # Get share of service of high temp technology
                service_high_tech_p = self.get_fraction_service_high_temp(
                    temp_h,
                    hybrid_cutoff_temp_low,
                    hybrid_cutoff_temp_high
                    )

                # Calculate share of service of low temp technology
                service_low_tech_p = 1.0 - service_high_tech_p

                tech_low_high_p['low'][day][hour] = service_low_tech_p
                tech_low_high_p['high'][day][hour] = service_high_tech_p

        return tech_low_high_p

    def calc_hybrid_eff(self, eff_tech_low, eff_tech_high):
        """Calculate efficiency for every hour for hybrid technology

        The weighted efficiency for every hour is calculated based on fraction of service
        delieverd with eigher hybrid technology

        Parameters
        ----------
        eff_tech_low : float
            Efficiency of technology operating at lower temperatures
        eff_tech_high : float
            Efficiency of technology operating at higher temperatures

        Return
        ------
        eff_hybrid_yh : array
            Efficiency of hybrid technology

        Info
        -----
        It is assumed that the temperature operating at higher temperatures is a heat pump
        """
        eff_hybrid_yh = np.zeros((365, 24))

        for day in range(365):
            for hour in range(24):

                # Fraction of service of low and high temp technology
                service_high_p = self.service_distr_hybrid_h_p['high'][day][hour]
                service_low_p = self.service_distr_hybrid_h_p['low'][day][hour]

                # Efficiencies
                eff_low = eff_tech_low[day][hour]
                eff_high = eff_tech_high[day][hour]

                # Calculate weighted efficiency
                eff_hybrid_yh[day][hour] = (service_high_p * eff_high) + (service_low_p * eff_low)

                assert eff_hybrid_yh[day][hour] >= 0

        return eff_hybrid_yh

    def calc_hybrid_fueltypes_p(self, nr_fueltypes, fueltype_low_temp, fueltype_high_temp):
        """Calculate share of fueltypes for every hour for hybrid technology

        Parameters
        -----------
        nr_fueltypes : int
            Number of fuels
        fueltype_low_temp : int
            Fueltype of low temperature technology
        fueltype_high_temp : int
            Fueltype of high temperature technology

        Return
        ------
        fueltypes_yh : array (fueltpes, days, hours)
            The share of fuel given for the fueltypes

        Info
        -----
            -   The distribution to different fueltypes is only valid within an hour,
                i.e. the fuel is not distributed across the day. This means that within
                an hour the array always sums up to 1 (=100%) across the fueltypes.

            -   The higer temperature technolgy is always a heat pump

            -   Fueltypes of both technologies must be different
        """
        fueltypes_yh = np.zeros((nr_fueltypes, 365, 24))

        # Calculate hybrid efficiency
        hybrid_eff_yh = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by)

        for day in range(365):
            for hour in range(24):

                # Fraction of service of low and high temp technology
                service_low_h_p = self.service_distr_hybrid_h_p['low'][day][hour]
                service_high_h_p = self.service_distr_hybrid_h_p['high'][day][hour]

                # Get hybrid efficiency
                hybrid_eff = hybrid_eff_yh[day][hour]

                # Calculate fuel fractions
                if service_low_h_p > 0:
                    fuel_low_h = np.divide(service_low_h_p, hybrid_eff)
                else:
                    fuel_low_h = 0

                if service_high_h_p > 0:
                    fuel_high_h = np.divide(service_high_h_p, hybrid_eff)
                else:
                    fuel_high_h = 0

                tot_fuel_h = fuel_low_h + fuel_high_h

                # Assign share of total fuel for respective fueltypes
                fueltypes_yh[fueltype_low_temp][day][hour] = np.divide(1.0, tot_fuel_h) * fuel_low_h
                fueltypes_yh[fueltype_high_temp][day][hour] = np.divide(1.0, tot_fuel_h) * fuel_high_h

        np.testing.assert_almost_equal(np.sum(fueltypes_yh), 365 * 24, decimal=3, err_msg='ERROR XY')

        return fueltypes_yh

    @classmethod
    def get_fraction_service_high_temp(cls, current_temp, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
        """Calculate percent of service for high-temp technology based on assumptions of hybrid technology

        Parameters
        ----------
        current_temp : float
            Temperature to find fraction
        hybrid_cutoff_temp_low : float
            Temperature from which below only low temp technology functions
        hybrid_cutoff_temp_high : float
            Temperature from which abive only high temp technology functions

        Return
        ------
        fraction_high_temp_tech : float
            Fraction of higher temperature technology

        Note
        -----
            -   It is assumed that share of service of tech_high at hybrid_cutoff_temp_high == 100%
        """
        if current_temp >= hybrid_cutoff_temp_high:
            fraction_high_temp_tech = 1.0
        elif current_temp < hybrid_cutoff_temp_low:
            fraction_high_temp_tech = 0.0
        else:
            if hybrid_cutoff_temp_low < 0:
                temp_diff = hybrid_cutoff_temp_high + abs(hybrid_cutoff_temp_low)
                temp_diff_current_temp = current_temp + abs(hybrid_cutoff_temp_low)
            else:
                temp_diff = hybrid_cutoff_temp_high - hybrid_cutoff_temp_low
                temp_diff_current_temp = current_temp - hybrid_cutoff_temp_low

            # Calculate service share of high temp technology
            fraction_high_temp_tech = np.divide(1.0, temp_diff) * temp_diff_current_temp

        return fraction_high_temp_tech
