"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
import unittest
import copy
import numpy as np
import energy_demand.main_functions as mf
ASSERTIONS = unittest.TestCase('__init__')

class EnduseClassSummarySector(object):
    """Class which is used to store summarised fuels across all sectors of an enduse

    The fuel attributes in the 'EnduseClass' within each sector which want to be transferred need to be entered here
    The fuels are summed across all sectors (e.g. all space heating across all sectors)
    """
    def __init__(self, enduse_fuel_yd, enduse_fuel_yh, enduse_fuel_peak_dh, enduse_fuel_peak_h):
        """Same attributes as in 'EnduseClass'
        """
        self.enduse_fuel_yd = enduse_fuel_yd
        self.enduse_fuel_yh = enduse_fuel_yh
        self.enduse_fuel_peak_dh = enduse_fuel_peak_dh
        self.enduse_fuel_peak_h = enduse_fuel_peak_h

class EnduseClass(object):
    """Class of an end use of the residential sector

    End use class for residential model. For every region, a different
    instance is generated.

    Parameters
    ----------
    reg_name : int
        The ID of the region. The actual region name is stored in `lu_reg`
    data : dict
        Dictionary containing data
    enduse : str
        Enduse given in a string
    enduse_fuel : array
        Fuel data for the region the endu
    tech_stock : object
        Technology stock of region
    heating_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with HDD)
    cooling_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with CDD)
    enduse_peak_yd_factor : float
        Peak yd factor of enduse

    Info
    ----
    Every enduse can only have on shape independently of the fueltype

    `self.enduse_fuel_new_fuel` is always overwritten in the cascade of fuel calculations

    Problem: Not all enduses have technologies assigned. Therfore peaks are derived from techstock in case there are technologies,
    otherwise enduse load shapes are used.
    """
    def __init__(self, reg_name, data, enduse, enduse_fuel, tech_stock, heating_factor_y, cooling_factor_y, enduse_peak_yd_factor, fuel_switches, service_switches, fuel_enduse_tech_p_by, service_tech_by_p, tech_increased_service, tech_decreased_share, tech_constant_share, installed_tech, sigm_parameters_tech, data_shapes_yd, data_shapes_dh, enduse_overall_change_ey, dw_stock):
        """CONSTRUCTOR
        """
        self.current_yr = data['curr_yr']
        self.base_yr = data['base_yr']
        self.end_yr = data['end_yr']
        self.sim_period = data['sim_period']

        self.enduse = enduse
        self.enduse_fuel = enduse_fuel
        self.enduse_fuelswitch_crit = self.get_fuel_switches_crit(fuel_switches)
        self.enduseswitch_crit = self.get_service_switches_crit(service_switches)

        # Get technologies of enduse depending on assumptions on fuel switches or service switches
        self.technologies_enduse = self.get_enduse_tech(service_tech_by_p[enduse], fuel_enduse_tech_p_by[enduse])

        # --------
        # Testing
        # --------
        if self.enduse_fuelswitch_crit and self.enduseswitch_crit:
            sys.exit("Error: Can't define service switch and fuel switch for enduse '{}' {}   {}".format(enduse, self.enduse_fuelswitch_crit, self.enduseswitch_crit))
        if self.enduse not in data_shapes_yd and self.technologies_enduse == []:
            sys.exit("Error: The enduse is not defined with technologies and no generic yd shape is provided for the enduse '{}' ".format(enduse))

        # -------------------------------
        # Yearly fuel calculation cascade
        # --------------------------------
        self.enduse_fuel_new_fuel = copy.deepcopy(enduse_fuel)
        print("Fuel train A: " + str(np.sum(self.enduse_fuel_new_fuel)))
        # Change fuel consumption based on climate change induced temperature differences
        self.temp_correction_hdd_cdd(cooling_factor_y, heating_factor_y)
        print("Fuel train B: " + str(np.sum(self.enduse_fuel_new_fuel)))

        # Calcualte smart meter induced general savings
        self.smart_meter_eff_gain(data['assumptions'])
        print("Fuel train C: " + str(np.sum(self.enduse_fuel_new_fuel)))

        # Enduse specific consumption change in % (due e.g. to other efficiciency gains). No technology considered
        self.enduse_specific_change(data['assumptions'], enduse_overall_change_ey)
        print("Fuel train D: " + str(np.sum(self.enduse_fuel_new_fuel)))

        # Calculate new fuel demands after scenario drivers
        self.enduse_building_stock_driver(dw_stock, reg_name)
        print("Fuel train E: " + str(np.sum(self.enduse_fuel_new_fuel)))

        # Calculate demand with changing elasticity (elasticity maybe on household level with floor area)
        ##self.enduse_elasticity(data, data['assumptions'])
        #print("Fuel train F: " + str(np.sum(self.enduse_fuel_new_fuel)))

        # ----------------------------------
        # Hourly fuel calcualtions cascade
        # ----------------------------------
        # Check if enduse is defined with technologies
        if self.technologies_enduse != []:
            print("Enduse {} is defined.... ".format(enduse) + str(self.technologies_enduse))

            # ------------------------------------------------------------------------
            # Calculate regional energy service (for base year)
            # ------------------------------------------------------------------------
            tot_service_h_by, service_tech, service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p = self.calc_enduses_service(
                fuel_enduse_tech_p_by[self.enduse],
                tech_stock,
                data['lu_fueltype']
                )

            # ----------------
            # Service Switches
            # ----------------
            if self.enduseswitch_crit:
                service_tech = self.switch_tech_service(
                    tot_service_h_by,
                    service_tech_by_p,
                    tech_increased_service[enduse],
                    tech_decreased_share[enduse],
                    tech_constant_share[enduse],
                    sigm_parameters_tech
                    )

            #summe = 0
            #for tech in service_tech:
            #    #print("tech before service switch: " + str(tech) + "  " + str(np.sum(service_tech[tech])))
            #    summe += np.sum(service_tech[tech])

            #print(" ")
            ##print("COMPARIOSN summe           :   " + str(summe))
            #print("COMPARIOSN tot_service_h_by:          " + str(np.sum(tot_service_h_by)))

            # ----------------
            # Fuel Switches
            # ----------------
            if self.enduse_fuelswitch_crit:
                service_tech = self.switch_tech_fuel(
                    installed_tech,
                    sigm_parameters_tech,
                    tot_service_h_by,
                    service_tech,
                    service_fueltype_tech_by_p,
                    service_fueltype_by_p,
                    fuel_switches,
                    fuel_enduse_tech_p_by[enduse]
                    )

            # -----------------------
            # Convert Service to Fuel
            # -----------------------
            # Convert service to fuel (y) for each fueltype depending on technological efficiences in current year
            self.enduse_to_fuel_fueltype_y(service_tech, tech_stock)
            print("Fuel train G: " + str(np.sum(self.enduse_fuel_new_fuel)))

            # Convert service to fuel (y) for each technology depending on technological efficiences in current year
            enduse_fuel_tech_y = self.enduse_to_fuel_per_tech(service_tech, tech_stock)
            #print("Fuel train H: " + str(np.sum(self.enduse_fuel_new_fuel)))

            summe = 0
            for tech in enduse_fuel_tech_y:
                print("Technologie {}  und fuel {} ".format(tech, np.sum(service_tech[tech])))
                summe += np.sum(service_tech[tech])
            print("TOTAL FUEL TO REDISRIBUTE " + str(summe))


            ##
            ## NEW: SERVICE SECTOR: NO TECHNOLOGY SPECIFIC SHAPES. Therefore distribute fuel for technologies
            ##      according to overall sector shape
            ##

            # --------
            # NON-PEAK
            # --------
            # Iterate technologies in enduse and assign technology specific shape for respective fuels
            self.enduse_fuel_yd = self.calc_enduse_fuel_tech_yd(enduse_fuel_tech_y, tech_stock)
            self.enduse_fuel_yh = self.calc_enduse_fuel_tech_yh(enduse_fuel_tech_y, tech_stock)
            #self.enduse_fuel_peak_h = self.get_peak_h_from_dh(self.enduse_fuel_peak_dh)# Get maximum hour demand per fueltype
            print("--SUMME enduse_fuel_yh: " + str(np.sum(self.enduse_fuel_yh)))

            # --------
            # PEAK (Peak is not defined by yd factor so far but read out from real data!) #TODO
            # --------
            # Get day with most fuel across all fueltypes (this is selected as max day)
            peak_day_nr = self.get_peak_fuel_day(self.enduse_fuel_yh)
            print("Peak day: " + str(peak_day_nr))

            # Iterate technologies in enduse and assign technology specific shape for peak for respective fuels
            self.enduse_fuel_peak_dh = self.calc_enduse_fuel_peak_tech_dh(data['assumptions'], enduse_fuel_tech_y, tech_stock, peak_day_nr)
            print("enduse_fuel_peak_dh: " + str(np.sum(self.enduse_fuel_peak_dh)))

            self.enduse_fuel_peak_h = self.get_peak_h_from_dh(self.enduse_fuel_peak_dh) # Get maximum hour demand per of peak day
            print("enduse_fuel_peak_h: " + str(np.sum(self.enduse_fuel_peak_h)))

            print("Proportion von day: " + str((100/np.sum(self.enduse_fuel_peak_dh)) * np.sum(self.enduse_fuel_peak_h)))
        else: # No technologies specified in enduse
            print("enduse is not defined with technologies: " + str(enduse))

            # --Peak yd (peak day) (same for enduse for all technologies)
            self.enduse_fuel_peak_yd = self.calc_enduse_fuel_peak_yd_factor(enduse_fuel, enduse_peak_yd_factor)

            # --------
            # NON-PEAK
            # --------
            self.enduse_fuel_yd = self.enduse_y_to_d(self.enduse_fuel_new_fuel, data_shapes_yd[enduse]['shape_non_peak_yd'])
            self.enduse_fuel_yh = self.enduse_d_to_h(self.enduse_fuel_yd, data_shapes_dh[enduse]['shape_non_peak_dh'])
            print("--SUMME2 enduse_fuel_yh: " + str(np.sum(self.enduse_fuel_yh)))

            # --------
            # PEAK
            # --------
            self.enduse_fuel_peak_dh = self.calc_enduse_fuel_peak_dh(self.enduse_fuel_peak_yd, data_shapes_dh[enduse]['shape_peak_dh'])
            self.enduse_fuel_peak_h = self.get_peak_h_from_dh(self.enduse_fuel_peak_dh)

        # Testing
        np.testing.assert_almost_equal(np.sum(self.enduse_fuel_yd), np.sum(self.enduse_fuel_yh), decimal=2, err_msg='', verbose=True)

    def calc_enduses_service(self, fuel_enduse_tech_p_by, tech_stock, fueltypes_lu):
        """Calculate energy service of each technology based on assumptions about base year fuel shares of an enduse

        This calculation converts fuels into energy services (e.g. fuel for heating into heat demand)
        and then calculates the fraction of an invidual technology to which it contributes to total energy
        service (e.g. how much of total heat demand condensing boilers contribute).

        #TODO

        Parameters
        ----------
        fuel_enduse_tech_p_by : dict
            Fuel composition of base year for every fueltype for each enduse (assumtions for national scale)
        tech_stock : object
            Technology stock of region

        Return
        ------
        tot_service_yh : array
            Total energy service per technology for base year (365, 24)
        service_tech_by : dict
            Energy service for every fueltype and technology (dict[fueltype][tech])

        Info
        -----
        Energy service = fuel * efficiency

        Notes
        -----
        The fraction of fuel is calculated based on regional temperatures. The fraction
        of fueltypes belonging to each technology is however based on national assumptions (fuel_enduse_tech_p_by)
        and thus changes the share of enery service in each region
        """
        service_tech_by = mf.init_dict(self.technologies_enduse, 'zero')
        service_fueltype_tech_by_p = mf.initialise_service_fueltype_tech_by_p(fueltypes_lu, fuel_enduse_tech_p_by)

        # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
        for fueltype, fuel_enduse in enumerate(self.enduse_fuel_new_fuel):
            for tech in fuel_enduse_tech_p_by[fueltype]:

                # Fuel share based on defined fuel fraction within fueltype (assumed national share of fuel of technology * tot fuel)
                fuel_tech_y = fuel_enduse_tech_p_by[fueltype][tech] * fuel_enduse

                # Distribute y to yh by multiplying total fuel of technology with yh fuel shape
                fuel_tech_yh = fuel_tech_y * tech_stock.get_tech_attribute(tech, 'shape_yh')

                # Convert to energy service
                service_tech_by[tech] += fuel_tech_yh * tech_stock.get_tech_attribute(tech, 'eff_by')
                #print("Convert fuel to service and add to existing: "+ str(np.sum(service_tech_by[tech])) + str("  ") + str(tech))

                # Get fuel distribution yh
                fueltype_share_yh = tech_stock.get_tech_attribute(tech, 'fueltypes_yh_p_cy')
                #print("FUELTYPE  {}   tech   {}     {}    {}     {}".format(fueltype, tech, np.sum(fuel_tech_y), np.sum(fuel_tech_yh), np.sum(fueltype_share_yh)))

                # Distribute service depending on fueltype distirbution
                for fueltype_installed_tech_yh, fueltype_share in enumerate(fueltype_share_yh):
                    fuel_fueltype = fueltype_share * fuel_tech_yh

                    # Convert fuel to service #TODO: WHY IS NOT IN TECH IF NO SERVICE?
                    if np.sum(fuel_fueltype) > 0:
                        service_fueltype_tech_by_p[fueltype_installed_tech_yh][tech] += np.sum(fuel_fueltype * tech_stock.get_tech_attribute(tech, 'eff_by'))

                # Testing
                ASSERTIONS.assertAlmostEqual(np.sum(fuel_tech_yh), np.sum(fuel_tech_y), places=7, msg="The fuel to service y to h went wrong {}  {}  ".format(np.sum(fuel_tech_yh), np.sum(fuel_tech_y)), delta=None)

        # --------------------------------------------------
        # Convert or aggregate service to other formats
        # --------------------------------------------------
        # --Calculate energy service demand over the full year and for every hour, sum demand accross all technologies
        tot_service_yh = np.zeros((365, 24))
        for _, service_tech in service_tech_by.items():
            tot_service_yh += service_tech

        # --Convert to percentage
        service_tech_by_p = {}
        for technology, service_tech in service_tech_by.items():
            service_tech_by_p[technology] = np.divide(1, np.sum(tot_service_yh)) * np.sum(service_tech)

        # Convert service per fueltype of technology
        for fueltype, service_fueltype in service_fueltype_tech_by_p.items():

            # Calculate total sum within fueltype
            sum_within_fueltype = sum(service_fueltype.values())

            # Calculate fraction of servcie per technology
            for tech, service_fueltype_tech in service_fueltype.items():
                if sum_within_fueltype > 0:
                    service_fueltype_tech_by_p[fueltype][tech] = np.divide(1, np.sum(sum_within_fueltype)) * service_fueltype_tech
                else:
                    service_fueltype_tech_by_p[fueltype][tech] = 0

        # Calculate service fraction per fueltype
        service_fueltype_by_p = mf.init_dict(fueltypes_lu.values(), 'zero')
        for fueltype, service_fueltype in service_fueltype_tech_by_p.items():
            for tech, service_fueltype_tech in service_fueltype.items():
                service_fueltype_by_p[fueltype] += service_fueltype_tech

        return tot_service_yh, service_tech_by, service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p

    def get_peak_fuel_day(self, enduse_fuel_yh):
        """Iterate hourly service and get day with most service

        Parameters
        ----------
        enduse_fuel_yh : array
            Fuel for all technologes in enduse

        Return
        ------
        peak_day_nr : int
            Day with most fuel across all fueltypes
        peak_day_shape_dh : array
            Peak dh shape of day with peak hour value

        Assumption: Day with most service is the day with peak

        Note
        -----
        The Peak day may change date in a year
        """
        max_fuel_day = 0

        # Sum all fuely across all fueltypes for every day and hour in a year
        all_fueltypes_tot_h = np.sum(enduse_fuel_yh, axis=0) #shape (365, 24)

        # Iterate summed fueltypes to read out maximum fuel
        for day_nr, services_dh in enumerate(all_fueltypes_tot_h):
            day_sum = np.sum(services_dh)

            if day_sum > max_fuel_day:
                #print("...serach: max: " + str(max_fuel_day))
                #print("fuzeltype 1: " + str(np.sum(enduse_fuel_yh[1][day_nr])))
                #print("fueltype 2: " + str(np.sum(enduse_fuel_yh[2][day_nr])))
                #print(day_sum)

                max_fuel_day = day_sum
                peak_day_nr = day_nr

        print("Peak Day Number {}  with peak fuel demand (across all fueltypes): {}        ".format(peak_day_nr, max_fuel_day))
        return peak_day_nr

    def get_enduse_tech(self, service_tech_by_p, fuel_enduse_tech_p_by):
        """Get all defined technologies of an enduse

        Parameters
        ----------
        service_tech_by_p : dict
            Percentage of total service per technology in base year in
        fuel_enduse_tech_p_by : dict
            Percentage of fuel per enduse per technology

        Return
        ------
        technologies_enduse : list
            All technologies (no technolgy is added twice)

        Depending on whether fuel swatches are implemented or services switches
        """
        if self.enduseswitch_crit:
            technologies_enduse = service_tech_by_p.keys()
        else:
            # If no fuel switch and no service switch, read out base year technologies
            technologies_enduse = set([])
            for _, tech_fueltype in fuel_enduse_tech_p_by.items():
                for tech in tech_fueltype.keys():
                    technologies_enduse.add(tech)

        return list(technologies_enduse)

    def switch_tech_service(self, tot_service_h_by, service_tech_by_p, tech_increase_service, tech_decrease_service, tech_constant_service, sigm_parameters_tech):
        """Scenaric service switches

        All diminishing technologies are proportionally to base year share diminished.

        Paramters
        ---------
        tot_service_h_by : array
            Hourly service of all technologies
        tech_stock : object
            Technology stock

        Returns
        -------
        service_tech_cy : dict
            Current year fuel for every technology (e.g. fueltype 1: 'techA': fuel) for every hour
        """
        print(" ")
        print("...Service switch is implemented "  + str(self.enduse))
        service_tech_cy_p = {}
        service_tech_cy = {}

        # -------------
        # Technology with increaseing service
        # -------------
        # Calculate diffusion of service for technology with increased service
        service_tech_increase_cy_p = self.get_service_diffusion(tech_increase_service, sigm_parameters_tech)

        for tech_increase, share_tech in service_tech_increase_cy_p.items():
            service_tech_cy_p[tech_increase] = share_tech # Add shares to output dict

        # -------------
        # Technology with decreasing service
        # -------------
        # Calculate proportional share of technologies with decreasing service of base year (distribution in base year)
        service_tech_decrease_by_rel = mf.get_service_rel_tech_decrease_by(
            tech_decrease_service, service_tech_by_p)

        # Add shares to output dict
        for tech_decrease in service_tech_decrease_by_rel:
            service_tech_cy_p[tech_decrease] = service_tech_by_p[tech_decrease]


        # Iterate service switches for increase tech, calculated gained service and substract this gained service proportionally for all decreasing technologies
        for tech_increase in service_tech_increase_cy_p:

            # Difference in service up to current year
            diff_service_increase = service_tech_increase_cy_p[tech_increase] - service_tech_by_p[tech_increase]

            # Substract service gain proportionaly to all technologies which are lowered and substract from other technologies
            for tech_decrease, service_tech_decrease in service_tech_decrease_by_rel.items():
                service_to_substract = service_tech_decrease * diff_service_increase

                # Testing
                if service_tech_cy_p[tech_decrease] - service_to_substract < -1:
                    sys.exit("Error in fuel switch")

                # Substract service (Because of rounding errors the service my fall below zero (therfore set to zero if only slighlty minus)
                if np.sum(service_tech_cy_p[tech_decrease] - service_to_substract) < 0:
                    service_tech_cy_p[tech_decrease] *= 0 # Set to zero service
                else:
                    service_tech_cy_p[tech_decrease] -= service_to_substract

        # -------------
        # Technology with constant service
        # -------------
        # Add all technologies with unchanged service in the future
        for tech_constant in tech_constant_service:
            service_tech_cy_p[tech_constant] = service_tech_by_p[tech_constant]

        # Multiply share of each tech with hourly service
        for tech, enduse_share in service_tech_cy_p.items():
            service_tech_cy[tech] = tot_service_h_by * enduse_share  # Total yearly hourly service * share of enduse

        print("...Finished service switch")
        return service_tech_cy

    def get_service_diffusion(self, tech_increased_service, sigm_parameters_tech):
        """Calculate energy service fraction of technologies with increased service

        Parameters
        ----------
        data : dict
            Data
        tech_increased_service : dict
            All technologies per enduse with increased future service share

        Returns
        -------
        service_tech_cy_p : dict
            Share of service per technology of current year
        """
        service_tech_cy_p = {}

        for tech_installed in tech_increased_service:
            # Get service for current year based on sigmoid diffusion
            service_tech_cy_p[tech_installed] = mf.sigmoid_function(
                self.current_yr,
                sigm_parameters_tech[self.enduse][tech_installed]['l_parameter'],
                sigm_parameters_tech[self.enduse][tech_installed]['midpoint'],
                sigm_parameters_tech[self.enduse][tech_installed]['steepness']
            )

        return service_tech_cy_p

    def get_fuel_switches_crit(self, fuelswitches):
        """Test whether there is a fuelswitch for this enduse

        Parameters
        ----------
        fuelswitches : dict
            All fuel switches

        Note
        ----
        If base year, no switches are implemented
        """
        if self.base_yr == self.current_yr:
            return False
        else:
            fuel_switches_enduse = []

            for fuelswitch in fuelswitches:
                print("ddd")
                print(fuelswitch)
                print(self.enduse)
                if fuelswitch['enduse'] == self.enduse: #If fuelswitch belongs to this enduse
                    fuel_switches_enduse.append(fuelswitch)

            if len(fuel_switches_enduse) > 0: # != []:
                return True
            else:
                return False

    def get_service_switches_crit(self, service_switches):
        """Test whether there are defined service switches for this enduse

        Parameters
        ----------
        service_switches : dict
            Service switches

        Note
        ----
        If base year, no switches are implemented
        """
        crit_service_switch = False
        if self.base_yr == self.current_yr:
            return crit_service_switch
        else:
            for service_switch in service_switches:
                if service_switch['enduse'] == self.enduse:
                    crit_service_switch = True

            return crit_service_switch

    def get_peak_h_from_dh(self, enduse_fuel_peak_dh):
        """Iterate peak day fuels and select peak hour

        # The peak of the individual fueltypes may not be all in the same hour of the day
        """
        peak_fueltype_h = np.zeros((enduse_fuel_peak_dh.shape[0]))

        # Peak values for every fueltype
        for fueltype, fuel_dh in enumerate(enduse_fuel_peak_dh):
            #print("--peakfinidng: " + str(fueltype) + str("  ") + str(np.max(fuel_dh)))
            peak_fueltype_h[fueltype] = np.max(fuel_dh) # Get hour with maximum fuel in a day of fueltype

        print("TESTSUM: " + str(np.sum(peak_fueltype_h)))
        return peak_fueltype_h

    def calc_enduse_fuel_peak_tech_dh(self, assumptions, enduse_fuel_tech, tech_stock, peak_day_nr):
        """Calculate peak demand

        This function gets the hourly values of the peak day for every fueltype.
        The daily fuel is converted to dh for each technology.

        Parameters
        ----------
        assumptions : array
            Assumptions
        enduse_fuel_tech : array
            Fuel per enduse and technology
        tech_stock : data
            Technology stock
        peak_day_nr : int
            Peak day number of enduse

        Returns
        -------
        fuels_peak_dh : array
            Peak values for peak day for every fueltype

        Notes
        ------
        *   For some technologies the dh peak day profile is not read in from technology stock but from
            shape_yh of peak day (hybrid technologies).
        """
        fuels_peak_dh = np.zeros((self.enduse_fuel_new_fuel.shape[0], 24))

        for tech in self.technologies_enduse:
            #print("Tech: " + str(tech) + "   " + str(enduse_fuel_tech[tech]))

            # Get yd fuel shape of technology
            fuel_shape_yd = tech_stock.get_tech_attribute(tech, 'shape_yd')

            # Calculate absolute fuel values for yd
            fuel_tech_y_d = enduse_fuel_tech[tech] * fuel_shape_yd #[peak_day_nr]
            #print("FUEL  yd: " + str(np.sum(fuel_tech_y_d)))

            # Calculate fuel for peak day
            fuel_tech_peak_d = fuel_tech_y_d[peak_day_nr]
            #print("FUEL PEAK DAY 2: " + str(fuel_tech_peak_d))

            # If hybrid technology
            if tech in assumptions['list_tech_heating_hybrid']:

                # The 'shape_peak_dh'is not defined in technology stock because in the 'RegionClass' the peak day is not yet known
                # Therfore, the shape_yh is read in and with help of information on peak day the hybrid dh shape generated
                tech_peak_dh_absolute = tech_stock.get_tech_attribute(tech, 'shape_yh')[peak_day_nr]
                tech_peak_dh = mf.absolute_to_relative(tech_peak_dh_absolute)

            else:
                # Assign Peak shape of a peak day of a technology
                tech_peak_dh = tech_stock.get_tech_attribute(tech, 'shape_peak_dh')

            # Multiply absolute d fuels with dh peak fuel shape
            fuel_tech_peak_dh = tech_peak_dh * fuel_tech_peak_d

            # Get fueltypes (distribution) of tech for peak day
            fueltypes_tech_share_yd = tech_stock.get_tech_attribute(tech, 'fueltypes_yh_p_cy')

            control_sum = 0
            # Iterate distribution of fueltypes for peak day and assign fuels to fuels_peak_dh
            for fueltype, fueltype_distr_yh in enumerate(fueltypes_tech_share_yd):

                # Multiply dh fuel with fueltype distribution
                fuels_peak_dh[fueltype] += fuel_tech_peak_dh * fueltype_distr_yh[peak_day_nr]

                control_sum += (fuel_tech_peak_dh * fueltype_distr_yh[peak_day_nr])

            # Testing
            np.testing.assert_almost_equal(np.sum(fuel_shape_yd), 1) #Test if yd shape is one
            np.testing.assert_almost_equal(np.sum(tech_peak_dh), 1, decimal=3, err_msg='Error XY')
            np.testing.assert_almost_equal(np.sum(control_sum), np.sum(fuel_tech_peak_dh), decimal=3, err_msg='Error XY')

        return fuels_peak_dh

    def calc_enduse_fuel_tech_yd(self, enduse_fuel_tech, tech_stock):
        """Iterate fuels for each technology and assign shape yd

        Parameters
        ----------
        enduse_fuel_tech : dict
            Fuel per technology in enduse
        tech_stock : object
            Technologies

        Return
        ------
        fuels_yd : array
            Fueltype storing daily fuel for every fueltype (fueltype, 365)
        """
        fuels_yd = np.zeros((self.enduse_fuel_new_fuel.shape[0], 365))
        control_sum = 0

        for tech in self.technologies_enduse:

            # Multiply fuel with shape_yd
            fuel_tech_yd = enduse_fuel_tech[tech] * tech_stock.get_tech_attribute(tech, 'shape_yd')

            # Get fueltypes of tech for every day
            fueltype_tech_share_yd = tech_stock.get_tech_attribute(tech, 'fuel_types_shares_yd')

            # Iterate shares of fueltypes, calculate share of fuel and add to fuels
            for fueltype_hybrid, fuel_shares_dh in enumerate(fueltype_tech_share_yd):
                fuels_yd[fueltype_hybrid] += fuel_tech_yd * fuel_shares_dh

                control_sum += np.sum(fuel_tech_yd * fuel_shares_dh)

            # Testing
            np.testing.assert_array_almost_equal(np.sum(fuel_tech_yd), np.sum(enduse_fuel_tech[tech]), decimal=3, err_msg="Error NR XXX")

        # Testing
        np.testing.assert_array_almost_equal(sum(enduse_fuel_tech.values()), np.sum(control_sum), decimal=2, err_msg="Error: The y to h fuel did not work")

        return fuels_yd

    def calc_enduse_fuel_tech_yh(self, enduse_fuel_tech, tech_stock):
        """Iterate fuels for each technology and assign shape yh

        Parameters
        ----------
        enduse_fuel_tech : dict
            Fuel per technology in enduse
        tech_stock : object
            Technologies

        Return
        ------
        fuels_yh : array
            Fueltype storing hourly fuel for every fueltype (fueltype, 365, 24)
        """
        fuels_yh = np.zeros((self.enduse_fuel_new_fuel.shape[0], 365, 24))
        control_sum = 0

        for tech in self.technologies_enduse:

            # Shape of fuel of technology for every hour in year
            fuel_tech_yh = enduse_fuel_tech[tech] * tech_stock.get_tech_attribute(tech, 'shape_yh')

            # Get distribution of fuel for every hour
            fueltypes_tech_share_yh = tech_stock.get_tech_attribute(tech, 'fueltypes_yh_p_cy')

            for fueltype, fuel_tech_share_h in enumerate(fueltypes_tech_share_yh):
                fuels_yh[fueltype] += fuel_tech_share_h * fuel_tech_yh

                control_sum += fuel_tech_share_h * fuel_tech_yh

        # Assert --> If this assert is done, then we need to substract the fuel from yearly data and run function:  enduse_to_fuel_fueltype_y
        np.testing.assert_array_almost_equal(np.sum(fuels_yh), np.sum(control_sum), decimal=2, err_msg="Error: The y to h fuel did not work")

        return fuels_yh

    def switch_tech_fuel(self, installed_tech, sigm_parameters_tech, tot_service_h_by, service_tech, service_fueltype_tech_by_p, service_fueltype_by_p, fuel_switches, fuel_enduse_tech_p_by):
        """Scenaric fuel switches

        Based on assumptions about shares of fuels which are switched per enduse to specific
        technologies, the installed technologies are used to calculate the new service demand
        after switching fuel shares.

        Parameters
        ----------

        assumptions : dict
            Assumptions
        tot_service_h_by : dict
            Total regional service for every hour for base year
        service_tech : dict
            Service for every fueltype and technology
        fuel_enduse_tech_p_by : dict
            Definition of fule in by of technologies
            #assumptions['rs_fuel_enduse_tech_p_by'][self.enduse]

        Returns
        -------
        service_tech_after_switch : dict
            Containing all service for each technology on a hourly basis
        """
        print(" ")
        print("... fuel_switch is implemented")
        print(" ")
        service_tech_after_switch = copy.deepcopy(service_tech)

        # Iterate all technologies which are installed in fuel switches
        for tech_installed in installed_tech[self.enduse]:

            # Read out sigmoid diffusion of service of this technology for the current year
            diffusion_cy = mf.sigmoid_function(
                self.current_yr,
                sigm_parameters_tech[self.enduse][tech_installed]['l_parameter'],
                sigm_parameters_tech[self.enduse][tech_installed]['midpoint'],
                sigm_parameters_tech[self.enduse][tech_installed]['steepness'])

            # Calculate increase in service based on diffusion of installed technology (diff & total service== Todays demand) - already installed service
            print("eeeeeeeeeeeeeeeeee")
            print(tech_installed)
            print(np.sum(service_tech[tech_installed]))
            print(diffusion_cy)
            print(np.sum(tot_service_h_by))
            service_tech_installed_cy = (diffusion_cy * tot_service_h_by) - service_tech[tech_installed]

            print("-----------Tech_installed:  "  + str(tech_installed) + str(self.current_yr))
            print("diffusion_cy  " + str(diffusion_cy))
            print(" Tot service  " + str(np.sum(tot_service_h_by)))
            print(" Tot ser aft  " + str(np.sum(service_tech_after_switch[tech_installed])))
            print("----")
            print(np.sum(diffusion_cy * tot_service_h_by))
            print(np.sum(service_tech[tech_installed]))
            print(np.sum((diffusion_cy * tot_service_h_by) - service_tech[tech_installed]))
            print("TODAY SHARE: " + str(np.sum((1 / np.sum(tot_service_h_by)) * service_tech[tech_installed])))

            # Assert if minus demand
            assert np.sum((diffusion_cy * tot_service_h_by) - service_tech[tech_installed]) >= 0

            # Get service for current year for technologies
            service_tech_after_switch[tech_installed] += service_tech_installed_cy
            print("service_tech_after_switch:  " + str(np.sum(service_tech_after_switch[tech_installed])))

            # ------------
            # Remove fuel of replaced energy service demand proportinally to fuel shares in base year (of national country)
            # ------------
            tot_service_switched_all_tech_instal_p = 0 # Total replaced service across different fueltypes
            fueltypes_replaced = [] # List with fueltypes where fuel is replaced

            # Iterate fuelswitches and read out the shares of fuel which is switched with the installed technology
            for fuelswitch in fuel_switches:
                # If the same technology is switched to across different fueltypes
                if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed:

                    # Add replaced fueltype
                    fueltypes_replaced.append(fuelswitch['enduse_fueltype_replace'])

                    # Share of service demand per fueltype * fraction of fuel switched
                    tot_service_switched_all_tech_instal_p += service_fueltype_by_p[fuelswitch['enduse_fueltype_replace']] * fuelswitch['share_fuel_consumption_switched']

            print(" ")
            print("replaced fueltypes: " + str(fueltypes_replaced))
            print("Service demand which is switched with this technology: " + str(tot_service_switched_all_tech_instal_p))

            # Iterate all fueltypes which are affected by the technology installed
            for fueltype_replace in fueltypes_replaced:

                # Get all technologies of the replaced fueltype
                technologies_replaced_fueltype = fuel_enduse_tech_p_by[self.enduse][fueltype_replace].keys()

                # Find fuel switch where this fueltype is replaced
                for fuelswitch in fuel_switches: #assumptions['rs_fuel_switches']:
                    if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed and fuelswitch['enduse_fueltype_replace'] == fueltype_replace:

                        # Service reduced for this fueltype (service technology cy sigmoid diff *  % of heat demand within fueltype)
                        if tot_service_switched_all_tech_instal_p == 0:
                            reduction_service_fueltype = 0
                        else:
                            # share of total service of fueltype * share of replaced fuel
                            service_fueltype_tech_by_p_rel = np.divide(1.0, tot_service_switched_all_tech_instal_p) * (service_fueltype_by_p[fueltype_replace] * fuelswitch['share_fuel_consumption_switched'])

                            print("service_fueltype_tech_by_p_rel -- : " + str(service_fueltype_tech_by_p_rel))
                            reduction_service_fueltype = service_tech_installed_cy * service_fueltype_tech_by_p_rel
                        break

                print("Reduction of additional service of technology in replaced fueltype: " + str(np.sum(reduction_service_fueltype)))

                # Iterate all technologies in within the fueltype and calculate reduction per technology
                for technology_replaced in technologies_replaced_fueltype:
                    print(" ")
                    print("technology_replaced: " + str(technology_replaced))
                    # It needs to be calculated within each region the share how the fuel is distributed...
                    # Share of heat demand for technology in fueltype (share of heat demand within fueltype * reduction in servide demand)
                    service_demand_tech = service_fueltype_tech_by_p[fueltype_replace][technology_replaced] * reduction_service_fueltype
                    print("service_demand_tech: " + str(np.sum(service_demand_tech)))

                    # -------
                    # Substract technology specific service
                    # -------
                    # Because in region the fuel distribution may be different because of different efficiencies, particularly for fueltypes,
                    # it may happen that the switched service is minus 0. If this is the case, assume that the service is zero.
                    if np.sum(service_tech_after_switch[technology_replaced] - service_demand_tech) < 0:
                        print("Warning: blblablab")
                        print(np.sum(service_tech_after_switch[technology_replaced]))
                        print(np.sum(service_demand_tech))
                        sys.exit("ERROR: Service cant be minus")
                        service_tech_after_switch[technology_replaced] = 0
                    else:
                        # Substract technology specific servide demand
                        service_tech_after_switch[technology_replaced] -= service_demand_tech
                        #print("B: " + str(np.sum(service_tech_after_switch[technology_replaced])))

                # Testing
                #assert np.testing.assert_almost_equal(np.sum(test_sum), np.sum(reduction_service_fueltype), decimal=4)

        return service_tech_after_switch

    def enduse_to_fuel_fueltype_y(self, service_tech, tech_stock):
        """Convert energy service to yearly fuel

        For every technology the service is taken and converted to fuel based on efficiency of current year

        Inputs
        ------
        service_tech : dict
            Service per fueltype and technology
        tech_stock : object
            Technological stock

        Info
        -----
        Fuel = Energy service / efficiency
        """
        # Initialise with all fuetlypes
        enduse_fuels = np.zeros((self.enduse_fuel_new_fuel.shape))

        # Convert service to fuel
        for tech in service_tech:
            ##print("SERVICE TO CONVERT: {}  ".format(tech) + str(np.sum(service_tech[tech])))

            # Calculate fuels (divide by efficiency)
            fuel_tech = np.divide(service_tech[tech], tech_stock.get_tech_attribute(tech, 'eff_cy'))

            fueltype_share_yh = tech_stock.get_tech_attribute(tech, 'fueltypes_yh_p_cy')

            for fueltype, fuel_share in enumerate(fueltype_share_yh):
                fuel_fueltype = fuel_share * fuel_tech
                enduse_fuels[fueltype] += np.sum(fuel_fueltype) # Share of fuel of fueltype_hybrid * fuel

        setattr(self, 'enduse_fuel_new_fuel', enduse_fuels)

    @staticmethod
    def enduse_to_fuel_per_tech(service_tech, tech_stock):
        """Calculate percent of fuel for each technology within fueltype considering current efficiencies

        Parameters
        ----------
        service_tech : dict
            Assumptions of share of fuel of base year
        tech_stock : object
            Technology stock

        Returns
        -------
        fuel_tech : dict
            Fuels per technology (the fueltype is given through technology)

        Info
        -----
        Fuel = Energy service / efficiency
        """
        fuel_tech = {} # Initialise with all fuetlypes

        # Convert service to fuel
        for tech in service_tech:
            fuel = np.divide(service_tech[tech], tech_stock.get_tech_attribute(tech, 'eff_cy'))
            fuel_tech[tech] = np.sum(fuel)

        return fuel_tech

    def enduse_specific_change(self, assumptions, enduse_overall_change_ey):
        """Calculates fuel based on assumed overall enduse specific fuel consumption changes

        Because for enduses where no technology stock is defined (and may consist of many different)
        technologies, a linear diffusion is suggested to best represent multiple
        sigmoid efficiency improvements of individual technologies.

        The changes are assumed across all fueltypes.

        Parameters
        ----------
        assumptions : dict
            assumptions

        Returns
        -------
        out_dict : dict
            Dictionary containing new fuel demands for `enduse`

        Notes
        -----
        Either a sigmoid standard diffusion or linear diffusion can be implemented. Linear is suggested.
        """
        # Fuel consumption shares in base and end year
        percent_by = 1.0
        percent_ey = enduse_overall_change_ey[self.enduse] #assumptions['enduse_overall_change_ey']

        # Share of fuel consumption difference
        diff_fuel_consump = percent_ey - percent_by
        diffusion_choice = assumptions['other_enduse_mode_info']['diff_method'] # Diffusion choice

        if diff_fuel_consump != 0: # If change in fuel consumption
            new_fuels = np.zeros((self.enduse_fuel_new_fuel.shape[0])) # fueltypes, days, hours

            # Lineare diffusion up to cy
            if diffusion_choice == 'linear':
                lin_diff_factor = mf.linear_diff(
                    self.base_yr,
                    self.curr_yr,
                    percent_by,
                    percent_ey,
                    len(self.sim_period)
                )
                change_cy = diff_fuel_consump * abs(lin_diff_factor)

            # Sigmoid diffusion up to cy
            elif diffusion_choice == 'sigmoid':
                sig_diff_factor = mf.sigmoid_diffusion(self.base_yr, self.curr_yr, self.end_yr, assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'], assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness'])
                change_cy = diff_fuel_consump * sig_diff_factor

            # Calculate new fuel consumption percentage
            for fueltype, fuel in enumerate(self.enduse_fuel_new_fuel):
                new_fuels[fueltype] = fuel * (1.0 + change_cy)

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

    def temp_correction_hdd_cdd(self, cooling_factor_y, heating_factor_y):
        """Change fuel demand for heat and cooling service depending on changes in HDD and CDD within a region (e.g. climate change induced)

        Paramters
        ---------
        heating_factor_y : array
            Distribution of fuel within year to days (yd) (directly correlates with HDD)
        cooling_factor_y : array
            Distribution of fuel within year to days (yd) (directly correlates with CDD)

        Return
        ------
        setattr

        Notes
        ----
        `cooling_factor_y` and `heating_factor_y` are based on the sum over the year. Therefore
        it is assumed that fuel correlates directly with HDD or CDD

        Technology mix and efficiencies are ignored at this stage. This will be taken into consideration with other steps
        """
        new_fuels = np.zeros((self.enduse_fuel_new_fuel.shape[0]))

        if self.enduse == 'rs_space_heating': #TODO
            for fueltype, fuel in enumerate(self.enduse_fuel_new_fuel):
                new_fuels[fueltype] = fuel * heating_factor_y

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

        elif self.enduse == 'cooling':
            for fueltype, fuel in enumerate(self.enduse_fuel_new_fuel):
                new_fuels[fueltype] = fuel * cooling_factor_y

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

    def enduse_elasticity(self, data_ext, assumptions):
        """Adapts yearls fuel use depending on elasticity

        # TODO: MAYBE ALSO USE BUILDING STOCK TO SEE HOW ELASTICITY CHANGES WITH FLOOR AREA
        Maybe implement rs_elasticities with floor area

        # TODO: Non-linear elasticity. Then for cy the elasticity needs to be calculated

        Info
        ----------
        Every enduse can only have on shape independently of the fueltype
        """
        if self.current_yr != self.base_yr: # if not base year

            new_fuels = np.zeros((self.enduse_fuel_new_fuel.shape[0])) #fueltypes, days, hours

            # End use elasticity
            elasticity_enduse = assumptions['rs_elasticities'][self.enduse]

            for fueltype, fuel in enumerate(self.enduse_fuel_new_fuel):

                if fuel != 0: # if fuel exists
                    fuelprice_by = data_ext['fuel_price'][self.base_yr][fueltype] # Fuel price by
                    fuelprice_cy = data_ext['fuel_price'][self.current_yr][fueltype] # Fuel price ey
                    new_fuels[fueltype] = mf.apply_elasticity(fuel, elasticity_enduse, fuelprice_by, fuelprice_cy)
                else:
                    new_fuels[fueltype] = fuel

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

    def smart_meter_eff_gain(self, assumptions):
        """Calculate fuel savings depending on smart meter penetration

        The smart meter penetration is assumed with a sigmoid diffusion.

        In the assumptions the maximum penetration and also the
        generally fuel savings for each enduse can be defined.

        Parameters
        ----------

        assumptions : dict
            assumptions

        Returns
        -------
        new_fuels : array
            Fuels which are adapted according to smart meter penetration
        """
        if self.enduse in assumptions['general_savings_smart_meter']:
            new_fuels = np.zeros((self.enduse_fuel_new_fuel.shape[0]))

            # Sigmoid diffusion up to current year
            sigm_factor = mf.sigmoid_diffusion(
                self.base_yr,
                self.current_yr,
                self.end_yr,
                assumptions['sig_midpoint'], assumptions['sig_steeppness']
                )

            # Smart Meter penetration (percentage of people having smart meters)
            penetration_by = assumptions['smart_meter_p_by']
            penetration_cy = assumptions['smart_meter_p_by'] + (sigm_factor * (assumptions['smart_meter_p_ey'] - assumptions['smart_meter_p_by']))

            for fueltype, fuel in enumerate(self.enduse_fuel_new_fuel):
                saved_fuel = fuel * (penetration_by - penetration_cy) * assumptions['general_savings_smart_meter'][self.enduse] # Saved fuel
                new_fuels[fueltype] = fuel - saved_fuel

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

    def enduse_building_stock_driver(self, dw_stock, reg_name):
        """The fuel data for every end use are multiplied with respective scenario driver

        If no building specific scenario driver is found, the identical fuel is returned.

        The HDD is calculated seperately!

        Parameters
        ----------
        dw_stock : dict
            ff
        reg_name : str
            Region

        Returns
        -------
        fuels_h : array
            Hourly fuel data [fueltypes, days, hours]

        Notes
        -----
        This is the energy end use used for disaggregating to daily and hourly
        """
        new_fuels = copy.deepcopy(self.enduse_fuel_new_fuel)

        # Test if enduse has a building related scenario driver
        if hasattr(dw_stock[reg_name][self.base_yr], self.enduse) and self.current_yr != self.base_yr:

            # Scenariodriver of building stock base year and new stock
            by_driver = getattr(dw_stock[reg_name][self.base_yr], self.enduse)
            cy_driver = getattr(dw_stock[reg_name][self.current_yr], self.enduse)

            # base year / current (checked) (as in chapter 3.1.2 EQ E-2)
            factor_driver = np.divide(cy_driver, by_driver) # FROZEN

            new_fuels *= factor_driver

            setattr(self, 'enduse_fuel_new_fuel', new_fuels)

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

        for fueltype, fuel in enumerate(fuels):
            fuels_d[fueltype] = enduse_shape_yd * fuel

        np.testing.assert_almost_equal(np.sum(fuels), np.sum(fuels_d), decimal=3, err_msg='The distribution of dwelling types went wrong', verbose=True)

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

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for fueltype, fuel in enumerate(fuels):
            for day in range(365):
                fuels_h[fueltype][day] = enduse_shape_dh[day] * fuel[day]

        ASSERTIONS.assertAlmostEqual(np.sum(fuels), np.sum(fuels_h), places=2, msg="The function Day to h tranfsormation failed", delta=None)

        return fuels_h
    
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

        for fueltype, fueltype_year_data in enumerate(fuels):
            '''print("Fuetlype: " + str(fueltype))
            print(factor_d)
            print(fueltype_year_data.shape)
            print(fueltype_year_data[0])
            print("--")
            print(fueltype_year_data)
            a = factor_d * fueltype_year_data # BIG CHANGE[0]
            print(a)
            '''
            fuels_d_peak[fueltype] = factor_d * fueltype_year_data
        return fuels_d_peak

    @classmethod
    def calc_enduse_fuel_peak_dh(self, fuels, shape_peak_dh):
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
        fuels_h_peak = np.zeros((fuels.shape[0], 24))

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for fueltype, fuel in enumerate(fuels):
            fuels_h_peak[fueltype] = shape_peak_dh * fuel

        return fuels_h_peak
