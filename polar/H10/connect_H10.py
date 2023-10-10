#!/usr/bin/env python
# coding: utf-8

# In[40]:


from PolarH10 import PolarH10
from bleak import BleakScanner
import numpy as np
from matplotlib import pyplot as plt
import asyncio
from tqdm import tqdm
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from time_utils import *
from save_timestamp_data import *
from log_utils import *
import configparser
import json
import asyncio
from bleak import BleakScanner


# In[ ]:
def check_terminate_flag():
    if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../terminate_flag.txt'))) or os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../terminate_polar_flag.txt'))):
        # os.remove("terminate_flag.txt")
        return True
    return False

async def main():
    # try:
        # record_len = 30
        # for device in devices:
        #     if device.name is not None and "Polar" in device.name:
        #         print("Find Polar H10!")
        #         polar_device = PolarH10(device)
        #         await polar_device.connect()
        #         try:
        #             await polar_device.get_device_info()
        #             await polar_device.print_device_info()
        #             await polar_device.start_ecg_stream()
        #             await polar_device.start_hr_stream()
        #             for i in tqdm(range(record_len), desc='Recording...'):
        #                 await asyncio.sleep(1)
        #             await polar_device.stop_ecg_stream()
        #             await polar_device.stop_hr_stream()

        #             # acc_data = polar_device.get_acc_data()
        #             ecg_data = polar_device.get_ecg_data()
        #             print("print(ecg_data)",ecg_data)
        #             # ibi_data = polar_device.get_ibi_data()
        #             hr_data = polar_device.get_hr_data()
        #             print("hr_data ",hr_data )
        #         finally:
        #             await polar_device.disconnect()
        devices = await BleakScanner.discover()
        # Initial config.ini
        config = configparser.ConfigParser()
        config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.ini')))
        polar_settings_str = config.get('device_settings', 'polar')
        polar_settings = json.loads(polar_settings_str)
        # General setting
        output_directory = os.path.dirname(os.path.abspath(__file__))
        current_index = get_next_index_polar(output_directory)
        # Log 
        logger = setup_logger(output_directory, current_index)
        config_data = {}
        for section in config.sections():
            if section != 'device_settings':
                config_data[section] = dict(config.items(section))
        logger.info(f"Loaded configuration: {config_data}")
        logger.info(f"Loaded Polar configuration: {polar_settings}")
        # seekthermal_settings_str = config.get('device_settings', 'polar')
        # config_data = {}
        # for section in config.sections():
        #     if section != 'device_settings':
        #         config_data[section] = dict(config.items(section))
        # logger.info(f"Loaded configuration: {config_data}")
        # logger.info(f"Loaded IRA configuration: {polar_settings}")
        record_len = int(polar_settings["record_len(in_second)"])
        for device in devices:
            timeflag = True
            if device.name is not None and "Polar" in device.name:
                print("Find Polar H10!")
                polar_device = PolarH10(device)
                await polar_device.connect()
                try:
                    await polar_device.get_device_info()
                    await polar_device.print_device_info()
                    await polar_device.start_ecg_stream()
                    await polar_device.start_hr_stream()
                    # try:
                    for i in tqdm(range(record_len), desc='Recording...'):
                        current_local_time = datetime.now()
                        if timeflag:
                            ntp_time, time_difference = get_ntp_time_and_difference()
                            fake_ntp_timestamp = ntp_time
                            logger.info("Using NTP time as the start timmer.")
                            timeflag = False
                        else:
                            current_local_time = datetime.now()
                            fake_ntp_timestamp = get_fake_ntp_time(current_local_time, time_difference)
                            logger.info("Using the local timmer to pretend to be NTP time. Data recorded")
                        print("current_local_time:", current_local_time)
                        print(f"NTP_Server_timestamp:, {fake_ntp_timestamp}")

                        # acc_data = polar_device.get_acc_data()
                        ecg_data = polar_device.get_ecg_data()
                        logger.info("ecg_data", ecg_data)
                        print("ecg_data", ecg_data)
                        save_timestamp_data_polar(ecg_data, current_index, fake_ntp_timestamp, output_directory, "ecg_data")
                        # ibi_data = polar_device.get_ibi_data()
                        hr_data = polar_device.get_hr_data()
                        print("get_hr_data", hr_data)
                        logger.info("get_hr_data", hr_data)
                        save_timestamp_data_polar(hr_data, current_index, fake_ntp_timestamp, output_directory, "hr_data")
                        await asyncio.sleep(1)

                        if check_terminate_flag():
                            logger.info("End recording by a terminate action.")
                            break

                    # except KeyboardInterrupt:
                    #     logger.info("End recording by a KeyboardInterrupt.") 
                
                    await polar_device.stop_ecg_stream()
                    await polar_device.stop_hr_stream()
                    
                finally:
                    await polar_device.disconnect()
            else:
                logger.error("Polar H10 device not found. ")
                print("Polar H10 device not found. ")


    # except Exception as e:
    #     logger.error(f"An error occurred: {str(e)}")
    #     print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
    # # In[ ]:





    # # In[ ]:


    # ecg_data['times'][-1] - ecg_data['times'][0]


    # # In[ ]:


    # hr_data['times'][-1] - hr_data['times'][0]


    # # In[ ]:


    # # hr_data['times'].shape


    # # In[ ]:


    # plt.plot(hr_data["times"],hr_data["values"])


    # # In[ ]:


    # plt.plot(ecg_data["times"][300:],ecg_data["values"][300:])


    # # In[ ]:


    # len(ecg_data["values"])


    # # In[ ]:


    # plt.plot(ecg_data['values'][:400])


    # # In[ ]:




