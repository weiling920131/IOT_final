import time, random, requests
import DAN
# import crawl_weather_V8 as cw
import os
import csv
from STT import STTAgent 
import threading
from gtts import gTTS

import RPi.GPIO as GPIO

v = 343
red_PIN = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(red_PIN,GPIO.IN)


def measure(music, RECV_text):   
    input_state = GPIO.input(red_PIN)
    play_music = f'play -q {music} vol 2.0'
    if RECV_text == True:
        print("----------------------------play message:----------------------------")
        os.system('play -q tts.mp3 vol 2.0')
        return False
    elif input_state == True:
        print("input state : true")
        DAN.push('Dummy_Sensor', "有客人進門了!!")
        os.system(play_music)
        time.sleep(1)
    else :
        print("exception : false")

    time.sleep(1)
    return True

def detect():
    global RECV_text
    
    try:
        while True:
            print("Detect RECV_text: ", RECV_text)
            played = measure("laoguo.mp3", RECV_text)
            if played == False:
                RECV_text = False
                tts_thread = threading.Thread(target = TTS)
                tts_thread.start()

    except KeyboardInterrupt:
        print("Exception:KeyboardInterrupt")

    finally:
        GPIO.cleanup()

def TTS():
    while True:
        text = DAN.pull('Dummy_Control')
        if text is None:
            continue
        
        # print("=========================text:",type(text[0]))
        time.sleep(1)
        # text = "吃雞巴"
        if text is not None:
            # print("===========================:",text)
            tts = gTTS(text=text[0], lang='zh-TW')
            tts.save('tts.mp3')
            global RECV_text
            RECV_text = True
            return

    

ServerURL = 'https://1.iottalk.tw/'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = '170.2' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'Dummy_Device'
DAN.profile['df_list']=['Dummy_Sensor', 'Dummy_Control']
DAN.profile['d_name']= '206_microphone'

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line
stt = STTAgent()

RECV_text = False

sensor = threading.Thread(target = detect)
sensor.start()

tts_thread = threading.Thread(target = TTS)
tts_thread.start()

while True:
    try:
        text = stt.run()
        if text is not None:
            print("The microphone receives: ", text)
            DAN.push('Dummy_Sensor', text)
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(1)

