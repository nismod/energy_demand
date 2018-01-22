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

    # Initialisations
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
    # Electricity:
    # According to OFEM, for GB there are about 2.3 mio electrically heated households
    # More specifically, they are made out of:
    #
    #       storage heaters:
    #           1.7m households --> 73.9%  ((100/2.3) * 1.7
    #
    #           However, these are often flats and this number contains some heatpumps,
    #           which results in lower fuel demand. Therefore in overall 70% of electriticy
    #           is assumed for storage heaters.
    #
    #       secondary heating (direct-acting heating systems):
    #           0.5m households --> 21.7% ((100/2.3) * 0.5
    #
    #       heat pumps
    #           ~ 0.1m households with heat pumps --> 4.3% ((100/2.3) * 0.1
    #
    # According to Hannon (2015), heat pumps account only for a tiny fraction of the UK.
    # heat supply for buildings (approximately 0.2%).
    #
    #  Ofgem (2015); Insights paper on households with electric and other non-gas heating,
    #  (December), 1–84.
    #
    #  Hannon, M. J. (2015). Raising the temperature of the UK heat pump market:
    #  Learning lessons from Finland. Energy Policy, 85, 369–375.
    #  https://doi.org/10.1016/j.enpol.2015.06.016
    # ---------------
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['gas']] = {
        'boiler_gas': 0.98,
        'stirling_micro_CHP': 0.02,
        'district_heating_gas': 0}
    #TO NODE: boiler_electricity --> Peaky profile from samson (which is only for gas) --> Use
    #
    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['electricity']] = {
        'heat_pumps_electricity': 0.04,
        'storage_heater_electricity': 0.74,
        'secondary_heater_electricity':0.22,

        #'district_heating_electricity': 0, #TODO ADD PROFILE FOR DISTRICT HEATING
        #'secondary_heater_electricity': 0.96
        #'boiler_electricity': 0.22 #getter

        #'heat_pumps_electricity': 0.04,
        #'secondary_heater_electricity': 0.96
        #'secondary_heater_electricity':0.96
        }

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0,
        'district_heating_biomass': 0.0}

    assumptions['rs_fuel_tech_p_by']['rs_space_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # ---------------
    # Water heating
    # Calculated based on TODO TODO
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
    #'''
    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['gas']] = {
        'boiler_gas': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['electricity']] = {
        #'boiler_electricity': 0.96,
        'secondary_heater_electricity': 0.96,
        'heat_pumps_electricity': 0.04,
        'district_heating_electricity': 0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    assumptions['ss_fuel_tech_p_by']['ss_space_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # Cooling
    #''' TODO TODO ss_cooling_ventilation
    assumptions['ss_fuel_tech_p_by']['ss_cooling_humidification'][fueltypes['electricity']] = {
        'ss_cooling_tech': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_cooled_storage'][fueltypes['electricity']] = {
        'ss_cooling_tech': 1.0}
    assumptions['ss_fuel_tech_p_by']['ss_fans'][fueltypes['electricity']] = {
        'ss_cooling_tech': 1.0}
    #'''

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
