"""Industry Submodel
"""
import energy_demand.enduse as endusefunctions

class IndustryModel(object):
    """Industry Submodel
    """
    def __init__(self, data, region_object, enduse_name, sector):
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
        self.sector_name = sector
        self.fuels_all_enduses = data['is_fueldata_disagg'][self.reg_name][self.sector_name]
        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):
        """Create enduse for industry sector
        """
        industry_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            sector=self.sector_name,
            enduse_fuel=self.fuels_all_enduses[self.enduse_name],
            tech_stock=region_object.is_tech_stock,
            heating_factor_y=region_object.ss_heating_factor_y, # from service
            cooling_factor_y=region_object.ss_cooling_factor_y, # from service
            fuel_switches=data['assumptions']['is_fuel_switches'],
            service_switches=data['assumptions']['is_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['is_fuel_enduse_tech_p_by'][self.enduse_name],
            service_tech_by_p=data['assumptions']['is_service_tech_by_p'][self.enduse_name],
            tech_increased_service=data['assumptions']['is_tech_increased_service'],
            tech_decreased_share=data['assumptions']['is_tech_decreased_share'],
            tech_constant_share=data['assumptions']['is_tech_constant_share'],
            installed_tech=data['assumptions']['is_installed_tech'],
            sig_param_tech=data['assumptions']['is_sig_param_tech'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['is_model'],
            dw_stock=data['ss_dw_stock'], #INDUSTRY STOCK?
            load_profiles=region_object.is_load_profiles
        )

        return industry_object
