#將plan.csv中的資料輸入到資料庫裡，供php使用

import pymysql
import csv

connection = pymysql.connect(host='127.0.0.1',
                        port=3306,
                        user='root',
                        password='nclab722',
                        database='penghu',
                        charset='utf8')

cursor = connection.cursor()

def planmysql(file):
    sql1 = "DROP TABLE `plan` ;"
    cursor.execute(sql1)

    sql2 = '''
    CREATE TABLE `plan`(
        `no` VARCHAR(50),
        `Time` VARCHAR(50),
        `POI` VARCHAR(50),
        `UserID` VARCHAR(200),
        `設置點` VARCHAR(50),
        `緯度` VARCHAR(50),
        `經度` VARCHAR(50),
        `BPLUID` VARCHAR(50),
        `age` VARCHAR(50),
        `gender` VARCHAR(50),
        `天氣` VARCHAR(50)
        );
    '''
    cursor.execute(sql2)

    with open(file, mode='r', newline='' , encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        next(reader)
        
        for row in reader:
            sql3 = "INSERT INTO `plan` (no,Time,POI,UserID,設置點,緯度,經度,BPLUID,age,gender,天氣) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(sql3, row)

    # 提交事務
    connection.commit()

    cursor.close()
    connection.close()
    print("csv already save in MySQL")
    
def testmysql(file):
    sql1 = "DROP TABLE `test` ;"
    cursor.execute(sql1)

    sql2 = '''
    CREATE TABLE `test`(
        `no` VARCHAR(50),
        `time` VARCHAR(50),
        `UserID_MemID` VARCHAR(200),
        `setpoint` VARCHAR(50),
        `latitude` VARCHAR(50),
        `longitude` VARCHAR(50)
        );
    '''
    cursor.execute(sql2)

    with open(file, mode='r', newline='' , encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        
        next(reader)
        
        for row in reader:

            sql3 = "INSERT INTO `test` (no,time,UserID_MemID,setpoint,latitude,longitude) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql3, row)

    # 提交事務
    connection.commit()

    cursor.close()
    connection.close()
    print("csv already save in MySQL")   


#如果原本就沒有這個Table,可以把最前面刪除Table移除
#planmysql('./penghu_csv_file/plan.csv') #相對路徑(一開始要建Mysql用的)
#testmysql('./penghu_csv_file/Beacon20220907-crowd.csv') #相對路徑(一開始要建Mysql用的)