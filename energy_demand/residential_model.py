"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
import energy_demand.technological_stock as ts
#import logging
import copy
from datetime import date

class Region(object):
    """Class of a region for the residential model

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_name : str
        Unique identifyer of region
    data : dict
        Dictionary containing data
    data_ext : dict
        Dictionary containing all data provided specifically for scenario run and from wrapper.abs

    # TODO: All calculatiosn are basd on driver_fuel_fuel_data
    """
    def __init__(self, reg_name, data, data_ext):
        """Constructor of Region Class
        """
        self.reg_name = reg_name
        self.enduses_fuel = data['fueldata_disagg'][reg_name] # Fuel array of region
        self.temp_by = data_ext['temperature_data'][data_ext['glob_var']['base_yr']] #TODO: READ IN SPECIFIC TEMP OF REGION
        self.temp_cy = data_ext['temperature_data'][data_ext['glob_var']['curr_yr']] #TODO: READ IN SPECIFIC TEMP OF REGION

        #get_peak_temp() #TODO: Get peak day gemperatures (day with hottest temperature and day with coolest temperature)

        # Create region specific technological stock
        self.tech_stock_by = ts.ResidTechStock(data, data_ext, self.temp_by, data_ext['glob_var']['base_yr'])
        self.tech_stock_cy = ts.ResidTechStock(data, data_ext, self.temp_cy, data_ext['glob_var']['curr_yr'])
        #print("OKO=====================" + str(self.tech_stock_by.__dict__))

        #print("OK: " + str(getattr(self.tech_stock_cy, 'heat_pump')))
        #print("OKO=====================" + str(self.tech_stock_cy['heat_pump'].eff_cy))

        # Calculate HDD and CDD scenario driver for heating and cooling
        self.hdd_by = self.get_heating_demand_shape(data, data_ext, self.temp_by, data_ext['glob_var']['base_yr'])
        self.cdd_by = self.get_cooling_demand_shape(data, data_ext, self.temp_by, data_ext['glob_var']['base_yr'])

        # Calculate fuel factors for heating and cooling
        self.hdd_cy = self.get_heating_demand_shape(data, data_ext, self.temp_cy, data_ext['glob_var']['curr_yr'])
        self.heating_shape_d_hdd_cy = (1.0 / np.sum(self.hdd_cy)) * self.hdd_cy # Shape of heating demand 

        self.cdd_cy = self.get_cooling_demand_shape(data, data_ext, self.temp_cy, data_ext['glob_var']['curr_yr']) #TODO
        #self.heating_shape_d_hdd_cy = (1.0 / self.hdd_cy) * self.hdd_cy #Cooling technology? # Shape ofcooling demand

        self.heat_diff_factor = (1.0 / self.hdd_by) * self.hdd_cy #shape (365,1)
        self.cooling_diff_factor = (1.0 / self.cdd_by) * self.cdd_cy #shape (365,1)

        # Create BOILER shape based on daily gas profiles
        self.fuel_shape_y_h_hdd_boilers_cy = self.y_to_h_heat_gas_boilers(data, data_ext, self.heating_shape_d_hdd_cy) # Shape of boilers (same efficiency over year)

        # Create HEATPUMP shape based on daily gas profiles (non-peak gas profiles)
        self.fuel_shape_y_h_hdd_hp_cy = self.y_to_h_heat_hp(data, data_ext, self.hdd_cy, self.tech_stock_cy) # Shape of hp (efficiency in dependency of temp diff)

        '''
        plot_a = np.zeros((365, 1))
        for nr, i in enumerate(self.fuel_shape_y_h_hdd_boilers_cy):
            plot_a[nr][0] = np.sum(self.fuel_shape_y_h_hdd_boilers_cy[nr])

        plot_b = np.zeros((365, 1))
        for nr, i in enumerate(self.fuel_shape_y_h_hdd_hp_cy):
            plot_b[nr][0] = np.sum(self.fuel_shape_y_h_hdd_hp_cy[nr])

        plt.plot(range(365), plot_a, 'red') #boiler shape
        plt.plot(range(365), plot_b, 'green') #hp shape
        plt.show()
        '''

        # Set attributs of all enduses to the Region Class
        self.create_enduses(data, data_ext)




        # -- summing functions
        # Sum final 'yearly' fuels (summarised over all enduses)
        self.fuels_new = self.tot_all_enduses_y(data)
        self.fuels_new_enduse_specific = self.enduse_specific_y(data) #each enduse individually
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%YEAR: " + str(data_ext['glob_var']['curr_yr']) + "  data  " + str(np.sum(self.fuels_new)))
        f = 0
        for i in self.fuels_new_enduse_specific:
            f += np.sum(self.fuels_new_enduse_specific[i])
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%YEAR22: " + str(data_ext['glob_var']['curr_yr']) + "  data  " + str(f))

        # Get 'peak demand day' (summarised over all enduses)
        self.fuels_peak_d = self.get_enduse_peak_d(data)

        # Get 'peak demand h' (summarised over all enduses)
        self.fuels_peak_h = self.get_enduse_peak_h(data)

        # Sum 'daily' demand in region (summarised over all enduses)
        self.fuels_tot_enduses_d = self.tot_all_enduses_d(data)

        # Sum 'hourly' demand in region (summarised over all enduses)
        self.fuels_tot_enduses_h = self.tot_all_enduses_h(data)

        # Calculate load factors from peak values
        self.reg_load_factor_d = self.load_factor_d(data)
        self.reg_load_factor_h = self.load_factor_h(data)

        # Calculate load factors from non peak values
        self.reg_load_factor_d_non_peak = self.load_factor_d_non_peak(data)
        self.reg_load_factor_h_non_peak = self.load_factor_h_non_peak(data)

        # Plot stacked end_uses
        #start_plot = mf.convert_date_to_yearday(2015, 1, 1) #regular day
        #fueltype_to_plot, nr_days_to_plot = 2, 1
        #self.plot_stacked_regional_end_use(nr_days_to_plot, fueltype_to_plot, start_plot, self.reg_name) #days, fueltype

        # Testing
        np.testing.assert_almost_equal(np.sum(self.fuels_tot_enduses_d), np.sum(self.fuels_tot_enduses_h), err_msg='The Regional disaggregation from d to h is false')

        test_sum = 0
        for enduse in self.fuels_new_enduse_specific:
            test_sum += np.sum(self.fuels_new_enduse_specific[enduse])
        np.testing.assert_almost_equal(np.sum(self.fuels_new), test_sum, err_msg='Summing end use specifid fuels went wrong')

    def fuel_correction_hp(self, hdd_cy, technological_stock):
        """Correct for different temperatures than base year. Also correct for different efficiencies

        hdd_cy : array
            Heating degree days for every day in current year

        Take as input the fuel shape of the HDD and calculate demand for constant efficiency (as in the case of boilers)

        Then calculate the demand in case of heat_pumps for the region and year

        Compare boielr and hp fuel demand and calculate factor. Then factor the demand and calculate new shape
        # Doest not consider real fuel changes

        -- Only relative change to boiler !
        """
        hp_heat_factor = np.zeros((365, 1)) # Initialise array for correcting fuel of every day

        # Calculate an array for a constant efficiency over every hour in a year
        for day, heat_d in enumerate(hdd_cy):
            d_factor = 0
            for hour, heat_share_h in enumerate(heat_d):
                d_factor += heat_share_h / getattr(technological_stock, 'heat_pump')[day][hour] # Hourly heat demand / heat pump efficiency
            hp_heat_factor[day][0] = np.sum(heat_share_h) / d_factor # Averae fuel fa ctor over the 24h of the day

        hp_shape = (1/np.sum(hp_heat_factor)) * hp_heat_factor

        return hp_shape

    def create_enduses(self, data, data_ext):
        """All enduses are initialised and inserted as an attribute of the Region Class

        All attributes from the Region Class are passed on to each enduse
        """
        # Iterate all enduses
        for enduse in data['resid_enduses']:
            Region.__setattr__(
                self,
                enduse, # Name of enduse
                EnduseResid(
                    self.reg_name,
                    data,
                    data_ext,
                    enduse,
                    self.enduses_fuel, #Masbe do weater correction not in region?
                    self.tech_stock_by,
                    self.tech_stock_cy,

                    self.heat_diff_factor,
                    self.cooling_diff_factor,
                    self.hdd_by,
                    self.cdd_by,
                    self.fuel_shape_y_h_hdd_hp_cy,
                    self.fuel_shape_y_h_hdd_boilers_cy
                    )
                )

    def tot_all_enduses_y(self, data):
        """Sum all fuel types over all end uses
        """
        sum_fuels = np.zeros((len(data['fuel_type_lu']), 1)) # Initialise

        for enduse in data['resid_enduses']:
            sum_fuels += self.__getattr__subclass__(enduse, 'enduse_fuelscen_driver') # Fuel of Enduse

        return sum_fuels

    def get_fuels_enduse_requested(self, enduse):
        """ TEST: READ ENDSE SPECIFID FROM"""
        fuels = self.__getattr__subclass__(enduse, 'enduse_fuelscen_driver')
        return fuels

    def enduse_specific_y(self, data):
        """Sum fuels for every fuel type for each enduse
        """
        sum_fuels_all_enduses = {}
        for enduse in data['resid_enduses']:
            sum_fuels_all_enduses[enduse] = np.zeros((len(data['fuel_type_lu']), 1))

        # Sum data
        for enduse in data['resid_enduses']:
            sum_fuels_all_enduses[enduse] += self.__getattr__subclass__(enduse, 'enduse_fuelscen_driver') # Fuel of Enduse
        return sum_fuels_all_enduses

    def tot_all_enduses_d(self, data):
        """Calculate total daily fuel demand for each fueltype
        """
        sum_fuels_d = np.zeros((len(data['fuel_type_lu']), 365))  # Initialise

        for enduse in data['resid_enduses']:
            sum_fuels_d += self.__getattr__subclass__(enduse, 'enduse_fuel_d')

        return sum_fuels_d

    def get_enduse_peak_d(self, data):
        """Summarise absolute fuel of peak days over all end_uses
        """
        sum_enduse_peak_d = np.zeros((len(data['fuel_type_lu']), 1))  # Initialise

        for enduse in data['resid_enduses']:
            sum_enduse_peak_d += self.__getattr__subclass__(enduse, 'enduse_fuel_peak_d') # Fuel of Enduse

        return sum_enduse_peak_d

    def get_enduse_peak_h(self, data):
        """Summarise peak value of all end_uses
        """
        sum_enduse_peak_h = np.zeros((len(data['fuel_type_lu']), 1, 24)) # Initialise

        for enduse in data['resid_enduses']:
            sum_enduse_peak_h += self.__getattr__subclass__(enduse, 'enduse_fuel_peak_h') # Fuel of Enduse

        return sum_enduse_peak_h

    def tot_all_enduses_h(self, data):
        """Calculate total hourly fuel demand for each fueltype
        """
        sum_fuels_h = np.zeros((len(data['fuel_type_lu']), 365, 24)) # Initialise

        for enduse in data['resid_enduses']:
            sum_fuels_h += self.__getattr__subclass__(enduse, 'enduse_fuel_h') #np.around(fuel_end_use_h,10)

        # Read out more error information (e.g. RuntimeWarning)
        #np.seterr(all='raise') # If not round, problem....np.around(fuel_end_use_h,10)
        return sum_fuels_h

    def load_factor_d(self, data):
        """Calculate load factor of a day in a year from peak values

        self.fuels_peak_d     :   Fuels for peak day (fueltype, data)
        self.fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data) for full year

        Return
        ------
        lf_d : array
            Array with load factor for every fuel type in %

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_d = np.zeros((len(data['fuel_type_lu']), 1))

        # Get day with maximum demand (in percentage of year)
        peak_d_demand = self.fuels_peak_d

        # Iterate fueltypes to calculate load factors for each fueltype
        for k, fueldata in enumerate(self.fuels_tot_enduses_d):
            average_demand = np.sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days

            if average_demand != 0:
                lf_d[k] = average_demand / peak_d_demand[k] # Calculate load factor

        lf_d = lf_d * 100 # Convert load factor to %
        return lf_d

    def load_factor_h(self, data):
        """Calculate load factor of a h in a year from peak data (peak hour compared to all hours in a year)

        self.fuels_peak_h     :   Fuels for peak day (fueltype, data)
        self.fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        lf_h : array
            Array with load factor for every fuel type [in %]

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_h = np.zeros((len(data['fuel_type_lu']), 1)) # Initialise array to store fuel

        # Iterate fueltypes to calculate load factors for each fueltype
        for fueltype, fueldata in enumerate(self.fuels_tot_enduses_h):

            # Maximum fuel of an hour of the peak day
            maximum_h_of_day = np.amax(self.fuels_peak_h[fueltype])

            #Calculate average in full year
            all_hours = []
            for day_hours in self.fuels_tot_enduses_h[fueltype]:
                for h in day_hours:
                    all_hours.append(h)
            average_demand_h = sum(all_hours) / (365 * 24) # Averae load = yearly demand / nr of days

            # If there is a maximum day hour
            if maximum_h_of_day != 0:
                average_demand_h = np.sum(fueldata) / (365 * 24) # Averae load = yearly demand / nr of days
                lf_h[fueltype] = average_demand_h / maximum_h_of_day # Calculate load factor

        lf_h = lf_h * 100 # Convert load factor to %

        return lf_h

    def load_factor_d_non_peak(self, data):
        """Calculate load factor of a day in a year from non-peak data

        self.fuels_peak_d     :   Fuels for peak day (fueltype, data)
        self.fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        lf_d : array
            Array with load factor for every fuel type in %

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_d = np.zeros((len(data['fuel_type_lu']), 1))

        # Iterate fueltypes to calculate load factors for each fueltype
        for k, fueldata in enumerate(self.fuels_tot_enduses_d):

            average_demand = sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days
            max_demand_d = max(fueldata)

            if  max_demand_d != 0:
                lf_d[k] = average_demand / max_demand_d # Calculate load factor

        lf_d = lf_d * 100 # Convert load factor to %
        return lf_d

    def load_factor_h_non_peak(self, data):
        """Calculate load factor of a h in a year from non-peak data

        self.fuels_peak_h     :   Fuels for peak day (fueltype, data)
        self.fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        lf_h : array
            Array with load factor for every fuel type [in %]

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_h = np.zeros((len(data['fuel_type_lu']), 1)) # Initialise array to store fuel

        # Iterate fueltypes to calculate load factors for each fueltype
        for fueltype, fueldata in enumerate(self.fuels_tot_enduses_h):

            all_hours = []
            for day_hours in self.fuels_tot_enduses_h[fueltype]:
                for h in day_hours:
                    all_hours.append(h)
            maximum_h_of_day_in_year = max(all_hours)

            average_demand_h = np.sum(fueldata) / (365 * 24) # Averae load = yearly demand / nr of days

            # If there is a maximum day hour
            if maximum_h_of_day_in_year != 0:
                lf_h[fueltype] = average_demand_h / maximum_h_of_day_in_year # Calculate load factor

        lf_h = lf_h * 100 # Convert load factor to %

        return lf_h

    def get_heating_demand_shape(self, data, data_ext, temperatures, year):
        """Calculate daily shape of heating demand based on calculating HDD for every day

        Based on temperatures of a year, the HDD are calculated for every
        day in a year. Based on the sum of all HDD of all days, the relative
        share of heat used for any day is calculated.

        The Heating Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        data : dict
            Base data dict
        data_ext : dict
            External data

        Return
        ------
        hdd_d : array
            Heating degree days for every day in a year (365, 1)

        Info
        -----
        The shape_d can be calcuated as follows: 1/ np.sum(hdd_d) * hdd_d

        #TODO: TEST
        # TODO: Linear or sigmoid diffusion of base temperature?
        """
        # Calculate base temperature for heating of current year #TODO: MAKE LINEAR
        t_base_heating_cy = mf.t_base_sigm(year, data['assumptions'], data_ext['glob_var']['base_yr'], data_ext['glob_var']['end_yr'], 't_base_heating')

        # Calculate hdd for every day (365,1)
        hdd_d = mf.calc_hdd(t_base_heating_cy, temperatures)

        return hdd_d

    def get_cooling_demand_shape(self, data, data_ext, temperatures, year):
        """Calculate daily shape of cooling demand based on calculating CDD for every day

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
        shape_d : array
            Fraction of heat for every day. Array-shape: 365, 1

        Info
        -----
        #TODO: TEST
        """
        t_base_cooling = mf.t_base_sigm(year, data['assumptions'], data_ext['glob_var']['base_yr'], data_ext['glob_var']['end_yr'], 't_base_cooling')

        cdd_d = mf.calc_cdd(t_base_cooling, temperatures) #current year

        #shape_d = cdd_d / np.sum(cdd_d)
        return cdd_d #shape_d, np.sum(cdd_d)

    def y_to_h_heat_hp(self, data, data_ext, hdd_cy, technological_stock):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump (not peak load shape)

        Refactor with fuel and in the end calc shape again
        # GREEN IS CORRECT
        Notes
        -----
        The share of fuel is taken instead of absolute fuels. But does not matter because if fuel is distributed accordingly
        #TODO: MAde after han
        """
        # From Daily to hourly
        shape_y_hp = np.zeros((365, 24))
        list_dates = mf.get_datetime_range(start=date(data_ext['glob_var']['base_yr'], 1, 1), end=date(data_ext['glob_var']['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):
            weekday = date_gasday.timetuple()[6] # 0: Monday
            if weekday == 5 or weekday == 6:
                daily_fuel_profile = (data['hourly_gas_shape_hp'][2] / np.sum(data['hourly_gas_shape_hp'][2])) # WkendHourly gas shape. Robert Sansom hp curve
            else:
                daily_fuel_profile = (data['hourly_gas_shape_hp'][1] / np.sum(data['hourly_gas_shape_hp'][1])) # Wkday Hourly gas shape. Robert Sansom hp curve

            # Calculate weighted average daily efficiency of heat pump
            av_daily_weig_eff = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):

                # Efficiency of technology #TODO: Fration of different heat pumps?
                tech_object = getattr(technological_stock, 'heat_pump')
                av_daily_weig_eff += heat_share_h * getattr(tech_object, 'eff_cy')[day][hour] # Hourly heat demand * heat pump efficiency
                #print("d_factor: " + str(heat_share_h)  + "   "+ str(heat_share_h) + "   " + (str(getattr(tech_object, 'eff_cy')[day][hour])) )

            # Recalculate fuel for day with heat pumps
            hp_daily_fuel = hdd_cy[day] / av_daily_weig_eff # Heat demand / efficiency = fuel

            # Distribute FUEL of day according to samson
            shape_y_hp[day] = hp_daily_fuel * daily_fuel_profile

        # ----Convert relative daily demand to hourly based on samson data
        hp_shape = (1/np.sum(shape_y_hp)) * shape_y_hp

        return hp_shape

    def y_to_h_heat_gas_boilers(self, data, data_ext, heating_shape):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        Assumption: Boiler have constant efficiency. The daily heat demand (calculated with hdd) is distributed within the day with robert sansom curve
        """
        shape_d_boilers = np.zeros((365, 24))

        list_dates = mf.get_datetime_range(start=date(data_ext['glob_var']['base_yr'], 1, 1), end=date(data_ext['glob_var']['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):
            weekday = date_gasday.timetuple()[6] # 0: Monday
            if weekday == 5 or weekday == 6:
                shape_d_boilers[day] = heating_shape[day] * (data['hourly_gas_shape'][2] / np.sum(data['hourly_gas_shape'][2])) # Wkend Hourly gas shape. Robert Sansom boiler curve
            else:
                shape_d_boilers[day] = heating_shape[day] * (data['hourly_gas_shape'][1] / np.sum(data['hourly_gas_shape'][1])) # Wkday Hourly gas shape. Robert Sansom boiler curve

        #TODO: ASSert if one
        return shape_d_boilers

    def __getattr__(self, attr):
        """Get method of own object
        """
        return self.attr

    def __getattr__subclass__(self, attr_main_class, attr_sub_class):
        """Get the attribute of a subclass"""
        object_class = getattr(self, attr_main_class)
        object_subclass = getattr(object_class, attr_sub_class)
        return object_subclass

    def plot_stacked_regional_end_use(self, nr_of_day_to_plot, fueltype, yearday, reg_name):
        """Plots stacked end_use for a region

        #TODO: Make that end_uses can be sorted, improve legend...

        0: 0-1
        1: 1-2
        2:

        #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
        """

        fig, ax = plt.subplots() #fig is needed
        nr_hours_to_plot = nr_of_day_to_plot * 24 #WHY 2?

        day_start_plot = yearday
        day_end_plot = (yearday + nr_of_day_to_plot)

        x = range(nr_hours_to_plot)

        legend_entries = []

        # Initialise (number of enduses, number of hours to plot)
        Y_init = np.zeros((len(self.enduses_fuel), nr_hours_to_plot))

        # Iterate enduse
        for k, enduse in enumerate(self.enduses_fuel):
            legend_entries.append(enduse)
            sum_fuels_h = self.__getattr__subclass__(enduse, 'enduses_fuel_h') #np.around(fuel_end_use_h,10)

            #fueldata_enduse = np.zeros((nr_hours_to_plot, ))
            list_all_h = []

            #Get data of a fueltype
            for _, fuel_data in enumerate(sum_fuels_h[fueltype][day_start_plot:day_end_plot]):

                for h in fuel_data:
                    list_all_h.append(h)

            Y_init[k] = list_all_h

        #color_list = ["green", "red", "#6E5160"]

        sp = ax.stackplot(x, Y_init)
        proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

        ax.legend(proxy, legend_entries)

        #ticks x axis
        ticks_x = range(24)
        plt.xticks(ticks_x)

        #plt.xticks(range(3), ['A', 'Big', 'Cat'], color='red')
        plt.axis('tight')

        plt.xlabel("Hours")
        plt.ylabel("Energy demand in GWh")
        plt.title("Stacked energy demand for region{}".format(reg_name))

        #from matplotlib.patches import Rectangle
        #legend_boxes = []
        #for i in color_list:
        #    box = Rectangle((0, 0), 1, 1, fc=i)
        #    legend_boxes.append(box)
        #ax.legend(legend_boxes, legend_entries)

        #ax.stackplot(x, Y_init)
        plt.show()


def plot_stacked_regional_end_use(self, nr_of_day_to_plot, fueltype, yearday, reg_name):
        """Plots stacked end_use for a region

        #TODO: Make that end_uses can be sorted, improve legend...

        0: 0-1
        1: 1-2
        2:

        #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
        """

        fig, ax = plt.subplots() #fig is needed
        nr_hours_to_plot = nr_of_day_to_plot * 24 #WHY 2?

        day_start_plot = yearday
        day_end_plot = (yearday + nr_of_day_to_plot)

        x = range(nr_hours_to_plot)

        legend_entries = []

        # Initialise (number of enduses, number of hours to plot)
        Y_init = np.zeros((len(self.enduse_fuel), nr_hours_to_plot))

        # Iterate enduse
        for k, enduse in enumerate(self.enduse_fuel):
            legend_entries.append(enduse)
            sum_fuels_h = self.__getattr__subclass__(enduse, 'enduse_fuel_h') #np.around(fuel_end_use_h,10)

            #fueldata_enduse = np.zeros((nr_hours_to_plot, ))
            list_all_h = []

            #Get data of a fueltype
            for _, fuel_data in enumerate(sum_fuels_h[fueltype][day_start_plot:day_end_plot]):

                for h in fuel_data:
                    list_all_h.append(h)

            Y_init[k] = list_all_h

        #color_list = ["green", "red", "#6E5160"]

        sp = ax.stackplot(x, Y_init)
        proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

        ax.legend(proxy, legend_entries)

        #ticks x axis
        ticks_x = range(24)
        plt.xticks(ticks_x)

        #plt.xticks(range(3), ['A', 'Big', 'Cat'], color='red')
        plt.axis('tight')

        plt.xlabel("Hours")
        plt.ylabel("Energy demand in GWh")
        plt.title("Stacked energy demand for region{}".format(reg_name))

        #from matplotlib.patches import Rectangle
        #legend_boxes = []
        #for i in color_list:
        #    box = Rectangle((0, 0), 1, 1, fc=i)
        #    legend_boxes.append(box)
        #ax.legend(legend_boxes, legend_entries)

        #ax.stackplot(x, Y_init)
        plt.show()

def residential_model_main_function(data, data_ext):
    """Main function of residential model

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally
    data_ext : dict
        All data provided externally

    Returns
    -------
    resid_object : object
        Object containing all regions as attributes for the residential model
    """
    fuel_in = test_function_fuel_sum(data) #SCRAP_ TEST FUEL SUM

    # Add all region instances as an attribute (region name) into the class `CountryResidentialModel`
    resid_object = CountryResidentialModel(data['lu_reg'], data, data_ext)

    print("READ OUT SPECIFIC ENDUSE FOR A REGION")
    #print(resid_object.get_specific_enduse_region('Wales', 'space_heating'))


    # ----------------------------
    # Attributes of whole country
    # ----------------------------
    fueltot = resid_object.tot_country_fuel # Total fuel of country
    country_enduses = resid_object.tot_country_fuel_enduse_specific # Total fuel of country for each enduse

    #TODO get tot_fuel_for_ever_enduse

    #TEST total fuel after run
    print("TEST MAIN START:" + str(fuel_in))
    print("Total Fuel after run: " + str(fueltot))
    print("DIFF: " + str(fueltot - fuel_in))

    return resid_object

class EnduseResid(object):
    """Class of an end use of the residential sector

    End use class for residential model. For every region, a different
    instance is generated.

    Parameters
    ----------
    reg_name : int
        The ID of the region. The actual region name is stored in `lu_reg`
    data : dict
        Dictionary containing data
    data_ext : dict
        Dictionary containing all data provided specifically for scenario run and from wrapper
    enduse : str
        Enduse given in a string
    enduse_fuel : array
        Fuel data for the region the endu

    Info
    ----------
    Every enduse can only have on shape independently of the fueltype

    #TODO: The technology switch also needs to be done for peak!
    """
    def __init__(self, reg_name, data, data_ext, enduse, enduse_fuel, tech_stock_by, tech_stock_cy, heat_diff_factor, cooling_diff_factor, hdd_by, cdd_by, fuel_shape_y_h_hdd_hp_cy, fuel_shape_y_h_hdd_boilers_cy):
        print("--Enduse: " + str(enduse))
        self.reg_name = reg_name
        self.enduse = enduse
        self.enduse_fuel = enduse_fuel[enduse] # Regional base fuel data

        # --Yearly fuel data (Check if always function below takes result from function above)
        self.enduse_fuel_after_weater_correction = self.weather_correction_hdd_cdd(cooling_diff_factor, heat_diff_factor)
        #print("A: " + str(np.sum(self.enduse_fuel_after_weater_correction)))

        # Enduse specific consumption change in % (due e.g. to other efficiciency gains). No technology considered
        self.enduse_fuel_after_specific_change = self.enduse_specifid_consumption_change(data_ext, data['assumptions'])
        print("FUEL TRAIN 1: " + str(self.enduse_fuel_after_specific_change))

        # Calculate changes in fuel based on fuel switches
        self.enduse_fuel_after_switch = self.enduse_fuel_switches(data_ext, data['assumptions'], tech_stock_by, tech_stock_cy, fuel_shape_y_h_hdd_boilers_cy)
        print("FUEL TRAIN 2: " + str(self.enduse_fuel_after_switch))


        '''# General efficiency gains of technology over time              //and TECHNOLOGY Switches WITHIN (not considering switching technologies across fueltypes)
        self.enduse_fuel_eff_gains = self.enduse_eff_gains(data_ext, data['assumptions']['tech_enduse_by'], tech_stock_by, tech_stock_cy)
        #print("B: " + str(np.sum(self.enduse_fuel_eff_gains)))
        '''
        # Calculate demand with changing elasticity (elasticity maybe on household level with floor area)
        self.enduse_fuel_after_elasticity = self.enduse_elasticity(data_ext, data['assumptions'])
        #print("D: " + str(np.sum(self.enduse_fuel_after_elasticity)))

        # Calcualte smart meter induced general savings
        self.enduse_fuel_smart_meter_eff_gains = self.smart_meter_eff_gain(data_ext, data['assumptions'])
        #print("E: " + str(np.sum(self.enduse_fuel_smart_meter_eff_gains)))

        # Calculate new fuel demands after scenario drivers TODO: THIS IS LAST MUTATION IN PROCESS... (all disaggreagtion function refer to this)
        self.enduse_fuelscen_driver = self.enduse_scenario_driver(data, data_ext)
        #print("F: " + str(np.sum(self.enduse_fuelscen_driver)))
        
        self.techologies_cy_after_switch = self.read_techologies_cy_after_switch()
        #print("G: " + str(np.sum(self.techologies_cy_after_switch)))

        #
        # TODO: CALCULATE FUEL SHARES OF HEATING TECHNOLOGY AND ASSING TO SPECIFIC CURVES
        # TODO: Calculate Shape for heating
        # fuel_shape_y_h_hdd_hp_cy,  --> fuel shape of hp
        # fuel_shape_y_h_hdd_boilers_cy --> fuel shape of boilers
        # Cooling specific shapes

        ##self.shape_cdd_by = cdd_by / np.sum(cdd_by) # shape fraction cooling base year
        ##self.shape_cdd_cy = (cdd_by * cooling_diff_factor) / np.sum(cdd_by) # calc fraction

        # Heating specific shapes
        ##self.shape_hdd_by = hdd_by / np.sum(hdd_by) # shape fraction heating base year
        ##self.shape_hdd_cy = (hdd_by * heat_diff_factor) / np.sum(hdd_by) # calc fraction (365,1)


        # --Current Year load shapes (adapt because of technology switch) (Shapes are identical for all fuel types)
        # Alter after technology_switch and fuel switch shapes depending on technology
        # --Base year load shapes (same load shape for all fuel types but not necessarily for all technologies within one enduse fuel)
        self.enduse_shape_d = data['dict_shp_enduse_d_resid'][enduse]['shape_d_non_peak']  # shape_d (365,1)
        self.enduse_shape_h = data['dict_shp_enduse_h_resid'][enduse]['shape_h_non_peak']  # shape_h (365,24)
        self.enduse_shape_peak_d = data['dict_shp_enduse_d_resid'][enduse]['shape_d_peak'] # shape_d peak (Factor to calc one day, percentages within every day)
        self.enduse_shape_peak_h = data['dict_shp_enduse_h_resid'][enduse]['shape_h_peak'] # shape_h peak
        self.enduse_shape_y_to_h = self.get_enduse_shape_y_to_h()                          # factor to calculate every hour demand from y demand

        # --Daily fuel data
        self.enduse_fuel_d = self.enduse_y_to_d()

        # --Hourly fuel data (% in h of day)
        self.enduse_fuel_h = self.enduse_d_to_h()

        # --Hourly_fuel_data_in_standard_year
        #self.enduse_fuel_y_to_h = self.enduse_y_to_h()

        # --Peak data
         # Calculate peak day (peak day)
        self.enduse_fuel_peak_d = self.enduse_peak_d() 
        # TODO: Efficiency gain in PEAK data
        # TODO: Fuel Switch in PEAK data

         # Calculate peak hour (peak hour)
        self.enduse_fuel_peak_h = self.enduse_peak_h()
        # TODO: Efficiency gain in PEAK data
        # TODO: Fuel Switch in PEAK data

        # TODO: ALL FUELS FOR DIFFERENT TECHNOLOGIES IN THIS ENDUSE

        # Testing
        np.testing.assert_almost_equal(np.sum(self.enduse_fuel_d), np.sum(self.enduse_fuel_h), decimal=5, err_msg='', verbose=True)
        #np.testing.assert_almost_equal(a,b) #np.testing.assert_almost_equal(self.enduse_fuel_d, self.enduse_fuel_h, decimal=5, err_msg='', verbose=True)

    def enduse_fuel_switches(self, data_ext, assumptions, tech_stock_by, tech_stock_cy, fuel_shape_y_h_hdd_boilers_cy):
        """ function steps to claculate fuel switches

        Step 1: Calculate service demand

        """
        print("============================================== FUEL SWITCH FUNCTION")

        if data_ext['glob_var']['curr_yr'] == data_ext['glob_var']['base_yr']: # If base year
            return self.enduse_fuel_after_specific_change
        elif self.enduse not in assumptions['installed_tech_switch']: # If no fuel switches for this enduse
            return self.enduse_fuel_after_specific_change

        new_fuels = copy.deepcopy(self.enduse_fuel_after_specific_change)

        # -----------------------------------------------------------------------------------------
        # Step 1: Calculate total regional energy service demand in a region (across all fueltypes)
        # -----------------------------------------------------------------------------------------
        tot_service_demand_h = mf.calc_regional_service_demand(fuel_shape_y_h_hdd_boilers_cy, assumptions['tech_enduse_by'][self.enduse], self.enduse_fuel_after_specific_change, assumptions['technologies'])
        print("tot_service_demand_h: " + str(np.sum(tot_service_demand_h)))

        # Iterate all technologies which are installed in fuel switches
        for tech_installed in assumptions['installed_tech_switch'][self.enduse]:
            print("--tech_installed: " + str(tech_installed))

            # -----------------------------------------------------------------------------------------
            # 2. Calculate and add fuel of newly installed technologies to fueltype of installed technology
            # -----------------------------------------------------------------------------------------

            # Read out sigmoid diffusion of energy service demand of this technology for the current year
            diffusion_energy_service_cy = mf.sigmoid_function(data_ext['glob_var']['curr_yr'], assumptions['sigm_parameters_tech'][self.enduse][tech_installed]['l_parameter'], assumptions['sigm_parameters_tech'][self.enduse][tech_installed]['midpoint'], assumptions['sigm_parameters_tech'][self.enduse][tech_installed]['steepness'])

            # Energy service demands
            service_demand_tech_installed_cy = diffusion_energy_service_cy * tot_service_demand_h # Share of service demand & total service demand
            print("service_demand_tech_installed_cy: " + str(service_demand_tech_installed_cy))

            # Convert energy service demand to fuel (service demand / efficiency cy )
            fuel_tech_installed_cy = np.sum(service_demand_tech_installed_cy / tech_stock_by.get_technology_attribute(tech_installed, 'eff_cy'))

            # Add fuels of installed technologies to existing fuel depending on fueltype of installed technology
            new_fuels[tech_stock_by.get_technology_attribute(tech_installed, 'fuel_type')][0] += fuel_tech_installed_cy

            # ---------------------------------------------------------------------------------------------------
            # 3. Remove fuel of replaced energy service demand proportinally to heat demand in base year
            # ---------------------------------------------------------------------------------------------------
            tot_heat_demand_switched_tech = 0 # Total replaced heat demand across different fueltypes
            fueltypes_replaced = [] # List with fueltypes where fuel is replaced

            # Iterate fuelswitches and read out the shares of fuel which is switched with the installed technology
            for fuelswitch in assumptions['resid_fuel_switches']:
                if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed:
                    fueltypes_replaced.append(fuelswitch['enduse_fueltype_replace'])

                    # Share of service demand per fueltype * fraction of fuel switched (CAN BE DONE BECAUSE HEAT DEMAND RELATIVE TO FUEL??)
                    tot_heat_demand_switched_tech += assumptions['service_demands_fueltypes'][self.enduse][fuelswitch['enduse_fueltype_replace']] * fuelswitch['share_fuel_consumption_switched']

            #print("dd")
            #print(assumptions['service_demands_fueltypes'])
            #print("tot_heat_demand_switched_tech")
            #print(tot_heat_demand_switched_tech)
            #print("......")
            #print(assumptions['service_demand_p'])
            print("Heat demand which is switched to this technology: " + str(tot_heat_demand_switched_tech))

            # Iterate all fueltypes which are affected in the technology installed
            for fueltype_replaced in fueltypes_replaced:
                print("------------------------------------------fueltype_replaced_--"  + str(fueltype_replaced))

                # Find fuel switch where this fueltype is replaced
                for fuelswitch in assumptions['resid_fuel_switches']:
                    if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed and fuelswitch['enduse_fueltype_replace'] == fueltype_replaced:

                        # share of total service of fueltype * share of replaced fuel (CAN BE DONE BECAUSE HEAT DEMAND IS PROPORTIONAL??)
                        relative_share = assumptions['service_demands_fueltypes'][self.enduse][fueltype_replaced] * fuelswitch['share_fuel_consumption_switched']
                        break

                # Service demand reduced for this fueltype (service technology cy (sigmoid diff) *  % of heat demand within fueltype)
                reduction_service_demand = service_demand_tech_installed_cy * ((1 / tot_heat_demand_switched_tech) * relative_share)
                print("reduction_service_demand: " + str(np.sum(reduction_service_demand)))

                # Service demand reduced per technology in this fueltype_replaced
                fueltype_technologies = assumptions['tech_enduse_by'][self.enduse][fueltype_replaced].keys()

                # Iterate all technologies in within the fueltype
                for technology_replaced in fueltype_technologies:
                    print("-------------heat demand within fueltype of technology: " + str(technology_replaced))

                    # Share of heat demand for technology in fueltype (share of heat demand within fueltype * reduction in servide demand)
                    service_demand_tech = assumptions['energy_service_p_fueltype'][self.enduse][fueltype_replaced][technology_replaced] * reduction_service_demand

                    # Convert service demand to fuel (service demand / eff of current year)
                    fuel_tech = service_demand_tech / tech_stock_cy.get_technology_attribute(technology_replaced, 'eff_cy')

                    # Substract fuel fuel
                    new_fuels[fueltype_replaced][0] -= np.sum(fuel_tech)

        return new_fuels

    def enduse_specifid_consumption_change(self, data_ext, assumptions):
        """Calculates fuel based on assumed overall enduse specific fuel consumption changes

        Either a sigmoid standard difufsion or linear diffusion can be implemented.

        Because for enduses where no technology stock is defined (and may consist of many different)
        technologies, a linear diffusion is suggested to best represent multiple
        sigmoid efficiency improvements of individual technologies.

        The changes are assumed across all fueltypes.

        Parameters
        ----------
        data_ext : dict
            Data

        assumptions : dict
            assumptions

        Returns
        -------
        out_dict : dict
            Dictionary containing new fuel demands for `enduse`

        Notes
        -----

        """
        percent_ey = assumptions['enduse_overall_change_ey'][self.enduse]  # Percent of fuel consumption in end year
        percent_by = 1.0                                                   # Percent of fuel consumption in base year (always 100 % per definition)
        diff_fuel_consump = percent_ey - percent_by                        # Percent of fuel consumption difference
        diffusion_choice = assumptions['other_enduse_mode_info']['diff_method'] # Diffusion choice

        if diff_fuel_consump == 0:# No change
            return self.enduse_fuel_after_weater_correction
        else:
            new_fuels = np.zeros((self.enduse_fuel_after_weater_correction.shape[0], 1)) #fueltypes, days, hours

            # Lineare diffusion up to cy
            if diffusion_choice == 'linear': #TODO: CHECK DIFF
                lin_diff_factor = mf.linear_diff(
                    data_ext['glob_var']['base_yr'],
                    data_ext['glob_var']['curr_yr'],
                    percent_by,
                    percent_ey,
                    len(data_ext['glob_var']['sim_period'])
                )
                change_cy = diff_fuel_consump * abs(lin_diff_factor) #NEW

            # Sigmoid diffusion up to cy
            if diffusion_choice == 'sigmoid':
                sig_diff_factor = mf.sigmoid_diffusion(data_ext['glob_var']['base_yr'], data_ext['glob_var']['curr_yr'], data_ext['glob_var']['end_yr'], assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'], assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness'])
                change_cy = diff_fuel_consump * sig_diff_factor

            # Calculate new fuel consumption percentage
            for fueltype, fuel in enumerate(self.enduse_fuel_after_weater_correction):
                new_fuels[fueltype] = fuel * (1 + change_cy)

            return new_fuels

    def weather_correction_hdd_cdd(self, cooling_diff_factor, heat_diff_factor):
        """Change fuel demand for heat and cooling service depending on
        changes in HDD and CDD within a region

        It is assumed that fuel consumption correlates directly with
        changes in HDD or CDD. This is plausible as today's share of heatpumps
        is only marginal.

        Returns
        -------
        out_dict : dict
            Dictionary containing new fuel demands for `enduse`

        Notes
        ---

        """
        new_fuels = np.zeros((self.enduse_fuel.shape[0], 1)) #fueltypes, days, hours

        if self.enduse == 'space_heating':
            for fueltype, fuel in enumerate(self.enduse_fuel):
                new_fuels[fueltype] = fuel * np.average(heat_diff_factor)
            return new_fuels

        elif self.enduse == 'cooling':
            for fueltype, fuel in enumerate(self.enduse_fuel):
                new_fuels[fueltype] = fuel * np.average(cooling_diff_factor)
            return new_fuels
        else:
            return self.enduse_fuel

    def read_techologies_cy_after_switch(self):
        """Read the faction of TOTAL enduse demand for each technology
        Assumption: Load shape is the same across all fueltypes
        """
        #for fuel in self.enduse_fuelscen_driver: #Iterate fuels
        pass

    def enduse_elasticity(self, data_ext, assumptions):
        """Adapts yearls fuel use depending on elasticity

        # TODO: MAYBE ALSO USE BUILDING STOCK TO SEE HOW ELASTICITY CHANGES WITH FLOOR AREA
        Maybe implement resid_elasticities with floor area

        # TODO: Non-linear elasticity. Then for cy the elasticity needs to be calculated

        Info
        ----------
        Every enduse can only have on shape independently of the fueltype
        """
        #try:
        if data_ext['glob_var']['curr_yr'] == data_ext['glob_var']['base_yr']:
            return self.enduse_fuel_after_switch
        else:
            new_fuels = np.zeros((self.enduse_fuel_after_switch.shape[0], 1)) #fueltypes, days, hours

            # End use elasticity
            elasticity_enduse = assumptions['resid_elasticities'][self.enduse]
            #elasticity_enduse_cy = nonlinear_def...

            for fueltype, fuel in enumerate(self.enduse_fuel_after_switch):

                if fuel != 0: # if fuel exists
                    fuelprice_by = data_ext['fuel_price'][data_ext['glob_var']['base_yr']][fueltype] # Fuel price by
                    fuelprice_cy = data_ext['fuel_price'][data_ext['glob_var']['curr_yr']][fueltype] # Fuel price ey
                    new_fuels[fueltype] = mf.apply_elasticity(fuel, elasticity_enduse, fuelprice_by, fuelprice_cy)
                else:
                    new_fuels[fueltype] = fuel
        return new_fuels

       # except Exception as err:
       #     print("ERROR: " + str(err.args))
       #     prnt("..")
       #     #logging.info("--")
       #     #logging.exception('I .Raised error in enduse_elasticity. Check if for every provided enduse an elasticity is provided')

    def enduse_eff_gains(self, data_ext, tech_frac_by, tech_stock_by, tech_stock_cy):
        """

        SPECIFIC EFF GAINS??
        
        Parameters
        ----------


        Returns
        -------
        out_dict : dict
            Dictionary containing new fuel demands for `enduse`

        Notes
        -----

        """
        if data_ext['glob_var']['curr_yr'] != data_ext['glob_var']['base_yr']:
            out_dict = np.zeros((self.enduse_fuel_after_specific_change.shape[0], 1))

            # Get technologies and share of technologies for each fueltype and enduse
            ##tech_frac_by = getattr(self.tech_stock_by, 'tech_frac_by')
            ##tech_frac_cy = getattr(self.tech_stock_cy, 'tech_frac_cy')

            # Assume no change in compostion of technologies
            tech_frac_cy = tech_frac_by # self.get_sigmoid_tech_diff(data, data_ext) #current year

            # Iterate fuels
            for fueltype, fueldata in enumerate(self.enduse_fuel_after_specific_change):

                
                # Iterate technologies and average efficiencies relative to distribution for base year
                overall_eff_by = 0
                for technology in tech_frac_by[self.enduse][fueltype]:
                    
                    # DIRECTAPROACH efficiency from fuel stoc ktech
                    tech_object_by= getattr(tech_stock_by, technology)
                    print("Ass " + str(tech_frac_by[self.enduse][fueltype][technology]) + str("  ") + str(np.average(getattr(tech_object_by, 'eff_cy'))))

                    # Overall efficiency: Share of technology * efficiency of base year technology
                    #overall_eff_by += np.sum(tech_frac_by[self.enduse][fueltype][technology] * getattr(self.tech_stock_by, technology)) #Only within FUELTYPE
                    overall_eff_by += np.sum(tech_frac_by[self.enduse][fueltype][technology] * getattr(tech_object_by, 'eff_cy')) #Only within FUELTYPE

                # Iterate technologies and average efficiencies relative to distribution for current year
                overall_eff_cy = 0

                for technology in tech_frac_cy[self.enduse][fueltype]:
                    
                    # DIRECTAPROACH efficiency from fuel stoc ktech
                    tech_object_cy= getattr(tech_stock_cy, technology)
                    print("Bsss " + str(tech_frac_cy[self.enduse][fueltype][technology]) + str("  ") + str(np.average(getattr(tech_object_cy, 'eff_cy'))))

                    # Overall efficiency: Share of technology * efficiency of base year technology
                    #overall_eff_cy += np.sum(tech_frac_cy[self.enduse][fueltype][technology] * getattr(self.tech_stock_cy, technology))
                    overall_eff_cy += np.sum(tech_frac_cy[self.enduse][fueltype][technology] * getattr(tech_object_cy, 'eff_cy'))

                # Calc new demand considering efficiency change
                if overall_eff_cy != 0: # Do not copy any values
                    print("yy:  " + str(technology) + str("  ") + str(data_ext['glob_var']['curr_yr']))

                    print("by: " + str(getattr(tech_object_by, 'eff_cy')[0][0]))
                    print("cy: " + str(getattr(tech_object_cy, 'eff_cy')[0][0]))
                    print("EFFICIENCY GAINS: " + str(self.enduse) + "  " + str((overall_eff_by / overall_eff_cy)))
                    out_dict[fueltype] = fueldata * (overall_eff_by / overall_eff_cy) # FROZEN old tech eff / new tech eff
                else:
                    out_dict[fueltype] = fueldata

            return out_dict
        else:
            return self.enduse_fuel_after_specific_change

    def smart_meter_eff_gain(self, data_ext, assumptions):
        """Calculate fuel savings depending on smart meter penetration

        The smart meter penetration is assumed with a sigmoid diffusion.

        In the assumptions the maximum penetration and also the 
        generally fuel savings for each enduse can be defined.

        Parameters
        ----------
        data_ext : dict
            External data
        assumptions : dict
            assumptions

        Returns
        -------
        new_fuels : array
            Fuels which are adapted according to smart meter penetration
        """
        if self.enduse in assumptions['general_savings_smart_meter']:
            new_fuels = np.zeros((self.enduse_fuel_after_elasticity.shape[0], 1)) #fueltypes, fuel

            # Sigmoid diffusion up to current year
            sigm_factor = mf.sigmoid_diffusion(data_ext['glob_var']['base_yr'], data_ext['glob_var']['curr_yr'], data_ext['glob_var']['end_yr'], assumptions['sig_midpoint'], assumptions['sig_steeppness'])

            # Smart Meter penetration (percentage of people having smart meters)
            penetration_by = assumptions['smart_meter_p_by']
            penetration_cy = assumptions['smart_meter_p_by'] + (sigm_factor * (assumptions['smart_meter_p_ey'] - assumptions['smart_meter_p_by']))

            for fueltype, fuel in enumerate(self.enduse_fuel_after_elasticity):

                # Saved fuel
                saved_fuel = fuel * (penetration_by - penetration_cy) * assumptions['general_savings_smart_meter'][self.enduse]
                #print("saved fuel--" + str(penetration_cy) + "-------" + str(self.enduse) + "------" + str(sigm_factor) + "--------" + str(np.sum(saved_fuel)))

                # New fuel
                new_fuels[fueltype] = fuel - saved_fuel

            return new_fuels
        else:
            return self.enduse_fuel_after_elasticity

    def enduse_scenario_driver(self, data, data_ext):
        """The fuel data for every end use are multiplied with respective scenario driver

        If no building specific scenario driver is found, the identical fuel is returned.

        The HDD is calculated seperately!

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_h : array
            Hourly fuel data [fueltypes, days, hours]

        Notes
        -----
        This is the energy end use used for disaggregating to daily and hourly
        """
        # Test if enduse has a building related scenario driver
        if hasattr(data['dw_stock'][self.reg_name][data_ext['glob_var']['base_yr']], self.enduse) and data_ext['glob_var']['curr_yr'] != data_ext['glob_var']['base_yr']:

            # Scenariodriver of building stock base year and new stock
            by_driver = getattr(data['dw_stock'][self.reg_name][data_ext['glob_var']['base_yr']], self.enduse) # Base year building stock
            cy_driver = getattr(data['dw_stock'][self.reg_name][data_ext['glob_var']['curr_yr']], self.enduse) # Current building stock

            factor_driver =  cy_driver / by_driver # FROZEN Here not effecieicny but scenario parameters!   base year / current (checked) (as in chapter 3.1.2 EQ E-2)

            return self.enduse_fuel_smart_meter_eff_gains * factor_driver

        else:
            #print("Enduse has not driver or is base year: " + str(self.enduse))
            return self.enduse_fuel_smart_meter_eff_gains

    #def get_enduse_y_to_h():
    #    """Disaggregate yearly fuel data to hourly fuel data"""
    #    fuels_y_to_h = np.zeros((len(self.enduse_fuel), 365, 24))
    #
    #    returnfuels_y_to_h

    def enduse_y_to_d(self):
        """Generate array with fuels for every day
        """
        fuels_d = np.zeros((len(self.enduse_fuel), 365))

        for k, fuels in enumerate(self.enduse_fuelscen_driver):
            fuels_d[k] = self.enduse_shape_d[:, 0] * fuels[0] # enduse_shape_d is  a two dim array with load shapes in first row

        return fuels_d

    def get_enduse_shape_y_to_h(self):
        """ Get percentage of every hour of a full year
        """
        return self.enduse_shape_d * self.enduse_shape_h

    def enduse_d_to_h(self):
        """Disaggregate yearly fuel data to every day in the year

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_h : array
            Hourly fuel data [fueltypes, days, hours]

        Notes
        -----
        """
        fuels_h = np.zeros((self.enduse_fuel_d.shape[0], 365, 24)) #fueltypes, days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel in enumerate(self.enduse_fuel_d):
            for day in range(365):
                fuels_h[k][day] = self.enduse_shape_h[day] * fuel[day]

        return fuels_h

    def enduse_peak_d(self):
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
        fuels_d_peak = np.zeros((len(self.enduse_fuel), 1))


        for k, fueltype_year_data in enumerate(self.enduse_fuelscen_driver):
            fuels_d_peak[k] = self.enduse_shape_peak_d * fueltype_year_data[0]

        return fuels_d_peak

    def enduse_peak_h(self):
        """Disaggregate daily peak day fuel data to the peak hours.

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_h_peak : array
            Hourly fuel data [fueltypes, peakday, peak_hours]

        Notes
        -----
        """
        fuels_h_peak = np.zeros((self.enduse_fuel_d.shape[0], 1, 24)) #fueltypes  days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel_data in enumerate(self.enduse_fuel_peak_d):
            for day in range(1):
                
                #TODO: Differentiate between technologies as they might have different fuel shapes and different fuel shares
                fuels_h_peak[k][day] = self.enduse_shape_peak_h * fuel_data[day]

        return fuels_h_peak

class CountryResidentialModel(object):
    """Class of a country containing all regions as self.attributes

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_names : list
        Dictionary containign the name of the Region (unique identifier)
    data : dict
        Main data dictionary
    data_ext : dict
        Main external data

    Notes
    -----
    this class has as many attributes as regions (for evry rgion an attribute)
    """
    def __init__(self, reg_names, data, data_ext):
        """Constructor of the class which holds all regions of a country
        """

        # Create object for every region
        self.create_regions(reg_names, data, data_ext)



        # Functions to summarise data for all Regions in the CountryResidentialModel class
        self.tot_country_fuel = self.get_overall_sum(reg_names)
        self.tot_country_fuel_enduse_specific = self.get_sum_for_each_enduse(data, reg_names)

        # TESTER: READ OUT Specific ENDUSE for a REGION
        #print("AA: " + str(self.get_specific_enduse_region('Wales', 'space_heating')))


        # ----- Testing
        n = 0
        for i in self.tot_country_fuel_enduse_specific:
            n += self.tot_country_fuel_enduse_specific[i]
        #print("============================ddddddddddd= " + str(self.tot_country_fuel))

        # TESTING
        test_sum = 0
        for enduse in self.tot_country_fuel_enduse_specific:
            test_sum += self.tot_country_fuel_enduse_specific[enduse]
        np.testing.assert_almost_equal(np.sum(self.tot_country_fuel), test_sum, decimal=5, err_msg='', verbose=True)

    def create_regions(self, reg_names, data, data_ext):
        """Create all regions and add them as attributes based on region name to the CountryResidentialModel Class

        Parameters
        ----------
        reg_names : list
            The name of the Region (unique identifier)
        """
        for reg_name in reg_names:
            CountryResidentialModel.__setattr__(
                self,
                str(reg_name), # Region identifiyer is converted into a string
                Region(reg_name, data, data_ext) #: Create a Region
                )

    def get_specific_enduse_region(self, spec_region, spec_enduse):
        _a = getattr(self, spec_region)
        enduse_fuels = _a.get_fuels_enduse_requested(spec_enduse)
        return enduse_fuels

    def get_overall_sum(self, reg_names):
        """Collect hourly data from all regions and sum across all fuel types and enduses
        """
        tot_sum = 0
        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name)) # Get region

            # Get fuel data of region #Sum hourly demand # could also be read out as houly
            tot_sum += np.sum(getattr(reg_object, 'fuels_tot_enduses_h'))

        return tot_sum

    def get_sum_for_each_enduse(self, data, reg_names):
        """Collect end_use specific hourly data from all regions and sum across all fuel types

        out: {enduse: sum(all_fuel_types)}

        """
        tot_sum_enduses = {}
        for enduse in data['resid_enduses']:
            tot_sum_enduses[enduse] = 0

        for reg_name in reg_names:
            reg_object = getattr(self, str(reg_name)) # Get region

            # Get fuel data of region
            enduse_fuels_reg = getattr(reg_object, 'fuels_new_enduse_specific')
            for enduse in enduse_fuels_reg:
                tot_sum_enduses[enduse] += np.sum(enduse_fuels_reg[enduse]) # sum across fuels

        return tot_sum_enduses










