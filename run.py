""" The sectorl model wrapper for smif to run the energy demand mdoel"""

from smif.sector_model import SectorModel
from main import energy_demand_model, load_data

class EDWrapper(SectorModel):

    def simulate(self, decisions, state, data):
        """This method should allow run model with inputs and outputs as arrays

        Arguments
        =========
        decision_variables : x-by-1 :class:`numpy.ndarray`
        """
        # Load Data
        #SIM_PARAM, fuel_type_lu, dwelling_type_lu, reg_pop, fuel_bd_data, csv_temp_2015, hourly_gas_shape, shape_app_elec, shape_hd_gas, bd_app_elec, bd_hd_gas, timesteps_app_bd, timesteps_hd_bd = load_data()
        base_data = load_data()
        # Data Manipulation
        # ...

        # Run Model
        data = {'population': {0: 1000, 1: 2000, 2: 3000}}
        results = energy_demand_model(base_data, data["population"])

        return results

    def extract_obj(self, results):
        """Implement this method to return a scalar value objective function

        This method should take the results from the output of the `simulate`
        method, process the results, and return a scalar value which can be
        used as the objective function

        Arguments
        =========
        results : :class:`dict`
            The results from the `simulate` method

        Returns
        =======
        float
            A scalar component generated from the simulation model results
        """
        pass

#if __name__ == "__main__":
