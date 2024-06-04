import time, random, requests
import DAN
import crawl_weather_V8 as cw
import os
import csv
from STT import STTAgent 

ServerURL = 'https://2.iottalk.tw/'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = '170.2' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'Dummy_Device'
DAN.profile['df_list']=['Dummy_Control']
DAN.profile['d_name']= '206_Dummy_Device'

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line
stt = STTAgent()
while True:
    try:
        text = stt.run()
        if text is not None:
            print(text)
            DAN.push('Dummy_Control', text)
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(1)

