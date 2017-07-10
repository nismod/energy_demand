"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
from datetime import date
import unittest
import numpy as np
import energy_demand.technological_stock as ts
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_shape_handling import hdd_cdd
from energy_demand.scripts_technologies import technologies_related
from energy_demand.scripts_geography import weather_station_location as wl
ASSERTIONS = unittest.TestCase('__init__')

class Region(object):
    """Region class

    For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_name : str
        Unique identifyer of region
    data : dict
        Dictionary containing data

    Info
    -------------------------
    - For each region, a technology stock is defined with help of regional temperature data technology specific
    - Regional specific fuel shapes are assigned to technologies
    """
    def __init__(self, reg_name, data):
        """Constructor of Region
        """
        self.reg_name = reg_name

        # Fuels of service sectors
        self.rs_enduses_fuel = data['rs_fueldata_disagg'][reg_name]
        self.ss_enduses_sectors_fuels = data['ss_fueldata_disagg'][reg_name]

        # Get closest weather station and temperatures
        closest_station_id = wl.get_closest_station(
            data['region_coordinates'][reg_name]['longitude'],
            data['region_coordinates'][reg_name]['latitude'],
            data['weather_stations']
            )
        temp_by = data['temperature_data'][closest_station_id][data['base_yr']]
        temp_cy = data['temperature_data'][closest_station_id][data['curr_yr']]

        # Get base temperatures for base and current year
        rs_t_base_heating_cy = hdd_cdd.t_base_sigm(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')
        rs_t_base_cooling_cy = hdd_cdd.t_base_sigm(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_cooling')

        ss_t_base_heating_cy = hdd_cdd.t_base_sigm(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_heating')
        ss_t_base_cooling_cy = hdd_cdd.t_base_sigm(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_cooling')

        rs_t_base_heating_by = hdd_cdd.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')
        rs_t_base_cooling_by = hdd_cdd.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_cooling')

        ss_t_base_heating_by = hdd_cdd.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_heating')
        ss_t_base_cooling_by = hdd_cdd.t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_cooling')

        # ----------------------------------------------------------------------------------------
        # Calculate HDD and CDD for calculating heating and cooling service demand (for rs and ss)
        # ----------------------------------------------------------------------------------------
        # Residential
        rs_hdd_by, _ = self.get_reg_hdd(data, temp_by, rs_t_base_heating_by)
        rs_cdd_by, _ = self.get_reg_cdd(data, temp_by, rs_t_base_cooling_by)

        rs_hdd_cy, rs_fuel_shape_heating_yd = self.get_reg_hdd(data, temp_cy, rs_t_base_heating_cy)
        rs_cdd_cy, rs_fuel_shape_cooling_yd = self.get_reg_cdd(data, temp_cy, rs_t_base_cooling_cy)

        # Service
        ss_hdd_by, _ = self.get_reg_hdd(data, temp_by, ss_t_base_heating_by)
        ss_cdd_by, _ = self.get_reg_cdd(data, temp_by, ss_t_base_cooling_by)

        ss_hdd_cy, ss_fuel_shape_heating_yd = self.get_reg_hdd(data, temp_cy, rs_t_base_heating_cy)
        ss_cdd_cy, ss_fuel_shape_cooling_yd = self.get_reg_cdd(data, temp_cy, ss_t_base_cooling_cy)

        # yd peak factors for heating and cooling (factor to calculate max daily demand from yearly demand)
        self.rs_reg_peak_yd_heating_factor = self.get_shape_peak_yd_factor(rs_hdd_cy)
        self.rs_reg_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(rs_cdd_cy)

        self.ss_reg_peak_yd_heating_factor = self.get_shape_peak_yd_factor(ss_hdd_cy)
        self.ss_reg_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(ss_cdd_cy)

        # Climate change correction factors (Assumption: Demand for heat correlates directly with fuel)
        self.rs_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_hdd_by))) * np.sum(rs_hdd_cy)
        self.rs_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_cdd_by))) * np.sum(rs_cdd_cy)

        self.ss_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_hdd_by))) * np.sum(ss_hdd_cy)
        self.ss_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_cdd_by))) * np.sum(ss_cdd_cy)

        # Create region specific technological stock
        self.rs_tech_stock = ts.TechStock(data, temp_by, temp_cy, data['assumptions']['rs_t_base_heating']['base_yr'], data['rs_all_enduses'], rs_t_base_heating_cy)
        self.ss_tech_stock = ts.TechStock(data, temp_by, temp_cy, data['assumptions']['ss_t_base_heating']['base_yr'], data['ss_all_enduses'], ss_t_base_heating_cy)

        # -------------------------------------------------------------------------------------------
        # Load and calculate fuel shapes for different technologies and assign to technological stock
        # -------------------------------------------------------------------------------------------

        # --Heating technologies for residential sector
        rs_fuel_shape_boilers_yh, rs_fuel_shape_boilers_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_heating_boilers_dh') # boiler, non-peak
        rs_fuel_shape_hp_yh, rs_fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(data, self.rs_tech_stock, rs_hdd_cy, 'rs_shapes_heating_heat_pump_dh') # heat pumps, non-peak
        rs_fuel_get_shape_cooling_yh = self.get_shape_cooling_yh(data, rs_fuel_shape_cooling_yd, 'rs_shapes_cooling_dh') # Residential cooling
        rs_fuel_shape_hybrid_tech_yh = self.get_shape_heating_hybrid_yh(self.rs_tech_stock, rs_fuel_shape_boilers_y_dh, rs_fuel_shape_hp_y_dh, rs_fuel_shape_heating_yd, 'hybrid_gas_elec', 'boiler_gas', 'electricity_heat_pumps') # Hybrid gas electric

        # --Heating technologies for service sector (the heating shape follows the gas shape of aggregated sectors)
        ss_fuel_shape_any_tech, ss_fuel_shape = self.ss_get_sector_enduse_shape(data, ss_fuel_shape_heating_yd, 'ss_space_heating')
        ss_fuel_get_shape_cooling_yh = self.ss_get_sector_enduse_shape(data, ss_fuel_shape_cooling_yd, 'ss_cooling_and_ventilation')
        ss_fuel_shape_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(self.ss_tech_stock, ss_fuel_shape, ss_fuel_shape, ss_fuel_shape_heating_yd, 'hybrid_gas_elec', 'boiler_gas', 'electricity_heat_pumps') # Hybrid

        # Assign shapes to technologies in technological stock (residential sector)
        self.assign_fuel_shapes_tech_stock(
            'rs',
            data['rs_all_enduses'],
            data['assumptions']['rs_all_specified_tech_enduse_by'],
            data,
            rs_fuel_shape_heating_yd,
            rs_fuel_shape_boilers_yh,
            rs_fuel_get_shape_cooling_yh,
            rs_fuel_shape_hp_yh,
            rs_fuel_shape_hybrid_tech_yh,
            self.rs_tech_stock
            )

        # Assign shapes to technologs in technological stock (service sector)
        self.assign_fuel_shapes_tech_stock(
            'ss',
            data['ss_all_enduses'],
            data['assumptions']['ss_all_specified_tech_enduse_by'],
            data,
            ss_fuel_shape_heating_yd,
            ss_fuel_shape_any_tech,
            ss_fuel_get_shape_cooling_yh,
            ss_fuel_shape_any_tech,
            ss_fuel_shape_hybrid_gas_elec_yh,
            self.ss_tech_stock
            )

    def get_shape_heating_hybrid_yh(self, tech_stock, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech, tech_low_temp, tech_high_temp):
        """Use yd shapes and dh shapes of hybrid technologies to generate yh shape

        Parameters
        ----------
        fuel_shape_boilers_y_dh : array
            Fuel shape of boilers (dh) for evey day in a year
        fuel_shape_hp_y_dh : array
            Fuel shape of heat pumps (dh) for every day in a year
        fuel_shape_heating_yd : array
            Fuel shape for assign demand to day in a year (yd)
        tech_low_temp : string
            Low temperature technology
        tech_high_temp : string
            High temperature technology

        Return
        -------
        fuel_shape_yh : array
            Share of yearly fuel for hybrid technology

        Note
        -----
        This is for hybrid_gas_elec technology

        The shapes are the same for any hybrid technology with boiler and heat pump
        """
        fuel_shape_yh = np.zeros((365, 24))

        # Create dh shapes for every day from relative dh shape of hybrid technologies
        fuel_shape_hybrid_y_dh = shape_handling.get_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=tech_stock.get_tech_attribute(hybrid_tech, 'service_distr_hybrid_h_p_cy'),
            eff_low_tech=tech_stock.get_tech_attribute(tech_low_temp, 'eff_cy'),
            eff_high_tech=tech_stock.get_tech_attribute(tech_high_temp, 'eff_cy')
            )

        # Calculate yh fuel shape
        for day, fuel_day in enumerate(fuel_shape_heating_yd):
            fuel_shape_yh[day] = fuel_shape_hybrid_y_dh[day] * fuel_day

        # Testing
        np.testing.assert_almost_equal(np.sum(fuel_shape_yh), 1, decimal=3, err_msg="ERROR XY: The hybridy yh shape does not sum up to 1.0")

        return fuel_shape_yh

    def get_shape_peak_yd_factor(self, demand_yd):
        """From yd shape calculate maximum relative yearly service demand which is provided in a day

        Parameters
        ----------
        demand_yd : shape
            Demand for energy service for every day in year

        Return
        ------
        max_factor_yd : float
            yd maximum factor

        Info
        -----
        If the shape is taken from heat and cooling demand the assumption is made that
        HDD and CDD are directly proportional to fuel usage
        """
        tot_demand_y = np.sum(demand_yd) # Total yearly demand
        max_demand_d = np.max(demand_yd) # Maximum daily demand
        max_factor_yd = np.divide(1.0, tot_demand_y) * max_demand_d

        return max_factor_yd

    def assign_fuel_shapes_tech_stock(self, abr, enduses, technologies_input, data, fuel_shape_heating_yd, fuel_shape_boilers_yh, fuel_get_shape_cooling_yh, fuel_shape_hp_yh, fuel_shape_hybrid_gas_elec_yh, tech_stock):
        """Assign fuel shapes to indidivdual technologies in technologicalStock

        The technologies are iterated and checked wheter they are part of
        a specified enduse. Depending on defined asspumptions different shape
        curves for yd or yh are taken.

        Parameters
        ----------
        data : dict
            data
        fuel_shape_heating_yd : array
            Assume that fuel of day is proportional to HDD (for all technologies)
        Return
        ------
        tech_stock : attribute
            Updated attribute of `Region` class
        """
        for enduse in enduses:

            # Iterate all technologies and check if specific technology has a own shape
            for technology in technologies_input[enduse]:

                # Get technology type
                tech_type = technologies_related.get_tech_type(technology, data['assumptions'], enduse)

                if tech_type == 'boiler_heating_tech':
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yd', fuel_shape_heating_yd, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', fuel_shape_boilers_yh, enduse)

                elif tech_type == 'cooling_tech':
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', fuel_get_shape_cooling_yh)

                elif tech_type == 'heat_pump':
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yd', fuel_shape_heating_yd, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', fuel_shape_hp_yh, enduse)

                elif tech_type == 'hybrid_tech':
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yd', fuel_shape_heating_yd, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', fuel_shape_hybrid_gas_elec_yh, enduse)

                elif tech_type == 'lighting_technology':
                    enduse_shape_from_HES_yd = data['{}_shapes_yd'.format(abr)]['{}_lighting'.format(abr)]['shape_non_peak_yd']
                    enduse_shape_from_HES_dh = data['{}_shapes_dh'.format(abr)]['{}_lighting'.format(abr)]['shape_non_peak_dh']
                    enduse_shape_from_HES_peak_yd_factor = data['{}_shapes_yd'.format(abr)]['{}_lighting'.format(abr)]['shape_peak_yd_factor']

                    # Convert yd and dh to yh
                    enduse_shape_from_HES_yh = shape_handling.convert_dh_yd_to_yh(enduse_shape_from_HES_yd, enduse_shape_from_HES_dh)

                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', enduse_shape_from_HES_yh, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yd', enduse_shape_from_HES_yd, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_peak_yd_factor', enduse_shape_from_HES_peak_yd_factor, enduse)

                elif tech_type == 'water_heating':
                    enduse_shape_from_HES_yd = data['{}_shapes_yd'.format(abr)]['{}_water_heating'.format(abr)]['shape_non_peak_yd']
                    enduse_shape_from_HES_dh = data['{}_shapes_dh'.format(abr)]['{}_water_heating'.format(abr)]['shape_non_peak_dh']
                    enduse_shape_from_HES_peak_yd_factor = data['{}_shapes_yd'.format(abr)]['{}_water_heating'.format(abr)]['shape_peak_yd_factor']

                    # Convert yd and dh to yh
                    enduse_shape_from_HES_yh = shape_handling.convert_dh_yd_to_yh(enduse_shape_from_HES_yd, enduse_shape_from_HES_dh)

                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yh', enduse_shape_from_HES_yh, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_yd', enduse_shape_from_HES_yd, enduse)
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_peak_yd_factor', enduse_shape_from_HES_peak_yd_factor, enduse)
                else:
                    sys.exit("Error: The technology '{}' techtype:'{}' was not defined in a TECHLISTE".format(technology, tech_type))

        return

    def get_reg_hdd(self, data, temperatures, t_base_heating_cy):
        """Calculate HDD for every day and daily yd shape of cooling demand

        Based on temperatures of a year, the HDD are calculated for every
        day in a year. Based on the sum of all HDD of all days, the relative
        share of heat used for any day is calculated.

        The Heating Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        data : dict
            Base data dict

        Return
        ------
        hdd_d : array
            Heating degree days for every day in a year (365, 1)

        Info
        -----
        The shape_yd can be calcuated as follows: 1/ np.sum(hdd_d) * hdd_d

        The diffusion is assumed to be sigmoid
        """
        # Calculate base temperature for heating of current year
        #t_base_heating_cy = hdd_cdd.t_base_sigm(year, data['assumptions'], data['base_yr'], data['end_yr'], t_base_type)

        # Calculate hdd for every day (365, 1)
        hdd_d = hdd_cdd.calc_hdd(t_base_heating_cy, temperatures)

        shape_hdd_d = shape_handling.absolute_to_relative(hdd_d)

        # Error testing
        if np.sum(hdd_d) == 0:
            sys.exit("Error: No heating degree days means no fuel for heating is necessary")

        return hdd_d, shape_hdd_d

    def get_reg_cdd(self, data, temperatures, t_base_cooling):
        """Calculate CDD for every day and daily yd shape of cooling demand

        Based on temperatures of a year, the CDD are calculated for every
        day in a year. Based on the sum of all CDD of all days, the relative
        share of heat used for any day is calculated.

        The Cooling Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        data : dict
            Base data dict
        data_ext : dict
            External data

        Return
        ------
        shape_yd : array
            Fraction of heat for every day. Array-shape: 365, 1
        """
        #t_base_cooling = hdd_cdd.t_base_sigm(year, data['assumptions'], data['base_yr'], data['end_yr'], t_base_type)

        cdd_d = hdd_cdd.calc_cdd(t_base_cooling, temperatures)

        shape_cdd_d = shape_handling.absolute_to_relative(cdd_d)

        return cdd_d, shape_cdd_d

    def get_fuel_shape_heating_hp_yh(self, data, tech_stock, rs_hdd_cy, tech_to_get_shape):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        tech_stock : object
            Technology stock
        rs_hdd_cy : array
            Heating Degree Days (365, 1)

        Returns
        -------
        hp_shape : array
            Daily shape how yearly fuel can be distributed to hourly
        shape_y_dh : array
            Shape of fuel shape for every day in a year (total sum = 365)
        Info
        ----
        The service is calculated based on the efficiency of gas heat pumps (av_heat_pump_gas)

        The daily heat demand is converted to daily fuel depending on efficiency of heatpumps (assume if 100% heat pumps).
        In a final step the hourly fuel is converted to percentage of yearly fuel demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily fuel demand curve for heat pumps taken from:
        Sansom, R. (2014). Decarbonising low grade heat for low carbon future. Dissertation, Imperial College London.
        """
        shape_yh_hp = np.zeros((365, 24))
        shape_y_dh = np.zeros((365, 24))

        list_dates = date_handling.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # See wether day is weekday or weekend
            weekday = date_gasday.timetuple().tm_wday

            # Take respectve daily fuel curve depending on weekday or weekend from Robert Sansom for heat pumps
            if weekday == 5 or weekday == 6:
                daily_fuel_profile = np.divide(data[tech_to_get_shape][2], np.sum(data[tech_to_get_shape][2])) # WkendHourly gas shape. Robert Sansom hp curve
            else:
                daily_fuel_profile = np.divide(data[tech_to_get_shape][1], np.sum(data[tech_to_get_shape][1])) # Wkday Hourly gas shape. Robert Sansom hp curve

            # Calculate weighted average daily efficiency of heat pump
            average_eff_d = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):
                tech_object = getattr(tech_stock, 'gas_heat_pumps') # Select gas heat pumps to calculate service shape
                average_eff_d += heat_share_h * getattr(tech_object, 'eff_cy')[day][hour] # Hourly heat demand * heat pump efficiency

            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = np.divide(rs_hdd_cy[day], average_eff_d)

            # Fuel distribution within day
            fuel_shape_d = hp_daily_fuel * daily_fuel_profile

            # Distribute fuel of day according to fuel load curve
            shape_yh_hp[day] = fuel_shape_d

            # Add normalised daily fuel curve
            shape_y_dh[day] = shape_handling.absolute_to_relative(fuel_shape_d)

        # Convert absolute hourly fuel demand to relative fuel demand within a year
        shape_yh = np.divide(1, np.sum(shape_yh_hp)) * shape_yh_hp

        return shape_yh, shape_y_dh

    def get_shape_cooling_yh(self, data, cooling_shape, tech_to_get_shape):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        This is for non-peak.

        Every the day same

        Taken from Denholm, P., Ong, S., & Booten, C. (2012). Using Utility Load Data to
        Estimate Demand for Space Cooling and Potential for Shiftable Loads,
        (May), 23. Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf

        Parameters
        ---------
        data : dict
            data

        Returns
        -------
        shape_yd_cooling_tech : array
            Shape of cooling devices

        Info
        ----
        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        """
        shape_yd_cooling_tech = np.zeros((365, 24))

        for day in range(365):
            shape_yd_cooling_tech[day] = data[tech_to_get_shape] * cooling_shape[day] # Shape of cooling (same for all days) * daily cooling demand

        return shape_yd_cooling_tech

    def ss_get_sector_enduse_shape(self, data, heating_shape, enduse):
        """Read generic shape for all technologies in a service sector enduse

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly heat demand for every day)
        enduse : str
            Enduse where technology is used

        Returns
        -------
        shape_yh_boilers : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_y_dh_boilers : array
            Shape of distribution of fuel within every day of a year (total sum == 365)

        Info
        ----
        """
        shape_yh_generic_tech = np.zeros((365, 24))
        shape_y_dh_generic_tech = np.zeros((365, 24))

        if enduse not in data['ss_all_tech_shapes_dh']:
            pass
        else:
            shape_non_peak_dh = data['ss_all_tech_shapes_dh'][enduse]['shape_non_peak_dh']

            for day in range(365):
                shape_yh_generic_tech[day] = heating_shape[day] * shape_non_peak_dh[day] #yd shape
                shape_y_dh_generic_tech[day] = shape_non_peak_dh[day] #dh shape

        return shape_yh_generic_tech, shape_y_dh_generic_tech

    def get_shape_heating_boilers_yh(self, data, heating_shape, tech_to_get_shape):
        """Convert daily fuel shape to hourly based on robert sansom daily load for boilers

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly heat demand for every day)

        Returns
        -------
        shape_yh_boilers : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_y_dh_boilers : array
            Shape of distribution of fuel within every day of a year (total sum == 365)

        Info
        ----
        The assumption is made that boilers have constant efficiency for every hour in a year.
        Therefore the fuel demand correlates directly with the heat service demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        Sansom, R. (2014). Decarbonising low grade heat for low carbon future. Dissertation, Imperial College London.
        """
        shape_yh_boilers = np.zeros((365, 24))
        shape_y_dh_boilers = np.zeros((365, 24))

        list_dates = date_handling.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # See wether day is weekday or weekend
            weekday = date_gasday.timetuple().tm_wday

            # Take respectve daily fuel curve depending on weekday or weekend
            if weekday == 5 or weekday == 6:

                # -----
                # The percentage of totaly yearly heat demand (heating_shape[day]) is distributed with daily fuel shape of boilers
                # Because boiler eff is constant, the shape_yh_boilers reflects the needed heat per hour
                # ------
                # Wkend Hourly gas shape. Robert Sansom boiler curve
                shape_yh_boilers[day] = heating_shape[day] * (data[tech_to_get_shape][2] / np.sum(data[tech_to_get_shape][2]))

                shape_y_dh_boilers[day] = np.divide(data[tech_to_get_shape][2], np.sum(data[tech_to_get_shape][2]))
            else:
                # Wkday Hourly gas shape. Robert Sansom boiler curve
                shape_yh_boilers[day] = heating_shape[day] * (data[tech_to_get_shape][1] / np.sum(data[tech_to_get_shape][1])) #yd shape

                shape_y_dh_boilers[day] = np.divide(data[tech_to_get_shape][1], np.sum(data[tech_to_get_shape][1])) #dh shape

        # Testing
        np.testing.assert_almost_equal(np.sum(shape_yh_boilers), 1, err_msg="Error in shape_yh_boilers: The sum of hourly shape is not 1: {}".format(np.sum(shape_yh_boilers)))

        return shape_yh_boilers, shape_y_dh_boilers
    