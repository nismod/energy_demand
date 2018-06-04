"""Project 2011 MSOA population to the future
with help of LAD population scenarios
"""
import os
from collections import defaultdict
from energy_demand.read_write import data_loader
from energy_demand.read_write import write_data

local_data_path = "C:/Users/cenv0553/ED/data/scenarios"
path_to_csv_MSOA = os.path.join(local_data_path, "pop_MSOA_orig.csv")
path_to_csv_LAD = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050.csv')
path_out = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050_MSOA.csv')

# Read 2011 MSOA population data
population_2011 = data_loader.load_MOSA_pop(path_to_csv_MSOA)

# Read 2015 - 2050 population data for LAD
pop_LAD_2015_2015 = data_loader.read_scenario_data(path_to_csv_LAD)

all_MSOA = []
for lad, msoas in population_2011.items():
    all_MSOA += list(msoas.keys())

msoa_pop_2011_2050 = defaultdict(staticmethod)

# Iterate MSOA
for msoa in all_MSOA:

    for lad, msoas in population_2011.items():
        msoas_of_lad = list(msoas.keys())
        if msoa in msoas_of_lad:
            lad_match = lad
            break

    # pop_LAD_2011
    lad_pop_by = sum(population_2011[lad_match].values())

    for year in pop_LAD_2015_2015.keys():

        # pop msoa 2011
        msoa_pop_2011 = population_2011[lad_match][msoa]

        # pop lad cy
        lad_pop_cy = pop_LAD_2015_2015[year]

        # Get change in LAd projection and assume that
        # the same change for all MSOA of the corresponding LAD
        change_p = lad_pop_cy / lad_pop_by

        msoa_pop_2011_2050[year][msoa] = change_p * msoa_pop_2011

# Write msoa to file
rows = (["region", "year", "value", "interval"])

for year, msoas in msoa_pop_2011_2050.keys():
    for msoa, pop in msoas.keys():
        rows.append(["msoas", "year", pop, 1])

write_data.create_csv_file(path_out, rows)









