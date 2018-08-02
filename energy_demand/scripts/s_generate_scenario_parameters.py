"""Generate scenario paramters for every year
"""
import os
import numpy as np
from energy_demand.basic import basic_functions
from energy_demand.technologies import diffusion_technologies
from energy_demand.read_write import write_data

def generate_general_parameter(
        regions,
        diffusion_choice,
        narratives
    ):
    """
    """
    # Sigmoid settings
    sig_midpoint = 0
    sig_steepness = 1

    paramter_list = []

    for narrative in narratives:
        base_yr = narrative['base_yr']
        end_yr = narrative['end_yr']
        region_value_by = narrative['region_value_by']
        region_value_ey = narrative['region_value_ey']

        modelled_yrs = range(base_yr, end_yr + 1, 1)

        # Iterate regions
        for region in regions:
            
            entry = []
            # Iterate every modelled year
            for curr_yr in modelled_yrs:

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

                entry.append(region)
                entry.append(curr_yr)
                entry.append(change_cy)
                entry.append("1")

                paramter_list.append(entry)

        #array_to_write = np.asarray(paramter_list)
    return paramter_list
    #return array_to_write

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

    #
    # Configuration
    # 
    modelled_yrs = range(base_yr, end_yr + 1, 1)

    #
    #
    # 
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
            "region_value_ey": region_value_ey}
        ]

    rows = generate_general_parameter(
        regions=regions,
        diffusion_choice='linear',
        narratives=narratives)
    #print(array_to_write)
    write_data.create_csv_file(path, rows)

    # Write out parameter
    #write_data.write_scenario_values(
    #    os.path.join(path, "{}.csv".format(parameter_name)),
    #    array_to_write=array_to_write)
    print("Finished generating scenario values")

run("C://Users//cenv0553//ED//data//_temp_scenario_run_paramters")
