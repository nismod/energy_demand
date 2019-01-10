"""Generate YAML files with standard yaml 
"""
import os
import configparser
from energy_demand.assumptions import general_assumptions
from energy_demand.assumptions import strategy_vars_def
from energy_demand.read_write import data_loader
from energy_demand.basic import lookup_tables

# ----------------------------
# Configuration
# ----------------------------
path_config = os.path.abspath(
    os.path.join(
            os.path.dirname(__file__), '..', '..', '..', "config"))

path_main = os.path.abspath(
    os.path.join(
            os.path.dirname(__file__), '..', "config_data"))
# Configuration paths
config = configparser.ConfigParser()
config.read(os.path.join(path_config, 'wrapperconfig.ini'))

# --------
# Other configuration
# --------
base_yr = 2015
sim_yrs = [2015, 2050]

paths = data_loader.load_paths(path_main)
data_path = os.path.normpath(config['PATHS']['path_local_data'])

local_paths = data_loader.get_local_paths(
    data_path)

data = {}

data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(
    paths)

assumptions = general_assumptions.Assumptions(
    base_yr=user_defined_base_yr,
    curr_yr=2015,
    sim_yrs=sim_yrs,
    paths=paths,
    enduses=data['enduses'],
    sectors=data['sectors'])

# Write parameters to YAML file
_, _ = strategy_vars_def.load_param_assump(
    assumptions)

print("==========")
print("Finishged generating YAML file with scenario parameters")
print("==========")
