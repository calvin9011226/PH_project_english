from flask import Flask, request, jsonify,render_template
from random import randrange
import json
import os
import pandas as pd
import numpy as np
import csv
import googlemaps
import populartimes  # 第三方模組，用來解析熱門時段資料

from linebot import LineBotApi, WebhookHandler
from linebot.models.events import PostbackEvent
from linebot.models import *
import XGBOOST_predicted
import ML
import Now_weather
import Filter
import Mysql_Management
import FlexMessage
import Googlemap_function
import get_location
import PH_Attractions
import urllib.parse
import pymysql
import time
import datetime as dt
from datetime import datetime as dt_now
from Analyze_datasteam import Log,CodeTimer,Analyze,timer_stop_log
from static.Language_memger import Keyword,error_information,information
from collections import Counter
from linebot.models import TextSendMessage
from dotenv import load_dotenv
from get_PHP_token import start_ngrok
app = Flask(__name__)

load_dotenv()  # read .env file
Penghu_csv_file=os.getenv("Penghu_csv_file")
PLAN_2DAY=f'{Penghu_csv_file}/plan_2day.csv'
PLAN_3DAY=f'{Penghu_csv_file}/plan_3day.csv'
PLAN_4DAY=f'{Penghu_csv_file}/plan_4day.csv'
PLAN_5DAY=f'{Penghu_csv_file}/plan_5day.csv' 
Ues_Language=os.getenv("Language")

MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_PORT=int(os.getenv("MYSQL_PORT"))
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE")


access_token=os.getenv("ACCESS_TOKEN")
secret =os.getenv("SECRET")
line_bot_api = LineBotApi(access_token)              
handler = WebhookHandler(secret)  

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

# As long as the ngrok service is started, PHP_ngrok will be automatically captured port 5000
PHP_ngrok =start_ngrok(port=5000)         
#print(PHP_ngrok)


""" Analyze_datasteam: Just to monitor the resource consumption of the entire project"""
#全部
log = Log(Auto_Clear=True,File_Only=True,File_Name="all/all_log",choose=["no"],Print_Funct="warning")
timer = CodeTimer(Print_Funct="warning")
analyze=Analyze(Print_Funct="warning")

#行程規劃
log2 = Log(Auto_Clear=True,File_Only=True,File_Name="vs/timely_history_log",choose=["no"],Print_Funct="warning")
timer2 = CodeTimer(Print_Funct="warning")

#臨時用
log3 = Log(Auto_Clear=True,File_Only=True,File_Name="focus/focus_log",choose=["no"],Print_Funct="warning")
timer3 = CodeTimer(Print_Funct="warning")

#紀錄CPU和記憶體使用量
log4 = Log(Auto_Clear=True,File_Only=True,File_Name="CPU_Memory/efficacy",Print_Funct="warning")
analyze=Analyze(Recording_process=True,Print_Funct="warning")


# Added safe_reply() function to avoid throwing errors when using invalid reply token 
# 新增 safe_reply() 函式，避免使用無效的 reply token 拋出錯誤
def safe_reply(reply_token, messages,source="Unspecified functionality"):
    try:
        dtype, size = analyze.analyze_input(messages)
        #log.data_size(size, message=f" reply_message <{source}> \t回傳大小", data_type=dtype)
        line_bot_api.reply_message(reply_token, messages)
        return size
    except Exception as e:
        print(f"safe_reply error: {e}")

# Send messages using push_message (does not rely on reply tokens)
# 使用 push_message 傳送訊息（不依賴 reply token）
def safe_push(user_id, messages,source="Unspecified functionality"):
    try:
        line_bot_api.push_message(user_id, messages)
    except Exception as e:
        print(f"safe_push error: {e}")

# Determine whether the msg entered by the user is in the specified key list.
# 判斷使用者輸入的 msg 是否為指定 key 清單裡。
def match_option(msg, key_list):
    return msg in [Keyword(k) for k in key_list]


# Global variables, recording the user's age and gender, as well as the input waiting status
# 全域變數，記錄使用者年齡與性別，以及等待輸入狀態
age_1, gender_1 = None, None
approveAgeRespond = False


# URL of the Google Form (not enabled)
# Google 表單的 URL (未啟用)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeT7kHB3bsE7rmxqJdzG42XfSS9ewNBBZPVH3xxunpYVcyDag/viewform?usp=header"


# Read historical crowd data
# 讀取歷史人潮資料
def build_history_crowd_table(history_csv_file):
    df = pd.read_csv(history_csv_file)
    df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    # Remove data that failed to convert
    # 移除轉換失敗的資料
    df = df.dropna(subset=['Time'])

    df['Hour'] = df['Time'].dt.hour

    # 以 (設置點, Hour) 為群組統計次數
    # Count the number of times in a group by (set point, Hour)
    crowd_table = df.groupby(['設置點', 'Hour']).size().reset_index(name='crowd_count')
    return crowd_table

