from flask import Flask, request
#from gevent.pywsgi import WSGIServer
from random import randrange
# 載入 json 標準函式庫，處理回傳的資料格式
import json
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models.events import PostbackEvent
#from linebot.exceptions import InvalidSignatureError
#from linebot.models import MessageEvent, TextMessage, TextSendMessage 
from linebot.models import *
#from xgboost import XGBClassifier
import csv
import Search
import urllib.parse

access_token = 'Lw2nJ8Dx7FfPEkMMWu2qmivQGp7/Z8/ZR0Yww4JO6SAWGVMu6AaJeO0dDSf+4RsrJWDy5d6rMcGU3gVd0/Qz/Tgu3kQR2bOothKf6CgyvlN2DqdoLi1Zt704CRjXEOLMV3z+3jsz25NfXBK7urHgWAdB04t89/1O/w1cDnyilFU='
secret = '3f0e6c03c17e4b5227013e377aa3d335'
line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
handler = WebhookHandler(secret)                     # 確認 secret 是否正確

#詢問旅遊天數
def travel_reply(Title,label1,text1,data1,label2,text2,data2,label3,text3,data3,label4,text4,data4):
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    #print("body:",body)
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token

        bubble = BubbleContainer(
            direction='ltr',
            #最上層
            hero=ImageComponent(
                    url='https://i.imgur.com/o2S08In.png',
                    size='full',
                    aspect_ratio='2:1',
                    aspect_mode='cover',
            ),
            #中間層
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text="請選擇您的行程規劃天數",size='xl',color='#000000')
                ],
            ),
            #最下層
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label1,text=text1,data=data1)
                    ),
                    SeparatorComponent(color='#000000'),
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label2,text=text2,data=data2)#(一定要有label和data)data設定為傳到handle_postback的值，text為使用者這邊跳出的文字
                    ),
                    SeparatorComponent(color='#000000'),
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label3,text=text3,data=data3)#(一定要有label和data)data設定為傳到handle_postback的值，text為使用者這邊跳出的文字
                    ),
                    SeparatorComponent(color='#000000'),
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label4,text=text4,data=data4)#(一定要有label和data)data設定為傳到handle_postback的值，text為使用者這邊跳出的文字
                    )
                ]
            ),
        )
        message=FlexSendMessage(alt_text=Title,contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))
         
#訊問是否要繼續
def ask_continue():
    body = request.get_data(as_text=True)    
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        
        bubble = BubbleContainer(
            direction='ltr',
            #中間層
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="是否繼續查詢",size='xl',color='#4C0099',align= "center")
                ],
            ),
            #最下層
            footer=BoxComponent(
                layout='horizontal',
                spacing='xs',
                contents=[
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label="是，請繼續",text="是，請繼續",data="是，請繼續")
                    )
                ]
            ),
        )
        message=FlexSendMessage(alt_text="是否繼續",contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))

#請求傳送位置資訊
def ask_location():
    body = request.get_data(as_text=True)    
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        
        bubble = BubbleContainer(
            direction='ltr',
            #中間層
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="請告訴系統您目前的位置",size='xl',color='#4C0099',align= "center")
                ],
            ),
            #最下層
            footer=BoxComponent(
                layout='horizontal',
                spacing='xs',
                contents=[
                    BoxComponent(
                        layout='horizontal',
                        spacing='xs',
                        contents=[
                            ButtonComponent(
                                style='secondary',
                                color='#FFEE99',
                                height='sm',
                                action=PostbackAction(label="需要幫助",text="需要幫助",data="需要幫助")
                            ),
                            ButtonComponent(
                                style='secondary',
                                color='#FFEE99',
                                height='sm',
                                action=PostbackAction(label="好",text="好",data="好")
                            )
                        ]
                    )
                ]
            ),
        )
        message=FlexSendMessage(alt_text="請傳送位置資訊",contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))

