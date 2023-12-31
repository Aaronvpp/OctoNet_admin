import streamlit as st
import configparser
import json
import subprocess
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from log_utils import *
from save_timestamp_data import *
import time
import psutil
import glob
import re

processes = []
 # Initialize the process_dict
process_dict = {
    "IRA": {"pid": None},
    "Depth Camera": {"pid": None},
    "MMWave": {"pid": None},
    "SeekThermal": {"pid": None},
    "Polar": {"pid": None},
}

def update_modality_status(status_placeholder):
    try:
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "status.json")), "r") as f:
            status_dict = json.load(f)
    except json.JSONDecodeError:
        status_dict = {}  # Provide a default value or log an error message


    status_text = ""
    for process_name, status in status_dict.items():
        if status == "running":
            status_text += f"{process_name}: {status} (Running)\n"
        else:
            status_text += f"{process_name}: {status} (Not Running)\n"

    status_placeholder.text(status_text)

def find_latest_log_file(log_dir):
    log_files = glob.glob(log_dir + "config_*")
    max_index = -1
    latest_log_file = None

    for log_file in log_files:
        match = re.search(r"config_(\d+)", log_file)
        if match:
            index = int(match.group(1))
            if index > max_index:
                max_index = index
                latest_log_file = log_file
    # print("latest_log_file", latest_log_file)

    return latest_log_file

def get_process_status(pid):
    try:
        process = psutil.Process(pid)
        return process.status()
    except psutil.NoSuchProcess:
        return "Not running"
    
def tail(file_path, n=10):
    with open(file_path, "r") as file:
        return list(file)[-n:]
    
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def save_config(config, file_path):
    with open(file_path, 'w') as configfile:
        config.write(configfile)

# Load the .ini file
ini_file_path = 'config.ini'
config = load_config(ini_file_path)

# Display the app title and instructions
st.title("Octonet")
st.write("Modify the values in the .ini file using the fields below and click 'Save' when finished.")

# Display and edit the [participant] section
st.subheader("Participant")
participant_id = st.text_input("ID", config.get("participant", "id"))
participant_age = st.number_input("Age", value=int(config.get("participant", "age")))
participant_gender = st.selectbox("Gender", ["M", "F"], index=["M", "F"].index(config.get("participant", "gender")))
participant_ethnicity = st.text_input("Ethnicity", config.get("participant", "ethnicity"))
participant_height = st.number_input("Height", value=int(config.get("participant", "height")))
participant_weight = st.number_input("Weight", value=int(config.get("participant", "weight")))

# Update the [participant] section with the new values
config.set("participant", "id", participant_id)
config.set("participant", "age", str(participant_age))
config.set("participant", "gender", participant_gender)
config.set("participant", "ethnicity", participant_ethnicity)
config.set("participant", "height", str(participant_height))
config.set("participant", "weight", str(participant_weight))

# Display and edit the [experiment] section
st.subheader("Experiment")
experiment_date = st.date_input("Date", value=datetime.strptime(config.get("experiment", "date"), "%Y-%m-%d"))
experiment_time = st.time_input("Time", value=datetime.strptime(config.get("experiment", "time"), "%H:%M:%S").time())
experiment_condition = st.text_input("Condition", config.get("experiment", "condition"))
experiment_group = st.text_input("Group", config.get("experiment", "group"))
experiment_illumination_level = st.text_input("Illumination Level", config.get("experiment", "illumination_level"))

# Update the [experiment] section with the new values
config.set("experiment", "date", str(experiment_date))
config.set("experiment", "time", str(experiment_time))
config.set("experiment", "condition", experiment_condition)
config.set("experiment", "group", experiment_group)
config.set("experiment", "illumination_level", experiment_illumination_level)

# Display and edit the [task_info] section
st.subheader("Task Info")
task_name = st.text_input("Task Name", config.get("task_info", "task_name"))
trial_number = st.number_input("Trial Number", value=int(config.get("task_info", "trial_number")))

# Update the [task_info] section with the new values
config.set("task_info", "task_name", task_name)
config.set("task_info", "trial_number", str(trial_number))  

# Display and edit the [notes] section
st.subheader("Notes")
notes_comments = st.text_area("Comments", config.get("notes", "comments"))

# Update the [notes] section with the new values
config.set("notes", "comments", notes_comments)

# Display and edit the [label] section
st.subheader("**Label Info**")
activity_options = ["sit", "jump", "dance", "stand", "walk"]  # Add more activities as needed
activity_label = st.selectbox("Activity", options=activity_options, index=activity_options.index(config.get("label_info", "activity")))
config.set("label_info", "activity", activity_label)

