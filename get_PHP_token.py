import requests
import json

def start_ngrok(port=5000):
    """根據指定 port 獲取對應的 ngrok 公開網址"""
    try:
        # 查詢 ngrok API
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = json.loads(response.text).get("tunnels", [])
        
        # 遍歷所有 tunnel，尋找符合條件的
        for tunnel in tunnels:
            #print(tunnel)
            public_url = tunnel.get("public_url", "")
            tunnel_proto = tunnel.get("proto", "")
            tunnel_config = tunnel.get("config", {})
            tunnel_port = tunnel_config.get("addr", "").split(":")[-1]  # 取得 port

            # 確保是 HTTPS，並且對應輸入的 port
            if tunnel_proto == "https" and str(tunnel_port) == str(port):
                return public_url

    except requests.exceptions.RequestException as e:
        print("無法獲取 ngrok 網址，可能 ngrok 未啟動:", e)
    
    return None

# 測試不同的 port
"""
PHP_ngrok = start_ngrok(5000)  # 這裡填入 ngrok 監聽的 port

if PHP_ngrok:
    print(f"PHP_ngrok 取得成功: {PHP_ngrok}")
    print(PHP_ngrok)
else:
    print("無法獲取 ngrok 公開網址")
"""