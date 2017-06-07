"""The technological stock for every simulation year"""
import sys
import numpy as np
import time
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
    def __init__(self, tech_name, data, temp_by, temp_cy, curr_yr): #, reg_shape_yd, reg_shape_yh, peak_yd_factor):
        """Contructor of Technology

        #TODO: Checke whetear all technologies which are temp dependent are specified for base year efficiency

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


        # Convert hourly fuel shares to average daily shares
        ###self.fuel_types_share_yd = mf.convert_hourly_to_daily_shares(self.fueltypes_fraction_yh_cy, len(data['lu_fueltype'])) #TODO: Single fueltype, = 1

        # -------
        # Depending on wheather only single fueltype or multiple fueltypes (hybrid technologies)
        # -------
        if self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            """ Hybrid efficiencies for residential heating
            """
            # Hybrid gas_electricity technology TODO: DEFINE TECHNOLOGY IN ASSUMPTIONS
            if self.tech_name == 'hybrid_gas_elec':
                tech_high_temp = 'av_heat_pump_electricity'
                tech_low_temp = 'boiler_gas'
                fueltype_low_temp = data['lu_fueltype']['gas']
                fueltype_high_temp = data['lu_fueltype']['electricity']
                hybrid_cutoff_temp_low = -5
                hybrid_cutoff_temp_high = 7
                eff_tech_low_by = data['assumptions']['technologies'][tech_low_temp]['eff_by']
                eff_tech_high_by = data['assumptions']['technologies'][tech_high_temp]['eff_by']

            # Get fraction of service for every hour for hybrid technology
            self.service_hybrid_h_p_cy = mf.service_hybrid_tech_low_high_h_p(temp_cy, hybrid_cutoff_temp_low, hybrid_cutoff_temp_high)

            # Calculate fuel share distribution
            eff_cy_tech_low = eff_tech_low_by + self.calc_efficiency_change(tech_low_temp, data, temp_cy, curr_yr)
            eff_cy_tech_high = eff_tech_high_by + self.calc_efficiency_change(tech_high_temp, data, temp_cy, curr_yr)

            self.fueltypes_fraction_yh_cy = self.calc_hybrid_fueltype(
                fueltype_low_temp,
                fueltype_high_temp,
                temp_cy,
                data['assumptions']['t_base_heating_resid']['base_yr'],
                data['assumptions']['heat_pump_slope_assumption'],
                eff_cy_tech_low,
                eff_cy_tech_high,
                self.service_hybrid_h_p_cy,
                len(data['lu_fueltype'])
            )

            # Shape
            # d_h --> IS different for every day or fueltype. --> Iterate days and calculate share of service for fueltype
            #--> Distribute share of fueltype to technology (is wrong) (e.g. 20% boiler, 80% hp)
        else:
            # Shares of fueltype for every hour for every fueltype
            self.fueltypes_fraction_yh_cy = mf.set_constant_fueltype(data['assumptions']['technologies'][self.tech_name]['fuel_type'], len(data['lu_fueltype']))

        # -------------------------------
        # Base and current year efficiencies
        # -------------------------------
        # Depending what sort of technology, make temp dependent, hybrid or constant efficiencies
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']:

            # Base year efficiency
            self.eff_by = mf.get_heatpump_eff(temp_by, data['assumptions']['heat_pump_slope_assumption'], data['assumptions']['technologies'][self.tech_name]['eff_by'], data['assumptions']['t_base_heating_resid']['base_yr'])

            # Efficiency change up to current year
            efficiency_change = self.calc_efficiency_change(self.tech_name, data, temp_cy, curr_yr)

            # Current year efficiency
            self.eff_cy = mf.get_heatpump_eff(temp_cy, data['assumptions']['heat_pump_slope_assumption'], data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change, data['assumptions']['t_base_heating_resid']['base_yr'])

        elif self.tech_name in data['assumptions']['list_tech_heating_hybrid']:

            # Base year efficiency
            self.eff_by = self.calc_hybrid_eff(temp_by, data['assumptions']['heat_pump_slope_assumption'], data['assumptions']['t_base_heating_resid']['base_yr'], eff_tech_low_by, eff_tech_high_by, self.service_hybrid_h_p_cy)

            # Current year efficiency (weighted according to service for hybrid technologies)
            t_base_heating_resid_cy = mf.t_base_sigm(data['data_ext']['glob_var']['base_yr'], data['assumptions'], data['data_ext']['glob_var']['base_yr'], data['data_ext']['glob_var']['end_yr'], 't_base_heating_resid')

            self.eff_cy = self.calc_hybrid_eff(temp_cy, data['assumptions']['heat_pump_slope_assumption'], t_base_heating_resid_cy, eff_cy_tech_low, eff_cy_tech_high, self.service_hybrid_h_p_cy)

            ##elif self.tech_name in data['assumptions']['list_tech_cooling_temp_dep']:
            ##sys.exit("Error: The technology is not defined in technology list (e.g. temp efficient tech or not")
        else:

            # Constant base year efficiency
            self.eff_by = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])

            # Efficiency change up to current year
            efficiency_change = self.calc_efficiency_change(self.tech_name, data, temp_cy, curr_yr)

            # Non temperature dependent efficiencies
            self.eff_cy = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change)


        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_types_share_yd = mf.convert_hourly_to_daily_shares(self.fueltypes_fraction_yh_cy, len(data['lu_fueltype']))

        # -------------------------------
        # Shapes
        # -------------------------------

        #-- Specific shapes of technologes filled with dummy data. Gets filled in Region Class
        self.shape_yd = np.ones((365))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh
        self.shape_peak_dh = self.get_shape_peak_dh(data)

    def calc_hybrid_eff(self, temp_yr, m_slope, t_base_heating, eff_tech_low, eff_tech_high, service_hybrid_h_p_cy):
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
                service_high_p = service_hybrid_h_p_cy[day][hour]['high']
                service_low_p = service_hybrid_h_p_cy[day][hour]['low']

                # Efficiencies
                eff_tech_low = eff_tech_low
                eff_tech_hp = m_slope * h_diff + eff_tech_high #Same as for heat pumpTODO: MAYBE NOT ALWAY HEAT PUMP. Make more complex

                # Calculate weighted efficiency
                eff_hybrid_yh[day][hour] = (service_high_p * eff_tech_hp) + (service_low_p * eff_tech_low)

                assert eff_tech_high >= 0

        return eff_hybrid_yh

    def calc_hybrid_fueltype(self, fueltype_low_temp, fueltype_high_temp, temp_yr, t_base_heating, m_slope, eff_tech_low, eff_tech_high, service_hybrid_h_p_cy, len_fueltypes):
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
                service_high_p = service_hybrid_h_p_cy[day][hour]['high']
                service_low_p = service_hybrid_h_p_cy[day][hour]['low']

                # Efficiencies m_slope, eff_tech_high, eff_tech_low
                # Calculate current year efficiency
                eff_tech_low = eff_tech_low
                eff_tech_high_hp = m_slope * h_diff + eff_tech_high #TODO: MAYBE NOT ALWAY HEAT PUMP. Make more complex

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
                fueltypes_yh[fueltype_low_temp][day][hour] = np.divide(1, tot_fuel) * fuel_low
                fueltypes_yh[fueltype_high_temp][day][hour] = np.divide(1, tot_fuel) * fuel_high

        return fueltypes_yh

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

    def calc_efficiency_change(self, technology, data, temp_cy, curr_yr):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency

        Parameters
        ----------
        data : dict
            All internal and external provided data
        temp_cy : array
            Temperatures of current year

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
        return efficiency_change

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