# Display and edit the [device_settings] section
st.subheader("Device Settings")

# Create columns for each device
col1, col2, col3, col4, col5 = st.columns(5)

# IRA device settings
with col1:
    st.markdown("**IRA**")
    ira_json = json.loads(config.get("device_settings", "ira"))
    ira_port = st.text_input("Port", ira_json["port"])
    ira_baud_rate = st.text_input("Baud Rate", ira_json["baud_rate"])
    ira_data_storage_location = st.text_input("Data Storage Location", ira_json["Data storage location"])
    ira_datatype = st.text_input("IRA_Datatype", ira_json["IRA_Datatype"])

    ira_json["port"] = ira_port
    ira_json["baud_rate"] = ira_baud_rate
    ira_json["Data storage location"] = ira_data_storage_location
    ira_json["IRA_Datatype"] = ira_datatype
    config.set("device_settings", "ira", json.dumps(ira_json))
    if st.button("Start IRA"):
        processes.append(subprocess.Popen(["python", "IRA/IRA.py"], cwd="/home/aiot-mini/code/"))
        st.success("IRA process started.")
    
    # Terminate processes when the "Terminate" button is clicked
    if st.button("Terminate IRA"):
        with open("terminate_ira_flag.txt", "w") as f:
            f.write("1")
        st.write("Sent termination_ira signal.")
        time.sleep(6)  

        if os.path.exists("terminate_ira_flag.txt"):
            os.remove("terminate_ira_flag.txt")
            st.write("IRA modality is ended.")

# Depth camera settings
with col2:
    st.markdown("**Depth Camera**")
    depth_cam_json = json.loads(config.get("device_settings", "depth_cam"))
    depth_cam_resolution = st.text_input("Resolution", depth_cam_json["resolution"])
    depth_cam_depth_format = st.text_input("Depth Format", depth_cam_json["depth_format"])
    depth_cam_color_format = st.text_input("Color Format", depth_cam_json["color_format"])
    depth_cam_depth_fps = st.text_input("Depth FPS", depth_cam_json["depth_fps"])
    depth_cam_color_fps = st.text_input("Color FPS", depth_cam_json["color_fps"])
    depth_cam_data_storage_location = st.text_input("Data Storage Location", depth_cam_json["Data storage location"])
    depth_cam_depth_datatype = st.text_input("Depth_Datatype", depth_cam_json["Depth_Datatype"])
    depth_cam_rgb_datatype = st.text_input("RGB_Datatype", depth_cam_json["RGB_Datatype"])


    
    depth_cam_json["resolution"] = depth_cam_resolution
    depth_cam_json["depth_format"] = depth_cam_depth_format
    depth_cam_json["color_format"] = depth_cam_color_format
    depth_cam_json["depth_fps"] = depth_cam_depth_fps
    depth_cam_json["color_fps"] = depth_cam_color_fps
    depth_cam_json["Data storage location"] = depth_cam_data_storage_location
    depth_cam_json["Depth_Datatype"] = depth_cam_depth_datatype
    depth_cam_json["RGB_Datatype"] = depth_cam_rgb_datatype
    config.set("device_settings", "depth_cam", json.dumps(depth_cam_json))

    if st.button("Start depthcamera"):
        processes.append(subprocess.Popen(["python","DeptCam/deptcam.py"], cwd="/home/aiot-mini/code/"))
        st.success("Depthcamera process started.")
    
    # Terminate processes when the "Terminate" button is clicked
    if st.button("Terminate depthcamera"):
        with open("terminate_depthcam_flag.txt", "w") as f:
            f.write("1")
        st.write("Sent termination_depthcam signal.")
        time.sleep(6)  

        if os.path.exists("terminate_depthcam_flag.txt"):
            os.remove("terminate_depthcam_flag.txt")
            st.write("Depthcamera modality is ended.")

