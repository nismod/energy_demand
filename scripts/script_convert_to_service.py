"""
"""
#path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-7])
import os
import sys
from datetime import date
from energy_demand.assumptions import assumptions
from energy_demand.read_write import data_loader
from energy_demand.basic import date_handling
import numpy as np
from energy_demand.initalisations import initialisations as init
from energy_demand.technologies import technologies_related
print("... start script {}".format(os.path.basename(__file__)))

def write_service_fueltype_by_p(path_to_txt, data):
    """Writ
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format(
        'service', 'fueltype', 'service_p') + '\n'
              )

    for service, fueltypes in data.items():
        for fueltype, service_p in fueltypes.items():
                file.write("{}, {}, {}".format(
                    service, fueltype, float(service_p)) + '\n')

    file.close()

    return

def write_service_fueltype_tech_by_p(path_to_txt, data):
    """Writ
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}".format(
        'service', 'fueltype', 'technology', 'service_p') + '\n'
              )

    for service, fueltype_tech in data.items():
        for fueltype, tech_list in fueltype_tech.items():
            if tech_list == {}:
                file.write("{}, {}, {}, {}".format(
                    service, fueltype, "None", 0) + '\n') #None and 0
            else:
                for tech, service_p in tech_list.items():
                    file.write("{}, {}, {}, {}".format(
                        service, fueltype, tech, float(service_p)) + '\n')

    file.close()

    return

def write_service_tech_by_p(path_to_txt, data):
    """Writ
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format(
        'enduse', 'technology', 'service_p') + '\n'
              )

    for enduse, technologies in data.items():
        for tech, service_p in technologies.items():
            file.write("{}, {}, {}".format(
                str.strip(enduse), str.strip(tech), float(service_p)) + '\n'
                      )

    file.close()

    return


def init_nested_dict_brackets(first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
            nested_dict[first_level_key][second_level_key] = {}

    return nested_dict

def init_nested_dict_zero(first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
            nested_dict[first_level_key][second_level_key] = 0

    return nested_dict

def init_dict_brackets(first_level_keys):
    """Initialise a  dictionary with one level

    Parameters
    ----------
    first_level_keys : list
        First level data

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = {}

    for first_key in first_level_keys:
        one_level_dict[first_key] = {}

    return one_level_dict

