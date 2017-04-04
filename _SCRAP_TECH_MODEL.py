    
    
    
    
    # --Efficiencies (Base year)
    eff_by = {
        # -- heating boiler ECUK Table 3.19
        'back_boiler' : 0.01,
        'combination_boiler' : 0.0,
        'condensing_boiler' : 0.5,
        'condensing_combination_boiler' : 0.0,
        'combination_boiler' : 0.0,

        # -- cooking
        'new_tech_A': 0.75,
        'tech_A' : 0.5,
        'tech_B' : 0.9,
        'tech_C': 0.0,

        # -- lighting
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        # -- cold
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,

        # -- wet
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,

        # -- consumer electronics
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,

        # -- home_computing
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5
        }
    assump_dict['eff_by'] = eff_by      # Add dictionaries to assumptions

    # --Efficiencies (End year)
    eff_ey = {
        # -- heating boiler ECUK Table 3.19
        'back_boiler' : 0.2,
        'combination_boiler' : 0.0,
        'condensing_boiler' : 0.99,
        'condensing_combination_boiler' : 0.0,
        'combination_boiler' : 0.0,

        # -- cooking
        'new_tech_A': 0.75,
        'tech_A' : 0.5,
        'tech_B' : 0.9,
        'tech_C': 0.0,

        # -- lighting
        'halogen_elec': 0.036,                   # Relative derived eff: 80% efficiency gaing to standard lighting blub RElative calculated to be 80% better than standard lighting bulb (180*0.02) / 100
        'standard_lighting_bulb': 0.02,          # Found on wikipedia
        'fluorescent_strip_lightinging': 0.054,  # Relative derived eff: 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_lighting_bulb': 0.034,    # Relative derived eff: 70% efficiency gain to standard lightingbulg
        'LED' : 0.048,                           # 40% savings compared to energy saving lighting bulb

        # -- cold
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,

        # -- wet
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,

        # -- consumer electronics
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,

        # -- home_computing
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5
        }
    assump_dict['eff_ey'] = eff_ey # Add dictionaries to assumptions

    # --Efficiencies (achieved until end year)
    eff_achieved = {
        # -- water heating boiler ECUK Table 3.19
        'back_boiler' : 0.0,
        'combination_boiler' : 0.0,
        'condensing_boiler' : 1.0,
        'condensing_combination_boiler' : 0.0,
        'combination_boiler' : 0.0,

        'boiler_A' : 0.5,
        'boiler_B' : 0.3,
        'new_tech_A': 0.1,
        'tech_A' : 0.5,
        'tech_B' : 0.5,
        'tech_C': 0.0,
        'tech_D' : 0.5,
        'tech_E' : 0.5,
        'tech_F': 0.0,
        'boiler_gas': 0.5,
        'boiler_oil': 0.5,
        'boiler_condensing': 0.5,
        'boiler_biomass': 0.5,
        'ASHP': 0.5,
        'HP_ground_source': 0.5,
        'HP_air_source': 0.5,
        'HP_gas': 0.5,
        'micro_CHP_elec': 0.5,
        'micro_CHP_thermal': 0.5,

        # -- lightinging
        'halogen_elec': 0.5,
        'standard_lighting_bulb': 0.5,
        'fluorescent_strip_lightinging': 0.5,
        'energy_saving_lighting_bulb': 0.5,
        'LED' : 0.6
    }
    assump_dict['eff_achieved'] = eff_achieved # Add dictionaries to assumptions

    # ---Helper function eff_achieved THIS can be used for scenarios to define how much of the fficiency was achieved
    for i in assump_dict['eff_achieved']:
        assump_dict['eff_achieved'][i] = 1.0

    # Define fueltype of each technology
    technology_fueltype = {
        #Lighting
        'LED': dict_fueltype['electricity'],
        'halogen_elec': dict_fueltype['electricity'],
        'standard_lighting_bulb': dict_fueltype['electricity'],
        'fluorescent_strip_lightinging': dict_fueltype['electricity'],
        'energy_saving_lighting_bulb': dict_fueltype['electricity'],
        'LED' : dict_fueltype['electricity'],

        #test
        'tech_A' : dict_fueltype['hydrogen'],
        'tech_B' : dict_fueltype['hydrogen'],
        'back_boiler' : dict_fueltype['electricity'],
        'condensing_boiler' : dict_fueltype['electricity']
    }
    assump_dict['technology_fueltype'] = technology_fueltype
