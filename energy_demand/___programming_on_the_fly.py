import numpy as np
from pprint import pprint
'''
# fuel = [
fuels = np.array((len(fueltypes), len(enduses)))



# Efficiencis of technologies
tech_charac = {# Technology description
               'tech_A': {'eff_by': 0.8,
                          'eff_ey': 0.9,
                          'fueltype': 0
                          },
               # Technology description
               'tech_B': {'eff_by': 0.8,
                          'eff_ey': 0.9,
                          'fueltype': 1
                          }
               }
pprint(tech_charac)

# Want to replace certaing percentage of fuel_end_use
new_end_use = old_end_use_fuel * share_to_replace * (eff_old/eff_new)

# List all enduces
all_end_uses = { #Heating
                'heating_gas': {'fuel_demand_by': data, 'share_to_replace_until_ey': 0.2, 'replacement_tech:' {'techA', 'techB'...}},
                'heating_oil': {'fuel_demand_by': data, 'share_to_replace_until_ey': 0.2}


                 } # Multiply existing enduses with all fuel types


# All 
tech_distr_by = {'heating_gas': {'tech_A': 1.0
                                },
                 'heating_oil': {'tech_B': 1.0
                                }
                }

tech_distr_ey = {'heating_gas': {'tech_A': 0.5,
                                 'tech_B': 0.5
                                },
                'heating_oil': {'tech_A': 1.0,
                                'tech_B': 0
                                }
                }

def get_new_energy_demand():
    fuel_diff = np.empty((len(fueltype), len(end_uses))


tech_stock_cy = {'tech_A': {'eff': get_efficiencies(tech_charac['tech_A'], self.year),
                           'share': get_share(self.year), 
                           'SD':  get_share(self.year) 
                           }
                }

# Iterate all enduse objects to get total new fuel demand
new_end_use = fuel_demand_by * fraction_to_replace * (eff_old/eff_new)
class EndUse(object):
    """Object for every end_use_fuel_type (total number = end_use_cat * fuel_types"""

    def __init__(self, sim_y):
        self.sim_y_by = sim_y_by
        self.fuel_demand_by = fuel_demand_by
        self.tech_efficiencies = get_cy_tech_efficiencies()
        self.fraction_to_replace = get_load_(sigmoid) # Calc how much of a total percentage needs to be replaced in sy
        self.fuel_type_technology_to_replace = fuel_type
        self.fuel_type_new_technolog = fuel_type


        # Technology distribution base year
        self.distr_by = distr_by_by # How fuel demand is generated with which tenology

        # Technology distribution end year
        self.distr_ey = calc_distr_ey(assumptions) # Contaings all new technologies which are used for eplacement
        ...

        self.OUT_DIFF_ENERGY_ARRAY = OUT_DIFF_ENERGY_ARRAY() # Array containing how much plus and minus of each fueltype

        

    def get_gas_fuel_demand(self.ED_gas_by):
        

        return


#-------------------------

tech_eff_sim_period = {2016: {'tech_A': effXY }...(oder object)



# TODO:
- Write functions which allow to easily replace assumptions in frac_replacement_assumptions 
(e.g. to replace the fraction of demand for all end_use)
def easy_func_to_replace_assumptions():
    # iterate demans
    for i in a.keys():
            # iterate end_uses
            for fueltype in a[i]:
                a[i][fueltype]['fract_replace'] = 39
                a[i][fueltype]['replace_tech'] = 'Tech_XY'
    pass

frac_replacement_assumptions = {'end_use_heating': {'fuel_type_A': {'fract_replace': 0.2, 'exist_tech': 'tech_A', 'replace_tech': 'tech_B'},
                                                    'fuel_type_B': {'fract_replace': 0.2, 'replace_tech': 'tech_B'},
                                                    'fuel_type_C': {'fract_replace': 0.2, 'replace_tech': 'tech_B'}
                                                   }
                               }

'''
#------------------------- 
#NEUER ANLAUF
#-------------------------
'''new_end_use = fuel_demand_by * fraction_to_replace * (eff_old/eff_new)
class EndUse():
    """Object for every end_use (all fuels one object)
    This is however only hearly demand.BaseException

    Every region has then an object
    """

    def __init__(self, end_use, sim_y, fuel_data, tech_eff_sim_period):
        self.end_use = str(end_use)             # Name of end use
        self.sim_y = sim_y                      # Simulation year
        self.fuels_by = get_fuels_by(fuel_data) # Array with all fuels for a given end-use.
        self.technology_efficiencies = tech_eff_sim_period[self.sim_y]) # Get all efficienceies of current year
        self.frac_to_replace = frac_replacements[self.end_use] # Read in fractions to replace

        # Fuel after eff & switches
        self.fuel_demand_sy = calc_new_fuel_demand_sy(self.fuels_by, self.frac_to_replace, self.technology_efficiencies)

        # Correct fuel after building stock
        self.fuel_after_build_sc = fuel_demand_sy * scenario_driver['end_use']

        # Convert yearly to hourly
        # yearly shape, hourly shape....
        #

    # Functions of EndUse
    def get_fuels_by(self.fuel_data):
        # load all fule data for all types of base year
        #np.array((len(fueltype, 0))
        pass

    # Functions to write
    # sum all fuels
#endUses_orig = ["Heating", "Cooking"]
'''
fuels = {"Oil": 0, "Gas": 1}

