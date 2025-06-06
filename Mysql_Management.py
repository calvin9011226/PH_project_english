#將plan.csv中的資料輸入到資料庫裡，供php使用

import pymysql
import csv
import os
from dotenv import load_dotenv
load_dotenv()  # read .env file

MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_PORT=int(os.getenv("MYSQL_PORT"))
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE")

# 將 plan.csv 資料匯入 MySQL
def import_plan_to_mysql(
    csv_file_path,
    mysql_config=None,
    full_fields=False
):

    if mysql_config is None:
        mysql_config = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "database": MYSQL_DATABASE
        }

    connection = pymysql.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"],
        charset='utf8mb4'
    )

    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS `plan`;")

    if full_fields:
        sql_create = '''
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
            `天氣` VARCHAR(50),
            `place_id` VARCHAR(100),
            `crowd` INT,
            `crowd_rank` INT
        );
        '''
        sql_insert = '''
            INSERT INTO `plan` (
                no, Time, POI, UserID, 設置點, 緯度, 經度,
                BPLUID, age, gender, 天氣, place_id, crowd, crowd_rank
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
    else:
        sql_create = '''
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
        sql_insert = '''
            INSERT INTO `plan` (
                no, Time, POI, UserID, 設置點, 緯度, 經度,
                BPLUID, age, gender, 天氣
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

    cursor.execute(sql_create)

    with open(csv_file_path, mode='r', newline='', encoding='utf-8-sig') as file_obj:
        reader = csv.reader(file_obj)
        next(reader)  # skip header
        for row in reader:
            cursor.execute(sql_insert, row)

    connection.commit()
    cursor.close()
    connection.close()
    print("✅ 資料已成功匯入資料庫 plan 表")

def fetch_plan_data():
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = "SELECT no, 設置點, 緯度, 經度, crowd_rank FROM plan ORDER BY crowd_rank ASC"
    cursor.execute(sql)
    results = cursor.fetchall()

    # 分別建立對應的 JS 陣列
    no_list, place_list, lat_list, lng_list, rank_list = [], [], [], [], []
    for row in results:
        no_list.append(row[0])
        place_list.append(row[1])
        lat_list.append(row[2])
        lng_list.append(row[3])
        rank_list.append(row[4])

    cursor.close()
    conn.close()

    return {
        "JS_number": no_list,
        "JS_place": place_list,
        "JS_latitude": lat_list,
        "JS_longitude": lng_list,
        "JS_crowdRank": rank_list,
    }

# 從 test 表讀取人潮資訊，並以 list of dict 回傳
def fetch_test_table_data(mysql_config=None):
    if mysql_config is None:
        mysql_config = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "database": MYSQL_DATABASE,
        }

    try:
        conn = pymysql.connect(
            host=mysql_config["host"],
            port=mysql_config["port"],
            user=mysql_config["user"],
            password=mysql_config["password"],
            database=mysql_config["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,  # 直接拿 dict
        )

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    `time`,
                    CAST(latitude  AS DOUBLE)  AS lat,
                    CAST(longitude AS DOUBLE)  AS lng
                FROM test
                WHERE latitude  IS NOT NULL
                  AND longitude IS NOT NULL
                """
            )
            rows = cur.fetchall()

        # ➜ 轉成 float，避免前端 NaN
        for r in rows:
            r["lat"] = float(r["lat"])
            r["lng"] = float(r["lng"])
        return rows

    except Exception as e:
        print(f"❌ MySQL error: {e}")
        return []

    finally:
        if conn:
            conn.close()