def ss_sum_fuel_enduse_sectors(ss_fuel_raw_data_enduses, ss_enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse
    """
    aggregated_fuel_enduse = {}

    for enduse in ss_enduses:
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes))

    # Iterate and sum fuel per enduse
    for _, fuels_sector in ss_fuel_raw_data_enduses.items():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse

def get_service_fueltype_tech(technology_list, hybrid_technologies, lu_fueltypes, fuel_p_tech_by, fuels, tech_stock):
    """Calculate total energy service percentage of each technology and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    lu_fueltypes : dict
        Fueltypes
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of base year (region dependent)

    Return
    ------
    service_tech_by_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p : dict
        Percentage of energy service witin a fueltype for all technologies with this fueltype for base year
    service_fueltype_by_p : dict
        Percentage of energy service per fueltype

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region.
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.

    Because regional efficiencies may differ within regions, the fuel distribution within
    the fueltypes may also differ
    """
    # Energy service per technology for base year
    service = init_nested_dict_brackets(fuels, lu_fueltypes.values())
    service_tech_by_p = init_dict_brackets(fuels) # Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p = init_nested_dict_brackets(fuels, lu_fueltypes.values()) # Percentage of service per technologies within the fueltypes
    service_fueltype_by_p = init_nested_dict_zero(service_tech_by_p.keys(), range(len(lu_fueltypes))) # Percentage of service per fueltype

    for enduse, fuel in fuels.items():

        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_service_fueltype = 0

            #Initiate NEW
            for tech in fuel_p_tech_by[enduse][fueltype]:
                service[enduse][fueltype][tech] = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype
                #print("------------Tech: {}  {} ".format(fuel_alltech_by, fuel_fueltype))

                # Get technology type
                tech_type = technologies_related.get_tech_type(tech, technology_list)

                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
                if tech_type == 'hybrid_tech':
                    eff_tech = hybrid_technologies[tech]['average_efficiency_national_by']
                elif tech_type == 'heat_pump':
                    eff_tech = technologies_related.eff_heat_pump(
                        temp_diff=10,
                        efficiency_intersect=tech_stock[tech]['eff_by']
                        )
                elif tech_type == 'dummy_tech':
                    eff_tech = 1
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech
                print("SERVICE NATIONA LCALCUATION: {} {} {}  {}  {}".format(enduse, tech, fuel_tech, eff_tech, service_fueltype_tech))

                # Add energy service demand
                service[enduse][fueltype][tech] += service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = 0
                    service_fueltype_by_p[enduse][fueltype] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = (1 / tot_service_fueltype) * service[enduse][fueltype][tech]
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = init.sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = (1 / total_service) * service_tech
                #print("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))

        print("Total Service base year for enduse {}  :  {}".format(enduse, total_service))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = (1.0 / total_service) * service_fueltype_by_p[enduse][fueltype]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p



base_data = {}
base_data['sim_param'] = {}
base_data['sim_param']['base_yr'] = 2015
base_data['sim_param']['end_yr'] = 2020
base_data['sim_param']['sim_years_intervall'] = 5 # Make calculation only every X year
base_data['sim_param']['sim_period'] = range(base_data['sim_param']['base_yr'], base_data['sim_param']['end_yr']  + 1, base_data['sim_param']['sim_years_intervall'])
base_data['sim_param']['sim_period_yrs'] = int(base_data['sim_param']['end_yr']  + 1 - base_data['sim_param']['base_yr'])
base_data['sim_param']['curr_yr'] = base_data['sim_param']['base_yr']
base_data['sim_param']['list_dates'] = date_handling.fullyear_dates(
    start=date(base_data['sim_param']['base_yr'], 1, 1),
    end=date(base_data['sim_param']['base_yr'], 12, 31))

# Paths
path_main = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-7])
local_data_path = r'Y:\01-Data_NISMOD\data_energy_demand'

# -----------------------------------------------------
# Load data and assumptions
# ------------------------------------------------------
base_data['path_dict'] = data_loader.load_paths(path_main, local_data_path)
base_data = data_loader.load_data_lookup_data(base_data)
base_data = data_loader.load_fuels(base_data)
base_data['assumptions'] = assumptions.load_assumptions(base_data)

# RESIDENTIAL: Convert base year fuel input assumptions to energy service
rs_service_tech_by_p, rs_service_fueltype_tech_by_p, rs_service_fueltype_by_p = get_service_fueltype_tech(
    base_data['assumptions']['technology_list'],
    base_data['assumptions']['hybrid_technologies'],
    base_data['lu_fueltype'],
    base_data['assumptions']['rs_fuel_tech_p_by'],
    base_data['rs_fuel_raw_data_enduses'],
    base_data['assumptions']['technologies']
    )

# SERVICE: Convert base year fuel input assumptions to energy service
fuels_aggregated_across_sectors = ss_sum_fuel_enduse_sectors(
    base_data['ss_fuel_raw_data_enduses'],
    base_data['ss_all_enduses'],
    base_data['nr_of_fueltypes'])
ss_service_tech_by_p, ss_service_fueltype_tech_by_p, ss_service_fueltype_by_p = get_service_fueltype_tech(
    base_data['assumptions']['technology_list'],
    base_data['assumptions']['hybrid_technologies'],
    base_data['lu_fueltype'],
    base_data['assumptions']['ss_fuel_tech_p_by'],
    fuels_aggregated_across_sectors,
    base_data['assumptions']['technologies']
    )

# INDUSTRY
fuels_aggregated_across_sectors = ss_sum_fuel_enduse_sectors(
    base_data['is_fuel_raw_data_enduses'],
    base_data['is_all_enduses'],
    base_data['nr_of_fueltypes'])
is_service_tech_by_p, is_service_fueltype_tech_by_p, is_service_fueltype_by_p = get_service_fueltype_tech(
    base_data['assumptions']['technology_list'],
    base_data['assumptions']['hybrid_technologies'],
    base_data['lu_fueltype'],
    base_data['assumptions']['is_fuel_tech_p_by'],
    fuels_aggregated_across_sectors,
    base_data['assumptions']['technologies']
    )

# ------------------
# Write to csv files
# ------------------
CSV_rs_service_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\rs_service_tech_by_p.csv')
CSV_rs_service_fueltype_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\rs_service_fueltype_tech_by_p.csv')
CSV_rs_service_fueltype_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\rs_service_fueltype_by_p.csv')
CSV_ss_service_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\ss_service_tech_by_p.csv')
CSV_ss_service_fueltype_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\ss_service_fueltype_tech_by_p.csv')
CSV_ss_service_fueltype_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\ss_service_fueltype_by_p.csv')
CSV_is_service_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\is_service_tech_by_p.csv')
CSV_is_service_fueltype_tech_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\is_service_fueltype_tech_by_p.csv')
CSV_is_service_fueltype_by_p = os.path.join(
    os.path.dirname(__file__), '..', r'data\data_scripts\services\is_service_fueltype_by_p.csv')

write_service_tech_by_p(CSV_rs_service_tech_by_p, rs_service_tech_by_p)
write_service_tech_by_p(CSV_ss_service_tech_by_p, ss_service_tech_by_p)
write_service_tech_by_p(CSV_is_service_tech_by_p, is_service_tech_by_p)

write_service_fueltype_tech_by_p(CSV_rs_service_fueltype_tech_by_p, rs_service_fueltype_tech_by_p)
write_service_fueltype_tech_by_p(CSV_ss_service_fueltype_tech_by_p, ss_service_fueltype_tech_by_p)
write_service_fueltype_tech_by_p(CSV_is_service_fueltype_tech_by_p, is_service_fueltype_tech_by_p)

write_service_fueltype_by_p(CSV_rs_service_fueltype_by_p, rs_service_fueltype_by_p)
write_service_fueltype_by_p(CSV_ss_service_fueltype_by_p, ss_service_fueltype_by_p)
write_service_fueltype_by_p(CSV_is_service_fueltype_by_p, is_service_fueltype_by_p)

print("... finished script {}".format(os.path.basename(__file__)))
