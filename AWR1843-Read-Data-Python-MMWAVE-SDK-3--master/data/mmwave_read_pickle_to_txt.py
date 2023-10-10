import os
import glob
import pickle

# Create the directory if it doesn't exist
output_directory = "txt_reader"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

pickle_files = glob.glob("output_*.pickle")

for pickle_file in pickle_files:
    output_txt_file = pickle_file.replace(".pickle", ".txt")
    output_txt_file = os.path.join(output_directory, output_txt_file)

    with open(pickle_file, 'rb') as f:
        data_dicts = pickle.load(f)

    with open(output_txt_file, 'w') as f:
        for index, data_dict in enumerate(data_dicts):
            timestamp = data_dict['timestamp']
            frame_data = data_dict['data']

            f.write(f"Index: {index}:\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("Data:\n")
            f.write(str(frame_data) + "\n")
            f.write("\n")