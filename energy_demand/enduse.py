"""
Enduse
========

Contains the `Enduse` Class. This is the most important class
where the change in enduse specific energy demand is simulated
depending on scenaric assumptions.
"""
import copy
import logging
import numpy as np
from energy_demand.technologies import diffusion_technologies
from energy_demand.initalisations import initialisations as init
from energy_demand.profiles import load_profile as lp
from energy_demand.technologies import fuel_service_switch
from energy_demand.basic import testing_functions as testing

class Enduse(object):
    """Enduse Class (Residential, Service and Industry)

    For every region and sector, a different instance
    is generated. In this class, first the change in
    energy demand is calculated on a yearls temporal scale.
    Calculations are performed in a cascade (e.g. first
    reducing climate change induced savings, then substracting
    further behavioural savings etc.). After yearly calculations,
    the demand is converted to hourly demand.

    Also within this function, the fuel inputs are converted
    to energy service (short: service) and later on
    converted back to fuel demand.

    Arguments
    ----------
    region_name : str
        Region name
    data : dict
        Data container
    enduse : str
        Enduse name
    sector : str
        Sector name
    fuel : array
        Yearly fuel data for different fueltypes
    tech_stock : object
        Technology stock of region
    heating_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with HDD)
    cooling_factor_y : array
        Distribution of fuel within year to days (yd) (directly correlates with CDD)
    fuel_switches : list
        Fuel switches
    service_switches : list
        Service switches
    fuel_tech_p_by : dict
        Fuel tech assumtions in base year
    tech_increased_service : dict
        Technologies per enduse with increased service due to scenarios
    tech_decreased_share : dict
        Technologies per enduse with decreased service due to scenarios
    tech_constant_share : dict
        Technologies per enduse with constat service
    installed_tech : dict
        Installed technologes per enduse
    sig_param_tech : dict
        Sigmoid parameters
    enduse_overall_change_ey : dict
        Assumptions related to overal change in endyear
    regional_lp_stock : object
        Load profile stock
    dw_stock : object,default=False
        Dwelling stock
    reg_scen_drivers : bool,default=None
        Scenario drivers per enduse
    crit_flat_profile : bool,default=False
        Criteria of enduse has a flat shape or not

    Note
    ----
    - Load profiles are assigned independently of the fueltype, i.e.
      the same profiles are assumed to hold true across different fueltypes

    - ``self.fuel_new_y`` is always overwritten in the cascade of calculations

    Warning
    -------
    Not all enduses have technologies assigned. Load peaks are derived
    from techstock in case technologies are defined. Otherwise enduse load
    profiles are used.
    """
    def __init__(
            self,
            region_name,
            data,
            enduse,
            sector,
            fuel,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            fuel_switches,
            service_switches,
            fuel_tech_p_by,
            tech_increased_service,
            tech_decreased_share,
            tech_constant_share,
            installed_tech,
            sig_param_tech,
            enduse_overall_change_ey,
            regional_lp_stock,
            dw_stock=False,
            reg_scen_drivers=None,
            crit_flat_profile=False
        ):
        """Enduse class constructor
        """
        self.enduse = enduse
        self.sector = sector
        self.fuel_new_y = np.copy(fuel)
        self.crit_flat_profile = crit_flat_profile

        # If enduse has no fuel return empty shapes
        if np.sum(fuel) == 0:
            self.crit_flat_profile = True
            self.fuel_y = np.zeros((fuel.shape[0]), dtype=float)
            self.fuel_yh = 0
            self.fuel_peak_dh = np.zeros((fuel.shape[0], 24), dtype=float)
            self.fuel_peak_h = 0
        else:
            # -----------------------------------------------------------------
            # Get correct parameters depending on model configuration
            # -----------------------------------------------------------------
            load_profiles = self.get_lp_stock(
                data['non_regional_lp_stock'],
                regional_lp_stock)

            self.enduse_techs = self.get_enduse_tech(
                fuel_tech_p_by)

            # Calculate fuel for hybrid technologies
            '''fuel_tech_p_by = self.adapt_fuel_tech_p_by(
                fuel_tech_p_by,
                tech_stock,
                data['assumptions']['hybrid_technologies'])'''

            # -------------------------------
            # Cascade of calculations on a yearly scale
            # --------------------------------
            # --Change fuel consumption based on climate change induced temperature differences
            self.apply_climate_change(
                cooling_factor_y,
                heating_factor_y,
                data['assumptions'])
            logging.debug("Fuel train B: " + str(np.sum(self.fuel_new_y)))

            # --Change fuel consumption based on smart meter induced general savings
            self.apply_smart_metering(
                data['assumptions'],
                data['sim_param'])
            #logging.debug("Fuel train C: " + str(np.sum(self.fuel_new_y)))

            # --Enduse specific consumption change in %
            self.apply_specific_change(
                data['assumptions'],
                enduse_overall_change_ey,
                data['sim_param'],
                data['lookups'])
            logging.debug("Fuel train D: " + str(np.sum(self.fuel_new_y)))

            # -------------------------------------------------------------------------------
            # Calculate new fuel demands after scenario drivers
            # -------------------------------------------------------------------------------
            self.apply_scenario_drivers(
                dw_stock,
                region_name,
                data,
                reg_scen_drivers,
                data['sim_param'])
            logging.debug("Fuel train E: " + str(np.sum(self.fuel_new_y)))
            # ----------------------------------
            # Hourly Disaggregation
            # ----------------------------------
            if self.enduse_techs == []:
                """If no technologies are defined for an enduse, the load profiles
                are read from dummy shape, which show the load profiles of the whole enduse.
                No switches can be implemented and only overall change of enduse.

                Note: for heating, technologies need to be assigned. Otherwise,
                here there will be problems
                """
                self.assign_load_profiles_no_techs(data, load_profiles)
            else:
                """If technologies are defined for an enduse
                """

                # ----
                # Get enduse specific configurations
                # ----
                mode_constrained, crit_switch_fuel, crit_switch_service = self.get_enduse_configuration(
                    data, fuel_switches, service_switches)

                # ------------------------------------
                # Calculate regional energy service
                # ------------------------------------
                tot_service_h_cy, service_tech, service_tech_cy_p, service_fueltype_tech_cy_p, service_fueltype_cy_p = self.fuel_to_service(
                    fuel_tech_p_by,
                    tech_stock,
                    data['lookups']['fueltype'],
                    load_profiles,
                    mode_constrained,
                    data['assumptions']['model_yeardays'],
                    data['assumptions']['model_yeardays_nrs']
                    )

                # ------------------------------------
                # Reduction of service because of heat recovery
                # (standard sigmoid diffusion)
                # ------------------------------------
                tot_service_h_cy = self.apply_heat_recovery(
                    data['assumptions'],
                    tot_service_h_cy,
                    'tot_service_h_cy',
                    data['sim_param'])

                service_tech = self.apply_heat_recovery(
                    data['assumptions'],
                    service_tech,
                    'service_tech',
                    data['sim_param'])

                # --------------------------------
                # Switches (service or fuel)
                # --------------------------------
                if crit_switch_service:
                    logging.info("... Service switch is implemented")
                    service_tech = self.service_switch(
                        tot_service_h_cy,
                        service_tech_cy_p,
                        tech_increased_service[enduse],
                        tech_decreased_share[enduse],
                        tech_constant_share[enduse],
                        sig_param_tech,
                        data['sim_param']['curr_yr'])
                elif crit_switch_fuel:
                    logging.debug("... Fuel switch is implemented")
                    service_tech = self.fuel_switch(
                        installed_tech,
                        sig_param_tech,
                        tot_service_h_cy,
                        service_tech,
                        service_fueltype_tech_cy_p,
                        service_fueltype_cy_p,
                        fuel_switches,
                        fuel_tech_p_by,
                        data['sim_param']['curr_yr'])
                else:
                    pass #No switch implemented

                # -------------------------------------------
                # Convert annual service to fuel per fueltype
                # -------------------------------------------
                fuel_tech_y = self.service_to_fuel(
                    service_tech,
                    tech_stock,
                    data['lookups'],
                    mode_constrained,
                    data['assumptions']['model_yeardays'])

                '''# Convert annaul service to fuel per fueltype for each technology
                fuel_tech_y = self.service_to_fuel_per_tech(
                    service_tech,
                    tech_stock,
                    mode_constrained,
                    data['assumptions']['model_yeardays'])'''

                # ------------------------------------------
                # Assign load profiles
                # ------------------------------------------
                self.assign_load_profiles_techs(
                    tech_stock,
                    fuel_tech_y,
                    data,
                    mode_constrained,
                    load_profiles)

    def get_enduse_configuration(self, data, fuel_switches, service_switches):
        """
        """
        mode_constrained = self.get_running_mode(
            data['assumptions']['mode_constrained'],
            data['assumptions']['enduse_space_heating'])

        crit_switch_fuel = self.get_crit_switch(
            fuel_switches, data['sim_param'], mode_constrained)

        crit_switch_service = self.get_crit_switch(
            service_switches, data['sim_param'], mode_constrained)

        testing.testing_switch_criteria(
            crit_switch_fuel,
            crit_switch_service,
            self.enduse)

        return mode_constrained, crit_switch_fuel, crit_switch_service 

    def assign_load_profiles_no_techs(self, data, load_profiles):
        """TODO
        """
        if self.crit_flat_profile:

            # Calculate fraction if flat shape of selected days to model
            self.fuel_y = self.fuel_new_y * data['assumptions']['model_yeardays_nrs']/365.0
        else:
            self.fuel_yh = load_profiles.get_lp(
                self.enduse,
                self.sector,
                'dummy_tech',
                'shape_yh') * self.fuel_new_y[:, np.newaxis, np.newaxis]

            # Read dh profile from peak day
            peak_day = self.get_peak_day()

            shape_peak_dh = lp.abs_to_rel(
                self.fuel_yh[:, peak_day, :])
            enduse_peak_yd_factor = load_profiles.get_lp(
                self.enduse, self.sector, 'dummy_tech', 'enduse_peak_yd_factor')

            self.fuel_peak_dh = self.fuel_new_y[:, np.newaxis] * enduse_peak_yd_factor * shape_peak_dh

            self.fuel_peak_h = lp.calk_peak_h_dh(self.fuel_peak_dh)

        return

    def assign_load_profiles_techs(self, tech_stock, fuel_tech_y, data, mode_constrained, load_profiles):
        """Assign load profile to enduse

        TODO
        """
        if self.crit_flat_profile:
            '''If a flat load profile is assigned (crit_flat_profile)
            do not store whole 8760 profile. This is only done in
            the summing step to save on memory
            '''
            self.fuel_y = self.calc_fuel_tech_y(
                tech_stock,
                fuel_tech_y,
                data['lookups'],
                mode_constrained)
        else:

            #---NON-PEAK
            self.fuel_yh = self.calc_fuel_tech_yh(
                fuel_tech_y,
                tech_stock,
                load_profiles,
                data['lookups'],
                mode_constrained,
                data['assumptions']['model_yeardays_nrs']
                )

            # --PEAK
            # Iterate technologies in enduse and assign technology specific profiles
            self.fuel_peak_dh = self.calc_peak_tech_dh(
                fuel_tech_y,
                tech_stock,
                load_profiles,
                data['lookups']
                )

            # Get maximum hour demand of peak day
            self.fuel_peak_h = lp.calk_peak_h_dh(self.fuel_peak_dh)

        return

    def get_lp_stock(self, non_regional_lp_stock, regional_lp_stock):
        """Defines the load profile stock depending on `enduse`.
        (Get regional or non-regional load profile data)

        Arguments
        ----------
        non_regional_lp_stock : object
            Non regional dependent load profiles
        regional_lp_stock : object
            Regional dependent load profiles

        Returns
        -------
        load_profiles : object
            Load profile

        Note
        -----
        Because for some enduses the load profiles depend on the region
        they are stored in the `WeatherRegion` Class. One such example is
        heating. If the enduse is not dependent on the region, the same
        load profile can be used for all regions

        If the enduse depends on regional factors, `regional_lp_stock`
        is returned. Otherwise, non-regional load profiles which can
        be applied for all regions is used (`non_regional_lp_stock`)
        """
        if self.enduse in non_regional_lp_stock.enduses_in_stock:
            return non_regional_lp_stock
        else:
            return regional_lp_stock

    def get_running_mode(self, mode_constrained, enduse_space_heating):
        """Check which mode needs to be run for an enduse

        Arguments
        -----------
        mode_constrained : bool
            Criteria of running mode
        enduse_space_heating : dict
            All heating enduses across all models

        Returns
        -------
        bool : bool
            The return value

        Note
        ----
        If 'crit_mode' == True, then overall heat is provided to
        the supply model not specified for technologies. Otherwise,
        heat demand is supplied per technology
        """
        if mode_constrained and self.enduse in enduse_space_heating:
            return True
        else:
            return False

    def calc_fuel_tech_y(self, tech_stock, fuel_tech_y, lookups, mode_constrained):
        """Calculate yearly fuel per fueltype (no load profile assigned)

        Arguments
        -----------
        tech_stock : object
            Technology stock
        fuel_tech_y : dict
            Fuel per technology per year
        lookups : dict
            look-up
        mode_constrained : bool
            Running mode

        Returns
        -------
        fuel_y : array
            Fuel per year per fueltype

        Note
        ----
        This function can be run in two different modes
        """
        fuel_y = np.zeros((lookups['fueltypes_nr']), dtype=float)

        if mode_constrained: #Constrained mode
            # Assign all to heat fueltype
            #fueltypes_tech_share_yh = np.zeros((lookups['fueltype']['fueltypes_nr']), dtype=float)
            #fueltypes_tech_share_yh[lookups['fueltype']['heat']] = 1

            for tech, fuel_tech_y in fuel_tech_y.items():
                
                tech_fuel_type_int = tech_stock.get_tech_attr(
                    self.enduse,
                    tech,
                    'tech_fueltype_int'
                    )

                #fuel_y += np.sum(fuel_tech_y) * fueltypes_tech_share_yh
                fuel_y[lookups['fueltype']['heat']] += np.sum(fuel_tech_y) #* fueltypes_tech_share_yh

        else:
            for tech, fuel_tech_y in fuel_tech_y.items():
                #fueltypes_tech_share_yh = tech_stock.get_tech_attr(
                #    self.enduse,
                #    tech,
                #    'fueltype_share_yh_all_h'
                #    )
                tech_fuel_type_int = tech_stock.get_tech_attr(
                    self.enduse,
                    tech,
                    'tech_fueltype_int'
                    )
                #fuel_y += np.sum(fuel_tech_y) * fueltypes_tech_share_yh
                fuel_y[tech_fuel_type_int] += np.sum(fuel_tech_y) #* fueltypes_tech_share_yh #BEO

        return fuel_y

    def apply_heat_recovery(self, assumptions, service, crit_dict, base_sim_param):
        """Reduce heating demand according to assumption on heat reuse

        Arguments
        ----------
        assumptions : dict
            Assumptions
        service : dict or array
            Service of current year
        crit_dict : str
            Criteria to run function differently
        base_sim_param : dict
            Base simulation parameters

        Returns
        -------
        service_reduced : dict or array
            Reduced service after assumption on reuse

        Note
        ----
        A standard sigmoid diffusion is assumed from base year to end year
        """
        if self.enduse in assumptions['heat_recovered']:

            # Fraction of heat recovered until end_year
            heat_recovered_p_by = assumptions['heat_recovered'][self.enduse]

            if heat_recovered_p_by == 0:
                return service
            else:

                # Fraction of heat recovered in current year
                sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                    base_sim_param['base_yr'],
                    base_sim_param['curr_yr'],
                    base_sim_param['end_yr'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness']
                )

                heat_recovered_p_cy = sig_diff_factor * heat_recovered_p_by

                # Apply to technologies each stored in dictionary
                if crit_dict == 'service_tech':
                    service_reduced = {}
                    for tech, service_tech in service.items():
                        service_reduced[tech] = service_tech * (1.0 - heat_recovered_p_cy)

                # Apply to array
                elif crit_dict == 'tot_service_h_cy':
                    service_reduced = service * (1.0 - heat_recovered_p_cy)

                return service_reduced
        else:
            return service

    def fuel_to_service(self, fuel_tech_p_by, tech_stock, lu_fueltypes, load_profiles, mode_constrained, model_yeardays, model_yeardays_nrs,):
        """Converts fuel to energy service (1),
        calcualates contribution service fraction (2)

        Arguments
        ----------
        fuel_tech_p_by : dict
            Fuel composition of base year for every fueltype for each
            enduse (assumtions for national scale)
        tech_stock : object
            Technology stock of region
        lu_fueltypes : dict
            Fueltype look-up
        load_profiles : object
            Load profiles
        mode_constrained : bool
            Criteria about mode

        Return
        ------
        tot_service_yh : array
            Total yh energy service per technology for base year (nr_of_days, 24)
        service_tech_cy : dict
            Energy service for every fueltype and technology
        service_tech_p : dict
            Fraction of energy service per technology
        service_fueltype_tech_p : dict
            Fraction of energy service per fueltype and technology
        service_fueltype_p : dict
            Fraction of service per fueltype

        Note
        -----
        **(1)** Calculate energy service of each technology based on assumptions
        about base year fuel shares of an enduse (`fuel_tech_p_by`).

        **(2)** The fraction of an invidual technology to which it
        contributes to total energy service (e.g. how much of
        total heat service is provided by boiler technology).

        -  Efficiency changes of technologis are considered.

        - Energy service = fuel * efficiency
        - This function can be run in two modes, depending on `mode_constrained` criteria
        - The base year efficiency is taken because the actual service can
          only be calculated with base year. Otherwise, the service would
          increase e.g. if technologies would become more efficient.
          Efficiencies are only considered if converting back to fuel
          However, the self.fuel_new_y is taken because the actual
          service was reduced e.g. due to smart meters or temperatur changes
        """
        if mode_constrained:
            """
            Constrained version
            no efficiencies are considered, because not technology specific service calculation
            """
            service_tech_cy = init.dict_zero(self.enduse_techs)
            service_fueltype_tech_p = init.service_type_tech_by_p(lu_fueltypes, fuel_tech_p_by)

            # Calculate share of service
            for fueltype, tech_list in fuel_tech_p_by.items():
                for tech, fuel_share in tech_list.items():

                    tech_load_profile = load_profiles.get_lp(
                        self.enduse,
                        self.sector,
                        tech,
                        'shape_yh'
                        )

                    fuel_tech = self.fuel_new_y[fueltype] * fuel_share

                    service = fuel_tech * tech_load_profile
                    service_tech_cy[tech] += service[[model_yeardays]]

                    # Assign all service to fueltype 'heat_fueltype'
                    try:
                        service_fueltype_tech_p[lu_fueltypes['heat']][tech] += float(np.sum(fuel_tech))
                    except KeyError:
                        service_fueltype_tech_p[lu_fueltypes['heat']][tech] = 0
                        service_fueltype_tech_p[lu_fueltypes['heat']][tech] += float(np.sum(fuel_tech))
        else:
            """Unconstrained version
            """
            service_tech_cy = init.dict_zero(self.enduse_techs)
            service_fueltype_tech_p = init.service_type_tech_by_p(lu_fueltypes, fuel_tech_p_by)

            tot_service_yh = np.zeros((model_yeardays_nrs, 24)) #NEW
            tot_service_y = 0
            service_fueltype_p = {}

            # Calulate share of energy service per tech depending on fuel and efficiencies
            for fueltype, tech_list in fuel_tech_p_by.items():
                service_fueltype_p[fueltype] = 0 #NEW
                for tech, fuel_share in tech_list.items():

                    # Base year eff must be used
                    tech_eff = tech_stock.get_tech_attr(
                        self.enduse, tech, 'eff_by')

                    tech_load_profile = load_profiles.get_lp(
                        self.enduse, self.sector, tech, 'shape_yh')

                    # Calculate fuel share and convert fuel to service
                    service_tech_y = self.fuel_new_y[fueltype] * fuel_share * tech_eff

                    # Calculate fuel share and convert fuel to service
                    if self.crit_flat_profile:
                        #_service = np.full((model_yeardays_nrs, 24), 1 / (model_yeardays_nrs * 24))
                        #service =  service_tech_y * _service * (model_yeardays_nrs / 365)
                        _service = np.full((model_yeardays_nrs, 24), 1 / (24)) #FASTER
                        service =  service_tech_y * _service * (1 / 365)
                    else:
                        service = service_tech_y * tech_load_profile

                    # Distribute y to yh profile and selection
                    service_tech_cy[tech] += service

                    # Add fuel for each technology (float() is necessary to avoid inf error)
                    #_sum = float(np.sum(service_tech))
                    #service_fueltype_tech_p[fueltype][tech] += _sum
                    service_fueltype_tech_p[fueltype][tech] += service_tech_y

                    # Calculate service fraction per fueltype and total service
                    #service_fueltype_p[fueltype] += _sum
                    service_fueltype_p[fueltype] += service_tech_y

                    # Sum service accross all technologies (365, 24)
                    tot_service_yh += service #NEW
                    #tot_service_y += _sum
                    tot_service_y += service_tech_y

        # --------------------------------------------------
        # Convert or aggregate service to other formats
        # --------------------------------------------------
        # Convert service of every technology to fraction of total service
        service_tech_p = self.convert_service_to_p(service_tech_cy, tot_service_y)

        # Convert service per fueltype of technology
        for fueltype, service_fueltype in service_fueltype_tech_p.items():
            for tech, service_fueltype_tech in service_fueltype.items():
                try:
                    #service_fueltype_tech_p[fueltype][tech] = service_fueltype_tech / sum(service_fueltype.values())
                    service_fueltype_tech_p[fueltype][tech] = service_fueltype_tech / float(service_fueltype_p[fueltype])
                except ZeroDivisionError:
                    service_fueltype_tech_p[fueltype][tech] = 0

        # --Calculate service fraction per fueltype
        #service_fueltype_p = {fueltype: sum(service_fueltype.values()) for fueltype, service_fueltype in service_fueltype_tech_p.items()}

        return tot_service_yh, service_tech_cy, service_tech_p, service_fueltype_tech_p, service_fueltype_p

    @classmethod
    def convert_service_to_p(cls, service_tech_cy, tot_service_y):
        """Calculate fraction of service for every technology of total service

        Arguments
        ----------
        service_tech_cy : array
            Service per technology
        tot_service_y : float
            Total yearly service

        Returns
        -------
        service_tech_p : dict
            All tecnology services are
            provided as a fraction of total service

        Note
        ----
        Iterate over values in dict and apply calculations
        """
        '''try:
            _total_service = 1.0 / float(np.sum(tot_service_yh))
        except ZeroDivisionError:
            _total_service = 0'''
        if tot_service_y == 0:
            _total_service = 0
        else:
            _total_service = 1 / tot_service_y
            
        # Apply calculation over all values of a dict
        service_tech_p = {
            technology: np.sum(service_tech) * _total_service for technology, service_tech in service_tech_cy.items()
            }

        return service_tech_p

    '''def adapt_fuel_tech_p_by(self, fuel_tech_p_by, tech_stock, hybrid_technologies):
        """Change the fuel share of hybrid technologies for base year
        depending on assumed electricity consumption

        Arguments
        ----------
        fuel_tech_p_by : dict
            Fuel fraction per technology in base year
        tech_stock : object
            Technology stock
        hybrid_technologies : list
            List with hybrid technologies

        Note
        -----
        - Because in case of hybrid technologies the share for fuel is not known
          of the auxiliry (low-temperature) technology, this share gets calculated.
        - For hybrid technologies, only the fuel share of heat pump must be defined
        """
        for hybrid_tech in hybrid_technologies:
            if hybrid_tech in self.enduse_techs:

                # Hybrid technologies information
                tech_low = tech_stock.get_tech_attr(
                    self.enduse, hybrid_tech, 'tech_low_temp')
                tech_low_fueltype = tech_stock.get_tech_attr(
                    self.enduse, hybrid_tech, 'tech_low_temp_fueltype')
                tech_high_fueltype = tech_stock.get_tech_attr(
                    self.enduse, hybrid_tech, 'tech_high_temp_fueltype')

                # Convert electricity share of heat pump into service
                if hybrid_tech in fuel_tech_p_by[tech_high_fueltype]:

                    # Electricity fuel of heat pump
                    fuel_high_tech = fuel_tech_p_by[tech_high_fueltype][hybrid_tech] * self.fuel_new_y[tech_high_fueltype]

                    # Calculate shares of fuels of hybrid tech
                    fuel_share_tech_low = np.sum(tech_stock.get_tech_attr(
                        self.enduse, hybrid_tech, 'fueltypes_yh_p_cy')[tech_low_fueltype])
                    fuel_share_tech_high = np.sum(tech_stock.get_tech_attr(
                        self.enduse, hybrid_tech, 'fueltypes_yh_p_cy')[tech_high_fueltype])

                    total_fuels = fuel_share_tech_low + fuel_share_tech_high

                    share_fuel_low_temp_tech = fuel_share_tech_low / total_fuels 
                    share_fuel_high_temp_tech = fuel_share_tech_high / total_fuels

                    # Calculate fuel with given fuel of hp and share of hp/other fuel
                    fuel_low_tech = fuel_high_tech * (share_fuel_low_temp_tech / share_fuel_high_temp_tech)

                    # Calculate fraction of total fuel of low temp technolgy (e.g. how much gas of total gas)
                    fuel_hyrid_low_temp_tech_p = (1.0 / self.fuel_new_y[tech_low_fueltype]) * fuel_low_tech

                    # Substract % from gas boiler
                    fuel_tech_p_by[tech_low_fueltype][hybrid_tech] = fuel_hyrid_low_temp_tech_p
                    fuel_tech_p_by[tech_low_fueltype][str(tech_low)] -= fuel_hyrid_low_temp_tech_p

        # ----------------------------------------------------------------------
        # Iterate all technologies and round that total sum within each fueltype
        # is always 1 (needs to be done because of rounding errors)
        # Maybe use other rounding method:
        # https://stackoverflow.com/questions/13483430/how-to-make-rounded-percentages-add-up-to-100
        # ----------------------------------------------------------------------
        for fueltype in fuel_tech_p_by:
            if sum(fuel_tech_p_by[fueltype].values()) != 1.0 and fuel_tech_p_by[fueltype] != {}: #if rounding error
                for tech in fuel_tech_p_by[fueltype]:
                    fuel_tech_p_by[fueltype][tech] = (1.0 / sum(fuel_tech_p_by[fueltype].values())) * fuel_tech_p_by[fueltype][tech]

        return fuel_tech_p_by
    '''

    def get_peak_day(self):
        """Iterate yh and get day with highes fuel (across all fueltypes)

        Return
        ------
        peak_day_nr : int
            Day with most fuel or service across all fueltypes

        Note
        -----
        - The day with most fuel across all fueltypes is
        considered to be the peak day
        - The Peak day may change date in a year
        """
        # Sum all fuel across all fueltypes for every hour in a year
        all_fueltypes_tot_h = np.sum(self.fuel_yh, axis=0)

        # Sum fuel within every hour for every day and get day with maximum fuel
        peak_day_nr = np.argmax(np.sum(all_fueltypes_tot_h, axis=1))

        return peak_day_nr

    @classmethod
    def get_enduse_tech(cls, fuel_tech_p_by):
        """Get all defined technologies of an enduse

        Arguments
        ----------
        fuel_tech_p_by : dict
            Percentage of fuel per enduse per technology

        Return
        ------
        enduse_techs : list
            All technologies (no technolgy is added twice)

        Note
        ----
        All technologies are read out, including those which
        are potentiall defined in fuel or service switches.

        If for an enduse a dummy technology is defined,
        the technologies of an enduse are set to an empty
        list.

        Warning
        -------
        For every enduse technologes must either be defined
        for no fueltype or for all fueltypes
        """
        enduse_techs = []
        for tech_fueltype in fuel_tech_p_by.values():
            for tech in tech_fueltype.keys():
                enduse_techs.append(tech)

                if tech == 'dummy_tech':
                    return []

        return list(set(enduse_techs))

    def service_switch(self, tot_service_h_cy, service_tech_by_p, tech_increase_service, tech_decrease_service, tech_constant_service, sig_param_tech, curr_yr):
        """Apply change in service depending on defined service switches

        Paramters
        ---------
        tot_service_h_cy : array
            Hourly service of all technologies
        service_tech_by_p : dict
            Fraction of service per technology
        tech_increase_service : dict
            Technologies with increased service
        tech_decrease_service : dict
            Technologies with decreased service
        tech_constant_service : dict
            Technologies with constant service
        sig_param_tech : dict
            Sigmoid diffusion parameters
        curr_yr : int
            Current year

        Returns
        -------
        service_tech_cy : dict
            Service per technology in current year after switch

        Note
        ----
        The service which is fulfilled by new technologies is
        substracted of the replaced technologies proportionally
        to the base year distribution of these technologies
        """
        logging.debug("... Service switch is implemented "  + str(self.enduse))
        service_tech_cy_p = {}
        service_tech_cy = {}

        # -------------
        # Technology with increaseing service
        # Calculate diffusion of service for technology with increased service
        # -------------
        service_tech_incr_cy_p = self.get_service_diffusion(
            tech_increase_service,
            sig_param_tech,
            curr_yr
            )

        # Add shares
        for tech_increase, share_tech in service_tech_incr_cy_p.items():
            service_tech_cy_p[tech_increase] = share_tech

        # -------------
        # Technology with decreasing service
        # Calculate proportional share of technologies with decreasing service of base year
        # -------------
        service_tech_decrease_by_rel = fuel_service_switch.get_service_rel_tech_decr_by(
            tech_decrease_service,
            service_tech_by_p
            )

        # Add shares of base_year to output dict
        for tech_decrease in service_tech_decrease_by_rel:
            service_tech_cy_p[tech_decrease] = service_tech_by_p[tech_decrease]

        # Calculated gained service and substract this proportionally of all decreasing technologies
        for tech_incr in service_tech_incr_cy_p:

            # Difference in service up to current year
            diff_service_incr = service_tech_incr_cy_p[tech_incr] - service_tech_by_p[tech_incr]

            # Substract service gain proportionaly to all technologies which are
            # lowered and substract from other technologies
            for tech_decr, service_tech_decr in service_tech_decrease_by_rel.items():
                service_to_substract = service_tech_decr * diff_service_incr

                # Substract service
                # Because of rounding errors the service may fall below zero
                # (therfore set to zero if only slighlty minus)
                if np.sum(service_tech_cy_p[tech_decr] - service_to_substract) < 0:
                    service_tech_cy_p[tech_decr] *= 0 # Set to zero service
                else:
                    service_tech_cy_p[tech_decr] -= service_to_substract

        # -------------
        # Technology with constant service
        # -------------
        # Add all technologies with unchanged service in the future
        for tech_constant in tech_constant_service:
            service_tech_cy_p[tech_constant] = service_tech_by_p[tech_constant]

        # Multiply share of each tech with hourly service
        for tech, enduse_share in service_tech_cy_p.items():
            # Total yearly hourly service * share of endusers_tech_decreased_share
            service_tech_cy[tech] = tot_service_h_cy * enduse_share

        return service_tech_cy

    def get_service_diffusion(self, tech_increased_service, sig_param_tech, curr_yr):
        """Calculate energy service fraction of technologies with increased service

        Arguments
        ----------
        tech_increased_service : dict
            All technologies per enduse with increased future service share
        sig_param_tech : dict
            Sigmoid diffusion parameters
        curr_yr : dict
            Current year

        Returns
        -------
        service_tech_cy_p : dict
            Share of service per technology of current year
        """
        service_tech_cy_p = {}

        for tech_installed in tech_increased_service:
            # Get service for current year based on sigmoid diffusion
            service_tech_cy_p[tech_installed] = diffusion_technologies.sigmoid_function(
                curr_yr,
                sig_param_tech[self.enduse][tech_installed]['l_parameter'],
                sig_param_tech[self.enduse][tech_installed]['midpoint'],
                sig_param_tech[self.enduse][tech_installed]['steepness']
            )

        return service_tech_cy_p

    def get_crit_switch(self, fuelswitches, base_parameters, mode_constrained):
        """Test whether there is a switch (service or fuel)

        Arguments
        ----------
        fuelswitches : dict
            All fuel switches
        base_parameters : float
            Base Arguments
        mode_constrained : bool
            Mode criteria

        Note
        ----
        If base year, no switches are implemented
        """
        if base_parameters['base_yr'] == base_parameters['curr_yr'] or mode_constrained is True:
            return False
        else:
            for fuelswitch in fuelswitches:
                if fuelswitch['enduse'] == self.enduse:
                    return True

            return False

    def calc_peak_tech_dh(self, enduse_fuel_tech, tech_stock, load_profile, lookups):
        """Calculate peak demand for every fueltype

        Arguments
        ----------
        assumptions : array
            Assumptions
        enduse_fuel_tech : array
            Fuel per enduse and technology
        tech_stock : data
            Technology stock
        load_profile : object
            Load profile

        Returns
        -------
        fuels_peak_dh : array
            Peak values for peak day for every fueltype

        Note
        ----
        - This function gets the hourly values of the peak day for every fueltype.
          The daily fuel is converted to dh for each technology.

        - For some technology types (heat_pump and hybrid)
          the dh peak day profile is not read in from technology
          stock but from shape_yh of peak day (hybrid technologies).
        """
        fuels_peak_dh = np.zeros((lookups['fueltypes_nr'], 24), dtype=float)

        # Get day with most fuel across all fueltypes
        peak_day_nr = self.get_peak_day()

        for tech in self.enduse_techs:
            #logging.debug("TECH ENDUSE    {}   {}".format(tech, self.enduse))

            tech_type = tech_stock.get_attribute_tech_stock(tech, self.enduse, 'tech_type')

            if tech_type == 'hybrid':# or tech_type == 'heat_pump': #Maybe add ventilation TODO
                """Read fuel from peak day
                """
                # Calculate absolute fuel values for yd (multiply fuel with yd_shape)
                fuel_tech_yd = enduse_fuel_tech[tech] * load_profile.get_lp(
                    self.enduse, self.sector, tech, 'shape_yd')

                # Calculate fuel for peak day
                fuel_tech_peak_d = fuel_tech_yd[peak_day_nr]

                # The 'shape_peak_dh'is not defined in technology stock because
                # in the 'Region' the peak day is not yet known
                # Therfore, the shape_yh is read in and with help of
                # information on peak day the hybrid dh shape generated
                tech_peak_dh = load_profile.get_lp(
                    self.enduse, self.sector, tech, 'shape_y_dh')[peak_day_nr]
            else:
                """Calculate fuel with peak factor
                """
                # Calculate fuel for peak day
                fuel_tech_peak_d = np.sum(enduse_fuel_tech[tech]) * load_profile.get_lp(
                    self.enduse, self.sector, tech, 'enduse_peak_yd_factor')

                # Assign Peak shape of a peak day of a technology
                tech_peak_dh = load_profile.get_shape_peak_dh(
                    self.enduse, self.sector, tech)

            # Multiply absolute d fuels with dh peak fuel shape
            fuel_tech_peak_dh = tech_peak_dh * fuel_tech_peak_d

            # Get fueltypes (distribution) of tech for peak day
            ##fueltypes_tech_share_yd = tech_stock.get_tech_attr(self.enduse, tech, 'fueltypes_yh_p_cy')
            
            fueltypes_tech_share_yd = 1
            # BEO
            tech_fuel_type_int = tech_stock.get_tech_attr(
                self.enduse, tech, 'tech_fueltype_int')

            # Peak day fuel shape * fueltype distribution for peak day
            # select from (7, nr_of_days, 24) only peak day for all fueltypes
            #fuels_peak_dh += fuel_tech_peak_dh * fueltypes_tech_share_yd[:, peak_day_nr, :]
            ##fuels_peak_dh[tech_fuel_type_int] += fuel_tech_peak_dh * fueltypes_tech_share_yd[peak_day_nr, :] #BEO
            fuels_peak_dh[tech_fuel_type_int] += fuel_tech_peak_dh * fueltypes_tech_share_yd #BEO

        return fuels_peak_dh

    def calc_fuel_tech_yh(self, enduse_fuel_tech, tech_stock, load_profiles, lookups, mode_constrained, nr_of_days):
        """Iterate fuels for each technology and assign shape yd and yh shape

        Arguments
        ----------
        enduse_fuel_tech : dict
            Fuel per technology in enduse
        tech_stock : object
            Technologies
        load_profiles : object
            Load profiles
        lookups : dict
            Fuel look-up table
        mode_constrained : bool
            Mode criteria
        nr_of_days : int
            Number of modelled days

        Return
        ------
        fuels_yh : array
            Fueltype storing hourly fuel for every fueltype (fueltype, nr_of_days, 24)
        """
        fuels_yh = np.zeros((lookups['fueltypes_nr'], nr_of_days, 24), dtype=float)

        if mode_constrained == True:
            fueltypes_tech_share_yh = np.zeros((lookups['fueltypes_nr']), dtype=float)

            # Assign full share to heat
            #fueltypes_tech_share_yh[lookups['fueltype']['heat']] = 1 BEO
            fueltypes_tech_share_yh['heat'] = 1

            for tech in self.enduse_techs:
                fuel_tech_yh = enduse_fuel_tech[tech] * load_profiles.get_lp(
                    self.enduse,
                    self.sector,
                    tech,
                    'shape_yh'
                    )
                fuels_yh += fueltypes_tech_share_yh[:, np.newaxis, np.newaxis] * fuel_tech_yh #SHARK
        else:
            for tech in self.enduse_techs:

                # Get fueltype of technology
                tech_fueltype_int = tech_stock.get_tech_attr(
                    self.enduse, tech, 'tech_fueltype_int')

                # Fuel distribution
                fuel_tech_yh = enduse_fuel_tech[tech] * load_profiles.get_lp(
                    self.enduse, self.sector, tech, 'shape_yh') #SHARK NEW

                # Get distribution per fueltype
                '''fueltypes_tech_share_yh = tech_stock.get_tech_attr(
                    self.enduse,
                    tech,
                    'fueltype_share_yh_all_h')
                '''
                ##fueltypes_tech_share_yh = np.zeros((lookups['fueltypes_nr']), dtype=float) #BELUGA
                ##fueltypes_tech_share_yh[tech_fueltype_int] = 1
                #fueltypes_tech_share_yh = 1

                # Get distribution of fuel for every day, calculate share of fuel, add to fuels
                ##fuels_yh += fueltypes_tech_share_yh[:, np.newaxis, np.newaxis] * fuel_tech_yh
                fuels_yh[tech_fueltype_int] += fuel_tech_yh #* fueltypes_tech_share_yh

        return fuels_yh

    def fuel_switch(self, installed_tech, sig_param_tech, tot_service_h_cy, service_tech, service_fueltype_tech_cy_p, service_fueltype_cy_p, fuel_switches, fuel_tech_p_by, curr_yr):
        """Calulation of service after considering fuel switch assumptions

        Arguments
        ----------
        installed_tech : dict
            Technologies installed
        sig_param_tech : dict
            Sigmoid diffusion parameters
        tot_service_h_cy : dict
            Total regional service for every hour for base year
        service_tech : dict
            Service for every fueltype and technology
        service_fueltype_tech_cy_p : dict
            Fraction of service per fueltype, technology for current year
        service_fueltype_cy_p : dict
            Fraction of service per fuyltpe in current year

        Returns
        -------
        service_tech_after_switch : dict
            Containing all service for each technology on a hourly basis

        Note
        ----
        - Based on assumptions about shares of fuels which are switched per enduse to specific
          technologies, the installed technologies are used to calculate the new service demand
          after switching fuel shares.

          TODO: MORE INFO
        """
        #logging.debug("... fuel_switch is implemented")
        service_tech_after_switch = copy.copy(service_tech)

        # Iterate all technologies which are installed in fuel switches
        for tech_installed in installed_tech[self.enduse]:

            # Read out sigmoid diffusion of service of this technology for the current year
            diffusion_cy = diffusion_technologies.sigmoid_function(
                curr_yr,
                sig_param_tech[self.enduse][tech_installed]['l_parameter'],
                sig_param_tech[self.enduse][tech_installed]['midpoint'],
                sig_param_tech[self.enduse][tech_installed]['steepness'])

            # Calculate increase in service based on diffusion of installed technology
            # (diff & total service== Todays demand) - already installed service

            #OLD
            ##service_tech_installed_cy = (diffusion_cy * tot_service_h_cy) - service_tech[tech_installed]
            service_tech_installed_cy = (diffusion_cy * tot_service_h_cy)

            # Assert if minus demand
            #assert np.sum((diffusion_cy * tot_service_h_cy) - service_tech[tech_installed]) >= 0

            # Get service for current year for technologies
            #service_tech_after_switch[tech_installed] += service_tech_installed_cy
            service_tech_after_switch[tech_installed] = service_tech_installed_cy #NEW

            # ------------
            # Remove fuel of replaced energy service demand proportinally to fuel shares in base year (of national country)
            # ------------
            tot_service_tech_instal_p = 0 # Total replaced service across different fueltypes
            fueltypes_replaced = [] # List with fueltypes where fuel is replaced

            # Iterate fuelswitches and read out the shares of fuel which is switched with the installed technology
            for fuelswitch in fuel_switches:
                # If the same technology is switched to across different fueltypes
                if fuelswitch['enduse'] == self.enduse:
                    if fuelswitch['technology_install'] == tech_installed:

                        # Add replaced fueltype
                        fueltypes_replaced.append(fuelswitch['enduse_fueltype_replace'])

                        # Share of service demand per fueltype * fraction of fuel switched
                        tot_service_tech_instal_p += service_fueltype_cy_p[fuelswitch['enduse_fueltype_replace']] * fuelswitch['share_fuel_consumption_switched']

            #logging.debug("replaced fueltypes: " + str(fueltypes_replaced))
            #logging.debug("Service demand which is switched with this technology: " + str(tot_service_tech_instal_p))

            # Iterate all fueltypes which are affected by the technology installed
            for fueltype_replace in fueltypes_replaced:

                # Get all technologies of the replaced fueltype
                technologies_replaced_fueltype = fuel_tech_p_by[fueltype_replace].keys()

                # Find fuel switch where this fueltype is replaced
                for fuelswitch in fuel_switches:
                    if fuelswitch['enduse'] == self.enduse and fuelswitch['technology_install'] == tech_installed and fuelswitch['enduse_fueltype_replace'] == fueltype_replace:

                        # Service reduced for this fueltype
                        # (service technology cy sigmoid diff *  % of heat demand within fueltype)
                        if tot_service_tech_instal_p == 0:
                            reduction_service_fueltype = 0
                        else:
                            # share of total service of fueltype * share of replaced fuel
                            service_fueltype_tech_cy_p_rel = np.divide(1.0, tot_service_tech_instal_p) * (service_fueltype_cy_p[fueltype_replace] * fuelswitch['share_fuel_consumption_switched'])

                            ##logging.debug("service_fueltype_tech_cy_p_rel -- : " + str(service_fueltype_tech_cy_p_rel))
                            reduction_service_fueltype = service_tech_installed_cy * service_fueltype_tech_cy_p_rel
                        break

                ##logging.debug("Reduction of additional service of technology in replaced fueltype: " + str(np.sum(reduction_service_fueltype)))

                # Iterate all technologies in within the fueltype and calculate reduction per technology
                for technology_replaced in technologies_replaced_fueltype:
                    ####logging.debug(" ")
                    #logging.debug("technology_replaced: " + str(technology_replaced))
                    # It needs to be calculated within each region the share how the fuel is distributed...
                    # Share of heat demand for technology in fueltype (share of heat demand within fueltype * reduction in servide demand)
                    service_demand_tech = service_fueltype_tech_cy_p[fueltype_replace][technology_replaced] * reduction_service_fueltype
                    ##logging.debug("service_demand_tech: " + str(np.sum(service_demand_tech)))

                    # -------
                    # Substract technology specific service
                    # -------
                    # Because in region the fuel distribution may be different because of different efficiencies, particularly for fueltypes,
                    # it may happen that the switched service is minus 0. If this is the case, assume that the service is zero.
                    if np.sum(service_tech_after_switch[technology_replaced] - service_demand_tech) < 0:

                        #sys.exit("ERROR: Service cant be minus") #TODO TODO TODO TODO
                        service_tech_after_switch[technology_replaced] = service_tech_after_switch[technology_replaced] * 0
                    else:
                        # Substract technology specific servide demand
                        service_tech_after_switch[technology_replaced] -= service_demand_tech
                        #logging.debug("B: " + str(np.sum(service_tech_after_switch[technology_replaced])))

                # Testing
                #assert np.testing.assert_almost_equal(np.sum(test_sum), np.sum(reduction_service_fueltype), decimal=4)

        return service_tech_after_switch

    def service_to_fuel(self, service_tech, tech_stock, lookups, mode_constrained, model_yeardays):
        """Convert yearly energy service to yearly fuel demand. For every
        technology the service is taken and converted
        to fuel based on efficiency of current year

        Inputs
        ------
        service_tech : dict
            Service per fueltype and technology
        tech_stock : object
            Technological stock
        lookups : dict
            look-up
        mode_constrained : bool
            Mode running criteria

        Note
        -----
        - The attribute 'fuel_new_y' is updated
        - Fuel = Energy service / efficiency
        """
        fuel_per_tech = {}
        enduse_fuels = np.zeros((lookups['fueltypes_nr']), dtype=float)

        if mode_constrained:
            fuel_fueltype_p = np.zeros((lookups['fueltypes_nr']), dtype=float)
            # Assign all to heat
            fuel_fueltype_p[lookups['fueltype']['heat']] = 1.0

            for tech, fuel_tech in service_tech.items():
                enduse_fuels += fuel_fueltype_p * np.sum(fuel_tech)

                #new
                fuel_tech[tech] = np.sum(fuel_tech)
            
        else:
            for tech, service in service_tech.items():
                eff_full_year = tech_stock.get_tech_attr(
                    self.enduse, tech, 'eff_cy')

                # If array anre more than one eff
                if isinstance(eff_full_year, np.ndarray):
                    if eff_full_year.shape[0] == 365:
                        eff_yh_selection = eff_full_year[[model_yeardays]]
                    else:
                        eff_yh_selection = eff_full_year

                    fuel_tech = np.divide(service, eff_yh_selection)
                else:
                    fuel_tech = service / eff_full_year

                _sum = np.sum(fuel_tech)
                fuel_per_tech[tech] = _sum #NEW JOIN

                #fueltype_share_yh_all_h = tech_stock.get_tech_attr(
                #    self.enduse, tech, 'fueltype_share_yh_all_h')
                tech_fuel_type_int = tech_stock.get_tech_attr(
                    self.enduse,
                    tech,
                    'tech_fueltype_int'
                    )
                # Multiply fuel of technology per fueltype with shape of yearl distrbution
                #enduse_fuels += fueltype_share_yh_all_h * np.sum(fuel_tech)
                enduse_fuels[tech_fuel_type_int] += _sum #BEO

        self.fuel_new_y = enduse_fuels

        return fuel_per_tech

    def service_to_fuel_per_tech(self, service_tech, tech_stock, mode_constrained, model_yeardays):
        """Calculate fraction of fuel per technology within fueltype
        considering current efficiencies.

        Arguments
        ----------
        service_tech : dict
            Assumptions of share of fuel of base year
        tech_stock : object
            Technology stock
        mode_constrained : bool
            Mode criteria

        Returns
        -------
        fuel_tech : dict
            Fuels per technology (the fueltype is given through technology)

        Note
        -----
        - Fuel = Energy service / efficiency
        """
        fuel_tech = {}

        if mode_constrained:
            for tech, service in service_tech.items():
                fuel_yh = service[[model_yeardays]]
                fuel_tech[tech] = np.sum(service)
        else:
            for tech, service in service_tech.items():
                # Convert service to fuel
                eff_full_year = tech_stock.get_tech_attr(self.enduse, tech, 'eff_cy')

                # If array anre more than one eff
                if isinstance(eff_full_year, np.ndarray):
                    if eff_full_year.shape[0] == 365: # efficiency is provided for full year
                        eff_yh_selection = eff_full_year[[model_yeardays]]
                    else:
                        eff_yh_selection = eff_full_year
                    fuel_yh = np.divide(service, eff_yh_selection)
                else:
                    #No array
                    fuel_yh = service / eff_full_year
                fuel_tech[tech] = np.sum(fuel_yh)

        return fuel_tech

    def apply_specific_change(self, assumptions, enduse_overall_change_ey, base_parameters, lookups):
        """Calculates fuel based on assumed overall enduse specific fuel consumption changes

        Arguments
        ----------
        assumptions : dict
            assumptions
        enduse_overall_change_ey : dict
            Assumption of overall change in end year

        base_parameters : dict
            Base simulation parameters

        Returns
        -------
        self.fuel_new_y - array
            Set attribute ``fuel_new_y``

        Note
        -----
        - Because for enduses where no technology stock is defined (and may
          consist of many different) technologies, a linear diffusion is
          suggested to best represent multiple sigmoid efficiency improvements
          of individual technologies.

        - The changes are assumed across all fueltypes.

        - Either a sigmoid standard diffusion or linear diffusion can be implemented.
          inear is suggested.
        """
        # Fuel consumption shares in base and end year
        percent_by = 1.0
        percent_ey = enduse_overall_change_ey[self.enduse]

        # Share of fuel consumption difference
        diff_fuel_consump = percent_ey - percent_by
        diffusion_choice = assumptions['other_enduse_mode_info']['diff_method']

        if diff_fuel_consump != 0: # If change in fuel consumption
            new_fuels = np.zeros((lookups['fueltypes_nr']), dtype=float)

            # Lineare diffusion up to cy
            if diffusion_choice == 'linear':
                lin_diff_factor = diffusion_technologies.linear_diff(
                    base_parameters['base_yr'],
                    base_parameters['curr_yr'],
                    percent_by,
                    percent_ey,
                    base_parameters['sim_period_yrs']
                )
                change_cy = lin_diff_factor

            # Sigmoid diffusion up to cy
            elif diffusion_choice == 'sigmoid':
                sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                    base_parameters['base_yr'],
                    base_parameters['curr_yr'],
                    base_parameters['end_yr'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_midpoint'],
                    assumptions['other_enduse_mode_info']['sigmoid']['sig_steeppness']
                    )
                change_cy = diff_fuel_consump * sig_diff_factor

            # Calculate new fuel consumption percentage
            new_fuels = self.fuel_new_y * change_cy

            self.fuel_new_y = new_fuels

    def apply_climate_change(self, cooling_factor_y, heating_factor_y, assumptions):
        """Change fuel demand for heat and cooling service depending on changes in
        HDD and CDD within a region (e.g. climate change induced)

        Paramters
        ---------
        cooling_factor_y : array
            Distribution of fuel within year to days (yd) (directly correlates with CDD)
        heating_factor_y : array
            Distribution of fuel within year to days (yd) (directly correlates with HDD)
        assumptions : dict
            Assumptions

        Return
        ------
        self.fuel_new_y - array
            Set attribute ``fuel_new_y``

        Note
        ----
        - `cooling_factor_y` and `heating_factor_y` are based on the sum
          over the year. Therefore it is assumed that fuel correlates
          directly with HDD or CDD.
        """
        if self.enduse in assumptions['enduse_space_heating']:
            self.fuel_new_y = self.fuel_new_y * heating_factor_y

        elif self.enduse in assumptions['enduse_space_cooling']:
            self.fuel_new_y = self.fuel_new_y * cooling_factor_y

        return

    def apply_smart_metering(self, assumptions, base_sim_param):
        """Calculate fuel savings depending on smart meter penetration

        Arguments
        ----------
        assumptions : dict
            assumptions
        base_sim_param : dict
            Base simulation parameters

        Returns
        -------
        self.fuel_new_y - array
            Set attribute ``fuel_new_y``. Fuels which are
            adapted according to smart meter penetration

        Note
        -----
        - The smart meter penetration is assumed with a sigmoid diffusion.

        - In the assumptions the maximum penetration and also the
          generally fuel savings for each enduse can be defined.
        """
        if self.enduse in assumptions['savings_smart_meter']:

            # Sigmoid diffusion up to current year
            sigm_factor = diffusion_technologies.sigmoid_diffusion(
                base_sim_param['base_yr'],
                base_sim_param['curr_yr'],
                base_sim_param['end_yr'],
                assumptions['smart_meter_diff_params']['sig_midpoint'],
                assumptions['smart_meter_diff_params']['sig_steeppness']
                )

            # Smart Meter penetration (percentage of people having smart meters)
            penetration_by = assumptions['smart_meter_p_by']
            penetration_cy = assumptions['smart_meter_p_by'] + (
                sigm_factor * (assumptions['smart_meter_p_ey'] - assumptions['smart_meter_p_by']))

            savings = assumptions['savings_smart_meter'][self.enduse]
            saved_fuel = self.fuel_new_y * (penetration_by - penetration_cy) * savings
            self.fuel_new_y = self.fuel_new_y - saved_fuel

            return

    def apply_scenario_drivers(self, dw_stock, region_name, data, reg_scen_drivers, base_sim_param):
        """The fuel data for every end use are multiplied with respective scenario driver

        Arguments
        ----------
        dw_stock : object
            Dwelling stock
        region_name : str
            Region name
        data : dict
            Data container
        reg_scen_drivers : dict
            Scenario drivers per enduse
        base_sim_param : dict
            Base simulation parameters

        Returns
        -------
        self.fuel_new_y - array
            Set attribute ``fuel_new_y``.

        Note
        -----
        - If no dwelling specific scenario driver is found, the identical fuel is returned.

          TODO
        """
        if reg_scen_drivers is None:
            reg_scen_drivers = {}

        base_yr = base_sim_param['base_yr']
        curr_yr = base_sim_param['curr_yr']

        new_fuels = np.copy(self.fuel_new_y)

        if not dw_stock:
            """Calculate non-dwelling related scenario drivers, if no dwelling stock
            Info: No dwelling stock is defined for this submodel
            """
            scenario_drivers = reg_scen_drivers[self.enduse]

            by_driver, cy_driver = 1, 1 #not 0

            for scenario_driver in scenario_drivers:

                # Get correct data depending on driver
                if scenario_driver == 'GVA':
                    by_driver_data = data['GVA'][base_yr][region_name]
                    cy_driver_data = data['GVA'][curr_yr][region_name]
                elif scenario_driver == 'population':
                    by_driver_data = data['population'][base_yr][region_name]
                    cy_driver_data = data['population'][curr_yr][region_name]
                #TODO :ADD OTHER ENDSES

                # Multiply drivers
                by_driver *= by_driver_data
                cy_driver *= cy_driver_data
            try:
                factor_driver = cy_driver / by_driver # FROZEN (as in chapter 3.1.2 EQ E-2)
            except ZeroDivisionError:
                factor_driver = 1

            new_fuels *= factor_driver

            self.fuel_new_y = new_fuels
        else:
            # Test if enduse has a dwelling related scenario driver
            if hasattr(dw_stock[region_name][base_yr], self.enduse) and curr_yr != base_yr:

                # Scenariodriver of dwelling stock base year and new stock
                by_driver = getattr(dw_stock[region_name][base_yr], self.enduse)
                cy_driver = getattr(dw_stock[region_name][curr_yr], self.enduse)

                # base year / current (checked) (as in chapter 3.1.2 EQ E-2)
                try:
                    factor_driver = cy_driver / by_driver # FROZEN
                except ZeroDivisionError:
                    factor_driver = 1

                new_fuels *= factor_driver

                self.fuel_new_y = new_fuels
            else:
                pass #enduse not define with scenario drivers
