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
import pandas as pd
import numpy as np
import csv
from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import XGBOOST_predicted
import ML
import Search
import Now_weather
import Filter
import Plan2MYSQL
import FlexMessage
from get_PHP_token import start_ngrok
import Googlemap_function
import get_location
import plan_location
import PH_Attractions
import urllib.parse
import time
import googlemaps
import populartimes  # 第三方模組，用來解析熱門時段資料
from linebot.models import TextSendMessage

#以下為測試
import pymysql
from collections import Counter
from datetime import datetime
from linebot.models import TextSendMessage



app = Flask(__name__)

path="./penghu_csv_file"
access_token = 'Lw2nJ8Dx7FfPEkMMWu2qmivQGp7/Z8/ZR0Yww4JO6SAWGVMu6AaJeO0dDSf+4RsrJWDy5d6rMcGU3gVd0/Qz/Tgu3kQR2bOothKf6CgyvlN2DqdoLi1Zt704CRjXEOLMV3z+3jsz25NfXBK7urHgWAdB04t89/1O/w1cDnyilFU='
secret = '3f0e6c03c17e4b5227013e377aa3d335'
line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
handler = WebhookHandler(secret)                     # 確認 secret 是否正確
#PHP_ngrok ="https://723e-123-241-68-148.ngrok-free.app"# 80
PHP_ngrok =start_ngrok(port=80)                         #只要啟動ngrok服務就會自動抓PHP_ngrok
print(PHP_ngrok)
global age_1 ,gender_1

