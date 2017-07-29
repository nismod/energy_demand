import energy_demand.enduse as class_enduse
import energy_demand.enduse as endusefunctions

# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

class ServiceModel(object):
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
        sector : string
            Service sector
        """
        self.reg_name = region_object.reg_name
        self.enduse_name = enduse_name
        self.sector_name = sector
        self.fuels_all_enduses = data['ss_fueldata_disagg'][self.reg_name][self.sector_name]

        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):
        """Create enduse for service sector
        """
        #print("...create Enduse {} in sector {} in Region {}".format(self.enduse_name, self.sector_name, reg_name))

        # --------------------------
        # Enduse specific parameters
        # --------------------------
        if self.enduse_name in data['assumptions']['enduse_space_heating']:
            enduse_peak_yd_factor = region_object.ss_peak_yd_heating_factor
        elif self.enduse_name in data['assumptions']['enduse_space_cooling']:
            enduse_peak_yd_factor = region_object.rs_peak_yd_cooling_factor
        else:

            # NEW #Because ventilation is newly created, assign shapes of any other sector for
            '''if self.enduse_name == 'ss_ventilation':
                any_sector = data['ss_sectors'][0]
                enduse_peak_yd_factor = data['ss_shapes_yd'][any_sector]['ss_cooling_ventilation']['shape_peak_yd_factor']

                data['ss_shapes_yd'][self.sector_name]['ss_ventilation'] = {}
                data['ss_shapes_dh'][self.sector_name]['ss_ventilation'] = {}

                data['ss_shapes_yd'][self.sector_name]['ss_ventilation']['shape_non_peak_yd'] = data['ss_shapes_yd'][any_sector]['ss_cooling_ventilation']['shape_non_peak_yd']
                data['ss_shapes_yd'][self.sector_name]['ss_ventilation']['shape_peak_yd_factor'] = data['ss_shapes_yd'][any_sector]['ss_cooling_ventilation']['shape_peak_yd_factor']

                data['ss_shapes_dh'][self.sector_name]['ss_ventilation']['shape_non_peak_dh'] = data['ss_shapes_dh'][any_sector]['ss_cooling_ventilation']['shape_non_peak_dh']
                data['ss_shapes_dh'][self.sector_name]['ss_ventilation']['shape_peak_dh'] = data['ss_shapes_dh'][any_sector]['ss_cooling_ventilation']['shape_peak_dh']
            else:'''
            enduse_peak_yd_factor = data['ss_shapes_yd'][self.sector_name][self.enduse_name]['shape_peak_yd_factor']

        # Add enduse to ServiceSector
        service_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            sector=self.sector_name,
            enduse_fuel=self.fuels_all_enduses[self.enduse_name],
            tech_stock=region_object.ss_tech_stock,
            heating_factor_y=region_object.ss_heating_factor_y,
            cooling_factor_y=region_object.ss_cooling_factor_y,
            enduse_peak_yd_factor=enduse_peak_yd_factor,
            fuel_switches=data['assumptions']['ss_fuel_switches'],
            service_switches=data['assumptions']['ss_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['ss_fuel_enduse_tech_p_by'][self.enduse_name],
            service_tech_by_p=data['assumptions']['ss_service_tech_by_p'][self.enduse_name],
            tech_increased_service=data['assumptions']['ss_tech_increased_service'],
            tech_decreased_share=data['assumptions']['ss_tech_decreased_share'],
            tech_constant_share=data['assumptions']['ss_tech_constant_share'],
            installed_tech=data['assumptions']['ss_installed_tech'],
            sig_param_tech=data['assumptions']['ss_sig_param_tech'],
            data_shapes_yd=data['ss_shapes_yd'][self.sector_name],
            data_shapes_dh=data['ss_shapes_dh'][self.sector_name],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['ss_model'],
            dw_stock=data['ss_dw_stock'],
            load_profiles=region_object.ss_load_profiles
        )

        return service_object
