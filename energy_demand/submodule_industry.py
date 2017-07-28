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
        print("...create Enduse {} in sector {} in Region {}".format(self.enduse_name, self.sector_name, self.reg_name))

        # --------------------------
        # Enduse specific parameters
        # --------------------------
        if self.enduse_name in data['assumptions']['enduse_space_heating']:
            enduse_peak_yd_factor = region_object.ss_peak_yd_heating_factor #Take heating factor from service sector data
        elif self.enduse_name in data['assumptions']['enduse_space_cooling']:
            enduse_peak_yd_factor = region_object.ss_peak_yd_cooling_factor #Take heating factor from service sector data
        else:
            enduse_peak_yd_factor = data['is_shapes_yd'][self.sector_name][self.enduse_name]['shape_peak_yd_factor']

            # Convert enduse_peak_yd_factor into #TODO: IMPROVE
            enduse_peak_yd_factor = (1 / (365))

        # Add enduse to ServiceSector
        industry_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            sector=self.sector_name,
            enduse_fuel=self.fuels_all_enduses[self.enduse_name],
            tech_stock=region_object.is_tech_stock,
            heating_factor_y=region_object.ss_heating_factor_y, # from service
            cooling_factor_y=region_object.ss_cooling_factor_y, # from service
            enduse_peak_yd_factor=enduse_peak_yd_factor,
            fuel_switches=data['assumptions']['is_fuel_switches'],
            service_switches=data['assumptions']['is_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['is_fuel_enduse_tech_p_by'][self.enduse_name],
            service_tech_by_p=data['assumptions']['is_service_tech_by_p'][self.enduse_name],
            tech_increased_service=data['assumptions']['is_tech_increased_service'],
            tech_decreased_share=data['assumptions']['is_tech_decreased_share'],
            tech_constant_share=data['assumptions']['is_tech_constant_share'],
            installed_tech=data['assumptions']['is_installed_tech'],
            sig_param_tech=data['assumptions']['is_sig_param_tech'],
            data_shapes_yd=data['is_shapes_yd'][self.sector_name],
            data_shapes_dh=data['is_shapes_dh'][self.sector_name],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['is_model'],
            dw_stock=data['ss_dw_stock'] #INDUSTRY STOCK?
        )

        return industry_object
