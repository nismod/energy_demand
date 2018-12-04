
import os
import configparser
import csv
import yaml
import numpy as np
from ruamel.yaml import YAML

from energy_demand.read_write import write_data


# ------------------------
# TEmp data
# ------------------------
path = "C:/_scrap/temp-data.yml"

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

write_data.write_yaml(dict_out, path)

# ------------------------
# Weather Stations
# ------------------------
path = "C:/_scrap/weateher-station.yml"

variant_list = []

for i in range(1, 101, 1):
    
    name = "NF{}".format(i)

    entry = {
        'name': "weather_station_coordinates__{}".format(name),
        'description': 'Weather station coordinates for weather data {}'.format(name),
        'data': {
            'longitude': 'stations_{}.csv'.format(name),
            'latitude': 'stations_{}.csv'.format(name)}
        }
    variant_list.append(entry)

dict_out = {
    'variants': variant_list
}

write_data.write_yaml(dict_out, path)