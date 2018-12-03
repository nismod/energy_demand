
import os
import configparser
import csv
import yaml
import numpy as np
from ruamel.yaml import YAML

def write_yaml(data, file_path):
    """Write plain data to a file as yaml

    Parameters
    ----------
    data
        Data to write (should be lists, dicts and simple values)
    file_path : str
        The path of the configuration file to write
    """
    with open(file_path, 'w') as file_handle:
        yaml = YAML(typ='unsafe')
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        return yaml.dump(data, file_handle)
    
path = "C:/_scrap/out.yml"

variant_list = []

for i in range(1, 101, 1):
    
    name = "NF{}".format(i)

    entry = {
        'name': name,
        'description': 'Weather realisation {}'.format(name),
        'data': {
            't_min': 'weather_data_{}.csv'.format(name),
            't_max': 'weather_data_{}.csv'.format(name)}
        }
    variant_list.append(entry)

dict_out = {
    'variants': variant_list
}

write_yaml(dict_out, path)