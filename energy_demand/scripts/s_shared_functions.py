"""Function which are used in multiple scripts
"""
import os
import csv
from datetime import date
from datetime import timedelta
from energy_demand.basic import date_prop
import json
import numpy as np

def create_txt_shapes(
        end_use,
        path_txt_shapes,
        shape_peak_dh,
        shape_non_peak_y_dh,
        shape_peak_yd_factor,
        shape_non_peak_yd
    ):
    """Function collecting functions to write out txt files
    """

    def jason_shape_peak_dh(input_array, outfile_path):
        """Wrte to txt. Array with shape: (24,)
        """
        np_dict = dict(enumerate(input_array))
        with open(outfile_path, 'w') as outfile:
            json.dump(np_dict, outfile)

    def jason_shape_non_peak_y_dh(input_array, outfile_path):
        """Wrte to txt. Array with shape: (model_yeardays_nrs, 24)
        """
        out_dict = {}
        for k, row in enumerate(input_array):
            out_dict[k] = dict(enumerate(row))
        with open(outfile_path, 'w') as outfile:
            json.dump(out_dict, outfile)

    def jason_shape_peak_yd_factor(input_array, outfile_path):
        """Wrte to txt. Array with shape: ()
        """
        with open(outfile_path, 'w') as outfile:
            json.dump(input_array, outfile)

    def jason_shape_non_peak_yd(input_array, outfile_path):
        """Wrte to txt. Array with shape: (model_yeardays_nrs)"""
        out_dict = {}
        for k, row in enumerate(input_array):
            out_dict[k] = row
        with open(outfile_path, 'w') as outfile:
            json.dump(out_dict, outfile)

    # Main function
    jason_shape_peak_dh(
        shape_peak_dh,
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt'))
        )
    jason_shape_non_peak_y_dh(
        shape_non_peak_y_dh, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_y_dh') + str('.txt')))
    jason_shape_peak_yd_factor(
        shape_peak_yd_factor, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
    jason_shape_non_peak_yd(
        shape_non_peak_yd, os.path.join(
            path_txt_shapes,
            str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))

    return

def read_assumption_sim_param(path_to_csv):
    """Read assumptions from dict

    Arguments
    ----------
    path_to_csv : str
        Path to csv file with info

    Return
    -----
    assumptions : dict
        Assumptions
    """
    assumptions = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(csvfile) # Skip headers

        for row in read_lines:
            try:
                assumptions[str(row[0])] = float(row[1])
            except ValueError:
                assumptions[str(row[0])] = None

    # Redefine sim_period_yrs
    assumptions['sim_period'] = range(
        int(assumptions['base_yr']),
        int(assumptions['end_yr']) + 1,
        int(assumptions['sim_years_intervall'])
        )

    # Redefine sim_period_yrs
    assumptions['list_dates'] = date_prop.fullyear_dates(
        start=date(int(assumptions['base_yr']), 1, 1),
        end=date(int(assumptions['base_yr']), 12, 31))

    return assumptions
