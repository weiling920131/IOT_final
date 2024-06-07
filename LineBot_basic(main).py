# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError 
# from linebot.models import MessageEvent, TextSendMessage, TextMessage

# from linebot.v3 import LineBotApi, WebhookHandler
# from linebot.v3.models import TextMessage, PushMessageRequest
# from linebot.v3.messaging import MessagingApi, Configuration
# from linebot.v3.messaging.models import TextMessage, PushMessageRequest

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)


import time
import DAN,threading

ServerURL = 'https://1.iottalk.tw/'      #with non-secure connection
Reg_addr = '103.1.3' #if None, Reg_addr = MAC address

DAN.profile['dm_name'] = 'LineBot'
DAN.profile['df_list']=['Msg-I', 'Msg-O']
DAN.profile['d_name']= '103_Dummy_Device'

DAN.device_registration_with_retry(ServerURL, Reg_addr)
configuration = Configuration(access_token='4i4FncKooWFGmj3ueylc7KeK7hCTv74mdIb8yXo6kuzgBKvobSS0TEtYr+6AblXnVmyNT4v4DZCu80bhlTtLmdKAqG6m4LZhnURi85YmUR7eyzwFIPNWtXhfM6r/7GygMDbanmYhfjb2jJNSz07fHwdB04t89/1O/w1cDnyilFU=')
# messaging_api = MessagingApi(configuration)
# messaging_api = MessagingApi(channel_access_token='') #LineBot's Channel access token
handler = WebhookHandler('7c4b10c631ec30a9a9a8a88aa186fea8')  
# line_bot_api = LineBotApi('Qc1Aa6fKTU3re63L/LJiI3nGfbzbAnmvBqlvELR3LBeLMYgLT+6hhxK9S+zGu9tTAPbKiy7sC8kk5fRSFmc6Z7+siufo52tSNks/SwqrlFM3daHL093Mcylq2fUID/0713n1e30LCrmJKmKBQ6N3hAdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
# handler = WebhookHandler('e40f04844ce6c0b7ed2c7f2df55945b1')        #LineBot's Channel secret
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


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     Msg = event.message.text
#     print(Msg)
#     DAN.push ('Msg-I', Msg)
#     time.sleep(0.5)
#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text=event.message.text)]
#             )
#         )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    Msg = event.message.text
    DAN.push ('Msg-I', Msg[0])
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )


def output():
    while True:
        ODF_data = pullMsg()#Pull data from an output device feature "Dummy_Control"
        if ODF_data != None:
            print (ODF_data[0])
            for userId in user_id_set:
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                # line_bot_api.push_message(userId, TextSendMessage(text=ODF_data[0]))  # Push API examples
                pass


        time.sleep(0.2)

   
if __name__ == "__main__":
    thread = threading.Thread(target=output)
    thread.daemon = True
    thread.start()

    idList = loadUserId()
    print(idList)
    if idList: user_id_set = set(idList)
    try:
        for userId in user_id_set:
            pass
            # line_bot_api.push_message(userId, TextMessage(text='LineBot is ready for you.'))  # Push API example
            # push_message_request = PushMessageRequest(
            #     to=userId,
            #     messages=[TextMessage(text='LineBot is ready for you.')]
            # )
            # response = messaging_api.push_message(push_message_request)

    except Exception as e:
        print(e)
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

