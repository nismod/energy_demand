
"""Script to run after installation of HIRE

Script function which are executed after model installation and
"""
import os
import zipfile

from energy_demand.read_write import data_loader
from energy_demand.scripts.smif_data_related import script_data_preparation_MISTRAL_pop_gva


def create_NISMOD1_data(path_to_zip_file, path_out):
    """

    Arguments
    ----------
    """
    print("... start running initialisation scripts", flush=True)
    config = data_loader.read_config_file(path_config_file)

    # Extract NISMOD population data
    path_to_zip_file = os.path.join(path_data, "population-economic-smif-csv-from-nismod-db.zip")
    path_extraction = os.path.join(path_out, "MISTRAL_pop_gva")
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(path_extraction)
    zip_ref.close()

    # Complete gva and pop data for every sector
    path_pop = os.path.join(local_data_path, "scenarios", "MISTRAL_pop_gva", "data")
    path_geography = os.path.join(local_data_path, "scenarios", "uk_pop_principal_2015_2050_MSOA_england.csv")
    geography_name = "lad_uk_2016"

    # All MISTRAL scenarios to prepare with correct config
    scenarios_to_generate = [
        'pop-baseline16_econ-c16_fuel-c16',
        'pop-f_econ-c_fuel-c',
        'pop-d_econ-c_fuel-c',]

    script_data_preparation_MISTRAL_pop_gva.run(
        path_to_folder=path_pop,
        path_MSOA_baseline=path_geography,
        MSOA_calculations=False,
        geography_name=geography_name,
        scenarios_to_generate=scenarios_to_generate)

    print("... successfully finished setup")
    return

if __name__ == '__main__':
    """
    """
    create_NISMOD1_data(
        path_to_zip_file="C:/Users/cenv0553/nismod2/data/energy_demand/population-economic-smif-csv-from-nismod-db.zip",
        path_out="C:/_NISMODI_DATA")
