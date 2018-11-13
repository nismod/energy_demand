"""
"""
from energy_demand.geography import weather_region
from energy_demand.assumptions import strategy_vars_def
import numpy as np

'''def test_WeatherRegion():

    from energy_demand.read_write import data_loader
    from energy_demand.assumptions import general_assumptions
    path_main = os.path.abspath("C://Users//cenv0553//nismod//models//energy_demand")
    path_main = os.path.join("")

    # Load data
    data = {}
    data['paths'] = data_loader.load_paths(path_main)
    data['local_paths'] = data_loader.get_local_paths(path_main)
    data['lookups'] = lookup_tables.basic_lookups()
    data['enduses'], data['sectors'], data['fuels'] = data_loader.load_fuels(data['paths'], data['lookups'])
    
    #{'base_yr': base_yr, 'curr_yr': curr_yr, 'sim_period_yrs': sim_period_yrs}
    #Load assumptions


    strategy_vars_def.load_param_assump(data['paths'], data['enduses'])
    data['assumptions'] = read_data.read_param_yaml(data['paths']['yaml_parameters'])
    data['tech_lp'] = data_loader.load_data_profiles(data['paths'], data['local_paths'], data['assumptions'])

    weather_region_obj = weather_region.WeatherRegion(
        weather_region_name="Bern",
        sim_param=data['sim_param'],
        assumptions=data['assumptions'],
        lookups=data['lookups'],
        enduses=['heating', 'cooking'],
        temp_by=np.zeros((365, 24)),
        tech_lp=data['tech_lp'],
        sectors=["sec_A"]
    )
    assert weather_region_obj.weather_region_name == 'Bern'
test_WeatherRegion()'''
