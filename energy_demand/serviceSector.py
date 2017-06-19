import energy_demand.enduseClass as class_enduse

class ServiceSectorClass(object):
    """Service Sector Class
    """
    def __init__(self, reg_name, sector_name, data, tech_stock, heating_factor_y, cooling_factor_y):
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
            cooling_factor_y
            )

        # Summing
        ##self.summ_enduses_across_all_sectors()

    def summ_enduses_across_all_sectors(self):

        # Iterate enduses
        #ServiceSectorClass.setattr(summed_enduse)
        pass

    def create_enduses_service(self, service_enduses, data, reg_name, tech_stock, heating_factor_y, cooling_factor_y):
        """

        Parameters
        ----------
        ff : list
            ff
        ff : dict
            ff
        """
        for service_enduse in service_enduses:

            '''# Enduse specific parameters
            if service_enduse == 'service_space_heating' or service_enduse == 'service_space_heating': #in data['assumptions']['enduse_resid_space_heating']:
                enduse_peak_yd_factor = reg_peak_yd_heating_factor # Regional yd factor for heating
            elif service_enduse == 'service_space_cooling' or service_enduse == 'service_space_cooling': #in data['assumptions']['enduse_space_cooling']:
                enduse_peak_yd_factor = reg_peak_yd_cooling_factor # Regional yd factor for cooling
            else:
                #enduse_peak_yd_factor = data['shapes_resid_yd'][service_enduse]['shape_peak_yd_factor'] # Get parameters from loaded shapes for enduse

                '''
            #TODO
            enduse_peak_yd_factor = 1
            print(" ")
            print("-------------------")
            print("Create Enduse in sector  {}".format(self.sector_name))
            print("-------------------")
            print(service_enduse)
            print(reg_name)

            # --------------------
            # Add enduse to region
            # --------------------
            ServiceSectorClass.__setattr__(
                self,
                service_enduse,

                class_enduse.EnduseResid(
                    reg_name,
                    data,
                    service_enduse,
                    self.fuels_all_enduses[service_enduse],
                    tech_stock,
                    heating_factor_y,
                    cooling_factor_y,
                    enduse_peak_yd_factor # yd factor which is different depending on enduse
                    )
                )
