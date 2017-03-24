"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
import energy_demand.technological_stock as ts

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
    # TESTING
    fuel_in = 0
    for reg in data['fueldata_disagg']:
        for enduse in data['fueldata_disagg'][reg]: 
            fuel_in += np.sum(data['fueldata_disagg'][reg][enduse])
    print("TEST MAIN START:" + str(fuel_in))

    # Generate technological stock for base year
    data['tech_stock_cy'] = ts.ResidTechStock(data, data_ext, data_ext['glob_var']['current_year'])

    # Add all region instances as an attribute (region name) into a Country class
    resid_object = Country_residential_model(data['reg_lu'], data, data_ext)

    # Total fuel of country
    fueltot = resid_object.tot_reg_fuel

    #TEST total fuel after run 
    print("TEST MAIN START:" + str(fuel_in))
    print("Total Fuel after run: " + str(fueltot))
    print("DIFF: " + str(fueltot - fuel_in))

    return resid_object

class Country_residential_model(object):
    """Class of a country containing all regions for the different enduses

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_id : int
        The ID of the region. The actual region name is stored in `reg_lu`

    Notes
    -----
    this class has as many attributes as regions (for evry rgion an attribute)
    """
    def __init__(self, sub_reg_names, data, data_ext):
        """Constructor or Region"""
        self.data = data
        self.data_ext = data_ext
        self.sub_reg_names = sub_reg_names


        self.create_regions() #: create object for every region
        self.tot_reg_fuel = self.get_overall_sum()

    def create_regions(self):
        """Create all regions and add them as attributes based on region name to this class"""
        for reg_ID in self.sub_reg_names:

            # Region object
            reg_object = Region(reg_ID, self.data, self.data_ext)

            # Create an atribute for every regions ()
            Country_residential_model.__setattr__(self, str(reg_ID), reg_object)

    def get_overall_sum(self):
        """Collect hourly data from all regions and sum across all fuel types"""
        tot_sum = 0
        for reg_id in self.data['reg_lu']:
            reg_object = getattr(self, str(reg_id)) # Get region
            # Get fuel data of region #Sum hourly demand # could also be read out as houly
            tot_sum += np.sum(getattr(reg_object, 'fuels_tot_enduses_h'))

        return tot_sum

