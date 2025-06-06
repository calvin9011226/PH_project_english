from flask import Flask, request, jsonify
from random import randrange
import json
import os
import pandas as pd
import numpy as np
import csv
import datetime
import googlemaps
import populartimes  # 第三方模組，用來解析熱門時段資料
from linebot import LineBotApi, WebhookHandler
from linebot.models.events import PostbackEvent
from linebot.models import *
import XGBOOST_predicted
import ML
import Search
import Now_weather
import Filter
import PLan3MYSQL
import Plan2MYSQL
import FlexMessage
import Googlemap_function
import get_location
import plan_location
import PH_Attractions
import urllib.parse
import time
from config import PLAN_2DAY, PLAN_3DAY, PLAN_4DAY, PLAN_5DAY, LOCATION_FILE
import math

app = Flask(__name__)

# 設定 Line Bot API：先嘗試從環境變數讀取，如果沒有，請手動設定（僅供測試用）
access_token = os.getenv("LINE_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")
if not access_token or not secret:
    print("❌ LINE_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未設定，請確認環境變數或手動設定")
    access_token = "your_line_access_token_here"
    secret = "your_line_channel_secret_here"

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 新增 safe_reply() 函式，避免使用無效的 reply token 拋出錯誤
def safe_reply(reply_token, messages):
    try:
        line_bot_api.reply_message(reply_token, messages)
    except Exception as e:
        print(f"safe_reply 發生錯誤: {e}")

# 使用 push_message 傳送訊息（不依賴 reply token）
def safe_push(user_id, messages):
    try:
        line_bot_api.push_message(user_id, messages)
    except Exception as e:
        print(f"safe_push 發生錯誤: {e}")

# 使用 DDNS URL（或 ngrok URL）
PHP_ngrok = "https://flask-service2.peterlinebot.ip-ddns.com"

# 全域變數，記錄使用者年齡與性別，以及等待輸入狀態
age_1, gender_1 = None, None
approveAgeRespond = False
approveGender = False

# Google 表單的 URL
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeT7kHB3bsE7rmxqJdzG42XfSS9ewNBBZPVH3xxunpYVcyDag/viewform?usp=header"

# 請在此設定您的 Google API 金鑰
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def update_plan_csv_with_populartimes(plan_csv_file):
    """
    更新 CSV：讀取位置檔案、計算各景點行走距離、人潮等資訊，並依據距離及人潮排序後更新排名。
    """
    location_csv_file = "C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv"
    loc_df = pd.read_csv(location_csv_file, header=None, usecols=[1,2], encoding='utf-8-sig')
    loc_df.columns = ['lat', 'lng']
    user_lat = float(loc_df.at[0, 'lat'])
    user_lng = float(loc_df.at[0, 'lng'])
    print("使用者位置：", user_lat, user_lng)

    plan_df = pd.read_csv(plan_csv_file, encoding='utf-8-sig')
    for col, default in [('place_id', ""), ('crowd', 0), ('distance', 0.0), ('crowd_rank', 0)]:
        if col not in plan_df.columns:
            plan_df[col] = default

    gmaps_client = googlemaps.Client(key=GOOGLE_API_KEY)
    
    for i, row in plan_df.iterrows():
        poi = row['設置點']
        try:
            lat = float(row['緯度'])
            lon = float(row['經度'])
        except Exception as e:
            print(f"錯誤：無法取得 {poi} 的緯度或經度: {e}")
            continue
        
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

        crowd_value = 0
        if place_id:
            try:
                pop_data = populartimes.get_id(GOOGLE_API_KEY, place_id)
                now = datetime.datetime.now()
                weekday = now.weekday()  # 0: 星期一
                current_hour = now.hour
                if pop_data.get('populartimes') and len(pop_data['populartimes']) > weekday:
                    day_data = pop_data['populartimes'][weekday]
                    data = day_data.get('data', [])
                    if len(data) > current_hour:
                        crowd_value = data[current_hour]
            except Exception as e:
                print(f"Error retrieving crowd data for {poi}: {e}")
        plan_df.at[i, 'crowd'] = crowd_value

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
        print(f"{poi} 的行走距離：{distance_km:.2f} 公里")

    plan_df['crowd'] = pd.to_numeric(plan_df['crowd'], errors='coerce').fillna(0).astype(int)
    plan_df.sort_values(['crowd', 'distance'], ascending=[True, True], inplace=True)
    plan_df['crowd_rank'] = range(1, len(plan_df) + 1)
    
    if 'distance' in plan_df.columns:
        plan_df.drop(columns=['distance'], inplace=True)
    
    plan_df.to_csv(plan_csv_file, index=False, encoding='utf-8-sig')
    print("CSV file updated with place_id, crowd and crowd_rank data (distance not included).")

