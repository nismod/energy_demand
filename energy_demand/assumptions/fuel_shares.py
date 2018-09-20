"""All fuel shares of the base year for the
different technologies are defined in this file.
"""
from collections import defaultdict
from energy_demand.initalisations import helpers

def assign_by_fuel_tech_p(enduses, sectors, fueltypes, fueltypes_nr):
    """Assigning fuel share per enduse for different technologies
    for the base year.

    Arguments
    ----------
    enduses : dict
        Enduses
    sectors : dict
        Sectors per submodel
    fueltypes : dict
        Fueltypes lookup
    fueltypes_nr : int
        Number of fueltypes

    Returns
    -------
    fuel_tech_p_by : dict
        Residential fuel share percentages
    fuel_tech_p_by : dict
        Service fuel share percentages
    fuel_tech_p_by : dict
        Industry fuel share percentages

    Note
    ----
    - In an enduse, either all fueltypes with assigned fuelsneed to be
      assigned with technologies or none. No mixing possible

    - Technologies can be defined for the following fueltypes:
        'solid_fuel': 0,
        'gas': 1,
        'electricity': 2,
        'oil': 3,
        'biomass': 4,
        'hydrogen': 5,
        'heat': 6

    -   Not defined fueltypes will be assigned placholder technologies
    """
    fuel_tech_p_by = defaultdict(dict)

    _fuel_tech_p_by = helpers.init_fuel_tech_p_by(
        enduses['residential'], fueltypes_nr)
    fuel_tech_p_by.update(_fuel_tech_p_by)
    
    _fuel_tech_p_by = helpers.init_fuel_tech_p_by(
        enduses['service'], fueltypes_nr)
    fuel_tech_p_by.update(_fuel_tech_p_by)
    
    _fuel_tech_p_by = helpers.init_fuel_tech_p_by(
        enduses['industry'], fueltypes_nr)
    fuel_tech_p_by.update(_fuel_tech_p_by)

    # ====================
    # Residential Submodel
    # ====================

    # ---------------
    # rs_lighting
    # Calculated on the basis of ECUK Table 3.08
    # ---------------
    fuel_tech_p_by['rs_lighting'][fueltypes['electricity']] = {
        'standard_lighting_bulb': 0.04,
        'halogen': 0.56,
        'fluorescent_strip_lighting': 0.07,
        'energy_saving_lighting_bulb': 0.32,
        'LED': 0.01}

    # ---------------
    # rs_cold
    # Calculated on the basis of ECUK Table 3.08
    # ---------------
    fuel_tech_p_by['rs_cold'][fueltypes['electricity']] = {
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
    fuel_tech_p_by['rs_cooking'][fueltypes['electricity']] = {
        'hob_electricity': 0.95,
        'hob_induction_electricity': 0.05}
    fuel_tech_p_by['rs_cooking'][fueltypes['gas']] = {
        'hob_gas': 1.0}
    fuel_tech_p_by['rs_cooking'][fueltypes['hydrogen']] = {
        'hob_hydrogen': 1.0}
    fuel_tech_p_by['rs_cooking'][fueltypes['biomass']] = {
        'hob_biomass': 1.0}

    # ---------------
    # rs_wet
    # calculated on the basis of EUCK Table 3.08
    # ---------------
    fuel_tech_p_by['rs_wet'][fueltypes['electricity']] = {
        'washing_machine': 0.305,
        'washer_dryer': 0.157,
        'dishwasher': 0.220,
        'tumble_dryer': 0.318}

    # ---------------
    # rs_space_heating
    #
    # According to the DCLG (2014) English Housing Survey. Energy Report. doi: 10.1017/CBO9781107415324.004.
    # Annex Table 3.1, the following number of electric heating technologies can be found in the UK:
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
    # storage heaters                   5.1   % of all houses --> ~ 62%     (100.0 / 8.15) * 5.1
    # secondary_heater_electricity
    #   electric room heaters	        2.0   % of all houses --> ~ 25%     (100.0 / 8.15) * 2.0
    #   electric central heating	    0.65  % of all houses --> ~ 8%     (100.0 / 8.15) * 0.65
    # heat pumps                        0.4   % of all houses --> ~ 0.5%     (100.0 / 8.15) * 0.4
    #
    # OFGEM (2015); Insights paper on households with electric and other non-gas heating,
    # (December), 1–84.
    #
    # Hannon, M. J. (2015). Raising the temperature of the UK heat pump market:
    # Learning lessons from Finland. Energy Policy, 85, 369–375.
    # https://doi.org/10.1016/j.enpol.2015.06.016
    # ---------------
    fuel_tech_p_by['rs_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    fuel_tech_p_by['rs_space_heating'][fueltypes['oil']] = {
        'boiler_condensing_oil': 0.6,
        'boiler_oil': 0.4}

    # ---
    # According to table 3.19, 59.7% (43.5% + 14.3%) have some form of condensing boiler.

    # Todays share of district heating is about 2% of UK non-industraiyl demand
    # http://fes.nationalgrid.com/media/1215/160712-national-grid-dh-summary-report.pdf
    # ---
    fuel_tech_p_by['rs_space_heating'][fueltypes['gas']] = {
        'boiler_condensing_gas': 0.60,
        'boiler_gas': 0.37,
        'stirling_micro_CHP_gas': 0.0,
        'district_heating_CHP_gas': 0.03}

    fuel_tech_p_by['rs_space_heating'][fueltypes['electricity']] = {
        'storage_heater_electricity': 0.62,
        'secondary_heater_electricity':0.33,
        'heat_pumps_electricity': 0.05}

    fuel_tech_p_by['rs_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0,
        'district_heating_biomass': 0.0}

    fuel_tech_p_by['rs_space_heating'][fueltypes['hydrogen']] = {
        'fuel_cell_hydrogen': 0,
        'district_heating_fuel_cell': 0,
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0}

    # -------------
    # Residential water heating
    # -------------
    fuel_tech_p_by['rs_water_heating'][fueltypes['gas']] = {
        'boiler_condensing_gas': 0.60,
        'boiler_gas': 0.37,
        'stirling_micro_CHP_gas': 0.0,
        'district_heating_CHP_gas': 0.03}

    fuel_tech_p_by['rs_water_heating'][fueltypes['electricity']] = {
        'storage_heater_electricity': 0.62,
        'secondary_heater_electricity':0.33,
        'heat_pumps_electricity': 0.05}

    fuel_tech_p_by['rs_water_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0,
        'district_heating_biomass': 0.0}

    fuel_tech_p_by['rs_water_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0}

    fuel_tech_p_by['rs_water_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    fuel_tech_p_by['rs_water_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    # ===================
    # Service subModel
    # ===================

    # ss_lighting Simplified based on Table 5.09 (Office lighting)
    fuel_tech_p_by['ss_lighting'][fueltypes['electricity']] = {
        'halogen': 0.45,
        'fluorescent_strip_lighting': 0.07,
        'energy_saving_lighting_bulb': 0.47, #All different lighting next to halogen are summarised here ("non-halogen lighting")
        'LED': 0.01}

    # ----------------
    # Service space heating (ss_space_heating)
    #  For ss_space heating the load profile is the same for all technologies
    # ----------------
    fuel_tech_p_by['ss_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    fuel_tech_p_by['ss_space_heating'][fueltypes['gas']] = {
        'district_heating_CHP_gas': 0.02,
        'boiler_condensing_gas': 0.6,
        'boiler_gas': 0.38}

    fuel_tech_p_by['ss_space_heating'][fueltypes['electricity']] = {
        'secondary_heater_electricity': 0.95,
        'heat_pumps_electricity': 0.05}

    fuel_tech_p_by['ss_space_heating'][fueltypes['oil']] = {
        'boiler_condensing_oil': 0.6,
        'boiler_oil': 0.4}

    fuel_tech_p_by['ss_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    fuel_tech_p_by['ss_space_heating'][fueltypes['hydrogen']] = {
        'fuel_cell_hydrogen': 0,
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0,
        'district_heating_fuel_cell': 0.0}

    # -------------
    # Service water heating
    # -------------
    fuel_tech_p_by['ss_water_heating'][fueltypes['gas']] = {
        'boiler_condensing_gas': 0.60,
        'boiler_gas': 0.37,
        'stirling_micro_CHP_gas': 0.0,
        'district_heating_CHP_gas': 0.03}

    fuel_tech_p_by['ss_water_heating'][fueltypes['electricity']] = {
        'storage_heater_electricity': 0.62,
        'secondary_heater_electricity':0.33,
        'heat_pumps_electricity': 0.05}

    fuel_tech_p_by['ss_water_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0,
        'district_heating_biomass': 0.0}

    fuel_tech_p_by['ss_water_heating'][fueltypes['hydrogen']] = {
        'boiler_hydrogen': 1.0}

    fuel_tech_p_by['ss_water_heating'][fueltypes['oil']] = {
        'boiler_oil': 1.0}

    fuel_tech_p_by['ss_water_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    # ------------------------------
    # Cooling
    # ECUK Table 5.09
    # ------------------------------
    fuel_tech_p_by['ss_cooling_humidification'][fueltypes['electricity']] = {
        'central_air_conditioner_electricity': 0.64,
        'decentral_air_conditioner_electricity': 0.36}
    fuel_tech_p_by['ss_cooling_humidification'][fueltypes['gas']] = {
        'central_air_conditioner_gas': 0.64,
        'decentral_air_conditioner_gas': 0.36}
    fuel_tech_p_by['ss_cooling_humidification'][fueltypes['oil']] = {
        'central_air_conditioner_oil': 0.64,
        'decentral_air_conditioner_oil': 0.36}

    # Helper: Transfer all defined shares for every enduse to every sector
    fuel_tech_p_by = helpers.copy_fractions_all_sectors(
        fuel_tech_p_by,
        sectors['service'],
        affected_enduses=enduses['service'])

    # ===================
    # Industry subModel  - Fuel shares of technologies in enduse
    # ===================

    # ----------------
    # Industrial space heating (is_space_heating)
    # ----------------
    fuel_tech_p_by['is_space_heating'][fueltypes['solid_fuel']] = {
        'boiler_solid_fuel': 1.0}

    fuel_tech_p_by['is_space_heating'][fueltypes['gas']] = {
        'district_heating_CHP_gas': 0.02,
        'boiler_condensing_gas': 0.6,
        'boiler_gas': 0.38}

    fuel_tech_p_by['is_space_heating'][fueltypes['electricity']] = {
        'secondary_heater_electricity': 0.95,
        'heat_pumps_electricity': 0.05}

    fuel_tech_p_by['is_space_heating'][fueltypes['oil']] = {
        'boiler_condensing_oil': 0.6,
        'boiler_oil': 0.4}

    fuel_tech_p_by['is_space_heating'][fueltypes['biomass']] = {
        'boiler_biomass': 1.0}

    fuel_tech_p_by['is_space_heating'][fueltypes['hydrogen']] = {
        'fuel_cell_hydrogen': 0,
        'boiler_hydrogen': 1.0,
        'heat_pumps_hydrogen': 0.0,
        'district_heating_fuel_cell': 0.0}

    # Helper: Transfer all defined shares for every enduse to every sector
    fuel_tech_p_by = helpers.copy_fractions_all_sectors(
        fuel_tech_p_by,
        sectors['industry'],
        affected_enduses=enduses['industry'])

    # ----------------
    # Industrial High temporal processes (is_high_temp_process)
    # ----------------
    # Todays share is about: 17% electric furnace, 82% basic oxygen (Key Statistics 2016, appea, EnergyQuest)
    #-- basic_metals (sector)
    fuel_tech_p_by['is_high_temp_process']['basic_metals'][fueltypes['solid_fuel']] = {
        'basic_oxygen_furnace': 1.0}
    fuel_tech_p_by['is_high_temp_process']['basic_metals'][fueltypes['electricity']] = {
        'electric_arc_furnace': 1.0}
    fuel_tech_p_by['is_high_temp_process']['basic_metals'][fueltypes['gas']] = {
        'SNG_furnace': 1.0}
    fuel_tech_p_by['is_high_temp_process']['basic_metals'][fueltypes['biomass']] = {
        'biomass_furnace': 1.0}
    fuel_tech_p_by['is_high_temp_process']['basic_metals'][fueltypes['hydrogen']] = {
        'hydrogen_furnace': 1.0}

    #-- non_metallic_mineral_products
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['solid_fuel']] = {
        'dry_kiln_coal': 0.9,
        'wet_kiln_coal': 0.1}
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['oil']] = {
        'dry_kiln_oil': 0.9,
        'wet_kiln_oil': 0.1}
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['gas']] = {
        'dry_kiln_gas': 0.9,
        'wet_kiln_gas': 0.1}
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['electricity']] = {
        'dry_kiln_electricity': 0.9,
        'wet_kiln_electricity': 0.1}
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['biomass']] = {
        'dry_kiln_biomass': 1.0}
    fuel_tech_p_by['is_high_temp_process']['non_metallic_mineral_products'][fueltypes['hydrogen']] = {
        'dry_kiln_hydrogen': 1.0}

    return fuel_tech_p_by
