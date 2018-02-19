
""" Definition of technologies
    ===========================

    The following parameters need to be defined in case
    a new technology is defined

    {"technology": "",
    "fueltype": "",
    "eff_by": "",
    "eff_ey": "",
    "year_eff_ey": "",
    "diff_method": "",
    "market_entry": "",
    "tech_list":    "",
    "tech_max_share": ""}


    basic_functions.del_file(paths['yaml_parameters_scenario'])
    write_data.write_yaml_param_scenario(
        paths['yaml_parameters_scenario'],
        strategy_vars)

technology, fueltype, eff_by, eff_ey,year_eff_ey, eff_achieved,diff_method,market_entry,tech_list,tech_max_share,NOTES,,,CORRECT_EFFICIENCIES_EX,, eff_by, eff_ey,,,,,
halogen,electricity,0.04,0.04,2050,1,linear,2010,rs_lighting,1,,,,0.04,,0.04,0.04,,,,,
"""

def write_techs_in_csv_to_YAML(path, strategy_vars):
    
    from energy_demand.read_write import write_data

    write_data.write_yaml_param_scenario(
        path,
        strategy_vars)

write_techs_in_csv_to_YAML("C:/_scrap", )
'''technologies = {
    {   
        "technology": "",
        "fueltype": "",
        "eff_by": "",
        "eff_ey": "",
        "year_eff_ey": "",
        "diff_method": "",
        "market_entry": "",
        "tech_list":    "",
        "tech_max_share": ""
        },
  '''