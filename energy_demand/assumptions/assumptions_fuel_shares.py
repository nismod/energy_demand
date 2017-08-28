"""
Fuel share assumptions
======================
All fuel shares of the base year for the different technologies are defined
"""
from energy_demand.technologies import technologies_related
from energy_demand.initalisations import initialisations
from energy_demand.initalisations import helper_functions
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def get_fuel_stock_definition(assumptions, data):
    """Assigning fuel or service shares per enduse for different
    technologies for the base year

    Parameters
    ----------
    assumptions : dict
        Assumptions
    data : dict
        Data container

    Returns
    -------
    assumptions : dict
        Asssumptions

    Note
    ----
    - For hybrid technologies, only assign electricity shares.
      The other repsective fuel share gets calculated in
      the function ``adapt_fuel_tech_p_by`` in the ``Enduse`` Class.
    """
    assumptions['rs_fuel_tech_p_by'] = initialisations.init_fuel_tech_p_by(data['rs_all_enduses'], data['nr_of_fueltypes'])
    assumptions['ss_fuel_tech_p_by'] = initialisations.init_fuel_tech_p_by(data['ss_all_enduses'], data['nr_of_fueltypes'])
    assumptions['is_fuel_tech_p_by'] = initialisations.init_fuel_tech_p_by(data['is_all_enduses'], data['nr_of_fueltypes'])

    # ------------------
    # Residential subModel - Fuel shares of technologies in enduse for base year
    # In an enduse, either all fueltypes need to be assigned with technologies or none. No mixing possible
    # ------------------

    # ---Lighting
    assumptions['rs_fuel_tech_p_by']['rs_lighting'][data['lu_fueltype']['electricity']] = {
        'standard_lighting_bulb': 0.02,
        'fluorescent_strip_lightinging' : 0.98,
        'energy_saving_lighting_bulb' : 0, #??,
        'LED': 0 #
        }

    # ---rs_cold (Refrigeration)
    assumptions['rs_fuel_tech_p_by']['rs_cold'][data['lu_fueltype']['electricity']] = {
        'chest_freezer': 0.087,
        'fridge_freezer': 0.588,
        'refrigerator': 0.143,
        'upright_freezer': 0.182
        }
    # ---rs_cooking
    assumptions['rs_fuel_tech_p_by']['rs_cooking'][data['lu_fueltype']['electricity']] = {
        'hob_electricity': 0.49,
        'oven_electricity': 0.51,
        'hob_induction_electricity': 0.0
        }

    # ---rs_wet
    assumptions['rs_fuel_tech_p_by']['rs_wet'][data['lu_fueltype']['electricity']] = {
        'washing_machine': 0.305,
        'washer_dryer': 0.157,
        'dishwasher': 0.220,
        'tumble_dryer': 0.318
        }

    #---Space heating
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['electricity']] = {
        'heat_pumps_electricity': 0.02, # 0.02 Hannon (2015)
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56}  # heat-pump share in uk #According to OFGEM 1.7 out of 4 mio households use storage heating == 42.5%..Hoever, often more flats and more fuel poverty and some heatpumps, i.e. lower demands (e.g. redue certain percentage)
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    # ---Water heating
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['electricity']] = {'hybrid_gas_electricity': 0.02, 'boiler_electricity': 0.98}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    tech_share_of_total_service = {
        'heat_pumps_electricity': 0.02,
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][data['lu_fueltype']['electricity']] = service_share_input_to_fuel(
        total_share_fueltype=0.0572,
        tech_share_of_total_service=tech_share_of_total_service,
        tech_stock=assumptions['technologies'],
        assumptions=assumptions)

    # ------------------
    # Service subModel - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['electricity']] = {
        'boiler_electricity': 0.98,
        'hybrid_gas_electricity': 0.02
        }
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    assumptions['ss_all_specified_tech_enduse_by'] = helper_functions.get_all_specified_tech(assumptions['ss_fuel_tech_p_by'])

    # ------------------
    # Industry subModel  - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['solid_fuel']] = {'boiler_solid_fuel': 1.0}
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['gas']] = {'boiler_gas': 1.0}
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['electricity']] = {'boiler_electricity': 0.5, 'heat_pumps_electricity': 0.5}  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['oil']] = {'boiler_oil': 1.0}
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['heat_sold']] = {'boiler_heat_sold': 1.0}
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['biomass']] = {'boiler_biomass': 1.0}
    assumptions['is_fuel_tech_p_by']['is_space_heating'][data['lu_fueltype']['hydrogen']] = {'boiler_hydrogen': 1.0}

    # ------------------
    # Helper functions
    # ------------------
    assumptions['rs_all_specified_tech_enduse_by'] = helper_functions.get_all_specified_tech(assumptions['rs_fuel_tech_p_by'])
    assumptions['is_all_specified_tech_enduse_by'] = helper_functions.get_all_specified_tech(assumptions['is_fuel_tech_p_by'])

    assumptions['rs_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['heat_pumps'], assumptions['rs_all_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['as_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['heat_pumps'], assumptions['ss_all_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['heat_pumps'], assumptions['is_all_specified_tech_enduse_by'], 'is_space_heating')

    assumptions['rs_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['hybrid_technologies'], assumptions['rs_all_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['as_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['hybrid_technologies'], assumptions['ss_all_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_all_specified_tech_enduse_by'] = helper_functions.add_undefined_tech(assumptions['hybrid_technologies'], assumptions['is_all_specified_tech_enduse_by'], 'is_space_heating')

    return assumptions

def service_share_input_to_fuel(total_share_fueltype, tech_share_of_total_service, tech_stock, assumptions):
    """Convert share of service to fuel share

    Parameters
    ----------
    total_share_fueltype : dict
        Shares per fueltype
    tech_share_of_total_service : dict
        Service share of technologies of a fueltype
        e.g. service_share_tech = {'tech_A': 0.4, 'tech_B': 0.6}¨
    tech_stock : object
        Technology stock
    assumptions : dict
        Assumptions

    Returns
    -------
    fuel_share_tech_within_fueltype : dict
        Fuel share

    Note
    -----
    Convert service share to fuel share. As an input, provide share of
    service per fueltype (e.g. in gas fueltype: 0.6 boilerA, 0.4, boilerB).

    With help of assumption of share per fueltype ``total_share_fueltype``,
    calculate fuel share.
    TODO:  IMPROVE
    """
    fuel_share_tech_within_fueltype = {}

    for technology, service_share_tech in tech_share_of_total_service.items():

        # Get efficiency (depending whether hybrid or regular technology or heat pumps for base year)
        tech_type = technologies_related.get_tech_type(
            technology,
            assumptions['technology_list']
            )

        if tech_type == 'hybrid_tech':
            eff_tech_by = assumptions['hybrid_technologies'][technology]['average_efficiency_national_by']
        elif tech_type == 'heat_pump':
            eff_tech_by = technologies_related.eff_heat_pump(
                temp_diff=10,
                efficiency_intersect=tech_stock[technology]['eff_by']
                )
        else:
            eff_tech_by = tech_stock[technology]['eff_by']

        # Convert total share of fueltype to fuel_share
        fueltype_tech_share = (total_share_fueltype * service_share_tech) / eff_tech_by

        fuel_share_tech_within_fueltype[technology] = fueltype_tech_share

    # Make that fuel shares sum up to 1
    total_fuel = 0
    for tech in fuel_share_tech_within_fueltype:
        total_fuel += fuel_share_tech_within_fueltype[tech]

    for tech, fuel in fuel_share_tech_within_fueltype.items():
        fuel_share_tech_within_fueltype[tech] = (1.0 / total_fuel) * fuel

    return fuel_share_tech_within_fueltype
