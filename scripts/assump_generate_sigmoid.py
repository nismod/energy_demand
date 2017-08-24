

    
# RESIDENTIAL: Convert base year fuel input assumptions to energy service
base_data['assumptions']['rs_service_tech_by_p'], base_data['assumptions']['rs_service_fueltype_tech_by_p'], base_data['assumptions']['rs_service_fueltype_by_p'] = fuel_service_switch.get_service_fueltype_tech(
        base_data['assumptions'],
        base_data['lu_fueltype'],
        base_data['assumptions']['rs_fuel_tech_p_by'],
        base_data['rs_fuel_raw_data_enduses'],
        base_data['assumptions']['technologies']
        )

base_data['assumptions']['rs_tech_increased_service'], base_data['assumptions']['rs_tech_decreased_share'], base_data['assumptions']['rs_tech_constant_share'] = fuel_service_switch.get_tech_future_service(base_data['assumptions']['rs_service_tech_by_p'], base_data['assumptions']['rs_share_service_tech_ey_p'])


# --Residential
base_data['assumptions']['rs_installed_tech'], base_data['assumptions']['rs_sig_param_tech'] = diffusion.get_sig_diffusion(
        base_data,
        base_data['assumptions']['rs_service_switches'],
        base_data['assumptions']['rs_fuel_switches'],
        base_data['rs_all_enduses'],
        base_data['assumptions']['rs_tech_increased_service'],
        base_data['assumptions']['rs_share_service_tech_ey_p'],
        base_data['assumptions']['rs_enduse_tech_maxL_by_p'],
        base_data['assumptions']['rs_service_fueltype_by_p'],
        base_data['assumptions']['rs_service_tech_by_p'],
        base_data['assumptions']['rs_fuel_tech_p_by']
        )
