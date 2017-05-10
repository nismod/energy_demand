"""The technological stock for every simulation year"""
import numpy as np
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913

class Technology(object):
    """Technology class
    """
    def __init__(self, tech_name, data, data_ext, temp_cy, year):
        """Contructor of technology
        # NTH: If regional diffusion, load into region and tehn into tech stock
        """
        self.curr_yr = year
        self.tech_name = tech_name
        self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type']
        self.eff_by = mf.const_eff_y_to_h(data['assumptions']['technologies'][self.tech_name]['eff_by'])
        self.eff_ey = mf.const_eff_y_to_h(data['assumptions']['technologies'][self.tech_name]['eff_ey'])
        self.eff_achieved_factor = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # Calculate efficiency in current year
        self.eff_cy = self.calc_efficiency_cy(data, data_ext, temp_cy, self.curr_yr, self.eff_by, self.eff_ey, self.diff_method, self.eff_achieved_factor)

    # Calculate efficiency in current year
    def calc_efficiency_cy(self, data, data_ext, temp_cy, curr_yr, eff_by, eff_ey, diff_method, eff_achieved):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency
        # per default linear diffusion assumed
        FUNCTION
        """
        efficiency_diff = eff_ey - eff_by

        if diff_method == 'linear':
            theor_max_eff = mf.linear_diff(data_ext['glob_var']['base_yr'], curr_yr, eff_by, eff_ey, len(data_ext['glob_var']['sim_period'])) # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
        if diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data_ext['glob_var']['base_yr'], curr_yr, data_ext['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        #print("theor_max_eff: " + str(efficiency_diff) + str("  ") + str(theor_max_eff) + str("  ") + str(data_ext['glob_var']['base_yr']) + str("   ") + str(data_ext['glob_var']['curr_yr']))

        # Consider actual achived efficiency
        actual_eff = theor_max_eff * eff_achieved

        # Differencey in efficiency change
        efficiency_change = actual_eff * efficiency_diff

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        # Temperature dependent efficiency #TODO: READ IN FROME ASSUMPTIONS 
        if self.tech_name in ['heat_pump']:
            eff_cy_hourly = mf.get_heatpump_eff(
                temp_cy,
                data['assumptions']['heat_pump_slope_assumption'], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                eff_cy,
                data['assumptions']['t_base_heating']['base_yr']
            )
        else:
            # Non temperature dependent efficiencies
            eff_cy_hourly = eff_cy # # Create efficiency for every hour

        return eff_cy_hourly

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model. For every HOUR IN EVERY REGION, #TODO?
    a Region Object needs to be generated

    Technology stock for every enduse

    Parameters
    ----------
    data : dict
        tbd
    assumptions : dict
        tbd
    data_ext : dict
        tbd
    curr_yr : int
        Current year
    """
    def __init__(self, data, data_ext, temp_cy, year):
        """Constructor of technologies for residential sector
        """

        # Crate all technologies and add as attribute (NEW)
        for technology_name in data['tech_lu']:

            # Technology object
            technology_object = Technology(
                technology_name,
                data,
                data_ext,
                temp_cy,
                year
            )

            # Set technology object as attribute
            ResidTechStock.__setattr__(
                self,
                technology_name,
                technology_object
            )
            print("carte obje  " + str(technology_name))
            print(technology_object.__dict__)

    def get_technology_attribute(self, technology, attribute_to_get):
        """Read an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(technology))
        tech_attribute = getattr(tech_object, str(attribute_to_get))

        return tech_attribute

    '''def create_hp_efficiency(self, data, temp_cy):
        """Calculate efficiency of heat pumps

        Because the heat pump efficiency is different every hour depending on the temperature,
        the efficiency needs to be calculated differently.

        Note
        ----
        The attributes self.heat_pump_m and self.heat_pump_b are created in self.create_iteration_efficiency()
        and reflect current year efficiency parameters for the heat pump technology.
        """
        heat_pump_slope_assumption = data['assumptions']['heat_pump_slope_assumption']

        ResidTechStock.__setattr__(
            self,
            'heat_pump',
            mf.get_heatpump_eff(
                temp_cy,
                heat_pump_slope_assumption, #self.heat_pump_m[0][0], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                self.heat_pump_b[0][0],
                data['assumptions']['t_base_heating']['base_yr']
                )
        )
    '''

    '''def create_iteration_efficiency(self, data, data_ext):
        """Iterate technologies of each enduse in 'base_yr' and add to technology_stock (linear diffusion)

        The efficiency of each technology is added as `self` attribute.
        Based on assumptions of theoretical maximum efficiency gains of
        each technology and assumptions on the actual achieved efficiency,
        the efficiency of the current year is calculated based
        on a linear diffusion.

        Returns
        -------
        Sets attributes with efficiency values for the current year

        Example
        -------
        Technology X is projected to have maximum potential efficiency increase
        from 0.5 to a 1.00 efficiency. If however, the acutal efficiency gain
        is only 50%, then after the simulation, an efficiency of 0.75 is reached

        #TODO: Assumption of lineare efficiency improvement
        """
        # Take Efficiency assumptions and not technology list because some technologies have more than one efficiency assumption
        technology_eff_assumptions = data['assumptions']['eff_by']

        # TODO: Alternatively iterate technology

        for technology_param in technology_eff_assumptions:
            eff_by = data['assumptions']['eff_by'][technology_param]
            eff_ey = data['assumptions']['eff_ey'][technology_param]

            # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
            theor_max_eff = mf.linear_diff(data_ext['glob_var']['base_yr'], data_ext['glob_var']['curr_yr'], eff_by, eff_ey, len(data_ext['glob_var']['sim_period']))

            # Get assmuption how much of efficiency potential is reaped
            achieved_eff = data['assumptions']['eff_achieved_resid'][technology_param]

            # Actual efficiency potential #TODO: Check if minus or plus number...TODO
            if eff_by >= 0:
                cy_eff = eff_by + (achieved_eff * (abs(theor_max_eff) - eff_by)) # Efficiency gain assumption achieved * theoretically maximum achieveable efficiency gain #abs is introduced because if minus value otherwie would become plus
                cy_eff = mf.const_eff_y_to_h(cy_eff)
            else:
                cy_eff = eff_by - (achieved_eff * (abs(theor_max_eff) - abs(eff_by))) # Efficiency gain
                cy_eff = mf.const_eff_y_to_h(cy_eff)

            ResidTechStock.__setattr__(self, technology_param, cy_eff)
        
    '''
