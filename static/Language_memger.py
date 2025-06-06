import os
import json
from dotenv import load_dotenv

# Read appoint Language from Environment variables
# 取得指定語言（從 .env 讀取 Lang 變數，預設為 zh）
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env file not found, using default language.")


user_lang =  os.getenv("Language", "zh")
language_path =  os.getenv("Language_Path", "./Language")
# Choose language (en:English zh:Chinese)
# 選擇語言（en：英文，zh：繁體中文）
def set_language(lang_code):
    global user_lang
    user_lang = lang_code


# Load language dictionaries (messages, error messages, notifications)
# 載入語言資料（一般訊息、錯誤提示、通知訊息） 
with open(os.path.join(language_path, "messages.json"), encoding="utf-8") as f:
    messages_dict = json.load(f)
with open(os.path.join(language_path,"error.json"), encoding="utf-8") as f:
    error_dict = json.load(f)
with open(os.path.join(language_path,"notifications.json"), encoding="utf-8") as f:
    notifications_dict = json.load(f)


# Get translated text from messages
# 從一般訊息檔案中取得對應語言文字
def Keyword(eng_key):
    
    if eng_key not in messages_dict:
        print(f"⚠️ [messages] Key '{eng_key}' not found. Available keys: {list(messages_dict.keys())}")
        return eng_key
    return messages_dict[eng_key].get(user_lang, eng_key)

# Get translated text from error messages
# 從錯誤訊息檔案中取得對應語言文字
def error_information(eng_key):
    if eng_key not in error_dict:
        print(f"⚠️ [error] Key '{eng_key}' not found. Available keys: {list(error_dict.keys())}")
        return eng_key
    return error_dict[eng_key].get(user_lang, eng_key)

# Get translated text from notifications
# 從通知訊息檔案中取得對應語言文字
def information(eng_key):
    if eng_key not in notifications_dict:
        print(f"⚠️ [notifications] Key '{eng_key}' not found. Available keys: {list(notifications_dict.keys())}")
        return eng_key
    return notifications_dict[eng_key].get(user_lang, eng_key)


# Get list of supported languages (based on messages.json)
# 取得支援語言清單（根據 messages.json）
def get_supported_languages():

    if messages_dict:
        first_key = next(iter(messages_dict.values()))
        return list(first_key.keys())
    return []

# Get all available keys for a given category (messages / error / notifications)
# 取得指定類別下的所有關鍵字列表（messages / error / notifications）
def get_available_keys(category="messages"):

    if category == "messages":
        return list(messages_dict.keys())
    elif category == "error":
        return list(error_dict.keys())
    elif category == "notifications":
        return list(notifications_dict.keys())
    else:
        return []