def process_travel_planning(option, reply_token, user_id):
    """
    根據選擇的行程規劃選項（例如 "兩天一夜"）進行推薦處理，
    reply_token 僅用於立即回覆，後續結果透過 push_message 傳送。
    """
    global age_1, gender_1
    print(f"處理行程規劃選項: {option}")
    if gender_1 is None or age_1 is None:
        safe_reply(reply_token, TextSendMessage("請先輸入年齡和性別再選擇行程規劃！"))
        return

    # 立即回覆提示，避免 token 過期
    #safe_reply(reply_token, TextSendMessage("已開始規劃，請稍等"))

    try:
        plan_data = pd.read_csv(PLAN_2DAY if option=="兩天一夜" else 
                                PLAN_3DAY if option=="三天兩夜" else 
                                PLAN_4DAY if option=="四天三夜" else 
                                PLAN_5DAY, encoding='utf-8-sig')
    except Exception as e:
        print(f"無法讀取 CSV 檔案: {e}")
        safe_push(user_id, TextSendMessage("行程資料讀取失敗，請稍後再試"))
        return

    try:
        userID = ML.XGboost_plan(plan_data, gender_1, age_1)
        print(f"推薦 User ID: {userID}")
    except Exception as e:
        print(f"XGboost_plan 執行失敗: {e}")
        safe_push(user_id, TextSendMessage("行程推薦失敗，請稍後再試"))
        return

    try:
        Filter.filter(PLAN_2DAY if option=="兩天一夜" else 
                      PLAN_3DAY if option=="三天兩夜" else 
                      PLAN_4DAY if option=="四天三夜" else 
                      PLAN_5DAY, userID)
        csv_plan = "C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/plan.csv"
        update_plan_csv_with_populartimes(csv_plan)
        Plan2MYSQL.plan2mysql(csv_plan)
    except Exception as e:
        print(f"資料處理失敗: {e}")
        safe_push(user_id, TextSendMessage("行程資料處理失敗，請稍後再試"))
        return

    try:
        location_file = "C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv"
        lat, lon = get_location.get_location(location_file)
        print(f"使用者位置: lat={lat}, lon={lon}")
    except Exception as e:
        safe_push(user_id, TextSendMessage("無法取得您的位置，請重新傳送位置資訊"))
        return

    # 以 push_message 傳送後續資訊與路線選項說明
    safe_push(user_id, [
    FlexMessage.ask_route_option(),  # 傳送 Flex Message，讓使用者選擇路線規劃選項
    TextSendMessage(f"以機器學習依據相關性，找尋過往數據最適合您的{option}行程"),
    TextSendMessage(
        "【系統路線】依照人潮較少規劃\n"
        "1. 整段規劃：一次性顯示完整路線（紅線）。\n"
        "2. 分段規劃：逐段規劃，每段完成後按『下一步』顯示（藍線）。\n"
        "3. 清除系統路線：清除所有系統路線。"
    ),
    TextSendMessage(
        "【使用者路線】\n"
        "1. 點選標記內『加入路線』將景點加入清單。\n"
        "2. 一次性規劃：顯示使用者路線（綠線）。\n"
        "3. 分段規劃：逐段規劃，每段完成後按『下一步』顯示（橘線）。\n"
        "4. 清除：清除使用者路線。"
    )
])


