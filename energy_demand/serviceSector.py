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

        print("eeeeeeeeeeeeeee")
        print(self.fuels_all_enduses)
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
        for enduse in service_enduses:

            '''# Enduse specific parameters
            if enduse == 'service_space_heating' or enduse == 'service_space_heating': #in data['assumptions']['enduse_resid_space_heating']:
                enduse_peak_yd_factor = reg_peak_yd_heating_factor # Regional yd factor for heating
            elif enduse == 'service_space_cooling' or enduse == 'service_space_cooling': #in data['assumptions']['enduse_space_cooling']:
                enduse_peak_yd_factor = reg_peak_yd_cooling_factor # Regional yd factor for cooling
            else:
                #enduse_peak_yd_factor = data['rs_shapes_yd'][enduse]['shape_peak_yd_factor'] # Get parameters from loaded shapes for enduse

                '''
            enduse_peak_yd_factor = 1 #TODO
            print(" ")
            print("-------------------")
            print("Create Enduse in sector  {}".format(self.sector_name))
            print("-------------------")
            print(enduse)
            print(reg_name)
            print(self.fuels_all_enduses[enduse])

            # --------------------
            # Add enduse to region
            # --------------------
            ServiceSectorClass.__setattr__(
                self,
                enduse,

                class_enduse.EnduseClass(
                    reg_name,
                    data,
                    enduse,
                    self.fuels_all_enduses[enduse],
                    tech_stock,
                    heating_factor_y,
                    cooling_factor_y,
                    enduse_peak_yd_factor, # yd factor which is different depending on enduse
                    data['assumptions']['ss_fuel_switches'],
                    data['assumptions']['ss_service_switches'],
                    data['assumptions']['ss_fuel_enduse_tech_p_by'],
                    data['assumptions']['ss_service_tech_by_p'],
                    data['assumptions']['ss_tech_increased_service'],
                    data['assumptions']['ss_tech_decreased_share'],
                    data['assumptions']['ss_tech_constant_share'],
                    data['assumptions']['ss_installed_tech'],
                    data['assumptions']['ss_sigm_parameters_tech'],
                    #data['ss_shapes_resid_yd'],
                    data['rs_shapes_yd'], #TODO CHANGE TO SS data['ss_shapes_dh'][self.sector_name]
                    data['rs_shapes_dh'], #TODO CHANGE TO SS data['ss_shapes_dh'][self.sector_name]
                    data['assumptions']['enduse_overall_change_ey']['service_sector']
                    )
            )