fuel_array = np.zeros((len(fuels), 1)) #Yearly fuel data

endUses_orig = {"Heating": "Heating", 
                "Cooking": "Cooking"}
fueldata_orig = {'Bern': {"Heating": fuel_array, "Cooking": fuel_array}}


endUses_orig = {"Heating": "Heating", "Cooking": "Cooking"}

class Region(object):
    """ Class of region """

    # Constructor (initialise class)
    def __init__(self, reg_id):
        self.reg_id = reg_id                    # Name/ID of region
        self.fueldata_reg = fueldata_orig[reg_id] # Fuel array of region

        #self.year = sim_year
        #self.pop = pop_by
        #self.floor_area = floor_area
        #self.SHAPES_ASSUMPTIONS


        # Functions in constructor
        self.create_end_use_objects(endUses_orig, self.fueldata_reg)     # Add end uses and fuel to region


    def create_end_use_objects(self, endUses_orig, fueldata_reg):
        """ Initialises all defined end uses. Adds an object  for each end use to the Region class"""
        
        a = {}
        for i in endUses_orig:
            a[i] = EndUse_Class(i, self.fueldata_reg[i])
        self.end_uses = a

        # Creat self objects {'key': Value}
        for i in self.end_uses:
            vars(self).update(self.end_uses) 

    def sum_all_appliances():
        '''Summen all appliances'''
        pass

    '''def create_endUse_object(self):
        """Function to generate all end use objects"""
        endUsesStore = []
        print(self.end_uses)
        for i in self.end_uses:
            #endUsesStore.append(EndUse_Class(i, self.fueldata[i]))
            EndUse_Class(i, self.fueldata[i])
            #EndUse_Class(i, self.fueldata[i])

        return endUsesStore
    '''



class EndUse_Class(object):
    def __init__(self, enduse_name, fuel_data_reg):
        self.enduse_name = enduse_name
        self.fuel_data_reg = fuel_data_reg


        
a = Region("Bern")
print(a.Heating.__dict__)
# Worked
'''
endUses = {"Heating": "Heating", "Cooking": "Cooking"}
fueldata = {'Bern': {"Heating": 100, "Cooking": 300}}
        
      for i in endUses:
            vars(self).update(self.end_uses) # create 


'''























'''
class Region(object):
    """ Class of region """

    def __init__(self, reg_id):
        self.reg_id = reg_id
        self.end_uses = endUses # load end_uses external
        self.fueldata = fueldata[reg_id] # load fuels external
        #print(self.end_uses)
        self.end_uses_all = self.create_endUse_object() # call function within class (Initiase all end uses)
    
   
    class EndUse_Class:
        def __init__(self, enduse_name, fuel_data_reg):
            self.enduse_name = enduse_name
            self.fuel_data_reg = fuel_data_reg

            # Initiate enduses
            #for i in endUses:
            #
            #    print("i: " + str(i))
            #    self.i = fueltype[str(i)]
   
    def create_endUse_object(self):
        """Function to generate all end use objects"""
        #endUsesStore = []
        for i in self.end_uses:
            self.EndUse_Class(i, self.fueldata[i])
        return
            #endUsesStore.append(self.EndUse_Class(i, self.fueldata[i]))
        #return endUsesStore
    #endUsesStore = create_endUse_object(self)
'''