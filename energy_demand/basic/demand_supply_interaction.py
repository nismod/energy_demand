"""Functions to configure energy demand outputs for supply model
"""
import os
import logging
import numpy as np
import pandas as pd

from energy_demand.basic import date_prop
from energy_demand.basic import testing_functions
from energy_demand.basic import lookup_tables

def constrained_results(
        results_constrained,
        results_unconstrained,
        submodels_names,
        technologies
    ):
    """Prepare results for energy supply model for
    constrained model running mode (no heat is provided but
    technology specific fuel use).
    The results for the supply model are provided aggregated
    as follows:

        { "submodel_fueltype_tech": np.array(regions, timesteps)}

    Because SMIF only takes results in the
    form of {key: np.array(regions, timesteps)}, the key
    needs to contain information about submodel, fueltype,
    and technology. Also these key must be defined in
    the `submodel_model` configuration file.

    Arguments
    ----------
    results_constrained : dict
        Aggregated results in form
        {technology: np.array((sector, region, fueltype, timestep))}
    results_unconstrained : array
        Restuls of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    submodels_names : list
        Names of sectors fur supply model
    technologies : dict
        Technologies

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}

    Note
    -----
    For the fuel demand for CHP plants, the co-generated electricity
    is not included in the demand model. Additional electricity supply
    generated from CHP plants need to be calculated in the supply
    model based on the fuel demand for CHP.
    For CHP efficiency therefore not the overall efficiency is used
    but only the thermal efficiency
    """
    supply_results = {}
    fueltypes = lookup_tables.basic_lookups()['fueltypes']

    #--------------------------------
    # Get all non heating related enduse
    # --------------------------------
    # Substract constrained fuel from nonconstrained (total) fuel
    non_heating_ed = results_unconstrained - sum(results_constrained.values())

    assert not testing_functions.test_if_minus_value_in_array(results_unconstrained)

    # ----------------------------------------
    # Add all constrained results (technology specific results)
    # Aggregate according to submodel, fueltype, technology, region, timestep
    # ----------------------------------------
    for submodel_nr, submodel in enumerate(submodels_names):
        for tech, fuel_tech in results_constrained.items():

            # ----
            # Technological simplifications because of different technology definition
            # and because not all technologies are used in supply model
            # ----
            tech_simplified = model_tech_simplification(tech)
            fueltype_str = technologies[tech].fueltype_str
            fueltype_int = technologies[tech].fueltype_int

            key_name = "{}_{}_{}".format(submodel, fueltype_str, tech_simplified)
            supply_results[key_name] = fuel_tech[submodel_nr][:, fueltype_int, :]

    # ---------------------------------
    # Add non_heating for all fueltypes
    # ---------------------------------
    for submodel_nr, submodel in enumerate(submodels_names):
        for fueltype_str, fueltype_int in fueltypes.items():

            if fueltype_str == 'heat':
                pass #Do not add non_heating demand for fueltype heat
            else:
                key_name = "{}_{}_{}".format(submodel, fueltype_str, "non_heating")
                logging.info("key_name d: " + str(key_name))
                # Add fuel for all regions for specific fueltype
                supply_results[key_name] = non_heating_ed[submodel_nr][:, fueltype_int, :]

    # --------------------------------------------
    # Check whether any entry is smaller than zero
    # --------------------------------------------
    for key_name, values in supply_results.items():
        if testing_functions.test_if_minus_value_in_array(values):
            logging.info("info: {}  {}".format(values, np.sum(values)))
            raise Exception("Error d: Negative entry in results " + str(key_name))

    logging.info("... Prepared results for energy supply model in constrained mode")
    return supply_results

def unconstrained_results(
        results_unconstrained,
        submodels_names
    ):
    """Prepare results for energy supply model for
    unconstrained model running mode (heat is provided).
    The results for the supply model are provided aggregated
    for every submodel, fueltype, region, timestep

    Note
    -----
    Because SMIF only takes results in the
    form of {key: np.aray(regions, timesteps)}, the key
    needs to contain information about submodel and fueltype

    Also these key must be defined in the `submodel_model`
    configuration file

    Arguments
    ----------
    results_unconstrained : array
        Results of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    submodels_names : list
        Names of sectors for supply model

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}
    """
    supply_results = {}
    fueltypes = lookup_tables.basic_lookups()['fueltypes']

    for submodel_nr, submodel in enumerate(submodels_names):
        for fueltype_str, fueltype_int in fueltypes.items():

            # Generate key name (must be defined in `sector_models`)
            key_name = "{}_{}".format(submodel, fueltype_str)

            # Add fueltype specific demand for all regions
            supply_results[key_name] = results_unconstrained[submodel_nr][:, fueltype_int, :]

            assert not testing_functions.test_if_minus_value_in_array(supply_results[key_name])

    logging.info("... Prepared results for energy supply model in unconstrained mode")
    return supply_results

