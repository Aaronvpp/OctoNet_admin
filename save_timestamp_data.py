import os
import glob
# import ntplib
from time import ctime
from datetime import datetime
import pickle
# import sys

def save_timestamp_data(temp_data, index, timestamp, output_directory):
    data_folder = os.path.join(output_directory, "data")
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    file_path = os.path.join(data_folder, f'output_{index}.pickle')
    
    # Load existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            existing_data = pickle.load(f)
    else:
        existing_data = []

    data_dict = {"timestamp": timestamp, "data": temp_data}
    existing_data.append(data_dict)
    
    with open(file_path, 'wb') as f:
        pickle.dump(existing_data, f)


def get_next_index(output_directory):
    data_folder = os.path.join(output_directory, "data")
    existing_files = glob.glob(os.path.join(data_folder, 'output_*.pickle'))
    indices = [int(os.path.splitext(os.path.basename(f))[0].split('_')[1]) for f in existing_files]
    return max(indices) + 1 if indices else 0

def get_next_index_global_log(output_directory):
    data_folder = os.path.join(output_directory, "logs")
    existing_files = glob.glob(os.path.join(data_folder, 'config_*.log'))
    indices = [int(os.path.splitext(os.path.basename(f))[0].split('_')[1]) for f in existing_files]
    return max(indices) + 1 if indices else 0

def save_timestamp_data_polar(temp_data, index, timestamp, output_directory, type):
    data_folder = os.path.join(output_directory, "data")
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    file_path = os.path.join(data_folder, f'output_{index}_{type}.pickle')
    
    # Load existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            existing_data = pickle.load(f)
    else:
        existing_data = []

    if temp_data["values"]:
        data_dict = {"timestamp": timestamp, "data": temp_data["values"][-1]}
        existing_data.append(data_dict)
    
    with open(file_path, 'wb') as f:
        pickle.dump(existing_data, f)


def get_next_index_polar(output_directory):
    data_folder = os.path.join(output_directory, "data")
    existing_files = glob.glob(os.path.join(data_folder, 'output_*_hr_data.pickle'))
    indices = [int(os.path.splitext(os.path.basename(f))[0].split('_')[1]) for f in existing_files]
    return max(indices) + 1 if indices else 0