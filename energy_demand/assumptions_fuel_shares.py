"""File to define fuel share for base year
"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
from energy_demand.scripts_technologies import technologies_related


def get_fuel_stock_definition(assumptions, data):
    """Assigning fuel or service shares per enduse for different technologies for base year

    Parameters
    ----------
    assumptions : dict
        Assumptions

    Returns
    -------
    assumptions : dict
        Asssumptions

    Info
    ----
    - For hybrid technologies, only assign electricity shares. The other repsective fuel share gets calculated in
    the function XY TODO:

    """
    # Define stocks for all enduse and fueltype
    assumptions['rs_fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['rs_all_enduses'], data['nr_of_fueltypes'])
    assumptions['ss_fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['ss_all_enduses'], data['nr_of_fueltypes'])
    assumptions['is_fuel_enduse_tech_p_by'] = initialise_dict_fuel_enduse_tech_p_by(data['is_all_enduses'], data['nr_of_fueltypes'])

    # ------------------
    # Residential subModel - Fuel shares of technologies in enduse for base year
    # ------------------

    # Coooking
    #assumptions['rs_fuel_enduse_tech_p_by']['rs_cooking'][data['lu_fueltype']['electricity']] = {'hob_electricity': 0.5, oven_electricity: 0.5}
    #assumptions['rs_fuel_enduse_tech_p_by']['rs_cooking'][data['lu_fueltype']['gas']] = {'hob_gas': 0.5, oven_gas: 0.5}
    #assumptions['rs_fuel_enduse_tech_p_by']['rs_cooking_microwave'][data['lu_fueltype']['electricity']] = {'microwave': 1.0}


    tech_share_of_total_service = {
        'heat_pumps_electricity': 0.02,
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56}

    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['electricity']] = service_share_input_to_fuel(
        total_share_fueltype=0.0572,
        tech_share_of_total_service=tech_share_of_total_service,
        tech_stock=assumptions['technologies'],
        assumptions=assumptions)

    #---Space heating
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['electricity']] = {
        'heat_pumps_electricity': 0.02, # 0.02 Hannon (2015)
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56}  # heat-pump share in uk #According to OFGEM 1.7 out of 4 mio households use storage heating == 42.5%..Hoever, often more flats and more fuel poverty and some heatpumps, i.e. lower demands (e.g. redue certain percentage)
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    # ---Water heating
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['electricity']] = {'hybrid_gas_electricity': 0.02, 'boiler_electricity': 0.98}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['rs_fuel_enduse_tech_p_by']['rs_water_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    # ---Lighting
    assumptions['rs_fuel_enduse_tech_p_by']['rs_lighting'][data['lu_fueltype']['electricity']] = {
        'standard_resid_lighting_bulb': 0.02,
        'fluorescent_strip_lightinging' : 0.98
        }

    # ------------------
    # Service subModel - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['electricity']] = {
        'boiler_electricity': 0.98,
        'hybrid_gas_electricity': 0.02
        }
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    '''# -- Space cooling and ventilation
    share_cooling_not_ventilation = 0.5

    #------------------------------
    # Split Cooling and Ventilation
    #------------------------------
    for sector in data['ss_fuel_raw_data_enduses']:
        data['ss_fuel_raw_data_enduses'][sector]['ss_space_cooling'] = data['ss_fuel_raw_data_enduses'][sector]['ss_cooling_ventilation'] * share_cooling_not_ventilation
        data['ss_fuel_raw_data_enduses'][sector]['ss_ventilation'] = data['ss_fuel_raw_data_enduses'][sector]['ss_cooling_ventilation'] * (1 - share_cooling_not_ventilation)

        assumptions['ss_fuel_enduse_tech_p_by']['ss_space_cooling'] = dict.fromkeys(range(data['nr_of_fueltypes']), {})
        assumptions['ss_fuel_enduse_tech_p_by']['ss_ventilation'] = dict.fromkeys(range(data['nr_of_fueltypes']), {})
        del data['ss_fuel_raw_data_enduses'][sector]['ss_cooling_ventilation']

    data['ss_all_enduses'].remove('ss_cooling_ventilation') #delete enduse
    data['ss_all_enduses'].append('ss_space_cooling')
    data['ss_all_enduses'].append('ss_ventilation')
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_cooling'][data['lu_fueltype']['gas']] = {'air_condition_gas': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_cooling'][data['lu_fueltype']['electricity']] = {'air_condition_electricity': 1.0}
    assumptions['ss_fuel_enduse_tech_p_by']['ss_space_cooling'][data['lu_fueltype']['oil']] = {'air_condition_oil': 1.0}
    '''
    #assumptions['ss_fuel_enduse_tech_p_by']['ss_cooling_ventilation'][data['lu_fueltype']['gas']] = {'air_condition_gas': 1.0}
    #assumptions['ss_fuel_enduse_tech_p_by']['ss_cooling_ventilation'][data['lu_fueltype']['electricity']] = {'air_fans_electricity': 0.8, 'air_condition_electricity': 0.2}
    #assumptions['ss_fuel_enduse_tech_p_by']['ss_cooling_ventilation'][data['lu_fueltype']['oil']] = {'air_condition_oil': 1.0}

     #TODO: Check that all defined technologies are inserted here, even if not defined

    assumptions['ss_all_specified_tech_enduse_by'] = helper_get_all_specified_tech(assumptions['ss_fuel_enduse_tech_p_by'])

    # ------------------
    # Industry subModel  - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['electricity']] = {'boiler_electricity': 0.5, 'heat_pumps_electricity': 0.5}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['is_fuel_enduse_tech_p_by']['is_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    # ------------------
    # Helper functions
    # ------------------
    assumptions['rs_all_specified_tech_enduse_by'] = helper_get_all_specified_tech(assumptions['rs_fuel_enduse_tech_p_by'])
    assumptions['is_all_specified_tech_enduse_by'] = helper_get_all_specified_tech(assumptions['is_fuel_enduse_tech_p_by'])

    assumptions['rs_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['heat_pumps'], assumptions['rs_all_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['as_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['heat_pumps'], assumptions['ss_all_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['heat_pumps'], assumptions['is_all_specified_tech_enduse_by'], 'is_space_heating')

    assumptions['rs_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['hybrid_technologies'], assumptions['rs_all_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['as_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['hybrid_technologies'], assumptions['ss_all_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_all_specified_tech_enduse_by'] = helper_add_not_defined_technologies(assumptions['hybrid_technologies'], assumptions['is_all_specified_tech_enduse_by'], 'is_space_heating')



    return assumptions











def initialise_dict_fuel_enduse_tech_p_by(all_enduses_with_fuels, nr_of_fueltypes):
    """Helper function to define stocks for all enduse and fueltype

    Parameters
    ----------
    all_enduses_with_fuels : dict
        Provided fuels
    nr_of_fueltypes : int
        Nr of fueltypes

    Returns
    -------
    fuel_enduse_tech_p_by : dict

    """
    fuel_enduse_tech_p_by = {}

    for enduse in all_enduses_with_fuels:
        fuel_enduse_tech_p_by[enduse] = dict.fromkeys(range(nr_of_fueltypes), {})

    return fuel_enduse_tech_p_by

def helper_get_all_specified_tech(fuel_enduse_tech_p_by):
    """Collect all technologies across all fueltypes for all endueses where a service share is defined for the end_year
    """
    all_defined_tech_service_ey = {}
    for enduse in fuel_enduse_tech_p_by:
        all_defined_tech_service_ey[enduse] = []
        for fueltype in fuel_enduse_tech_p_by[enduse]:
            all_defined_tech_service_ey[enduse].extend(fuel_enduse_tech_p_by[enduse][fueltype])

    return all_defined_tech_service_ey



def helper_add_not_defined_technologies(heat_pumps, all_specified_tech_enduse_by, enduse):
    """Helper function
    """
    for heat_pump in heat_pumps:
        if heat_pump not in all_specified_tech_enduse_by[enduse]:
            all_specified_tech_enduse_by[enduse].append(heat_pump)

    return all_specified_tech_enduse_by

def service_share_input_to_fuel(total_share_fueltype, tech_share_of_total_service, tech_stock, assumptions):
    """Share of total service per technologies are provided for a fueltype

    Parameters
    ----------
    tech_share_of_total_service : dict
        Service share of technologies of a fueltype
        service_share_tech = {'tech_A': 0.4, 'tech_B': 0.6}
    """
    fuel_share_tech_within_fueltype = {}

    for technology, service_share_tech in tech_share_of_total_service.items():

        # --------------
        # Get efficiency
        # --------------
        tech_type = technologies_related.get_tech_type(technology, assumptions['technology_list'])

        # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
        if tech_type == 'hybrid_tech':
            eff_tech_by = assumptions['hybrid_technologies'][technology]['average_efficiency_national_by']
        elif tech_type == 'heat_pump':
            eff_tech_by = technologies_related.eff_heat_pump(
                m_slope=assumptions['hp_slope_assumption'],
                h_diff=10,
                intersect=tech_stock[technology]['eff_by']
                )
        else:
            eff_tech_by = tech_stock[technology]['eff_by']

        # ---------------------
        # Convert to fuel_share
        # ---------------------
        fueltype_tech_share = (total_share_fueltype * service_share_tech) / eff_tech_by

        fuel_share_tech_within_fueltype[technology] = fueltype_tech_share

    # -----------------------------------
    # Make that fuel shares sum up to 1
    # -----------------------------------
    total_fuel = 0
    for tech in fuel_share_tech_within_fueltype:
        total_fuel += fuel_share_tech_within_fueltype[tech]

    for tech, fuel in fuel_share_tech_within_fueltype.items():
        fuel_share_tech_within_fueltype[tech] = (1.0 / total_fuel) * fuel

    return fuel_share_tech_within_fueltype