class Region(object):
    """Class of a region for the residential model

    The main class of the residential model. For every region, a Region object needs to be generated.

    Parameters
    ----------
    reg_id : int
        The ID of the region. The actual region name is stored in `reg_lu`
    data : dict
        Dictionary containing data
    data_ext : dict
        Dictionary containing all data provided specifically for scenario run and from wrapper.abs

    # TODO: CHECK IF data could be reduced as input (e.g. only provide fuels and not data)
    """
    def __init__(self, reg_id, data, data_ext):
        """Constructor or Region"""
        self.reg_id = reg_id                                        # ID of region
        self.data = data                                            # data
        self.data_ext = data_ext                                    # external data
        self.assumptions = data['assumptions']
        self.current_year = data_ext['glob_var']['current_year']    # Current year
        self.reg_fuel = data['fueldata_disagg'][reg_id]             # Fuel array of region (used to extract all end_uses)

        # Set attributs of all enduses
        self.create_enduse_objects()

        # Sum final 'yearly' fuels (summarised over all enduses)
        self.fuels_new = self.tot_all_enduses_y()

        # Get 'peak demand day' (summarised over all enduses)
        self.enduse_fuel_peak_d = self.get_enduse_peak_d()

        # Get 'peak demand h' (summarised over all enduses)
        self.enduse_fuel_peak_h = self.get_enduse_peak_h()

        # Sum 'daily' demand in region (summarised over all enduses)
        self.fuels_tot_enduses_d = self.tot_all_enduses_d()

        # Sum 'hourly' demand in region (summarised over all enduses)
        self.fuels_tot_enduses_h = self.tot_all_enduses_h()

        # Testing
        np.testing.assert_almost_equal(np.sum(self.fuels_tot_enduses_d), np.sum(self.fuels_tot_enduses_h), err_msg='The Regional disaggregation from d to h is false')
        # add some more

        # Calculate load factors
        self.reg_load_factor_d = self.load_factor_d()
        self.reg_load_factor_h = self.load_factor_h()

        # Plot stacked end_uses
        start_plot = mf.convert_date_to_yearday(2015, 1, 1) #regular day
        fueltype_to_plot, nr_days_to_plot = 2, 1
        #self.plot_stacked_regional_end_use(nr_days_to_plot, fueltype_to_plot, start_plot, self.reg_id) #days, fueltype

    def create_enduse_objects(self):
        """All enduses are initialised and inserted as an attribute of the Region Class"""

        # Iterate enduses
        for enduse in self.reg_fuel:

            # Enduse object
            enduse_object = EndUseClassResid(self.reg_id, self.data, self.data_ext, enduse, self.reg_fuel)

            #self.end_uses[enduse] = EndUseClassResid(self.reg_id, self.data, self.data_ext, enduse, self.reg_fuel)  super(MyTest, self).
            Region.__setattr__(self, enduse, enduse_object)

    def tot_all_enduses_y(self):
        """Sum all fuel types over all end uses"""
        sum_fuels = np.zeros((len(self.data['fuel_type_lu']), 1)) # Initialise

        for enduse in self.reg_fuel:
            sum_fuels += self.__getattr__subclass__(enduse, 'reg_fuelscen_driver') # Fuel of Enduse

        return sum_fuels

    def tot_all_enduses_d(self):
        """Calculate total daily fuel demand for each fueltype"""
        sum_fuels_d = np.zeros((len(self.data['fuel_type_lu']), 365))  # Initialise

        for enduse in self.reg_fuel:
            sum_fuels_d += self.__getattr__subclass__(enduse, 'reg_fuel_d')

        return sum_fuels_d

    def get_enduse_peak_d(self):
        """Summarise peak value of all end_uses"""
        sum_enduse_peak_d = np.zeros((len(self.data['fuel_type_lu']), 1))  # Initialise

        for enduse in self.reg_fuel:
            sum_enduse_peak_d += self.__getattr__subclass__(enduse, 'enduse_fuel_peak_d') # Fuel of Enduse

        return sum_enduse_peak_d

    def get_enduse_peak_h(self):
        """Summarise peak value of all end_uses"""
        sum_enduse_peak_h = np.zeros((len(self.data['fuel_type_lu']), 1, 24)) # Initialise

        for enduse in self.reg_fuel:
            sum_enduse_peak_h += self.__getattr__subclass__(enduse, 'enduse_fuel_peak_h') # Fuel of Enduse

        return sum_enduse_peak_h

    def tot_all_enduses_h(self):
        """Calculate total hourly fuel demand for each fueltype"""
        sum_fuels_h = np.zeros((len(self.data['fuel_type_lu']), 365, 24)) # Initialise

        for enduse in self.reg_fuel:
            sum_fuels_h += self.__getattr__subclass__(enduse, 'enduse_fuel_h') #np.around(fuel_end_use_h,10)

        # Read out more error information (e.g. RuntimeWarning)
        #np.seterr(all='raise') # If not round, problem....np.around(fuel_end_use_h,10)
        return sum_fuels_h

    def load_factor_d(self):
        """Calculate load factor of a day in a year"""
        lf_y = np.zeros((len(self.data['fuel_type_lu']), 1)) # Initialise

        maximum_d = self.enduse_fuel_peak_d

        # Iterate fueltypes to calculate load factors for each fueltype
        for k, data_fueltype in enumerate(self.fuels_tot_enduses_d):

            # Averae load = yearly demand / nr of days
            average_demand = np.sum(data_fueltype) / 365

            # Calculate load factor
            lf_y[k] = average_demand / maximum_d[k]

        return lf_y

    def load_factor_h(self):
        """Calculate load factor of a h in a year
        # TODO: PEAK CAlculations are still wrong

        # Note retirmd as [%]...
        """
        # Initialise array to store fuel
        lf_y = np.zeros((len(self.data['fuel_type_lu']), 1))

        # Iterate fueltypes to calculate load factors for each fueltype
        for fueltype, data_fueltype in enumerate(self.fuels_tot_enduses_h):
            #print("FUELTYPE: " + str(fueltype))
            maximum_h_of_day = np.amax(self.enduse_fuel_peak_h[fueltype])

            #print("maximum_h_of_day: " + str(maximum_h_of_day))

            # If there is a maximum day hour
            if maximum_h_of_day != 0:

                # Averae load = yearly demand / nr of days
                average_demand_h = np.sum(data_fueltype) / (365 * 24)
                #print("data_fueltype:    " + str(np.sum(data_fueltype)))
                #print("average_demand_h: " + str(average_demand_h))

                # Calculate load factor
                lf_y[fueltype] = average_demand_h / maximum_h_of_day

        #print("lf_y: " + str(lf_y))
        return lf_y

    def __getattr__(self, attr):
        """Get method of own object"""
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
        Y_init = np.zeros((len(self.reg_fuel), nr_hours_to_plot))

        # Iterate enduse
        for k, enduse in enumerate(self.reg_fuel):
            legend_entries.append(enduse)
            sum_fuels_h = self.__getattr__subclass__(enduse, 'enduse_fuel_h') #np.around(fuel_end_use_h,10)

            #data_fueltype_enduse = np.zeros((nr_hours_to_plot, ))
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

