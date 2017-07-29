"""The technological stock for every simulation year"""
import sys
import numpy as np
from energy_demand.scripts_technologies import diffusion_technologies as diffusion
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_technologies import technologies_related
#pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213

class TechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model.
    """
    def __init__(self, data, temp_by, temp_cy, t_base_heating, potential_enduses, t_base_heating_cy, enduse_technologies, sectors):
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
        for enduse in potential_enduses:
            list_with_technologies_per_enduse_all_sectors = []
        #   print("       ...technology {}      {}".format(enduse, enduse_technologies[enduse]))

        #    for sector in sectors:
            for technology in enduse_technologies[enduse]:
                    #print("         ...{}   {}".format(sector, technology))
                    # Technology object
                    technology_object = Technology(
                        enduse,
                        #sector,
                        technology,
                        data,
                        temp_by,
                        temp_cy,
                        t_base_heating,
                        potential_enduses,
                        t_base_heating_cy
                    )
                    list_with_technologies_per_enduse_all_sectors.append(technology_object)

            # Set technology object as attribute
            TechStock.__setattr__(
                self,
                enduse,
                list_with_technologies_per_enduse_all_sectors
            )

    def get_tech_attr(self, enduse, tech, attribute_to_get):
        """Get a technology attribute from a technology object stored in a list

        Parameters
        ----------
        enduse : string
            Enduse to read technology specified for this enduse
        tech : list
            List with stored technologies
        attribute_to_get : string
            Attribute of technology to get

        Return
        -----
        tech_attribute : attribute
            Technology attribute
        """
        tech_objects = getattr(self, str(enduse))
        #try:
        for tech_object in tech_objects:
            if tech_object.tech_name == tech: # and tech_object.sector == sector:
                tech_attribute = getattr(tech_object, str(attribute_to_get))

        return tech_attribute

        #except Exception as e:
        #    print(e)
        #    sys.exit("could not get technology attribute {}  {}  {} ".format(enduse, tech, attribute_to_get))


    def set_tech_attribute_enduse(self, tech, attribute_to_set, value_to_set, enduse, sector):
        """Set an attrribute of a technology (stored in a list) in the technology stock

        If the attribute does not exist, create new attribute
        """
        tech_objects = getattr(self, str(enduse))
        for tech_object in tech_objects:
            if tech_object.tech_name == tech: # and tech_object.sector == sector:
                setattr(tech_object, str(attribute_to_set), value_to_set)

class Technology(object):
    """Technology Class for residential and service technology

    Notes
    -----
    The attribute `shape_peak_yd_factor` is initiated with dummy data and only filled with real data
    in the `Region` Class. The reason is because this factor depends on regional temperatures

    The daily and hourly shape of the fuel used by this Technology
    is initiated with zeros in the 'Technology' attribute. Within the `Region` Class these attributes
    are filled with real values.

    Only the yd shapes are provided on a technology level and not dh shapes

    """
    def __init__(self, enduse, tech_name, data, temp_by, temp_cy, t_base_heating, potential_enduses, t_base_heating_cy): #, sectors):
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
        #self.sector = sector
        self.tech_name = tech_name
        self.market_entry = data['assumptions']['technologies'][tech_name]['market_entry']
        self.tech_type = technologies_related.get_tech_type(tech_name, data['assumptions'])
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']

        # Diffusion method
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method'] #Not used

        # Fuel shapes (specific shapes of technologes are filled with dummy data and real shape filled in Region Class)
        #self.shape_yd = np.ones((365))
        #self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get shape of peak dh where not read from values directly (TODO: IMPROVE THAT SHAPE IS BETTER ASSIGNED)
        #TODO: ONLY FOR RESIDENTIAL SECTOR OCHS BIG BAUSTELLE
        #self.shape_peak_dh = self.get_shape_peak_dh(data)

        # Calculate fuel types and distribution
        if self.tech_type == 'hybrid_tech':

            self.tech_low_temp = data['assumptions']['technologies'][tech_name]['tech_low_temp']
            self.tech_high_temp = data['assumptions']['technologies'][tech_name]['tech_high_temp']

            self.tech_low_temp_fueltype = data['assumptions']['technologies'][self.tech_low_temp]['fuel_type']
            self.tech_high_temp_fueltype = data['assumptions']['technologies'][self.tech_high_temp]['fuel_type']

            self.eff_tech_low_by = self.const_eff_yh(data['assumptions']['technologies'][self.tech_low_temp]['eff_by'])
            self.eff_tech_high_by = self.get_heatpump_eff(temp_by, data['assumptions']['hp_slope_assumption'], data['assumptions']['technologies'][self.tech_high_temp]['eff_by'], t_base_heating)

            # Consider efficincy improvements
            eff_tech_low_cy = self.calc_eff_cy(data['assumptions']['technologies'][self.tech_low_temp]['eff_by'], self.tech_low_temp, data['base_yr'], data['end_yr'], data['curr_yr'], data['sim_period'], data['assumptions'])
            eff_tech_high_cy = self.calc_eff_cy(data['assumptions']['technologies'][self.tech_high_temp]['eff_by'], self.tech_high_temp, data['base_yr'], data['end_yr'], data['curr_yr'], data['sim_period'], data['assumptions'])

            # Efficiencies
            self.eff_tech_low_cy = self.const_eff_yh(eff_tech_low_cy) #constant eff of low temp tech
            self.eff_tech_high_cy = self.get_heatpump_eff(temp_cy, data['assumptions']['hp_slope_assumption'], eff_tech_high_cy, t_base_heating_cy)

            # Get fraction of service for hybrid technologies for every hour
            self.service_distr_hybrid_h_p_cy = self.service_hybrid_tech_low_high_h_p(
                temp_cy,
                data['assumptions']['technologies'][tech_name]['hybrid_cutoff_temp_low'],
                data['assumptions']['technologies'][tech_name]['hybrid_cutoff_temp_high']
                )

            # Shares of fueltype for every hour for multiple fueltypes
            self.fueltypes_yh_p_cy = self.calc_hybrid_fueltypes_p(
                data['nr_of_fueltypes'],
                self.tech_low_temp_fueltype,
                self.tech_high_temp_fueltype)
        else:
            # Shares of fueltype for every hour for single fueltype
            self.fueltypes_yh_p_cy = self.set_constant_fueltype(data['assumptions']['technologies'][tech_name]['fuel_type'], data['nr_of_fueltypes'])

        # -------------------------------
        # Base and current year efficiencies
        # Depending what sort of technology, make temp dependent, hybrid or constant efficiencies
        # -------------------------------
        if self.tech_type == 'heat_pump':
            self.eff_by = self.get_heatpump_eff(
                temp_by,
                data['assumptions']['hp_slope_assumption'],
                data['assumptions']['technologies'][tech_name]['eff_by'],
                t_base_heating)

            self.eff_cy = self.get_heatpump_eff(
                temp_cy,
                data['assumptions']['hp_slope_assumption'],
                self.calc_eff_cy(data['assumptions']['technologies'][tech_name]['eff_by'], tech_name, data['base_yr'], data['end_yr'], data['curr_yr'], data['sim_period'], data['assumptions']),
                t_base_heating_cy)

        elif self.tech_type == 'hybrid_tech':
            self.eff_by = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by)
            self.eff_cy = self.calc_hybrid_eff(self.eff_tech_low_cy, self.eff_tech_high_cy) # Current year efficiency (weighted according to service for hybrid technologies)
            '''elif self.tech_type == 'cooling_tech':
                #TODO: DEFINE
                self.eff_by =
                self.eff_cy =
            '''
        else:
            self.eff_by = self.const_eff_yh(data['assumptions']['technologies'][tech_name]['eff_by'])
            self.eff_cy = self.const_eff_yh(
                self.calc_eff_cy(data['assumptions']['technologies'][tech_name]['eff_by'], tech_name, data['base_yr'], data['end_yr'], data['curr_yr'], data['sim_period'], data['assumptions'])
            )

        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_types_shares_yd = self.convert_yh_to_yd_fueltype_shares(data['nr_of_fueltypes'], self.fueltypes_yh_p_cy)

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
            Y-value at 10 degree difference
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

                eff_hp_yh[day][h_nr] = shape_handling.eff_heat_pump(m_slope, h_diff, b)

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
        """
        tech_low_high_p = {
            'low': np.zeros((365, 24)),
            'high': np.zeros((365, 24))
            }

        for day, temp_d in enumerate(temp_cy):
            for hour, temp_h in enumerate(temp_d):

                # Get share of service of high temp technology
                service_high_tech_p = self.fraction_service_high_temp(
                    temp_h,
                    hybrid_cutoff_temp_low,
                    hybrid_cutoff_temp_high
                    )

                # Calculate share of service of low temp technology
                service_low_tech_p = 1.0 - service_high_tech_p

                tech_low_high_p['low'][day][hour] = service_low_tech_p
                tech_low_high_p['high'][day][hour] = service_high_tech_p

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
                service_high_p = self.service_distr_hybrid_h_p_cy['high'][day][hour]
                service_low_p = self.service_distr_hybrid_h_p_cy['low'][day][hour]

                # Efficiencies
                eff_low = eff_tech_low[day][hour]
                eff_high = eff_tech_high[day][hour]

                # Calculate weighted efficiency
                eff_hybrid_yh[day][hour] = (service_high_p * eff_high) + (service_low_p * eff_low)

                assert eff_hybrid_yh[day][hour] >= 0

        return eff_hybrid_yh

    def convert_yh_to_yd_fueltype_shares(self, nr_fueltypes, fueltypes_yh_p_cy):
        """Take share of fueltypes for every yh and calculate the mean share of every day

        The daily sum is calculated for every row of an array.

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
            #print("  {}   {}   {} {}".format(fueltype, fueltype_yh.shape, fueltype_yh.mean(axis=1).shape, np.sum(fueltype_yh.mean(axis=1))))

            # Calculate share of fuel per fueltype in day (If all fueltypes in one day == 24 (because 24 * 1.0)
            fuel_yd_shares[fueltype] = fueltype_yh.sum(axis=1) #Calculate percentage for a day

        #Testing
        np.testing.assert_almost_equal(np.sum(fuel_yd_shares), 8760, decimal=3, err_msg='Error XY')
        return fuel_yd_shares

    def calc_hybrid_fueltypes_p(self, nr_fueltypes, fueltype_low_temp, fueltype_high_temp):
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

        The overall service share defined for either technology overrules the input fuel shares for hybrid technologies
        """
        fueltypes_yh = np.zeros((nr_fueltypes, 365, 24))

        # Calculate hybrid efficiency
        hybrid_eff_yh = self.calc_hybrid_eff(self.eff_tech_low_by, self.eff_tech_high_by) #or cy?

        for day in range(365):
            for hour in range(24):
                #service_low_h, service_high_h = 0, 0

                # Fraction of service of low and high temp technology
                service_low_h_p = self.service_distr_hybrid_h_p_cy['low'][day][hour]
                service_high_h_p = self.service_distr_hybrid_h_p_cy['high'][day][hour]

                # Efficiency of low and high tech
                #eff_tech_low = self.eff_tech_low_by[day][hour] #cy or by?
                #eff_tech_high_hp = self.eff_tech_high_by[day][hour] # cy or by?
                #hybrid_eff = (service_high_h_p * eff_tech_high_hp) + (service_low_h_p * eff_tech_low)

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

                # The the low and high temp tech have same fueltype
                if fueltype_low_temp == fueltype_high_temp:
                    fueltypes_yh[fueltype_high_temp][day][hour] = 1.0 # fueltype_low_temp
                else:
                    # Assign share of total fuel for respective fueltypes
                    fueltypes_yh[fueltype_low_temp][day][hour] = np.divide(1.0, tot_fuel_h) * fuel_low_h
                    fueltypes_yh[fueltype_high_temp][day][hour] = np.divide(1.0, tot_fuel_h) * fuel_high_h

        np.testing.assert_almost_equal(np.sum(fueltypes_yh), 365 * 24, decimal=3, err_msg='ERROR XY')

        return fueltypes_yh

    def get_shape_peak_dh(self, data):
        """Depending on technology the peak shape dh is different and defined here

        Parameters
        ----------
        data : dict
            Data

        Info
        -----
        -   For hybrid technologies the dh peak shape depends on the region and therefore is dicrectly read out
            from the shape_yh and initiated here with zeros
        -   If no specific peak shape is defined, the peak is read out from shape_yh and initiated here with zeros
        """
        if self.enduse in data['ss_all_enduses']:
            shape_peak_dh = data['ss_shapes_dh'][self.sector][self.enduse]['shape_peak_dh']
        elif self.enduse in data['is_all_enduses']:
            shape_peak_dh = data['is_shapes_dh'][self.sector][self.enduse]['shape_peak_dh']
        else:
            #if self.enduse in data['rs_all_enduses']:

            # --See wheter the technology is part of a defined enduse and if yes, get technology specific peak shape
            if self.tech_type == 'storage_heating_electricity':
                shape_peak_dh = data['rs_shapes_space_heating_storage_heater_elec_heating_dh']['peakday'] #done
            elif self.tech_type == 'secondary_heating_electricity':
                shape_peak_dh = data['rs_shapes_space_heating_second_elec_heating_dh']['peakday'] #done
            elif self.tech_type == 'boiler_heating_tech':
                shape_peak_dh = data['rs_shapes_heating_boilers_dh']['peakday'] # Peak curve robert sansom done
            elif self.tech_type == 'heat_pump':
                shape_peak_dh = data['rs_shapes_heating_heat_pump_dh']['peakday'] # Peak curve robert sansom done
            elif self.tech_type == 'hybrid_tech':
                shape_peak_dh = np.ones((24)) # The shape is assigned in region from peak day
            elif self.tech_name == 'cooling_tech':
                shape_peak_dh = np.ones((24)) # TODO: DEfine peak curve for cooling
            else:
                shape_peak_dh = np.ones((24)) # Technology is not part of defined enduse initiate with dummy data

        return shape_peak_dh

    def calc_eff_cy(self, eff_by, technology, base_yr, current_yr, end_yr, sim_period, assumptions): #data):data['base_yr'],data['end_yr'], data['curr_yr'], data['assumptions']
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
            theor_max_eff = diffusion.linear_diff(
                base_yr,
                current_yr,
                assumptions['technologies'][technology]['eff_by'],
                assumptions['technologies'][technology]['eff_ey'],
                len(sim_period)
            )
        elif self.diff_method == 'sigmoid':
            theor_max_eff = diffusion.sigmoid_diffusion(base_yr, current_yr, end_yr, assumptions['sig_midpoint'], assumptions['sig_steeppness'])

        # Consider actual achieved efficiency
        actual_max_eff = theor_max_eff * self.eff_achieved_factor

        # Differencey in efficiency change
        efficiency_change = actual_max_eff * (assumptions['technologies'][technology]['eff_ey'] - assumptions['technologies'][technology]['eff_by'])

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        return eff_cy