# Rewrite update_plan_csv to use the data we collected to fill in the crowd
# 改寫 update_plan_csv，改成用我們統計出來的資料來補 crowd
def update_plan_csv_with_history_crowd(plan_csv_file, history_crowd_table):
    location_csv_file = f"{Penghu_csv_file}/location.csv"
    loc_df = pd.read_csv(location_csv_file, header=None, usecols=[1,2], encoding='utf-8-sig')
    loc_df.columns = ['lat', 'lng']
    user_lat = float(loc_df.at[0, 'lat'])
    user_lng = float(loc_df.at[0, 'lng'])

    plan_df = pd.read_csv(plan_csv_file, encoding='utf-8-sig')
    for col, default in [('crowd', 0), ('distance', 0.0), ('crowd_rank', 0)]:
        if col not in plan_df.columns:
            plan_df[col] = default

    gmaps_client = googlemaps.Client(key=GOOGLE_API_KEY)

    now = dt.datetime.now()
    current_hour = now.hour

    for i, row in plan_df.iterrows():
        poi = row['設置點']

        # --- Query the number of people ---
        # --- 查詢人潮量 ---
        crowd_value = 0
        try:
            matched = history_crowd_table[(history_crowd_table['設置點'] == poi) & (history_crowd_table['Hour'] == current_hour)]
            if not matched.empty:
                crowd_value = int(matched.iloc[0]['crowd_count'])
        except Exception as e:
            print(f"Warning: Unable to find the crowd data of {poi} at {current_hour} from the historical crowd table: {e}")

        # --- Query walking distance ---
        # --- 查詢步行距離 ---
        try:
            lat = float(row['緯度'])    # latitude
            lon = float(row['經度'])    # longitude
            directions_result = gmaps_client.directions(f"{user_lat},{user_lng}", f"{lat},{lon}", mode="walking")
            if directions_result and len(directions_result) > 0:
                leg = directions_result[0]['legs'][0]
                distance_m = leg['distance']['value']
                distance_km = distance_m / 1000.0
            else:
                distance_km = 0.0
        except Exception as e:
            print(f"Error retrieving walking distance for {poi}: {e}")
            distance_km = 0.0
        plan_df.at[i, 'distance'] = distance_km

    # --- Sort by crowd and distance in ascending order ---
    # --- 排序 crowd+distance、小的排前面 ---
    plan_df['crowd'] = pd.to_numeric(plan_df['crowd'], errors='coerce').fillna(0).astype(int)
    plan_df.sort_values(['crowd', 'distance'], ascending=[True, True], inplace=True)
    plan_df['crowd_rank'] = range(1, len(plan_df) + 1)

    if 'distance' in plan_df.columns:
        plan_df.drop(columns=['distance'], inplace=True)

    
    required_columns = [
        'no', 'Time', 'POI', 'UserID', '設置點', '緯度', '經度', 'BPLUID',
        'age', 'gender', '天氣', 'place_id', 'crowd', 'crowd_rank'
    ]

    # Check for missing fields
    # 檢查缺失欄位
    for col in required_columns:
        if col not in plan_df.columns:
            plan_df[col] = ""

    # Reorder and archive
    # 重新排序並存檔
    plan_df = plan_df[required_columns]
    plan_df.to_csv(plan_csv_file, index=False, encoding='utf-8-sig')

    print("CSV file updated with crowd count from history and crowd_rank.")


