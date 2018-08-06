"""Load paramter values from csv files
"""
import os
import pandas as pd
from energy_demand.read_write import read_data
from collections import defaultdict

def load_full_parameters(
        temp_path,
        parameter_names
    ):
    """Load all csv files
    """
    container_out = {}

    for name in parameter_names:

        container = defaultdict(dict)

        path_file = os.path.join(temp_path, "{}.csv".format(name))
        #print("path_file " + str(path_file))

        # Load files with headers {"region", "year", "value", "interval"}
        #df_param = pd.read_csv(path_file, index_col=False)

        #list_with_dict_entries = df_param.to_dict(orient='region') #Convert to dict

        #for entry in list_with_dict_entries:
        #    region = entry['region']
        #    value = entry['value']
        #    year = entry['year']
        #
        #    container[region][year] = value
        #
        #container_out[name] = dict(container)

    return container
