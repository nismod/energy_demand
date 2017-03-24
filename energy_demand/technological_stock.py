"""The technological stock for every simulation year"""
import technological_stock_functions as tf
import energy_demand.main_functions as mf

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model. For every region,
    a Region Object needs to be generated

    Parameters
    ----------
    data : dict
        tbd
    assumptions : dict
        tbd
    data_ext : dict
        tbd
    current_year : int
        Current year

    TODO: Improve and replace glob_var
    """
    def __init__(self, data, data_ext, current_year):
        """Constructor of technologies for residential sector"""
        self.base_year = data_ext['glob_var']['base_year']
        self.end_year = data_ext['glob_var']['end_year']
        self.current_year = current_year #data_ext['glob_var']['current_year']
        self.assumptions = data['assumptions']
        self.tech_lu = data['tech_lu']

        # Execute function to add all technological efficiencies as self argument
        self.crate_iteration_efficiency()

        # get share of technologies of base_year
        self.tech_frac_by_assumptions = data['assumptions']['technologies_enduse_by']
        self.tech_frac_ey_assumptions = data['assumptions']['technologies_enduse_ey']

        #self.tech_frac_eyy = data['assumptions']['technologies_enduse_by']
        # Get share of technology of current year #TODO
        self.tech_frac = self.get_sigmoid_tech_diff()

    def crate_iteration_efficiency(self):
        """Iterate technologes in 'base_year' dict and add to technology_stock

        The efficiency of each technology is added as `self` attribute.
        Based on assumptions of theoretical maximum efficiency gains of
        each technology and assumptions on the actual achieved efficiency, 
        the efficiency of the current year is calculated based 
        on a linear diffusion.

        Example
        -------
        Technology X is projected to have maximum potential efficiency increase
        from 0.5 to a 1.00 efficiency. If however, the acutal efficiency gain
        is only 50%, then after the simulation, an efficiency of 0.75 is reached
        """
        technology_list = self.assumptions['eff_by']

        for technology in technology_list:
            eff_by = self.assumptions['eff_by'][technology]
            eff_ey = self.assumptions['eff_ey'][technology]
            sim_years = self.end_year - self.base_year

            # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated TODO: Ev. round
            theor_max_eff = tf.lineardiffusion(self.base_year, self.current_year, eff_by, eff_ey, sim_years)

            # Get assmuption how much of efficiency potential is reaped
            achieved_eff = self.assumptions['eff_achieved'][technology]

            # Actual efficiency potential
            #self.technologies[technology] = achieved_eff * theor_max_eff # Efficiency gain assumption achieved * theoretically maximum achieveable efficiency gain
            value_for_new_attribute = achieved_eff * theor_max_eff # Efficiency gain assumption achieved * theoretically maximum achieveable efficiency gain

            ResidTechStock.__setattr__(self, technology, value_for_new_attribute)

    def get_sigmoid_tech_diff(self):
        """Calculate change in fuels based on sigmoid diffusion of fraction of technologies

        With help of assumptions on the fraction of technologies for each
        enduse and fueltype for the `base_year` and `end_year` the
        fraction of technologies for the `current_year` is calculated.

        Also the change in fuel is calculated depending on the relationship
        `sigmoid_frac_tech_change`.

        Notes
        -----
        In the process of calculating the differences in the fraction
        the individual technologies are converted in to IDs in order
        to create arrays. In the end, the technology IDs are replaced
        with strings for each technology.

        """
        tech_frac_by = self.tech_frac_by_assumptions
        tech_frac_ey = self.tech_frac_ey_assumptions
        tech_frac_cy = {}

        # Sigmoid efficiency for all technologies (TODO: TECHNOLOGY SPECIFIC DIFFUSION)
        sigmoid_frac_tech_change = tf.sigmoidefficiency(self.base_year, self.current_year, self.end_year)

        for enduse in tech_frac_by:
            tech_frac_cy[enduse] = {}

            by_enduse_array = mf.convert_to_array_technologies(tech_frac_by[enduse], self.tech_lu)  # Base year fraction of technolgies for the enduse
            ey_enduse_array = mf.convert_to_array_technologies(tech_frac_ey[enduse], self.tech_lu)  # End year fraction of technolgies for the enduse

            nr_of_fueltypes = len(by_enduse_array)

            # If no technolgies are in this enduse
            if ey_enduse_array == []:
                for fueltype in range(nr_of_fueltypes):
                    tech_frac_cy[enduse][fueltype] = {}
                continue # Go to next enduse

            # iterate fuel type and the technologies in iter
            for fueltype in range(nr_of_fueltypes):

                # No technologies are within this fuel type
                if by_enduse_array[fueltype] == []:
                    tech_frac_cy[enduse][fueltype] = {}
                    continue # Go to next fueltype

                # calc fuel diff (the ID of technology vanishes)
                diff = ey_enduse_array[fueltype] - by_enduse_array[fueltype]

                # Multiply fraction with fraction_technologies and replace technology_IDs
                diff_fract_sigmoid = diff * sigmoid_frac_tech_change

                # Current year fraction (frac of base year plus changes up to current year)
                diff_cy = by_enduse_array[fueltype][:, 1] + diff_fract_sigmoid[:, 1]

                # Convert the arrays back to dictionary and replace IDs of technologies with strings
                technologey_of_enduse = tech_frac_by[enduse][fueltype].keys() # String name of technologies of enduse and fueltype
                tech_frac_cy[enduse][fueltype] = dict(zip(technologey_of_enduse, diff_cy.flatten()))

        return tech_frac_cy
