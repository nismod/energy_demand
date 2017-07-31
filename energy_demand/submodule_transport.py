"""Dummy transportation model
"""
import energy_demand.enduse as enduse_functions
import numpy as np

class TransportModel(object):
    """Industry Submodel
    """
    def __init__(self, region_object, enduse):
        """Constructor of industry submodel

        Parameters
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse : string
            Enduse
        sector : string
            Service sector
        """
        self.region_name = region_object.region_name
        self.enduse = enduse

        self.fuels_reg = region_object.ts_fuels

        self.enduse_object = self.ts_create_enduse()

    def ts_create_enduse(self):
        """Create enduse for industry sector
        """
        transport_object = enduse_functions.genericFlatEnduse(self.fuels_reg)

        return transport_object
