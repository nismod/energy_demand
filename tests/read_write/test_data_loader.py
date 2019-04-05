"""
"""
from pytest import fixture
from unittest.mock import Mock
from energy_demand.read_write.data_loader import get_local_paths


@fixture(scope='function')
def config_file(tmpdir):

    config_file = tmpdir.mkdir("config").join("wrapperconfig.ini")
    content = \
"""
[PATHS]
path_local_data = /vagrant/data/energy_demand
path_processed_data = /vagrant/data/energy_demand/_processed_data
path_result_data = /vagrant/data/energy_demand/results
path_config_data = /vagrant/data/energy_demand/config_data

[CONFIG]
base_yr = 2015
weather_yr_scenario = 2015
user_defined_simulation_end_yr = 2050
user_defined_weather_by = 2015

[CRITERIA]
mode_constrained = True
virtual_building_stock_criteria = True
write_out_national = False
reg_selection = False
MSOA_crit = False
reg_selection_csv_name = msoa_regions_ed.csv
spatial_calibration = False
cluster_calc = False
write_txt_additional_results = True
validation_criteria = True
plot_crit = False
crit_plot_enduse_lp = False
writeYAML_keynames = True
writeYAML = False
crit_temp_min_max = False

[DATA_PATHS]
local_path_datafolder = /vagrant/data/energy_demand
path_strategy_vars =  /vagrant/data/energy_demand/energy_demand_minimal/00_user_defined_variables
#ONS principal projection
path_population_data_for_disaggregation_LAD =  /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050.csv
#ONS principal projection
folder_raw_carbon_trust = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/G_Carbon_Trust_advanced_metering_trial/
path_population_data_for_disaggregation_MSOA = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050_MSOA_lad.csv
path_floor_area_virtual_stock_by = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/K-floor_area/floor_area_LAD_latest.csv
path_assumptions_db = /vagrant/data/energy_demand/_processed_data/assumptions_from_db
data_processed = /vagrant/data/energy_demand/_processed_data
lad_shapefile = /vagrant/data/energy_demand/energy_demand_minimal/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp
path_post_installation_data = /vagrant/data/energy_demand/_processed_data
weather_data = _/raw_data/A-temperature_data/cleaned_weather_stations_data
load_profiles = /vagrant/data/energy_demand/_processed_data/load_profiles
rs_load_profile_txt = /vagrant/data/energy_demand/_processed_data/load_profiles/rs_submodel),
ss_load_profile_txt = /vagrant/data/energy_demand/_processed_data/load_profiles/ss_submodel),
yaml_parameters = /vagrant/data/energy_demand/config/yaml_parameters.yml
yaml_parameters_constrained = /vagrant/data/energy_demand/config/yaml_parameters_constrained.yml
yaml_parameters_keynames_constrained = /vagrant/data/energy_demand/config/yaml_parameters_keynames_constrained.yml
yaml_parameters_keynames_unconstrained = /vagrant/data/energy_demand/config/yaml_parameters_keynames_unconstrained.yml
yaml_parameters_scenario = /vagrant/data/energy_demand/config/yaml_parameters_scenario.yml

"""

    config_file.write(content)

    return str(config_file)


def test_get_local_paths(config_file):

    actual = get_local_paths(config_file)

    assert isinstance(actual, dict)
    assert actual['yaml_parameters_scenario'] == '/vagrant/data/energy_demand/config/yaml_parameters_scenario.yml'
