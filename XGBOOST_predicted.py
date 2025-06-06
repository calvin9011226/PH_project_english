import xgboost as xgb
import Now_weather
from random import randrange
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from dotenv import load_dotenv
import os
load_dotenv()  # 讀取 .env 檔案
Penghu_csv_file=os.getenv("Penghu_csv_file")


def XGboost_recommend1(arr,gender,age): 
    le = LabelEncoder()
    labelencoder = LabelEncoder()

    Data = pd.read_csv(f'{Penghu_csv_file}/penghu_orignal2.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'], Data['設置點']],
                            columns= ['weather','gender','age','label'])
        
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode

    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    onehotencoder = OneHotEncoder(categories = 'auto')
    X=onehotencoder.fit_transform(X).toarray()    
        #print(list(X.columns))
        #R = pd.DataFrame(X)
        #print(R)
    Y = df_data['label'].values    
        
        
    Y = le.fit_transform(Y) #由於字串無法做訓練，所以進行Label encoding編碼

    arr_labelencode = labelencoder.transform(arr) #用同一個labelencoder能transform到一樣的編碼
    #print(arr_labelencode[0])

    Value_arr = np.array([arr_labelencode[0],gender,age])
    #print(Value_arr)
    final=onehotencoder.transform([Value_arr])#用同一個onehotencoder能transform到一樣的編碼
    #print(final)
    loaded_model = XGBClassifier()
    loaded_model.load_model('xgb_model1.bin')
    predicted = loaded_model.predict(final)
    #print(predicted)
    result = le.inverse_transform(predicted)
    #print(result[0])
    return result[0]

