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
    data_ext : dict
        tbd

    TODO: Improve and replace glob_var
    """
    def __init__(self, data, assumptions, data_ext, current_year):
        """Constructor of technologies for residential sector"""
        self.base_year = data_ext['glob_var']['base_year']
        self.end_year = data_ext['glob_var']['end_year']
        self.current_year = current_year #data_ext['glob_var']['current_year']
        self.assumptions = assumptions
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
        """Iterate technology list base yeare and add to technology_stock

        The efficiency of each technology is added as `self` Attribute
        Based on assumptions of theoretical maximum efficiency gaing of
        each technology and the actual achieved efficiency, the efficiency
        of the current year is calculated based on a linear diffusion

        Example
        -------
        Technology X is projected to have maximum potential efficiency increase
        from 0.5 to a 1.00 efficiency. If however, the acutal efficiency gain
        is only 50%, then after the simulation, an efficiency of 0.75 is reached
        """

        technology_list = self.assumptions['eff_by']
        self.technologies = {}

        for technology in technology_list:

            eff_by = self.assumptions['eff_by'][technology]
            eff_ey = self.assumptions['eff_ey'][technology]
            sim_years = self.end_year - self.base_year

            # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated TODO: Ev. round
            theor_max_eff = tf.lineardiffusion(self.base_year, self.current_year, eff_by, eff_ey, sim_years)

            # Get assmuption how much of efficiency potential is reaped
            achieved_eff = self.assumptions['eff_achieved'][technology]

            # Actual efficiency potential
            self.technologies[technology] = achieved_eff * theor_max_eff # Efficiency gain assumption achieved * theoretically maximum achieveable efficiency gain

        for _ in self.technologies:
            vars(self).update(self.technologies) # Creat self objects {'key': Value}

    def get_sigmoid_tech_diff(self):
        """ Get distribution of technologies for current year. Use sigmoid diffusion

        :convert diwth with technological fractions to array

        """
        tech_frac_by = self.tech_frac_by_assumptions
        tech_frac_ey = self.tech_frac_ey_assumptions

        tech_frac_cy = {}

        # Sigmoid efficiency for all technologies (TODO: TECHNOLOGY SPECIFIC DIFFUSION)
        sigmoid_fraction_technologies_change = tf.sigmoidefficiency(self.base_year, self.current_year, self.end_year)
        print("sigmoid_fraction_technologies_change: " + str(sigmoid_fraction_technologies_change))

        for enduse in tech_frac_by:
            print("Enduse---------------------------" + str(enduse))
            print(tech_frac_by[enduse])
            tech_frac_cy[enduse] = {}

            # Base year fraction
            by_enduse_array = mf.convert_to_array_TECHNOLOGES(tech_frac_by[enduse], self.tech_lu)
            print("by_enduse_array: " + str(by_enduse_array))

            # End year fraction
            ey_enduse_array = mf.convert_to_array_TECHNOLOGES(tech_frac_ey[enduse], self.tech_lu)
            print("ey_enduse_array: " + str(ey_enduse_array))

            nr_of_fueltypes = len(by_enduse_array)



            if ey_enduse_array == []:
                for fueltype in range(nr_of_fueltypes):
                    tech_frac_cy[enduse][fueltype] = {}
                print("Empty, no technologies in this enduse" + str(tech_frac_cy[enduse])) 
                continue

            # iterate fuel type and the technologies in iter
            for fueltype in range(nr_of_fueltypes):
                print("FUELTYE ---------" + str(fueltype))

                if by_enduse_array[fueltype] == []:
                    print("No technologes in this fueltype")
                    tech_frac_cy[enduse][fueltype] = {}
                    continue

                # Technologes of enduse and fueltype
                technologey_of_enduse = tech_frac_by[enduse][fueltype].keys()

                print(by_enduse_array[fueltype])
                print(by_enduse_array[fueltype])
                print(ey_enduse_array[fueltype])
                diff_fraction = ey_enduse_array[fueltype] - by_enduse_array[fueltype] # calc fuel diff (the ID of technology vanishes)

                print("adler")
                print(diff_fraction.shape)
                print(diff_fraction)
                # Multiply fraction with fraction_technologies and replace technology_IDs
                diff_fraction_sigmoid = diff_fraction * sigmoid_fraction_technologies_change
                print("diff_fraction_cy: " + str(diff_fraction_sigmoid))
                print(diff_fraction_sigmoid.shape)

                # Current year fraction (frac of base year plus changes up to current year)
                diff_fraction_cy = by_enduse_array[fueltype][:,1] + diff_fraction_sigmoid[:,1]
                print(diff_fraction_cy)
                print("---")
                print(diff_fraction_cy.flatten())
                print(dict(enumerate(diff_fraction_cy)))
                print(dict(zip(technologey_of_enduse, diff_fraction_cy.flatten()))) #key, values
                print("ooo")

                tech_frac_cy[enduse][fueltype] = dict(zip(technologey_of_enduse, diff_fraction_cy.flatten()))
        return tech_frac_cy
