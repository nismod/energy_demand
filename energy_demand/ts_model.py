"""

Transportation Submodel
====================

"""
from energy_demand.profiles import generic_shapes

class OtherModel(object):
    """Other Model
    """
    def __init__(self, region_object, enduse):
        """Constructor

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

        # Transportation + agriculture
        self.fuels_reg = region_object.ts_fuels # + region_object.ag_fuels

        self.enduse_object = self.create_enduse()

    def create_enduse(self):
        """Create enduse
        """
        model_object = generic_shapes.genericFlatEnduse(self.fuels_reg)

        return model_object
