from flask_ngrok import run_with_ngrok
from flask import Flask, request
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 載入 json 標準函式庫，處理回傳的資料格式
import json

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True) # 取得收到的訊息內容
    try:
        json_data = json.loads(body) # json 格式化訊息內容
        access_token = 'h/47RBzNDXh5jWXncB7rZ1GPYKG15fDyuCewrJEJ8Q314NL732t6hQo+Oql/hM/Jn02uU2jCv36wlnPP6XP4p5HG9nUiYfAndRecgTlf2LlQ19m9bc7/Fc3MuguAw0IRCzUiHJjco7gdD1DSD1G2TwdB04t89/1O/w1cDnyilFU='
        secret = '1bf0051081f4240f32595d32d374b04c'
        line_bot_api = LineBotApi(access_token) # 確認 token 是否正確
        handler = WebhookHandler(secret) # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature'] # 加入回傳的 headers
        handler.handle(body, signature) # 綁定訊息回傳的相關資訊
        msg = json_data['events'][0]['message']['text'] # 取得 LINE 收到的文字訊息
        tk = json_data['events'][0]['replyToken'] # 取得回傳訊息的 Token
        line_bot_api.reply_message(tk,TextSendMessage(msg)) # 回傳訊息
        print(msg, tk) # 印出內容
    except:
        print(body) # 如果發生錯誤，印出收到的內容
    return 'OK' # 驗證 Webhook 使用，不能省略
if __name__ == "__main__":
    run_with_ngrok(app) # 串連 ngrok 服務
    app.run()