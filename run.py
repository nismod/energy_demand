""" The sectorl model wrapper for smif to run the energy demand mdoel"""

from smif.sector_model import SectorModel
from energy_demand.main import energy_demand_model, load_data
from energy_demand.assumptions import load_assumptions
class EDWrapper(SectorModel):
    """Energy Demand Wrapper"""

    def simulate(self, decisions, state, data):
        """This method should allow run model with inputs and outputs as arrays

        Arguments
        =========
        decision_variables : x-by-1 :class:`numpy.ndarray`
        """

        # Load data needed for energy demand model
        base_data = load_data()

        # Load all assumptions
        assumptions_model_run = load_assumptions()

        # Maybe manipulate some more data
        # ...

        # Run Model
        results = energy_demand_model(base_data, assumptions_model_run, data)

        # TODO: write out to csv file or similar

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

if __name__ == "__main__":
    energy_demand = EDWrapper() # Wrapper function

    data_pop = {'population': {0: 3000000, 1: 5300000, 2: 53000000}}
    energy_demand.simulate([], [], data_pop)