@app.route("/", methods=["GET", "POST"])
def linebot_route():
    global age_1, gender_1, approveAgeRespond, approveGender
    try:
        body = request.get_data(as_text=True)
        print(f"📥 收到請求: {body}")
        json_data = json.loads(body)

        if not json_data.get("events") or len(json_data.get("events")) == 0:
            print("無事件資料，直接回傳 OK")
            return "OK"

        for event in json_data['events']:
            # 取得 userId 供 push_message 使用
            user_id = event['source'].get('userId')
            if "message" in event:
                tk = event['replyToken']
                msg_type = event['message']['type']
                if msg_type == 'text':
                    msg = event['message']['text']
                    print(f"收到訊息: {msg}")
                    if msg in ["男", "女", "其他"]:
                        print(f"直接輸入性別: {msg}")
                        gender_1 = FlexMessage.classify_gender(msg)
                        safe_reply(tk, [FlexMessage.ask_location()])
                        return 'OK'
                    if msg in ["系統路線", "使用者路線"]:
                        location_file = "C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv"
                        try:
                            lat, lon = get_location.get_location(location_file)
                            print(f"使用者位置: lat={lat}, lon={lon}")
                        except Exception as e:
                            print(f"無法取得使用者位置: {e}")
                            safe_reply(tk, TextSendMessage("無法取得您的位置，請重新傳送位置資訊"))
                            return 'OK'
                        
                        url = f"{PHP_ngrok}/PengHu_system_plan.php?lat={lat}&lng={lon}" if msg=="系統路線" else f"{PHP_ngrok}/PengHu_people_plan.php?lat={lat}&lng={lon}"
                        safe_reply(tk, TextSendMessage(text=url))
                        return 'OK'
                    if approveAgeRespond:
                        try:
                            print(f"detect age = {msg}")
                            if 0 <= int(msg) <= 120:
                                age_1 = int(msg)
                                approveAgeRespond = False
                                message = FlexMessage.gender_reply("性別類型", "請輸入您的性別", 
                                                                   "男", "男", "男", 
                                                                   "女", "女", "女", 
                                                                   "其他", "其他", "其他")
                                safe_reply(tk, message)
                                approveGender = True
                            else:
                                print(f"data overflow or underflow: {msg}")
                                safe_reply(tk, TextSendMessage("請輸入\"正確年紀\""))
                        except Exception as e:
                            print(f"age type error: {msg}, {e}")
                            safe_reply(tk, TextSendMessage("請輸入\"正確年紀\""))
                        return 'OK'
                    if msg in ["兩天一夜", "三天兩夜", "四天三夜", "五天四夜"]:
                        process_travel_planning(msg, tk, user_id)
                        return 'OK'
                    if msg == "行程規劃" or msg == "6":
                        print("行程規劃功能觸發")
                        safe_reply(tk, [
                            TextSendMessage("請選擇您的行程規劃天數，將以大數據推薦行程"),
                            FlexMessage.travel_reply("行程規劃",
                                                     "兩天一夜", "兩天一夜", "兩天一夜",
                                                     "三天兩夜", "三天兩夜", "三天兩夜",
                                                     "四天三夜", "四天三夜", "四天三夜",
                                                     "五天四夜", "五天四夜", "五天四夜")
                        ])
                    elif msg == "景點推薦" or msg == "2":
                        print("景點推薦功能觸發")
                        safe_reply(tk, [
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
                    elif msg == "一般景點推薦" or msg == "2-2":
                        print(msg)
                        if gender_1 is None:
                            gender_1 = -1
                        if age_1 is None:
                            age_1 = 30

                        weather = Now_weather.weather()
                        temperature = Now_weather.temperature()
                        arr = np.array([weather])
                        tidal = Now_weather.tidal()
                        print("輸入參數:", arr, gender_1, age_1, tidal, temperature)
                        
                        try:
                            recommend = XGBOOST_predicted.XGboost_recommend2(arr, gender_1, age_1, tidal, temperature)
                            print("推薦結果:", recommend)
                        except Exception as e:
                            print(f"❌ XGBoost 預測錯誤: {e}")
                            safe_reply(tk, TextSendMessage("系統錯誤，請稍後再試"))
                            return 'OK'
                        
                        encoded_destination = urllib.parse.quote(recommend)
                        route_finder_url = f"https://3614-59-102-234-91.ngrok-free.app/test.php?destination={encoded_destination}"
                        print("推薦結果:", recommend)
                        
                        try:
                            recommend_website, recommend_imgur, recommend_map = PH_Attractions.Attractions_recommend(recommend)
                            print(recommend_website, recommend_imgur, recommend_map)
                        except Exception as e:
                            print(f"❌ Attractions 推薦錯誤: {e}")
                            safe_reply(tk, TextSendMessage("景點推薦錯誤，請稍後再試"))
                            return 'OK'
                        
                        safe_push(user_id, [
                            TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                            TextSendMessage(str(recommend)),
                            ImageSendMessage(original_content_url=str(recommend_imgur) + ".jpg", preview_image_url=str(recommend_imgur) + ".jpg"),
                            TextSendMessage(recommend_website),
                            TextSendMessage(recommend_map)
                        ])
                    elif msg == "永續觀光" or msg == "2-1":
                        print(msg)
                        if gender_1 is None:
                            gender_1 = -1
                        if age_1 is None:
                            age_1 = 30
                        try:
                            gender_val = float(gender_1)
                        except Exception as e:
                            print("轉換 gender_1 為 float 失敗:", e)
                            gender_val = 0.0
                        if gender_val < 0:
                            print("⚠️ 永續觀光功能：檢測到 gender 為負數 ({}), 強制設定為 0".format(gender_val))
                            gender_val = 0.0
                        weather = Now_weather.weather()
                        temperature = Now_weather.temperature()
                        arr = np.array([weather])
                        tidal = Now_weather.tidal()
                        print("輸入參數:", arr, gender_val, age_1, tidal, temperature)
                        
                        try:
                            recommend = ML.XGboost_recommend3(arr, gender_val, age_1, tidal, temperature)
                            print("推薦結果:", recommend)
                        except Exception as e:
                            print(f"❌ 永續觀光預測錯誤: {e}")
                            safe_reply(tk, TextSendMessage("永續觀光推薦失敗，請稍後再試"))
                            return 'OK'
                        
                        try:
                            recommend_website, recommend_imgur, recommend_map = PH_Attractions.Attractions_recommend1(recommend)
                        except Exception as e:
                            print(f"❌ Attractions 推薦錯誤: {e}")
                            safe_reply(tk, TextSendMessage("景點推薦錯誤，請稍後再試"))
                            return 'OK'
                        
                        safe_push(user_id, [
                            TextSendMessage("感謝等待\n系統以AI大數據機器學習的方式推薦以下適合您的地點"),
                            TextSendMessage(str(recommend)),
                            ImageSendMessage(original_content_url=str(recommend_imgur)+".jpg", preview_image_url=str(recommend_imgur)+".jpg"),
                            TextSendMessage(recommend_website),
                            TextSendMessage(recommend_map)
                        ])
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
                        safe_reply(tk, [survey_message, button_template])
                    elif msg == "景點人潮" or msg == "3":
                        print("景點人潮分析功能觸發")
                        safe_reply(tk, [
                            TextSendMessage("請點選以下網址，將由大數據為您分析這時間的人潮"),
                            TextSendMessage(str(PHP_ngrok) + "/PengHu_crowd2.php")
                        ])
                    elif msg == "附近搜尋" or msg == "4":
                        print("附近搜尋功能觸發")
                        safe_reply(tk, FlexMessage.ask_keyword())
                    elif msg in ["餐廳", "停車場", "風景區", "住宿"]:
                        print(f"{msg} 搜尋功能觸發")
                        try:
                            lat, lon = get_location.get_location("C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv")
                            Googlemap_function.googlemap_search_nearby(lat, lon, msg)
                            carousel_contents = FlexMessage.Carousel_contents("C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/recommend.csv")
                            safe_reply(tk, FlexMessage.Carousel(carousel_contents))
                        except Exception as e:
                            print(f"❌ 附近搜尋功能錯誤: {e}")
                            safe_reply(tk, TextSendMessage("附近搜尋功能錯誤，請稍後再試"))
                            return 'OK'
                    elif msg == "景點":
                        print("景點推薦網址功能觸發")
                        safe_reply(tk, [
                            TextSendMessage("請點選以下網址，將為您推薦附近景點"),
                            TextSendMessage(str(PHP_ngrok) + "/attration.php")
                        ])
                    elif msg == "租車" or msg == "5":
                        print("租車推薦功能觸發")
                        safe_reply(tk, [
                            TextSendMessage("請點選以下網址，將為您推薦租車店家"),
                            TextSendMessage(str(PHP_ngrok) + "/car_rent.php")
                        ])
                    elif msg == "收集資料&修改資料" or msg == "1":
                        print("收集資料功能觸發")
                        safe_reply(tk, TextSendMessage("請輸入你的年紀"))
                        approveAgeRespond = True
                    else:
                        print(f"未處理訊息: {msg}")
                elif event['message']['type'] == 'location':
                    add = event['message'].get('address', '')
                    lat = event['message']['latitude']
                    lon = event['message']['longitude']
                    print(f"收到位置: {add}, lat: {lat}, lon: {lon}")
                    try:
                        with open("C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv", 'w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([add, lat, lon])
                        safe_reply(tk, TextSendMessage("資料儲存完畢\n請根據您的需求點選下方圖文選單,來獲得相對應的功能"))
                        print("結束使用「收集資料功能」\n------------------")
                    except Exception as e:
                        print(f"❌ 位置資料儲存錯誤: {e}")
                        safe_reply(tk, TextSendMessage("位置資料儲存錯誤，請稍後再試"))
            else:
                print("收到非 message 事件")
        return 'OK'
    except Exception as e:
        print(f"❌ 錯誤處理訊息: {e}")
        print(f"收到的原始內容: {body}")
        return jsonify({"status": "error", "message": str(e)}), 500

@handler.add(PostbackEvent)
def handle_postback(event):
    global age_1, gender_1
    postback_data = event.postback.data
    print(f"收到 Postback: {postback_data}")
    user_id = event.source.get('userId')
    
    if postback_data in ["兩天一夜", "三天兩夜", "四天三夜", "五天四夜"]:
        process_travel_planning(postback_data, event.reply_token, user_id)
    elif postback_data in ["男", "女", "其他"]:
        print(f"使用者選擇性別: {postback_data}")
        gender_1 = FlexMessage.classify_gender(postback_data)
        safe_reply(event.reply_token, [FlexMessage.ask_location()])
    elif postback_data in ["系統路線", "使用者路線"]:
        location_file = "C:/Users/user/Desktop/Penghu/PH_project_v1-main/PH_project_v1-main/penghu_csv_file/location.csv"
        try:
            lat, lon = get_location.get_location(location_file)
            print(f"使用者位置: lat={lat}, lon={lon}")
        except Exception as e:
            print(f"無法取得使用者位置: {e}")
            safe_reply(event.reply_token, TextSendMessage("無法取得您的位置，請重新傳送位置資訊"))
            return
        
        url = f"{PHP_ngrok}/system_route.php?lat={lat}&lng={lon}" if postback_data=="系統路線" else f"{PHP_ngrok}/user_route.php?lat={lat}&lng={lon}"
        safe_reply(event.reply_token, TextSendMessage(text=url))
    elif postback_data == "需要幫助":
        print("使用者請求幫助")
        reply_array = [
            ImageSendMessage(original_content_url='https://imgur.com/8AKsigL.png', preview_image_url='https://imgur.com/8AKsigL.png'),
            ImageSendMessage(original_content_url='https://imgur.com/bXnZJLP.png', preview_image_url='https://imgur.com/bXnZJLP.png'),
            ImageSendMessage(original_content_url='https://imgur.com/QXc788f.png', preview_image_url='https://imgur.com/QXc788f.png'),
            ImageSendMessage(original_content_url='https://imgur.com/BwqfFxs.png', preview_image_url='https://imgur.com/BwqfFxs.png')
        ]
        safe_reply(event.reply_token, reply_array)

if __name__ == "__main__":
    print("🚀 啟動 Flask 伺服器...")
    app.run(host="0.0.0.0", port=8000, debug=True)
