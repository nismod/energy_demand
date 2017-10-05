"""Functions related to the technological stock
"""
import sys
import numpy as np
import logging
from energy_demand.technologies import tech_related
from energy_demand.profiles import load_profile
#pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213

class TechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(self, stock_name, assumptions, sim_param, lookups, temp_by, temp_cy, t_base_heating_by, potential_enduses, t_base_heating_cy, enduse_technologies):
        """Constructor of technologies for residential sector

        Arguments
        ----------
        stock_name : str
            Name of technology stock
        data : dict
            All data
        temp_by : array
            Base year temperatures
        temp_cy : int
            Current year temperatures
        t_base_heating_by : float
            Base temperature for heating
        potential_enduses : list
            Enduses of technology stock
        t_base_heating_cy : float
            Base temperature current year
        enduse_technologies : list
            Technologies of technology stock

        Notes
        -----
        - The shapes are given for different enduse as technology may be used
          in different enduses and either a technology specific shape is
          assigned or an overall enduse shape
        """
        self.stock_name = stock_name

        self.stock_technologies = self.create_tech_stock(
            assumptions, sim_param, lookups,
            temp_by,
            temp_cy,
            t_base_heating_by,
            t_base_heating_cy,
            potential_enduses,
            enduse_technologies
            )

    def get_attribute_tech_stock(self, technology, enduse, attribute_to_get):
        """Get attribuet from technology stock

        Arguments
        ----------
        technology : str
            Technology
        enduse : str
            Enduse
        attribute_to_get : str
            Attribute to read out

        Return
        ------
        tech_obj.tech_type : object
        """
        tech_obj = self.stock_technologies[(technology, enduse)]

        if attribute_to_get == 'tech_type':
            return tech_obj.tech_type

    @classmethod
    def create_tech_stock(cls, assumptions, sim_param, lookups, temp_by, temp_cy, t_base_heating_by, t_base_heating_cy, enduses, technologies):
        """Create technologies and add to dict with key_tuple

        Arguments
        ----------
        data : dict
            All data
        temp_by : array
            Base year temperatures
        temp_cy : int
            Current year temperatures
        t_base_heating_by : float
            Base temperature for heating
        t_base_heating_cy : float
            Base temperature current year
        enduses : list
            Enduses of technology stock
        technologies : list
            Technologies of technology stock
        """
        stock_technologies = {}

        for enduse in enduses:
            for technology_name in technologies[enduse]:
                #logging.debug("         ...{}   {}".format(sector, technology))
                tech_type = tech_related.get_tech_type(technology_name, assumptions['tech_list'])

                if tech_type == 'hybrid_tech':
                    # Create hybrid technology object
                    tech_object = HybridTechnology(
                        enduse,
                        technology_name,
                        assumptions, sim_param, lookups,
                        temp_by,
                        temp_cy,
                        t_base_heating_by,
                        t_base_heating_cy
                        )
                else:
                    tech_object = Technology(
                        technology_name,
                        assumptions, sim_param, lookups,
                        temp_by,
                        temp_cy,
                        t_base_heating_by,
                        t_base_heating_cy,
                        tech_type
                    )

                stock_technologies[(technology_name, enduse)] = tech_object

        return stock_technologies

    def get_tech_attr(self, enduse, tech_name, attribute_to_get):
        """Get a technology attribute from a technology object stored in a list

        Arguments
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
        tech_object = self.stock_technologies[(tech_name, enduse)]

        if attribute_to_get == 'service_distr_hybrid_h_p':
            return tech_object.service_distr_hybrid_h_p
        elif attribute_to_get == 'eff_cy':
            return tech_object.eff_cy
        elif attribute_to_get == 'eff_by':
            return tech_object.eff_by
        elif attribute_to_get == 'tech_low_temp':
            return tech_object.tech_low_temp
        elif attribute_to_get == 'tech_low_temp_fueltype':
            return tech_object.tech_low_temp_fueltype
        elif attribute_to_get == 'tech_high_temp_fueltype':
            return tech_object.tech_high_temp_fueltype
        elif attribute_to_get == 'fueltypes_yh_p_cy':
            return tech_object.fueltypes_yh_p_cy
        elif attribute_to_get == 'fueltype_share_yh_all_h':
            return tech_object.fueltype_share_yh_all_h
        else:
            sys.exit("Error: Attribute not found")

class Technology(object):
    """Technology Class

    Arguments
    ----------
    tech_name : str
        Technology Name
    data : dict
        All internal and external provided data
    temp_by : array
        Temperatures of base year
    temp_cy : array
        Temperatures of current year
    t_base_heating_by : float
        Base temperature for heating
    t_base_heating_cy : float
        Base temperature current year
    tech_type : str
        Technology type

    Notes
    -----

    """
    def __init__(self, tech_name, assumptions, sim_param, lookups, temp_by, temp_cy, t_base_heating, t_base_heating_cy, tech_type):
        """Contructor
        """
        if tech_name == 'dummy_tech':
            self.tech_name = tech_name
            self.tech_type = tech_type
        else:
            self.tech_name = tech_name
            self.tech_type = tech_type
            self.market_entry = assumptions['technologies'][tech_name]['market_entry']
            self.eff_achieved_factor = assumptions['technologies'][self.tech_name]['eff_achieved']
            self.diff_method = assumptions['technologies'][self.tech_name]['diff_method']

            # Shares of fueltype for every hour for single fueltype
            self.fueltypes_yh_p_cy = self.set_constant_fueltype(
                assumptions['technologies'][tech_name]['fuel_type'], lookups['nr_of_fueltypes'], assumptions['nr_ed_modelled_dates'])

            # Calculate shape per fueltype
            self.fueltype_share_yh_all_h = load_profile.calc_fueltype_share_yh_all_h(
                self.fueltypes_yh_p_cy)

            # --------------------------------------------------------------
            # Base and current year efficiencies depending on technology type
            # --------------------------------------------------------------
            if tech_type == 'heat_pump':
                self.eff_by = tech_related.get_heatpump_eff(
                    temp_by,
                    assumptions['technologies'][tech_name]['eff_by'],
                    t_base_heating)

                self.eff_cy = tech_related.get_heatpump_eff(
                    temp_cy,
                    tech_related.calc_eff_cy(
                        assumptions['technologies'][tech_name]['eff_by'],
                        tech_name,
                        sim_param,
                        assumptions,
                        self.eff_achieved_factor,
                        self.diff_method
                        ),
                    t_base_heating_cy)
            else:
                self.eff_by = assumptions['technologies'][tech_name]['eff_by']
                self.eff_cy = tech_related.calc_eff_cy(
                    assumptions['technologies'][tech_name]['eff_by'],
                    tech_name,
                    sim_param,
                    assumptions,
                    self.eff_achieved_factor,
                    self.diff_method
                    )

    @staticmethod
    def set_constant_fueltype(fueltype, len_fueltypes, nr_of_days=365):
        """Create dictionary with constant single fueltype

        Arguments
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
        fueltypes_yh = np.zeros((len_fueltypes, nr_of_days, 24))

        # Insert for the single fueltype for every hour the share to 1.0
        fueltypes_yh[fueltype] = 1.0

        return fueltypes_yh

