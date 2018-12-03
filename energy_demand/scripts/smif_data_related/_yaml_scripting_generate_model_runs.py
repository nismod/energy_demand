import os
import configparser
import csv
import yaml
import numpy as np
from ruamel.yaml import YAML

from energy_demand.read_write import write_data


def run(
        path,
        sos_model,
        narrative,
        weather_name,
        gva_scenario,
        population_scenario,
        timesteps
    ):

    # Narrative parameters
    narratives = {
        'air_leakage': [narrative],
        'assump_diff_floorarea_pp': [narrative],
        'cooled_floorarea': [narrative],
        'dm_improvement': [narrative],
        'f_eff_achieved': [narrative],
        'generic_enduse_change': [narrative],
        'heat_recovered': [narrative],
        't_base_heating': [narrative],
        'p_cold_rolling_steel': [narrative],
        'smart_meter_p': [narrative],
        'generic_fuel_switch': [narrative]
        }

    scenario_name = 'energy_demand_constrained__{}__{}__{}'.format(weather_name, population_scenario, gva_scenario)

    yaml_dict_out = {
        'name': scenario_name,
        'description': "",
        'sos_model': sos_model,
        'stamp': "",
        'decision_module': '',
        'narratives': narratives,
        'strategies': {},
        'timesteps': timesteps,
        'scenarios': {
            'gva_per_head': gva_scenario,
            'population': population_scenario,
            'temperature': weather_name,
            'weather_station_coordinates': 'weather_station_coordinates__{}'.format(weather_name)
        }
    }


    path_out_file = os.path.join(path, "{}.yml".format(scenario_name))
    write_data.write_yaml(yaml_dict_out, path_out_file)

path = "C:/_scrap"

for i in range(1, 101, 1):

    # Narrative
    narrative = "central_narrative"

    # Scenario data
    gva_scenario = 'gva_baseline'
    population_scenario = 'pop_low'
    timesteps = [2015, 2050]
    sos_model = "energy_demand_constrained"
    weather_realisation = "NF{}".format(i)

    # Create .yml file
    run(
        path,
        sos_model,
        narrative,
        weather_realisation,
        gva_scenario,
        population_scenario,
        timesteps)