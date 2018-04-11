"""
Functions related to the technological stock
"""
import numpy as np
from energy_demand.technologies import tech_related

class TechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(
            self,
            name,
            technologies,
            other_enduse_mode_info,
            base_yr,
            curr_yr,
            fueltypes,
            temp_by,
            temp_cy,
            t_base_heating_by,
            potential_enduses,
            t_base_heating_cy,
            enduse_technologies
        ):
        """Constructor of technologies for residential sector

        Arguments
        ----------
        name : str
            Name of technology stock
        technologies : dict
            All technologies and their properties
        other_enduse_mode_info : dict
            Other diffusion information
        base_yr : int
            Base year
        curr_yr : int
            Base year
        fueltypes : dict
            Fueltypes
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
        self.name = name

        self.stock_technologies = create_tech_stock(
            technologies,
            other_enduse_mode_info,
            base_yr,
            curr_yr,
            fueltypes,
            temp_by,
            temp_cy,
            t_base_heating_by,
            t_base_heating_cy,
            potential_enduses,
            enduse_technologies)

    def get_tech(self, name, enduse):
        """Get technology of technology stock

        Arguments
        ----------
        name : str
            Name of technology to get
        enduse : str
            Enduse of technology
        """
        return self.stock_technologies[(name, enduse)]

    def get_tech_attr(self, enduse, name, attribute_to_get, hybrid=False):
        """Get a technology attribute from a technology
        object stored in a list

        Arguments
        ----------
        enduse : string
            Enduse to read technology specified for this enduse
        name : string
            List with stored technologies
        attribute_to_get : string
            Attribute of technology to get

        Return
        -----
        tech_attribute : attribute
            Technology attribute
        """
        tech_object = self.stock_technologies[(name, enduse)]

        if hybrid:
            attribute_value_low_temp = getattr(tech_object.tech_hybrid_low_temp, attribute_to_get)
            attribute_value_high_temp = getattr(tech_object.tech_hybrid_high_temp, attribute_to_get)
            
            return attribute_value_low_temp, attribute_value_high_temp
        else:
            attribute_value = getattr(tech_object, attribute_to_get)

        return attribute_value

    def get_tech_attr_of_attr(self, enduse, tech_name, hybrid_tech, attribute_to_get):
        """Get attribute of self.attribute object
        """
        # Technology
        tech_object = self.stock_technologies[(tech_name, enduse)]

        # Assigned hybrid technology
        tech_object_hybrid_tech = getattr(tech_object, hybrid_tech)

        # Attribute of assigned hybrid technology
        attribute_value = getattr(tech_object_hybrid_tech, attribute_to_get)

        return attribute_value

    def add_tech(
            self,
            name,
            enduse,
            tech_obj
        ):
        """Add technology to technology stock

        Arguments
        ---------
        tech_obj : object
            Technology object
        """
        self.stock_technologies[(name, enduse)] = tech_obj

def create_tech_stock(
        technologies,
        other_enduse_mode_info,
        base_yr,
        curr_yr,
        fueltypes,
        temp_by,
        temp_cy,
        t_base_heating_by,
        t_base_heating_cy,
        enduses,
        enduse_technologies
    ):
    """Create technologies and add to dict with key_tuple

    Arguments
    ----------
    technologies : dict
        All technology assumptions
    other_enduse_mode_info : dict
        Diffusion info
    lookups : dict
        Lookups
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
    enduse_technologies : list
        Technologies of technology stock
    """
    stock_technologies = {}

    for enduse in enduses:
        for technology in enduse_technologies[enduse]:

            tech_type = technologies[technology].tech_type

            if tech_type == 'placeholder_tech':
                # This is placeholder technology a whole enduse
                pass
            elif tech_type == 'hybrid_tech':
                # Hybrid technologies consist of individual technologies
                pass
            else:
                tech_obj = Technology(
                    name=technology,
                    tech_type=technologies[technology].tech_type,
                    fueltype_str=technologies[technology].fueltype_str,
                    eff_achieved=technologies[technology].eff_achieved,
                    diff_method=technologies[technology].diff_method,
                    eff_by=technologies[technology].eff_by,
                    eff_ey=technologies[technology].eff_ey,
                    year_eff_ey=technologies[technology].year_eff_ey,
                    market_entry=technologies[technology].market_entry,
                    tech_max_share=technologies[technology].tech_max_share,
                    other_enduse_mode_info=other_enduse_mode_info,
                    base_yr=base_yr,
                    curr_yr=curr_yr,
                    fueltypes=fueltypes,
                    temp_by=temp_by,
                    temp_cy=temp_cy,
                    t_base_heating_by=t_base_heating_by,
                    t_base_heating_cy=t_base_heating_cy,
                    description=technologies[technology].description)

                stock_technologies[(technology, enduse)] = tech_obj

        # ----------------------------------------------------------------
        # Add for every enduse placeholder technologies for every fueltype
        # ----------------------------------------------------------------
        for fueltype_str in fueltypes:

            placeholder_technology = 'placeholder_tech__{}'.format(fueltype_str)

            # Placeholder technology
            tech_obj = Technology(
                name=placeholder_technology,
                tech_type='placeholder_tech',
                fueltype_str=fueltype_str,
                fueltypes=fueltypes)

            stock_technologies[(placeholder_technology, enduse)] = tech_obj

    return stock_technologies

class HybridTech(object):
    """Hybrid technology system consisting of
    two different technologies

    Arguments
    ---------

    """
    def __init__(
            self,
            name,
            share_service_low=None,
            share_service_high=None,
            tech_hybrid_low_temp=None,
            tech_hybrid_high_temp=None,
            tech_type='hybrid_tech'
        ):
        """Contructor
        """
        self.name = name
        self.tech_type = tech_type

        # Add shares
        tech_hybrid_low_temp.set_tech_attr('share_service', share_service_low)
        tech_hybrid_high_temp.set_tech_attr('share_service', share_service_high)

        self.tech_hybrid_low_temp = tech_hybrid_low_temp
        self.tech_hybrid_high_temp = tech_hybrid_high_temp

        self.hybrid_technologies = ['tech_hybrid_low_temp', 'tech_hybrid_high_temp']

    def get_tech_attr(self, attribute_to_get, value_to_get):
        """Set a technology attribute

        Arguments
        ----------
        attribute_to_get : str
            Attribue to get
        value_to_get : any
            Value to get
        """
        setattr(self, attribute_to_get, value_to_get)

    def get_tech_hybrid_attr(self, hybrid_tech, attribute_to_get):
        """Get attribute of self.attribute object
        """

        # Assigned hybrid technology
        tech_object_hybrid_tech = getattr(self, hybrid_tech)

        # Attribute of assigned hybrid technology
        attribute_value = getattr(tech_object_hybrid_tech, attribute_to_get)

        return attribute_value

class Technology(object):
    """Technology Class

    Arguments
    ----------
    name : str
        The name of a technology
    tech_type : str
        Technology type
    fueltype_str : str
        Fueltype given as string
    eff_achieved : float
        Percentage of how much the potential efficiency improvement is reaslied
    diff_method : str
        How the diffusion occurs (sigmoid or linear)
    eff_by : float
        Base year efficiency
    eff_ey : float
        Future end year efficiency
    year_eff_ey : float
        Year when the efficiency `eff_ey` is fully realised
    market_entry : float
        Year when technology comes on the market
    tech_max_share : float
        Maximum theoretical penetration of technology
    other_enduse_mode_info : dict
        Sigmoid diffusion informaiton
    base_yr : float
        Base year
    curr_yr : float
        Current year
    fueltypes : dict
        Fueltype
    temp_by : array
        Temperatures of base year
    temp_cy : array
        Temperatures of current year
    t_base_heating_by : float
        Base temperature for heating
    t_base_heating_cy : float
        Base temperature current year
    description : str
        Technology description

    Notes
    -----
    * Technologies only coming on the market in the future can be defined by
      defining a future market entry year
    """
    def __init__(
            self,
            name,
            tech_type=None,
            fueltype_str=None,
            eff_achieved=None,
            diff_method=None,
            eff_by=None,
            eff_ey=None,
            year_eff_ey=None,
            market_entry=None,
            tech_max_share=None,
            other_enduse_mode_info=None,
            base_yr=None,
            curr_yr=None,
            fueltypes=None,
            temp_by=None,
            temp_cy=None,
            t_base_heating_by=None,
            t_base_heating_cy=None,
            description=''
        ):
        """Contructor
        """
        self.name = name
        self.tech_type = tech_type
        self.description = description
        self.fueltype_str = fueltype_str
        self.fueltype_int = tech_related.get_fueltype_int(fueltypes, fueltype_str)
        self.eff_achieved_f = eff_achieved
        self.diff_method = diff_method
        self.market_entry = market_entry
        self.tech_max_share = tech_max_share

        if tech_type == 'placeholder_tech':
            self.eff_by = 1.0
            self.eff_cy = 1.0
        elif tech_type == 'heat_pump':
            self.eff_by = tech_related.calc_hp_eff(
                temp_by,
                eff_by,
                t_base_heating_by)

            self.eff_cy = tech_related.calc_hp_eff(
                temp_cy,
                tech_related.calc_eff_cy(
                    base_yr,
                    curr_yr,
                    eff_by,
                    eff_ey,
                    year_eff_ey,
                    other_enduse_mode_info,
                    self.eff_achieved_f,
                    self.diff_method),
                t_base_heating_cy)
        else:
            self.eff_by = eff_by
            self.eff_cy = tech_related.calc_eff_cy(
                base_yr,
                curr_yr,
                eff_by,
                eff_ey,
                year_eff_ey,
                other_enduse_mode_info,
                self.eff_achieved_f,
                self.diff_method)

    def set_tech_attr(self, attribute_to_set, value_to_set):
        """Set a technology attribute

        Arguments
        ----------
        attribute_to_set : str
            Attribue to set
        value_to_set : any
            Value to set
        """
        setattr(self, attribute_to_set, value_to_set)