#訊問關鍵字
def ask_keyword():
    body = request.get_data(as_text=True)    
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        
        bubble = BubbleContainer(
            direction='ltr',
            #最上層
            hero=ImageComponent(
                    url='https://zh-tw.skyticket.com/guide/wp-content/uploads/2020/12/shutterstock_1086233933.jpg',
                    align= "center",
                    size='full',
                    aspect_ratio='20:15',
                    aspect_mode='cover',
            ),
            #中間層
            body=BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text="請選擇搜尋的關鍵字",size='xl',color='#4C0099',align= "center")
                ]
            ),
            #最下層
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    BoxComponent(
                        layout='vertical',
                        spacing='xs',
                        contents= [
                            BoxComponent(
                                layout='horizontal',
                                spacing='xs',
                                contents= [
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents= [
                                            ImageComponent(
                                                url = "https://th.bing.com/th/id/OIP.bz7UqgUAkIQZ_l5BA8WQ0AHaHa?pid=ImgDet&w=512&h=512&rs=1",
                                                aspectRatio = "1:1",
                                                aspectMode = "cover",
                                                size = "md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="風景區",text="風景區",data="風景區")
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents= [
                                            ImageComponent(
                                                url = "https://thumb.silhouette-ac.com/t/d8/d8a7e9674d55ca5fe9173b02cc4fb7dd_w.jpeg",
                                                aspectRatio = "1:1",
                                                aspectMode = "cover",
                                                size = "md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="餐廳",text="餐廳",data="餐廳")
                                            )
                                        ]
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                spacing='xs',
                                contents= [
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents= [
                                            ImageComponent(
                                                url = "https://th.bing.com/th/id/OIP.VgsoPsjpE4Pb9BRWjZ5tFwAAAA?pid=ImgDet&rs=1",
                                                aspectRatio = "1:1",
                                                aspectMode = "cover",
                                                size = "md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="停車場",text="停車場",data="停車場")
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='vertical',
                                        spacing='xs',
                                        contents= [
                                            ImageComponent(
                                                url = "https://png.pngtree.com/png-vector/20190623/ourlarge/pngtree-hotel-icon-png-image_1511479.jpg",
                                                aspectRatio = "1:1",
                                                aspectMode = "cover",
                                                size = "md"
                                            ),
                                            ButtonComponent(
                                                style='secondary',
                                                color='#FFEE99',
                                                height='sm',
                                                action=MessageAction(label="住宿",text="住宿",data="住宿")
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        message=FlexSendMessage(alt_text="選擇關鍵字",contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))
         
#店家資訊
def recommend(name,price_level,rating,img_url,location,place_id):
    body = request.get_data(as_text=True)  
    #web_url,img_url,map_url = Search.Attractions_recommend(name)
    component=Rating_Component(rating)
    try:
        #map_url=f'https://www.google.com/maps/place/?q=place_id:{place_id}' #舊的搜尋方法
        map_url = f'https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}'
        #print("Google Maps URL:", map_url) #確認google地址可不可以使用
    except Exception:
        map_url="no information"
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        
        bubble = BubbleContainer(
            direction='ltr',
            #最上層
            hero=ImageComponent(
                    url=img_url,
                    align= "center",
                    size='full',
                    aspect_ratio='20:15',
                    aspect_mode='cover',
            ),
            #中間層
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=name,size='xl',color='#000000'),
                    BoxComponent(
                        layout='baseline',
                        margin = 'md',
                        contents=component
                    ),
                    TextComponent(text="價格等級:"+price_level,size='md',color='#000000')
                ]
            ),
            #最下層
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=[
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=URIAction(
                            label='地圖',
                            uri=map_url,  # 設定要跳轉的網頁連結
                        )
                    )
                ]    
            )
                
        )
        
        message=FlexSendMessage(alt_text=name,contents=bubble)
        return bubble
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))

#星等
def Rating_Component(rating):
    rating=float(rating)
    rating=str(rating)
    integer_part, decimal_part = rating.split('.')
    integer_part = int(integer_part)
    decimal_part = int(decimal_part)
    component = []
    
    for _ in range(integer_part):
        icon_component = IconComponent(
            size='sm',
            url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
        )
        component.append(icon_component)
    if integer_part==0:
        integer_part=1
    if integer_part<5:
        if(decimal_part<4):
            icon_component = IconComponent(
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
            )
            component.append(icon_component)
        elif(3<decimal_part<8):
            icon_component = IconComponent(
                size='sm',
                url="https://i.imgur.com/8eAZJ80.png"
            )
            component.append(icon_component)
        else:
            icon_component = IconComponent(
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
            )
            component.append(icon_component)
        integer_part=integer_part+1
    if (integer_part) < 5:
        for _ in range(5-integer_part):
            icon_component = IconComponent( 
                size='sm',
                url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
            )
            component.append(icon_component)
    text_component = TextComponent(
                        text=rating,
                        size='sm',
                        color="#999999",
                        margin="md",
                        flex=0
                    )
    component.append(text_component)
    return component

#很多店家資訊
def Carousel(carousel_contents):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        carousel_flex_message = CarouselContainer(
            contents = carousel_contents
        )
        message=FlexSendMessage(alt_text='店家資訊',contents=carousel_flex_message)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))

#
def Carousel_contents(file):
    with open(file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        carousel_contents = []
        contents = []
        rows = list(reader)
        n = min(10, len(rows))
        i = 1
        for row in rows:
            contents = recommend(row[0], row[1], row[2], row[3], row[4], row[5])
            carousel_contents.append(contents)
            if i == n:
                break
            i += 1

    return carousel_contents


#詢問要在哪裡找尋飯店
def Plan_hotel(Plan_contents):
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        
        bubble = BubbleContainer(
            direction='ltr',
            #最上層
            hero=ImageComponent(
                    url='https://th.bing.com/th/id/R.93316e4363d28d99e9ecd8debc5e57de?rik=hhiGLzuuawAWsQ&pid=ImgRaw&r=0',
                    size='full',
                    aspect_ratio='2:1',
                    aspect_mode='cover',
            ),
            #中間層
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text="您要在哪個景點搜尋民宿",size='xl',color='#000000')
                ],
            ),
            #最下層
            footer=BoxComponent(
                layout='vertical',
                spacing='xs',
                contents=Plan_contents
            )
        )
        message=FlexSendMessage(alt_text="選擇景點",contents=bubble)
        return message
    except:
         line_bot_api.reply_message(tk,TextSendMessage("發生錯誤"))
         
