"""

Transportation Submodel
====================

"""
from energy_demand.profiles import generic_shapes

class OtherModel(object):
    """Other Model
    """
    def __init__(self, region_obj, enduse, nr_ed_modelled_dates):
        """Constructor

        Arguments
        ----------
        data : dict
            Data
        region_obj : dict
            Object of region
        enduse : string
            Enduse
        sector : string
            Service sector
        """
        self.region_name = region_obj.region_name
        self.enduse = enduse

        # Transportation + agriculture
        #self.fuels_reg =  #region_obj.ts_fuels + region_obj.ag_fuels

        self.enduse_object = self.create_enduse(region_obj, nr_ed_modelled_dates)

    def create_enduse(self, region_obj, nr_ed_modelled_dates):
        """Create enduse
        """
        model_object = generic_shapes.GenericFlatEnduse(region_obj.ts_fuels, nr_ed_modelled_dates)

        return model_object
