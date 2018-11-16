from ruamel.yaml import YAML
import numpy as np
import yaml
path = "C:/USers/cenv0553/ed/_scrap/test_file.yml"
data_to_dump = {1: np.zeros((3,4)), 2: 33}

def load(file_path):
    """Parse yaml config file into plain data (lists, dicts and simple values)
    Parameters
    ----------
    file_path : str
        The path of the configuration file to parse
    """
    with open(file_path, 'r') as file_handle:
        return YAML(typ='unsafe').load(file_handle)


def dump(data, file_path):
    """Write plain data to a file as yaml
    Parameters
    ----------
    data
        Data to write (should be lists, dicts and simple values)
    file_path : str
        The path of the configuration file to write
    """
    with open(file_path, 'w') as file_handle:
        yaml = YAML(typ='unsafe')
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        return yaml.dump(data, file_handle)

dump(data_to_dump, path)

b = load(path)

print("--------")
print(data_to_dump)
print("===================" )
print(b)
'''
def write_yaml(data_to_dump, file_path):
    #yaml = YAML()
    #yaml.dump(data_to_dump, file_path, default_flow_style=False)
    with open(file_path, 'w') as outfile:
        yaml.dump(data_to_dump, outfile, default_flow_style=False)
write_yaml(data_to_dump, path)

def read_yaml(file_path):
    #yaml = YAML() #typ='safe')   # default, if not specfied, is 'rt' (round-trip)
    yaml.load(file_path)
    return yaml

ff = read_yaml(path)

print(ff[1])'''