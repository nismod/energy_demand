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
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']

        self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type']
        ##self.fuel_type = mf.constant_fueltype(data['assumptions']['technologies'][self.tech_name]['fuel_type'])

        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # -------
        # Hybrid
        # --> Efficiencies depending on temp
        # --> Fueltype depending on temp_cut_off
        # -------

        hybrid_tech_list = ['hybrid_gas_elec']
        if self.tech_name in hybrid_tech_list:
            """ Hybrid efficiencies
            - Define temp_switch and share of service (e.g. 5 degree, 60%, 6 Degree: 20%, 7 degree: 20%)
            - Define daily curve with technology mix in percent for every hour
            - Define average effiiciency depending on tech switch
            - define fuel share for every hour


            """
            if self.tech_name == 'hybrid_gas_elec':
                tech_high_temp = 'av_heat_pump_electricity'
                tech_low_temp = 'boiler_gas'
                fueltype_low_temp = data['lu_fueltype']['gas']
                fueltype_ligh_temp = data['lu_fueltype']['electricity']

            self.hybrid_temp_cut_off = 1 # Temperature where fueltypes are switched

            self.eff_cy = self.calc_hybrid_eff(
                temp_cy,
                self.hybrid_temp_cut_off,
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['t_base_heating_resid']['base_yr'],
                data['assumptions']['technologies'][tech_low_temp]['eff_by'], # Boiler efficiency
                data['assumptions']['technologies'][tech_high_temp]['eff_by'] # Heat pump efficiency
            )

            # Fueltype for every hour #Make possible that different fueltypes fueltype: {h1: {typA: 50%, typB: 40%}, ....}
            self.fueltype = self.calc_hybrid_fueltype(temp_cy, self.hybrid_temp_cut_off, fueltype_low_temp, fueltype_ligh_temp)

            # Shape
            # d_h --> IS different for every day or fueltype. --> Iterate days and calculate share of service for fueltype
            #--> Distribute share of fueltype to technology (is wrong) (e.g. 20% boiler, 80% hp)



        # -------------------------------
        # Efficiencies
        # -------------------------------
        # --Base year
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']: # Make temp dependent base year efficiency
            self.eff_by = mf.get_heatpump_eff(
                temp_by, #Base year temperatures
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['technologies'][self.tech_name]['eff_by'],
                data['assumptions']['t_base_heating_resid']['base_yr']
            )
        else:
            # Constant base year efficiency
            self.eff_by = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])

        # --Current year
        self.eff_cy = self.calc_efficiency_cy(data, temp_cy)

        # -------------------------------
        # Shapes
        # -------------------------------

        #-- Specific shapes of technologes filled with dummy data. Gets filled in Region Class
        self.shape_yd = np.ones((365, 1))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh
        self.shape_peak_dh = self.get_shape_peak_dh(data)

    def calc_hybrid_eff(self, temp_yr, hybrid_temp_cut_off, m_slope, t_base_heating, eff_boiler, eff_hp):
        """Calculate efficiency for every hour for hybrid technology
        """
        eff_hybrid_yh = np.zeros((365, 24))

        for day, temp_day in enumerate(temp_yr):
            for h_nr, temp_h in enumerate(temp_day):
                if t_base_heating < temp_h:
                    h_diff = 0
                else:
                    if temp_h < 0: #below zero temp
                        h_diff = t_base_heating + abs(temp_h)
                    else:
                        h_diff = abs(t_base_heating - temp_h)

                # Test which efficieny of hybrid tech is used
                if temp_h <= hybrid_temp_cut_off:
                    #print("----Boiler Efficiency"  + str(eff_boiler))
                    efficiency = eff_boiler #Boiler efficiency
                else:
                    #print("----HP     Efficiency "  + str(m_slope * h_diff + eff_hp))
                    efficiency = m_slope * h_diff + eff_hp # Heat pump efficiency

                eff_hybrid_yh[day][h_nr] = efficiency

        return eff_hybrid_yh

    def calc_hybrid_fueltype(self, temp_yr, hybrid_temp_cut_off, fueltype_low_temp, fueltype_high_temp):
        """Calculate efficiency for every hour for hybrid technology
        """
        fueltype_yh = np.zeros((365, 24))

        for day, temp_day in enumerate(temp_yr):
            for h_nr, temp_h in enumerate(temp_day):

                # Test which efficieny of hybrid tech is used
                if temp_h <= hybrid_temp_cut_off:
                    fueltype_yh[day][h_nr] = fueltype_low_temp
                else:
                    fueltype_yh[day][h_nr] = fueltype_high_temp

        return fueltype_yh

    def get_shape_peak_dh(self, data):
        """Depending on technology the shape dh is different
        #TODO: MORE INFO
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
