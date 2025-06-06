"""
import pandas as pd
import datetime as dt
import googlemaps
from populartimes import get_id

GOOGLE_API_KEY = "AIzaSyBkBeV2pKxDvLzQmcCe1X6jkqWMFhVXiuI"

def build_history_crowd_table(history_csv_file):
    df = pd.read_csv(history_csv_file)
    df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df = df.dropna(subset=['Time'])
    df['Hour'] = df['Time'].dt.hour
    history_crowd = df.groupby(['設置點', 'Hour']).size().reset_index(name='history_count')
    return history_crowd

def build_populartimes_table(place_list, gmaps):
    rows = []
    for place in place_list:
        try:
            res = gmaps.find_place(input=place, input_type="textquery", fields=["place_id"])
            if res.get("candidates"):
                place_id = res["candidates"][0]["place_id"]
                pop_data = get_id(GOOGLE_API_KEY, place_id)
                for day_data in pop_data.get("populartimes", []):
                    for hour, value in enumerate(day_data.get("data", [])):
                        rows.append({"設置點": place, "Hour": hour, "populartimes_count": value})
        except Exception as e:
            print(f"❌ {place} 無法抓取 populartimes：{e}")
        print("build_populartimes_table 完成度")
    return pd.DataFrame(rows)

def analyze_correlation(history_csv_file):
    print("\n📊 開始計算歷史人潮與 populartimes 的每小時相關係數\n")
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    # 步驟一：歷史人潮統計
    history_table = build_history_crowd_table(history_csv_file)
    print("\n 取得歷史人潮資料")

    # 步驟二：抓取 populartimes 資料
    place_list = history_table['設置點'].unique()
    populartimes_table = build_populartimes_table(place_list, gmaps)
    print("\n 取得 populartimes 資料")

    # 步驟三：合併兩份資料
    merged = pd.merge(history_table, populartimes_table, on=['設置點', 'Hour'])
    print("\n 合併 populartimes 和 歷史人潮資料")

    # 步驟四：依據每個地點計算 Pearson correlation
    result = []
    for place in merged['設置點'].unique():
        sub = merged[merged['設置點'] == place]
        if len(sub) >= 5:
            corr = sub['history_count'].corr(sub['populartimes_count'])
            result.append({"設置點": place, "相關係數": round(corr, 3), "資料筆數": len(sub)})
        else:
            result.append({"設置點": place, "相關係數": None, "資料筆數": len(sub)})
    print("\n計算相關係數")

    # 輸出分析結果
    result_df = pd.DataFrame(result)
    print(result_df.sort_values(by='相關係數', ascending=False).to_string(index=False))
    return result_df

# 使用範例：
analyze_correlation("./penghu_csv_file/Beacon20220907-crowd.csv")
"""


import pandas as pd
import datetime as dt
import googlemaps
from populartimes import get_id
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import os
import matplotlib.pyplot as plt

#讓plt可以顯示中文
plt.rcParams["font.family"] = "DFKai-SB"  
plt.rcParams["axes.unicode_minus"] = False 

GOOGLE_API_KEY = "AIzaSyB25tMdD2SXv7VWi7JMT5DD0sR1ON9WCw4"

def build_history_crowd_table(history_csv_file):
    df = pd.read_csv(history_csv_file)
    df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df = df.dropna(subset=['Time'])
    df['Hour'] = df['Time'].dt.hour
    history_crowd = df.groupby(['設置點', 'Hour']).size().reset_index(name='history_count')
    return history_crowd

def build_populartimes_table(place_list, gmaps, save_path=None,input_path=None):
    if input_path is None:      
        rows = []
        i=0
        for place in place_list:
            try:
                res = gmaps.find_place(input=place, input_type="textquery", fields=["place_id"])
                if res.get("candidates"):
                    place_id = res["candidates"][0]["place_id"]
                    pop_data = get_id(GOOGLE_API_KEY, place_id)
                    yesterday_idx = (dt.datetime.today().weekday() - 1) % 7
                    
                    for j, day_data in enumerate(pop_data.get("populartimes", [])):
                        if j == yesterday_idx:
                            for hour, value in enumerate(day_data.get("data", [])):
                                rows.append({"設置點": place, "Hour": hour, "populartimes_count": value})
                    i += 1
                print(f"populartimes完成度:{round(i/len(place_list)*100,3)}%")
            except Exception as e:
                    print(f"❌ {place} 無法抓取 populartimes：{e}")


        df = pd.DataFrame(rows)
        
        # ✅ 如果給定儲存路徑，就把結果寫出來
        if save_path:
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"✅ populartimes 資料已儲存至：{save_path}")
    else:
        df = pd.read_csv(input_path)
    
    return df

