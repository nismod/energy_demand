import energy_demand.enduse as endusefunctions

class ResidentialModel(object):
    """
    """
    def __init__(self, data, region_object, enduse_name):
        """Constructor of ResidentialModel
        """
        self.reg_name = region_object.reg_name
        self.enduse_name = enduse_name
        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):
        """create enduse object
        """
        if self.enduse_name in data['assumptions']['enduse_space_heating']:
            # Regional yd factor for heating
            enduse_peak_yd_factor = region_object.rs_reg_peak_yd_heating_factor

        elif self.enduse_name in data['assumptions']['enduse_space_cooling']:
            # Regional yd factor for cooling
            enduse_peak_yd_factor = region_object.rs_reg_peak_yd_cooling_factor
        else:
            # Get parameters from loaded shapes for enduse
            enduse_peak_yd_factor = data['rs_shapes_yd'][self.enduse_name]['shape_peak_yd_factor']

        enduse_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            enduse_fuel=region_object.rs_enduses_fuel[self.enduse_name],
            tech_stock=region_object.rs_tech_stock,
            heating_factor_y=region_object.rs_heating_factor_y,
            cooling_factor_y=region_object.rs_cooling_factor_y,
            enduse_peak_yd_factor=enduse_peak_yd_factor,
            fuel_switches=data['assumptions']['rs_fuel_switches'],
            service_switches=data['assumptions']['rs_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['rs_fuel_enduse_tech_p_by'],
            service_tech_by_p=data['assumptions']['rs_service_tech_by_p'],
            tech_increased_service=data['assumptions']['rs_tech_increased_service'],
            tech_decreased_share=data['assumptions']['rs_tech_decreased_share'],
            tech_constant_share=data['assumptions']['rs_tech_constant_share'],
            installed_tech=data['assumptions']['rs_installed_tech'],
            sig_param_tech=data['assumptions']['rs_sig_param_tech'],
            data_shapes_yd=data['rs_shapes_yd'],
            data_shapes_dh=data['rs_shapes_dh'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['residential_sector'],
            dw_stock=data['rs_dw_stock']
            )

        return enduse_object
