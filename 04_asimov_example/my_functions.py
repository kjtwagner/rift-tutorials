# my_functions.py

import re
import os
import h5py
import yaml
import numpy as np

################################################
# Definitions for IMRPhenomXPHM, SEOBNRv4PHM, SEOBNRv5PHM #
################################################

def get_event(filename):
    pattern = r"GW\d{6}_\d{6}"
    match = re.search(pattern, filename)
    if match:
        event_name = match.group(0)
    else:
        print(f"No event name found in {filename}")
        event_name = None  # or some default value
    return event_name
    
    
    
def get_value(h5_file, search_strings, parent_name='/'):
    # Check if search_strings is a single string. If so, convert it to a list for consistent handling
    if isinstance(search_strings, str):  
        search_strings = [search_strings]
    
    with h5py.File(h5_file, 'r') as f:
        # Define a nested recursive function to search through the HDF5 file structure
        def search_recursive(current_parent_name):
            # Iterate over all keys (dataset or group names) at the current level in the HDF5 file
            for key in f[current_parent_name].keys():
                full_path = current_parent_name + key
                # Check if the item at full_path is a dataset (contains data)
                if isinstance(f[full_path], h5py.Dataset):
                    # Loop through each search string
                    for search_string in search_strings:  
                        if search_string == key:  
                            # Get the dataset's value
                            value = f[full_path]
                            # Handle different data types in the dataset
                            # If the value is a numpy bytes type:
                            if isinstance(value[()][0], np.bytes_):
                                # If there's only one value, decode it to a UTF-8 string
                                if len(value[()]) == 1: 
                                    value_str = value[()][0].decode('utf-8')
                                # If there are multiple values, decode each one into a list of strings
                                else:  
                                    value_str = [item.decode('utf-8') for item in value[()]]
                            # If the value is a numpy boolean, convert it to a string
                            elif isinstance(value[()][0], np.bool_):
                                value_str = str(value[()][0]) 
                            # For all other types, convert to string
                            else:
                                value_str = str(value[()][0])
                            return value_str  
                        # If no match is found with this key, continue to the next search string or key
                # If the item is a group (i.e., a folder-like structure), recurse into it
                elif isinstance(f[full_path], h5py.Group):
                    # Call search_recursive on the subgroup, appending '/' to the path
                    result = search_recursive(f[full_path].name + '/')
                    # If a match was found in the subgroup, return it
                    if result is not None:  
                        return result
            # If no match is found at this level or in any subgroups, return None
            return None  
        
        # Start the recursive search from the specified parent_name (default is root '/')
        result = search_recursive(parent_name)
        
        if result is None:
            print(f"No value found for {search_strings}")
        return result
        

def convert_to_dict_C01(group, print_dict=False):
    data_dict = {}
    for key, value in group.items():
        if isinstance(value[()][0], np.bytes_):
            if len(value[()]) == 1: 
                value_str = value[()][0].decode('utf-8')
            else:  
                value_str = [item.decode('utf-8') for item in value[()]]
        elif isinstance(value[()][0], np.bool_):
            value_str = str(value[()][0]) 
        else:
            value_str = str(value[()][0]) 
        
        data_dict[key] = value_str
        
        if print_dict==True:
            print(f"{key}: {value_str}")

    return data_dict

def remove_none_values(d):
    if isinstance(d, dict):
        return {k: remove_none_values(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_none_values(item) for item in d]
    else:
        return d

def string_dict_to_dict(string_dict):
    pairs = string_dict.strip('{}').split(',')
    channel_dict = {}
    for pair in pairs:
        if ':' in pair:
            key, value        = pair.split(':', 1)
            key               = key.strip().strip("'")
            value             = value.strip().strip("'")
            channel_dict[key] = value
    return channel_dict

def get_string_value(input_string, key):
    import re
    # Define the regex pattern to grab the value up until the next , or )
    pattern = rf"{key}=([^,)]+)"
    # Search for the value in the string
    match = re.search(pattern, input_string)
    if match is None: 
        pattern = rf"'{key}':\s*([^,]+)"
        match = re.search(pattern, input_string)
    value = match.group(1)
    return value

def get_type(input_string):
    import re
    # Define the regex pattern to grab the value up until the next , or )
    pattern = rf"^([^\(]+)"
    # Search for the value in the string
    match = re.search(pattern, input_string)
    value = match.group(1)
    return value

def save_psd_data(data, file_path):
    """
    data: list of lists, consisting of psd data
    file_path: where data will be saved
    """
    with open(file_path, 'w') as file:
        for item in data:
            line = ' '.join(f'{x:.2e}' for x in item)
            file.write(line + '\n')



#####################
# Definitions for NRSur7dq4 #
#####################

def convert_to_dict_NRSur(group):
            data_dict = {}
            for key, value in group.items():
                if isinstance(value[()][0], np.bytes_):
                    if len(value[()]) == 1: 
                        value_str = value[()][0].decode('utf-8')
                        if value_str == "None":
                            value_str = None
                        elif value_str.startswith("{") and value_str.endswith("}") and key!="prior_dict":
                            value_str = [item.replace('"', '').replace("'", "").replace(" ", "") for item in value_str[1:-1].split(', ')]
                    else:  
                        value_str = [item.decode('utf-8') for item in value[()]]
                elif isinstance(value[()][0], np.bool_):
                    value_str = bool(str(value[()][0])=='true' or str(value[()][0])=='True')
                elif isinstance(value[()][0], np.int64):  
                    value_str = int(value[()][0])
                elif isinstance(value[()][0], np.float64):  
                    value_str = float(value[()][0])
                else:
                    value_str = str(value[()][0]) 

                data_dict[key] = value_str

            return data_dict
