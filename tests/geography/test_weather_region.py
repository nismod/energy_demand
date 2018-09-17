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

def test_change_temp_climate():

    temp_data = np.zeros((365, 24)) + 10
    for i in range(31):
        temp_data[i] = 5

    yeardays_month_days = {
        0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
        1: [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58],
        2: [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
        3: [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119],
        4: [120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150],
        5: [151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180],
        6: [181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211],
        7: [212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242],
        8: [243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272],
        9: [273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303],
        10: [304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333],
        11: [334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364]}

    strategy_vars = {'climate_change_temp_d': {
        'Jan': {2015: 0, 2020: 2}, # January (can be plus or minus)
        'Feb': {2015: 0, 2020: 3}, # February
        'Mar': {2015: 0, 2020: 0}, # March
        'Apr': {2015: 0, 2020: 0}, # April
        'May': {2015: 0, 2020: 0}, # May
        'Jun': {2015: 0, 2020: 0}, # June
        'Jul': {2015: 0, 2020: 0}, # July
        'Aug': {2015: 0, 2020: 0}, # August
        'Sep': {2015: 0, 2020: 0}, # September
        'Oct': {2015: 0, 2020: 0}, # October
        'Nov': {2015: 0, 2020: 0}, # November
        'Dec': {2015: 0, 2020: 0}}}

    curr_yr = 2020

    result = weather_region.change_temp_climate(
        curr_yr,
        temp_data,
        yeardays_month_days,
        strategy_vars)

    assert result[30][0] == 5 + 2
    assert result[40][0] == 10 + 3
