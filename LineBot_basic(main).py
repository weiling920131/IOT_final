# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import time
import DAN
import crawl_weather_V8 as cw

ServerURL = 'https://1.iottalk.tw/'      #with non-secure connection
Reg_addr = '103.1.3' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'LineBot'
DAN.profile['df_list']=['Msg-I', 'Msg-O']
DAN.profile['d_name']= '103_Dummy_Device'

DAN.device_registration_with_retry(ServerURL, Reg_addr)

line_bot_api = LineBotApi('Qc1Aa6fKTU3re63L/LJiI3nGfbzbAnmvBqlvELR3LBeLMYgLT+6hhxK9S+zGu9tTAPbKiy7sC8kk5fRSFmc6Z7+siufo52tSNks/SwqrlFM3daHL093Mcylq2fUID/0713n1e30LCrmJKmKBQ6N3hAdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
handler = WebhookHandler('e40f04844ce6c0b7ed2c7f2df55945b1')        #LineBot's Channel secret
user_id_set=set()                                         #LineBot's Friend's user id 
app = Flask(__name__)


def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None


def saveUserId(userId):
        idFile = open('idfile', 'a')
        idFile.write(userId+';')
        idFile.close()

def pullMsg():
    data = DAN.pull('Msg-O')
    while data == None:
        print('Pulling Msg-O')
        data = DAN.pull('Msg-O')
        time.sleep(0.5)
    return data


@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    if '溫度' in Msg:
        data = cw.web_crawler()
        print(data)
        print(data['temp_103'])
        DAN.push ('Msg-I', data['temp_103'])
        time.sleep(0.5)
        odf = pullMsg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="{}度".format(odf[0])))
    elif '濕度' in Msg:
        data = cw.web_crawler()
        print(data['temp_103'])
        DAN.push ('Msg-I', data['hum_103'])
        time.sleep(0.5)
        odf = pullMsg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="{}%".format(odf[0])))
    else:
        print('收到:{}'.format(Msg))
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="輸入\"溫度\"或\"濕度\"以查詢"))
    
    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)


   
if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    try:
        for userId in user_id_set:
            line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
            for i in range(3):
                line_bot_api.push_message(userId, TextSendMessage(text='Push Message {}'.format(i)))
            while True:
                try:
                    ODF_data = pullMsg()#Pull data from an output device feature "Dummy_Control"
                    if ODF_data != None:
                        print (ODF_data[0])
                        line_bot_api.push_message(userId, TextSendMessage(text='{}'.format(ODF_data[0])))   
                except KeyboardInterrupt:
                    break

                except Exception as e:
                    print(e)
                    if str(e).find('mac_addr not found:') != -1:
                        print('Reg_addr is not found. Try to re-register...')
                        DAN.device_registration_with_retry(ServerURL, Reg_addr)
                    else:
                        print('Connection failed due to unknow reasons.')
                        time.sleep(1)    

                time.sleep(0.2)
            try:
                DAN.deregister()
            except:
                pass
    except Exception as e:
        print(e)
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

