"""Dummy transportation model
"""
import energy_demand.enduse as enduse_functions
import numpy as np

class TransportModel(object):
    """Industry Submodel
    """
    def __init__(self, region_object, enduse_name):
        """Constructor of industry submodel

        Parameters
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse_name : string
            Enduse
        sector : string
            Service sector
        """
        self.reg_name = region_object.reg_name
        self.enduse_name = enduse_name

        self.fuels_reg = region_object.ts_fuels

        self.enduse_object = self.ts_create_enduse()

    def ts_create_enduse(self):
        """Create enduse for industry sector
        """
        transport_object = enduse_functions.genericFlatEnduse(self.fuels_reg)

        return transport_object