# Seek Thermal settings
with col3:
    st.markdown("**Seek Thermal**")
    seekthermal_json = json.loads(config.get("device_settings", "seekthermal"))
    seekthermal_port = st.text_input("Port", seekthermal_json["port"])
    seekthermal_frame_rate = st.text_input("Frame Rate", seekthermal_json["frame_rate"])
    seekthermal_color_palette = st.text_input("Color Palette", seekthermal_json["color_palette"])
    seekthermal_shutter_mode = st.text_input("Shutter Mode", seekthermal_json["shutter_mode"])
    seekthermal_agc_mode = st.text_input("AGC Mode", seekthermal_json["agc_mode"])
    seekthermal_temperature_unit = st.text_input("Temperature Unit", seekthermal_json["temperature_unit"])
    seekthermal_data_storage_location = st.text_input("Data Storage Location", seekthermal_json["Data storage location"])
    seekthermal_datatype = st.text_input("seekthermal_Datatype", seekthermal_json["seekthermal_Datatype"])

    seekthermal_json["port"] = seekthermal_port
    seekthermal_json["frame_rate"] = seekthermal_frame_rate
    seekthermal_json["color_palette"] = seekthermal_color_palette
    seekthermal_json["shutter_mode"] = seekthermal_shutter_mode
    seekthermal_json["agc_mode"] = seekthermal_agc_mode
    seekthermal_json["temperature_unit"] = seekthermal_temperature_unit
    seekthermal_json["Data storage location"] = seekthermal_data_storage_location
    seekthermal_json["seekthermal_Datatype"] = seekthermal_datatype
    config.set("device_settings", "seekthermal", json.dumps(seekthermal_json))

    if st.button("Start SeekThermal Camera"):
        processes.append(subprocess.Popen(["python","seekcamera-python/runseek/seekcamera-opencv.py"], cwd="/home/aiot-mini/code/"))
        st.success("SeekThermal Camera process started.")
    
    # Terminate processes when the "Terminate" button is clicked
    if st.button("Terminate SeekThermal Camera"):
        with open("terminate_seek_flag.txt", "w") as f:
            f.write("1")
        st.write("Sent termination_seek signal.")
        time.sleep(6)  

        if os.path.exists("terminate_seek_flag.txt"):
            os.remove("terminate_seek_flag.txt")
            st.write("SeekThermal Camera modality is ended.")
# MMWave settings
with col4:
    st.markdown("**MMWave**")
    mmwave_json = json.loads(config.get("device_settings", "mmwave"))
    mmwave_setting1 = st.text_input("Setting 1", mmwave_json["setting1"])
    mmwave_setting2 = st.text_input("Setting 2", mmwave_json["setting2"])
    mmwave_data_storage_location = st.text_input("Data Storage Location", mmwave_json["Data storage location"])
    mmwave_datatype = st.text_input("mmwave_Datatype", mmwave_json["mmwave_Datatype"])

    mmwave_json["setting1"] = mmwave_setting1
    mmwave_json["setting2"] = mmwave_setting2
    mmwave_json["Data storage location"] = mmwave_data_storage_location
    mmwave_json["mmwave_Datatype"] = mmwave_datatype
    
    config.set("device_settings", "mmwave", json.dumps(mmwave_json))

    if st.button("Start MMWave"):
        processes.append(subprocess.Popen(["python","AWR1843-Read-Data-Python-MMWAVE-SDK-3--master/readData_AWR1843.py"], cwd="/home/aiot-mini/code/"))
        st.success("MMWave process started.")
    
    # Terminate processes when the "Terminate" button is clicked
    if st.button("Terminate MMWave"):
        with open("terminate_mmwave_flag.txt", "w") as f:
            f.write("1")
        st.write("Sent termination_mmwave signal.")
        time.sleep(6)  

        if os.path.exists("terminate_mmwave_flag.txt"):
            os.remove("terminate_mmwave_flag.txt")
            st.write("MMWave modality is ended.")

with col5:
    st.markdown("**Polar**")
    polar_json = json.loads(config.get("device_settings", "polar"))
    polar_record_len = st.text_input("Record Length (in seconds)", polar_json["record_len(in_second)"])
    polar_data_storage_location = st.text_input("Data Storage Location", polar_json["Data storage location"])
    polar_datatype = st.text_input("polar_Datatype", polar_json["polar_Datatype"])
    
    
    polar_json["record_len(in_second)"] = polar_record_len
    polar_json["Data storage location"] = polar_data_storage_location
    polar_json["polar_Datatype"] = polar_datatype
    
    
    config.set("device_settings", "polar", json.dumps(polar_json))

    if st.button("Start Polar heart rate tracking"):
        processes.append(subprocess.Popen(["python","polar/H10/connect_H10.py"], cwd="/home/aiot-mini/code/"))
        st.success("Polar process started.")
    
    # Terminate processes when the "Terminate" button is clicked
    if st.button("Terminate Polar"):
        with open("terminate_polar_flag.txt", "w") as f:
            f.write("1")
        st.write("Sent termination_polar signal.")
        time.sleep(6)  

        if os.path.exists("terminate_polar_flag.txt"):
            os.remove("terminate_polar_flag.txt")
            st.write("Polar modality is ended.")