def analyze_correlation(history_csv_file,intime_csv_file=None,result_csv_file=None,yesterday="2025"):
    print("\n📊 開始計算歷史人潮與 populartimes 的每小時相關係數與誤差指標\n")
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    # 步驟一：歷史人潮統計
    history_table = build_history_crowd_table(history_csv_file)
    print("\n ✅ 取得歷史人潮資料")

    # 步驟二：抓取 populartimes 資料
    place_list = history_table['設置點'].unique()
    populartimes_table = build_populartimes_table(place_list, gmaps,intime_csv_file)
    print("\n ✅  取得 populartimes 資料")

    # 步驟三：合併兩份資料
    merged = pd.merge(history_table, populartimes_table, on=['設置點', 'Hour'])
    print("\n ✅  合併 populartimes 和 歷史人潮資料")


    # 步驟四：依據每個地點計算 Pearson correlation、MAE、MSE
    result = []
    #print(merged['設置點'].unique())
    for place in merged['設置點'].unique():
        sub = merged[merged['設置點'] == place]
        #print(sub)
        if len(sub) >= 5:
            total_history = sub['history_count'].sum()
            total_popular = sub['populartimes_count'].sum()
            #print("history_count:",sub['history_count'])
            #print("populartimes_count:",sub['populartimes_count'])
            corr = sub['history_count'].corr(sub['populartimes_count'])
            #print(corr)
            mae = mean_absolute_error(sub['history_count'], sub['populartimes_count'])
            mse = mean_squared_error(sub['history_count'], sub['populartimes_count'])

            result.append({
                "設置點": place,
                "相關係數": round(corr, 3),
                "MAE": round(mae, 2),
                "MSE": round(mse, 2),
                "歷史人潮總數": total_history,
                "populartimes 總數": total_popular,
                "資料筆數": len(sub)
            })
        else:
            result.append({
                "設置點": place,
                "相關係數": None,
                "MAE": None,
                "MSE": None,
                "歷史人潮總數": total_history,
                "populartimes 總數": total_popular,
                "資料筆數": len(sub)
            })

    result_df = pd.DataFrame(result)
    #print(result_df.sort_values(by='相關係數', ascending=False).to_string(index=False))
    result_df.to_csv(result_csv_file, index=False, encoding='utf-8-sig')
    print("✅ 地點分析結果已儲存至 correlation_result.csv")

    # 額外：畫出每小時的相關係數折線圖（跨景點）
    hourly_corrs = []
    hourly_mae = []
    for hour in range(24):
        sub = merged[merged['Hour'] == hour]
        if len(sub) >= 1:
            corr = sub['history_count'].corr(sub['populartimes_count'])
            mae = mean_absolute_error(sub['history_count'], sub['populartimes_count'])
            mse = mean_squared_error(sub['history_count'], sub['populartimes_count'])
            hourly_corrs.append(corr)
            hourly_mae.append(mae)
        else:
            hourly_corrs.append(np.nan)
            hourly_mae.append(np.nan)
    
    plt.figure(figsize=(10, 5))
    plt.plot(range(24), hourly_mae, marker='x', linestyle='-', linewidth=2)
    plt.title(f"每小時歷史人潮與及時人潮的 MAE\n{yesterday}", fontsize=24)
    plt.xlabel("小時 (Hour)", fontsize=16)
    plt.ylabel("MAE", fontsize=16)
    plt.xticks(range(24))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"./penghu_csv_file/histroy_intime/intime-crowd{yesterday}.png")

    plt.figure(figsize=(10, 5))
    plt.plot(range(24), hourly_corrs, marker='o', linestyle='-', linewidth=2)
    plt.title(f"每小時歷史人潮與及時人潮的相關係數\n{yesterday}", fontsize=24)
    plt.ylabel("相關係數", fontsize=16)
    plt.xticks(range(24))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"./penghu_csv_file/histroy_intime/result_相關係數{yesterday}.png")

    return result_df

# 使用範例：

yesterday = (dt.datetime.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
analyze_correlation("./penghu_csv_file/Beacon20220907-crowd.csv",f"./penghu_csv_file/histroy_intime/intime-crowd{yesterday}.csv",f"./penghu_csv_file/histroy_intime/result_相關係數{yesterday}.csv",yesterday)
