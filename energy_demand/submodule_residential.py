import energy_demand.enduse as endusefunctions

class ResidentialModel(object):
    """
    """
    def __init__(self, data, region_object, enduse_name, sector):
        """Constructor of ResidentialModel

        Parameters
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse_name : string
            Enduse
        """
        self.reg_name = region_object.reg_name
        self.enduse_name = enduse_name
        self.sector_name = sector
        self.enduse_object = self.create_enduse(region_object, data)
        
    def create_enduse(self, region_object, data):
        """Create enduse objects and add to list
        """
        if self.enduse_name in data['assumptions']['enduse_space_heating']:
            enduse_peak_yd_factor = region_object.rs_peak_yd_heating_factor # Regional yd factor for residential space heating

        elif self.enduse_name in data['assumptions']['enduse_space_cooling']:
            enduse_peak_yd_factor = region_object.ss_peak_yd_cooling_factor # Regional yd factor for cooling for service sector
        else:
            # Get parameters from loaded shapes for enduse
            enduse_peak_yd_factor = data['rs_shapes_yd'][self.enduse_name]['shape_peak_yd_factor']

        enduse_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            sector=self.sector_name,
            enduse_fuel=region_object.rs_enduses_fuel[self.enduse_name],
            tech_stock=region_object.rs_tech_stock,
            heating_factor_y=region_object.rs_heating_factor_y,
            cooling_factor_y=region_object.rs_cooling_factor_y,
            enduse_peak_yd_factor=enduse_peak_yd_factor,
            fuel_switches=data['assumptions']['rs_fuel_switches'],
            service_switches=data['assumptions']['rs_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['rs_fuel_enduse_tech_p_by'][self.enduse_name],
            service_tech_by_p=data['assumptions']['rs_service_tech_by_p'][self.enduse_name],
            tech_increased_service=data['assumptions']['rs_tech_increased_service'],
            tech_decreased_share=data['assumptions']['rs_tech_decreased_share'],
            tech_constant_share=data['assumptions']['rs_tech_constant_share'],
            installed_tech=data['assumptions']['rs_installed_tech'],
            sig_param_tech=data['assumptions']['rs_sig_param_tech'],
            data_shapes_yd=data['rs_shapes_yd'],
            data_shapes_dh=data['rs_shapes_dh'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['rs_model'],
            dw_stock=data['rs_dw_stock']
            )

        return enduse_object