# Update CSV: Read location files, calculate walking distance, crowds, and other information for each attraction, and update the rankings based on distance and crowds.
# 更新 CSV：讀取位置檔案、計算各景點行走距離、人潮等資訊，並依據距離及人潮排序後更新排名。
def update_plan_csv_with_populartimes(plan_csv_file,option):

    location_csv_file = f"{Penghu_csv_file}/location.csv"
    loc_df = pd.read_csv(location_csv_file, header=None, usecols=[1,2], encoding='utf-8-sig')
    loc_df.columns = ['lat', 'lng']
    user_lat = float(loc_df.at[0, 'lat'])
    user_lng = float(loc_df.at[0, 'lng'])
    print("User location ：", user_lat, user_lng)

    plan_df = pd.read_csv(plan_csv_file, encoding='utf-8-sig')
    for col, default in [('place_id', ""), ('crowd', 0), ('distance', 0.0), ('crowd_rank', 0)]:
        if col not in plan_df.columns:
            plan_df[col] = default

    gmaps_client = googlemaps.Client(key=GOOGLE_API_KEY)
    

    for i, row in plan_df.iterrows():
        
        poi = row['設置點']
        try:
            lat = float(row['緯度'])    # latitude
            lon = float(row['經度'])    # longitude
        except Exception as e:
            print(f"Error: Unable to get latitude or longitude for {poi} : {e}")
            continue

        timer3.start(tag=f"{option}-查詢place_id")
        try:
            res = gmaps_client.find_place(input=poi, input_type='textquery', fields=['place_id'])
            if res.get('candidates'):
                place_id = res['candidates'][0].get('place_id', "")
            else:
                place_id = ""
        except Exception as e:
            print(f"Error retrieving place_id for {poi}: {e}")
            place_id = ""
        plan_df.at[i, 'place_id'] = place_id
        timer_stop_log(tag=f"{option}-查詢place_id", timer=timer3, log=log3)
        #timer3.start(tag=f"{option}-查詢人潮資料")

        crowd_value = 0
        if place_id:
            try:
                timer3.start(tag=f"{option}-人潮資料_爬蟲")
                pop_data = populartimes.get_id(GOOGLE_API_KEY, place_id)
                timer_stop_log(tag=f"{option}-人潮資料_爬蟲", timer=timer3, log=log3)
                now = dt.datetime.now()
                weekday = now.weekday()  # 0: Monday
                current_hour = now.hour
                timer3.start(tag=f"{option}-人潮資料_塞選")
                if pop_data.get('populartimes') and len(pop_data['populartimes']) > weekday:
                    day_data = pop_data['populartimes'][weekday]
                    data = day_data.get('data', [])
                    if len(data) > current_hour:
                        crowd_value = data[current_hour]
                timer_stop_log(tag=f"{option}-人潮資料_塞選", timer=timer3, log=log3)
            except Exception as e:
                print(f"Error retrieving crowd data for {poi}: {e}")
        plan_df.at[i, 'crowd'] = crowd_value
        #timer_stop_log(tag=f"{option}-查詢人潮資料", timer=timer3, log=log3)
        timer3.start(tag=f"{option}-查詢步行距離")

        distance_km = 0.0
        try:
            directions_result = gmaps_client.directions(f"{user_lat},{user_lng}", f"{lat},{lon}", mode="walking")
            if directions_result and len(directions_result) > 0:
                leg = directions_result[0]['legs'][0]
                distance_m = leg['distance']['value']
                distance_km = distance_m / 1000.0
        except Exception as e:
            print(f"Error retrieving walking distance for {poi}: {e}")
        plan_df.at[i, 'distance'] = distance_km
        print(f"{poi} walking distance: {distance_km:.2f} km")
        timer_stop_log(tag=f"{option}-查詢步行距離", timer=timer3, log=log3)
        
    plan_df['crowd'] = pd.to_numeric(plan_df['crowd'], errors='coerce').fillna(0).astype(int)
    plan_df.sort_values(['crowd', 'distance'], ascending=[True, True], inplace=True)
    plan_df['crowd_rank'] = range(1, len(plan_df) + 1)
    
    if 'distance' in plan_df.columns:
        plan_df.drop(columns=['distance'], inplace=True)

   
    plan_df.to_csv(plan_csv_file, index=False, encoding='utf-8-sig')
    print("CSV file updated with place_id, crowd and crowd_rank data (distance not included).")

