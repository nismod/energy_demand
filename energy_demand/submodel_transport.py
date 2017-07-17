"""
"""

class TransportModel(object):
    """Industry Submodel
    """
    def __init__(self, data, region_object):
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
        self.fuels_all_enduses = data['ts_fueldata_disagg'][self.reg_name]

        #self.enduse_object = self.create_enduse(region_object, data)