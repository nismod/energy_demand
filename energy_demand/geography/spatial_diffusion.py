"""This file calculates spatial diffusion index
"""
from collections import defaultdict
import numpy as np

def calc_diff_index(regions, enduses):
    """Load or calculate spatial index e.g. based on urban/rural population
    """
    spatial_index = defaultdict(dict)

    for enduse in enduses:
        #dummy_indeces = [1.4, 2]
        #cnt = 0
        for region in regions:

            dummy_index = 1 #TODO
            #dummy_index = dummy_indeces[cnt] #TODO

            spatial_index[enduse][region] = dummy_index
            #cnt += 1

    return dict(spatial_index)

def calc_diff_factor(regions, spatial_diffusion_index, fuels):
    """Calculate factor for every region to calculate
    energy demand to be reduced for every region

    Multiply index with % of total ed demand of region
    """

    # Calculate fraction of energy demand of every region of total demand
    reg_enduse_p = {}
    fraction_p = {}

    for fuel_submodel in fuels:

        # -----------------------------------
        # If sectors, sum fuel across sectors
        # -----------------------------------
        fuel_submodel_new = {}
        for reg, entries in fuel_submodel.items():

            try:
                enduses = []
                fuel_submodel_new[reg] = {}
                for sector in entries:
                    for enduse in entries[sector]:
                        fuel_submodel_new[reg][enduse] = 0
                        enduses.append(enduse)
                    break

                for sector in entries:
                    for enduse in entries[sector]:
                        fuel_submodel_new[reg][enduse] += np.sum(entries[sector][enduse])

                fuel_submodel = fuel_submodel_new

            except IndexError:
                enduses = entries.keys()
                break

        # --------------------
        # Calculate % of enduse ed of a region of total enduse ed
        # --------------------
        for enduse in enduses:
            reg_enduse_p[enduse] = {}
            fraction_p[enduse] = {}

            # Total uk fuel of enduse
            tot_enduse_uk = 0
            for reg in regions:
                tot_enduse_uk += fuel_submodel[reg][enduse]

            # Calculate regional % of enduse
            for region in regions:
                reg_enduse_p[enduse][region] = np.sum(fuel_submodel[reg][enduse]) / np.sum(tot_enduse_uk)

            tot_reg_enduse_p = sum(reg_enduse_p[enduse].values())

            # Calculate fraction
            for region in regions:
                fraction_p[enduse][region] = np.sum(reg_enduse_p[enduse][region]) / tot_reg_enduse_p

        # ----------
        # Multiply fraction of enduse with spatial_diffusion_index
        # ----------
        reg_fraction_multiplied_index = {}
        for enduse, regions_fuel_p in fraction_p.items():
            reg_fraction_multiplied_index[enduse] = {}

            for reg, fuel_p in regions_fuel_p.items():
                reg_fraction_multiplied_index[enduse][reg] = fuel_p * spatial_diffusion_index[enduse][reg]

    #-----------
    # Normalize
    #-----------
    for enduse in reg_fraction_multiplied_index:
        sum_enduse = sum(reg_fraction_multiplied_index[enduse].values())
        for reg in reg_fraction_multiplied_index[enduse]:
            reg_fraction_multiplied_index[enduse][reg] = reg_fraction_multiplied_index[enduse][reg] / sum_enduse

    # TEsting
    for enduse in reg_fraction_multiplied_index:
        np.testing.assert_almost_equal(sum(reg_fraction_multiplied_index[enduse].values()), 1, decimal=2)

    return reg_fraction_multiplied_index
