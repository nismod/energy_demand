"""Functions to generate figures
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_folder(path_folder, name_subfolder=None):
    """Creates folder or subfolder

    Arguments
    ----------
    path : str
        Path to folder
    folder_name : str, default=None
        Name of subfolder to create
    """
    if not name_subfolder:
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
    else:
        path_result_subolder = os.path.join(path_folder, name_subfolder)
        if not os.path.exists(path_result_subolder):
            os.makedirs(path_result_subolder)

def load_data(in_path, scenarios):
    """Read results
    """

    data_container = {}

    for scenario in scenarios:
        data_container[scenario] = {}

        for mode in ['CENTRAL', 'DECENTRAL']:
            data_container[scenario][mode] = {}

            # Iterate over weather scenarios
            path_scenarios = os.path.join(in_path, scenario, mode, 'energy_supply_constrained', 'decision_0')
            weather_scenarios = os.listdir(path_scenarios)

            for weather_scenario in weather_scenarios:
                data_container[scenario][mode][weather_scenario] = {}

                # ---------------------------
                # Load supply generation mix
                # ---------------------------
                data_container[scenario][mode]['energy_supply_constrained'] = {}
                path_supply_mix = os.path.join(in_path, scenario, mode, weather_scenario, 'energy_supply_constrained', 'decision_0')

                all_files = os.listdir(path_supply_mix)

                for file_name in all_files:
                    path_file = os.path.join(path_supply_mix, file_name)
                    print(".... loading file: {}".format(file_name))

                    # Load data
                    data_file = pd.read_csv(path_file)

                    # Set energy_hub as index
                    try:
                        data_file.set_index('energy_hub')
                    except:
                        print("... file does not have 'energy_hub' as column")

                    data_container[scenario][mode][weather_scenario]['supply_mix'][file_name] = data_file

    return data_container


def fig_3(data_container, fueltype='electricity'):
    """
    """

    # Create x-y chart of a time-span (x-axis: demand, y-axis: time)

    
    # Dataset
    df = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
    
    # Invert axis (df1.T)
    # plot
    df.plot.area()

    '''data = np.random.rand(10, 4)
    columns = ['a', 'b', 'c', 'd']

    df = pd.DataFrame(data, columns=columns)
    df.plot.area()
    df.plot.hist(stacked=True, orientation='horizontal')
    #plt.show()
    print("t")

    ax = plt.gca()
    ax.invert_xaxis()

    #plt.gca().invert_yaxis()
    #df = pd.DataFrame(data, columns=columns)
    #df.plot.area()
    plt.show()
    print("t")
    raise Exception
    '''
    return


def fig_4(data_container):
    """
    """

    return


def fig_5(data_container):
    """
    """

    return


def fig_6(data_container):
    """
    """

    return
