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
        start_time_tech = time.time()

        self.tech_name = tech_name
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # NEW Shares of fueltype for every hour for every fueltype
        #self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type']
        self.fuel_types_share_yh = mf.constant_fueltype(data['assumptions']['technologies'][self.tech_name]['fuel_type'], len(data['lu_fueltype']))

        # Convert hourly fuel shares to average daily shares
        ###self.fuel_types_share_yd = mf.convert_hourly_to_daily_shares(self.fuel_types_share_yh, len(data['lu_fueltype'])) #TODO: Single fueltype, = 1

        # -------
        # Hybrid
        # --> Efficiencies depending on temp
        # --> Fueltype depending on temp_cut_off

        # -------
        if self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            """ Hybrid efficiencies
            - Define temp_switch and share of service (e.g. 5 degree, 60%, 6 Degree: 20%, 7 degree: 20%)
            - Define daily curve with technology mix in percent for every hour
            - Define average effiiciency depending on tech switch
            - define fuel share for every hour
            """
            if self.tech_name == 'hybrid_gas_elec':
                self.tech_high_temp = 'av_heat_pump_electricity'
                self.tech_low_temp = 'boiler_gas'
                fueltype_low_temp = data['lu_fueltype']['gas']
                fueltype_high_temp = data['lu_fueltype']['electricity']

            self.hybrid_temp_cut_off_low_temp = -5 # Temperature where fueltypes are switched
            self.hybrid_temp_cut_off_high_temp = 7 # Temperature where fueltypes are switched

            # HYBRID: MIXED, three scenarios (boiler, combi, hp)
            # ------A Get service distribution for every hour, Get service fraction based on temp(lindiff) and assume distribution of fuel based on dummy data
            self.fractions_service_high_low = mf.fraction_service_high_low_temp_tech(temp_cy, self.hybrid_temp_cut_off_low_temp, self.hybrid_temp_cut_off_high_temp)

            # Create daily shapes based on technology mix ()
            # ---------------------
            # Calculate based on service assumption for every hour the split of daily curve

            # C. Calculate fuel share distribution
            # TODO: DO NOT ASSIGN FOR EVERY HOUR BUT ASSIGN AVERAGE ACROSS : MAYBE???
            self.fuel_types_share_yh = self.calc_hybrid_fueltype(fueltype_low_temp, fueltype_high_temp, self.fractions_service_high_low, len(data['lu_fueltype']))

            # Shape
            # d_h --> IS different for every day or fueltype. --> Iterate days and calculate share of service for fueltype
            #--> Distribute share of fueltype to technology (is wrong) (e.g. 20% boiler, 80% hp)

        # -------------------------------
        # Efficiencies
        # -------------------------------
        # --Base year
        if self.tech_name in data['assumptions']['list_tech_heating_temp_dep']: # Make temp dependent base year efficiency

            efficiency_change = self.calc_efficiency_change(self.tech_name, data, temp_cy, curr_yr)
            
            self.eff_by = mf.get_heatpump_eff(
                temp_by,
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['technologies'][self.tech_name]['eff_by'],
                data['assumptions']['t_base_heating_resid']['base_yr']
            )

            self.eff_cy = mf.get_heatpump_eff(
                temp_cy,
                data['assumptions']['heat_pump_slope_assumption'], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change,
                data['assumptions']['t_base_heating_resid']['base_yr']
            )

        elif self.tech_name in data['assumptions']['list_tech_heating_hybrid']:
            efficiency_change_low_tech = self.calc_efficiency_change(self.tech_low_temp, data, temp_cy, curr_yr)
            efficiency_change_high_tech = self.calc_efficiency_change(self.tech_high_temp, data, temp_cy, curr_yr)

            self.eff_by = self.calc_hybrid_eff(
                temp_by,
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['t_base_heating_resid']['base_yr'],
                data['assumptions']['technologies'][self.tech_low_temp]['eff_by'],
                data['assumptions']['technologies'][self.tech_high_temp]['eff_by'],
                self.fractions_service_high_low
            )

            self.eff_cy = self.calc_hybrid_eff(
                temp_cy,
                data['assumptions']['heat_pump_slope_assumption'],
                data['assumptions']['t_base_heating_resid']['base_yr'],
                data['assumptions']['technologies'][self.tech_low_temp]['eff_by'] + efficiency_change_low_tech, # Boiler efficiency
                data['assumptions']['technologies'][self.tech_high_temp]['eff_by'] + efficiency_change_high_tech, # Heat pump efficiency
                self.fractions_service_high_low
            )
            ##elif self.tech_name in data['assumptions']['list_tech_cooling_temp_dep']:
            ##sys.exit("Error: The technology is not defined in technology list (e.g. temp efficient tech or not")
        else:
            efficiency_change = self.calc_efficiency_change(self.tech_name, data, temp_cy, curr_yr)
            # Constant base year efficiency
            self.eff_by = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'])

            # Non temperature dependent efficiencies
            self.eff_cy = mf.const_eff_yh(data['assumptions']['technologies'][self.tech_name]['eff_by'] + efficiency_change)




        # Convert hourly fuel type shares to daily fuel type shares
        self.fuel_types_share_yd = mf.convert_hourly_to_daily_shares(self.fuel_types_share_yh, len(data['lu_fueltype']))

        # -------------------------------
        # Shapes
        # -------------------------------

        #-- Specific shapes of technologes filled with dummy data. Gets filled in Region Class
        self.shape_yd = np.ones((365)) # 1))
        self.shape_yh = np.ones((365, 24))
        self.shape_peak_yd_factor = 1

        # Get Shape of peak dh
        self.shape_peak_dh = self.get_shape_peak_dh(data)
        #print("  ----TIME for technology %s seconds" % (time.time() - start_time_tech))

    def calc_hybrid_eff(self, temp_yr, m_slope, t_base_heating, eff_boiler, eff_hp, fractions_high_low):
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

                frac_service_high = fractions_high_low[day][hour]['high']
                frac_service_low = fractions_high_low[day][hour]['low']

                eff_tech_high = eff_boiler #Biler eff
                eff_tech_low = m_slope * h_diff + eff_hp # Heat pump efficiency

                av_efficiency = (frac_service_high * eff_tech_high) + (frac_service_low * eff_tech_low)

                eff_hybrid_yh[day][hour] = av_efficiency

        return eff_hybrid_yh

    def calc_hybrid_fueltype(self, fueltype_low_temp, fueltype_high_temp, fractions_service_high_low, len_fueltypes):
        """Calculate efficiency for every hour for hybrid technology

        Here the distribution to different fueltypes is only valid within an hour (e.g. the fuel is not distributed across
        the day)

        TODO: SEE if based on daily share of each service the hourly distribution can be made: Improve
        """
        '''fueltype_yh = np.zeros((365, 24))

        for day, temp_day in enumerate(temp_yr):
            for h_nr, temp_h in enumerate(temp_day):

                # Test which efficieny of hybrid tech is used
                if temp_h <= hybrid_temp_cut_off:
                    fueltype_yh[day][h_nr] = fueltype_low_temp
                else:
                    fueltype_yh[day][h_nr] = fueltype_high_temp
        '''
        fueltypes_yh = np.zeros((len_fueltypes, 365, 24))

        for day in range(365):
            for hour in range(24):

                # Share of service of low tech
                frac_tech_low = fractions_service_high_low[day][hour]['low']
                frac_tech_high = fractions_service_high_low[day][hour]['high']

                dummy_service = 100

                if frac_tech_low > 0:
                    fuel_low = np.divide(dummy_service, frac_tech_low) #TODO: CHECK
                else:
                    fuel_low = 0

                if frac_tech_high > 0:
                    fuel_high = np.divide(dummy_service, frac_tech_high) #TODO: CHECK
                else:
                    fuel_high = 0

                tot_fuel = fuel_low + fuel_high

                fueltypes_yh[fueltype_low_temp][day][hour] = np.divide(1, tot_fuel) * fuel_low
                fueltypes_yh[fueltype_high_temp][day][hour] = np.divide(1, tot_fuel) * fuel_high

        #TODO: WRITE ASSERT
        #Across all fueltypes for every h sum up to 100%
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
        start_time_ResidTechStock = time.time()

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
        #print("  ----TIMER for ResidTechStock: %s seconds---" % (time.time() - start_time_ResidTechStock))

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
