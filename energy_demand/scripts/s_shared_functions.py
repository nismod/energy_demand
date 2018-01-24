"""Function which are used in multiple scripts
"""
import os
import json
import numpy as np
from energy_demand.read_write import write_data

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
    '''def jason_shape_peak_dh(input_array, outfile_path):
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
    jason_shape_peak_dh(
        shape_peak_dh,
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')))
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
            str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))'''

    # Main function
    write_data.write_array_to_txt(
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')),
        shape_peak_dh)

    write_data.write_array_to_txt(
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_y_dh') + str('.txt')),
        shape_non_peak_y_dh)

    write_data.write_array_to_txt(
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')),
        np.array([shape_peak_yd_factor]))

    write_data.write_array_to_txt(
        os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')),
        shape_non_peak_yd)

    return
