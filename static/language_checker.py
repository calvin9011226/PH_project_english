import os
import json
from collections import defaultdict

# 設定語言資料夾路徑
LANG_DIR = "./Language"
LANG_SUFFIXES = ["zh", "en"]  # 支援語言種類

def check_lang_files():
    merged_keys = defaultdict(set)

    for file_name in os.listdir(LANG_DIR):
        if file_name.endswith(".json"):
            with open(os.path.join(LANG_DIR, file_name), encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    for key in data.keys():
                        if "_" in key:
                            base, lang = key.rsplit("_", 1)
                            merged_keys[base].add(lang)
                except Exception as e:
                    print(f"❌ 讀取失敗：{file_name}, 錯誤：{e}")

    print("🔍 語言缺漏報告：")
    for base_key, langs in merged_keys.items():
        missing = [l for l in LANG_SUFFIXES if l not in langs]
        if missing:
            print(f"⚠️ {base_key} 缺少語言：{missing}")

    print("✅ 完成檢查")

if __name__ == "__main__":
    check_lang_files()
