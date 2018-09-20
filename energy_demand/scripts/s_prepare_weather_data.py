import os
import pandas as pd

#def run(path_files, path_out_files):
if 1 == 1:
    """Iterate weather data from MIDAS and
    generate annual hourly temperatre data files
    for every weather station by interpolating missing values
    http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/
    """
    path_files = "C:/Users/cenv0553/ED/data/_raw_data/_test_raw_weather_data"
    path_out_files ="C:/Users/cenv0553/ED/data/_raw_data/_test_raw_weather_data_cleaned"

    # Create out folder
    if os.path.isdir(path_out_files):
        pass
    else:
        os.mkdir(path_out_files)
        
    # Read all files
    all_annual_raw_files = os.listdir(path_files)
    
    # Iterate all files
    for file_name in all_annual_raw_files:

        full_path_filename = os.path.join(path_files, file_name)
        
        print("...reading in filename: " + str(full_path_filename))
                
        # Read raw file to panda dataframe
        raw_csv_file = pd.read_csv(file_name)
        
#run(
#    path_files="C:/Users/cenv0553/ED/data/raw_data/_test_raw_weather_data",
#    path_out_files="C:/Users/cenv0553/ED/data/_raw_data/_test_raw_weather_data_cleaned"
#)