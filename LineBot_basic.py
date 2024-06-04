# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import time, random, requests
import DAN
import crawl_weather_V8 as cw
import os
import csv

ServerURL = 'https://2.iottalk.tw/'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
Reg_addr = '170.1.3' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'LineBot Device'
DAN.profile['df_list']=['Msg-I', 'Msg-O']
DAN.profile['d_name']= '170_Dummy_Device_1'

DAN.device_registration_with_retry(ServerURL, Reg_addr)

line_bot_api = LineBotApi('4i4FncKooWFGmj3ueylc7KeK7hCTv74mdIb8yXo6kuzgBKvobSS0TEtYr+6AblXnVmyNT4v4DZCu80bhlTtLmdKAqG6m4LZhnURi85YmUR7eyzwFIPNWtXhfM6r/7GygMDbanmYhfjb2jJNSz07fHwdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
handler = WebhookHandler('7c4b10c631ec30a9a9a8a88aa186fea8')        #LineBot's Channel secret
user_id_set=set()                                         #LineBot's Friend's user id 
app = Flask(__name__)

def pull_Msg():
    data = DAN.pull('Msg-O')
    while data == None:
        print('Pulling Msg-O')
        data = DAN.pull('Msg-O')
        time.sleep(0.5)
    return data

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
        cw.crawl_weather()
        print(cw.temp[0])
        DAN.push ('Msg-I', cw.temp[0])
        time.sleep(0.5)
        odf = pull_Msg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="{}度".format(odf[0])))
    elif '濕度' in Msg:
        cw.crawl_weather()
        DAN.push ('Msg-I', cw.hum[0])
        time.sleep(0.5)
        odf = pull_Msg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="{}%".format(odf[0])))
    else:
        print('GotMsg:{}'.format(Msg))
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
    except Exception as e:
        print(e)
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

