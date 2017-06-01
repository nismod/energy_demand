"""The technological stock for every simulation year"""
import sys
import numpy as np
#import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
# pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member

class Technology(object):
    """Technology Class for residential & SERVICE technologies #TODO

    Notes
    -----
    The attribute `shape_peak_yd_factor` is initiated with dummy data and only filled with real data
    in the `Region` Class. The reason is because this factor depends on regional temperatures

    The daily and hourly shape of the fuel used by this Technology
    is initiated with zeros in the 'Technology' attribute. Within the `Region` Class these attributes
    are filled with real values.

    Only the yd shapes are provided on a technology level and not dh shapes

    """
    def __init__(self, tech_name, data, temp_by, temp_cy, year): #, reg_shape_yd, reg_shape_yh, peak_yd_factor):
        """Contructor of Technology

        #TODO: Checke whetear all technologies which are temp dependent are specified for base year efficiency

        Parameters
        ----------
        tech_name : str
            Technology Name
        data : dict
            All internal and external provided data
        temp_cy : array
            Temperatures of current year
        year : float
            Current year
        """
        self.curr_yr = year
        self.tech_name = tech_name

        self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type']

        # -------
        # Hybrid
        # --> Efficiencies depending on temp
        # --> Fueltype depending on temp_cut_off
        # -------

        # -------------------------------
        # Technology specific assumptions
        # -------------------------------
        # Assign base year efficiency depending on technology
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']: # Make temp dependent base year efficiency
            self.eff_by = mf.get_heatpump_eff(
                temp_by,
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['technologies'][self.tech_name]['eff_by'],
                data['assumptions']['t_base_heating_resid']['base_yr']
            )
        else:
            # Constant base year efficiency
            self.eff_by = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])


        self.eff_ey = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_ey'])
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # Attributes generated

        #-- Specific shapes of technologes (filled with dummy data)
        self.shape_yd = np.ones((365, 1))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh
        self.shape_peak_dh = self.get_shape_peak_dh(data)

        # Calculate efficiency in current year
        self.eff_cy = self.calc_efficiency_cy(data, temp_cy)



    def get_shape_peak_dh(self, data):
        """Depending on technology the shape dh is different
        #TODO: MORE INFO
        #TODO:
        """
        # --See wheter the technology is part of a defined enduse and if yes, get technology specific peak shape
        if self.tech_name in data['assumptions']['list_tech_heating_const']:
            
             # Peak curve robert sansom
            shape_peak_dh = np.divide(data['shapes_resid_heating_boilers_dh'][3], np.sum(data['shapes_resid_heating_boilers_dh'][3]))

        elif self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
             # Peak curve robert sansom
            shape_peak_dh = np.divide(data['shapes_resid_heating_heat_pump_dh'][3], np.sum(data['shapes_resid_heating_heat_pump_dh'][3]))

            #elif self-tech_name in data['assumptions']['list_tech_cooling_const']:
            #    self.shape_peak_dh =
            # TODO: DEfine peak curve for cooling

        else:
            # Technology is not part of defined enduse initiate with dummy data
            shape_peak_dh = np.ones((24, ))

        return shape_peak_dh

    def calc_efficiency_cy(self, data, temperatures):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency

        Parameters
        ----------
        data : dict
            All internal and external provided data
        temperatures : array
            Temperatures of current year

        Returns
        -------
        eff_cy_hourly : array
            Array with hourly efficiency over full year

        Notes
        -----
        The development of efficiency improvements over time is assumed to be linear
        This can however be changed with the `diff_method` attribute
        """
        # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
        if self.diff_method == 'linear':
            theor_max_eff = mf.linear_diff(
                data['data_ext']['glob_var']['base_yr'],
                self.curr_yr,
                data['assumptions']['technologies'][self.tech_name]['eff_by'],
                data['assumptions']['technologies'][self.tech_name]['eff_ey'],
                len(data['data_ext']['glob_var']['sim_period'])
            )
        elif self.diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data['data_ext']['glob_var']['base_yr'], self.curr_yr, data['data_ext']['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        # Consider actual achived efficiency
        actual_max_eff = theor_max_eff * self.eff_achieved_factor

        # Differencey in efficiency change
        efficiency_change = actual_max_eff * (data['assumptions']['technologies'][self.tech_name]['eff_ey'] - data['assumptions']['technologies'][self.tech_name]['eff_by'])
        #print("theor_max_eff: " + str(theor_max_eff))
        #print("actual_max_eff: " + str(actual_max_eff))
        #print(data['assumptions']['technologies'][self.tech_name]['eff_ey'] - data['assumptions']['technologies'][self.tech_name]['eff_by'])
        #print("self.eff_achieved_factor:" + str(self.eff_achieved_factor))
        #print("efficiency_change: " + str(efficiency_change))
        # Actual efficiency potential
        #eff_cy = data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change

        # ---------------------------------
        # Technology specific efficiencies
        # ---------------------------------
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
            eff_cy_hourly = mf.get_heatpump_eff(
                temperatures,
                data['assumptions']['heat_pump_slope_assumption'], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change,
                data['assumptions']['t_base_heating_resid']['base_yr']
            )
        elif self.tech_name in data['assumptions']['list_tech_cooling_temp_dep']:
            sys.exit("Error: The technology is not defined in technology list (e.g. temp efficient tech or not")
        else:
            # Non temperature dependent efficiencies
            eff_cy_hourly = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change)

        return eff_cy_hourly

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(self, data, technologies, temp_by, temp_cy):
        """Constructor of technologies for residential sector

        Parameters
        ----------
        data : dict
            All data
        technologies : list
            Technologies of technology stock
        temp_cy : int
            Temperatures of current year
        """

        # Crate all technologies and add as attribute
        for tech_name in technologies:

            # Technology object
            technology_object = Technology(
                tech_name,
                data,
                temp_by,
                temp_cy,
                data['data_ext']['glob_var']['curr_yr'],
            )

            # Set technology object as attribute
            ResidTechStock.__setattr__(
                self,
                tech_name,
                technology_object
            )

    def get_tech_attribute(self, tech, attribute_to_get):
        """Read an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(tech))
        tech_attribute = getattr(tech_object, str(attribute_to_get))

        return tech_attribute

    def set_tech_attribute(self, tech, attribute_to_set, value_to_set):
        """Set an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(tech))
        setattr(tech_object, str(attribute_to_set), value_to_set)

        return