def XGboost_recommend2(arr,gender,age,tidal,temperature,dont_go_here): 
    le = LabelEncoder()
    labelencoder = LabelEncoder()

    Data = pd.read_csv(f'{Penghu_csv_file}/penghu_orignal2.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
    df_data = df_data[~df_data['label'].isin(dont_go_here)]     # 這個會去判斷是否為不推薦名單,並不讓他進入機器學習
    
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode
    #print(dict(zip(labelencoder.classes_, labelencoder.transform(labelencoder.classes_))))
    
    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料
    # onehotencoder = OneHotEncoder(categories = 'auto')
    #print("原始資料:",X)
    onehotencoder = OneHotEncoder(categories = 'auto',handle_unknown='ignore')
    #print("onehotencoder=",onehotencoder)
    X=onehotencoder.fit_transform(X).toarray()    
    #print("OneHotEncoder 見過的類別:", onehotencoder.categories_)
    
        
    Y = df_data['label'].values    
        
        
    Y = le.fit_transform(Y) #由於字串無法做訓練，所以進行Label encoding編碼
    arr_labelencode = labelencoder.transform(arr) #用同一個labelencoder能transform到一樣的編碼
    # print(arr_labelencode[0])

    Value_arr = np.array([arr_labelencode[0],gender,age,tidal,temperature], dtype=object)#把輸入資料轉成object,使做了fit_transform的onehotencoder能有相同屬性
    #print(Value_arr)
    #print(type(Value_arr))
    final=onehotencoder.transform([Value_arr])#用同一個onehotencoder能transform到一樣的編碼
    # print(final)
    loaded_model = XGBClassifier()
    loaded_model.load_model('xgb_model2.bin')
    predicted = loaded_model.predict(final)
    #print(predicted)
    result = le.inverse_transform(predicted)
    #print("XGboost_recommend2 result[0]:",result[0])
   

    """
    # 列出 One-Hot Encoding 的特徵名稱
    feature_names = np.hstack(onehotencoder.categories_)  # 獲取所有類別名稱
    feature_names = [str(name) for name in feature_names]  # 轉換成字串列表
    for i, name in enumerate(feature_names):
        print(f"f{i} -> {name}")
    """
    return result[0]




def XGboost_recommend3(arr,gender,age,tidal,temperature): 
    le = LabelEncoder()
    labelencoder = LabelEncoder()

    Data = pd.read_csv(f'{Penghu_csv_file}/generated_data_updated1.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
        
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode

    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    # onehotencoder = OneHotEncoder(categories = 'auto',handle_unknown='ignore')
    onehotencoder = OneHotEncoder(categories = 'auto')
    X=onehotencoder.fit_transform(X).toarray()    
    Y = df_data['label'].values    
        
        
    Y = le.fit_transform(Y) #由於字串無法做訓練，所以進行Label encoding編碼
    arr_labelencode = labelencoder.transform(arr) #用同一個labelencoder能transform到一樣的編碼

    Value_arr = np.array([arr_labelencode[0],gender,age,tidal,temperature], dtype=object)
    print("Value_arr :'weather','gender','age','tidal','temperature'= ",Value_arr)
    final=onehotencoder.transform([Value_arr])#用同一個onehotencoder能transform到一樣的編碼
    loaded_model = XGBClassifier()
    loaded_model.load_model('PHtest.bin')
    predicted = loaded_model.predict(final)
    result = le.inverse_transform(predicted)
    print(result[0])
    return result[0]




def XGboost_classification(arr,gender,age,tidal,temperature,arr_msg): #把景點和餐廳從推薦景點中分開
    le = LabelEncoder()
    labelencoder = LabelEncoder()

    if arr_msg == ['永續景點']:
        print("arr_msg =" ,arr_msg)
        Data = pd.read_csv(f'{Penghu_csv_file}/test/Sustainable/locations_Attractions.csv',encoding='utf-8-sig')
        loaded_model = XGBClassifier()
        loaded_model.load_model('sustainable_Attractions.bin')

    if arr_msg == ['一般景點']:
        print("arr_msg =" ,arr_msg)
        Data = pd.read_csv(f'{Penghu_csv_file}/test/non Sustainable/penghu_Attractions.csv',encoding='utf-8-sig')
        loaded_model = XGBClassifier()
        loaded_model.load_model('non_sustainable_attraction.bin')

    if arr_msg == ['永續餐廳']:
        print("arr_msg =" ,arr_msg)
        Data = pd.read_csv(f'{Penghu_csv_file}/test/Sustainable/locations_non_Attractions.csv',encoding='utf-8-sig')
        loaded_model = XGBClassifier()
        loaded_model.load_model('sustainable_non_Attractions.bin')

    if arr_msg == ['一般餐廳']:
        print("arr_msg =" ,arr_msg)
        Data = pd.read_csv(f'{Penghu_csv_file}/test/non Sustainable/penghu_non_Attractions.csv',encoding='utf-8-sig')
        loaded_model = XGBClassifier()
        loaded_model.load_model('non_sustainable_non_Attractions.bin')

    # Data = pd.read_csv('C:/Users/wkao_/Desktop/NCLab/penghu project/penghu_csv_file/test/non Sustainable/penghu_Attractions.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
        
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode
    
    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    # onehotencoder = OneHotEncoder(categories = 'auto',handle_unknown='ignore')
    onehotencoder = OneHotEncoder(categories = 'auto',handle_unknown='ignore')
    X=onehotencoder.fit_transform(X).toarray()    
    Y = df_data['label'].values    
        
        
    Y = le.fit_transform(Y) #由於字串無法做訓練，所以進行Label encoding編碼
    arr_labelencode = labelencoder.transform(arr) #用同一個labelencoder能transform到一樣的編碼

    Value_arr = np.array([arr_labelencode[0],gender,age,tidal,temperature])
    print("Value_arr :'weather','gender','age','tidal','temperature'= ",Value_arr)
    final=onehotencoder.transform([Value_arr])#用同一個onehotencoder能transform到一樣的編碼
    predicted = loaded_model.predict(final)
    
    result = le.inverse_transform(predicted)
    print(result[0])
    return result[0]




#arr = np.array("風")
#arr = np.atleast_1d(arr)
#print(XGboost_recommend2(arr,1,25,2,24))
#print(XGboost_recommend1(arr,1,69))
weather = Now_weather.weather()
arr = np.array([weather])
print("Now_weather.weather() :",arr)
gender = randrange(0,2)
age = randrange(15,55)
temperature = Now_weather.temperature()
tidal = randrange(0,3)
#print(XGboost_recommend1(arr,gender,age))


for i in range (5):
    gender = randrange(-1,10)
    age = randrange(15,80)
    print(arr,gender,age,tidal,temperature)
    print(XGboost_recommend2(arr,gender,age,tidal,temperature,[]))

#print(XGboost_recommend3(arr,gender,age,tidal,temperature))
# print(XGboost_classification(arr,1,50,2,24,['永續景點']))