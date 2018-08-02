"""Generate scenario paramters for every year
"""
import os
import pandas as pd
from energy_demand.basic import basic_functions
from energy_demand.technologies import diffusion_technologies

def generate_general_parameter(
        path,
        regions,
        diffusion_choice,
        narratives
    ):
    """
    """
    entries = []

    # ------------------
    # Iterate narratives
    # ------------------
    for narrative in narratives:

        # Paramter of narrative
        base_yr = narrative['base_yr']
        end_yr = narrative['end_yr']
        region_value_by = narrative['region_value_by']
        region_value_ey = narrative['region_value_ey']

        if not sig_midpoint:
            sig_midpoint = 0
        if not sig_steepness:
            sig_steepness = 1

        # Calculate modelled years
        modelled_yrs = range(base_yr, end_yr + 1, 1)

        # Iterate regions
        for region in regions:

            # Iterate every modelled year
            for curr_yr in modelled_yrs:

                entry = {}
                if diffusion_choice == 'linear':
                    lin_diff_factor = diffusion_technologies.linear_diff(
                        base_yr,
                        curr_yr,
                        region_value_by[region],
                        region_value_ey[region],
                        end_yr)
                    change_cy = lin_diff_factor

                # Sigmoid diffusion up to cy
                elif diffusion_choice == 'sigmoid':

                    diff_value = region_value_ey[region] - region_value_by[region]

                    sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                        base_yr,
                        curr_yr,
                        end_yr,
                        sig_midpoint,
                        sig_steepness)
                    change_cy = diff_value * sig_diff_factor

                entry['region'] = region
                entry['year'] = curr_yr
                entry['value'] = change_cy
                entry['interval'] = 1 #add line

                # Append to dataframe
                entries.append(entry)

     # Create dataframe to store values of parameter
    col_names = ["region", "year", "value", "interval"]
    my_df = pd.DataFrame(entries, columns=col_names)
    my_df.to_csv(path, index=False) #Index prevents writing index rows

def run(
        path,
        base_yr=2015,
        end_yr=2050
    ):
    """

    Inputs
    ------
    path : str
        Path to store all generated scenario values
    """

    # --------------
    # Configuration
    # --------------
    modelled_yrs = range(base_yr, end_yr + 1, 1)

    # --------------
    # 
    # --------------
    regions = ['A', 'B']


    # Create folder to store parameters
    basic_functions.create_folder(path)

    # ------------------------
    # General change over time
    # ------------------------
    # Write value for every modelled year
    parameter_name = "test_param"

    # Dummy
    region_value_by = {}
    region_value_ey = {}
    for region_nr, region in enumerate(regions):
        region_value_by[region] = 1
        region_value_ey[region] = 2

    narratives = [
        {
            "base_yr": base_yr,
            "end_yr": end_yr,
            "region_value_by": region_value_by,
            "region_value_ey": region_value_ey,
            
            # Optional
            "sig_midpoint": None,
            "sig_steepness": None
            }
        ]

    # -------------------------------------------
    # Calculate parameters and generate .csv file
    # -------------------------------------------
    generate_general_parameter(
        path=os.path.join(path, "{}.csv".format(parameter_name)),
        regions=regions,
        diffusion_choice='sigmoid',
        narratives=narratives)

    print("Finished generating scenario values")

run("C://Users//cenv0553//ED//data//_temp_scenario_run_paramters")
