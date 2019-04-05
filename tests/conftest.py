#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for energy_demand.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
from __future__ import absolute_import, division, print_function

from pytest import fixture


@fixture(scope='function')
def config_file(tmpdir):
    config_file = tmpdir.mkdir("config").join("wrapperconfig.ini")
    contents = """
[PATHS]
path_local_data = tests
path_processed_data = tests/_processed_data
path_result_data = tests/results
path_config_data = tests/config_data
path_new_scenario = tests/results/tmp_model_run_results

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
local_path_datafolder = tests/energy_demand_minimal
path_strategy_vars = tests/energy_demand_minimal/00_user_defined_variables
#ONS principal projection
path_population_data_for_disaggregation_LAD =  tests/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050.csv  
#ONS principal projection
folder_raw_carbon_trust = tests/energy_demand_minimal/_raw_data/G_Carbon_Trust_advanced_metering_trial/
path_population_data_for_disaggregation_MSOA = tests/energy_demand_minimal/_raw_data/J-population_disagg_by/uk_pop_principal_2015_2050_MSOA_lad.csv
path_floor_area_virtual_stock_by = tests/energy_demand_minimal/_raw_data/K-floor_area/floor_area_LAD_latest.csv
path_assumptions_db = tests/_processed_data/assumptions_from_db
data_processed = tests/_processed_data
lad_shapefile = tests/energy_demand_minimal/_raw_data/C_LAD_geography/same_as_pop_scenario/lad_2016_uk_simplified.shp
path_post_installation_data = tests/_processed_data
weather_data = /raw_data/A-temperature_data/cleaned_weather_stations_data
load_profiles = tests/_processed_data/load_profiles
rs_load_profile_txt = tests/_processed_data/load_profiles/rs_submodel
ss_load_profile_txt = tests/_processed_data/load_profiles/ss_submodel
yaml_parameters = tests/config/yaml_parameters.yml
yaml_parameters_constrained = tests/config/yaml_parameters_constrained.yml
yaml_parameters_keynames_constrained = tests/config/yaml_parameters_keynames_constrained.yml
yaml_parameters_keynames_unconstrained = tests/config/yaml_parameters_keynames_unconstrained.yml
yaml_parameters_scenario = tests/config/yaml_parameters_scenario.yml

[CONFIG_DATA]
path_main = tests/config_data
# Path to all technologies
path_technologies = tests/config_data/05-technologies/technology_definition.csv
# Paths to fuel raw data
rs_fuel_raw = tests/config_data/02-fuel_base_year/rs_fuel.csv
ss_fuel_raw = tests/config_data/02-fuel_base_year/ss_fuel.csv
is_fuel_raw = tests/config_data/02-fuel_base_year/is_fuel.csv
# Load profiles
lp_rs = tests/config_data/03-load_profiles/rs_submodel/HES_lp.csv
# Technologies load shapes
path_hourly_gas_shape_resid = tests/config_data/03-load_profiles/rs_submodel/lp_gas_boiler_dh_SANSOM.csv
lp_elec_hp_dh = tests/config_data/03-load_profiles/rs_submodel/lp_elec_hp_dh_LOVE.csv
lp_all_microCHP_dh = tests/config_data/03-load_profiles/rs_submodel/lp_all_microCHP_dh_SANSOM.csv
path_shape_rs_cooling = tests/config_data/03-load_profiles/rs_submodel/shape_residential_cooling.csv
path_shape_ss_cooling = tests/config_data/03-load_profiles/ss_submodel/shape_service_cooling.csv
lp_elec_storage_heating = tests/config_data/03-load_profiles/rs_submodel/lp_elec_storage_heating_HESReport.csv
lp_elec_secondary_heating = tests/config_data/03-load_profiles/rs_submodel/lp_elec_secondary_heating_HES.csv
# Census data
path_employment_statistics = tests/config_data/04-census_data/LAD_census_data.csv
# Validation datasets
val_subnational_elec = tests/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec.csv
val_subnational_elec_residential = tests/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_domestic.csv
val_subnational_elec_non_residential = tests/config_data/01-validation_datasets/02_subnational_elec/data_2015_elec_non_domestic.csv
val_subnational_elec_msoa_residential = tests/config_data/01-validation_datasets/02_subnational_elec/MSOA_domestic_electricity_2015_cleaned.csv
val_subnational_elec_msoa_non_residential = tests/config_data/01-validation_datasets/02_subnational_elec/MSOA_non_dom_electricity_2015_cleaned.csv
val_subnational_gas = tests/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas.csv
val_subnational_gas_residential = tests/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_domestic.csv
val_subnational_gas_non_residential = tests/config_data/01-validation_datasets/03_subnational_gas/data_2015_gas_non_domestic.csv
val_nat_elec_data = tests/config_data/01-validation_datasets/01_national_elec_2015/elec_demand_2015.csv
"""
    config_file.write(contents)
    return str(config_file)
