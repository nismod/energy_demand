"""The technological stock for every simulation year"""
import numpy as np
import energy_demand.technological_stock_functions as tf
import energy_demand.main_functions as mf
# pylint: disable=I0011,C0321,C0301,C0103, C0325, R0902, R0913

# TODO: Create technology class

class Technology(object):

    def __init__(self, tech_name, data, data_ext, temp_cy, year):
        """Contructor of technology
        # NTH: If regional diffusion, load into region and tehn into tech stock
        """
        self.curr_yr = year
        self.tech_name = tech_name
        self.fuel_type = data['assumptions']['technologies'][self.tech_name]['fuel_type'] #TOD: USE IT
        self.eff_by = data['assumptions']['technologies'][self.tech_name]['eff_by']
        self.eff_ey = data['assumptions']['technologies'][self.tech_name]['eff_ey']
        self.eff_achieved = data['assumptions']['technologies'][self.tech_name]['eff_achieved']
        self.diff_method = data['assumptions']['technologies'][self.tech_name]['diff_method']
        self.market_entry = float(data['assumptions']['technologies'][self.tech_name]['market_entry'])

        # Calculate efficiency in current year
        self.eff_cy = self.calc_efficiency_cy(data, data_ext, temp_cy, self.curr_yr, self.eff_by, self.eff_ey, self.diff_method, self.eff_achieved)
        #print("EFFICIENCY CY: " + str(tech_name) + str(np.average(self.eff_cy)))

    # Calculate efficiency in current year
    def calc_efficiency_cy(self, data, data_ext, temp_cy, curr_yr, eff_by, eff_ey, diff_method, eff_achieved):
        """Calculate efficiency of current year based on efficiency assumptions and achieved efficiency
        # per default linear diffusion assumed
        FUNCTION
        """
        # NEW
        efficiency_diff = eff_ey - eff_by

        if diff_method == 'linear':
            theor_max_eff = mf.linear_diff(data_ext['glob_var']['base_yr'], curr_yr, eff_by, eff_ey, len(data_ext['glob_var']['sim_period'])) # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
            #TODO: Check if only factor or already absolute with eff_by Nd eff_ey
        if diff_method == 'sigmoid':
            theor_max_eff = mf.sigmoid_diffusion(data_ext['glob_var']['base_yr'], curr_yr, data_ext['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        #print("theor_max_eff: " + str(efficiency_diff) + str("  ") + str(theor_max_eff) + str("  ") + str(data_ext['glob_var']['base_yr']) + str("   ") + str(data_ext['glob_var']['curr_yr']))

        # Consider actual achived efficiency
        actual_eff = theor_max_eff * eff_achieved

        # Differencey in effuciency change
        efficiency_change = actual_eff * efficiency_diff

        # Actual efficiency potential
        eff_cy = eff_by + efficiency_change

        # Temperature dependent efficiency
        if self.tech_name in ['heat_pump']:
            eff_cy_hourly = mf.get_heatpump_eff(
                temp_cy,
                data['assumptions']['heat_pump_slope_assumption'], # Constant assumption of slope (linear assumption, even thoug not linear in realisty): -0.08
                eff_cy,
                data['assumptions']['t_base_heating']['base_yr']
            )
        else:
            # Non temperature dependent efficiencies
            eff_cy_hourly = mf.create_efficiency_array(eff_cy) # Create efficiency for every hour

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
        #self.temp_cy = temp_cy

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
            #print("carte obje" + str(technology_name))
            #print(technology_object.__dict__)

        # Execute function to add all parameters of all technologies which define efficienes to technological stock
        ###self.create_iteration_efficiency(data, data_ext)

        # Add Heat pump to technological stock (two efficiency parameters) (Efficiency for every hour and not only one value over year)
        #self.create_hp_efficiency(data, temp_cy)

        # Calculate share of technologies within each fueltype (e.g. fraction of households with each technology)
        self.tech_frac_by = data['assumptions']['tech_enduse_by'] #base year
        self.tech_frac_ey = data['assumptions']['tech_enduse_ey'] #end year
        self.tech_frac_cy = self.get_sigmoid_tech_diff(data, data_ext) #current year

    def get_technology_attribute(self, technology, attribute_to_get):
        """Read an attrribute from a technology in the technology stock
        """
        tech_object = getattr(self, str(technology))
        tech_attribute = getattr(tech_object, str(attribute_to_get))

        return tech_attribute

    def create_hp_efficiency(self, data, temp_cy):
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

    def create_iteration_efficiency(self, data, data_ext):
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
                cy_eff = mf.create_efficiency_array(cy_eff)
            else:
                cy_eff = eff_by - (achieved_eff * (abs(theor_max_eff) - abs(eff_by))) # Efficiency gain
                cy_eff = mf.create_efficiency_array(cy_eff)

            ResidTechStock.__setattr__(self, technology_param, cy_eff)

    def get_sigmoid_tech_diff(self, data, data_ext):
        """Calculate change in fuel demand based on sigmoid diffusion of fraction of technologies for each enduse

        I. With help of assumptions on the fraction of technologies for each
        enduse and fueltype for the `base_yr` and `end_yr` the
        fraction of technologies for the `curr_yr` is calculated.

        II.The change in fuel is calculated depending on the relationship
        `sig_frac_tech_change`.

        Returns
        -------
        tech_frac_cy : dict
            A nested.

        Example
        -------

        Notes
        -----
        In the process of calculating the differences in the fraction
        the individual technologies are converted in to IDs in order
        to create arrays. In the end, the technology IDs are replaced
        with strings for each technology.
        """
        tech_frac_cy = {}

        # Sigmoid efficiency which is achieved up to cy (so far for all technologies)
        sig_frac_tech_change = mf.sigmoid_diffusion(data_ext['glob_var']['base_yr'], data_ext['glob_var']['curr_yr'], data_ext['glob_var']['end_yr'], data['assumptions']['sig_midpoint'], data['assumptions']['sig_steeppness'])

        for enduse in self.tech_frac_by:
            tech_frac_cy[enduse] = {}

            # Convert to array and replace fuels with strings
            by_enduse_array = mf.convert_to_tech_array(self.tech_frac_by[enduse], data['tech_lu'])  # Base year fraction of technolgies for the enduse
            ey_enduse_array = mf.convert_to_tech_array(self.tech_frac_ey[enduse], data['tech_lu'])  # End year fraction of technolgies for the enduse

            # If no technolgies are in this enduse
            if ey_enduse_array == []:
                for fueltype in range(len(data['fuel_type_lu'])):
                    tech_frac_cy[enduse][fueltype] = {}
                continue # Go to next enduse

            # iterate fuel type and the technologies
            for fueltype in range(len(data['fuel_type_lu'])):

                # No technologies are within this fuel type
                if by_enduse_array[fueltype] == []:
                    tech_frac_cy[enduse][fueltype] = {}
                    continue # Go to next fueltype

                diff = ey_enduse_array[fueltype][:, 1] - by_enduse_array[fueltype][:, 1] # Calculate difference in share of technologies between end and base year
                diff_fract_sig = diff * sig_frac_tech_change # Multiply overall difference with achieved efficiency
                diff_cy = by_enduse_array[fueltype][:, 1] + diff_fract_sig # Current year fraction (frac of base year plus changes up to current year)

                # Convert the arrays back to dictionary and replace strings of technologies with str
                technologey_of_enduse = self.tech_frac_by[enduse][fueltype].keys()
                tech_frac_cy[enduse][fueltype] = dict(zip(technologey_of_enduse, diff_cy.flatten()))

        return tech_frac_cy
