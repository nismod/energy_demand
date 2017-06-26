"""The technological stock for every simulation year"""
import numpy as np
import energy_demand.main_functions as mf
#pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(self, data, technologies, temp_by, temp_cy, t_base_heating):
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
        for technology in technologies:

            # Technology object
            technology_object = Technology(
                technology,
                data,
                temp_by,
                temp_cy,
                t_base_heating
            )

            # Set technology object as attribute
            ResidTechStock.__setattr__(
                self,
                technology,
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
    def __init__(self, tech_name, data, temp_by, temp_cy, t_base_heating):
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
        self.tech_name = tech_name
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # Base temp assumptions for by and cy
        #t_base_heating = data['assumptions']['rs_t_base_heating']['base_yr']
        ###ss_t_base_heating_by = data['assumptions']['ss_t_base_heating']['base_yr']

        t_base_heating_cy = mf.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')
        ###ss_t_base_heating_cy = mf.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_heating')


        # ss_t_base_heating_cy 
        #TODO:
        # -------
        # Depending on wether only single fueltype or multiple fueltypes (e.g. hybrid technologies)
        # -------
        if self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            """Hybrid efficiencies for residential heating"""

            # Hybrid gas_electricity technology TODO: DEFINE TECHNOLOGY IN ASSUMPTIONS
            if self.tech_name == 'hybrid_gas_elec':
                tech_low_temp = data['assumptions'][self.tech_name]['tech_low_temp']
                tech_high_temp = data['assumptions'][self.tech_name]['tech_high_temp']

                eff_tech_low_by = self.const_eff_yh(data['assumptions']['technologies'][tech_low_temp]['eff_by'])
                eff_tech_high_by = self.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumpt'], data['assumptions']['technologies'][tech_high_temp]['eff_by'], t_base_heating)
                ###ss_eff_tech_high_by = self.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumpt'], data['assumptions']['technologies'][tech_high_temp]['eff_by'], ss_t_base_heating_by)

                # Consider efficincy improvements
                eff_tech_low_cy = self.calc_eff_cy(data['assumptions']['technologies'][tech_low_temp]['eff_by'], tech_low_temp, data)
                eff_tech_high_cy = self.calc_eff_cy(data['assumptions']['technologies'][tech_high_temp]['eff_by'], tech_high_temp, data)

                # efficiencies
                eff_tech_low_cy = self.const_eff_yh(eff_tech_low_cy)
                eff_tech_high_cy = self.get_heatpump_eff(temp_cy, data['assumptions']['hp_slope_assumpt'], eff_tech_high_cy, t_base_heating_cy)
                ###ss_eff_tech_high_cy = self.get_heatpump_eff(temp_cy, data['assumptions']['hp_slope_assumpt'], eff_tech_high_cy, ss_t_base_heating_by)
            
            #if self.tech_name == 'hybrid_whatever':

            # Get fraction of service for hybrid technologies for every hour
            self.service_distr_hybrid_h_p_cy = self.service_hybrid_tech_low_high_h_p(
                temp_cy,
                data['assumptions'][self.tech_name]['hybrid_cutoff_temp_low'],
                data['assumptions'][self.tech_name]['hybrid_cutoff_temp_high']
                )

            # Get fraction of fueltypes for every hour
            self.fueltypes_yh_p_cy = self.calc_hybrid_fueltype(
                data['nr_of_fueltypes'],
                eff_tech_low_cy,
                eff_tech_high_cy,
                data['assumptions']['technologies'][tech_low_temp]['fuel_type'], #fueltype_low_temp,
                data['assumptions']['technologies'][tech_high_temp]['fuel_type'])
            
            '''self.ss_fueltypes_yh_p_cy = self.calc_hybrid_fueltype(
                data['nr_of_fueltypes'],
                eff_tech_low_cy,
                ss_eff_tech_high_cy,
                data['assumptions']['technologies'][tech_low_temp]['fuel_type'], #fueltype_low_temp,
                data['assumptions']['technologies'][tech_high_temp]['fuel_type'])
            '''
        else:
            # Shares of fueltype for every hour for single fueltype
            self.fueltypes_yh_p_cy = self.set_constant_fueltype(data['assumptions']['technologies'][self.tech_name]['fuel_type'], data['nr_of_fueltypes'])

        # -------------------------------
        # Base and current year efficiencies
        # -------------------------------

        # Depending what sort of technology, make temp dependent, hybrid or constant efficiencies
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
            self.eff_by = self.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumpt'], data['assumptions']['technologies'][self.tech_name]['eff_by'], t_base_heating)
            self.eff_cy = self.get_heatpump_eff(temp_cy, data['assumptions']['hp_slope_assumpt'], self.calc_eff_cy(data['assumptions']['technologies'][self.tech_name]['eff_by'], self.tech_name, data), t_base_heating_cy)

        elif self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            self.eff_by = self.calc_hybrid_eff(eff_tech_low_by, eff_tech_high_by)
            self.eff_cy = self.calc_hybrid_eff(eff_tech_low_cy, eff_tech_high_cy) # Current year efficiency (weighted according to service for hybrid technologies)

            ##elif self.tech_name in data['assumptions']['list_tech_cooling_temp_dep']:
            ##sys.exit("Error: The technology is not defined in technology list (e.g. temp efficient tech or not")
        else:
            self.eff_by = self.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])
            self.eff_cy = self.const_eff_yh(self.calc_eff_cy(data['assumptions']['technologies'][self.tech_name]['eff_by'], self.tech_name, data))

        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_types_shares_yd = self.convert_yh_to_yd_fueltype_shares(data['nr_of_fueltypes'], self.fueltypes_yh_p_cy)
        ###self.ss_fuel_types_shares_yd = self.convert_yh_to_yd_fueltype_shares(data['nr_of_fueltypes'], self.ss_fueltypes_yh_p_cy)
    
        # -------------------------------
        # FUEL Shapes (not service)
        #  Specific shapes of technologes filled with dummy data. Gets filled in Region Class
        # -------------------------------
        self.shape_yd = np.ones((365))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh where not read from values directly
        self.shape_peak_dh = self.get_shape_peak_dh(data)

    def get_heatpump_eff(self, temp_yr, m_slope, b, t_base_heating):
        """Calculate efficiency according to temperatur difference of base year

        For every hour the temperature difference is calculated and the efficiency of the heat pump calculated
        based on efficiency assumptions

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

                eff_hp_yh[day][h_nr] = mf.eff_heat_pump(m_slope, h_diff, b)

                #--Testing
                assert eff_hp_yh[day][h_nr] > 0

        return eff_hp_yh

    def service_hybrid_tech_low_high_h_p(self, temp_cy, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
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
        tech_low_high_p : dict
            Share of lower and higher service fraction for every hour

        Info
        ----
        TODO: Plot chart in INDESIGN OF SHARE OF USAGE FOR HYBRID TECH
        """
        tech_low_high_p = {}

        for day, temp_d in enumerate(temp_cy):
            tech_low_high_p[day] = {}

            for hour, temp_h in enumerate(temp_d):

                # Get share of service of high temp technology
                service_high_tech_p = self.fraction_service_high_temp(temp_h, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high)

                # Calculate share of service of low temp technology
                service_low_tech_p = 1 - service_high_tech_p

                tech_low_high_p[day][hour] = {
                    'low': service_low_tech_p,
                    'high': service_high_tech_p
                    }

        return tech_low_high_p

    def fraction_service_high_temp(self, current_temp, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high):
        """Calculate percent of service for high-temp technology based on assumptions of hybrid technology

        Parameters
        ----------
        current_temp : float
            Temperature to find fraction

        Info
        -----
        hybrid_cutoff_temp_low : float
            Lower temperature limit where only lower technology is operated with 100%
        hybrid_cutoff_temp_high : float
            Higher temperature limit where only lower technology is operated with 100%

        Return
        ------
        fraction_current_temp : float
            Fraction of higher temperature technology
            It is assumed that share of service of tech_high at hybrid_cutoff_temp_high == 100%
        """
        if current_temp >= hybrid_cutoff_temp_high:
            fraction_current_temp = 1.0
        elif current_temp < hybrid_cutoff_temp_low:
            fraction_current_temp = 0.0
        else:
            if hybrid_cutoff_temp_low < 0:
                temp_diff = hybrid_cutoff_temp_high + abs(hybrid_cutoff_temp_low)
                temp_diff_current_temp = current_temp + abs(hybrid_cutoff_temp_low)
            else:
                temp_diff = hybrid_cutoff_temp_high - hybrid_cutoff_temp_low
                temp_diff_current_temp = current_temp - hybrid_cutoff_temp_low

            # Calculate service share of high temp technology
            fraction_current_temp = np.divide(1.0, temp_diff) * temp_diff_current_temp

        return fraction_current_temp

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
        eff_yh = np.full((365, 24), input_eff)

        return eff_yh

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
        temp_yr : dict
            Hourly temperatures
        m_slope : float
            Heat pumps slope assumptions
        t_base_heating : float
            Base temperatures for heating

        Return
        ------
        var1 : dict
            Blabla

        Info
        -----
        It is assumed that the temperature operating at higher temperatures is a heat pump
        """
        eff_hybrid_yh = np.zeros((365, 24))

        for day in range(365):
            for hour in range(24):

                # Fraction of service of low and high temp technology
                service_high_p = self.service_distr_hybrid_h_p_cy[day][hour]['high']
                service_low_p = self.service_distr_hybrid_h_p_cy[day][hour]['low']

                # Efficiencies
                eff_low = eff_tech_low[day][hour]
                eff_high = eff_tech_high[day][hour]

                # Calculate weighted efficiency
                eff_hybrid_yh[day][hour] = (service_high_p * eff_high) + (service_low_p * eff_low)

                assert eff_hybrid_yh[day][hour] >= 0

        return eff_hybrid_yh

    def convert_yh_to_yd_fueltype_shares(self, nr_fueltypes, fueltypes_yh_p_cy):
        """Take share of fueltypes for every yh and calculate the mean share of every day

        The daily mean is calculated for every row of an array.

        Parameters
        ----------
        nr_fueltypes : int
            Number of defined fueltypes

        Return
        ------
        fuel_yd_shares : array
            Yd shape fuels

        Example
        -------
        array((8fueltype, 365days, 24)) is converted into array((8fueltypes, 365days with average))
        """
        fuel_yd_shares = np.zeros((nr_fueltypes, 365))

        for fueltype, fueltype_yh in enumerate(fueltypes_yh_p_cy):
            fuel_yd_shares[fueltype] = fueltype_yh.mean(axis=1) #Calculate mean for every row in array

        #Testing
        np.testing.assert_almost_equal(np.sum(fuel_yd_shares), 365, decimal=3, err_msg='Error XY')

        return fuel_yd_shares

    def calc_hybrid_fueltype(self, nr_fueltypes, eff_tech_low_cy, eff_tech_high_cy, fueltype_low_temp, fueltype_high_temp):
        """Calculate share of fueltypes for every hour for hybrid technology

        Parameters
        -----------
        temp_yr : array
            Temperature data
        t_base_heating : float
            Base temperature for residential heating
        m_slope : float
            Slope of heat pump
        nr_fueltypes : int
            Number of fuels

        Return
        ------
        fueltypes_yh : array (fueltpes, days, hours)
            The share of fuel given for the fueltypes

        Info
        -----
        The distribution to different fueltypes is only valid within an hour,
        i.e. the fuel is not distributed across the day. This means that within an hour the array
        always sums up to 1 (=100%) across the fueltypes.

        The higer temperature technolgy is always a heat pump

        TODO: SEE if based on daily share of each service the hourly distribution can be made: Improve
        fuel = Energy service / efficiency
        """
        fueltypes_yh = np.zeros((nr_fueltypes, 365, 24))

        for day in range(365):
            for hour in range(24):

                # Fraction of service of low and high temp technology
                service_high_h_p = self.service_distr_hybrid_h_p_cy[day][hour]['high']
                service_low_h_p = self.service_distr_hybrid_h_p_cy[day][hour]['low']

                # Efficiency of low and high tech
                eff_tech_low = eff_tech_low_cy[day][hour]
                eff_tech_high_hp = eff_tech_high_cy[day][hour]

                dummy_service = 100.0

                # Calculate fuel fractions: (frac_tech * dummy_service) / eff_tech
                if service_low_h_p > 0:
                    service_low_h = dummy_service * service_low_h_p
                    fuel_low_h = np.divide(service_low_h, eff_tech_low)
                else:
                    fuel_low_h = 0

                if service_high_h_p > 0:
                    service_high_h = dummy_service * service_high_h_p
                    fuel_high_h = np.divide(service_high_h, eff_tech_high_hp)
                else:
                    fuel_high_h = 0

                tot_fuel_h = fuel_low_h + fuel_high_h

                # The the low and high temp tech have same fueltype
                if fueltype_low_temp == fueltype_high_temp:
                    fueltypes_yh[fueltype_low_temp][day][hour] = 1.0
                else:
                    # Assign share of total fuel for respective fueltypes
                    fueltypes_yh[fueltype_low_temp][day][hour] = np.divide(1, tot_fuel_h) * fuel_low_h
                    fueltypes_yh[fueltype_high_temp][day][hour] = np.divide(1, tot_fuel_h) * fuel_high_h

        # Testing
        np.testing.assert_almost_equal(np.sum(fueltypes_yh), 365 * 24, decimal=3, err_msg='ERROR XY')

        return fueltypes_yh

    def get_shape_peak_dh(self, data):
        """Depending on technology the shape dh is different
        #TODO: MORE INFO
        #TODO: PEAK OF HYBRID TECHNOLOGIEs
        """
        # --See wheter the technology is part of a defined enduse and if yes, get technology specific peak shape
        if self.tech_name in data['assumptions']['list_tech_heating_const']:

             # Peak curve robert sansom
            shape_peak_dh = np.divide(data['rs_shapes_heating_boilers_dh'][3], np.sum(data['rs_shapes_heating_boilers_dh'][3]))

        elif self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:
             # Peak curve robert sansom
            shape_peak_dh = np.divide(data['rs_shapes_heating_heat_pump_dh'][3], np.sum(data['rs_shapes_heating_heat_pump_dh'][3]))

        elif self.tech_name in data['assumptions']['list_tech_heating_hybrid']: # if hybrid technology
            #TODO: WRONG: THE PEAK SHAPE FOR HYBRID TECH IS REGIONAL DEPENDENT AND IS TAKEN from shape_yh directly for peak day
            # The shape is assigned in region from peak day #TODO CHECK
            shape_peak_dh = np.ones((24))
            #elif self-tech_name in data['assumptions']['list_tech_cooling_const']:
            #    self.shape_peak_dh =
            # TODO: DEfine peak curve for cooling
        else:
            # Technology is not part of defined enduse initiate with dummy data
            shape_peak_dh = np.ones((24))

        return shape_peak_dh

    def calc_eff_cy(self, eff_by, technology, data):
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
                data['base_yr'],
                data['curr_yr'],
                data['assumptions']['technologies'][technology]['eff_by'],
                data['assumptions']['technologies'][technology]['eff_ey'],
                len(data['sim_period'])
            )
        elif self.diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data['base_yr'], data['curr_yr'], data['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        # Consider actual achived efficiency
        actual_max_eff = theor_max_eff * self.eff_achieved_factor

        # Differencey in efficiency change
        efficiency_change = actual_max_eff * (data['assumptions']['technologies'][technology]['eff_ey'] - data['assumptions']['technologies'][technology]['eff_by'])

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        return eff_cy
