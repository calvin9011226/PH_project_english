from xgboost import XGBClassifier
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from random import randrange
import xgboost as xgb
from dotenv import load_dotenv
import os
load_dotenv()  # 讀取 .env 檔案
Penghu_csv_file=os.getenv("Penghu_csv_file")


def XGboost_recommend1():
    le = LabelEncoder()
    labelencoder = LabelEncoder()
    tree_deep = 100 #可理解成epoch
    learning_rate = 0.3
        
    Data = pd.read_csv('C:/Users/roy88/testproject/python/xgboost/penghu_orignal2.csv',encoding='utf-8-sig')
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
        
        
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)# stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    Y_train = le.fit_transform(Y_train) #由於字串無法做訓練，所以進行Label encoding編碼


    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)

    # 儲存模型
    xgboostModel.save_model('xgb_model1.bin')


def XGboost_recommend2():
    le = LabelEncoder()
    labelencoder = LabelEncoder()
    tree_deep = 300 #可理解成epoch
    learning_rate = 0.3
        
    Data = pd.read_csv(f'{Penghu_csv_file}/penghu_orignal2.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
    print(df_data)
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode

    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    onehotencoder = OneHotEncoder(categories = 'auto')
    X=onehotencoder.fit_transform(X).toarray()    
    # print(list(X.columns))
    #R = pd.DataFrame(X)
    #print(R)
    Y = df_data['label'].values    
        
        
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)# stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    Y_train = le.fit_transform(Y_train) #由於字串無法做訓練，所以進行Label encoding編碼


    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)
    
    # 列出 One-Hot Encoding 的特徵名稱
    feature_names = np.hstack(onehotencoder.categories_)  # 獲取所有類別名稱
    feature_names = [str(name) for name in feature_names]  # 轉換成字串列表
    for i, name in enumerate(feature_names):
        print(f"f{i} -> {name}")
    

    # 儲存模型
    xgboostModel.save_model('xgb_model2_test1.bin')
    print('訓練集Accuracy: %.2f%% ' % (xgboostModel.score(X_train,Y_train) * 100.0))

def XGboost_recommend3():
    le = LabelEncoder()
    labelencoder = LabelEncoder()
    tree_deep = 100 #可理解成epoch
    learning_rate = 0.3
        
    Data = pd.read_csv(f'{Penghu_csv_file}/generated_data_updated1.csv',encoding='utf-8-sig')
    df_data = pd.DataFrame(data= np.c_ [Data['weather'], Data['gender'], Data['age'] ,Data['tidal'],Data['temperature'],Data['設置點']],
                           columns= ['weather','gender','age','tidal','temperature','label'])
        
    df_data['weather'] = labelencoder.fit_transform(df_data['weather'])#轉換文字要做one-hot encode前要先做label encode

    X = df_data.drop(labels=['label'],axis=1).values # 移除label並取得剩下欄位資料

    onehotencoder = OneHotEncoder(categories = 'auto')
    X=onehotencoder.fit_transform(X).toarray()    
    #print(list(X.columns))
    #R = pd.DataFrame(X)
    #print(R)
    Y = df_data['label'].values    
        
        
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)# stratify=Y  -> 依据标签y，按原数据y中各类比例，分配给train和test，使得train和test中各类数据的比例与原数据集一样
    Y_train = le.fit_transform(Y_train) #由於字串無法做訓練，所以進行Label encoding編碼


    xgboostModel = XGBClassifier(n_estimators=tree_deep, learning_rate= learning_rate)
    xgboostModel.fit(X_train, Y_train)

    # 儲存模型
    xgboostModel.save_model('xgb_model3.bin')

#XGboost_recommend1()
XGboost_recommend2()
#XGboost_recommend3()