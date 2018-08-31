"""Project 2011 MSOA population to the future with help of LAD population scenarios
"""
import os
from collections import defaultdict
from energy_demand.read_write import data_loader
from energy_demand.read_write import write_data

def remap_lads(lad_name):
    """Some LADs of MSOA census data do not match
    the LAD geographies of the LAD population data
    """
    if lad_name == 'E06000048':
        lad_mapped = 'E06000057' #Northumberland
    elif lad_name == 'E08000020':
        lad_mapped = 'E08000037'
    elif lad_name == 'E07000097':
        lad_mapped = 'E07000242'
    elif lad_name == 'E07000100':
        lad_mapped = 'E07000240'
    elif lad_name == 'E07000101':
        lad_mapped = 'E07000243'
    elif lad_name == 'E07000104': #Welwyn Hatfield
        lad_mapped = 'E07000241'
    else:
        lad_mapped = lad_name

    return lad_mapped

mapping_dict = True
population_script = False
gva_script = False

# ------------------------------------------------
# Create mapping dict {"LAD": [MSOAs]}
# ------------------------------------------------
if mapping_dict:
    local_data_path = "C:/Users/cenv0553/ED/data/scenarios"
    path_to_csv_MSOA = os.path.join(local_data_path, "pop_MSOA_orig.csv")
    path_to_csv_LAD = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050.csv')
    path_out = os.path.join(local_data_path, 'mapping_MSOA_LAD.txt')

    # Read 2011 MSOA population data
    population_2011 = data_loader.load_MOSA_pop(path_to_csv_MSOA)

    # Read 2015 - 2050 population data for LAD
    pop_lads_2015_2015 = data_loader.read_scenario_data(path_to_csv_LAD)

    all_msoas = []
    for lad, msoas in population_2011.items():
        all_msoas += list(msoas.keys())

    # all lads
    all_lads = list(pop_lads_2015_2015[2015].keys())

    dict_mapping = {}

    # ----------------------------------------------------
    # Iterate MSOA and add population
    # ----------------------------------------------------
    for msoa in all_msoas:

        for lad, msoas in population_2011.items():
            msoas_of_lad = list(msoas.keys())
            if msoa in msoas_of_lad:
                lad_match = lad
                break

        # Remap
        lad_match_remap = remap_lads(lad_match)
        try:
            dict_mapping[lad_match_remap].append(msoa)
        except KeyError:
            dict_mapping[lad_match_remap] = [msoa]

    print(len(dict_mapping.keys()))
    text_file = open(path_out, "w")
    text_file.write(str(dict_mapping))
    text_file.close()
    print("Finished dict script")

# ------------------------------------------------
# Population
# ------------------------------------------------
if population_script:
    local_data_path = "C:/Users/cenv0553/ED/data/scenarios"
    path_to_csv_MSOA = os.path.join(local_data_path, "pop_MSOA_orig.csv")
    path_to_csv_LAD = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050.csv')
    path_out = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050_MSOA_lad.csv')

    # Read 2011 MSOA population data
    population_2011 = data_loader.load_MOSA_pop(path_to_csv_MSOA)

    # Read 2015 - 2050 population data for LAD
    pop_lads_2015_2015 = data_loader.read_scenario_data(path_to_csv_LAD)

    all_msoas = []
    for lad, msoas in population_2011.items():
        all_msoas += list(msoas.keys())

    msoa_pop_2011_2050 = defaultdict(dict)

    # all lads
    all_lads = list(pop_lads_2015_2015[2015].keys())

    # ----------------------------------------------------
    # Iterate MSOA and add population
    # ----------------------------------------------------
    for msoa in all_msoas:

        for lad, msoas in population_2011.items():
            msoas_of_lad = list(msoas.keys())
            if msoa in msoas_of_lad:
                lad_match = lad
                break

        # Remap
        lad_match_remap = remap_lads(lad_match)

        # Remove lad
        for lad_position, lad in enumerate(all_lads):
            if lad == lad_match_remap:
                all_lads.pop(lad_position)
                break

        # pop_LAD_2011
        lad_pop_by = sum(population_2011[lad_match].values())

        for year in pop_lads_2015_2015.keys():

            # pop msoa 2011
            msoa_pop_2011 = population_2011[lad_match][msoa]

            # pop lad cy
            lad_pop_cy = pop_lads_2015_2015[year][lad_match_remap]

            # Get change in LAd projection and assume that
            # the same change for all MSOA of the corresponding LAD
            change_p = lad_pop_cy / lad_pop_by

            msoa_pop_2011_2050[year][msoa] = change_p * msoa_pop_2011

    # ----------------------------------------------------
    # Iterate all lads and add population for northern ireland and scotland
    # ----------------------------------------------------
    for lad in all_lads:
        for year in pop_lads_2015_2015.keys():
            msoa_pop_2011_2050[year][lad] = pop_lads_2015_2015[year][lad]

    # Write msoa to file
    rows = [("region", "year", "value", "interval")]

    for year, msoas in msoa_pop_2011_2050.items():
        for msoa, pop in msoas.items():
            rows.append([msoa, year, pop, 1])

    write_data.create_csv_file(path_out, rows)

    #np.savetxt(path_out, rows, delimiter=",", header="{}, {}, {}, {}".format("region", "year", "value", "interval"), comments='')
    print("Finished pop script")

# ------------------------------------------------
# GVA Dummy data
# ------------------------------------------------
if gva_script:
    local_data_path = "C:/Users/cenv0553/ED/data/scenarios"
    
    path_to_csv_MSOA = os.path.join(local_data_path, "pop_MSOA_orig.csv")
    path_to_csv_LAD_pop = os.path.join(local_data_path, 'uk_pop_high_migration_2015_2050.csv')
    path_out = os.path.join(local_data_path, 'gva_sven_msoa_lad.csv')

    dummy_gva = 1000

    # Get all MSOA
    path_to_csv_MSOA = os.path.join(local_data_path, "pop_MSOA_orig.csv")
    population_2011 = data_loader.load_MOSA_pop(path_to_csv_MSOA)

    # Get all LADS
    pop_lads_2015_2015 = data_loader.read_scenario_data(path_to_csv_LAD_pop)

    all_msoas = []
    for lad, msoas in population_2011.items():
        all_msoas += list(msoas.keys())

    gva_dummy_msoa_lad = defaultdict(dict)

    # all lads
    all_lads = list(pop_lads_2015_2015[2015].keys())

    # ----------------------------------------------------
    # Iterate MSOA and add population
    # ----------------------------------------------------
    for msoa in all_msoas:

        for lad, msoas in population_2011.items():
            msoas_of_lad = list(msoas.keys())
            if msoa in msoas_of_lad:
                lad_match = lad
                break

        # Remap
        lad_match_remap = remap_lads(lad_match)

        # Remove lad
        for lad_position, lad in enumerate(all_lads):
            if lad == lad_match_remap:
                all_lads.pop(lad_position)
                break


        for year in pop_lads_2015_2015.keys():
            gva_dummy_msoa_lad[year][msoa] = dummy_gva

    # ----------------------------------------------------
    # Iterate all lads and add population for northern ireland and scotland
    # ----------------------------------------------------
    for lad in all_lads:
        for year in pop_lads_2015_2015.keys():
            gva_dummy_msoa_lad[year][lad] = dummy_gva

    # Write msoa to file
    rows = [("region", "year", "value", "interval")]

    for year, msoas in gva_dummy_msoa_lad.items():
        for msoa, gva in msoas.items():
            rows.append([msoa, year, gva, 1])

    write_data.create_csv_file(path_out, rows)
    print("Finished gva script")
