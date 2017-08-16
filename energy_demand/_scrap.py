        else: # No technologies specified in enduse
            print("enduse is not defined with technologies: " + str(self.enduse))
            #enduse_peak_yd_factor = self.reg_peak_yd_heating_factor # Regional yd factor for heating
            #enduse_peak_yd_factor = self.reg_peak_yd_cooling_factor # Regional yd factor for cooling
            enduse_peak_yd_factor = 1

            # --Peak yd (peak day) (same for enduse for all technologies)
            self.enduse_fuel_peak_yd = self.calc_enduse_fuel_peak_yd_factor(
                enduse_fuel,
                enduse_peak_yd_factor
                )

            # --------
            # NON-PEAK
            # --------
            self.enduse_fuel_yd = self.enduse_y_to_d(
                self.enduse_fuel_new_fuel,
                data['shapes_resid_yd'][self.enduse]['shape_non_peak_yd']
                )
            self.enduse_fuel_yh = self.enduse_d_to_h(self.enduse_fuel_yd, data['shapes_resid_dh'][self.enduse]['shape_non_peak_h'])

            # --------
            # PEAK
            # --------
            self.enduse_fuel_peak_yh = self.calc_enduse_fuel_peak_yh(self.enduse_fuel_peak_yd, data['shapes_resid_dh'][enduse]['shape_peak_dh'])
            self.enduse_fuel_peak_h = self.get_peak_from_yh(self.enduse_fuel_peak_yh)


    def get_peak_from_yh(self, enduse_fuel_peak_yh):
        """Iterate yearly fuels and select day with most fuel
        """
        peak_fueltype_h = np.zeros((enduse_fuel_peak_yh.shape[0]))

        for fueltype, fuel_yh in enumerate(enduse_fuel_peak_yh):
            max_fuel_h = np.max(fuel_yh) # Get hour with maximum fuel_yh
            peak_fueltype_h[fueltype] = max_fuel_h # add
        return peak_fueltype_h

    def calc_enduse_fuel_peak_yd_factor(self, fuels, factor_d):
            """Disaggregate yearly absolute fuel data to the peak day.
        Parameters
        ----------
        self : self
            Data from constructor
        Returns
        -------
        fuels_d_peak : array
            Hourly absolute fuel data
        Example
        -----
        Input: 20 FUEL * 0.004 [0.4%] --> new fuel
        """
        fuels_d_peak = np.zeros((len(fuels)))
            fuels_d_peak[fueltype] = factor_d * fueltype_year_data
        return fuels_d_peak


    def get_calc_enduse_fuel_peak_h(self, data, attribute_to_get):
        """Summarise peak values of all enduses for every fueltype
        """
        sum_calc_enduse_fuel_peak_yh = np.zeros((len(data['fuel_type_lu']), 1)) # Initialise

        for fueltype in data['fuel_type_lu']:
            for enduse in data['resid_enduses']:
                sum_calc_enduse_fuel_peak_yh[fueltype] += self.__getattr__subclass__(enduse, attribute_to_get)[fueltype] # Fuel of Endus enduse_fuel_peak_dh

        return sum_calc_enduse_fuel_peak_yh


    def enduse_y_to_d(self, fuels, enduse_shape_yd):
        """Generate array with fuels for every day
        Parameters
        ----------
        fuels : array
            Yearly fuel data
        enduse_shape_yd : array
            Shape of enduse yd
        Returns
        -------
        fuels_d : array
            Hourly fuel data (365, 1)
        """
        fuels_d = np.zeros((fuels.shape[0], 365))

        for k, fuel in enumerate(fuels):
            fuels_d[k] = enduse_shape_yd * fuel
        
        return fuels_d

    def enduse_d_to_h(self, fuels, enduse_shape_dh):
        """Disaggregate yearly fuel data to every day in the year
        Parameters
        ----------
        self : self
            Data from constructor
        enduse_shape_dh : array
            Shape of dh of every day (365, 24)
        Returns
        -------
        fuels_h : array
            Hourly fuel data [fueltypes, days, hours]
        Notes
        -----
        """
        fuels_h = np.zeros((fuels.shape[0], 365, 24))

        for k, fuel in enumerate(fuels):
            for day in range(365):
                fuels_h[k][day] = enduse_shape_dh[day] * fuel[day]

        return fuels_h

    def calc_enduse_fuel_peak_yh(self, fuels, shape_peak_dh):
        """Disaggregate daily peak day fuel data to the peak hours.
        Parameters
        ----------
        self : self
            Data from constructor
        shape_peak_dh : dict
            Peak shape for enduse (here not iteration over technology shapes)
        Returns
        -------
        fuels_h_peak : array
            Hourly fuel data [fueltypes, peakday, peak_hours]
        Notes
        -----
        """
        fuels_h_peak = np.zeros((fuels.shape[0], 1, 24)) #fueltypes  days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for fueltype, fuel_data in enumerate(fuels):
            fuels_h_peak[fueltype] = shape_peak_dh * fuel_data
        return fuels_h_peak



#-------------


# Iterate technologies in enduse and assign technology specific shape for peak for respective fuels
self.enduse_fuel_peak_dh = self.calc_peak_tech_dh(
    data['assumptions'], enduse_fuel_tech_y, tech_stock, load_profiles)

# Get maximum hour demand per of peak day
self.enduse_fuel_peak_h = shape_handling.calk_peak_h_dh(self.enduse_fuel_peak_dh)