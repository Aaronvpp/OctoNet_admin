import serial
import time
import ast
import numpy as np
import cv2
import os

# Interpolating the subpage into a complete frame by using the bilinear interpolating method with window size at 3x3.
def SubpageInterpolating(subpage):
    shape = subpage.shape
    mat = subpage.copy()
    for i in range(shape[0]):
        for j in range(shape[1]):
            if mat[i,j] > 0.0:
                continue
            num = 0
            try:
                top = mat[i-1,j]
                num = num+1
            except:
                top = 0.0
            
            try:
                down = mat[i+1,j]
                num = num+1
            except:
                down = 0.0
            
            try:
                left = mat[i,j-1]
                num = num+1
            except:
                left = 0.0
            
            try:
                right = mat[i,j+1]
                num = num+1
            except:
                right = 0.0
            mat[i,j] = (top + down + left + right)/num
    return mat

def main():
    # Open serial port (example with '/dev/tty.SLAB_USBtoUART' replace with your port and desired baud rate)
    port = '/dev/ttyUSB0'
    baud_rate = 921600
    ser = serial.Serial(port, baud_rate, timeout=1)
    
    Detected_temperature =  np.ones((24,32))*20

    if not ser.is_open:
        print(f"Failed to open serial port {port}")
        return

    try:
        print(f"Reading data from {port} at {baud_rate} baud")
        old_time = 0
        index = 0  # Initialize index

        # Find the next available index for the output file
        print(os.path)
        while os.path.exists(f"TermalSensor/data/output_{index}.txt"):
            index += 1

        output_file = open(f"TermalSensor/data/output_{index}.txt", "w")  # Open the output file

        while True:
            data = ser.readline().strip()
            if len(data) > 0:
                msg_str = str(data.decode('utf-8'))
            # time.sleep(0.1)
            try:
                dict_data = ast.literal_eval(msg_str)
                # esp32_timestamp = dict_data["Timestamp"]
                Onboard_timestamp = int(dict_data["loc_ts"])
                Ambient_temperature = float(dict_data["AT"])
                Detected_temperature = np.array(dict_data["data"]).reshape((24,32))
                # print(Onboard_timestamp - old_time)
                # old_time = Onboard_timestamp
                print(f"Timestamp: {Onboard_timestamp} | Ambient Temperature: {Ambient_temperature} | Detected Temperature: {Detected_temperature}")
                output_str = f"Timestamp: {Onboard_timestamp} | Ambient Temperature: {Ambient_temperature} | Detected Temperature:{Detected_temperature}"
                output_file.write(output_str + "\n")
                    
            
                
            except:
                print("Error")
            index += 1  # Increment index

            # print(Detected_temperature.shape)
            ira_interpolated = SubpageInterpolating(Detected_temperature)
            ira_norm = ((ira_interpolated - np.min(ira_interpolated))/ (37 - np.min(ira_interpolated))) * 255
            ira_expand = np.repeat(ira_norm, 20, 0)
            ira_expand = np.repeat(ira_expand, 20, 1)
            ira_img_colored = cv2.applyColorMap((ira_expand).astype(np.uint8), cv2.COLORMAP_JET)
            cv2.namedWindow('All', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('All', ira_img_colored)
            key = cv2.waitKey(1) 
            if key == 27 or key == 113:
                break
            
        cv2.destroyAllWindows()   
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()  # Close the serial port
        output_file.close()  # Close the output file

if __name__ == "__main__":
    main()