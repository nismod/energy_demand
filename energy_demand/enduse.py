"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
import copy
import numpy as np
from energy_demand.scripts_technologies import diffusion_technologies as diffusion
from energy_demand.scripts_initalisations import initialisations as init
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_technologies import fuel_service_switch
from energy_demand.scripts_basic import testing_functions as testing
from energy_demand.scripts_shape_handling import generic_shapes as generic_shapes

class Enduse(object):
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

    Info
    ----
    Every enduse can only have on shape independently of the fueltype

    `self.enduse_fuel_new_y` is always overwritten in the cascade of fuel calculations

    Problem: Not all enduses have technologies assigned. Therfore peaks are derived from techstock in case there are technologies,
    otherwise enduse load shapes are used.
    """
    def __init__(self, reg_name, data, enduse, sector, enduse_fuel, tech_stock, heating_factor_y, cooling_factor_y, fuel_switches, service_switches, fuel_enduse_tech_p_by, service_tech_by_p, tech_increased_service, tech_decreased_share, tech_constant_share, installed_tech, sig_param_tech, enduse_overall_change_ey, dw_stock, load_profiles):
        """Enduse class constructor
        """
        print("..create enduse {}".format(enduse))
        self.enduse = enduse
        self.sector = sector
        self.curr_yr = data['curr_yr']
        self.base_yr = data['base_yr']
        self.end_yr = data['end_yr']
        self.sim_period = data['sim_period']
        self.enduse_fuel_y = enduse_fuel
        self.enduse_fuel_new_y = copy.deepcopy(enduse_fuel)

        # Test whether fuel is provided for enduse
        if np.sum(enduse_fuel) == 0: # Enduse has no fuel. Create empty shapes
            self.enduse_fuel_yd = np.zeros((self.enduse_fuel_y.shape[0], 365))
            self.enduse_fuel_yh = np.zeros((self.enduse_fuel_y.shape[0], 365, 24))
            self.enduse_fuel_peak_dh = np.zeros((self.enduse_fuel_y.shape[0], 24))
            self.enduse_fuel_peak_h = np.zeros((self.enduse_fuel_y.shape[0]))
        else:
            self.crit_switch_fuel = self.get_crit_switch_fuel(fuel_switches)
            self.crit_switch_service = self.get_crit_switch_service(service_switches)
            testing.testing_switch_criteria(self.crit_switch_fuel, self.crit_switch_service, self.enduse)

            # Get technologies of enduse depending on assumptions on fuel switches or service switches
            self.technologies_enduse = self.get_enduse_tech(service_tech_by_p, fuel_enduse_tech_p_by)

            # Calculate fuel for hybrid technologies (electricity is defined, other fuel shares are calculated)
            fuel_enduse_tech_p_by = self.adapt_fuel_enduse_tech_p_by('hybrid_gas_electricity', fuel_enduse_tech_p_by, tech_stock, self.enduse_fuel_new_y, data['assumptions']['hybrid_technologies'])
            #fuel_enduse_tech_p_by = self.adapt_fuel_enduse_tech_p_by('hybrid_hydrogen_electricity', fuel_enduse_tech_p_by, tech_stock, self.enduse_fuel_new_y, data['assumptions']['hybrid_technologies'])
            #fuel_enduse_tech_p_by = self.adapt_fuel_enduse_tech_p_by('hybrid_biomass_electricity', fuel_enduse_tech_p_by, tech_stock, self.enduse_fuel_new_y, data['assumptions']['hybrid_technologies'])
            #TODO: FOR ALL OTHER HYBRDI TECHNOLOGIES

            # -------------------------------
            # Yearly fuel calculation cascade
            # --------------------------------
            print("Fuel train A: " + str(np.sum(self.enduse_fuel_new_y)))
            testsumme = np.sum(self.enduse_fuel_new_y[2])
            testsumme2 = self.enduse_fuel_new_y

            # Change fuel consumption based on climate change induced temperature differences
            self.temp_correction_hdd_cdd(cooling_factor_y, heating_factor_y, data['assumptions'])
            print("Fuel train B: " + str(np.sum(self.enduse_fuel_new_y)))

            # Calcualte smart meter induced general savings
            self.smart_meter_eff_gain(data['assumptions'])
            print("Fuel train C: " + str(np.sum(self.enduse_fuel_new_y)))

            # Enduse specific consumption change in % (due e.g. to other efficiciency gains). No technology considered
            self.enduse_specific_change(data['assumptions'], enduse_overall_change_ey)
            print("Fuel train D: " + str(np.sum(self.enduse_fuel_new_y)))

            # Calculate new fuel demands after scenario drivers
            self.enduse_building_stock_driver(dw_stock, reg_name)
            print("Fuel elec E: " + str(np.sum(self.enduse_fuel_new_y)))
            print("Fuel all fueltypes E: " + str(np.sum(self.enduse_fuel_new_y)))

            # ----------------------------------
            # Hourly fuel calculation cascade
            # ----------------------------------
            print("Enduse {} is defined.... ".format(enduse) + str(self.technologies_enduse))

            for fueltype in range(self.enduse_fuel_y.shape[0]):
                print("FUELTYPE - enduse  {} ".format(np.sum(self.enduse_fuel_y[fueltype])))

            # ------------------------------------------------------------------------
            # Calculate regional energy service (for current year after e.g. smart meter and temp and general fuel redution)
            # MUST IT REALLY BE FOR BASE YEAR (I donpt think so)
            # ------------------------------------------------------------------------
            tot_service_h_cy, service_tech, service_tech_cy_p, service_fueltype_tech_cy_p, service_fueltype_cy_p = self.fuel_to_service_cy(
                fuel_enduse_tech_p_by,
                tech_stock,
                data['lu_fueltype'],
                load_profiles
                )

            # ---------------------------------------------------------------------------------------
            # Reduction of service because of heat recovery (standard sigmoid diffusion)
            # ---------------------------------------------------------------------------------------
            tot_service_h_cy = self.service_reduction_heat_recovery(data['assumptions'], tot_service_h_cy, 'tot_service_h_cy', data['assumptions']['heat_recovered'])
            service_tech = self.service_reduction_heat_recovery(data['assumptions'], service_tech, 'service_tech', data['assumptions']['heat_recovered'])

            control_tot_service = 0
            for tech, fuel in service_tech.items():
                control_tot_service += np.sum(fuel)
            print("control_tot_service A: " + str(control_tot_service))

            # --------------------------------
            # Energy service switches
            # --------------------------------
            if self.crit_switch_service:
                service_tech = self.switch_tech_service(
                    tot_service_h_cy,
                    service_tech_cy_p,
                    tech_increased_service[enduse],
                    tech_decreased_share[enduse],
                    tech_constant_share[enduse],
                    sig_param_tech
                    )

            '''control_tot_service = 0
            for tech, fuel in service_tech.items():
                #print("tech before service switch: " + str(tech) + str("  ") + str(self.enduse) + "  " + str(np.sum(fuel)))
                control_tot_service += np.sum(fuel)
            print("control_tot_service B: " + str(control_tot_service))
            np.testing.assert_almost_equal(control_tot_service, np.sum(tot_service_h_cy), err_msg="not all technologies were specieified for each provided fuelty")
            '''
            # --------------------------------
            # Fuel Switches
            # --------------------------------
            if self.crit_switch_fuel:
                service_tech = self.switch_tech_fuel(
                    installed_tech,
                    sig_param_tech,
                    tot_service_h_cy,
                    service_tech,
                    service_fueltype_tech_cy_p,
                    service_fueltype_cy_p,
                    fuel_switches,
                    fuel_enduse_tech_p_by
                    )

            control_tot_service = 0
            for tech, fuel in service_tech.items():
                control_tot_service += np.sum(fuel)
                #print("tech before service switch: " + str(tech) + str("  ") + str(self.enduse) + "  " + str(np.sum(fuel)))
            #print("control_tot_service C: " + str(control_tot_service))

            # -------------------------------------------------------
            # Convert Service to Fuel
            # -------------------------------------------------------
            # Convert service to fuel (y) for each fueltype depending on technological efficiences in current year
            self.service_to_fuel_fueltype_y(service_tech, tech_stock)
            print("Fuel train G ele : " + str(np.sum(self.enduse_fuel_new_y[2])))
            print("Fuel train G all: " + str(np.sum(self.enduse_fuel_new_y)))

            # Convert service to fuel per tech (y) for each technology depending on technological efficiences in current year
            enduse_fuel_tech_y = self.service_to_fuel_per_tech(service_tech, tech_stock)

            # -------------------------------------------------------
            # Fuel shape assignement
            # -------------------------------------------------------

            #---NON-PEAK
            # Iterate technologies in enduse and assign technology specific shape for respective fuels
            self.enduse_fuel_yd = self.calc_enduse_fuel_tech_yd(enduse_fuel_tech_y, tech_stock, load_profiles)
            print("Fuel train Gb ele : " + str(np.sum(self.enduse_fuel_new_y[2])))
            print("Fuel train Gb all: " + str(np.sum(self.enduse_fuel_new_y)))
            print("Fuel train I: " + str(np.sum(self.enduse_fuel_yd)))
            print("Fuel train I: " + str(np.sum(self.enduse_fuel_yd[2])))

            self.enduse_fuel_yh = self.calc_enduse_fuel_tech_yh(enduse_fuel_tech_y, tech_stock, load_profiles)
            print("Fuel train aa ele : " + str(np.sum(self.enduse_fuel_new_y[2])))
            print("Fuel train aa all: " + str(np.sum(self.enduse_fuel_new_y)))
            print("Fuel train K: " + str(np.sum(self.enduse_fuel_yh)))
            print("Fuel train K: " + str(np.sum(self.enduse_fuel_yh[2])))

            '''if round(np.sum(self.enduse_fuel_yh[2]), 0) != round(testsumme, 0):
                print(testsumme)
                print(np.sum(self.enduse_fuel_yh[2]))
                sys.exit("ERRROR O HMAN")
            '''
            #if round(np.sum(self.enduse_fuel_yh), 1) != round(np.sum(testsumme2), 1):
            #np.testing.assert_almost_equal(np.sum(self.enduse_fuel_yh), np.sum(testsumme2), decimal=1, err_msg='Error 2')

            # --PEAK

            # Iterate technologies in enduse and assign technology specific shape for peak for respective fuels
            self.enduse_fuel_peak_dh = self.calc_enduse_fuel_peak_tech_dh(
                data['assumptions'],
                enduse_fuel_tech_y,
                tech_stock,
                load_profiles
                )

            # Get maximum hour demand per of peak day
            self.enduse_fuel_peak_h = self.get_peak_h_from_dh()

            # Testing
            np.testing.assert_almost_equal(np.sum(self.enduse_fuel_yd), np.sum(self.enduse_fuel_yh), decimal=2, err_msg='', verbose=True)

    def service_reduction_heat_recovery(self, assumptions, service_to_reduce, crit_dict, assumption_heat_recovered):
        """Reduce heating demand according to assumption on heat reuse

        A standard sigmoid diffusion is assumed from base year to end year

        Parameters
        ----------
        assumptions : dict
            Assumptions
        service_to_reduce : dict or array
            Service of current year
        crit_dict :

        Returns
        -------
        service_to_reduce or service_to_reduce
        """
        if self.enduse in assumption_heat_recovered:

            # Fraction of heat recovered until end_year
            heat_recovered_p_by = assumption_heat_recovered[self.enduse]

            if heat_recovered_p_by == 0: # IF heat is recovered
                return service_to_reduce
            else:

                # Fraction of heat recovered in current year
                sig_diff_factor = diffusion.sigmoid_diffusion(
                    self.base_yr,
                    self.curr_yr,
                    self.end_yr,
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness']
                )

                heat_recovered_p_cy = sig_diff_factor * heat_recovered_p_by

                # Apply to technologies each stored in dictionary
                if crit_dict == 'service_tech':
                    service_to_reduce_new = {}
                    for tech, service_tech in service_to_reduce.items():
                        service_to_reduce_new[tech] = service_tech * (1.0 - heat_recovered_p_cy)

                # Apply to array
                if crit_dict == 'tot_service_h_cy':
                    service_to_reduce_new = service_to_reduce * (1.0 - heat_recovered_p_cy)

                return service_to_reduce_new
        else:
            return service_to_reduce

    def fuel_to_service_cy(self, fuel_enduse_tech_p_by, tech_stock, fueltypes_lu, load_profiles):
        """Calculate energy service of each technology based on assumptions about base year fuel shares of an enduse

        This calculation converts fuels into energy services (e.g. fuel for heating into heat demand)
        and then calculates the fraction of an invidual technology to which it contributes to total energy
        service (e.g. how much of total heat demand condensing boilers contribute).

        Parameters
        ----------
        fuel_enduse_tech_p_by : dict
            Fuel composition of base year for every fueltype for each enduse (assumtions for national scale)
        tech_stock : object
            Technology stock of region

        Return (TODO)
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

        The service is calculated after changes to fuel were applied (in the cascade
        such as e.g. due to changes in temperatures or similar)
        """
        service_tech_cy = init.init_dict(self.technologies_enduse, 'zero')
        service_fueltype_tech_p = init.init_service_fueltype_tech_by_p(fueltypes_lu, fuel_enduse_tech_p_by)

        # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
        for fueltype, fuel_enduse in enumerate(self.enduse_fuel_new_y):
            for tech in fuel_enduse_tech_p_by[fueltype]:
                print("tech: {} ".format(tech))

                # Fuel for each technology, calculated based on defined fuel fraction within fueltype for by (assumed national share of fuel of technology * tot fuel)
                fuel_tech_y = fuel_enduse_tech_p_by[fueltype][tech] * fuel_enduse

                # Distribute y to yh by multiplying total fuel of technology with yh fuel shape
                fuel_tech_yh = fuel_tech_y * load_profiles.get_load_profile(self.enduse, self.sector, tech, 'shape_yh') # OCHS

                # ------------------------------
                # Convert to energy service for base year (because the actual service is provided in base year)
                # - The base year efficiency is taken because the actual service can only be calculated with base year efficiny.
                # - However, the enduse_fuel_y is taken because the actual service was reduced e.g. due to smart meters or temperatur changes
                # - The actual base year service demand (without any other changes for base year) must be calulated with enduse_fuel_y
                # ------------------------------
                service_tech_yh_by = fuel_tech_yh * tech_stock.get_tech_attr(self.enduse, tech, 'eff_cy')

                # service_distr_hybrid_h_p_cy
                service_tech_cy[tech] += service_tech_yh_by

                #print("fuel to service:  {}  {}    fuel enduse: {}       fuel tech: {}        service: {}  fueltype:  {}".format(tech, np.sum(tech_stock.get_tech_attr(self.enduse, self.sector, tech, 'eff_cy')), np.sum(fuel_enduse), np.sum(fuel_tech_y), np.sum(service_tech_yh_by), fueltype))
                service_fueltype_tech_p[fueltype][tech] += np.sum(service_tech_yh_by)

        # --------------------------------------------------
        # Convert or aggregate service to other formats
        # --------------------------------------------------
        # --Calculate energy service demand over the full year and for every hour, sum demand accross all technologies
        tot_service_yh = np.zeros((365, 24))
        for _, service_tech in service_tech_cy.items():
            tot_service_yh += service_tech

        # --Convert to percentage
        service_tech_p = {}
        for technology, service_tech in service_tech_cy.items():
            service_tech_p[technology] = np.divide(1, np.sum(tot_service_yh)) * np.sum(service_tech)

        # Convert service per fueltype of technology
        for fueltype, service_fueltype in service_fueltype_tech_p.items():

            # Calculate total sum within fueltype
            sum_within_fueltype = sum(service_fueltype.values())

            # Calculate fraction of servcie per technology
            for tech, service_fueltype_tech in service_fueltype.items():
                if sum_within_fueltype > 0:
                    service_fueltype_tech_p[fueltype][tech] = np.divide(1, np.sum(sum_within_fueltype)) * service_fueltype_tech
                else:
                    service_fueltype_tech_p[fueltype][tech] = 0

        # Calculate service fraction per fueltype
        service_fueltype_p = init.init_dict(fueltypes_lu.values(), 'zero')
        for fueltype, service_fueltype in service_fueltype_tech_p.items():
            for tech, service_fueltype_tech in service_fueltype.items():
                service_fueltype_p[fueltype] += service_fueltype_tech

        return tot_service_yh, service_tech_cy, service_tech_p, service_fueltype_tech_p, service_fueltype_p

    def adapt_fuel_enduse_tech_p_by(self, tech, fuel_enduse_tech_p_by, tech_stock, enduse_fuel_new_y, hybrid_technologies):
        """Change the fuel share of low temp technologies for hybrid tech

        TODO: Define the two hybrid technologies possible (hydrogen, elec), gas-elec
        TODO: DESCRIBE BETTEr
        """
        for hybrid_tech in hybrid_technologies:
            if hybrid_tech in self.technologies_enduse:

                # Hybrid technologies information
                tech_low = tech_stock.get_tech_attr(self.enduse, tech, 'tech_low_temp')
                tech_low_temp_fueltype = tech_stock.get_tech_attr(self.enduse, tech, 'tech_low_temp_fueltype')
                tech_high_temp_fueltype = tech_stock.get_tech_attr(self.enduse, tech, 'tech_high_temp_fueltype')

                # Convert electricity share of heat pump into service
                if tech in fuel_enduse_tech_p_by[tech_high_temp_fueltype]:

                    # Electricity fuel of heat pump
                    fuel_high_tech = fuel_enduse_tech_p_by[tech_high_temp_fueltype][hybrid_tech] * enduse_fuel_new_y[tech_high_temp_fueltype]

                    # Calculate shares of fuels of hybrid tech
                    total_fuels = np.sum(tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')[tech_low_temp_fueltype]) + np.sum(tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')[tech_high_temp_fueltype])

                    share_fuel_high_temp_tech = (1 / total_fuels) * np.sum(tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')[tech_high_temp_fueltype])
                    share_fuel_low_temp_tech = (1 / total_fuels) * np.sum(tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')[tech_low_temp_fueltype])

                    # Calculate fuel with given fuel of hp and share of hp/other fuel
                    fuel_low_tech = fuel_high_tech * (share_fuel_low_temp_tech / share_fuel_high_temp_tech)

                    # Calculate fraction of total fuel of low temp technolgy (e.g. how much gas of total gas)
                    fuel_hyrid_low_temp_tech_p = (1.0 / enduse_fuel_new_y[tech_low_temp_fueltype]) * fuel_low_tech

                    # Substract % from gas boiler
                    fuel_enduse_tech_p_by[tech_low_temp_fueltype][hybrid_tech] = fuel_hyrid_low_temp_tech_p
                    fuel_enduse_tech_p_by[tech_low_temp_fueltype][str(tech_low)] -= fuel_hyrid_low_temp_tech_p #substract from low tech defined share

        # ---------------------------------------------------------------------------------------------------------------------------------
        # Iterate all technologies and round that total sum within each fueltype is always 1 (needs to be done because of rounding errors)
        # TODO: improve rounding method: https://stackoverflow.com/questions/13483430/how-to-make-rounded-percentages-add-up-to-100
        # ---------------------------------------------------------------------------------------------------------------------------------
        for fueltype in fuel_enduse_tech_p_by:
            if sum(fuel_enduse_tech_p_by[fueltype].values()) != 1.0 and fuel_enduse_tech_p_by[fueltype] != {}: #if rounding error
                for tech in fuel_enduse_tech_p_by[fueltype]:
                    fuel_enduse_tech_p_by[fueltype][tech] = (1.0 / sum(fuel_enduse_tech_p_by[fueltype].values())) * fuel_enduse_tech_p_by[fueltype][tech]

        return fuel_enduse_tech_p_by

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
        max_fuel_d = 0

        # Sum all fuely across all fueltypes for every day and hour in a year
        all_fueltypes_tot_h = np.sum(enduse_fuel_yh, axis=0) #shape (365, 24)

        # Iterate summed fueltypes to read out maximum fuel
        for day_nr, services_dh in enumerate(all_fueltypes_tot_h):
            day_sum = np.sum(services_dh)

            if day_sum > max_fuel_d:
                max_fuel_d = day_sum
                peak_day_nr = day_nr

        #print("Peak Day Number {}  with peak fuel demand (across all fueltypes): {}   {}      ".format(peak_day_nr, max_fuel_dy, self.enduse))
        return peak_day_nr

    def get_enduse_tech(self, service_tech_cy_p, fuel_enduse_tech_p_by):
        """Get all defined technologies of an enduse

        Parameters
        ----------
        service_tech_cy_p : dict
            Percentage of total service per technology in base year in
        fuel_enduse_tech_p_by : dict
            Percentage of fuel per enduse per technology

        Return
        ------
        technologies_enduse : list
            All technologies (no technolgy is added twice)

        Depending on whether fuel swatches are implemented or services switches
        """
        if self.crit_switch_service:
            technologies_enduse = service_tech_cy_p.keys()
        else:
            # If no fuel switch and no service switch, read out base year technologies
            technologies_enduse = set([])
            for _, tech_fueltype in fuel_enduse_tech_p_by.items():
                for tech in tech_fueltype.keys():
                    technologies_enduse.add(tech)

        return list(technologies_enduse)

    def switch_tech_service(self, tot_service_h_cy, service_tech_by_p, tech_increase_service, tech_decrease_service, tech_constant_service, sig_param_tech):
        """Scenaric service switches
        All diminishing technologies are proportionally to base year share diminished.
        Paramters
        ---------
        tot_service_h_cy : array
            Hourly service of all technologies
        tech_stock : object
            Technology stock
        Returns
        -------
        service_tech_cy : dict
            Current year fuel for every technology (e.g. fueltype 1: 'techA': fuel) for every hour
        """
        print("...Service switch is implemented "  + str(self.enduse))
        service_tech_cy_p = {}
        service_tech_cy = {}

        # -------------
        # Technology with increaseing service
        # -------------
        # Calculate diffusion of service for technology with increased service
        service_tech_increase_cy_p = self.get_service_diffusion(tech_increase_service, sig_param_tech)

        for tech_increase, share_tech in service_tech_increase_cy_p.items():
            service_tech_cy_p[tech_increase] = share_tech # Add shares to output dict

        # -------------
        # Technology with decreasing service
        # -------------
        # Calculate proportional share of technologies with decreasing service of base year (distribution in base year)
        service_tech_decrease_by_rel = fuel_service_switch.get_service_rel_tech_decrease_by(
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
            service_tech_cy[tech] = tot_service_h_cy * enduse_share  # Total yearly hourly service * share of enduse

        print("...Finished service switch")
        return service_tech_cy

    def get_service_diffusion(self, tech_increased_service, sig_param_tech):
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
            service_tech_cy_p[tech_installed] = diffusion.sigmoid_function(
                self.curr_yr,
                sig_param_tech[self.enduse][tech_installed]['l_parameter'],
                sig_param_tech[self.enduse][tech_installed]['midpoint'],
                sig_param_tech[self.enduse][tech_installed]['steepness']
            )

        return service_tech_cy_p

    def get_crit_switch_fuel(self, fuelswitches):
        """Test whether there is a fuelswitch for this enduse

        Parameters
        ----------
        fuelswitches : dict
            All fuel switches

        Note
        ----
        If base year, no switches are implemented
        """
        if self.base_yr == self.curr_yr:
            return False
        else:
            fuel_switches_enduse = []

            for fuelswitch in fuelswitches:
                if fuelswitch['enduse'] == self.enduse: #If fuelswitch belongs to this enduse
                    fuel_switches_enduse.append(fuelswitch)

            if len(fuel_switches_enduse) > 0: # != []:
                return True
            else:
                return False

    def get_crit_switch_service(self, service_switches):
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
        if self.base_yr == self.curr_yr:
            return crit_service_switch
        else:
            for service_switch in service_switches:
                if service_switch['enduse'] == self.enduse:
                    crit_service_switch = True

            return crit_service_switch

    def get_peak_h_from_dh(self):
        """Iterate peak day fuels and select peak hour

        # The peak of the individual fueltypes may not be all in the same hour of the day
        """
        peak_fueltype_h = np.zeros((self.enduse_fuel_peak_dh.shape[0]))

        # Peak values for every fueltype
        for fueltype, fuel_dh in enumerate(self.enduse_fuel_peak_dh):
            #print("--peakfinidng: " + str(fueltype) + str("  ") + str(np.max(fuel_dh)))
            peak_fueltype_h[fueltype] = np.max(fuel_dh) # Get hour with maximum fuel in a day of fueltype

        #print("TESTSUM: " + str(np.sum(peak_fueltype_h)))
        return peak_fueltype_h

    def calc_enduse_fuel_peak_tech_dh(self, assumptions, enduse_fuel_tech, tech_stock, load_profile):
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

        Returns
        -------
        fuels_peak_dh : array
            Peak values for peak day for every fueltype

        Notes
        ------
        *   For some technologies the dh peak day profile is not read in from technology stock but from
            shape_yh of peak day (hybrid technologies).
        """
        fuels_peak_dh = np.zeros((self.enduse_fuel_new_y.shape[0], 24))

        for tech in self.technologies_enduse:
            #print("TECH ENDUSE    {}   {}".format(tech, self.enduse))
            # Get yd fuel shape of technology
            fuel_shape_yd = load_profile.get_load_profile(self.enduse, self.sector, tech, 'shape_yd')

            # Calculate absolute fuel values for yd
            fuel_tech_y_d = enduse_fuel_tech[tech] * fuel_shape_yd
            #print("FUEL  yd: " + str(np.sum(fuel_tech_y_d)))

            # Get day with most fuel across all fueltypes (this is selected as max day)
            peak_day_nr = self.get_peak_fuel_day(self.enduse_fuel_yh)
            #print("FUEL PEAK DAY 2: " + str(fuel_tech_peak_d))

            # If shape is read directly from yh (e.g. hybrid technology, service cooling and ventilation)
            if tech in assumptions['list_tech_heating_hybrid'] or tech in assumptions['list_tech_cooling_ventilation']: #assumptions['list_tech_cooling']:

                # Calculate fuel for peak day
                fuel_tech_peak_d = fuel_tech_y_d[peak_day_nr]

                # The 'shape_peak_dh'is not defined in technology stock because in the 'Region' the peak day is not yet known
                # Therfore, the shape_yh is read in and with help of information on peak day the hybrid dh shape generated
                tech_peak_dh_absolute = load_profile.get_load_profile(self.enduse, self.sector, tech, 'shape_yh')[peak_day_nr]
                tech_peak_dh = shape_handling.absolute_to_relative(tech_peak_dh_absolute)
            else:
                # Calculate fuel for peak day
                fuel_tech_peak_d = np.sum(enduse_fuel_tech[tech]) * load_profile.get_load_profile(self.enduse, self.sector, tech, 'enduse_peak_yd_factor')

                # Assign Peak shape of a peak day of a technology
                tech_peak_dh = load_profile.get_shape_peak_dh(self.enduse, self.sector, tech)

            # Multiply absolute d fuels with dh peak fuel shape
            fuel_tech_peak_dh = tech_peak_dh * fuel_tech_peak_d

            # Get fueltypes (distribution) of tech for peak day
            fueltypes_tech_share_yd = tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')

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

    def calc_enduse_fuel_tech_yd(self, enduse_fuel_tech, tech_stock, load_profiles):
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
        fuels_yd = np.zeros((self.enduse_fuel_new_y.shape[0], 365))

        for tech in self.technologies_enduse:

            # Multiply shape with fuel
            fuel_tech_yd = enduse_fuel_tech[tech] * load_profiles.get_load_profile(self.enduse, self.sector, tech, 'shape_yd') # OCHS

            # Get fueltypes of tech for every day
            fueltype_tech_share_yd = tech_stock.get_tech_attr(self.enduse, tech, 'fuel_types_shares_yd')

            # Iterate shares of fueltypes, calculate share of fuel and add to fuels
            for fueltype, fuel_shares_dh in enumerate(fueltype_tech_share_yd):

                if np.sum(fuel_shares_dh) != 0:
                    share_of_fuel = (1.0 / 8760) * np.sum(fuel_shares_dh)
                else:
                    share_of_fuel = np.zeros((365))

                fuels_yd[fueltype] += fuel_tech_yd * share_of_fuel

            # Testing
            np.testing.assert_array_almost_equal(np.sum(fuel_tech_yd), np.sum(enduse_fuel_tech[tech]), decimal=3, err_msg="Error NR XXX")

        # Testing
        #np.testing.assert_array_almost_equal(sum(enduse_fuel_tech.values()), np.sum(control_sum), decimal=2, err_msg="Error: The y to h fuel did not work")

        return fuels_yd

    def calc_enduse_fuel_tech_yh(self, enduse_fuel_tech, tech_stock, load_profiles):
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
        fuels_yh = np.zeros((self.enduse_fuel_new_y.shape[0], 365, 24))
        control_sum = 0

        for tech in self.technologies_enduse:

            # Shape of fuel of technology for every hour in year
            fuel_tech_yh = enduse_fuel_tech[tech] * load_profiles.get_load_profile(self.enduse, self.sector, tech, 'shape_yh') # OCHS

            # Get distribution of fuel for every hour
            fueltypes_tech_share_yh = tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')

            for fueltype, fuel_tech_share in enumerate(fueltypes_tech_share_yh):
                if np.sum(fuel_tech_share) != 0:
                    share_of_fuel = (1.0 / 8760) * np.sum(fuel_tech_share)
                else:
                    share_of_fuel = np.zeros((365, 24))

                fuels_yh[fueltype] += fuel_tech_yh * share_of_fuel

                control_sum += fuel_tech_yh * share_of_fuel

        # Assert --> If this assert is done, then we need to substract the fuel from yearly data and run function:  service_to_fuel_fueltype_y
        np.testing.assert_array_almost_equal(np.sum(fuels_yh), np.sum(control_sum), decimal=2, err_msg="Error: The y to h fuel did not work")

        return fuels_yh

    def switch_tech_fuel(self, installed_tech, sig_param_tech, tot_service_h_cy, service_tech, service_fueltype_tech_cy_p, service_fueltype_cy_p, fuel_switches, fuel_enduse_tech_p_by):
        """Scenaric fuel switches

        Based on assumptions about shares of fuels which are switched per enduse to specific
        technologies, the installed technologies are used to calculate the new service demand
        after switching fuel shares.

        Parameters
        ----------

        assumptions : dict
            Assumptions
        tot_service_h_cy : dict
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
        print("... fuel_switch is implemented")

        service_tech_after_switch = copy.deepcopy(service_tech)

        # Iterate all technologies which are installed in fuel switches
        for tech_installed in installed_tech[self.enduse]:

            # Read out sigmoid diffusion of service of this technology for the current year
            diffusion_cy = diffusion.sigmoid_function(
                self.curr_yr,
                sig_param_tech[self.enduse][tech_installed]['l_parameter'],
                sig_param_tech[self.enduse][tech_installed]['midpoint'],
                sig_param_tech[self.enduse][tech_installed]['steepness'])

            # Calculate increase in service based on diffusion of installed technology (diff & total service== Todays demand) - already installed service
            print("eeeeeeeeeeeeeeeeee")
            print(sig_param_tech[self.enduse][tech_installed])
            print(tech_installed)
            print(np.sum(service_tech[tech_installed]))
            print(diffusion_cy)
            print(np.sum(tot_service_h_cy))

            #OLD
            ##service_tech_installed_cy = (diffusion_cy * tot_service_h_cy) - service_tech[tech_installed]

            #NEW
            service_tech_installed_cy = (diffusion_cy * tot_service_h_cy)

            print("-----------Tech_installed:  "  + str(tech_installed) + str(self.curr_yr))
            print(" service_tech_installed_cy: {}".format(np.sum(service_tech_installed_cy)))
            print("diffusion_cy  " + str(diffusion_cy))
            print(" Tot service before " + str(np.sum(tot_service_h_cy)))
            print(" Tot service after  " + str(np.sum(service_tech_after_switch[tech_installed])))
            print("----")
            print(np.sum(diffusion_cy * tot_service_h_cy))
            print(np.sum(service_tech[tech_installed]))
            print(np.sum((diffusion_cy * tot_service_h_cy) - service_tech[tech_installed]))
            print("TODAY SHARE (fraciton): " + str(np.sum((1 / np.sum(tot_service_h_cy)) * service_tech[tech_installed])))

            # Assert if minus demand
            #assert np.sum((diffusion_cy * tot_service_h_cy) - service_tech[tech_installed]) >= 0

            # Get service for current year for technologies
            #service_tech_after_switch[tech_installed] += service_tech_installed_cy
            service_tech_after_switch[tech_installed] = service_tech_installed_cy #NEW
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
                    tot_service_switched_all_tech_instal_p += service_fueltype_cy_p[fuelswitch['enduse_fueltype_replace']] * fuelswitch['share_fuel_consumption_switched']

            print(" ")
            print("replaced fueltypes: " + str(fueltypes_replaced))
            print("Service demand which is switched with this technology: " + str(tot_service_switched_all_tech_instal_p))

            # Iterate all fueltypes which are affected by the technology installed
            for fueltype_replace in fueltypes_replaced:

                # Get all technologies of the replaced fueltype
                #technologies_replaced_fueltype = fuel_enduse_tech_p_by[self.enduse][fueltype_replace].keys()
                technologies_replaced_fueltype = fuel_enduse_tech_p_by[fueltype_replace].keys()

                # Find fuel switch where this fueltype is replaced
                for fuelswitch in fuel_switches: #assumptions['rs_fuel_switches']:
                    if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed and fuelswitch['enduse_fueltype_replace'] == fueltype_replace:

                        # Service reduced for this fueltype (service technology cy sigmoid diff *  % of heat demand within fueltype)
                        if tot_service_switched_all_tech_instal_p == 0:
                            reduction_service_fueltype = 0
                        else:
                            # share of total service of fueltype * share of replaced fuel
                            service_fueltype_tech_cy_p_rel = np.divide(1.0, tot_service_switched_all_tech_instal_p) * (service_fueltype_cy_p[fueltype_replace] * fuelswitch['share_fuel_consumption_switched'])

                            print("service_fueltype_tech_cy_p_rel -- : " + str(service_fueltype_tech_cy_p_rel))
                            reduction_service_fueltype = service_tech_installed_cy * service_fueltype_tech_cy_p_rel
                        break

                print("Reduction of additional service of technology in replaced fueltype: " + str(np.sum(reduction_service_fueltype)))

                # Iterate all technologies in within the fueltype and calculate reduction per technology
                for technology_replaced in technologies_replaced_fueltype:
                    print(" ")
                    print("technology_replaced: " + str(technology_replaced))
                    # It needs to be calculated within each region the share how the fuel is distributed...
                    # Share of heat demand for technology in fueltype (share of heat demand within fueltype * reduction in servide demand)
                    service_demand_tech = service_fueltype_tech_cy_p[fueltype_replace][technology_replaced] * reduction_service_fueltype
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
                        print(np.sum(service_tech_after_switch[technology_replaced] - service_demand_tech))
                        #sys.exit("ERROR: Service cant be minus") #TODO TODO TODO TODO
                        service_tech_after_switch[technology_replaced] = 0
                    else:
                        # Substract technology specific servide demand
                        service_tech_after_switch[technology_replaced] -= service_demand_tech
                        #print("B: " + str(np.sum(service_tech_after_switch[technology_replaced])))

                # Testing
                #assert np.testing.assert_almost_equal(np.sum(test_sum), np.sum(reduction_service_fueltype), decimal=4)

        return service_tech_after_switch

    def service_to_fuel_fueltype_y(self, service_tech, tech_stock):
        """Convert energy service to yearly fuel

        For every technology the service is taken and converted to fuel based on efficiency of current year

        The attribute 'enduse_fuel_new_y' is updated

        Inputs
        ------
        service_tech : dict
            Service per fueltype and technology
        tech_stock : object
            Technological stock

        Info
        -----
        Fuel = Energy service / efficiency

        - Note: Because for hybrid technologies the service is split into two fueltypes according to the fuel assignement
        based on temperature and efficincies, the recalculated fuel shares are different than the once provided in the assumptino. However,
        the overall share stays the same. Because assignin initial shares of gas or electricity for individual technologies is anyway difficult.
        """
        enduse_fuels = np.zeros((self.enduse_fuel_new_y.shape))

        # Convert service to fuel
        for tech, service in service_tech.items():

            # If hybrid tech, calculate share of service for each technology
            fuel_tech = np.divide(service, tech_stock.get_tech_attr(self.enduse, tech, 'eff_cy'))
            fueltype_share_yh = tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')

            for fueltype, fuel_share in enumerate(fueltype_share_yh):

                share_of_fuel = (1.0 / np.sum(fueltype_share_yh)) * np.sum(fuel_share)
                fuel_fueltype = share_of_fuel * np.sum(fuel_tech)

                ##print("-- service to fuel: {} service:  {} fuel_tech: {} fueltyp: {}  fuel_fueltype: {}".format(tech, np.sum(service), np.sum(fuel_tech), fueltype, np.sum(fuel_fueltype)))
                enduse_fuels[fueltype] += np.sum(fuel_fueltype) # Share of fuel of fueltype_hybrid * fuel

        setattr(self, 'enduse_fuel_new_y', enduse_fuels)

    def service_to_fuel_per_tech(self, service_tech, tech_stock):
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
        fuel_tech = {}
        control_sum = 0

        # Convert service to fuel
        for tech, service in service_tech.items():
            fuel = np.divide(service, tech_stock.get_tech_attr(self.enduse, tech, 'eff_cy'))
            control_sum += np.sum(fuel)
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
        percent_ey = enduse_overall_change_ey[self.enduse]

        # Share of fuel consumption difference
        diff_fuel_consump = percent_ey - percent_by
        diffusion_choice = assumptions['other_enduse_mode_info']['diff_method'] # Diffusion choice

        if diff_fuel_consump != 0: # If change in fuel consumption
            new_fuels = np.zeros((self.enduse_fuel_new_y.shape[0])) # fueltypes, days, hours

            # Lineare diffusion up to cy
            if diffusion_choice == 'linear':
                lin_diff_factor = diffusion.linear_diff(
                    self.base_yr,
                    self.curr_yr,
                    percent_by,
                    percent_ey,
                    len(self.sim_period)
                )
                change_cy = diff_fuel_consump * abs(lin_diff_factor)

            # Sigmoid diffusion up to cy
            elif diffusion_choice == 'sigmoid':
                sig_diff_factor = diffusion.sigmoid_diffusion(
                    self.base_yr,
                    self.curr_yr,
                    self.end_yr,
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness']
                    )
                change_cy = diff_fuel_consump * sig_diff_factor

            # Calculate new fuel consumption percentage
            for fueltype, fuel in enumerate(self.enduse_fuel_new_y):
                new_fuels[fueltype] = fuel * (1.0 + change_cy)

            setattr(self, 'enduse_fuel_new_y', new_fuels)

    def temp_correction_hdd_cdd(self, cooling_factor_y, heating_factor_y, assumptions):
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
        new_fuels = np.zeros((self.enduse_fuel_new_y.shape[0]))

        if self.enduse in assumptions['enduse_space_heating']:
            for fueltype, fuel in enumerate(self.enduse_fuel_new_y):
                new_fuels[fueltype] = fuel * heating_factor_y

            setattr(self, 'enduse_fuel_new_y', new_fuels)

        elif self.enduse in assumptions['enduse_space_cooling']: # 'cooling': #TODO
            for fueltype, fuel in enumerate(self.enduse_fuel_new_y):
                new_fuels[fueltype] = fuel * cooling_factor_y

            setattr(self, 'enduse_fuel_new_y', new_fuels)

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
            new_fuels = np.zeros((self.enduse_fuel_new_y.shape[0]))

            # Sigmoid diffusion up to current year
            sigm_factor = diffusion.sigmoid_diffusion(
                self.base_yr,
                self.curr_yr,
                self.end_yr,
                assumptions['sig_midpoint'], assumptions['sig_steeppness']
                )

            # Smart Meter penetration (percentage of people having smart meters)
            penetration_by = assumptions['smart_meter_p_by']
            penetration_cy = assumptions['smart_meter_p_by'] + (sigm_factor * (assumptions['smart_meter_p_ey'] - assumptions['smart_meter_p_by']))

            for fueltype, fuel in enumerate(self.enduse_fuel_new_y):
                saved_fuel = fuel * (penetration_by - penetration_cy) * assumptions['general_savings_smart_meter'][self.enduse] # Saved fuel
                new_fuels[fueltype] = fuel - saved_fuel

            setattr(self, 'enduse_fuel_new_y', new_fuels)

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
        new_fuels = copy.deepcopy(self.enduse_fuel_new_y)

        # Test if enduse has a building related scenario driver
        if hasattr(dw_stock[reg_name][self.base_yr], self.enduse) and self.curr_yr != self.base_yr:

            # Scenariodriver of building stock base year and new stock
            by_driver = getattr(dw_stock[reg_name][self.base_yr], self.enduse)
            cy_driver = getattr(dw_stock[reg_name][self.curr_yr], self.enduse)

            # base year / current (checked) (as in chapter 3.1.2 EQ E-2)
            factor_driver = np.divide(cy_driver, by_driver) # FROZEN

            new_fuels *= factor_driver

            setattr(self, 'enduse_fuel_new_y', new_fuels)

class genericFlatEnduse(object):
    """Class for generic enduses with flat shapes
    """
    def __init__(self, enduse_fuel):
        self.enduse_fuel_y = enduse_fuel

        # Generate flat shapes (i.e. same amount of fuel for every hour in a year)
        shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd = generic_shapes.generic_flat_shape(shape_peak_yd_factor=1)

        # Convert shape_peak_dh into fuel per day
        max_fuel_d = np.zeros((self.enduse_fuel_y.shape[0]))
        for fueltype in range(len(enduse_fuel)):
            # Multiply average daily fuel demand for flat shape * peak factor
            max_fuel_d[fueltype] = (np.sum(self.enduse_fuel_y[fueltype]) / 365.0) * shape_peak_yd_factor

        # Yd fuel shape per fueltype (non-peak)
        self.enduse_fuel_yd = np.zeros((self.enduse_fuel_y.shape[0], 365))
        for fueltype in range(len(enduse_fuel)):
            self.enduse_fuel_yd[fueltype] = shape_non_peak_yd * self.enduse_fuel_y[fueltype]

        # Yh fuel shape per fueltype (non-peak)
        self.enduse_fuel_yh = np.zeros((self.enduse_fuel_y.shape[0], 365, 24))
        for fueltype in range(len(enduse_fuel)):
            for day in range(365):
                self.enduse_fuel_yh[fueltype][day] = (shape_non_peak_yd[day] * shape_non_peak_dh[day]) * self.enduse_fuel_y[fueltype]

        # Dh fuel shape per fueltype (peak)
        self.enduse_fuel_peak_dh = np.zeros((self.enduse_fuel_y.shape[0], 24))
        for fueltype in range(len(enduse_fuel)):
            # day shape (sum= 1) * (yearly_fuel * shape_peak_yd_factor)
            self.enduse_fuel_peak_dh[fueltype] = shape_peak_dh * max_fuel_d[fueltype]

        # h fuel shape per fueltype (peak)
        self.enduse_fuel_peak_h = self.get_peak_h_from_dh()

    def get_peak_h_from_dh(self):
        """Iterate peak day fuels and select peak hour

        Return
        ------
        peak_fueltype_h : array
            Fuel per fueltype in peak day
        """
        peak_fueltype_h = np.zeros((self.enduse_fuel_peak_dh.shape[0]))

        for fueltype, fuel_dh in enumerate(self.enduse_fuel_peak_dh):

            # Get maximum fuel per fueltype of peak day
            peak_fueltype_h[fueltype] = np.max(fuel_dh)

        return peak_fueltype_h
