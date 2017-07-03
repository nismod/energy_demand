def write_YAML(crit_write, path_YAML, yaml_list):
    """Creates a YAML file with the timesteps IDs

    Parameters
    ----------
    crit_write : int
        Whether a yaml file should be written or not (1 or 0)
    path_YAML : str
        Path to write out YAML file
    yaml_list : list
        List containing YAML dictionaries for every region
    """
    if crit_write:
        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)

    return

def write_final_result(data, result_dict, lu_reg, crit_YAML):
    """Write reults for energy supply model

    Parameters
    ----------
    data : dict
        Whether a yaml file should be written or not (1 or 0)
    result_dict : dict
        Dictionary which is stored to txt
    lu_reg : dict
        Look up dict for regions
    crit_YAML : bool
        Criteria if YAML files are generated

    Example
    -------
    The output in the textfile is as follows:

        england, P0H, P1H, 139.42, 123.49
    """
    main_path = data['path_dict']['path_main'][:-5] # Remove data from path_main

    for fueltype in data['lu_fueltype'].values():

        # Path to create csv file
        path = os.path.join(main_path, 'model_output/_fueltype_{}_hourly_results.csv'.format(fueltype))

        with open(path, 'w', newline='') as fp:
            csv_writer = csv.writer(fp, delimiter=',')
            data = []
            yaml_list_fuel_type = []

            # Iterate fueltypes
            for reg in result_dict[fueltype]:

                for reg, hour, obs_value, _ in result_dict[fueltype]:
                    start_id = "P{}H".format(hour)
                    end_id = "P{}H".format(hour + 1)
                    data.append((lu_reg[reg], start_id, end_id, obs_value))
                    yaml_list_fuel_type.append({'region':  lu_reg[reg], 'start': start_id, 'end': end_id, 'value': float(obs_value), 'units': 'CHECK GWH', 'year': 'XXXX'})

            csv_writer.writerows(data)

            # Write YAML
            write_YAML(crit_YAML, os.path.join(main_path, 'model_output/YAML_  ----TIMESTEPS_{}.yml'.format(fueltype)), yaml_list_fuel_type)

def write_out_txt(path_to_txt, enduses_service):
    """Generate a txt file with base year service for each technology according to provided fuel split input
    """
    file = open(path_to_txt, "w")

    file.write("---------------------------------------------------------------" + '\n')
    file.write("Base year energy service (as share of total per enduse)" + '\n')
    file.write("---------------------------------------------------------------" + '\n')

    for enduse in enduses_service:
        file.write(" " + '\n')
        file.write("Enduse  "+ str(enduse) + '\n')
        file.write("----------" + '\n')

        for tech in enduses_service[enduse]:
            file.write(str(tech) + str("\t") + str("\t") + str("\t") + str(enduses_service[enduse][tech]) + '\n')

    file.close()
    return