# ------------- Testing functions
def test_function_fuel_sum(data):
    """ Sum raw disaggregated fuel data """
    fuel_in = 0
    for reg in data['fueldata_disagg']:
        for enduse in data['fueldata_disagg'][reg]:
            fuel_in += np.sum(data['fueldata_disagg'][reg][enduse])
    return fuel_in













'''#Scrap-------------------------------------------------
        #Scrap-------------------------------------------------
        #Scrap-------------------------------------------------
        boiler_efficiency_BY = 0.5

        hp_eff = mf.get_heatpump_eff(self.temp_by, -0.05, 2)
        boiler_eff = self.const_eff_y_to_h(boiler_efficiency_BY)

        # Share of final FUEL demand for each technology?
        tot_fuel = 555
        tot_heat = boiler_eff * (self.fuel_shape_y_h_hdd_boilers_cy * tot_fuel) #Boiler eff & fuel demand of each day

        # Fraction of 
        share_heat_wished_hp = 0.5
        share_heat_wished_boilers = 0.5

        share_heat_hp = tot_heat * share_heat_wished_hp
        share_heat_boiler = tot_heat * share_heat_wished_boilers

        # Calculate absolute fuel depending on wished end use share in heat
        abs_fuel_hp = np.sum(share_heat_hp / hp_eff)
        abs_fuel_boilers = np.sum(share_heat_boiler / boiler_eff)
        print("dd: " + str(np.sum(tot_heat / boiler_eff)))
        print("abs_fuel_hp: " + str(abs_fuel_hp))
        print("abs_fuel_boilers: " + str(abs_fuel_boilers))

        # Distribute fuel according to shape 

        prnt(":.")
        hp_heat = tot_fuel * share_heat_wished_hp
        boiler_heat = tot_fuel * share_heat_wished_boilers

        # FUEL NEEDED if jeweils 100% der technology
        print("SHAPES")
        print(np.sum(self.fuel_shape_y_h_hdd_boilers_cy))
        print(np.sum(self.fuel_shape_y_h_hdd_hp))

        total_heat_if_100_boiler = np.sum(boiler_eff * (self.fuel_shape_y_h_hdd_boilers_cy * tot_fuel))
        total_heat_if_100_hpp = np.sum(hp_eff * (self.fuel_shape_y_h_hdd_hp * tot_fuel))

        print("TOTAL HEAT NEEDED if 100 BOILER " + str(total_heat_if_100_boiler))
        print("EFF: " + str(total_heat_if_100_boiler / tot_fuel))
        print("TOTAL HEAT NEEDED if 100 HP " + str(total_heat_if_100_hpp))
        print("EFF: " + str(total_heat_if_100_hpp / tot_fuel))

        #print("FUEL BOILER: " + str(hp_heat * ))
        print("FUEL hp: " + str())

        print("---")
        print("HEAT NEEDED FOR 100% BOILER: " + str(boiler_eff * (self.fuel_shape_y_h_hdd_boilers_cy * tot_fuel)))
        print("FUEL NEEDED FOR 100% HP:     " + str(hp_eff * (self.fuel_shape_y_h_hdd_hp * tot_fuel)))

        share_boiler = 0.5
        share_hp = 0.5
        tot_f = (share_boiler / np.sum(boiler_eff)) + (share_hp / np.sum(hp_eff))
        fuel_boilers = tot_fuel * (1 / tot_f) * (share_boiler / np.sum(boiler_eff))
        fuel_hp = tot_fuel *(1 / tot_f) * (share_hp / np.sum(hp_eff))
        print("fuel_boilers " + str(fuel_boilers))
        print("fuel_hp      " + str(fuel_hp))

        # Plot HP and Gas shape for 
        plt.plot(range(24), self.fuel_shape_y_h_hdd_boilers_cy[100], 'red') #boiler shape
        plt.plot(range(24), self.fuel_shape_y_h_hdd_hp[100], 'green') #hp shape
        plt.show()
        
        # plot with fuels
        plt.plot(range(24), self.fuel_shape_y_h_hdd_boilers_cy[0] * fuel_boilers, 'red') #boiler shape
        plt.plot(range(24), self.fuel_shape_y_h_hdd_hp[0] * fuel_hp, 'green') #Gas shape

        plt.show()


        print("..")
        prnt("..")

        #Scrap-------------------------------------------------
        #Scrap-------------------------------------------------
    #Scrap-------------------------------------------------
    '''