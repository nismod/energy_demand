    eff_by = {

        #---Heating
        'ASHP': 0.0, #?? PERCENTAGE
        'GSHP' : 0.0, #?? PERCENTAGE
        'HP_gas' : 0.0, #?? PERCENTAGE
        'uCHP_stirling_elec': 0.06,  #Combined heat and power
        'uCHP_stirling_thermal': 0.72, #Combined heat and power
        'HP_ground_source': 0.5, #Heating pumps ground source
        'HP_air_source': 0.0,
        'HP_gas': 0.0,
        'micro_CHP_elec': 0.0,
        'micro_CHP_thermal': 0.0,
        'HYDROGEN_TECH': 0.0,

        # -- Water heating
        'boiler_gas' : 0.7,
        'boiler_oil' : 0.7,
        'boilder_condens': 0.85,
        'coal_boiler' : 0.6,
        'boiler_elec' : 0.99,
        'HYDROGEN_TECH': 0.0,

        # -- Cooking
        'cooking_gas': 0.5,
        'cooking_elec': 0.9,
        'HYDROGEN_TECH': 0.0,

        # -- resid_lighting
        'halogen_elec': 0.036,                # 80% efficiency gaing to standard light blub RElative calculated to be 80% better than standard light bulb (180*0.02) / 100
        'standard_light_bulb': 0.02,          # Found on wiki: self
        'fluorescent_strip_resid_lighting': 0.054,  # 50% efficiency gaint to halogen (0.036*150) / 100
        'energy_saving_light_bulb': 0.034,    # 70% efficiency gain to standard lightbulg
        'LED' : 0.048,                         # 40% savings compared to energy saving light bulb

         # -- Cold Appliances
        'TECH_A': 0.0, #PV ??
        'TECH_B': 0.0,  
        'HYDROGEN_TECH': 0.0,
        
         # -- ICT
        'TECH_A': 0.0, #PV ??
        'TECH_B': 0.0,   

        # -- Other
        'PV': 0.1, #PV ??
        'micro_wind': 0.13


        }