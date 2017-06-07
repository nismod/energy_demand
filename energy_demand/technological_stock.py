"""The technological stock for every simulation year"""
import sys
import numpy as np
import time
import energy_demand.main_functions as mf
#import energy_demand.technological_stock_functions as tf
# pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213

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
    def __init__(self, tech_name, data, temp_by, temp_cy, curr_yr): #, reg_shape_yd, reg_shape_yh, peak_yd_factor):
        """Contructor of Technology

        # TODO: CALCULATE CURRENT EFFICIENY EAR AND BASE YEAR EFFICIENCY IN SAME STROKE
        Parameters
        ----------
        tech_name : str
            Technology Name
        data : dict
            All internal and external provided data
        temp_cy : array
            Temperatures of current year
        curr_yr : float
            Current year
        """
        self.tech_name = tech_name
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # -------
        # Depending on wheather only single fueltype or multiple fueltypes (hybrid technologies)
        # -------
        if self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            """ Hybrid efficiencies for residential heating
            """
            # Hybrid gas_electricity technology TODO: DEFINE TECHNOLOGY IN ASSUMPTIONS
            if self.tech_name == 'hybrid_gas_elec':
                self.tech_high_temp = data['assumptions']['hybrid_gas_elec']['tech_high_temp']
                self.tech_low_temp = data['assumptions']['hybrid_gas_elec']['tech_low_temp']
                self.hybrid_cutoff_temp_low = data['assumptions']['hybrid_gas_elec']['hybrid_cutoff_temp_low']
                self.hybrid_cutoff_temp_high = data['assumptions']['hybrid_gas_elec']['hybrid_cutoff_temp_high']
                
                self.fueltype_low_temp = data['assumptions']['technologies'][self.tech_low_temp]['fuel_type']
                self.fueltype_high_temp = data['assumptions']['technologies'][self.tech_high_temp]['fuel_type']
                
                self.eff_tech_low_by = data['assumptions']['technologies'][self.tech_low_temp]['eff_by']
                self.eff_tech_high_by = data['assumptions']['technologies'][self.tech_high_temp]['eff_by']

                self.eff_tech_low_cy = self.calc_eff_cy(self.eff_tech_low_by, self.tech_low_temp, data, curr_yr)
                self.eff_tech_high_cy = self.calc_eff_cy(self.eff_tech_high_by, self.tech_high_temp, data, curr_yr)

            #if self.tech_name == 'hybrid_whatever':

            # Get fraction of service for hybrid technologies for every hour
            self.service_hybrid_h_p_cy = self.service_hybrid_tech_low_high_h_p(temp_cy)

            # Get fraction of fueltypes for every hour
            self.fueltypes_p_cy = self.calc_hybrid_fueltype(
                temp_cy,
                data['assumptions']['t_base_heating_resid']['base_yr'],
                data['assumptions']['hp_slope_assumpt'],
                len(data['lu_fueltype'])
            )

        else:
            # Shares of fueltype for every hour for single fueltype
            self.fueltypes_p_cy = self.set_constant_fueltype(data['assumptions']['technologies'][self.tech_name]['fuel_type'], len(data['lu_fueltype']))

        # -------------------------------
        # Base and current year efficiencies
        # -------------------------------
        t_base_heating_resid_cy = mf.t_base_sigm(data['data_ext']['glob_var']['base_yr'], data['assumptions'], data['data_ext']['glob_var']['base_yr'], data['data_ext']['glob_var']['end_yr'], 't_base_heating_resid')

        # Depending what sort of technology, make temp dependent, hybrid or constant efficiencies
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
            self.eff_by = self.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumpt'], data['assumptions']['technologies'][self.tech_name]['eff_by'], data['assumptions']['t_base_heating_resid']['base_yr'])
            
            self.eff_cy = self.get_heatpump_eff(
                temp_cy,
                data['assumptions']['hp_slope_assumpt'],
                self.calc_eff_cy(data['assumptions']['technologies'][self.tech_name]['eff_by'], self.tech_name, data, curr_yr),
                t_base_heating_resid_cy)

        elif self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            self.eff_by = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by, temp_by, data['assumptions']['hp_slope_assumpt'], data['assumptions']['t_base_heating_resid']['base_yr'])
            # Current year efficiency (weighted according to service for hybrid technologies)
            self.eff_cy = self.calc_hybrid_eff(self.eff_tech_low_cy, self.eff_tech_high_cy, temp_cy, data['assumptions']['hp_slope_assumpt'], t_base_heating_resid_cy)

            ##elif self.tech_name in data['assumptions']['list_tech_cooling_temp_dep']:
            ##sys.exit("Error: The technology is not defined in technology list (e.g. temp efficient tech or not")
        else:
            self.eff_by = self.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])

            # CURRENT YEAR EFFICIENCY
            self.eff_cy = self.const_eff_yh(
                self.calc_eff_cy(data['assumptions']['technologies'][self.tech_name]['eff_by'], self.tech_name, data, curr_yr))

        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_types_share_yd = self.convert_yh_to_yd_shares(len(data['lu_fueltype']))

        # -------------------------------
        # Shapes
        #  Specific shapes of technologes filled with dummy data. Gets filled in Region Class
        # -------------------------------
        self.shape_yd = np.ones((365))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh
        self.shape_peak_dh = self.get_shape_peak_dh(data)

    def get_heatpump_eff(self, temp_yr, m_slope, b, t_base_heating):
        """Calculate efficiency according to temperatur difference of base year

        For every hour the temperature difference is calculated and the efficiency of the heat pump calculated
        based on efficiency assumptions

        #TODO: EITHER ASSUME DIFFERENT HEAT PUMP TECHNOLOGIES OR HEAT PUMP MIX TO CALCULATE EFFICIENCY

        Parameters
        ----------
        temp_yr : array
            Temperatures for every hour in a year (365, 24)
        m_slope : float
            Slope of efficiency of heat pump for different temperatures
        b : float
            Intercept (TODO: define for slope...(check in excel for GSHP and HSP))
        t_base_heating : float
            Base temperature for heating

        Return
        ------
        eff_hp_yh : array (365, 24)
            Efficiency for every hour in a year

        Info
        -----
        The efficiency assumptions of the heat pump are taken from Staffell et al. (2012).

        Staffell, I., Brett, D., Brandon, N., & Hawkes, A. (2012). A review of domestic heat pumps.
        Energy & Environmental Science, 5(11), 9291. https://doi.org/10.1039/c2ee22653g
        """
        eff_hp_yh = np.zeros((365, 24))

        for day, temp_day in enumerate(temp_yr):
            for h_nr, temp_h in enumerate(temp_day):
                if t_base_heating < temp_h:
                    h_diff = 0
                else:
                    if temp_h < 0: #below zero temp
                        h_diff = t_base_heating + abs(temp_h)
                    else:
                        h_diff = abs(t_base_heating - temp_h)
                eff_hp_yh[day][h_nr] = m_slope * h_diff + b #[day][h_nr]

                #--Testing
                assert eff_hp_yh[day][h_nr] > 0

        return eff_hp_yh

    def service_hybrid_tech_low_high_h_p(self, temp_cy): #, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
        """Calculate fraction of service for every hour within each hour

        Within every hour the fraction of service provided by the low-temp technology
        and the high-temp technology is calculated

        Parameters
        ----------
        temp_cy : array
            Temperature of current year
        
        Info
        ----
        hybrid_cutoff_temp_low : int
            Temperature cut-off criteria (blow this temp, 100% service provided by lower temperature technology)
        hybrid_cutoff_temp_high : int
            Temperature cut-off criteria (above this temp, 100% service provided by higher temperature technology)

        Return
        ------
        fraction_high_low : dict
            Share of lower and higher service fraction for every hour
        """
        fraction_high_low = {}

        for day, temp_d in enumerate(temp_cy):
            fraction_high_low[day] = {}

            for hour, temp_h in enumerate(temp_d):
                service_high_tech_p = self.fraction_service_high_temp(self.hybrid_cutoff_temp_low, self.hybrid_cutoff_temp_high, temp_h)
                service_low_tech_p = 1 - service_high_tech_p
                fraction_high_low[day][hour] = {'low': service_low_tech_p, 'high': service_high_tech_p}

        return fraction_high_low

    def fraction_service_high_temp(self, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high, current_temp):
        """Calculate percent of service for high-temp technology based on assumptions of hybrid technology

        Parameters
        ----------
        hybrid_cutoff_temp_low : float
            Lower temperature limit where only lower technology is operated with 100%
        hybrid_cutoff_temp_high : float
            Higher temperature limit where only lower technology is operated with 100%
        current_temp : float
            Temperature to find fraction

        Return
        ------
        fraction_currenttemp : float
            Fraction of higher temperature technology
            It is assumed that share of service of tech_high at hybrid_cutoff_temp_high == 100%
        """
        if current_temp >= hybrid_cutoff_temp_high:
            fraction_currenttemp = 1.0
        elif current_temp < hybrid_cutoff_temp_low:
            fraction_currenttemp = 0.0
        else:
            if hybrid_cutoff_temp_low < 0:
                temp_diff = hybrid_cutoff_temp_high + abs(hybrid_cutoff_temp_low)
                temp_diff_currenttemp = current_temp + abs(hybrid_cutoff_temp_low)
            else:
                temp_diff = hybrid_cutoff_temp_high - hybrid_cutoff_temp_low
                temp_diff_currenttemp = current_temp - hybrid_cutoff_temp_low

            # Calculate share of high temp
            fraction_currenttemp = np.divide(1.0, temp_diff) * temp_diff_currenttemp

        return fraction_currenttemp

    def set_constant_fueltype(self, fueltype, len_fueltypes):
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

    def const_eff_yh(self, input_eff):
        """Assing a constant efficiency to every hour in a year

        Parameters
        ----------
        input_eff : float
            Efficiency of a technology

        Return
        ------
        eff_yh : array
            Array with efficency for every hour in a year (365,24)
        """
        eff_yh = np.zeros((365, 24))
        eff_yh += input_eff

        return eff_yh

    def calc_hybrid_eff(self, eff_tech_low, eff_tech_high, temp_yr, m_slope, t_base_heating):
        """Calculate efficiency for every hour for hybrid technology
        """
        eff_hybrid_yh = np.zeros((365, 24))

        for day, temp_day in enumerate(temp_yr):
            for hour, temp_h in enumerate(temp_day):
                if t_base_heating < temp_h:
                    h_diff = 0
                else:
                    if temp_h < 0: #below zero temp
                        h_diff = t_base_heating + abs(temp_h)
                    else:
                        h_diff = abs(t_base_heating - temp_h)

                # Fraction of service of low and high temp technology
                service_high_p = self.service_hybrid_h_p_cy[day][hour]['high']
                service_low_p = self.service_hybrid_h_p_cy[day][hour]['low']

                # Efficiencies
                eff_tech_low = eff_tech_low
                eff_tech_hp = m_slope * h_diff + eff_tech_high #Same as for heat pumpTODO: MAYBE NOT ALWAY HEAT PUMP. Make more complex

                # Calculate weighted efficiency
                eff_hybrid_yh[day][hour] = (service_high_p * eff_tech_hp) + (service_low_p * eff_tech_low)

                assert eff_tech_hp >= 0

        return eff_hybrid_yh

    def convert_yh_to_yd_shares(self, len_fueltypes):
        """Take shares of fueltypes for every hour and calculate share of fueltypes of a day
        """
        fuely_yd_shares = np.zeros((len_fueltypes, 365))

        for fueltype, fueltype_yh in enumerate(self.fueltypes_p_cy):
            fuely_yd_shares[fueltype] = fueltype_yh.mean(axis=1) # Calculate daily mean for every row

        return fuely_yd_shares

    def calc_hybrid_fueltype(self, temp_yr, t_base_heating, m_slope, len_fueltypes):
        """Calculate share of fueltypes for every hour for hybrid technology

        Here the distribution to different fueltypes is only valid within an hour (e.g. the fuel is not distributed across
        the day)

        TODO: SEE if based on daily share of each service the hourly distribution can be made: Improve
        uel = Energy service / efficiency
        """
        fueltypes_yh = np.zeros((len_fueltypes, 365, 24))

        for day, temp_day in enumerate(temp_yr):
            for hour, temp_h in enumerate(temp_day):
                if t_base_heating < temp_h:
                    h_diff = 0
                else:
                    if temp_h < 0: #below zero temp
                        h_diff = t_base_heating + abs(temp_h)
                    else:
                        h_diff = abs(t_base_heating - temp_h)

                # Fraction of service of low and high temp technology
                service_high_p = self.service_hybrid_h_p_cy[day][hour]['high']
                service_low_p = self.service_hybrid_h_p_cy[day][hour]['low']

                # Efficiencies m_slope, eff_tech_high, eff_tech_low
                # Calculate current year efficiency
                eff_tech_low = self.eff_tech_low_cy
                eff_tech_high_hp = m_slope * h_diff + self.eff_tech_high_cy #TODO: MAYBE NOT ALWAY HEAT PUMP. Make more complex

                dummy_service = 100.0

                # Calculate fuel fractions: (frac_tech * dummy_service) / eff_tech
                if service_low_p > 0:
                    service_low_p = dummy_service * service_low_p
                    fuel_low = np.divide(service_low_p, eff_tech_low)
                else:
                    fuel_low = 0

                if service_high_p > 0:
                    service_high_p = dummy_service * service_high_p
                    fuel_high = np.divide(service_high_p, eff_tech_high_hp)
                else:
                    fuel_high = 0

                tot_fuel = fuel_low + fuel_high

                # Assign share of total fuel for respective fueltypes
                fueltypes_yh[self.fueltype_low_temp][day][hour] = np.divide(1, tot_fuel) * fuel_low
                fueltypes_yh[self.fueltype_high_temp][day][hour] = np.divide(1, tot_fuel) * fuel_high

        return fueltypes_yh

    def get_shape_peak_dh(self, data):
        """Depending on technology the shape dh is different
        #TODO: MORE INFO
        #TODO: PEAK OF HYBRID TECHNOLOGIEs
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
            shape_peak_dh = np.ones((24))

        return shape_peak_dh

    def calc_eff_cy(self, eff_by, technology, data, curr_yr):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency

        Parameters
        ----------
        data : dict
            All internal and external provided data

        Returns
        -------
        eff_cy : array
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
                curr_yr,
                data['assumptions']['technologies'][technology]['eff_by'],
                data['assumptions']['technologies'][technology]['eff_ey'],
                len(data['data_ext']['glob_var']['sim_period'])
            )
        elif self.diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data['data_ext']['glob_var']['base_yr'], curr_yr, data['data_ext']['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        # Consider actual achived efficiency
        actual_max_eff = theor_max_eff * self.eff_achieved_factor

        # Differencey in efficiency change
        efficiency_change = actual_max_eff * (data['assumptions']['technologies'][technology]['eff_ey'] - data['assumptions']['technologies'][technology]['eff_by'])
        #print("theor_max_eff: " + str(theor_max_eff))
        #print("actual_max_eff: " + str(actual_max_eff))
        #print(data['assumptions']['technologies'][self.tech_name]['eff_ey'] - data['assumptions']['technologies'][self.tech_name]['eff_by'])
        #print("self.eff_achieved_factor:" + str(self.eff_achieved_factor))
        #print("efficiency_change: " + str(efficiency_change))
        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change
        return eff_cy

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
