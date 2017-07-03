"""Reading data
"""
import os
import sys
import csv
import numpy as np

def read_csv_base_data_service(path_to_csv, nr_of_fueltypes):
    """This function reads in base_data_CSV all fuel types (first row is fueltype, subkey), header is appliances

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : dict
        Returns an dict with arrays

    Notes
    -----
    the first row is the fuel_ID
    The header is the sub_key
    """
    try:
        lines = []
        end_uses_dict = {}

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')
            _headings = next(read_lines) # Skip first row
            _secondLine = next(read_lines) # Skip first row

            # All sectors
            all_sectors = set([])
            for sector in _secondLine[1:]: #skip fuel ID:
                #if sector not in all_sectors:
                all_sectors.add(sector)

            # All enduses
            all_enduses = set([])
            for enduse in _headings[1:]: #skip fuel ID:
                #if enduse not in all_enduses:
                all_enduses.add(enduse)

            # Initialise dict
            for sector in all_sectors:
                end_uses_dict[sector] = {}
                for enduse in all_enduses:
                    end_uses_dict[sector][enduse] = np.zeros((nr_of_fueltypes)) #{}

            # Iterate rows
            for row in read_lines:
                lines.append(row)

            for cnt_fueltype, row in enumerate(lines):
                cnt = 1 #skip first
                for entry in row[1:]:
                    enduse = _headings[cnt]
                    sector = _secondLine[cnt]
                    end_uses_dict[sector][enduse][cnt_fueltype] += float(entry)
                    cnt += 1
    except:
        print("Error: Could not exectue read_csv_base_data_service")
    
    return end_uses_dict, list(all_sectors), list(all_enduses)

def read_csv_dict_no_header(path_to_csv):
    """Read in csv file into a dict (without header)

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {{str(Year): float(1990), str(Header1): float(Val1), str(Header2): float(Val2)}}
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        for row in read_lines: # Iterate rows
            try:
                out_dict[int(row[0])] = float(row[1])
            except ValueError:
                out_dict[int(row[0])] = str(row[1])

    return out_dict

def read_csv_float(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    service_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches, float) # Convert list into array

def read_csv(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    service_switches = []
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches) # Convert list into array