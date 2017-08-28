"""The sector model wrapper for smif to run the energy demand model
"""
import os

from smif import SpaceTimeValue
from smif.sector_model import SectorModel
from energy_demand.main import energy_demand_model
from energy_demand.read_write_loader import load_data
from energy_demand.assumptions import load_assumptions
from energy_demand.national_dissaggregation import disaggregate_base_demand_for_reg
from energy_demand.dwelling_stock_generator import resid_build_stock

class EDWrapper(SectorModel):
    """Energy Demand Wrapper"""

    def simulate(self, decisions, state, data):
        """This method should allow run model with inputs and outputs as arrays

        Arguments
        =========
        decision_variables : x-by-1 :class:`numpy.ndarray`
        """
        timestep = data['timestep']

        # Population
        pop = {}
        pop[timestep] = {}
        for obs in data['population']:
            pop[timestep][obs.region] = obs.value

        # Fuel prices
        # - corresponds to `data/scenario_and_base_data/lookup_fuel_types.csv`
        #   with `_price` appended to each type
        fuel_price_index = {
            "solid_fuel_price": 0,
            "gas_price": 1,
            "electricity_price": 2,
            "oil_price": 3,
            "heat_sold_price": 4,
            "bioenergy_waste_price": 5,
            "hydrogen_price": 6,
            "future_fuel_price": 7,
        }
        price = {}
        price[timestep] = {}
        for data_key, fuel_type_id in fuel_price_index.items():
            # expect single value (annual/national) for each fuel price
            price[timestep][fuel_type_id] = data[data_key][0].value

        data_external = {
            'population': pop,
            'glob_var': {
                'base_year': timestep,
                'current_yr': timestep,
                'end_yr': timestep
            },
            'fuel_price': price
        }

        # Load data needed for energy demand model
        path_main = os.path.join(os.path.dirname(__file__), 'data')
        base_data = load_data(path_main, data_external)

        # Load assumptions
        base_data = load_assumptions(base_data)

        # Disaggregate national data into regional data
        base_data = disaggregate_base_demand_for_reg(
            base_data, 1, data_external)

        # Generate virtual dwelling stock over whole simulatin period
        base_data = resid_build_stock(
            base_data, base_data['assumptions'], data_external)

        # Run Model
        results = energy_demand_model(base_data, data_external)

        # results will be written to results.yaml by default
        output = {}
        for parameter, results_list in results.items():
            if parameter in ['electricity', 'gas']:
                output[parameter + '_demand'] = [
                    SpaceTimeValue(region_name, hour, demand, units)
                    for region_name, hour, demand, units in results_list
                ]

        return output

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
