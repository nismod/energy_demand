"""
Service Submodel
====================

"""
import energy_demand.enduse_func as endusefunctions

class ServiceModel(object):
    """Service Submodel
    """
    def __init__(self, data, region_obj, enduse, sector):
        """Constructor of ResidentialModel

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
        self.sector = sector

        self.enduse_object = self.create_enduse(region_obj, data)

    def create_enduse(self, region_obj, data):
        """Create enduse for service sector

        Arguments
        ----------
        region_obj : object
            Region
        data : dict
            Data container

        Returns
        -------
        enduse_object : dict
            Object of an enduse
        """
        # Add enduse to ServiceSector
        enduse_object = endusefunctions.Enduse(
            region_name=self.region_name,
            data=data,
            enduse=self.enduse,
            sector=self.sector,
            fuel=region_obj.ss_enduses_sectors_fuels[self.sector][self.enduse],
            tech_stock=region_obj.ss_tech_stock,
            heating_factor_y=region_obj.ss_heating_factor_y,
            cooling_factor_y=region_obj.ss_cooling_factor_y,
            fuel_switches=data['assumptions']['ss_fuel_switches'],
            service_switches=data['assumptions']['ss_service_switches'],
            fuel_tech_p_by=data['assumptions']['ss_fuel_tech_p_by'][self.enduse],
            tech_increased_service=data['assumptions']['ss_tech_increased_service'],
            tech_decreased_share=data['assumptions']['ss_tech_decreased_share'],
            tech_constant_share=data['assumptions']['ss_tech_constant_share'],
            installed_tech=data['assumptions']['ss_installed_tech'][self.enduse],
            sig_param_tech=data['assumptions']['ss_sig_param_tech'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['ss_model'],
            regional_lp_stock=region_obj.ss_load_profiles,
            dw_stock=data['ss_dw_stock']
        )

        return enduse_object
