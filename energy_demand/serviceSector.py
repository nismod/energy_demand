class ServiceSectorClass(object):
    """
    """
    def __init__(self, sector_name, data):
        """Constructor of ServiceSector
        """
        print("Generate Sector: " + str(sector_name))
        self.sector_name = sector_name
        self.fuels_all_enduses = data['fuel_raw_data_service_enduses'][sector_name]


        # Summing
        ##self.summ_enduses_across_all_sectors()


    def summ_enduses_across_all_sectors(self):

        # Iterate enduses
        #ServiceSectorClass.setattr(summed_enduse)
        pass