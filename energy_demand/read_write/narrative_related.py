"""Functions handling the narratives
"""
import pandas as pd
import math
from collections import defaultdict

from energy_demand.basic import lookup_tables

def get_all_sectors_of_narratives(narratives):
    """Get all defined sectors of all narratives

    ARguments
    --------
    narratives : list
        All defined narratives

    Returns
    -------
    all_sectors : list
        All sectors
    """
    all_sectors = set()
    for narrative in narratives:
        all_sectors.add(narrative['sector'])
    all_sectors = list(all_sectors)

    return all_sectors

def get_sector_narrative(sector_to_match, switches):
    """Get all switches of a sector if the switches are
    defined specifically for a sector. If the switches are
    not specifically for a sector, return all switches

    Arguments
    ----------
    sector_to_match : int
        Sector to find switches
    switches : list
        Switches

    Returns
    -------
    switches : list
        Switches of sector
    """
    if sector_to_match is True:
        return switches
    else:
        switches_out = []

        for switch in switches:

            if switch['sector'] == sector_to_match:
                switches_out.append(switch)
            elif not switch['sector']: # Not defined specifically for sectors and append all
                switches_out.append(switch)
            else:
                pass

        return switches_out

def crit_dim_var(var):
    """Check if nested dict or not

    Arguments
    ---------
    var : dict
        Dictionary to test wheter single or multidimensional parameter

    Returns
    -------
    single_dimension : bool
        True: Single dimension, False: Multidimensional parameter
    """
    if type(var) is list:# or 'dummy_sector':
        single_dimension = True
    else:
        try:
            for entry in var:
                # If list is in ndested dict, then multidimensional
                if type(var[entry]) is list:
                    single_dimension = False
                    break
                else:
                    # IF no keys, then fail and thus single dimensional
                    var[entry].keys()

            single_dimension = False
        except AttributeError:
            single_dimension = True

    return single_dimension

def read_from_narrative(narratives):
    """Read from narratives the defined
    value for the last defined timestep

    Arguments
    ---------
    narratives : lives
        Narratives

    Returns
    -------
    last_value : float
        Value of last defined timestep narrative
    """
    last_year = 0
    for narrative in narratives:
        if narrative['end_yr'] > last_year:
            last_value = narrative['value_ey']
            last_year = narrative['end_yr']

    return last_value

def default_narrative(
        end_yr,
        value_by,
        value_ey,
        diffusion_choice='linear',
        sig_midpoint=0,
        sig_steepness=1,
        base_yr=2015,
        regional_specific=True
    ):
    """Create a default single narrative with a single timestep

    E.g. from value 0.2 in 2015 to value 0.5 in 2050

    Arguments
    ----------
    end_yr : int
        End year of narrative
    value_by : float
        Value of start year of narrative
    value_ey : float
        Value at end year of narrative
    diffusion_choice : str, default='linear'
        Wheter linear or sigmoid
    sig_midpoint : float, default=0
        Sigmoid midpoint
    sig_steepness : float, default=1
        Sigmoid steepness
    base_yr : int
        Base year
    regional_specific : bool
        If regional specific or not

    Returns
    -------
    container : list
        List with narrative
    """
    default_narrative = [{
        'base_yr': base_yr,
        'end_yr': end_yr,
        'value_by': value_by,
        'value_ey': value_ey,
        'diffusion_choice': diffusion_choice,
        'sig_midpoint': sig_midpoint,
        'sig_steepness': sig_steepness,
        'regional_specific': regional_specific}]

    return default_narrative

def autocomplete(parameter_narratives, simulation_base_yr, sub_param_crit):
    """
    """
    autocomplet_param_narr = defaultdict(dict)

    for sub_param_name, narratives_sector in parameter_narratives.items():
        for sector, narratives in narratives_sector.items():
            autocomplet_param_narr[sub_param_name][sector] = []

            switches_to_create_narrative = get_sector_narrative(sector, narratives)

            # Get all years of switches_to_create_narrative
            all_yrs = []
            for narrative in switches_to_create_narrative:
                all_yrs.append(narrative['end_yr'])

            all_yrs.sort()

            for year_cnt, year in enumerate(all_yrs):
                for narrative in switches_to_create_narrative:
                    if narrative['end_yr'] == year:
                        yr_narrative = narrative
                        break

                # Add missing entries to narrative
                if year_cnt == 0:
                    # Update
                    yr_narrative['base_yr'] = simulation_base_yr
                    yr_narrative['value_by'] = narrative['default_by']

                    # previous value
                    previous_yr = narrative['end_yr']
                    previous_value = narrative['value_ey']
                else:
                    # Update
                    yr_narrative['base_yr'] = previous_yr
                    yr_narrative['value_by'] = previous_value

                    # previous value
                    previous_yr = narrative['end_yr']
                    previous_value = narrative['value_ey']

                autocomplet_param_narr[sub_param_name][sector].append(yr_narrative)

    # Remove all dummy sector
    autocomplet_param_narr_new = defaultdict(dict)

    for param_name, sector_data in autocomplet_param_narr.items():
        for sector, data in sector_data.items():
            if sector == 'dummy_sector':
                autocomplet_param_narr_new[param_name] = data
            else:
                autocomplet_param_narr_new[param_name][sector] = data

    autocomplet_param_narr = dict(autocomplet_param_narr_new)

    # If only single dimension parameter, remove dummy mutliparameter name
    if not sub_param_crit:
        try:
            autocomplet_param_narr = autocomplet_param_narr['dummy_single_param']
        except:
            pass

    return autocomplet_param_narr

