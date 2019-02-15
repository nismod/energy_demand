import os

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

paths = [
    "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final/h_min",
    "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final/h_max",
    "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final/l_min",
    "//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final/l_max",
]
#paths = ["//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/_p3_weather_final/UNFINISHED"]
for path in paths:
    folders = os.listdir(path)

    for folder in folders:
        path_folder = os.path.join(path, folder)
        folder_size = get_size(path_folder) / 8589934592 #bit to Gigabyte
        print("Size: {}  {}".format(round(folder_size, 3), path_folder), flush=True)