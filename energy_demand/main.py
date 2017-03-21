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
- leasitciies
- assumptions

# The docs can be found here: http://ed.readthedocs.io
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
#!python3.6
import os
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
    all_regions = [] # List to store all regions
    result_dict = mf.initialise_energy_supply_dict(len(data['fuel_type_lu']), len(data['reg_lu']), data_ext['glob_var']['base_year']) # Dict for output to energy supply model

    # --------------------------
    # Residential model
    # --------------------------

    # Generate technological stock
    data['tech_stock'] = ts.ResidTechStock(data['assumptions'], data_ext)

    # Create regions for residential model Iterate regions and generate objects
    for reg in data['reg_lu']:

        # Residential
        a = rm.Region(reg, data, data_ext)
        all_regions.append(a)



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
    result_dict = mf.convert_out_format_es(data, data_ext, all_regions)

    # --- Write out functions....scrap to improve
    print("...Write results for energy supply model to csv file and YAML files")
    mf.write_to_csv_will(data, result_dict, data['reg_lu'], False) # FALSE: don't create YAML file

    print("FINAL Fueltype:  " + str(len(result_dict)))
    print("FINAL region:    " + str(len(result_dict[1])))
    print("FINAL timesteps: " + str(len(result_dict[1][0])))
    print("Finished energy demand model")

    # Plot REgion 0 for half a year
    #pf.plot_x_days(result_dict[2], 0, 12)
    return result_dict

# Run
if __name__ == "__main__":

    # -------------------------------------------------------------------
    # Execute only once befure executing energy demand module for a year
    # ------------------------------------------------------------------_
    # Wheater generater (change base_demand data)

    # External data provided to wrapper
    data_external = {'population': {2015: {0: 3000001, 1: 5300001, 2: 53000001},
                                    2016: {0: 3001001, 1: 5301001, 2: 53001001}
                                   },

                     'glob_var': {'base_year': 2015,
                                  'current_year': 2016,
                                  'end_year': 2020
                                 },
                    }

    # Data container #TODO: add data_external to base_data
    base_data = {}

    # Model calculations outside main function
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' #path_main = '../data'
    base_data = mf.load_data(base_data, path_main) # Load and generate data

    base_data = assumpt.load_assumptions(base_data) # Load assumptions
    #base_data['assumptions'] = assumptions_model_run # Add assumptions to data

    base_data = mf.disaggregate_base_demand_for_reg(base_data, 1, data_external) # Disaggregate national data into regional data

    # Generate virtual building stock over whole simulatin period
    base_data = bg.resid_build_stock(base_data, base_data['assumptions'], data_external)

    # Generate technological stock over whole simulation period
    #base_tech_stock_resid = ts.ResidTechStock(2015, assumptions_model_run, data_external)

    # -----------------
    # Run main function
    # -----------------
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
