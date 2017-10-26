"""Functions related to the technological stock
"""
import sys
import numpy as np
from energy_demand.technologies import tech_related

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

        # Select only modelled yeardays
        self.stock_technologies = self.create_tech_stock(
            assumptions, sim_param, lookups,
            temp_by,
            temp_cy,
            t_base_heating_by,
            t_base_heating_cy,
            potential_enduses,
            enduse_technologies
            )

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

        if attribute_to_get == 'tech_fueltype':
            attribute_value = tech_object.tech_fueltype
        elif attribute_to_get == 'tech_type':
            attribute_value = tech_object.tech_type
        elif attribute_to_get == 'tech_fueltype_int':
            attribute_value = tech_object.tech_fueltype_int
        elif attribute_to_get == 'eff_cy':
            attribute_value = tech_object.eff_cy
        elif attribute_to_get == 'eff_by':
            attribute_value = tech_object.eff_by
        elif attribute_to_get == 'tech_low_temp':
            attribute_value = tech_object.tech_low_temp
        elif attribute_to_get == 'tech_low_temp_fueltype':
            attribute_value = tech_object.tech_low_temp_fueltype
        elif attribute_to_get == 'tech_high_temp_fueltype':
            attribute_value = tech_object.tech_high_temp_fueltype
        elif attribute_to_get == 'fueltypes_yh_p_cy':
            attribute_value = tech_object.fueltypes_yh_p_cy
        elif attribute_to_get == 'fueltype_share_yh_all_h':
            attribute_value = tech_object.fueltype_share_yh_all_h
        else:
            sys.exit("Error: Attribute not found {}".format(attribute_to_get))

        return attribute_value

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

                tech_obj = Technology(
                    technology_name,
                    assumptions,
                    sim_param,
                    lookups,
                    temp_by,
                    temp_cy,
                    t_base_heating_by,
                    t_base_heating_cy,
                    tech_type
                )

                stock_technologies[(technology_name, enduse)] = tech_obj

        return stock_technologies

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
            self.tech_fueltype = assumptions['technologies'][tech_name]['fuel_type']
            self.tech_fueltype_int = tech_related.get_fueltype_int(lookups['fueltype'], self.tech_fueltype)
            self.market_entry = assumptions['technologies'][tech_name]['market_entry']
            self.eff_achieved_factor = assumptions['technologies'][self.tech_name]['eff_achieved']
            self.diff_method = assumptions['technologies'][self.tech_name]['diff_method']

            # Shares of fueltype for every hour for single fueltype
            self.fueltypes_yh_p_cy = np.full((
                assumptions['model_yeardays_nrs'], 24), 1, dtype=float)

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