def Plan_contents(file):  
    with open(file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # 跳過標頭行
        plan_contents = []
        rows = list(reader)
        n = min(10, len(rows))
        i = 1
        for row in rows:
            contents=ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=TextSendMessage(label=row[4],text=row[4],data=row[4])
                    ) 
            plan_contents.append(contents)
            
            if i == n:
                break
            i += 1
    return plan_contents
#print(Plan_contents("C:/Users/roy88/testproject/python/linebot/ph/plan.csv"))

def gender_reply(Title,question,label1,text1,data1,label2,text2,data2,label3,text3,data3):
    try:
        
        bubble = BubbleContainer(
            direction='ltr',
            #最上層
            hero=ImageComponent(
                    url="https://th.bing.com/th/id/R.c0c0ea7da18a703a414e22914b4b7ad3?rik=79Ben6v2hTid9A&pid=ImgRaw&r=0",
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
            ),
            #中間層
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=question,size='xl',color='#000000',align='center')
                ],
            ),
            #最下層
            footer=BoxComponent(
                layout='vertical',
                spacing='xs', 
                contents=[
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label1,text=text1,data=data1)
                    ),
                    SeparatorComponent(color='#000000'),
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label2,text=text2,data=data2)#(一定要有label和data)data設定為傳到handle_postback的值，text為使用者這邊跳出的文字
                    ),
                    SeparatorComponent(color='#000000'),
                    # websiteAction
                    ButtonComponent(
                        style='secondary',
                        color='#FFEE99',
                        height='sm',
                        action=PostbackAction(label=label3,text=text3,data=data3)#(一定要有label和data)data設定為傳到handle_postback的值，text為使用者這邊跳出的文字
                    ),
                    SeparatorComponent(color='#000000'),
                ]
            ),
        )
        message=FlexSendMessage(alt_text=Title,contents=bubble)
        return message
    except:
        print("ERROR")
        
def classify_gender(gender):
    if gender=="男":
        gender = 1
    elif gender=="女":
         gender = 0 
    elif gender=="其他":
        gender = -1  
    return gender