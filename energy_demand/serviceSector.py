import energy_demand.enduseClass as class_enduse

class ServiceSectorClass(object):
    """Service Sector Class
    """
    def __init__(self, reg_name, sector_name, data, tech_stock, heating_factor_y, cooling_factor_y, reg_peak_yd_heating_factor, reg_peak_yd_cooling_factor):
        """Constructor of ServiceSector
        """
        print("Generate Sector: " + str(sector_name))
        self.sector_name = sector_name
        self.fuels_all_enduses = data['ss_fuel_raw_data_enduses'][sector_name]

        # Get all service enduses
        ss_all_enduses = data['ss_all_enduses']

        # Att endueses as attribute to service sector
        self.create_enduses_service(
            ss_all_enduses,
            data,
            reg_name,
            tech_stock,
            heating_factor_y,
            cooling_factor_y,
            reg_peak_yd_heating_factor,
            reg_peak_yd_cooling_factor
            )

    def create_enduses_service(self, enduses, data, reg_name, tech_stock, heating_factor_y, cooling_factor_y, reg_peak_yd_heating_factor, reg_peak_yd_cooling_factor):
        """Enduse services across all sectors

        Parameters
        ----------
        ff : list
            ff
        ff : dict
            ff
        """
        for enduse in enduses:

            # Enduse specific parameters
            if enduse == 'ss_space_heating':
                enduse_peak_yd_factor = reg_peak_yd_heating_factor # Regional yd factor for heating
            elif enduse == 'ss_space_cooling': #TODO: MAKE SHARED LIST FOR ALL HEATING ENDUSES
                enduse_peak_yd_factor = reg_peak_yd_cooling_factor # Regional yd factor for cooling
            else:
                enduse_peak_yd_factor = data['ss_shapes_yd'][self.sector_name][enduse]['shape_peak_yd_factor']

            print(" ")
            print("-------------------")
            print("Create Enduse {} in sector {} in Region {}".format(enduse, self.sector_name, reg_name))
            print("-------------------")

            # --------------------
            # Add enduse to ServiceSector
            # --------------------
            ServiceSectorClass.__setattr__(
                self,
                enduse,

                class_enduse.EnduseClass(
                    reg_name=reg_name,
                    data=data,
                    enduse=enduse,
                    enduse_fuel=self.fuels_all_enduses[enduse],
                    tech_stock=tech_stock,
                    heating_factor_y=heating_factor_y,
                    cooling_factor_y=cooling_factor_y,
                    enduse_peak_yd_factor=enduse_peak_yd_factor,
                    fuel_switches=data['assumptions']['ss_service_switches'],
                    service_switches=data['assumptions']['ss_service_switches'],
                    fuel_enduse_tech_p_by=data['assumptions']['ss_fuel_enduse_tech_p_by'],
                    service_tech_by_p=data['assumptions']['ss_service_tech_by_p'],
                    tech_increased_service=data['assumptions']['ss_tech_increased_service'],
                    tech_decreased_share=data['assumptions']['ss_tech_decreased_share'],
                    tech_constant_share=data['assumptions']['ss_tech_constant_share'],
                    installed_tech=data['assumptions']['ss_installed_tech'],
                    sigm_parameters_tech=data['assumptions']['ss_sigm_parameters_tech'],
                    data_shapes_yd=data['ss_shapes_yd'][self.sector_name],
                    data_shapes_dh=data['ss_shapes_dh'][self.sector_name],
                    enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['service_sector'],
                    dw_stock=data['ss_dw_stock']
                    )
            )
