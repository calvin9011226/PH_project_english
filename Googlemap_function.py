import googlemaps
from time import sleep 

import configparser
import mysql.connector
import pandas as pd
import datetime
import csv
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()  # 讀取 .env 檔案
#api_key = "AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls"
api_key =os.getenv("GOOGLE_API_KEY")
path="./penghu_csv_file"

def googlemap_search(lat,lng):
    #get api key
    #config=configparser.ConfigParser()
    #config.read('information.ini')
    #gmaps=googlemaps.Client(key=config.get('googlemap','api_key'))
    gmaps=googlemaps.Client(key=api_key)
    #change to dictionary
    loc={'lat':lat,'lng':lng}
    #搜尋2km裡的民宿
    rad=2000
    search_number=len(gmaps.places_nearby(keyword="住宿",radius=rad,location=loc)['results'])
    
    placeID_list=[]
    for place in gmaps.places_nearby(keyword="住宿",radius=rad,location=loc)['results']:
        placeID_list.append(place['place_id'])

    hotel_info=[]
    for id in placeID_list:
        hotel_info.append(gmaps.place(place_id=id,language="zh-TW")['result'])
        sleep(0.3)
        
    name_list=[]
    loc_list=[]
    latitude_list=[]
    longtitude_list=[]
    for h in hotel_info:
        #print(h['name'])
        #print(h['geometry']['location'])
        if len(h['name'])>=50:          #如果民宿名稱的字數大於50，把40項之後的刪除
            h['name']=list(h['name'])
            del h['name'][40:len(h['name'])-1]
            h['name']=''.join(h['name'])
        name_list.append(h['name'])
        loc_list.append(h['geometry']['location'])
        latitude_list.append(h['geometry']['location']['lat'])
        longtitude_list.append(h['geometry']['location']['lng'])
        #print("結束1")
        #print("name_list=",name_list,"loc_list=",loc_list)
    #print("結束2")
    #print("共找到",search_number,"筆資料")
    #print("類型",type(hotel_info))
    #print('h',h)



    with open(f'{path}/hotel_data.csv','w+',newline='',encoding='utf-8-sig')as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(["hotel_name","latitude","longitude"])
        for x,y,z in zip (name_list,latitude_list,longtitude_list) :
            writer.writerow([x]+[y]+[z])
        print("File Write Complete")

    return search_number,name_list,loc_list
        #幾筆資料，飯店名稱，經緯度
#print(googlemap_search(25.01911370863636,121.45954571664332))


def googlemap_search_nearby(lat,lng,keyword):
    #get api keyAIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls
    #config=configparser.ConfigParser()
    #config.read('information.ini')
    #gmaps=googlemaps.Client(key=config.get('googlemap','api_key'))
    gmaps=googlemaps.Client(key=api_key)
    #change to dictionary
    loc={'lat':lat,'lng':lng}
    rad=2000
    search_number=len(gmaps.places_nearby(keyword=keyword,radius=rad,location=loc)['results'])
    
    placeID_list=[]
    for place in gmaps.places_nearby(keyword=keyword,radius=rad,location=loc)['results']:
        placeID_list.append(place['place_id'])
    print("placeID_list:",placeID_list)

    hotel_info=[]
    for id in placeID_list:
        hotel_info.append(gmaps.place(place_id=id,language="zh-TW")['result'])
        sleep(0.1)  # 避免 API 限速
    print("hotel_info:",hotel_info)   
    search_list=[]
    
    maxwidth=800
    for h in hotel_info:
        #print("check")
        if len(h['name'])>=50:          #如果名稱的字數大於50，把40項之後的刪除
            h['name']=list(h['name'])
            del h['name'][40:len(h['name'])-1]
            h['name']=''.join(h['name'])

        try:
            photoreference=h['photos'][0]['photo_reference']
            img_url=f'https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photoreference}&key={api_key}'
        except Exception:
            img_url="https://th.bing.com/th/id/R.409832a9886d51eb28e38d9f5a312cb9?rik=RoSWoLpVeJgp5A&riu=http%3a%2f%2fwww.allsense.com.tw%2fshopt%2fimages%2fs1%2fnotImg_.jpg&ehk=kZLbCtiT8lwcptfA4NEyrgaZmtH4XxJxWI8voOSAdfs%3d&risl=&pid=ImgRaw&r=0"
        #print(h)
        try:
            price_level=h['price_level']
        except Exception:
            price_level="N/A"
        try:
            rating=h['rating']
        except Exception:
            rating="0"
        
        dic={'name':h['name'],
             'price_level':price_level,
             'rating':rating,
             'img_url':img_url,
             'place_id':h["place_id"],
             'location':h['geometry']['location'],
             'place_id':h["place_id"]}
        search_list.append(dic)
        
    with open(f'{path}/recommend.csv','w+',newline='',encoding='utf-8-sig')as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(['name','price_level','rating','img_url','location','place_id'])
        search_list = sorted(search_list,key=lambda row:float(row["rating"]), reverse=True)#由高到低排序
        for h in search_list:
            writer.writerow([h['name'], h['price_level'], h['rating'], h['img_url'], h['location'],h["place_id"]])
        print("File Write Complete")
    return search_list,search_number

def googlemap_search_hotel(lng,lat):
    #get api key
    #config=configparser.ConfigParser()
    #config.read('information.ini')
    #gmaps=googlemaps.Client(key=config.get('googlemap','api_key'))
    #api_key = "AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls"
    gmaps=googlemaps.Client(key=api_key)
    #change to dictionary
    loc={'lat':lat,'lng':lng}
    #搜尋2km裡的民宿
    rad=2000
    search_number=len(gmaps.places_nearby(keyword="住宿",radius=rad,location=loc)['results'])
    
    placeID_list=[]
    for place in gmaps.places_nearby(keyword="住宿",radius=rad,location=loc)['results']:
        placeID_list.append(place['place_id'])

    hotel_info=[]
    for id in placeID_list:
        hotel_info.append(gmaps.place(place_id=id,language="zh-TW")['result'])
        sleep(0.3)
    maxwidth=800
    name_list=[]
    loc_list=[]
    latitude_list=[]
    longtitude_list=[]
    url_list=[]
    for h in hotel_info:
        try:
            photoreference=h['photos'][0]['photo_reference']
            url=f'https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photoreference}&key={api_key}'
        except Exception:
            url="no information"        
        #print(h['name'])
        #print(h['geometry']['location'])
        if len(h['name'])>=50:          #如果民宿名稱的字數大於50，把40項之後的刪除
            h['name']=list(h['name'])
            del h['name'][40:len(h['name'])-1]
            h['name']=''.join(h['name'])
        name_list.append(h['name'])
        loc_list.append(h['geometry']['location'])
        latitude_list.append(h['geometry']['location']['lat'])
        longtitude_list.append(h['geometry']['location']['lng'])
        url_list.append(url)
        #print("結束1")
        #print("name_list=",name_list,"loc_list=",loc_list)
    #print("結束2")
    #print("共找到",search_number,"筆資料")
    #print("類型",type(hotel_info))
    #print('h',h)



    with open(f'{path}/hotel_data.csv','w+',newline='',encoding='utf-8-sig')as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(["hotel_name","latitude","longitude","url"])
        for x,y,z,w in zip (name_list,latitude_list,longtitude_list,url_list) :
            writer.writerow([x]+[y]+[z]+[w])
        print("File Write Complete")

    return search_number,name_list,loc_list
        #幾筆資料，飯店名稱，經緯度

#googlemap_search_nearby(24.965557795991632,121.19527772068977,"餐廳")
#print(googlemap_search_hotel(119.56562,23.56505)[2])