# Add checkboxes for each modality
st.subheader("Select Modalities to Start")
start_ira = st.checkbox("Start IRA")
start_depth_camera = st.checkbox("Start Depth Camera")
start_mmwave = st.checkbox("Start MMWave")
start_seekthermal = st.checkbox("Start Seek Thermal")
start_polar = st.checkbox("Start Polar")
# Save the modified .ini file when the "Save" button is clicked
if st.button("Save and Run"):
    save_config(config, ini_file_path)
    st.success("Config file saved.")
    
    # Start recording data
    st.write("Running and recording data...")
    # Save the global config and log
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini')))
    output_directory = os.path.dirname(os.path.abspath(__file__))
    current_index = get_next_index_global_log(output_directory)
    logger = setup_logger(output_directory, current_index)
    config_data = {}
    for section in config.sections():
        config_data[section] = dict(config.items(section))
    logger.info(f"Loaded Global Configuration: {config_data}")

    # when starting the IRA process:
    if start_ira:
        process = subprocess.Popen(["python", "IRA/IRA.py"], cwd="/home/aiot-mini/code/")
        process_dict["IRA"]["pid"] = process.pid
        processes.append(process)

    if start_depth_camera:
        process = subprocess.Popen(["python", "DeptCam/deptcam.py"], cwd="/home/aiot-mini/code/")
        process_dict["Depth Camera"]["pid"] = process.pid
        processes.append(process)

    if start_mmwave:
        process = subprocess.Popen(["python", "AWR1843-Read-Data-Python-MMWAVE-SDK-3--master/readData_AWR1843.py"], cwd="/home/aiot-mini/code/")
        process_dict["MMWave"]["pid"] = process.pid
        processes.append(process)

    # process = subprocess.Popen(["python", "Audio_Collector/main.py", "json", "/home/aiot-mini/code/Audio_Collector/config_file/speed_playfromfile_new.json"], cwd="/home/aiot-mini/code/")
    # process_dict[process.pid] = "Audio Collector"
    # processes.append(process)

    if start_seekthermal:
        process = subprocess.Popen(["python", "seekcamera-python/runseek/seekcamera-opencv.py"], cwd="/home/aiot-mini/code/")
        process_dict["SeekThermal"]["pid"] = process.pid
        processes.append(process)

    if start_polar:
        process = subprocess.Popen(["python", "polar/H10/connect_H10.py"], cwd="/home/aiot-mini/code/")
        process_dict["Polar"]["pid"] = process.pid
        processes.append(process)

    with open("process_dict.json", "w") as f:
        json.dump(process_dict, f)
    # process_dict = {
    # "IRA": {"pid": process.pid, "log_dir": "./IRA/logs/"},
    # "Depth Camera": {"pid": process.pid, "log_dir": "./DeptCam/logs/"},
    # "MMWave": {"pid": process.pid, "log_dir": "./path/to/IRA/log/"},
    # "SeekThermal": {"pid": process.pid, "log_dir": "./seekcamera-python/runseek/logs/"},
    # # "Audio Collector": {"pid": process.pid, "log_dir": "./path/to/IRA/log/"},
    # "Polar": {"pid": process.pid, "log_dir": "./polar/H10/logs/"},
    # }
    # st.subheader("Process Log")
    # time.sleep(6)  # To let the config file to be generated
    # # num_lines = st.slider("Number of log lines to display", 1, 30, 2)

    # for process_name, process_info in process_dict.items():
    #     log_dir = process_info["log_dir"]
    #     log_file_path = find_latest_log_file(log_dir)
    #     if log_file_path:
    #         log_content = tail(log_file_path, n=5)
    #         st.write(f"{process_name} Log:{log_file_path}")
    #         for line in log_content:
    #             st.write(line.strip())
    #     else:
    #         st.write(f"{process_name} Log: No log file found,{log_file_path}")
    # st.subheader("Process Status")
    # for pid, process_name in process_dict.items():
    #     status = get_process_status(pid)
    #     st.write(f"{process_name}: {status}")

    # st.subheader("Process Log")

    # for pid, process_name in process_dict.items():
    #     log_file_path = "path/to/log_file"  
    #     log_content = tail(log_file_path, n=10)
    #     st.write(f"{process_name} Log:")
    #     for line in log_content:
    #         st.write(line.strip())

# Terminate processes when the "Terminate" button is clicked
if st.button("Terminate All"):
    with open("terminate_flag.txt", "w") as f:
        f.write("1")
    st.write("Sent termination signal.")
    time.sleep(6)  

    if os.path.exists("terminate_flag.txt"):
        os.remove("terminate_flag.txt")
        st.write("All processes are terminated.")
        
# Daemon Process
status_placeholder = st.empty()
while True:
    update_modality_status(status_placeholder)
    time.sleep(5)