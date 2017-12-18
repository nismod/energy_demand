"""
Fuel share assumptions
======================
All fuel shares of the base year for the
different technologies are defined
"""
from energy_demand.initalisations import helpers

def assign_by_fuel_tech_p(assumptions, enduses, lookups):
    """Assigning fuel share per enduse for different
    technologies for the base year

    Arguments
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
    - In an enduse, either all fueltypes need to be
      assigned with technologies or none. No mixing possible

    - Technologies can be defined for the following fueltypes:
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'biomass': 4,
        'hydrogen': 5,
        'heat': 6
    """
    assumptions['rs_fuel_tech_p_by'] = helpers.init_fuel_tech_p_by(
        enduses['rs_all_enduses'], lookups['fueltypes_nr'])
    assumptions['ss_fuel_tech_p_by'] = helpers.init_fuel_tech_p_by(
        enduses['ss_all_enduses'], lookups['fueltypes_nr'])
    assumptions['is_fuel_tech_p_by'] = helpers.init_fuel_tech_p_by(
        enduses['is_all_enduses'], lookups['fueltypes_nr'])

    # ====================
    # Residential Submodel
    # ====================

    # ---------------
    # rs_lighting
    # calculated on the basis of ECUK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_lighting'][lookups['fueltype']['electricity']] = {
        'standard_lighting_bulb': 0.04,
        'halogen': 0.56,
        'fluorescent_strip_lightinging' : 0.07,
        'energy_saving_lighting_bulb' : 0.32,
        'LED': 0.01}

    # ---------------
    # rs_cold
    # calculated on the basis of ECUK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_cold'][lookups['fueltype']['electricity']] = {
        'chest_freezer': 0.087,
        'fridge_freezer': 0.588,
        'refrigerator': 0.143,
        'upright_freezer': 0.182}

    # ---------------
    # rs_cooking
    # calculated on the basis of ECUK Table 3.08 and assumption that 5-10% house households
    # ---------------
    # use induction hobs)
    assumptions['rs_fuel_tech_p_by']['rs_cooking'][lookups['fueltype']['electricity']] = {
        'hob_electricity': 0.95,
        'hob_induction_electricity': 0.05} # https://productspy.co.uk/are-induction-hobs-safe/ (5-10%)
        
    assumptions['rs_fuel_tech_p_by']['rs_cooking'][lookups['fueltype']['gas']] = {
        'hob_gas': 1.0}

    # ---------------
    # rs_wet
    # calculated on the basis of EUCK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_wet'][lookups['fueltype']['electricity']] = {
        'washing_machine': 0.305,
        'washer_dryer': 0.157,
        'dishwasher': 0.220,
        'tumble_dryer': 0.318}

    # ---------------
    # rs_space_heating
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['oil']] = {
        'boiler_oil': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['gas']] = {
        'boiler_gas': 0.98,
        'stirling_micro_CHP': 0.02}

    # heat-pump share in uk #According to OFGEM 1.7 out of 4
    # mio households use storage heating == 42.5%..Hoever,
    # often more flats and more fuel poverty and some heatpumps,
    # i.e. lower demands (e.g. redue certain percentage)
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['electricity']] = {
        'heat_pumps_electricity': 0.04, # 0.02 Hannon (2015) 04
        'storage_heater_electricity': 0.40,
        'secondary_heater_electricity': 0.56} #0.56

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][lookups['fueltype']['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ---------------
    # Water heating
    # Calculated based on TODOTODO
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['oil']] = {
        'boiler_oil': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['gas']] = {
        'boiler_gas': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['electricity']] = {
        'boiler_electricity': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][lookups['fueltype']['hydrogen']] = {
        'boiler_hydrogen': 1.0}

    # ===================
    # Service subModel
    # ===================

    # ----------------
    # ss_space_heating
    # ----------------
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['gas']] = {
        'boiler_gas': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['electricity']] = {
        'boiler_electricity': 0.96,
        'heat_pumps_electricity': 0.04}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['oil']] = {
        'boiler_oil': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][lookups['fueltype']['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    assumptions['ss_specified_tech_enduse_by'] = helpers.get_def_techs(
        assumptions['ss_fuel_tech_p_by'])

    # ===================
    # Industry subModel  - Fuel shares of technologies in enduse
    # ===================

    # ----------------
    # is_space_heating
    # ----------------
    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['gas']] = {
        'boiler_gas': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['electricity']] = {
        'boiler_electricity': 0.5,
        'heat_pumps_electricity': 0.5} #  'av_heat_pump_electricity': 0.02Hannon 2015, heat-pump share in uk

    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['oil']] = {
        'boiler_oil': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][lookups['fueltype']['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ------------------
    # Get technologies of an enduse
    # ------------------
    assumptions['rs_specified_tech_enduse_by'] = helpers.get_def_techs(assumptions['rs_fuel_tech_p_by'])
    assumptions['is_specified_tech_enduse_by'] = helpers.get_def_techs(assumptions['is_fuel_tech_p_by'])

    assumptions['rs_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'], assumptions['rs_specified_tech_enduse_by'], 'rs_space_heating')
    assumptions['ss_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'], assumptions['ss_specified_tech_enduse_by'], 'ss_space_heating')
    assumptions['is_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'], assumptions['is_specified_tech_enduse_by'], 'is_space_heating')
    assumptions['test'] = 'test'

    return assumptions
