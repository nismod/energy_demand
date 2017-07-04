import energy_demand.enduse as class_enduse
import energy_demand.enduse as endusefunctions

# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

class ServiceModel(object):

    def __init__(self, data, region_object, enduse_name, sector):
        """Constructor of ResidentialModel
        """
        self.reg_name = region_object.reg_name
        self.enduse_name = enduse_name
        self.sector_name = sector
        self.fuels_all_enduses = data['ss_fueldata_disagg'][self.reg_name][self.sector_name]

        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):

        #print("...Create Enduse {} in sector {} in Region {}".format(self.enduse_name, self.sector_name, reg_name))
        # Enduse specific parameters
        if self.enduse_name in data['assumptions']['enduse_space_heating']:
            enduse_peak_yd_factor = region_object.reg_peak_yd_heating_factor
        elif self.enduse_name in data['assumptions']['enduse_space_cooling']:
            enduse_peak_yd_factor = region_object.reg_peak_yd_cooling_factor
        else:
            enduse_peak_yd_factor = data['ss_shapes_yd'][self.sector_name][self.enduse_name]['shape_peak_yd_factor'] #[enduse] # NEW
        # Add enduse to ServiceSector
        service_object = endusefunctions.Enduse(
            reg_name=self.reg_name,
            data=data,
            enduse=self.enduse_name,
            enduse_fuel=self.fuels_all_enduses[self.enduse_name],
            tech_stock=region_object.ss_tech_stock,
            heating_factor_y=region_object.ss_heating_factor_y,
            cooling_factor_y=region_object.ss_cooling_factor_y,
            enduse_peak_yd_factor=enduse_peak_yd_factor,
            fuel_switches=data['assumptions']['ss_fuel_switches'],
            service_switches=data['assumptions']['ss_service_switches'],
            fuel_enduse_tech_p_by=data['assumptions']['ss_fuel_enduse_tech_p_by'],
            service_tech_by_p=data['assumptions']['ss_service_tech_by_p'],
            tech_increased_service=data['assumptions']['ss_tech_increased_service'],
            tech_decreased_share=data['assumptions']['ss_tech_decreased_share'],
            tech_constant_share=data['assumptions']['ss_tech_constant_share'],
            installed_tech=data['assumptions']['ss_installed_tech'],
            sig_param_tech=data['assumptions']['ss_sig_param_tech'],
            data_shapes_yd=data['ss_shapes_yd'][self.sector_name],
            data_shapes_dh=data['ss_shapes_dh'][self.sector_name],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['service_sector'],
            dw_stock=data['ss_dw_stock']
        )

        return service_object

class ServiceSector(object):
    """Service Sector Class
    """
    def __init__(self, reg_name, sector_name, data, tech_stock, heating_factor_y, cooling_factor_y, reg_peak_yd_heating_factor, reg_peak_yd_cooling_factor, fuels_all_enduses):
        """Constructor of ServiceSector
        """
        print("...Generate Sector: " + str(sector_name))
        self.sector_name = sector_name
        self.fuels_all_enduses = fuels_all_enduses[sector_name]

        # Set all endueses of service sector as attribute to sector
        self.create_enduses_service(
            data,
            reg_name,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            reg_peak_yd_heating_factor,
            reg_peak_yd_cooling_factor
            )

    def create_enduses_service(self, data, reg_name, tech_stock, heating_factor_y, cooling_factor_y, reg_peak_yd_heating_factor, reg_peak_yd_cooling_factor):
        """Enduse services across all sectors

        Parameters
        ----------
        ff : list
            ff
        ff : dict
            ff
        """
        for enduse in data['ss_all_enduses']:
            print("...Create Enduse {} in sector {} in Region {}".format(enduse, self.sector_name, reg_name))

            # Enduse specific parameters
            if enduse in data['assumptions']['enduse_space_heating']:
                enduse_peak_yd_factor = reg_peak_yd_heating_factor
            elif enduse in data['assumptions']['enduse_space_cooling']:
                enduse_peak_yd_factor = reg_peak_yd_cooling_factor
            else:
                enduse_peak_yd_factor = data['ss_shapes_yd'][self.sector_name][enduse]['shape_peak_yd_factor'] #[enduse] # NEW

            # Add enduse to ServiceSector
            ServiceSector.__setattr__(
                self,
                enduse,

                class_enduse.Enduse(
                    reg_name=reg_name,
                    data=data,
                    enduse=enduse,
                    enduse_fuel=self.fuels_all_enduses[enduse],
                    tech_stock=tech_stock,
                    heating_factor_y=heating_factor_y,
                    cooling_factor_y=cooling_factor_y,
                    enduse_peak_yd_factor=enduse_peak_yd_factor,
                    fuel_switches=data['assumptions']['ss_fuel_switches'],
                    service_switches=data['assumptions']['ss_service_switches'],
                    fuel_enduse_tech_p_by=data['assumptions']['ss_fuel_enduse_tech_p_by'],
                    service_tech_by_p=data['assumptions']['ss_service_tech_by_p'],
                    tech_increased_service=data['assumptions']['ss_tech_increased_service'],
                    tech_decreased_share=data['assumptions']['ss_tech_decreased_share'],
                    tech_constant_share=data['assumptions']['ss_tech_constant_share'],
                    installed_tech=data['assumptions']['ss_installed_tech'],
                    sig_param_tech=data['assumptions']['ss_sig_param_tech'],
                    data_shapes_yd=data['ss_shapes_yd'][self.sector_name],
                    data_shapes_dh=data['ss_shapes_dh'][self.sector_name],
                    enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['service_sector'],
                    dw_stock=data['ss_dw_stock']
                    )
            )