def model_tech_simplification(tech):
    """This function aggregated different technologies
    which are not defined in supply model

    Arguments
    ---------
    tech : str
        Technology

    Returns
    -------
    tech_newly_assigned : str
        Technology newly assigned
    """
    if tech == 'boiler_condensing_gas':
        tech_newly_assigned = 'boiler_gas'
    elif tech == 'boiler_condensing_oil':
        tech_newly_assigned = 'boiler_oil'
    elif tech == 'storage_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    elif tech == 'secondary_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    else:
        tech_newly_assigned = tech

    if tech != tech_newly_assigned:
        logging.debug(
            "Assigned new technology '%s' for '%s' to provide for simplified supply output",
            tech_newly_assigned, tech)

    return tech_newly_assigned

def write_national_results_amman(
        path_folder,
        results_unconstrained,
        regions,
        fueltype_str,
        fuelype_nr,
        year
    ):
    """Write national results of all fueltypes

    Inputs
    ------
    results_unconstrained : array
        (submodel, region, fueltype, periods)
    """
    logging.info("... writing file for amman")

    path = os.path.join(path_folder, "file_AMMAN_{}_{}.csv".format(fueltype_str, year))

    # Sum across all sectors
    sum_across_submodels = results_unconstrained.sum(axis=0)

    # Change ot days
    nr_regs = len(regions)
    nr_fueltypes = sum_across_submodels.shape[1]
    sum_across_regions_days = sum_across_submodels.reshape(nr_regs, nr_fueltypes, 365, 24)

    # Iterate over every hour in year
    rows = []
    for region_nr, region in enumerate(regions):
        for day in range(365):
            row = {'region': region}

            daysum = np.sum(sum_across_regions_days[region_nr][fuelype_nr][day])
            row['day'] = day
            row['demand_GWh'] = daysum

            rows.append(row)

    # Create dataframe
    col_names = ['region', 'day', 'demand_GWh']
    my_df = pd.DataFrame(rows, columns=col_names)

    my_df.to_csv(path, index=False) #Index prevents writing index rows

def write_national_results(
        path_folder,
        results_unconstrained,
        enduse_specific_results,
        fueltype_str,
        fuelype_nr,
        year,
        write_regions=False,
        submodels_names=['residential', 'service', 'industry']
    ):
    """Write national results of all fueltypes

    Input
    ------
    results_unconstrained : array
        (submodel, region, fueltype, periods)
    """
    logging.info("... writing file for modassar")

    path = os.path.join(path_folder, "file_MODASSAR_{}_{}.csv".format(fueltype_str, year))

    # Sum across all regions
    sum_across_regions = results_unconstrained.sum(axis=1)

    rows = []
    for hour in range(8760):

        # Get day and hour
        day_year, hour_day_year = date_prop.convert_h_to_day_year_and_h(hour)

        row = {'year': year, 'hour': hour}

        for submodel_nr, submodel in enumerate(submodels_names):

            # Total energy demand
            ed_submodel_h = sum_across_regions[submodel_nr][fuelype_nr][hour]

            # Space heating related demand for sector
            if submodel_nr == 0:
                space_heating_demand = enduse_specific_results['rs_space_heating'][fuelype_nr][day_year][hour_day_year]
            elif submodel_nr == 1:
                space_heating_demand = enduse_specific_results['ss_space_heating'][fuelype_nr][day_year][hour_day_year]
            else:
                space_heating_demand = enduse_specific_results['is_space_heating'][fuelype_nr][day_year][hour_day_year]

            ed_submodel_heating_h = space_heating_demand
            str_name_heat = "{}_heat".format(submodel)
            row[str_name_heat] = ed_submodel_heating_h

            # Non-heating related demand
            ed_submodel_non_heating_h = ed_submodel_h - space_heating_demand

            str_name_non_heat = "{}_non_heat".format(submodel)

            row[str_name_non_heat] = ed_submodel_non_heating_h

        rows.append(row)

    # Create dataframe
    col_names = [
        'year',
        'hour',
        'residential_non_heat',
        'residential_heat',
        'service_non_heat',
        'service_heat',
        'industry_non_heat',
        'industry_heat']

    my_df = pd.DataFrame(rows, columns=col_names)
    my_df.to_csv(path, index=False) #Index prevents writing index rows

    # Plot national results
    '''validation_enduses.plot_dataframe_function(
        my_df,
        x_column_name='hour',
        y_column_names=['residential_non_heat', 'service_non_heat', 'industry_non_heat'],
        plot_kind='line')'''