# Handle itinerary recommendation; reply_token used for immediate reply only.
# 根據選擇的行程規劃選項（例如 "兩天一夜"）進行推薦處理，reply_token 僅用於立即回覆，後續結果透過 push_message 傳送。
def process_travel_planning(option, reply_token, user_id,choose):

    global age_1, gender_1
    print(f"Processing Itinerary Planning options: {option}")

    # 立即回覆提示，避免 token 過期
    #safe_reply(reply_token, TextSendMessage("已開始規劃，請稍等"))
    
    try:
        plan_data = pd.read_csv(PLAN_2DAY if option==Keyword("2 Days 1 Night") else 
                                PLAN_3DAY if option==Keyword("3 Days 2 Nights") else 
                                PLAN_4DAY if option==Keyword("4 Days 3 Nights") else 
                                PLAN_5DAY, encoding='utf-8-sig')
    except Exception as e:
        print(f"Unable to read CSV file: {e}")
        safe_push(user_id, TextSendMessage(error_information("PlanLoadFailed")),"PlanLoadFailed")
        return

    timer2.start(tag="Machine Learning",group=option)
    try:
        userID = ML.XGboost_plan(plan_data, gender_1, age_1)
        print(f"Recommend User ID: {userID}")
    except Exception as e:
        print(f"XGboost_plan error: {e}")
        safe_push(user_id, TextSendMessage(error_information("PlanRecommendFailed")),"XGboost_plan error")
        return
    timer_stop_log(tag="Machine Learning",group=option, content=plan_data, timer=timer2, log=log2)

    timer2.start(tag="Attraction Filtering",group=option)
    try:
        Filter.filter(PLAN_2DAY if option==Keyword("2 Days 1 Night") else 
                      PLAN_3DAY if option==Keyword("3 Days 2 Nights") else 
                      PLAN_4DAY if option==Keyword("4 Days 3 Nights") else 
                      PLAN_5DAY, userID)
        csv_plan = f"{Penghu_csv_file}/plan.csv"
        plan_content = pd.read_csv(csv_plan, encoding='utf-8-sig')
        timer_stop_log(tag="Attraction Filtering",group=option ,content=plan_content, timer=timer2, log=log2)
        
        
        if choose=="Real-Time Crowd Data":
            timer2.start(tag="Attraction Ranking",group=option)
            update_plan_csv_with_populartimes(csv_plan,option)
            timer_stop_log(tag="Attraction Ranking",group=option, timer=timer2, log=log2)
        else:
            timer2.start(tag="Attraction Ranking",group=option)
            crowd_csv=f"{Penghu_csv_file}/Beacon20220907-crowd.csv"
            history_crowd_table = build_history_crowd_table(crowd_csv)
            update_plan_csv_with_history_crowd(csv_plan, history_crowd_table)
            timer_stop_log(tag="Attraction Ranking",group=option, timer=timer2, log=log2)

        timer2.start(tag="Data to Database",group=option)
        mysql_config={
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "database": MYSQL_DATABASE
        }
        Mysql_Management.import_plan_to_mysql(
            csv_file_path=f"{Penghu_csv_file}/plan.csv",
            full_fields=True
        )
        timer_stop_log(tag="Data to Database",group=option , timer=timer2, log=log2)

    except Exception as e:
        print(f"Data processing failed: {e}")
        safe_push(user_id, TextSendMessage(error_information("PlanProcessFailed")),"Failed to Process itinerary data")
        return

    try:
        location_file = f"{Penghu_csv_file}/location.csv"
        lat, lon = get_location.get_location(location_file)
        print(f"User location: lat={lat}, lon={lon}")
    except Exception as e:
        print(f"Unable to obtain User location: {e}")
        safe_push(user_id, TextSendMessage(error_information("LocationNotFound")),"LocationNotFound")
        return

    # 以 push_message 傳送後續資訊與路線選項說明
    response_list=[
        FlexMessage.ask_route_option(),  # 傳送 Flex Message，讓使用者選擇路線規劃選項
        TextSendMessage(information("AskRouteOption_Intro").format(option=option)),
        TextSendMessage(information("SystemRoute_Description")),
        TextSendMessage(information("UserRoute_Description"))
    ]
    safe_push(user_id, response_list,"Route Option Description")

    return response_list


