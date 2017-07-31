"""Residential Submodel
"""
import energy_demand.enduse as endusefunctions

class ResidentialModel(object):
    """Residential Submodel
    """
    def __init__(self, data, region_object, enduse, sector):
        """Constructor of ResidentialModel

        Parameters
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse : string
            Enduse
        """
        self.region_name = region_object.region_name
        self.enduse = enduse
        self.sector = sector
        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):
        """Create enduse objects and add to list
        """
        enduse_object = endusefunctions.Enduse(
            region_name=self.region_name,
            data=data,
            enduse=self.enduse,
            sector=self.sector,
            enduse_fuel=region_object.rs_enduses_fuel[self.enduse],
            tech_stock=region_object.rs_tech_stock,
            heating_factor_y=region_object.rs_heating_factor_y,
            cooling_factor_y=region_object.rs_cooling_factor_y,
            fuel_switches=data['assumptions']['rs_fuel_switches'],
            service_switches=data['assumptions']['rs_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['rs_fuel_enduse_tech_p_by'][self.enduse],
            service_tech_by_p=data['assumptions']['rs_service_tech_by_p'][self.enduse],
            tech_increased_service=data['assumptions']['rs_tech_increased_service'],
            tech_decreased_share=data['assumptions']['rs_tech_decreased_share'],
            tech_constant_share=data['assumptions']['rs_tech_constant_share'],
            installed_tech=data['assumptions']['rs_installed_tech'],
            sig_param_tech=data['assumptions']['rs_sig_param_tech'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['rs_model'],
            dw_stock=data['rs_dw_stock'],
            load_profiles=region_object.rs_load_profiles
            )

        return enduse_object
