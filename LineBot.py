# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import time, threading
import DAN
# import crawl_weather_V8 as cw

ServerURL = 'https://1.iottalk.tw/'      #with non-secure connection
Reg_addr = '103.1.3' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'LineBot'
DAN.profile['df_list']=['Msg-I', 'Msg-O']
DAN.profile['d_name']= '103_Dummy_Device'

DAN.device_registration_with_retry(ServerURL, Reg_addr)

line_bot_api = LineBotApi('4i4FncKooWFGmj3ueylc7KeK7hCTv74mdIb8yXo6kuzgBKvobSS0TEtYr+6AblXnVmyNT4v4DZCu80bhlTtLmdKAqG6m4LZhnURi85YmUR7eyzwFIPNWtXhfM6r/7GygMDbanmYhfjb2jJNSz07fHwdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
handler = WebhookHandler('7c4b10c631ec30a9a9a8a88aa186fea8')        #LineBot's Channel secret
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
        # print('Pulling Msg-O')
        data = DAN.pull('Msg-O')
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
    DAN.push('Msg-I', Msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Msg))
    userId = event.source.user_id
    idlist = 0
    global user_id_set
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
        idlist = loadUserId()
    if idlist: user_id_set = set(idlist)

def speech2text():
    for userId in user_id_set:
        line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
        while True:
            ODF_data = pullMsg()#Pull data from an output device feature "Dummy_Control"
            if ODF_data != None:
                print (ODF_data[0])
                line_bot_api.push_message(userId, TextSendMessage(text='{}'.format(ODF_data[0])))   
               

            time.sleep(10)

   
if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    thread1 = threading.Thread(target=speech2text)
    thread1.daemon = True
    thread1.start()

    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    
