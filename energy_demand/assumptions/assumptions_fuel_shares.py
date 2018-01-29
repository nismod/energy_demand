"""
Base year fuel share assumptions
=========================================
All fuel shares of the base year for the
different technologies are defined in this file.
"""
from energy_demand.initalisations import helpers

def assign_by_fuel_tech_p(assumptions, enduses, fueltypes, fueltypes_nr):
    """Assigning fuel share per enduse for different technologies
    for the base year.

    Arguments
    ----------
    assumptions : dict
        Assumptions
    enduses : dict
        Enduses
    fueltypes : dict
        Fueltypes lookup
    fueltypes_nr : int
        Number of fueltypes

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
        enduses['rs_all_enduses'], fueltypes_nr)
    assumptions['ss_fuel_tech_p_by'] = helpers.init_fuel_tech_p_by(
        enduses['ss_all_enduses'], fueltypes_nr)
    assumptions['is_fuel_tech_p_by'] = helpers.init_fuel_tech_p_by(
        enduses['is_all_enduses'], fueltypes_nr)

    # ====================
    # Residential Submodel
    # ====================

    # ---------------
    # rs_lighting
    # Calculated on the basis of ECUK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_lighting'][fueltypes['electricity']] = {
        'standard_lighting_bulb': 0.04,
        'halogen': 0.56,
        'fluorescent_strip_lightinging' : 0.07,
        'energy_saving_lighting_bulb' : 0.32,
        'LED': 0.01}

    # ---------------
    # rs_cold
    # Calculated on the basis of ECUK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_cold'][fueltypes['electricity']] = {
        'chest_freezer': 0.087,
        'fridge_freezer': 0.588,
        'refrigerator': 0.143,
        'upright_freezer': 0.182}

    # ---------------
    # rs_cooking
    # Calculated on the basis of ECUK Table 3.08
    # Calculated on the assumption that 5 to 10%
    # of all households have induction hobs (https://productspy.co.uk/are-induction-hobs-safe/ (5-10%))
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_cooking'][fueltypes['electricity']] = {
        'hob_electricity': 0.95,
        'hob_induction_electricity': 0.05}

    assumptions['rs_fuel_tech_p_by']['rs_cooking'][fueltypes['gas']] = {
        'hob_gas': 1.0}

    # ---------------
    # rs_wet
    # calculated on the basis of EUCK Table 3.08
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_wet'][fueltypes['electricity']] = {
        'washing_machine': 0.305,
        'washer_dryer': 0.157,
        'dishwasher': 0.220,
        'tumble_dryer': 0.318}

    # ---------------
    # rs_space_heating
    #
    # According to the DCLG (2014) English Housing Survey. Energy Report. doi: 10.1017/CBO9781107415324.004.
    # Annex Table 3.1, the following number of electric heating technologies
    # can be found in the UK:
    #
    # storage heaters             5.5   % of all houses
    # electric room heaters	      2.0   % of all houses
    # electric central heating	 0.65   % of all houses
    #
    # As heat pumps were not accounted for, they are taken from OFGEM (2015),
    # which states that there are about 0.1m heat pumps of about in total 27m
    # households in the UK. This corresponds to about 0.4 %. (see also Hannon 2015).
    # According to Hannon (2015), heat pumps account only for a tiny fraction of the UK.
    # heat supply for buildings (approximately 0.2%). This percentage is substract from
    # the storage heaters.
    #
    # storage heaters             5.1   % of all houses --> ~ 62%     (100.0 / 8.15) * 5.1
    # electric room heaters	      2.0   % of all houses --> ~ 25%     (100.0 / 8.15) * 2.0
    # electric central heating	  0.65  % of all houses --> ~ 8%     (100.0 / 8.15) * 0.65
    # heat pumps                  0.4   % of all houses --> ~ 5%     (100.0 / 8.15) * 0.4
    #
    # OFGEM (2015); Insights paper on households with electric and other non-gas heating,
    # (December), 1–84.
    #
    # Hannon, M. J. (2015). Raising the temperature of the UK heat pump market:
    # Learning lessons from Finland. Energy Policy, 85, 369–375.
    # https://doi.org/10.1016/j.enpol.2015.06.016
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['gas']] = {
        'boiler_gas': 0.98,
        'stirling_micro_CHP_gas': 0.02,
        'district_heating_gas': 0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['electricity']] = {
        'storage_heater_electricity': 0.62,
        'secondary_heater_electricity': 0.25,
        'district_heating_electricity': 0.08, # same shape as CHP
        'heat_pumps_electricity': 0.05} #0.05

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0,
        'district_heating_biomass': 0.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ---------------
    # Water heating
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['gas']] = {
        'boiler_gas': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['electricity']] = {
        'boiler_electricity': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_water_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0}

    # ===================
    # Service subModel
    # ===================
    # For ss_space heating the load profile is the same for all technologies

    # ----------------
    # ss_space_heating
    # ----------------
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['gas']] = {
        'boiler_gas': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['electricity']] = {
        'boiler_electricity': 0.96,
        'heat_pumps_electricity': 0.04,
        'district_heating_electricity': 0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ------------------------------
    # Cooling
    # ------------------------------
    # ECUK Table 5.09
    assumptions['ss_fuel_tech_p_by']['ss_cooling_humidification'][fueltypes['electricity']] = {
        'central_air_conditioner_electricity': 0.64,
        'decentral_air_conditioner_electricity': 0.36}
    assumptions['ss_fuel_tech_p_by']['ss_cooling_humidification'][fueltypes['gas']] = {
        'central_air_conditioner_gas': 0.64,
        'decentral_air_conditioner_gas': 0.36}
    assumptions['ss_fuel_tech_p_by']['ss_cooling_humidification'][fueltypes['oil']] = {
        'central_air_conditioner_oil': 0.64,
        'decentral_air_conditioner_oil': 0.36}
    '''assumptions['ss_fuel_tech_p_by']['ss_cooled_storage'][fueltypes['electricity']] = {
        'ss_cooling_tech_electricity': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_fans'][fueltypes['electricity']] = {
        'ss_cooling_tech_electricity': 1.0}'''

    # ===================
    # Industry subModel  - Fuel shares of technologies in enduse
    # ===================

    # ----------------
    # is_space_heating
    # ----------------
    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['gas']] = {
        'boiler_gas': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['electricity']] = {
        'boiler_electricity': 0.96,
        'heat_pumps_electricity': 0.04}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['is_fuel_tech_p_by']['is_space_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ------------------
    # Get technologies of an enduse
    # ------------------
    assumptions['rs_specified_tech_enduse_by'] = helpers.get_def_techs(
        assumptions['rs_fuel_tech_p_by'])

    assumptions['ss_specified_tech_enduse_by'] = helpers.get_def_techs(
        assumptions['ss_fuel_tech_p_by'])

    assumptions['is_specified_tech_enduse_by'] = helpers.get_def_techs(
        assumptions['is_fuel_tech_p_by'])

    assumptions['rs_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'],
        assumptions['rs_specified_tech_enduse_by'],
        'rs_space_heating')

    assumptions['ss_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'],
        assumptions['ss_specified_tech_enduse_by'],
        'ss_space_heating')

    assumptions['is_specified_tech_enduse_by'] = helpers.add_undef_techs(
        assumptions['heat_pumps'],
        assumptions['is_specified_tech_enduse_by'],
        'is_space_heating')

    assumptions['test'] = 'test'

    return assumptions