def read_user_defined_param(
        df,
        simulation_base_yr,
        simulation_end_yr,
        default_streategy_var,
        var_name
    ):
    """Read in user defined narrative parameters
    """
    parameter_narratives = {}
    single_param_narratives = {}

    lookups = lookup_tables.basic_lookups()

    # End uses
    columns = list(df.columns)

    if 'enduses' in columns:
        sub_param_crit = True
    else:
        sub_param_crit = False

    if len(list(df.columns)) == 1:
        single_dim_param = True
    else:
        single_dim_param = False

    if single_dim_param:

        # Read single dimension param and create single step narrative
        single_step_narrative = {}
        single_step_narrative['sector'] = 'dummy_sector'
        single_step_narrative['default_value'] = default_streategy_var['default_value']
        single_step_narrative['value_ey'] = float(df[var_name][0])
        single_step_narrative['end_yr'] = simulation_end_yr
        single_step_narrative['base_yr'] = simulation_base_yr
        single_step_narrative['value_by'] = default_streategy_var['default_value']
        single_step_narrative['regional_specific'] = default_streategy_var['regional_specific']
        single_step_narrative['diffusion_choice'] = 'linear'
        single_param_narratives = [single_step_narrative]

        return single_param_narratives
    else:
        # Read multidmensional param
        if sub_param_crit:
            enduses = set(df['enduses'].values)
            for enduse in enduses:
                parameter_narratives[enduse] = {}

                # All rows of enduse
                df_enduse = df.loc[df['enduses'] == enduse]

                # Get all sectors and years
                sectors = set()
                end_yrs = set()

                for i in df_enduse.index:
                    try:
                        sector = df_enduse.at[i, 'sector']
                        sectors.add(sector)
                    except:
                        pass

                    try:
                        end_yr = int(df_enduse.at[i, 'end_yr'])
                        end_yrs.add(end_yr)
                    except:
                        pass
                if list(sectors) == []:

                    for end_yr in end_yrs:
                        try:
                            _ = default_streategy_var[enduse]
                            defined_in_model = True
                        except:
                            #print("... not defined in model")
                            defined_in_model = False

                        if defined_in_model:
                            narrative = {}
                            narrative['sector'] = 'dummy_sector'
                            narrative['end_yr'] = end_yr
                            narrative['sig_midpoint'] = 0
                            narrative['sig_steepness'] = 1
                            narrative['regional_specific'] = default_streategy_var[enduse]['regional_specific']
                            narrative['default_by'] = default_streategy_var[enduse]['default_value']

                            for _index, row in df_enduse.iterrows():

                                try:
                                    interpolation_params = row['interpolation_params']
                                except:
                                    # Generic fuel switch
                                    interpolation_params = row['param_generic_fuel_switch']

                                if interpolation_params == 'diffusion_choice':
                                    int_diffusion_choice = float(row[var_name])
                                    narrative['diffusion_choice'] = lookups['diffusion_type'][int_diffusion_choice]
                                else:
                                    narrative[interpolation_params] = float(row[var_name])

                            # Add narrative
                            try:
                                parameter_narratives[enduse][narrative['sector']].append(narrative)
                            except KeyError:
                                parameter_narratives[enduse][narrative['sector']] = [narrative]
                else:
                    # If setctor specific, this needs to be implemented
                    pass
        else:
            sectors = set()
            end_yrs = set()

            for i in df.index:
                try:
                    sector = df.at[i, 'sector']
                    sectors.add(sector)
                except:
                    pass
                try:
                    end_yr = int(df.at[i, 'end_yr'])
                    end_yrs.add(end_yr)
                except:
                    pass

            if list(sectors) == []:
                parameter_narratives['dummy_single_param'] = {}

                for end_yr in end_yrs:
                    narrative = {}
                    narrative['sector'] = 'dummy_sector'
                    narrative['end_yr'] = end_yr
                    narrative['sig_midpoint'] = 0
                    narrative['sig_steepness'] = 1
                    narrative['regional_specific'] = default_streategy_var['regional_specific']
                    narrative['default_by'] = default_streategy_var['default_value']

                    for _index, row in df.iterrows():

                        interpolation_params = row['interpolation_params']

                        if interpolation_params == 'diffusion_choice':
                            lookups = lookup_tables.basic_lookups()
                            int_diffusion_choice = int(row[var_name])
                            narrative['diffusion_choice'] = lookups['diffusion_type'][int_diffusion_choice]
                        else:
                            narrative[interpolation_params] = float(row[var_name])

                    # Add narrative
                    try:
                        parameter_narratives['dummy_single_param'][narrative['sector']].append(narrative)
                    except (KeyError, AttributeError):
                        parameter_narratives['dummy_single_param'][narrative['sector']] = [narrative]
            else:
                # Needs to be implemented in case sector specific
                pass

        parameter_narratives = autocomplete(
            parameter_narratives,
            simulation_base_yr,
            sub_param_crit)

        return parameter_narratives
