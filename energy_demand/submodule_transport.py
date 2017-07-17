import energy_demand.enduse as enduse_functions

class TransportModel(object):
    """Industry Submodel
    """
    def __init__(self, data, region_object, enduse_name):
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

        self.enduse_object = self.create_enduse(data)

    def create_enduse(self, data):
        """Create enduse for industry sector
        """

        fuels_tranpsort_reg = data['ts_fueldata_disagg'][self.reg_name]

        transport_object = enduse_functions.genericEnduse(fuels_tranpsort_reg)

        return transport_object
