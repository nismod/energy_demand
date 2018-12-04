"""Generate model runs
"""
import os
import configparser
import csv
import yaml
import numpy as np
from ruamel.yaml import YAML

from energy_demand.read_write import write_data

def generate_yaml(
        narrative,
        params,
        out_folder,
        weather_real,
        name_sector_model
    ):

    # Create narratives
    narratives = []

    for param_name in params:
        #Narratives
        narratives.append({
            'name': param_name,
            'provides': {'energy_demand_constrained': [param_name]},
            'description': '',
            'variants': [
                {
                    'name': narrative,
                    'description': '',
                    'data': [{param_name: '{}__{}.csv'.format(param_name, narrative)}]
                }]
        })


    yaml_dict = {

        'name': name_sector_model,

        #Narratives
        'narratives': narratives,
    
        # Scenarios
        'scenarios': ['population', 'gva_per_head','temperature'],

        'description': 'Model run description is...',
        
        'model_dependencies': [],
        
        'sector_models': ['energy_demand_constrained'],

        #Scenario dependendies
        'scenario_dependencies': [
            {
                'sink': name_sector_model,
                'source': 'population',
                'source_output': 'population',
                'sink_input': 'population'
            },
            {
                'sink': name_sector_model,
                'source': 'gva_per_head',
                'source_output': 'gva_per_head',
                'sink_input': 'gva_per_head'
            },
            {
                'sink': name_sector_model,
                'source': 'gva_per_sector',
                'source_output': 'gva_per_sector',
                'sink_input': 'gva_per_sector'
            },
            {
                'sink': name_sector_model,
                'source': 'weather_station_coordinates',
                'source_output': 'latitude',
                'sink_input': 'latitude'
            },
            {
                'sink': name_sector_model,
                'source': 'weather_station_coordinates',
                'source_output': 'longitude',
                'sink_input': 'longitude'
            },
            {
                'sink': name_sector_model,
                'source': 'temperature',
                'source_output': 't_min',
                'sink_input': 't_min'
            },
            {
                'sink': name_sector_model,
                'source': 'temperature',
                'source_output': 't_max',
                'sink_input': 't_max'
            }],
        

        }

    path_yaml = os.path.join(out_folder, "energy_demand_constrained__{}.yml".format(weather_real))
    write_data.write_yaml(yaml_dict, path_yaml)

params = [
    'air_leakage',
    'assump_diff_floorarea_pp',
    'cooled_floorarea',
    'dm_improvement',
    'f_eff_achieved',
    'generic_enduse_change',
    'heat_recovered',
    'is_t_base_heating',
    'p_cold_rolling_steel',
    'rs_t_base_heating',
    'ss_t_base_heating',
    'smart_meter_p',
    'generic_fuel_switch']

out_folder = "C:/_scrap"

#Weather scenario
weather_real = "NF1"
name_sector_model = "energy_demand_constrained"

generate_yaml(
    narrative='central',
    params=params,
    out_folder=out_folder,
    weather_real=weather_real,
    name_sector_model=name_sector_model)