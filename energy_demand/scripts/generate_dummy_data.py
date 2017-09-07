"""Generate dummy data to use in smif as scenario data for testing
"""
from pprint import pprint
import logging
from energy_demand.read_write.data_loader import dummy_data_generation
import yaml



def main():
    """Generate and write out data
    """
    data = dummy_data_generation({
        'sim_param': {
            'base_yr': 2010,
            'end_yr': 2050
        }
    })
    plogging.debug(data)

    # regions

    # gva : year x region
    gva = []
    for year, region_value in data['GVA'].items():
        for region, value in region_value.items():
            gva.append({
                'interval': 1,
                'year': year,
                'region': region,
                'value': value
            })
    with open('gva.yaml', 'w') as file_handle:
        yaml.dump(gva, file_handle)

    # population : year x region
    population = []
    for year, region_value in data['population'].items():
        for region, value in region_value.items():
            population.append({
                'interval': 1,
                'year': year,
                'region': region,
                'value': value
            })
    with open('population.yaml', 'w') as file_handle:
        yaml.dump(population, file_handle)

    # residential_floor_area (rs_floorarea) : year x region
    residential_floor_area = []
    for year, region_value in data['rs_floorarea'].items():
        for region, value in region_value.items():
            residential_floor_area.append({
                'interval': 1,
                'year': year,
                'region': region,
                'value': value
            })
    with open('residential_floor_area.yaml', 'w') as file_handle:
        yaml.dump(residential_floor_area, file_handle)

if __name__ == '__main__':
    main()