class EndUseClassResid(object): #OBJECT OR REGION? --> MAKE REGION IS e.g. data is loaded from parent class
    """Class of an end use category of the residential sector

    End use class for residential model. For every region, a different
    instance is generated.

    Parameters
    ----------
    reg_id : int
        The ID of the region. The actual region name is stored in `reg_lu`
    data : dict
        Dictionary containing data
    data_ext : dict
        Dictionary containing all data provided specifically for scenario run and from wrapper
    enduse : str
        Enduse given in a string
    reg_fuel : array
        Fuel data for the region the endu

    Info
    ----------
    Every enduse can only have on shape independently of the fueltype

    """
    def __init__(self, reg_id, data, data_ext, enduse, reg_fuel):

        # Call parent data
        #super().__init__(reg_id, data, data_ext)

        # --General data, fueldata, technological stock
        self.reg_id = reg_id                                        # Region
        self.enduse = enduse                                        # EndUse Name
        self.current_year = data_ext['glob_var']['current_year']    # from parent class
        self.base_year = data_ext['glob_var']['base_year']          # from parent class
        self.data = data                                            # from parent class
        self.data_ext = data_ext                                    # from parent class
        self.assumptions = data['assumptions']                      # Assumptions from regions
        self.reg_fuel = reg_fuel[enduse]                            # Regional base fuel data
        self.tech_stock_by = data['tech_stock_by']                  # Technological stock base_data['tech_stock_by']
        self.tech_stock_cy = data['tech_stock_cy']                  # Technological stock base_data['tech_stock_by']

        # --Load shapes
        self.enduse_shape_d = data['dict_shp_enduse_d_resid'][enduse]['shape_d_non_peak']  # shape_d
        self.enduse_shape_h = data['dict_shp_enduse_h_resid'][enduse]['shape_h_non_peak']  # shape_h
        self.enduse_shape_peak_d = data['dict_shp_enduse_d_resid'][enduse]['shape_d_peak'] # shape_d peak (Factor to calc one day)
        self.enduse_shape_peak_h = data['dict_shp_enduse_h_resid'][enduse]['shape_h_peak'] # shape_h peak

        # --Yearly fuel data (Check if always function below takes result from function above)
        print("ENDUSE: " + str(self.enduse))

        self.reg_fuel_eff_gains = self.enduse_eff_gains()                # General efficiency gains of technology over time
        print("AAA: " + str(np.sum(self.reg_fuel_eff_gains)))

        self.reg_fuel_after_switch = self.enduse_fuel_switches()         # Calculate fuel switches
        print("bbb: " + str(np.sum(self.reg_fuel_after_switch)))

        self.reg_fuel_after_elasticity = self.enduse_elasticity()        # Calculate demand with changing elasticity (elasticity maybe on household level with floor area)
        print("ccc: " + str(np.sum(self.reg_fuel_after_elasticity)))

        self.reg_fuelscen_driver = self.enduse_scenario_driver()         # Calculate new fuel demands after scenario drivers TODO: THIS IS LAST MUTATION IN PROCESS... (all disaggreagtion function refer to this)
        print("DDD: " + str(np.sum(self.reg_fuelscen_driver)))


        # --Daily fuel data
        self.reg_fuel_d = self.enduse_y_to_d()                           # Disaggregate yearly demand for every day

        # --Hourly fuel data
        self.enduse_fuel_h = self.enduse_d_to_h()                        # Disaggregate daily demand to hourly demand
        self.enduse_fuel_peak_d = self.enduse_peak_d()                   # Calculate peak day
        self.enduse_fuel_peak_h = self.enduse_peak_h()                   # Calculate peak hour

        # Testing
        np.testing.assert_almost_equal(np.sum(self.reg_fuel_d), np.sum(self.enduse_fuel_h), decimal=7, err_msg='', verbose=True)
        #np.testing.assert_almost_equal(a,b) #np.testing.assert_almost_equal(self.reg_fuel_d, self.enduse_fuel_h, decimal=5, err_msg='', verbose=True)

    def enduse_elasticity(self):
        """Adapts yearls fuel use depending on elasticity

        # TODO: MAYBE ALSO USE BUILDING STOCK TO SEE HOW ELASTICITY CHANGES WITH FLOOR AREA
        Maybe implement resid_elasticities with floor area

        # TODO: Non-linear elasticity. Then for cy the elasticity needs to be calculated

        Info
        ----------
        Every enduse can only have on shape independently of the fueltype

        """
        new_fuels = np.zeros((self.reg_fuel_after_switch.shape[0], 1)) #fueltypes, days, hours

        # End use elasticity
        elasticity_enduse = self.assumptions['resid_elasticities'][self.enduse]
        #elasticity_enduse_cy = nonlinear_def...

        for fueltype, fuel in enumerate(self.reg_fuel_after_switch):

            if fuel != 0: # if fuel exists
                # Fuel prices
                fuelprice_by = self.data_ext['fuel_price'][self.base_year][fueltype]
                fuelprice_cy = self.data_ext['fuel_price'][self.current_year][fueltype]

                new_fuels[fueltype] = mf.apply_elasticity(fuel, elasticity_enduse, fuelprice_by, fuelprice_cy)

            else:
                new_fuels[fueltype] = fuel
        print("enduse:  " + str(self.enduse))
        print(elasticity_enduse)
        print(self.reg_fuel_after_switch)
        print("....")
        print(new_fuels)
        return new_fuels

    def enduse_eff_gains(self):
        """Adapts yearls fuel use depending on technology mix within each fueltypes (e.g. boiler_elcA to boiler_elecB)

        This function implements technology switch within each enduse. (Does not consider share of fuel which is switched)

        1. The technological fraction of each enduse is read
        2. The efficiencies of base and current year of all years are read ind
        3. Overall efficiency of all technologies is used

        Returns
        -------
        out_dict : dict
            Dictionary containing new fuel demands for `enduse`

        Notes
        -----
        In this function the change in fuel is calculated for the enduse
        only based on the change in the fraction of technology (technology stock)
        composition.

        It does not consider fuel switches (e.g. % of fuel which is replaced) for
        an enduse but only calculated within each fuel type.

        # Will maybe be on household level
        """
        out_dict = np.zeros((self.reg_fuel.shape[0], 1))

        # Get technologies and share of technologies for each fueltype and enduse
        tech_frac_by = getattr(self.tech_stock_by, 'tech_frac')
        tech_frac_cy = getattr(self.tech_stock_cy, 'tech_frac')

        # Iterate fuels
        for fueltype, fueldata in enumerate(self.reg_fuel):

            # Iterate technologies and average efficiencies relative to distribution for base year
            overall_eff_by = 0
            for technology in tech_frac_by[self.enduse][fueltype]:

                # Overall efficiency: Share of technology * efficiency of base year technology
                overall_eff_by += tech_frac_by[self.enduse][fueltype][technology] * getattr(self.tech_stock_by, technology)

            # Iterate technologies and average efficiencies relative to distribution for curren
            overall_eff_cy = 0
            for technology in tech_frac_cy[self.enduse][fueltype]:

                # Overall efficiency: Share of technology * efficiency of base year technology
                overall_eff_cy += tech_frac_cy[self.enduse][fueltype][technology] * getattr(self.tech_stock_cy, technology)

            # Calc new demand considering efficiency change
            if overall_eff_cy != 0: # Do not copy any values
                out_dict[fueltype] = fueldata * (overall_eff_by / overall_eff_cy) #TODO: Ev umgekehrt
            else:
                out_dict[fueltype] = fueldata

        return out_dict

    def enduse_fuel_switches(self):
        """Calculates absolute fuel changes from assumptions about switches in changes of fuel percentages
        It also considers technological efficiency changes of replaced and old technologies.

        Replace fuel percentages (sigmoid fasion) with a technology

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuel_switch_array : array
            tbd

        Notes
        -----
        """
        # Share of fuel types for each end use
        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse] # Base year
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse] # End year    #Maximum change in % of fueltype up to endyear

        # Test whether share of fuel types stays identical
        if np.array_equal(fuel_p_by, fuel_p_ey): # no fuel switches
            return self.reg_fuel
        else:
            fuel_switch_array = np.copy((self.reg_fuel)) # Out_dict initialisation

            # Assumptions about which technology is installed and replaced
            tech_install = self.assumptions['tech_install'][self.enduse] #  Technology which is installed
            eff_replacement = getattr(self.tech_stock_cy, tech_install)

            tech_replacement_dict = self.assumptions['tech_replacement_dict'][self.enduse] #  Dict with current technologes which are to be replaced

            #print("tech_replacement_dict")
            #print(tech_replacement_dict)

            #print("fuel_p_ey " + str(fuel_p_ey))
            #print("fuel_p_by " + str(fuel_p_by))

            # Calculate percentage differences over full simulation period
            ###fuel_diff = fuel_p_ey[:, 1] - fuel_p_by[:, 1] # difference in percentage (ID gets wasted because it is substracted)
            #print("fuel_diff: " + str(fuel_diff))

            # Calculate sigmoid diffusion of fuel switches
            ###fuel_p_cy = fuel_diff * tf.sigmoidefficiency(self.data_ext['glob_var']['base_year'], self.current_year, self.data_ext['glob_var']['end_year'])
            fuel_p_cy = fuel_p_by * tf.sigmoidefficiency(self.data_ext['glob_var']['base_year'], self.current_year, self.data_ext['glob_var']['end_year'])
            #print("fuel_p_cy:" + str(fuel_p_cy))
            #print(fuel_p_ey[:, 1])
            #print("fuel_p_ey:" + str(fuel_p_ey))
            #print(fuel_p_cy.shape)
            #print("self.reg_fuel: " + str(self.reg_fuel))
            #print(self.reg_fuel.shape)

            # Differences in absolute fuel amounts
            absolute_fuel_diff = self.reg_fuel[0] * fuel_p_cy[:, 1] # Multiply fuel demands by percentage changes
            #print("absolute_fuel_diff: " + str(absolute_fuel_diff))
            #print("Technology which is installed:           " + str(tech_install))
            #print("Efficiency of technology to be installed " + str(eff_replacement))
            #print("Current Year:" + str(self.current_year))

            for fuel_type, fuel_diff in enumerate(absolute_fuel_diff):

                # Only if there is a fuel difference
                if fuel_diff > 0:

                    tech_replace = tech_replacement_dict[fuel_type]           # Technology which is replaced (read from technology replacement dict)
                    eff_tech_remove = getattr(self.tech_stock_cy, tech_replace)  # Get efficiency of technology to be replaced

                    # Fuel factor   #TODO ev. auch umgekehrt
                    fuel_factor = eff_tech_remove / eff_replacement
                    fuel_consid_eff = fuel_diff * fuel_factor
                    print("Technology fuel factor difference: " + str(eff_tech_remove) + "   " + str(eff_replacement) + "  " + str(fuel_factor))
                    print("fuel_diff: " + str(fuel_diff))
                    # Add  fuels (if minus, no technology weighting is necessary)
                    if fuel_diff > 0:
                        fuel_switch_array[int(fuel_type)] += fuel_consid_eff # Add Fuel

            #print("Old Fuel: " + str(self.reg_fuel))
            #print("--")
            #print("New Fuel: " + str(fuel_switch_array))
            return fuel_switch_array

    def enduse_scenario_driver(self):
        """The fuel data for every end use are multiplied with respective scenario driver

        If no building specific scenario driver is found, the identical fuel is returned.

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
        if hasattr(self.data['reg_dw_stock_by'][self.reg_id], self.enduse):

            # Scenariodriver of building stock base year and new stock
            by_driver = getattr(self.data['reg_dw_stock_by'][self.reg_id], self.enduse)     # Base year building stock
            cy_driver = getattr(self.data['reg_dw_stock_cy'][self.reg_id], self.enduse) # Current building stock

            factor_driver = cy_driver / by_driver  #TODO: Or the other way round
            fueldata_scenario_diver = self.reg_fuel_after_elasticity * factor_driver
            print("self.enduse: " + str(self.enduse))
            print(cy_driver) #ERROR: CURRENT YEAR LIGHTIGNS HAS NO 
            print(by_driver)
            print(fueldata_scenario_diver)
            #pint("..")
            return fueldata_scenario_diver

        else:
            # This fuel is not changed by building related scenario driver
            return self.reg_fuel_after_elasticity

    def enduse_y_to_d(self):
        """Generate array with fuels for every day"""
        fuels_d = np.zeros((len(self.reg_fuel), 365))

        # Iterate yearday and
        for k, fueltype_year_data in enumerate(self.reg_fuelscen_driver):
            fuels_d[k] = self.enduse_shape_d[:, 0] * fueltype_year_data[0] # enduse_shape_d is  a two dim array with load shapes in first row

        return fuels_d

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
        fuels_h = np.zeros((self.reg_fuel_d.shape[0], 365, 24)) #fueltypes, days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel_type_data in enumerate(self.reg_fuel_d):
            for day in range(365):
                fuels_h[k][day] = self.enduse_shape_h[day] * fuel_type_data[day]

        return fuels_h

    def enduse_peak_d(self):
        """Disaggregate yearly fuel data to the peak day.

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_d_peak : array
            Hourly fuel data [fueltypes, peak_day, hours]

        Notes
        -----
        """
        fuels_d_peak = np.zeros((len(self.reg_fuel), 1))

        # Iterate yearday and
        for k, fueltype_year_data in enumerate(self.reg_fuelscen_driver):
            fuels_d_peak[k] = self.enduse_shape_peak_d * fueltype_year_data[0] # enduse_shape_d is  a two dim array with load shapes in first row

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
        fuels_h_peak = np.zeros((self.reg_fuel_d.shape[0], 1, 24)) #fueltypes  days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel_data in enumerate(self.enduse_fuel_peak_d):
            for day in range(1):
                fuels_h_peak[k][day] = self.enduse_shape_peak_h * fuel_data[day]

        return fuels_h_peak
