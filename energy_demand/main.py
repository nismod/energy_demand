"""Main file containing the energy demand model main function
#
# Description: Energy Demand Model - Run one year
# Authors: Sven Eggimann, ...
#
# Abbreviations:
# -------------
# bd = Base demand
# by = Base year
# p  = Percent
# e  = electricitiy
# g  = gas
# lu = look up
# h = hour
# d = day

- Read out individal load shapes
- HEating Degree DAys
- efficiencies
- assumptions
- Overall total for every region...own class?


Down the line
- make sure that if a fuel type is added this correspoends to the fuel dict
# The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6

import sys
import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
import energy_demand.technological_stock as ts
import energy_demand.residential_model as rm
import energy_demand.plot_functions as pf
print("Start Energy Demand Model with python version: " + str(sys.version))

def energy_demand_model(data, data_ext):
    """Main function of energy demand model to calculate yearly demand

    This function is executed in the wrapper.

    Parameters
    ----------
    data : dict
        Contains all data not provided externally
    data_ext : dict
        All data provided externally

    Returns
    -------
    result_dict : dict
        A nested dictionary containing all data for energy supply model with timesteps for every hour in a year.
        [fuel_type : region : timestep]

    """
    # Initialisation
    
    # SCENARIO UNCERTAINTY
    # TODO: Implement wheater generator (multiply fuel with different scenarios)
    #data = wheater_generator_(data) # Read in CWV data and calcul difference between average and min and max of year 2015

    # --------------------------
    # Residential model
    # --------------------------
    all_regions_resid = rm.residential_model_main_function(data, data_ext)

    # --------------------------
    # Service Model
    # --------------------------

    # --------------------------
    # Industry Model
    # --------------------------

    # --------------------------
    # Transportation Model
    # --------------------------





    # Convert to dict for energy_supply_model
    result_dict = mf.convert_out_format_es(data, data_ext, all_regions_resid)

    # --- Write to csv and YAML
    mf.write_to_csv_will(data, result_dict, data['reg_lu'], False)

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[1])))
    print("FINAL timesteps: " + str(len(result_dict[1][0])))
    print("Finished energy demand model")

    # Plot REgion 0 for half a year
    #pf.plot_x_days(result_dict[2], 0, 2)
    return result_dict

# Run
if __name__ == "__main__":

    # -------------------------------------------------------------------
    # Execute only once befure executing energy demand module for a year
    # ------------------------------------------------------------------_
    # Wheater generater (change base_demand data)

    # External data provided from wrapper
    data_external = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001},
                                    2016: {0: 3001001, 1: 5301001, 2: 53001001}
                                   },

                     'glob_var': {'base_year': 2015,
                                  'current_year': 2016,
                                  'end_year': 2020
                                 },

                     'fuel_price': {2015: {0: 10.0, 1: 10.0, 2: 10.0, 3: 10.0, 4: 10.0, 5: 10.0, 6: 10.0, 7: 10.0},
                                    2016: {0: 12.0, 1: 13.0, 2: 14.0, 3: 12.0, 4: 13.0, 5: 14.0, 6: 13.0, 7: 13.0}
                                   },
                     # Demand of other sectors
                     'external_enduses': {'waste_water': {0: 10000}, #Yearly fuel data
                                          'ICT_model': {}
                                         }
                    }

    # Data container
    base_data = {}

    # Model calculations outside main function
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' #path_main = '../data'
    base_data = mf.load_data(base_data, path_main, data_external) # Load and generate data

    # Load assumptions
    print("Load Assumptions")
    base_data = assumpt.load_assumptions(base_data)

    # Disaggregate national data into regional data
    base_data = mf.disaggregate_base_demand_for_reg(base_data, 1, data_external) 

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)

    # Generate technological stock for base year (Maybe for full simualtion period? TODO)
    base_data['tech_stock_by'] = ts.ResidTechStock(base_data, base_data['assumptions'], data_external, data_external['glob_var']['base_year'])


    # Run main function
    energy_demand_model(base_data, data_external)
    print("Finished running Energy Demand Model")





    """A one-line summary that does not use variable names or the
    function name.
    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).
    This can have multiple paragraphs.
    You may include some math:

"""
