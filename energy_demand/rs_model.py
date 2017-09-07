"""

Residential Submodel
====================

The residential submodule models energy demand
for the residential sector.
"""
import energy_demand.enduse as endusefunctions

class ResidentialModel(object):
    """Residential Submodel
    """
    def __init__(self, data, region_object, enduse, sector):
        """Constructor of ResidentialModel

        Arguments
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse : string
            Enduse
        enduse : sector
            sector
        """
        self.region_name = region_object.region_name
        self.enduse = enduse
        self.sector = sector
        self.enduse_object = self.create_enduse(
            region_object,
            data
            )

        #TODO LATER ON: SUMMARY ACROSS AL SECTORS (to save on memory)
        #self.enduse_object_aggregated_across_all_sectors

    def create_enduse(self, region_object, data):
        """Create enduse objects and add to list

        Arguments
        ----------
        region_object : object
            Region
        data : dict
            Data container

        Returns
        -------
        enduse_object : dict
            Object of an enduse
        """
        enduse_object = endusefunctions.Enduse(
            region_name=self.region_name,
            data=data,
            enduse=self.enduse,
            sector=self.sector,
            fuel=region_object.rs_enduses_fuel[self.enduse],
            tech_stock=region_object.rs_tech_stock,
            heating_factor_y=region_object.rs_heating_factor_y,
            cooling_factor_y=region_object.rs_cooling_factor_y,
            fuel_switches=data['assumptions']['rs_fuel_switches'],
            service_switches=data['assumptions']['rs_service_switches'],
            fuel_tech_p_by=data['assumptions']['rs_fuel_tech_p_by'][self.enduse],
            tech_increased_service=data['assumptions']['rs_tech_increased_service'],
            tech_decreased_share=data['assumptions']['rs_tech_decreased_share'],
            tech_constant_share=data['assumptions']['rs_tech_constant_share'],
            installed_tech=data['assumptions']['rs_installed_tech'],
            sig_param_tech=data['assumptions']['rs_sig_param_tech'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['rs_model'],
            regional_profile_stock=region_object.rs_load_profiles,
            dw_stock=data['rs_dw_stock']
            )

        return enduse_object
