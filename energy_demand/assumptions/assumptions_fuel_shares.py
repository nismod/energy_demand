"""
Fuel share assumptions
======================
All fuel shares of the base year for the different technologies are defined
"""
from energy_demand.technologies import technologies_related
from energy_demand.initalisations import initialisations
from energy_demand.initalisations import helpers

def assign_by_fuel_tech_p(assumptions, data):
    """Assigning fuel share per enduse for different
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
    - In an enduse, either all fueltypes need to be
      assigned with technologies or none. No mixing possible
    """
    rs_fuel_tech_p_by = initialisations.init_fuel_tech_p_by(
        data['enduses']['rs_all_enduses'], data['lookups']['nr_of_fueltypes'])
    ss_fuel_tech_p_by = initialisations.init_fuel_tech_p_by(
        data['enduses']['ss_all_enduses'], data['lookups']['nr_of_fueltypes'])
    is_fuel_tech_p_by = initialisations.init_fuel_tech_p_by(
        data['enduses']['is_all_enduses'], data['lookups']['nr_of_fueltypes'])

    fuel_nr_oil = data['lookups']['fueltype']['oil']
    fuel_nr_elec = data['lookups']['fueltype']['electricity']
    fuel_nr_gas = data['lookups']['fueltype']['gas']
    fuel_nr_heat_sold = data['lookups']['fueltype']['heat_sold']
    fuel_nr_biomass = data['lookups']['fueltype']['biomass']
    fuel_nr_hydrogen = data['lookups']['fueltype']['hydrogen']
    fuel_nr_solid_fuel = data['lookups']['fueltype']['solid_fuel']

    # ------------------
    # Residential subModel
    # ------------------

    # ---Lighting (calculated on the basis of EUCK Table 3.08)
    rs_fuel_tech_p_by['rs_lighting'][fuel_nr_elec] = {
        'standard_lighting_bulb': 0.04,
        'halogen': 0.56,
        'fluorescent_strip_lightinging' : 0.07,
        'energy_saving_lighting_bulb' : 0.32,
        'LED': 0.01
        }

    # ---rs_cold (calculated on the basis of EUCK Table 3.08)
    rs_fuel_tech_p_by['rs_cold'][fuel_nr_elec] = {
        'chest_freezer': 0.087,
        'fridge_freezer': 0.588,
        'refrigerator': 0.143,
        'upright_freezer': 0.182
        }

    # ---rs_cooking (calculated on the basis of EUCK Table 3.08)
    rs_fuel_tech_p_by['rs_cooking'][fuel_nr_elec] = {
        'hob_electricity': 0.49,
        'oven_electricity': 0.51,
        'hob_induction_electricity': 0.0 #TODO: MAKE OWN ASSUMPTION
        }

    # ---rs_wet (calculated on the basis of EUCK Table 3.08)
    rs_fuel_tech_p_by['rs_wet'][fuel_nr_elec] = {
        'washing_machine': 0.305,
        'washer_dryer': 0.157,
        'dishwasher': 0.220,
        'tumble_dryer': 0.318
        }

    #---Space heating (calculated based on XX TODO)
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_solid_fuel] = {
        'boiler_solid_fuel': 1.0
        }
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_gas] = {
        'boiler_gas': 1.0
        }
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_elec] = {
        'heat_pumps_electricity': 0.02, # 0.02 Hannon (2015)
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56
        }  # heat-pump share in uk #According to OFGEM 1.7 out of 4
        # mio households use storage heating == 42.5%..Hoever,
        # often more flats and more fuel poverty and some heatpumps,
        # i.e. lower demands (e.g. redue certain percentage)
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_oil] = {
        'boiler_oil': 1.0
        }
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_heat_sold] = {
        'boiler_heat_sold': 1.0
        }
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_biomass] = {
        'boiler_biomass': 1.0
        }
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_hydrogen] = {
        'boiler_hydrogen': 1.0
        }

    # ---Water heating
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_solid_fuel] = {
        'boiler_solid_fuel': 1.0
        }
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_gas] = {
        'boiler_gas': 1.0
        }
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_elec] = {
        'hybrid_gas_electricity': 0.02,
        'boiler_electricity': 0.98
        }  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_oil] = {
        'boiler_oil': 1.0
        }
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_heat_sold] = {
        'boiler_heat_sold': 1.0
        }
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_biomass] = {
        'boiler_biomass': 1.0
        }
    rs_fuel_tech_p_by['rs_water_heating'][fuel_nr_hydrogen] = {
        'boiler_hydrogen': 1.0
        }

    # --------------
    # ALTERNATIVE APPROCH BY ASSIGNIN SERVICE SHARES AND NOT FUEL SAHRES
    # --------------
    '''
    # Service share within a fueltype
    tech_share_tot_service = {
        'heat_pumps_electricity': 0.02,
        'hybrid_gas_electricity': 0.02,
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56}

    # Calculate what this means in fuel shares
    rs_fuel_tech_p_by['rs_space_heating'][fuel_nr_elec] = service_share_input_to_fuel(
        total_share_fueltype=0.0572,
        tech_share_tot_service=tech_share_tot_service,
        tech_stock=assumptions['technologies'],
        assumptions=assumptions)
    '''

    assumptions['rs_fuel_tech_p_by'] = rs_fuel_tech_p_by
    # --------------
    # TODO: Make that e.g. GW can be added to calculate fuel
    # --------------
    # add_GWH_heating_change_serivce_ey()

    # ------------------
    # Service subModel - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_solid_fuel] = {
        'boiler_solid_fuel': 1.0
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_gas] = {
        'boiler_gas': 1.0
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_elec] = {
        'boiler_electricity': 0.98,
        'hybrid_gas_electricity': 0.02
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_oil] = {
        'boiler_oil': 1.0
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_heat_sold] = {
        'boiler_heat_sold': 1.0
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_biomass] = {
        'boiler_biomass': 1.0
        }
    ss_fuel_tech_p_by['ss_space_heating'][fuel_nr_hydrogen] = {
        'boiler_hydrogen': 1.0
        }

    assumptions['ss_specified_tech_enduse_by'] = helpers.get_def_techs(
        ss_fuel_tech_p_by)

    assumptions['ss_fuel_tech_p_by'] = ss_fuel_tech_p_by
    # ------------------
    # Industry subModel  - Fuel shares of technologies in enduse
    # ------------------

    # ---Space heating
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_solid_fuel] = {
        'boiler_solid_fuel': 1.0}
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_gas] = {
        'boiler_gas': 1.0
        }
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_elec] = {
        'boiler_electricity': 0.5,
        'heat_pumps_electricity': 0.5
        }  #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_oil] = {
        'boiler_oil': 1.0
        }
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_heat_sold] = {
        'boiler_heat_sold': 1.0
        }
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_biomass] = {
        'boiler_biomass': 1.0
        }
    is_fuel_tech_p_by['is_space_heating'][fuel_nr_hydrogen] = {
        'boiler_hydrogen': 1.0
    }

    assumptions['is_fuel_tech_p_by'] = is_fuel_tech_p_by
    # ------------------
    # Helper functions
    # ------------------
    assumptions['rs_specified_tech_enduse_by'] = helpers.get_def_techs(assumptions['rs_fuel_tech_p_by'])
    assumptions['is_specified_tech_enduse_by'] = helpers.get_def_techs(assumptions['is_fuel_tech_p_by'])

    assumptions['rs_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['heat_pumps'], assumptions['rs_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['ss_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['heat_pumps'], assumptions['ss_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['heat_pumps'], assumptions['is_specified_tech_enduse_by'], 'is_space_heating')

    assumptions['rs_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['hybrid_technologies'], assumptions['rs_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['ss_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['hybrid_technologies'], assumptions['ss_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_specified_tech_enduse_by'] = helpers.add_undef_techs(assumptions['hybrid_technologies'], assumptions['is_specified_tech_enduse_by'], 'is_space_heating')

    return assumptions

def service_share_input_to_fuel(total_share_fueltype, tech_share_tot_service, tech_stock, assumptions):
    """Convert share of service to fuel share

    Parameters
    ----------
    total_share_fueltype : dict
        Shares of total service of this fueltype
    tech_share_tot_service : dict
        Service share of technologies of a fueltype
        e.g. service_share_tech = {'tech_A': 0.4, 'tech_B': 0.6}¨
    tech_stock : object
        Technology stock
    assumptions : dict
        Assumptions

    Returns
    -------
    fuel_share_tech_fueltype : dict
        Fuel share per technology of a fueltype

    Note
    -----
    Convert service share to fuel share. As an input, provide share of
    service per fueltype (e.g. in gas fueltype: 0.6 boilerA, 0.4, boilerB).

    With help of assumption of share per fueltype ``total_share_fueltype``,
    calculate fuel share.
    TODO:  IMPROVE
    """
    fuel_share_tech_fueltype = {}

    for technology, service_share_tech in tech_share_tot_service.items():

        # Get by efficiency
        tech_type = technologies_related.get_tech_type(
            technology,
            assumptions['tech_list']
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

        # Convert total share of service to fuel share (service to fuel)
        fueltype_tech_share = (total_share_fueltype * service_share_tech) / eff_tech_by

        fuel_share_tech_fueltype[technology] = fueltype_tech_share

    # Make that fuel shares sum up to 1
    total_fuel = sum(fuel_share_tech_fueltype.values())

    for tech, fuel in fuel_share_tech_fueltype.items():
        fuel_share_tech_fueltype[tech] = (1.0 / total_fuel) * fuel

    return fuel_share_tech_fueltype