class HybridTechnology(object):
    """Hybrid technology which consist of two different technologies

    Arguments
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

    Note
    -----
    - The higher temperature technology is always an electric heat pump
    - The lower temperature (used for peak)
    """
    def __init__(self, enduse, tech_name, assumptions, sim_param, lookups, temp_by, temp_cy, t_base_heating_by, t_base_heating_cy):
        """
        """
        self.enduse = enduse
        self.tech_name = tech_name
        self.tech_type = 'hybrid'

        self.tech_low_temp = assumptions['technologies'][tech_name]['tech_low_temp']
        self.tech_high_temp = assumptions['technologies'][tech_name]['tech_high_temp']

        self.tech_low_temp_fueltype = assumptions['technologies'][self.tech_low_temp]['fuel_type']
        self.tech_high_temp_fueltype =assumptions['technologies'][self.tech_high_temp]['fuel_type']

        self.eff_tech_low_by = assumptions['technologies'][self.tech_low_temp]['eff_by']
        self.eff_tech_high_by = tech_related.get_heatpump_eff(
            temp_by, assumptions['technologies'][self.tech_high_temp]['eff_by'], t_base_heating_by)

        # Efficiencies
        self.eff_tech_low_cy = tech_related.calc_eff_cy(
            assumptions['technologies'][self.tech_low_temp]['eff_by'],
            self.tech_low_temp,
            sim_param,
            assumptions,
            assumptions['technologies'][self.tech_low_temp]['eff_achieved'],
            assumptions['technologies'][self.tech_low_temp]['diff_method']
            )

        eff_tech_high_cy = tech_related.calc_eff_cy(
            assumptions['technologies'][self.tech_high_temp]['eff_by'],
            self.tech_high_temp,
            sim_param,
            assumptions,
            assumptions['technologies'][self.tech_high_temp]['eff_achieved'],
            assumptions['technologies'][self.tech_high_temp]['diff_method']
            )

        self.eff_tech_high_cy = tech_related.get_heatpump_eff(
            temp_cy, eff_tech_high_cy, t_base_heating_cy)

        # Get fraction of service for hybrid technologies for every hour
        self.service_distr_hybrid_h_p = self.service_hybrid_tech_low_high_h_p(
            temp_cy,
            assumptions['technologies'][tech_name]['hybrid_cutoff_temp_low'],
            assumptions['technologies'][tech_name]['hybrid_cutoff_temp_high']
            )

        # Shares of fueltype for every hour for multiple fueltypes
        self.fueltypes_yh_p_cy = self.calc_hybrid_fueltypes_p(lookups['nr_of_fueltypes'])

        self.fueltype_share_yh_all_h = load_profile.calc_fueltype_share_yh_all_h(
            self.fueltypes_yh_p_cy)

        self.eff_by = self.calc_hybrid_eff(
            self.eff_tech_low_by, self.eff_tech_high_by)

        # Current year efficiency (weighted according to service for hybrid technologies)
        self.eff_cy = self.calc_hybrid_eff(
            self.eff_tech_low_cy, self.eff_tech_high_cy)

    @classmethod
    def service_hybrid_tech_low_high_h_p(cls, temp_cy, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
        """Calculate fraction of service for every hour within each hour

        Arguments
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

        Note
        -----
                Within every hour the fraction of service provided by the low-temp technology
        and the high-temp technology is calculated
        """
        tech_low_high_p = {}

        # Substract cutoff temperature from yh temp
        hybrid_service_temp_range = hybrid_cutoff_temp_high - hybrid_cutoff_temp_low
        fast_factor = np.divide(1.0, (hybrid_service_temp_range))

        # Calculate service share (interpolate linearly)
        service_high_tech_p_FAST = fast_factor * (temp_cy - hybrid_cutoff_temp_low)

        # Set service share to 1.0
        service_high_tech_p_FAST[temp_cy > hybrid_cutoff_temp_high] = 1.0

        # Set service share to 0.0
        service_high_tech_p_FAST[temp_cy < hybrid_cutoff_temp_low] = 0.0

        tech_low_high_p['low'] = 1 - service_high_tech_p_FAST
        tech_low_high_p['high'] = service_high_tech_p_FAST

        return tech_low_high_p

    def calc_hybrid_eff(self, eff_tech_low, eff_tech_high):
        """Calculate efficiency for every hour for hybrid technology

        The weighted efficiency for every hour is calculated based
        on fraction of service delieverd with eigher hybrid technology

        Arguments
        ----------
        eff_tech_low : float
            Efficiency of technology operating at lower temperatures
        eff_tech_high : float
            Efficiency of technology operating at higher temperatures

        Return
        ------
        eff_hybrid_yh : array
            Efficiency of hybrid technology

        Note
        -----
        It is assumed that the temperature operating at higher temperatures is a heat pump
        """
        # (Service fraction high tech * efficiency) + (Service fraction low tech * efficiency) (all are 365,24 arrays)
        eff_hybrid_yh = (self.service_distr_hybrid_h_p['high'] * eff_tech_high) + (self.service_distr_hybrid_h_p['low'] * eff_tech_low)

        return eff_hybrid_yh

    def calc_hybrid_fueltypes_p(self, nr_fueltypes):
        """Calculate share of fueltypes for every hour for hybrid technology

        Arguments
        -----------
        nr_fueltypes : int
            Number of fuels

        Return
        ------
        fueltypes_yh : array
            The share of fuel given for the fueltypes (fueltpes, days, hours)

        Note
        -----
        -   The distribution to different fueltypes is only valid within an hour,
            i.e. the fuel is not distributed across the day. This means that within
            an hour the array always sums up to 1 (=100%) across the fueltypes.

        -   The higer temperature technolgy is always a heat pump

        -   Fueltypes of both technologies must be different
        """
        # Calculate hybrid efficiency
        hybrid_eff_yh = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by)

        # Calculate fuel fractions
        fuel_low_h = self.service_distr_hybrid_h_p['low'] / hybrid_eff_yh
        fuel_high_h = self.service_distr_hybrid_h_p['high'] / hybrid_eff_yh

        tot_fuel_h = fuel_low_h + fuel_high_h

        # Assign share of total fuel for respective fueltypes
        fueltypes_yh = np.zeros((nr_fueltypes, 365, 24))
        _var = np.divide(1.0, tot_fuel_h)

        fueltypes_yh[self.tech_low_temp_fueltype] = _var * fuel_low_h
        fueltypes_yh[self.tech_high_temp_fueltype] = _var * fuel_high_h

        return fueltypes_yh