# Google 表單的 URL
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe0MUssdGPeLqZFTEkBDJy4VBf5k2jsefT-QCA0iNbdau-j_A/viewform"

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    global approveGender
    global approveAgeRespond

    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            #功能1
            if msg == "行程規劃"or msg =="6":
                print(msg)
                # line_bot_api.reply_message(tk,TextSendMessage(msg)) # 回傳訊息
                # line_bot_api.reply_message(tk,TextSendMessage("請選擇您的行程規劃天數，將以大數據推薦行程"))
                line_bot_api.reply_message(tk,[TextSendMessage("請選擇您的行程規劃天數，將以大數據推薦行程"),FlexMessage.travel_reply("行程規劃","兩天一夜","兩天一夜","兩天一夜","三天兩夜","三天兩夜","三天兩夜","四天三夜","四天三夜","四天三夜","五天四夜","五天四夜","五天四夜")])               
            #功能2
            elif msg == "景點推薦" or msg == "2":
                print(msg)
                line_bot_api.reply_message(tk, [
                    TemplateSendMessage(
                        alt_text='請選擇是或否',
                        template=ConfirmTemplate(
                            text='您是否希望系統推薦永續觀光景點？',
                            actions=[
                                MessageAction(label='是', text='永續觀光'),
                                MessageAction(label='否', text='一般景點推薦')
                            ]
                        )
                    )
                    
                ])
            elif msg == "一般景點推薦"or msg =="2-2":
                print(msg)
                dont_go_here,message_text=people_high5(tk)       #人潮太多,不推薦
                print(message_text)
                weather = Now_weather.weather()
                temperature = Now_weather.temperature()
                
                #weather = "雨"
                # temperature = randrange(15,24)
                arr = np.array([weather])
                tidal = Now_weather.tidal()
                # tidal = randrange(0,2)
                # gender = randrange(0,2)
                age = randrange(15,55)
                global age_1,gender_1 #測試用
                print(arr,gender_1,age_1,tidal,temperature)

                #為了展示是否有考慮人潮
                recommend = XGBOOST_predicted.XGboost_recommend2(arr,gender_1,age_1,tidal,temperature,[])
                for dont_go_here_list in dont_go_here:
                    if recommend ==dont_go_here_list:
                        clowd_message=f"\n\n{recommend} 的人潮太多,所以改推薦 "
                        recommend = XGBOOST_predicted.XGboost_recommend2(arr,gender_1,age_1,tidal,temperature,dont_go_here)
                        clowd_message=clowd_message+recommend
                        break
                    else:
                        clowd_message=""

                encoded_destination = urllib.parse.quote(recommend)
                route_finder_url = f"https://3614-59-102-234-91.ngrok-free.app/test.php?destination={encoded_destination}"
                print("推薦地點:",recommend) #推薦的地點是從XGBOOST_predicted來的
                
                recommend_website,recommend_imgur,recommend_map = PH_Attractions.Attractions_recommend(recommend)#圖片,網址,map是從PH_Attractions來的
                print(recommend_website,recommend_imgur,recommend_map)
                line_bot_api.reply_message(tk,[TextSendMessage(f"感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                      TextSendMessage(str(recommend+clowd_message)),
                                                      ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg",preview_image_url=str(recommend_imgur)+".jpg"),
                                                      TextSendMessage(recommend_website),
                                                      TextSendMessage(recommend_map)
                                                      ])
                
                # ************************************************************************************************
                
                # line_bot_api.reply_message(
                #     tk,
                #     [
                #         TextSendMessage("感謝等待\n系統已推薦以下適合您的地點"),
                #         TextSendMessage(str(recommend)),
                #         TextSendMessage(f"點擊以下連結查看到該地點的路線：\n{route_finder_url}")
                #     ]
                # )
                
            elif msg == "永續觀光"or msg =="2-1":#測試功能
                print(msg)
                dont_go_here,message_text=people_high5(tk)       #人潮太多,不推薦
                print(message_text)

                weather = Now_weather.weather()
                temperature = Now_weather.temperature()
                arr = np.array([weather])
                tidal = Now_weather.tidal()
                print(arr,gender_1,age_1,tidal,temperature)

                recommend = ML.XGboost_recommend3(arr,gender_1,age_1,tidal,temperature,[])
                for dont_go_here_list in dont_go_here:
                    if recommend ==dont_go_here_list:
                        clowd_message=f"\n\n{recommend} 的人潮太多,所以改推薦 "
                        recommend = ML.XGboost_recommend3(arr,gender_1,age_1,tidal,temperature,dont_go_here)
                        clowd_message=clowd_message+recommend
                        break
                    else:
                        clowd_message=""
                print("推薦地點:",recommend) #推薦的地點是從XGboost_recommend3來的
                recommend_website,recommend_imgur,recommend_map = PH_Attractions.Attractions_recommend1(recommend)#圖片,網址,map是從PH_Attractions來的
                line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                      TextSendMessage(str(recommend+clowd_message)),
                                                      ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg",preview_image_url=str(recommend_imgur)+".jpg"),
                                                      TextSendMessage(recommend_website),
                                                      TextSendMessage(recommend_map)
                                                      ])
                '''
                recommend_website,recommend_imgur,recommend_map = Search.Attractions_recommend(recommend)
                line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                TextSendMessage(str(recommend)),
                                                ImageSendMessage(original_content_url=str(recommend_imgur),preview_image_url=str(recommend_imgur)),
                                                TextSendMessage(recommend_website),
                                                TextSendMessage(recommend_map)
                                                 ])
                '''                 
            # beta "填寫問卷"
            elif msg == "填寫問卷(先關閉)":
                survey_message = TextSendMessage(text="請點擊以下連結填寫問卷：")
                button_template = TemplateSendMessage(
                    alt_text='問卷連結',
                    template=ButtonsTemplate(
                        title='填寫問卷',
                        text='請點擊下方按鈕開始填寫問卷',
                        actions=[
                            URIAction(
                                label='開始填寫',
                                uri=GOOGLE_FORM_URL
                            )
                        ]
                    )
                )
                line_bot_api.reply_message(tk, [survey_message, button_template])                
            #功能3
            elif msg == "景點人潮"or msg=="3":
                print(msg)
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將由大數據為您分析這時間的人潮"),TextSendMessage(str(PHP_ngrok)+"/PengHu_crowd2.php")])
            #功能4
            elif msg == "附近搜尋"or msg =="4":
                print(msg)
                line_bot_api.reply_message(tk,FlexMessage.ask_keyword())
            elif msg == "餐廳" or msg == "停車場" or msg == "風景區" or msg == "住宿":
                print(msg)
                lat,lon=get_location.get_location(f'{path}/location.csv')
                Googlemap_function.googlemap_search_nearby(lat,lon,msg)
                carousel_contents=FlexMessage.Carousel_contents(f'{path}/recommend.csv')
                line_bot_api.reply_message(tk,FlexMessage.Carousel(carousel_contents)) 
            elif msg == "景點":
                print(msg)                                       # 印出內容
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將為您推薦附近景點"),TextSendMessage(str(PHP_ngrok)+"/attration.php")])

            #功能5
            elif msg == "租車" or msg =="5":
                line_bot_api.reply_message(tk, [TextSendMessage("請點選以下網址，將為您推薦租車店家"),TextSendMessage(str(PHP_ngrok)+"/car_rent.php")])

            # # 測試用
            # elif msg == "資料":
            #     print(msg)
            #     global age_1
            #     print(age_1)
            #     reply = f"您目前的年齡是: {age_1} 歲"
            #     line_bot_api.reply_message(tk, TextSendMessage(reply))

            ############################# 測試功能 ##############################################
            elif msg == "景點人潮test" :
                print(msg)
                try:
                    # 連線資料庫，資料來源與 PengHu_crowd2.php 相同
                    conn = pymysql.connect(
                        host='127.0.0.1',
                        user='root',
                        password='nclab722',
                        db='penghu',
                        charset='utf8'
                    )
                    cursor = conn.cursor()
                    # 讀取資料表 test 中的 setpoint（景點名稱）與 time（紀錄時間）
                    sql = "SELECT setpoint, time FROM test"
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    
                    # 取得目前時間的 24 小時制小時數（例如 13 代表下午1點）
                    now = datetime.now()
                    current_hour = now.hour
                    
                    # 建立一個 Counter 用來統計每個景點在當前小時的紀錄筆數
                    crowd_counter = Counter()
                    for row in results:
                        place = row[0]  # 景點名稱
                        time_str = row[1]  # 例如 "2/1/2022 1:07:51 PM"
                        try:
                            # 解析時間字串，假設格式為 "%m/%d/%Y %I:%M:%S %p"
                            record_time = datetime.strptime(time_str, "%m/%d/%Y %I:%M:%S %p")
                            # 若該筆紀錄與目前時間相同（小時），則計數
                            if record_time.hour == current_hour:
                                crowd_counter[place] += 1
                        except Exception as e:
                            print(f"時間解析錯誤: {time_str}, {e}")
                    
                    # 若沒有符合當前時段的資料，則回傳提示訊息
                    if not crowd_counter:
                        reply_message = TextSendMessage(text="目前無法取得當前時段的人潮資料。")
                    else:
                        # 取出人潮數量最多的前五名
                        top5 = crowd_counter.most_common(5)
                        message_text = "目前人潮最壅擠的前五個景點：\n"
                        for idx, (place, count) in enumerate(top5, start=1):
                            message_text += f"{idx}. {place} - 人潮數量：{count}\n"
                        reply_message = TextSendMessage(text=message_text)
                    
                    # 回覆訊息給使用者
                    line_bot_api.reply_message(tk, [reply_message])
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"資料庫連線或處理錯誤: {e}")
                    line_bot_api.reply_message(tk, [TextSendMessage(text="資料取得失敗，請稍後再試。")])
                    
            ###########################################################################    

            #功能6
            elif msg == "收集資料&修改資料"or msg=="1":
                print(msg)
                line_bot_api.reply_message(tk,TextSendMessage("請輸入你的年紀"))
                approveAgeRespond=True
            elif approveAgeRespond==True:
                try:
                    age=msg #儲存age
                    print("detect age=",age)
                    if 0<=int(age) and int(age)<=120:
                        age_1=int(age) #測試用
                        approveAgeRespond=False
                        message=FlexMessage.gender_reply("性別類型","請輸入您的性別","男","男","男","女","女","女","其他","其他","其他")
                        line_bot_api.reply_message(tk,message)
                        approveGender=True

            
                    #年紀不合常理
                    else:
                        print("data overflow or underflow", age)
                        line_bot_api.reply_message(tk,TextSendMessage("請輸入\"正確年紀\""))
                #其他錯誤
                except Exception as e:
                    print("age type error", age)
                    line_bot_api.reply_message(tk,TextSendMessage("請輸入\"正確年紀\""))  
                 
            else :
                print(msg)                                       # 印出內容
                reply = msg
                # line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息

        if type=='location':
                add = json_data['events'][0]['message']['address']  # 取得 LINE 收到的文字訊息
                lat = json_data['events'][0]['message']['latitude']  # 取得 LINE 收到的文字訊息
                lon = json_data['events'][0]['message']['longitude']  # 取得 LINE 收到的文字訊息
                print(add, lat, lon)
                with open(f'{path}/location.csv', 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([add, lat, lon])
                line_bot_api.reply_message(tk,TextSendMessage("資料儲存完畢\n請根據您的需求點選下方圖文選單,來獲得相對應的功能"))
                print("結束使用\"收集資料功能\" \n------------------") 

    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

                                        
def people_high5(tk):                                 # 找尋人潮最多的前五名
    try:
        # 連線資料庫，資料來源與 PengHu_crowd2.php 相同
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='nclab722',
            db='penghu',
            charset='utf8'
        )
        cursor = conn.cursor()
        # 讀取資料表 test 中的 setpoint（景點名稱）與 time（紀錄時間）
        sql = "SELECT setpoint, time FROM test"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 取得目前時間的 24 小時制小時數（例如 13 代表下午1點）
        now = datetime.now()
        current_hour = now.hour
        
        # 建立一個 Counter 用來統計每個景點在當前小時的紀錄筆數
        crowd_counter = Counter()
        high5_place=["","","","",""]

        for row in results:
            place = row[0]  # 景點名稱
            time_str = row[1]  # 例如 "2/1/2022 1:07:51 PM"
            try:
                # 解析時間字串，假設格式為 "%m/%d/%Y %I:%M:%S %p"
                record_time = datetime.strptime(time_str, "%m/%d/%Y %I:%M:%S %p")
                # 若該筆紀錄與目前時間相同（小時），則計數
                if record_time.hour == current_hour:
                    crowd_counter[place] += 1
            except Exception as e:
                print(f"時間解析錯誤: {time_str}, {e}")
        
        # 若沒有符合當前時段的資料，則回傳提示訊息
        if not crowd_counter:
            reply_message = TextSendMessage(text="目前無法取得當前時段的人潮資料。")
        else:
            # 取出人潮數量最多的前五名
            top5 = crowd_counter.most_common(5)
            message_text = "目前人潮最壅擠的前五個景點：\n"
            for idx, (place, count) in enumerate(top5, start=1):
                message_text += f"{idx}. {place} - 人潮數量：{count}\n"
                high5_place[idx-1]=place
            #reply_message = TextSendMessage(text=message_text)
        
        # 回覆訊息給使用者
        #line_bot_api.reply_message(tk, [reply_message])
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"資料庫連線或處理錯誤: {e}")
        line_bot_api.reply_message(tk, [TextSendMessage(text="資料取得失敗，請稍後再試。")])
    #print(high5_place)
    return high5_place,message_text