@app.route("/", methods=["GET", "POST"])
def linebot_route():
    global age_1, gender_1, approveAgeRespond, approveGender
    try:
        body = request.get_data(as_text=True)
        print(f"📥 Request received: {body}")
        json_data = json.loads(body)

        if not json_data.get("events") or len(json_data.get("events")) == 0:
            print("No event data, directly return OK")
            return "OK"

        for event in json_data['events']:
            # 取得 userId 供 push_message 使用
            user_id = event['source'].get('userId')
            if "message" in event:
                tk = event['replyToken']
                msg_type = event['message']['type']
                if msg_type == 'text':
                    msg = event['message']['text']
                    if str.isdigit(msg):
                        timer.start(Keyword("Age"))
                        analyze.start_resource_watch(tag=Keyword("Age"))
                    else:
                        timer.start(msg)
                        analyze.start_resource_watch(tag=msg)
                    
                    print(f"Receive message : {msg}")
                    if match_option(msg, ["Man", "Woman", "else"]):
                        print(f"msg")
                        gender_1 = FlexMessage.classify_gender(msg)
                        size_content=safe_reply(tk, [FlexMessage.ask_location()],"定位設定")
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                        return 'OK'
                    if match_option(msg, ["SystemRoutePlanning", "UserRoutePlanning"]):
                        location_file = f"{Penghu_csv_file}/location.csv"
                        try:
                            lat, lon = get_location.get_location(location_file)
                            print(f"User location: lat={lat}, lon={lon}")
                        except Exception as e:
                            print(f"Unable to obtain User location: {e}")
                            size_content=safe_reply(tk, TextSendMessage(error_information("LocationNotFound")),"LocationNotFound")
                            return 'OK'
                        
                        url = f"{PHP_ngrok}/PengHu_system_plan.html?lat={lat}&lng={lon}" if msg==Keyword("SystemRoutePlanning") else f"{PHP_ngrok}/PengHu_people_plan.html?lat={lat}&lng={lon}"
                        size_content=safe_reply(tk, TextSendMessage(text=url),"System and User Routing Functions")
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                        
                        return 'OK'
                    if approveAgeRespond:
                        try:
                            print(f"detect age = {msg}")
                            if 0 <= int(msg) <= 120:
                                age_1 = int(msg)
                                approveAgeRespond = False
                                message = FlexMessage.gender_reply(
                                    information("GenderTitle"),     
                                    information("GenderHint"),       
                                    Keyword("Man"), Keyword("Man"), Keyword("Man"),
                                    Keyword("Woman"), Keyword("Woman"), Keyword("Woman"),
                                    Keyword("else"), Keyword("else"), Keyword("else")
                                )
                                size_content=safe_reply(tk, message,"Age")
                                timer_stop_log(tag=Keyword("Age"), size=size_content, timer=timer, log=log)
                                analyze.end_resource_watch(tag=Keyword("Age"),log=log4)
                            else:
                                print(f"data overflow or underflow: {msg}")
                                safe_reply(tk, TextSendMessage(Keyword("EnterValidAge")),"Error Age")
                                
                                
                        except Exception as e:
                            print(f"age type error: {msg}, {e}")
                            safe_reply(tk, TextSendMessage(Keyword("EnterValidAge")),"Error Age")
                            
                        return 'OK'
                    if match_option(msg, ["2 Days 1 Night", "3 Days 2 Nights", "4 Days 3 Nights","5 Days 4 Nights"]):
                        
                       # timer2.start(tag=msg,group="Real-Time Crowd Data")
                        response_list=process_travel_planning(msg, tk, user_id,"Real-Time Crowd Data")
                        #timer_stop_log(tag=msg,group="Real-Time Crowd Data", content=response_list,timer=timer2,log=log2)
                        #timer2.start(tag=msg,group="istorical Crowd Data")
                        #response_list1=process_travel_planning(msg, tk, user_id,"Historical Crowd Data")
                        #timer_stop_log(tag=msg,group="istorical Crowd Data", content=response_list1,timer=timer2,log=log2)
                        timer_stop_log(tag=msg, content=response_list,timer=timer,log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                        
                        return 'OK'
                    if msg == Keyword("Itinerary Planning") or msg == "6":
                        if age_1==None or gender_1==None: #Need to Data Collection
                            Modify_personal_information(tk,Keyword("Itinerary Planning"))
                            print(msg)
                        size_content=safe_reply(tk, [
                            TextSendMessage(information("ChooseItineraryDays")),
                            FlexMessage.travel_reply(Keyword("Itinerary Planning"),
                                                     Keyword("2 Days 1 Night") ,Keyword("2 Days 1 Night") ,Keyword("2 Days 1 Night"),
                                                     Keyword("3 Days 2 Nights"),Keyword("3 Days 2 Nights"),Keyword("3 Days 2 Nights"),
                                                     Keyword("4 Days 3 Nights"),Keyword("4 Days 3 Nights"),Keyword("4 Days 3 Nights"),
                                                     Keyword("5 Days 4 Nights"),Keyword("5 Days 4 Nights"),Keyword("5 Days 4 Nights"))
                        ],msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["Attraction Recommendation"]) or msg == "2":
                        if age_1==None or gender_1==None: #需要收集資料與修改資料
                            Modify_personal_information(tk,Keyword("Attraction Recommendation"))
                        else:
                            #from datetime import datetime
                            print(Keyword("Attraction Recommendation"))
                            size_content=safe_reply(tk, [
                                TemplateSendMessage(
                                    alt_text=information("ConfirmYesNo"),
                                    template=ConfirmTemplate(
                                        text=information("AskSustainableTourism"),
                                        actions=[
                                            MessageAction(label='Yes', text=Keyword("Sustainable Tourism")),
                                            MessageAction(label='No', text=Keyword("General Attraction Recommendation"))
                                        ]
                                    )
                                )
                            ],msg)
                            timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                            analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["General Attraction Recommendation"]) or msg =="2-2":
                        print(msg)
                        dont_go_here,message_text=people_high5(tk)       #人潮太多,不推薦
                        print(message_text)
                        weather = Now_weather.weather()
                        temperature = Now_weather.temperature()
                        
                        # weather 
                        arr = np.array([weather])
                        tidal = Now_weather.tidal()
                        print(arr,gender_1,age_1,tidal,temperature)

                        # To show whether the crowd is taken into consideration
                        # 為了展示是否有考慮人潮
                        recommend = XGBOOST_predicted.XGboost_recommend2(arr,gender_1,age_1,tidal,temperature,[])
                        for dont_go_here_list in dont_go_here:
                            if recommend ==dont_go_here_list:
                                new_place  = XGBOOST_predicted.XGboost_recommend2(arr,gender_1,age_1,tidal,temperature,dont_go_here)
                                clowd_message = information("TooCrowdedMessage").format(place=recommend,recommendation=new_place)
                                recommend = new_place
                                break
                            else:
                                clowd_message=""

                        encoded_destination = urllib.parse.quote(recommend)
                        print("recommend place:",recommend) #推薦的地點是從XGBOOST_predicted來的
                        
                        recommend_website,recommend_imgur,recommend_map = PH_Attractions.Attractions_recommend(recommend)#圖片,網址,map是從PH_Attractions來的
                        print(recommend_website,recommend_imgur,recommend_map)
                        response_list = [
                            TextSendMessage(information("AIBasedRecommendation").format(recommendation=recommend + clowd_message)),
                            ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg", preview_image_url=str(recommend_imgur)+".jpg"),
                            TextSendMessage(recommend_website),
                            TextSendMessage(recommend_map),
                            TextSendMessage(str(message_text))
                        ]
                        line_bot_api.reply_message(tk,response_list)
                        timer_stop_log(tag=msg, content=response_list, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                        # ************************************************************************************************
                        
                        # line_bot_api.reply_message(
                        #     tk,
                        #     [
                        #         TextSendMessage("感謝等待\n系統已推薦以下適合您的地點"),
                        #         TextSendMessage(str(recommend)),
                        #         TextSendMessage(f"點擊以下連結查看到該地點的路線：\n{route_finder_url}")
                        #     ]
                        # )
                        
                    elif match_option(msg, ["Sustainable Tourism"]) or msg == "2-1":  
                        print(msg)

                        # 取得不推薦的景點清單與訊息
                        dont_go_here, message_text = people_high5(tk)  # 人潮太多, 不推薦
                        print(message_text)

                        # 取得 Now_weather 模組資料，並檢查是否為 None，若是則給予預設值
                        weather = Now_weather.weather()
                        if weather is None:
                            weather = 0  # 可依需求設定預設天氣值
                        temperature = Now_weather.temperature()
                        if temperature is None:
                            temperature = 0  # 預設溫度值
                        tidal = Now_weather.tidal()
                        if tidal is None:
                            tidal = 0  # 預設潮汐值

                        # 確保 gender_1 與 age_1 有有效值
                        if gender_1 is None:
                            gender_1 = -1  # 預設性別
                        if age_1 is None:
                            age_1 = 30    # 預設年齡

                        # 轉成 numpy array 時只取 weather
                        arr = np.array([weather])
                        print(arr, gender_1, age_1, tidal, temperature)

                        # 初始推薦，不包含不推薦清單
                        recommend = ML.XGboost_recommend3(arr, gender_1, age_1, tidal, temperature, [])
                        clowd_message = ""  # 初始化訊息

                        # 檢查推薦結果是否在不推薦清單中
                        for dont_go_here_list in dont_go_here:
                            if recommend == dont_go_here_list:
                                new_place = ML.XGboost_recommend3(arr, gender_1, age_1, tidal, temperature, dont_go_here)
                                clowd_message = information("TooCrowdedMessage").format(place=recommend,recommendation=new_place)
                                recommend = new_place
                                break

                        print("recommend place:", recommend)  # 印出推薦結果

                        # 取得景點相關資訊 (圖片、網站、地圖)
                        recommend_website, recommend_imgur, recommend_map = PH_Attractions.Attractions_recommend1(recommend)
                        
                        response_list = [
                            TextSendMessage(information("AIBasedRecommendation").format(recommendation=recommend + clowd_message)),
                            ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg",preview_image_url=str(recommend_imgur)+".jpg"),
                            TextSendMessage(recommend_website),
                            TextSendMessage(recommend_map),
                            TextSendMessage(str(message_text))
                            ]
                        line_bot_api.reply_message(tk,response_list)
                        timer_stop_log(tag=msg, content=response_list, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)

                        '''
                        recommend_website,recommend_imgur,recommend_map = Search.Attractions_recommend(recommend)
                        line_bot_api.reply_message(tk,[TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                                                        TextSendMessage(str(recommend)),
                                                        ImageSendMessage(original_content_url=str(recommend_imgur),preview_image_url=str(recommend_imgur)),
                                                        TextSendMessage(recommend_website),
                                                        TextSendMessage(recommend_map)
                                                        ])
                        '''     
                    # Unimplemented function            
                    elif msg == "填寫問卷":
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
                        size_content=safe_reply(tk, [survey_message, button_template],msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["Crowd Information"]) or msg == "3":
                        print(msg)
                        size_content=safe_reply(tk, [
                            TextSendMessage(information("ClickURLForCrowdAnalysis")),
                            TextSendMessage(str(PHP_ngrok) + "/PengHu_crowd.html")
                        ],msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["Nearby Search"]) or msg == "4":
                        print(msg)
                        size_content=safe_reply(tk, FlexMessage.ask_keyword(),msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["Restaurant", "Scenic Area", "Parking Lot", "Accommodation"]):
                        print(msg)
                        try:
                            lat, lon = get_location.get_location(f"{Penghu_csv_file}/location.csv")
                            Googlemap_function.googlemap_search_nearby(lat, lon, msg)
                            carousel_contents = FlexMessage.Carousel_contents(f"{Penghu_csv_file}/recommend.csv")
                            size_content=safe_reply(tk, FlexMessage.Carousel(carousel_contents),msg)
                            timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                            analyze.end_resource_watch(tag=msg,log=log4)

                        except Exception as e:
                            print(f"❌ Nearby Search error: {e}")
                            safe_reply(tk, TextSendMessage(error_information("NearbySearchFailed")),"Nearby Search error")
                
                            return 'OK'
                    
                    elif match_option(msg, ["Car Rental Information"]) or msg == "5":
                        print(msg)
                        size_content=safe_reply(tk, [
                            TextSendMessage(information("ClickURLForCarRental")),
                            TextSendMessage(str(PHP_ngrok) + "/car_rent.html")
                        ],msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                    elif match_option(msg, ["Data Collection"]) or msg == "1":
                        print(msg)
                        size_content=safe_reply(tk, TextSendMessage(information("EnterYourAge")),msg)
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
                        approveAgeRespond = True
                    else:
                        print(f"Unprocessed messages: {msg}")
                elif msg_type == 'location':
                    timer.start(tag=msg_type)
                    analyze.start_resource_watch(tag=msg_type)
                    add = event['message'].get('address', '')
                    lat = event['message']['latitude']
                    lon = event['message']['longitude']
                    print(f"Location: {add}, lat: {lat}, lon: {lon}")

                    try:
                        with open(f"{Penghu_csv_file}/location.csv", 'w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([add, lat, lon])
                        size_content=safe_reply(tk, TextSendMessage(information("DataSaved_SelectFunction")),"location")
                        timer_stop_log(tag=msg_type, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg_type,log=log4)
                        print("Finish 「Data Collection」\n------------------")
                    except Exception as e:
                        print(f"❌ Failed to save location data: {e}")
                        size_content=safe_reply(tk, TextSendMessage(error_information("LocationSaveFailed")),"location error")
                        timer_stop_log(tag=msg, size=size_content, timer=timer, log=log)
                        analyze.end_resource_watch(tag=msg,log=log4)
            else:
                print("Non-message event received")
        return 'OK'
    
    except Exception as e:
        print(f"❌ error message: {e}")
        print(f"Original content: {body}")
        return jsonify({"status": "error", "message": str(e)}), 500

@handler.add(PostbackEvent)
def handle_postback(event):
    global age_1, gender_1
    postback_data = event.postback.data
    print(f"Postback: {postback_data}")
    user_id = event.source.get('userId')
    print('peter',user_id )
    
    if match_option(postback_data, ["2 Days 1 Night", "3 Days 2 Nights", "4 Days 3 Nights","5 Days 4 Nights"]):
        #process_travel_planning(postback_data, event.reply_token, user_id,"Real-Time Crowd Data")
        process_travel_planning(postback_data, event.reply_token, user_id,"Historical Crowd Data")
    elif match_option(postback_data, ["Man", "Woman", "else"]):
        print(f"User selects gender: {postback_data}")
        gender_1 = FlexMessage.classify_gender(postback_data)
        safe_reply(event.reply_token, [FlexMessage.ask_location()],postback_data)
    elif match_option(postback_data, ["SystemRoutePlanning", "UserRoutePlanning"]):
        location_file = f"{Penghu_csv_file}/location.csv"
        try:
            lat, lon = get_location.get_location(location_file)
            print(f"User location: lat={lat}, lon={lon}")
        except Exception as e:
            print(f"Unable to obtain User location: {e}")
            safe_reply(event.reply_token, TextSendMessage(error_information("LocationNotFound")),"LocationNotFound")
            return
        
        url = f"{PHP_ngrok}/PengHu_system_plan.html?lat={lat}&lng={lon}" if postback_data==Keyword("SystemRoutePlanning") else f"{PHP_ngrok}/PengHu_people_plan.html?lat={lat}&lng={lon}"
        safe_reply(event.reply_token, TextSendMessage(text=url),postback_data)
    elif postback_data == "需要幫助":
        print("Need to help")
        reply_array = [
            ImageSendMessage(original_content_url='https://imgur.com/8AKsigL.png', preview_image_url='https://imgur.com/8AKsigL.png'),
            ImageSendMessage(original_content_url='https://imgur.com/bXnZJLP.png', preview_image_url='https://imgur.com/bXnZJLP.png'),
            ImageSendMessage(original_content_url='https://imgur.com/QXc788f.png', preview_image_url='https://imgur.com/QXc788f.png'),
            ImageSendMessage(original_content_url='https://imgur.com/BwqfFxs.png', preview_image_url='https://imgur.com/BwqfFxs.png')
        ]
        safe_reply(event.reply_token, reply_array,postback_data)
def people_high5(tk):                                 # 找尋人潮最多的前五名
    try:
        # 連線資料庫，資料來源與 PengHu_crowd2.php 相同
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8'
        )
        cursor = conn.cursor()
        # 讀取資料表 test 中的 setpoint（景點名稱）與 time（紀錄時間）
        sql = "SELECT setpoint, time FROM test"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 取得目前時間的 24 小時制小時數（例如 13 代表下午1點）
        now = dt_now.now()
        current_hour = now.hour
        
        # 建立一個 Counter 用來統計每個景點在當前小時的紀錄筆數
        crowd_counter = Counter()
        high5_place=["","","","",""]

        for row in results:
            place = row[0]  # 景點名稱
            time_str = row[1]  # 例如 "2/1/2022 1:07:51 PM"
            try:
                # 解析時間字串，假設格式為 "%m/%d/%Y %I:%M:%S %p"
                record_time = dt_now.strptime(time_str, "%m/%d/%Y %I:%M:%S %p")
                # 若該筆紀錄與目前時間相同（小時），則計數
                if record_time.hour == current_hour:
                    crowd_counter[place] += 1
            except Exception as e:
                print(f"time error: {time_str}, {e}")
        
        # 若沒有符合當前時段的資料，則回傳提示訊息
        if not crowd_counter:
           reply_message = TextSendMessage(text=error_information("NoCrowdData"))
        else:
            # 取出人潮數量最多的前五名
            top5 = crowd_counter.most_common(5)
            message_text = information("CrowdedTop5Header")
            for idx, (place, count) in enumerate(top5, start=1):
                message_text += information("CrowdedTop5Item").format(idx=idx, place=place, count=count)
                high5_place[idx-1]=place
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database connection or processing error: {e}")
        line_bot_api.reply_message(tk, [TextSendMessage(text=error_information("DataFetchFailed"))])
    #print(high5_place)
    return high5_place,message_text
########################################################################### 

#If the name and age are not filled in, but the function needs to be able to collect and modify information
#如果沒有填寫姓名與年齡,但功能需要可以導向收集資料&修改資料
def Modify_personal_information(tk,message):
    message_return = information("RequireGenderAgeBeforeFeature").format(feature=message)
    # 建立快速回覆按鈕
    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=Keyword("Data Collection"), text=Keyword("Data Collection")))
    ])

    # 發送訊息，讓用戶可以直接點擊「收集資料&修改資料」
    line_bot_api.reply_message(
        tk, [
            TextSendMessage(
                text=str(message_return),
                quick_reply=quick_reply_buttons
            )
        ]
    )