########################################################################### 




@handler.add(PostbackEvent)
def handle_postback(event):
    # 取得 Postback Action 傳送的資料
    postback_data = event.postback.data
    if postback_data =="兩天一夜":
            global age_1,gender_1 #測試用
            print("2days")
            print(gender_1)
            gender = randrange(0,2)
            age = randrange(15,55)
            file=f'{path}/plan_2day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender_1,age_1)  
            print(userID,gender,age)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql(f'{path}/plan.csv')

            # _____________________測試________________________________________________
            # 從 location.csv 檔案中獲取最新的位置資訊
            lat, lon = get_location.get_location(f'{path}/location.csv')
            print("lat and lon :", lat ,lon)
            # 將位置資訊加入 URL
            url = f"{PHP_ngrok}/PengHu_plan.php?lat={lat}&lng={lon}"
            line_bot_api.reply_message(event.reply_token, [
            TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的兩天一夜行程"),
            TextSendMessage(url)
            ])
            # _____________________測試________________________________________________

            # line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的兩天一夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan_old.php")])
            
    elif postback_data =="三天兩夜":
            print("3days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file=f'{path}/plan_3day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql(f'{path}/plan.csv')
            
            # _____________________測試________________________________________________
            # 從 location.csv 檔案中獲取最新的位置資訊
            lat, lon = get_location.get_location(f'{path}/location.csv')
            print("lat and lon :", lat ,lon)
            # 將位置資訊加入 URL
            url = f"{PHP_ngrok}/PengHu_plan.php?lat={lat}&lng={lon}"
            line_bot_api.reply_message(event.reply_token, [
            TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的三天兩夜行程"),
            TextSendMessage(url)
            ])
            # _____________________測試________________________________________________
            
            # line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的三天兩夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan_old.php")]) //舊版本
    
    elif postback_data =="四天三夜":
            print("4days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file=f'{path}/plan_4day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql(f'{path}/plan.csv')
                        
            # _____________________測試________________________________________________
            # 從 location.csv 檔案中獲取最新的位置資訊
            lat, lon = get_location.get_location(f'{path}/location.csv')
            print("lat and lon :", lat ,lon)
            # 將位置資訊加入 URL
            url = f"{PHP_ngrok}/PengHu_plan.php?lat={lat}&lng={lon}"
            line_bot_api.reply_message(event.reply_token, [
            TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的四天三夜行程"),
            TextSendMessage(url)
            ])
            # _____________________測試________________________________________________
            
            # line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的四天三夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
    elif postback_data =="五天四夜":
            print("5days")
            gender = randrange(0,2)
            age = randrange(15,55)
            file=f'{path}/plan_5day.csv'
            plan_data = pd.read_csv(file,encoding='utf-8-sig')
            userID = ML.XGboost_plan(plan_data,gender,age)  
            print(userID)
            Filter.filter(file,userID)
            Plan2MYSQL.plan2mysql(f'{path}/plan.csv')
                        
            # _____________________測試________________________________________________
            # 從 location.csv 檔案中獲取最新的位置資訊
            lat, lon = get_location.get_location(f'{path}/location.csv')
            print("lat and lon :", lat ,lon)
            # 將位置資訊加入 URL
            url = f"{PHP_ngrok}/PengHu_plan.php?lat={lat}&lng={lon}"
            line_bot_api.reply_message(event.reply_token, [
            TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的五天四夜行程"),
            TextSendMessage(url)
            ])
            # _____________________測試________________________________________________
            
            # line_bot_api.reply_message(event.reply_token, [TextSendMessage("以使用機器學習依據相關性，找尋過往數據最適合您的五天四夜行程"),TextSendMessage(str(PHP_ngrok)+"/PengHu_plan.php")])
    elif postback_data=="男" or postback_data=="女" or postback_data=="其他":

            # gender=postback_data
            # gender=FlexMessage.classify_gender(gender)
            # global gender_1 #測試用
            gender_1=postback_data
            gender_1=FlexMessage.classify_gender(gender_1)#測試用
            # print(gender_1)
            line_bot_api.reply_message(event.reply_token, [FlexMessage.ask_location()])
    if postback_data=="需要幫助" :
        reply_array=[]
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/8AKsigL.png',preview_image_url='https://imgur.com/8AKsigL.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/bXnZJLP.png',preview_image_url='https://imgur.com/bXnZJLP.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/QXc788f.png',preview_image_url='https://imgur.com/QXc788f.png'))
        reply_array.append(ImageSendMessage(original_content_url='https://imgur.com/BwqfFxs.png',preview_image_url='https://imgur.com/BwqfFxs.png'))
        line_bot_api.reply_message(event.reply_token,reply_array)
if __name__ == "__main__":
    app.run()