@app.route("/generate-timeline", methods=["GET"])
def generate_timeline():
    #timer2.generate_timeline_plot(file_name="focus/timeline")
    #timer2.Function_duration(detail_timestamp=False,log_name="focus/focus_log",file_name="focus/function_time_sample")
    #timer2.Function_duration(detail_timestamp=True ,log_name="focus/focus_log",file_name="focus/function_time_detail")
    #timer.generate_timeline_plot(file_name="all/timeline")
    #timer.Function_duration(detail_timestamp=False,log_name="all/all_log",feature_mapping_style="penghu",file_name="all/function_time_sample")
    #timer.Function_duration(detail_timestamp=True ,log_name="all/all_log",feature_mapping_style="penghu" ,file_name="all/function_time_detail")
    #timer2.generate_timeline_plot(file_name="vs/timeline_history_vs_time",size_off=True)
    #timer2.Function_duration(detail_timestamp=True,log_name="vs/timely_history_log" ,title="各項功能總耗時與資料大小\n以三天兩夜為例\n",file_name="vs/function_time_detail")
    #timer2.Function_duration(detail_timestamp=False,log_name="vs/timely_history_log",title="各項功能總耗時與資料大小\n以三天兩夜為例\n",file_name="vs/function_time_sample")
    analyze.plot_resource_distribution(
    log_path="./documentary/CPU_Memory/efficacy.log",
    save_path="./documentary/CPU_Memory/resource_dist.png",
    metric="both",          
    top_n=None,              
    memory_display_unit="GB"
)
    return "✅ 時序圖已建立"

@app.route("/PengHu_system_plan.html")
def render_system_plan():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    plan_data = Mysql_Management.fetch_plan_data()
    return render_template("PengHu_system_plan.html", lat=lat, lng=lng, lang=Ues_Language, GOOGLE_API_KEY=GOOGLE_API_KEY,**plan_data)

@app.route("/PengHu_people_plan.html")
def render_people_plan():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    plan_data = Mysql_Management.fetch_plan_data()
    return render_template("PengHu_people_plan.html", lat=lat, lng=lng, lang=Ues_Language, GOOGLE_API_KEY=GOOGLE_API_KEY,**plan_data)

@app.route("/car_rent.html")
def render_car_rent():
    return render_template("car_rent.html")

@app.route("/PengHu_crowd.html")
def render_PengHu_crowd():
    data = Mysql_Management.fetch_test_table_data()
    return render_template("PengHu_crowd.html", planData=data)



if __name__ == "__main__":
    print("🚀 Run Flask Sever...")
    app.run(host="0.0.0.0", port=5000, debug=True)




