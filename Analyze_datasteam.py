import logging
from datetime import datetime
import os
import json
import time
import re
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import cm
from matplotlib.ticker import MultipleLocator
import psutil                           #取得電腦資源占用套件
from threading import Thread
import matplotlib.dates as mdates
import glob

#讓plt可以顯示中文
plt.rcParams["font.family"] = "Microsoft JhengHei"   # 或你機器真的有的字型
plt.rcParams["axes.unicode_minus"] = False           # 讓負號也正常

#公版字型
Default_font = {
    "x_label": 16,
    "y_label": 16,
    "x_ticks": 14,
    "y_ticks": 14,
    "title": 20,
    "legend_title": 13,
    "legend_content": 15,
    "value_text": 12,
    "colorbar_label": 16,
    "colorbar_ticks": 14
}

#--------------------------------------畫圖函數--------------------------------------------------

#統計時間圖
def plot_bar(
    labels,             # list: y 軸項目名稱（已在外面排好序）
    values,             # list or list of lists: 對應 label 的数值
    save_path,          # str: 圖片儲存路徑
    title="",           # str: 標題
    xlabel="Time (s)",  # str: X 軸標籤
    is_stacked=False,   # bool: 是否堆叠
    colors=None,        # list: bar 顏色
    sub_colors=None,    # dict: 子功能→對應顏色
    data_sizes=None,    # dict: label→大小
    show_times=True,    # bool: 是否顯示子功能的耗時
    longest_time=40,    # 時間最長的那一段
    tick_interval=None, # 決定每個時間間隔
    fixed_xlim=None,    # 決定總時長
    size_off=False,     # 是否要印出
    font_config=None,
):
    #字體大小設定參數

    data_fontsize=12
    config = {**Default_font, **(font_config or {})}

    fig, ax = plt.subplots(figsize=(12, max(4, len(labels)*0.7)))
    y_pos = range(len(labels))  
        # 設定 x 軸最大值
    if fixed_xlim:
        ax.set_xlim(0, fixed_xlim)
        longest_time=fixed_xlim
    else:
        ax.set_xlim(0, longest_time * 1.1)

    min_width = longest_time/150  # 最小可視寬度（單位：秒，可自行調整）

    # 如果外面沒有傳 colors，就補一个空列表
    if colors is None:
        colors = [None] * len(labels)

    if is_stacked:
        # 堆疊 bar
        
        for i, segment in enumerate(values):
            left = 0
            seg_colors = colors[i] or [None]*len(segment)

            for j, v in enumerate(segment):
                display_width = max(v, min_width)  # 若 v 太小就畫 min_width
                ax.barh(i, display_width, left=left, color=seg_colors[j], edgecolor='white')
                if show_times and v>min_width*8:
                    ax.text(left + display_width / 2, i, f"{v:.2f}s",
                            ha='center', va='center', fontsize=config["value_text"])
                left += display_width  # 用 display_width 堆疊      

        # 資料大小
        if data_sizes and  not size_off:
            for i, label in enumerate(labels):
                bar_len = sum(values[i])
                offset =ax.get_xlim()[1]*0.02           #資料大小的位移量
                size = data_sizes.get(label, 0)
                ax.text(bar_len + offset, i, f"{size:.0f}B",
                        va='center', fontsize=data_fontsize)

        # 劃出標籤
        if sub_colors:
            handles = [Patch(color=c, label=sub) for sub, c in sub_colors.items()]
#            ax.legend(handles=handles, title="Sub-function",loc='center left', bbox_to_anchor=(0.8235, 0.2105),
#                     fontsize=config["legend_content"],title_fontsize=config["legend_title"],prop={'weight': 'normal'},framealpha=0.9)
            ax.legend(handles=handles,loc='center left', bbox_to_anchor=(0.733, 0.247),prop={'size': config["legend_content"], 'weight': 'normal'}
                      ,framealpha=1,edgecolor='none')

    else:
        # 普通水平 bar
        bar_colors = colors
        ax.barh(y_pos, values, color=bar_colors)
        
        
        for i, v in enumerate(values):
            display_width = max(v, min_width)  # 若 v 太小就畫 min_width

            if show_times and v>min_width*10:
                ax.text(v/2, i, f"{v:.2f}s",
                        ha='center', va='center', fontsize=config["value_text"])
                
        # 標註「資料大小」
        if data_sizes and  not size_off:
            for i, label in enumerate(labels):
                bar_len = values[i]
                offset =ax.get_xlim()[1]*0.01           #資料大小的位移量
                size = data_sizes.get(label, 0)
                ax.text(bar_len + offset, i, f"{size:.0f}B",va='center', 
                        fontsize=data_fontsize)

    # 設定 x 軸最大值
    if tick_interval:
        ax.xaxis.set_major_locator(MultipleLocator(tick_interval))  # 每 2 秒一格
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels,fontsize=config["y_label"])
    ax.set_xlabel(xlabel,fontsize=config["x_label"])
    ax.tick_params(axis='x', labelsize=config["x_ticks"])
    #ax.set_title(title,fontsize=16)
    fig.text(0.55, 0.06, title, ha='center', va='center', fontsize=config["title"])
    ax.grid(True, axis='x',color='gray', alpha=0.2)
    plt.tight_layout(pad=1.5,rect=[0, 0.1, 1, 1])
    plt.savefig(save_path, dpi=1000)
    plt.close()

#Pie Chart圓餅圖
def plot_pie(
    labels,                     # list: 項目名稱
    values,                     # list: 對應 label 的数值
    save_path,                  # str:  圖片儲存路徑
    title="",                   # str:  標題
    label_type="",              # str:  label標籤的資料單位
    colors=None,                # list: bar 顏色
    emphasize_num=0,             # int:  把前幾大的圓餅圖突出
    Values_Visible=True,        # bool: 是否要顯示數據
    Percentage_Visible=True,    # bool: 是否要顯示百分比
    font_config=None
):
    
    #圓餅圖內部顯示的數值、百分比
    inter_text = []
    total=sum(values)
    config = {**Default_font, **(font_config or {})}
    
    for value in values:
        parts = []
        if Values_Visible:
            parts.append(f"{value}")
        if Percentage_Visible:
            percent = (value / total) * 100
            parts.append(f"{percent:.1f}%")
        inter_text.append("\n".join(parts) if parts else "")

    def adjust_autopct(inter_text):
        def _autopct(pct):
            idx = _autopct.counter
            _autopct.counter += 1
            return inter_text[idx]
        _autopct.counter = 0
        return _autopct
    
    #最大突出的部分
    explode = []
    if emphasize_num==0:
        explode = [0] * len(values)
    else:    
        if emphasize_num>=len(values):
            emphasize_num=len(values)-1
            print(f"設定突出目標已超標,以降低至{emphasize_num}個")
        
        top_v = sorted(values, reverse=True)[:emphasize_num]
        for val in values:
            if val in top_v:
                explode.append(0.1)
            else:
                explode.append(0)

    #自動配色
    if colors is None:
        cmap = plt.get_cmap("tab20", len(values))  # 自動根據 values 數量配色
        colors = [cmap(i) for i in range(len(values))]

    fig, ax = plt.subplots()
    plt.pie(values, radius=3, labels=labels,autopct=adjust_autopct(inter_text),explode=explode,colors=colors)
    ax.axis('equal')
    ax.set_xlabel(label_type,fontsize=config["x_label"])
    plt.title(title, fontsize=config["title"])
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

#折線圖
def plot_multiline_timeseries(
    time_index,
    data_dict,
    save_path="./plot.png",
    title="折線圖",
    xlabel="時間",
    ylabel="數值",
    figsize=(12, 6),
    font_config=None,
    legend_config=None
):

    config = {**Default_font, **(font_config or {})}

    plt.figure(figsize=figsize)
    for tag, values in data_dict.items():
        plt.plot(time_index, values, marker='o', linestyle='-', label=tag)

    plt.tick_params(axis='x', labelsize=config["x_ticks"])
    plt.tick_params(axis='y', labelsize=config["y_ticks"])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gcf().autofmt_xdate()
    plt.title(title, fontsize=config["title"])
    plt.xlabel(xlabel, fontsize=config["x_label"])
    plt.ylabel(ylabel, fontsize=config["y_label"])
    plt.legend(
        loc="upper left",
        bbox_to_anchor=(1, 1),
        prop=legend_config or {'size': config["legend_content"], 'weight': 'normal'}
    )
    plt.tight_layout(pad=1.5, rect=[0, 0, 1, 0.95])
    plt.grid(True)
    plt.savefig(save_path, dpi=300)
    plt.close()




#---------------------------------------- 恆定值 ---------------------------------------------------
Unit_conversion={"B":1,"bytes":1,"Bytes":1,
                 "KB":1024      ,"kB":1024,
                 "MB":1048576   ,"mB":1048576,
                 "GB":1073741824,"gB":1073741824}

#------------------------------- feature mapping 定義字典 -------------------------------------------
penghu_FM={
    "永續觀光": "景點推薦",
    "一般景點推薦": "景點推薦",
    "景點推薦": "景點推薦",
    "景點人潮": "景點人潮",
    "附近搜尋": "附近搜尋",
    "餐廳": "附近搜尋",
    "風景區": "附近搜尋",
    "停車場": "附近搜尋",
    "住宿": "附近搜尋",
    "行程規劃": "行程規劃",
    "兩天一夜": "行程規劃",
    "三天兩夜": "行程規劃",
    "四天三夜": "行程規劃",
    "五天四夜": "行程規劃",
    "收集資料&修改資料": "收集資料&修改資料",
    "年齡設定": "收集資料&修改資料",
    "性別設定": "收集資料&修改資料",
    "location": "收集資料&修改資料",
    "男": "收集資料&修改資料",
    "女": "收集資料&修改資料",
    "其他": "收集資料&修改資料",
    "租車": "租車"
}


#-------------------------------------- 公用函數-----------------------------------------------------

def build_feature_mapping_from_log(
    log_path,                           # log 檔案路徑
    feature_mapping_style="auto",       # "penghu" 使用預設, "auto" 從 log 建, 或外部傳入 dict
    match_type="",                      # "Data Size", "Data Time", etc.
    predefined_mapping=None):           # 傳入 dict（非 penghu 時使用）

    # 預設 penghu 模式
    if feature_mapping_style == "penghu":
        return penghu_FM
    
    # 自動從 log 建立
    elif feature_mapping_style == "auto":
        feature_mapping = {}
        with open(log_path, "r", encoding='utf-8-sig', errors='replace') as f:
            for line in f:
                if f"[{match_type}]" in line:
                    match = re.search(rf"\[{match_type}\]\s+(.*?)\s+:", line)
                    if match:
                        tag = match.group(1).strip()
                        main_tag= strip_main(tag)
                        if tag != main_tag:
                            feature_mapping[tag] = main_tag
                            
            if not feature_mapping:
                print("⚠️ 沒有從 log 中偵測到有效的子功能對應")

            return feature_mapping

    # 外部傳入
    elif isinstance(predefined_mapping, dict):
        return predefined_mapping

    else:
        print("❗ 無效的 feature_mapping_style 或 mapping 格式")
        return {}

def strip_main(tag,choose="main_tag"): 
    if "-" in tag:
        split_pos = tag.rfind("-")
        main_tag = tag[:split_pos].strip()
        sub_tag = tag[split_pos + 1:].strip()
    else:
        main_tag = tag
        sub_tag = tag

    if choose=="main_tag":
        return main_tag
    else:
        return sub_tag

if not os.path.exists("documentary"):
    os.mkdir("documentary") 




# 管理決定資料是否顯示在終端機
class PrintManager:
    LEVEL_PRIORITY = {
        "all": -1,     # 顯示所有輸出
        "info": 0,     # 最基本層級
        "data": 1,
        "warning": 2,
        "error": 3,
        "off": 99      # 關閉所有輸出
    }
    LEVEL_ICON = {
        "info":     "⚪ ",
        "data":     "🔵 ",
        "warning":  "🟠 ",
        "error":    "🔴 ",
    }

    def __init__(self, mode="all", prefix=""):
        if mode not in self.LEVEL_PRIORITY:
            print(f"⚠️  無效的 Print_Funct 設定：{mode}，自動改為 'off'")
            mode = "off"
        self.mode = mode
        self.prefix = prefix

    def print_level_handle(self, *args, level="info", text=None):
            text = text if text is not None else " ".join(str(a) for a in args)
            text = str(text).strip()
            if level not in self.LEVEL_PRIORITY:
                print(f"⚠️  警告,有無效的 level 設定：{level}")
            # 圖標處理
            icon = self.LEVEL_ICON.get(level, "")
            full_msg = f"{icon}{self.prefix}{text}"
            msg_priority = self.LEVEL_PRIORITY.get(level, 0)
            mode_priority = self.LEVEL_PRIORITY.get(self.mode, 99)

            # error 永遠印出
            #print("mode_priority=",mode_priority,"\tmsg_priority=",msg_priority)
            if level == "error" or  mode_priority<=msg_priority :
                print(full_msg)


#多執行緒管理
class ResourceMonitor:
    def __init__(self, tag, proc, fps=5):
        self.tag = tag                  
        self.proc = proc
        self.interval = 1 / fps
        self.samples_cpu = []
        self.samples_mem = []
        self.running = False                    # 是否要進行監控
        self.thread = None                       

    def _collect(self):
        while self.running:
            cpu_val = self.proc.cpu_percent(interval=self.interval) # 取得 CPU 目前資源使用量
            mem_val = self.proc.memory_info().rss                   # 取得記憶體目前資源使用量
            self.samples_cpu.append(cpu_val)
            self.samples_mem.append(mem_val)

    def start(self):
        self.running = True                         #開啟資源監控
        self.thread = Thread(target=self._collect)
        self.thread.start()


    def stop(self):
        self.running = False
        self.thread.join()
        return self.samples_cpu, self.samples_mem


    


# 定義 Log 類別
class Log:

    # 把允許寫入 log 的方法存在 config 中 choose[all,log,data_size,data_time,data_message,data_content,else_info]
    def __init__(self, choose=["all"], Print_Funct="all", Auto_Clear=False , File_Only=False, File_Name="log"):
        
        # 建立 logger 實體與名稱
        logger_name = f"Logger_{File_Name.replace('/', '_')}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # 清除重複 handler（避免重複 log）
        if self.logger.handlers:
            self.logger.handlers.clear()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self._config = set(choose)

        # 設定輸出到終端機權限
        self.Print_funct = Print_Funct
        self.printer = PrintManager(mode=Print_Funct, prefix="[Log]\t")
        self.logprint = self.printer.print_level_handle
        self.logprint(f"Log choose 以設定: {self._config}")

        # 設定 log 檔是否要依照每小時時間命名還是直接寫入在指定的檔案
        if(File_Only):
            log_filename=f"./documentary/{File_Name}.log"
        else:
            # 設定 log 檔名（以年月日_小時）格式
            now = datetime.now().strftime("%Y%m%d_%H")
            log_filename = f"./documentary/log_{now}.log"

        # 設定是否要複寫檔案還是繼續接著寫
        if(Auto_Clear):
            handler = logging.FileHandler(log_filename, mode='w',encoding='utf-8-sig')
            self.logprint(f"已清空{log_filename}的檔案")
        else:
            handler = logging.FileHandler(log_filename,encoding='utf-8-sig')
            self.logprint(f"新增到{log_filename}的檔案")

        # 設定 formatter 並掛上 handler
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    #   data:大小  ,data_type:資料的類別   ,message:是哪個資料流的大小
    def data_size(self, data, message="", data_type="",root_config_enable=False):
        if "all" in self._config or "log" in self._config or root_config_enable or "data_size" in self._config:
            
            if data_type!="":
                data_type=f"[{data_type}]"

            self.logger.info(f"[Data Size] {data_type} {message} : {data}")
            self.logprint(level="data",text=f"data_size 寫入->\t{data_type} {message} : {data}")

    #   data:時間  ,unit:時間單位(預設為微秒)  ,message:是哪個資料流的時間
    def data_time(self, data, message="", unit="s",root_config_enable=False):                 
        if "all" in self._config or "log" in self._config or root_config_enable or "data_time" in self._config:
            self.logger.info(f"[Data Time]  {message} : {data:.7f}{unit}")
            self.logprint(level="data",text=f"data_time 寫入->\t{message} : {data}{unit}")

    #   message:想寫入的資訊或訊息
    def data_message(self, message):
        if "all" in self._config or "log" in self._config or "data_message" in self._config:
            self.logger.info(message)
            self.logprint(level="data",text=f"message 寫入->\t{message}")
    
    #   data:想寫入的資料內容  ,num_limit:限制字數的數量
    def data_content(self, data, num_limit=None):
        if "all" in self._config or "log" in self._config or "data_content" in self._config:
            if isinstance(num_limit, int) and num_limit >= 0:
                # 僅對可切割型別做截斷
                if isinstance(data, (str, list, tuple)):
                    data = data[:num_limit]
                else:
                    self.logprint(level="warning", text=f"<data_content> !!! 無法對 {type(data).__name__} 做截斷，將完整寫入 !!!")

            elif num_limit is not None:
                # num_limit 不是數字
                self.logprint(level="warning", text=f"<data_content> !!! num_limit 必須是非負整數，忽略限制 !!!")

            # 最終不論型別，都寫入 log
            self.logger.info(data)
            self.logprint(level="data", text=f"content 寫入->\t{data}")
                
    #抓取目前程式的 CPU% 與記憶體 RSS，並寫入 log
    def data_resource_usage(self, data_type="", Memory_unit="MB", choose=["CPU", "Memory"], Use_multi_core=False,Use_during=False, tag="", override_values=None):
        cpu_estimated   = override_values.get("cpu_estimated")    if override_values else None
        memory          = override_values.get("memory")       if override_values else None
        core_num  = override_values.get("core")         if override_values else psutil.cpu_count(logical=True)
        CPU_during= override_values.get("CPU_during")   if override_values else ""
        Memory_during= override_values.get("Memory_during")   if override_values else ""
        FPS = override_values.get("FPS")   if override_values else 1

        if "all" in self._config or "log" in self._config or "data_resource_usage" in self._config:
            if "CPU" in choose and cpu_estimated is not None:
                if Use_multi_core:
                    write_cpu_type="Multi_core CPU (mean)"
                    write_cpu_core=f"(Used {core_num} cores)"
                else:
                    write_cpu_type="CPU (mean)"
                    write_cpu_core=""

                if Use_during:
                    write_cpu_during=f"\nCPU During : {CPU_during} FPS={FPS}"
                else:
                    write_cpu_during=""

                
                self.logger.info(f"[{write_cpu_type}] {data_type} {tag} : {cpu_estimated}% {write_cpu_core} {write_cpu_during}")
                self.logprint(level="data",text=f"data_resource_usage 寫入->\t[{write_cpu_type}] {data_type} {tag} : {cpu_estimated}% {write_cpu_core} {write_cpu_during}")
                

            if "Memory" in choose and memory is not None:
                if Use_during:
                    write_Memory_during=f"\nMemory During : {Memory_during} FPS={FPS}"
                else:
                    write_Memory_during=""

                self.logger.info(f"[Memory] {data_type} {tag} : {memory}{Memory_unit} {write_Memory_during}")
                self.logprint(level="data", text=f"data_resource_usage 寫入->\t[Memory] {data_type} {tag} : {memory}{Memory_unit} {write_Memory_during}")

    def else_info(self, data,info_type, data_type="", message="", unit=""):
        if "all" in self._config or "log" in self._config or "else_info" in self._config:
            self.logger.info(f"[{info_type}] {data_type} {message} : {data}{unit}")
            self.logprint(level="data",text=f"else info 寫入->\t[{info_type}] {data_type} {message} : {data}{unit}")


class CodeTimer:
    
    def __init__(self,choose=["all"], Print_Funct="all"):

        self.start_times = {}
        self.records = [] 
        self._config = set(choose)

        # 設定輸出到終端機權限
        self.Print_funct = Print_Funct
        self.printer = PrintManager(mode=Print_Funct, prefix="[CodeTimer]\t")
        self.Timerprint = self.printer.print_level_handle
        self.Timerprint(f"CodeTimer choose 以設定: {self._config}")

    def start(self, tag,group=""):
        if group!="":
            tag=f"{group}-{tag}"
        self.start_times[tag] = time.perf_counter()
        
    def stop(self, tag, size=None):
        if tag in self.start_times:
            end = time.perf_counter()
            elapsed = end - self.start_times[tag]
            self.records.append({
                'tag': tag,
                'start': self.start_times[tag],
                'end': end,
                'duration': elapsed,
                'size': size
            })
            return elapsed
        else:
            self.Timerprint(level="warning",text=f" !!! 未建立{tag} starttime 節點標籤 !!!")
            return None
    
    
    def generate_timeline_plot(self, file_name="",refresh=True,size_off=False):
        if  "all" in self._config or "timeline" in self._config:
            max_records = 100
            records = self.records[:max_records]

            if not records:
                self.Timerprint(level="error",text=" !!! 沒有任何時間紀錄 !!!")
                return
            
            if  len(records)>max_records:
                self.Timerprint(level="warning",text=" !!! 記錄的資料太多,只保留前100個資料 !!!")

            if file_name=="":
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/timeline_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"
            
            tag_records = defaultdict(list)
            for rec in records:
                tag_records[rec['tag']].append(rec)

            # 為每個 tag 分配一條 y 軸位置
            tag_y_map = {tag: i for i, tag in enumerate(tag_records.keys())}

            fig, ax = plt.subplots(figsize=(10, len(tag_y_map) * 0.6))
            for tag, rec_list in tag_records.items():
                y_pos = tag_y_map[tag]
                for rec in rec_list:
                    start = rec['start'] - records[0]['start']
                    duration = rec['duration']
                    end = rec['end'] - records[0]['start']
                    size= rec['size']
                    ax.broken_barh([(start, duration)], (y_pos - 0.2, 0.4), facecolors='skyblue')
                    ax.text(start + duration / 2, y_pos, f"{duration:.2f}s", ha='center', va='center', fontsize=8)
                    if not size_off:
                        ax.text(end+0.25 , y_pos+ 0.25, f"{size}B", ha='right', va='bottom', fontsize=8)
            ax.set_yticks(range(len(tag_y_map)))
            ax.set_yticklabels(tag_y_map.keys())
            ax.set_xlabel("Time (s)")
            if size_off:
                ax.set_title("系統時序圖：處理階段耗時")
            else:
                ax.set_title("系統時序圖：處理階段耗時與資料大小")
            ax.grid(True, axis='x')
            plt.tight_layout()
            plt.savefig(save_path)
            self.Timerprint(f"✅ 已產生時序圖{save_path}")
            if refresh:
                self.records.clear()
                self.Timerprint("✅ records 已清空")
        else:
            self.Timerprint("未啟動 generate_timeline_plot")
            return


    def Function_duration(self, log_name="", file_name="", feature_mapping=None,feature_mapping_style="auto",
                             size_off=False, title="",detail_timestamp=False, Sorting_method="time_length",
                             detail_timestamp_same_color=False,tick_interval=None,limit_longtime=None):
        
        if "all" in self._config or "Function_duration" in self._config:
            
            # 設定 log 檔路徑
            if log_name == "":
                now = datetime.now().strftime("%Y%m%d_%H")
                log_path = f"./documentary/log_{now}.log"
            else:
                log_path = f"./documentary/{log_name}.log"

            # 檢查 log 路徑是否存在
            if not os.path.exists(log_path):
                self.Timerprint(level="error",text=f" !!! 不存在 {log_path} !!!")
                return
            else:
                self.Timerprint(f"分析: {log_path}")

            # 決定儲存路徑
            if not file_name:
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/function_time_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"

            # 標題設定
            if title == "":
                title = "各項功能總耗時" if size_off else "各項功能總耗時與資料大小"

            # 避免在沒啟用 detail_timestamp 功能誤用了 detail_timestamp_same_color 功能
            if (not detail_timestamp) and detail_timestamp_same_color:
                detail_timestamp_same_color=False
                self.Timerprint(level="warning",text=" <Function_duration> 未啟用 detail_timestamp -> 關閉 detail_timestamp_same_color 功能")

            # 功能對應表
            if feature_mapping==None:
                feature_mapping = build_feature_mapping_from_log(
                    log_path, feature_mapping_style, match_type="Data Size", predefined_mapping=feature_mapping
                )

            feature_mapping_list = set(feature_mapping.values())
            if not feature_mapping_list:
                self.Timerprint(level="error",text=f"⚠️ 無有效的 feature_mapping,無資料繪圖")
                return
            else:
                self.Timerprint(f"feature_mapping_list: {feature_mapping_list}")

            # 統計結構
            time_summary = defaultdict(float)                           
            size_summary = defaultdict(float)                           
            sub_time_summary = defaultdict(lambda: defaultdict(float))  # 子功能對應
            first_appearance_order = {}                                 # 儲存 arrival time 順序
            sub_feature_first_appearance_order = {}
            order_counter = 0
            sub_counter = 0

            # 取得所有資訊
            with open(log_path, "r", encoding='utf-8-sig', errors='replace') as f:
                for line in f:
                    if "[Data Time]" in line:
                        match = re.search(r"\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            used_time = float(match.group(2))
                            main_tag = feature_mapping.get(tag, tag)
                            if main_tag in feature_mapping_list:
                                time_summary[main_tag] += used_time
                                sub_time_summary[main_tag][tag] += used_time

                                # 排序整體功能和子功能的
                                if main_tag not in first_appearance_order:
                                    first_appearance_order[main_tag] = order_counter
                                    order_counter += 1
                                if tag not in sub_feature_first_appearance_order:
                                    sub_feature_first_appearance_order[tag] = sub_counter
                                    sub_counter += 1

                    elif "[Data Size]" in line:
                        match = re.search(r"\[Data Size\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            size = float(match.group(2))
                            main_tag = feature_mapping.get(tag, tag)
                            if main_tag in feature_mapping_list:
                                size_summary[main_tag] += size

            self.Timerprint(f"📊 排序方式: {Sorting_method}")
            
            

            # 進行排序
            if detail_timestamp:
                if Sorting_method == "arrival_time":
                    sorted_big = sorted(time_summary.items(), key=lambda x: first_appearance_order.get(x[0], float('inf')), reverse=True)
                else:
                    sorted_big = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)

                big_labels = [k for k, _ in sorted_big]
                big_values = [list(sub_time_summary[k].values()) for k in big_labels]
                big_sublabels = [list(sub_time_summary[k].keys()) for k in big_labels]

                max_total_time = max(sum(v) for v in big_values)
                self.Timerprint(f"⏱️ 最大總耗時：{max_total_time:.2f} 秒")

                if detail_timestamp_same_color:

                    stripped_tags = {strip_main(tag,"sub_tag") for tags in big_sublabels for tag in tags}

                    # 排序順序由首次出現的原始 tag 決定
                    def get_order(tag):
                        for full_tag in sub_feature_first_appearance_order:
                            if strip_main(full_tag,"sub_tag") == tag:
                                return sub_feature_first_appearance_order[full_tag]
                        return float('inf')

                    sorted_stripped = sorted(stripped_tags, key=get_order)
                    cmap = cm.get_cmap("tab20", len(sorted_stripped))
                    sub_colors = {tag: cmap(i) for i, tag in enumerate(sorted_stripped)}
                    colors = [[sub_colors[strip_main(tag,"sub_tag")] for tag in tags] for tags in big_sublabels]
                else:
                    all_sub = list({tag for tags in big_sublabels for tag in tags})
                    all_sub.sort(key=lambda tag: sub_feature_first_appearance_order.get(tag, float('inf')), reverse=True)
                    cmap = cm.get_cmap("tab20", len(all_sub))
                    sub_colors = {tag: cmap(i) for i, tag in enumerate(all_sub)}
                    colors = [[sub_colors[tag] for tag in tags] for tags in big_sublabels]

                plot_bar(big_labels, big_values, save_path, title=title, is_stacked=True, colors=colors, sub_colors=sub_colors,
                        data_sizes=size_summary,longest_time=max_total_time,tick_interval=tick_interval,fixed_xlim=limit_longtime,size_off=size_off)
            else:
                if Sorting_method == "arrival_time":
                    sorted_items = sorted(time_summary.items(), key=lambda x: first_appearance_order.get(x[0], float('inf')), reverse=True)
                else:
                    sorted_items = sorted(time_summary.items(), key=lambda x: x[1], reverse=True)

                labels, values = zip(*sorted_items)

                max_total_time = max(values)
                self.Timerprint(f"⏱️ 最大總耗時：{max_total_time:.2f} 秒")

                cmap = cm.get_cmap("tab10", len(values))
                colors = [cmap(i) for i in range(len(values))]

                plot_bar(list(labels), list(values), save_path, title=title, is_stacked=False, colors=colors, data_sizes=size_summary,
                        longest_time=max_total_time,tick_interval=tick_interval,fixed_xlim=limit_longtime,size_off=size_off)

            self.Timerprint(f"✅ 已產生圖 {save_path}")
        else:
            self.Timerprint("未啟動 Function_duration")
            return



class Analyze:
    def __init__(self,choose=["all"], Print_Funct="all",resource_choose=["CPU", "Memory"],Multi_core=False,Recording_process=False,memory_unit="MB",FPS=5):

        self._config = set(choose)

        # 設定輸出到終端機權限
        self.Print_funct = Print_Funct
        self.printer = PrintManager(mode=Print_Funct, prefix="[Analyze]\t")
        self.Analyzeprint = self.printer.print_level_handle
        self.Analyzeprint(f"Analyze choose 以設定: {self._config}")

        # 紀錄 CPU 和 記憶體資源
        self._resource_choose = resource_choose
        self._Multi_core = Multi_core
        self._memory_unit = memory_unit
        self._Recording_process =Recording_process
        self._FPS=FPS

        # 宣告所有 teg 存放
        self._active_resource_watches = {}

    def analyze_input(self,data):
        # 嘗試是 JSON 字串
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                self.Analyzeprint(level="data",text=f"✅ 這是 JSON 字串")
                return "json", len(data.encode('utf-8'))
            except json.JSONDecodeError:
                self.Analyzeprint(level="data",text="✅ 這是純文字")
                return "text", len(data.encode('utf-8'))

        elif isinstance(data, dict) or isinstance(data, list):
            self.Analyzeprint(level="data",text="✅ 這是已解析的 JSON 結構")
            return "json_dict", len(str(data).encode('utf-8'))

        elif isinstance(data, bytes):
            self.Analyzeprint(level="data",text="✅ 這是二進制資料")
            return "binary", len(data)

        else:
            self.Analyzeprint(level="data",text="❓ 無法辨識")
            return "unknown", len(str(data).encode('utf-8'))
        
    def datasize_percent(self, log_name="", file_name="", feature_mapping=None,feature_mapping_style="auto",
                        label_type="DataSize (Byte)",Values_Visible=True,Percentage_Visible=True):
        if "all" in self._config or "datasize_percent" in self._config:
            
            # 設定 log 檔路徑
            if log_name == "":
                now = datetime.now().strftime("%Y%m%d_%H")
                log_path = f"./documentary/log_{now}.log"
            else:
                log_path = f"./documentary/{log_name}.log"
            
            if not os.path.exists(log_path):
                self.Analyzeprint(level="error",text=f" !!! 不存在指定log檔路徑: {log_path} !!!")
                return
            else:
                self.Analyzeprint(f"分析: {log_path}")

            # 決定儲存路徑
            if not file_name:
                now = datetime.now().strftime("%Y%m%d_%H")
                save_path = f"./documentary/datasize_percent_{now}.png"
            else:
                save_path = f"./documentary/{file_name}.png"

            #  預設功能對應表
            feature_mapping = build_feature_mapping_from_log(log_path,feature_mapping_style,match_type="Data Size", 
                                                             predefined_mapping=feature_mapping)
            
            size_summary = defaultdict(float)        
            feature_mapping_list = set(feature_mapping.values())
            if not feature_mapping_list:
                self.Analyzeprint(level="error",text=" !!! 無有效的 feature_mapping !!!")
                return
            else:
                self.Analyzeprint(f"feature_mapping_list: {feature_mapping_list}")

            with open(log_path, "r", encoding='utf-8-sig', errors='replace') as f:
                for line in f:
                    if "[Data Size]" in line:
                        match = re.search(r"\[Data Size\]\s+(.*?)\s+:\s+([\d.]+)", line)
                        if match:
                            tag = match.group(1).strip()
                            size = float(match.group(2))
                            main_tag = feature_mapping.get(tag, tag)
                            if main_tag in feature_mapping_list:
                                size_summary[main_tag] += size

            labels = list(size_summary.keys())
            values = list(size_summary.values())


            plot_pie(labels,values,save_path,title="各項功能的資料大小總占比",label_type=label_type,
                     emphasize_num=1,Values_Visible=Values_Visible,Percentage_Visible=Percentage_Visible)

    def start_resource_watch(self, tag):
        proc = psutil.Process(os.getpid())
        proc.cpu_percent(interval=None)                 # CPU 紀錄時要先清空之前的殘餘的執行紀錄 
        monitor = ResourceMonitor(tag, proc, self._FPS)

        monitor.start()
        self._active_resource_watches[tag] = {
            "start_time": time.perf_counter(),
            "monitor": monitor,
            "multi_core": self._Multi_core,
            "memory_unit": self._memory_unit,
            "choose": self._resource_choose,
            "Recording_process": self._Recording_process,
            "FPS": self._FPS,
        }
        print("->start tag=\t",tag)
    

    def end_resource_watch(self, tag, log=None, data_type=""):
        if tag not in self._active_resource_watches:
            self.Analyzeprint(level="warning", text=f"!!! 未建立{tag} start_resource_watch 節點標籤 !!!")
            return
         
        watch = self._active_resource_watches.pop(tag)  # 開始資源監控時的資訊
        end_time = time.perf_counter()              
        duration = end_time - watch["start_time"]       # 傳回監控時間
        cores = psutil.cpu_count()                      # 取得目前裝置的核心數
       
        monitor = watch["monitor"]              # 取得監控裝置
        unit = watch["memory_unit"]             # 取得記憶體單位
        samples_cpu, samples_mem = monitor.stop() if monitor else ([], [])  #取得 monitor 監控期間每個時間段的資訊

        # --------- 記憶體 ---------
        if samples_mem:  
            Memory_during = [mem / watch["FPS"] for mem in samples_mem]
            mem_estimated = round(sum(Memory_during) / Unit_conversion[unit], 3)
        else:
            mem_estimated = 0.0
        
        # --------- CPU ---------
        cpu_raw = round(sum(samples_cpu) / len(samples_cpu), 3) if samples_cpu else 0.0
        cpu_share = round((cpu_raw / (100 * cores)) * 100, 3) if samples_cpu else 0.0

        # --------- CPU During Log ---------
        if watch["multi_core"]:                                            
            multi_core_sample = [round(s / cores, 3) for s in samples_cpu]
            CPU_during = f"{multi_core_sample}"
        else:
            CPU_during = f"{samples_cpu}"

        # --------- 寫入 Log ---------
        if log:
            log.data_resource_usage(
                tag            =tag,
                data_type      =data_type,
                Memory_unit    =unit,
                choose         =watch["choose"],
                Use_multi_core = watch["multi_core"],
                Use_during     =watch["Recording_process"],
                override_values={
                    "cpu_estimated":cpu_share if watch.get("multi_core") else cpu_raw,
                    "memory": mem_estimated,
                    "core": cores,
                    "FPS": watch["FPS"],
                    "CPU_during": CPU_during if watch.get("Recording_process") else None,
                    "Memory_during":Memory_during if watch.get("Recording_process") else None,
                }
            )

        self.Analyzeprint(level="data",text=f"📈 CPU: {cpu_raw}% ,Memory: {mem_estimated} MB, Time: {duration:.2f}s")
        print("->end tag=\t",tag)
        return duration, cpu_raw, cpu_share, mem_estimated


    def hourly_time_flow(
        self,
        log_path: str,
        start_time: datetime,
        end_time: datetime,
        save_path: str = "./hourly_function_time.png",
        tag_filter: list = None  # 加入這個參數，支援功能過濾
    ):
        """
        讀取單一 log 檔案（包含 [Data Time]），依據時間範圍與每小時，統計各功能總耗時，畫出折線圖。

        Parameters:
        - log_path: str → log 檔案路徑
        - start_time: datetime → 只分析該時間以後的 log
        - end_time: datetime → 只分析該時間以前的 log
        - save_path: str → 圖片儲存路徑
        - tag_filter: list → 限定要畫的功能名稱（預設 None 表示全畫）
        """

        pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+- INFO - \[Data Time\]\s+(.*?)\s+:\s+([\d.]+)s'
        )
        hourly_function_times = defaultdict(lambda: defaultdict(float))  # {hour -> {tag -> total_time}}
        function_totals = defaultdict(float)

        with open(log_path, encoding='utf-8') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                    if not (start_time <= timestamp <= end_time):
                        continue
                    tag = match.group(2).strip()
                    if tag_filter and tag not in tag_filter:
                        continue  # 不在篩選清單中的就跳過
                    duration = float(match.group(3))
                    hour = timestamp.replace(minute=0, second=0, microsecond=0)
                    hourly_function_times[hour][tag] += duration
                    function_totals[tag] += duration

        # 整理資料
        hours = sorted(hourly_function_times.keys())
        all_tags = sorted(set(tag for tags in hourly_function_times.values() for tag in tags))
        data_dict = {
            tag: [hourly_function_times[hour].get(tag, 0) for hour in hours]
            for tag in all_tags
        }

        # 調用通用折線圖繪製函數
        plot_multiline_timeseries(
            time_index=hours,
            data_dict=data_dict,
            save_path=save_path,
            title="Total execution time when calculating risk",
            xlabel="Time",
            ylabel="Execution time (s)",
            font_config=None  # 或用 Default_font
        )

        return dict(function_totals)

    def plot_resource_distribution(
        self,
        log_path: str,
        save_path: str = "./resource_dist.png",
        metric: str = "both",                   # "cpu" / "mem" / "both"
        top_n: int = None,                      # 僅顯示前 N 名，其餘合併為 "Other"
        memory_display_unit: str="keep",        # 是否對記憶體做單位轉換(keep 表示採用log裡的單位)      
        feature_mapping: dict = None,
        font_config: dict = None,
        show_percent: bool = True,
                     
    ):
        def merge_by_feature_mapping(data_dict, mapping):
            merged = defaultdict(float)
            for tag, value in data_dict.items():
                # 用 mapping 把 tag 轉成主功能
                main_tag = mapping.get(tag, tag)
                merged[main_tag] += value
            return dict(merged)

        if not os.path.exists(log_path):
            self.Analyzeprint(level="error",text=f"<plot_resource_distribution> !!! log not found: {log_path}")
            return
        

        cpu_pat = re.compile(r"\[CPU \(mean\)\]\s+(.*?)\s+:\s+([\d.]+)%")
        mem_pat = re.compile(r"\[Memory\]\s+(.*?)\s+:\s+([\d.]+)\s*([A-Za-z]+)")
        
        cpu_dict, mem_dict = defaultdict(float), defaultdict(float)

        with open(log_path, encoding="utf-8") as f:
            for line in f:
                # CPU 區
                match = cpu_pat.search(line)
                if match:
                    tag = match.group(1)
                    cpu_val = float(match.group(2))
                    cpu_dict[tag] += cpu_val
                # 記憶體區
                match = mem_pat.search(line)
                if match:
                    tag = match.group(1)
                    num_val  = float(match.group(2))
                    unit = match.group(3)
                    mem_dict[tag] += num_val   
                
                    
        if not cpu_dict and not mem_dict:
            self.Analyzeprint(level="error",text="<plot_resource_distribution> 沒抓到任何資源紀錄")
            return

        cfg = {**Default_font, **(font_config or {})}
        if feature_mapping:
            cpu_dict = merge_by_feature_mapping(cpu_dict, feature_mapping)
            mem_dict = merge_by_feature_mapping(mem_dict, feature_mapping)\
            
        def _aggregate(d: dict):
            """依 top_n 對 dict 做 other 合併並回傳 labels & values"""
            if not top_n or len(d) <= top_n:
                return list(d.keys()), list(d.values())

            sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)
            kept = sorted_items[:top_n]
            other_sum = sum(v for _, v in sorted_items[top_n:])
            labels = [k for k, _ in kept] + ["Other"]
            values = [v for _, v in kept] + [other_sum]
            return labels, values

        

        # --------- CPU ----------
        if metric.lower() in ("cpu", "both") and cpu_dict:
            lbl, val = _aggregate(cpu_dict)
            cpu_path = save_path if metric == "cpu" else save_path.replace(".png", "_CPU.png")
            plot_pie(
                labels=lbl,
                values=val,
                save_path=cpu_path,
                title="CPU usage",
                label_type="CPU (%)",
                font_config=cfg,
                emphasize_num=1,
                Values_Visible=False,
                Percentage_Visible=show_percent
            )
            self.Analyzeprint(f"✅ 已產生圖 {cpu_path}")


        # --------- Memory ----------
        if metric.lower() in ("mem", "both") and mem_dict:
            if memory_display_unit != "keep":
                divisor = Unit_conversion[unit]/Unit_conversion[memory_display_unit]
                mem_dict = {k: round(v * divisor,3) for k, v in mem_dict.items()}
                unit = memory_display_unit  # 用指定單位顯示

            lbl, val = _aggregate(mem_dict)
            mem_path = save_path if metric == "mem" else save_path.replace(".png", "_Memory.png")
            plot_pie(
                labels=lbl,
                values=val,
                save_path=mem_path,
                title="Memory usage",
                label_type=f"Memory ({unit})",
                font_config=cfg,
                emphasize_num=1,
                Values_Visible=True,
                Percentage_Visible=show_percent
            )
            self.Analyzeprint(f"✅ 已產生圖 {mem_path}")
            

# === Helper function for快速結束並記錄 === (結合log時間、大小紀錄 + 時間stop節點) 
def timer_stop_log(tag,group="",size=None, content="", timer=None, log=None):
    """
    自動停止計時並記錄耗時與資料大小

    :param tag: 記錄的標籤名稱
    :param content: 要分析大小的資料
    :param timer: CodeTimer 實例
    :param log: Log 實例
    """

    if timer is None or log is None:
        print("❗請傳入 timer 與 log 實例")
        return
    if size==None:
        size_content=len(str(content).encode('utf-8'))
    else:
        size_content=size

    if group!="":
        tag=f"{group}-{tag}"

    elapsed = timer.stop(tag, size=size_content)
    log.data_time(elapsed, message=tag,root_config_enable=True)
    log.data_size(size_content, message=tag,root_config_enable=True)
    return elapsed



"""
def plot_hourly_function_time_trend(log_dir="./documentary", save_path="./documentary/hourly_function_time.png"):
    pattern = re.compile(r'\[Data Time\]\s+(.*?)\s+:\s+([\d.]+)')
    hourly_data = defaultdict(lambda: defaultdict(float))  # {hour -> {tag -> total_time}}

    log_files = sorted(glob.glob(os.path.join(log_dir, "log_*.log")))

    for file_path in log_files:
        match_hour = re.search(r"log_(\d{8}_\d{2})\.log", os.path.basename(file_path))
        if not match_hour:
            continue
        hour_str = match_hour.group(1)
        hour_time = datetime.strptime(hour_str, "%Y%m%d_%H")

        with open(file_path, "r", encoding='big5', errors='replace') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    tag = match.group(1).strip()
                    duration = float(match.group(2))
                    hourly_data[hour_time][tag] += duration

    if not hourly_data:
        print("❗ 沒有找到任何符合的 log 檔案")
        return

    # 確定所有功能名稱
    all_tags = set()
    for tag_data in hourly_data.values():
        all_tags.update(tag_data.keys())
    all_tags = sorted(all_tags)

    # 將時間與資料轉為圖表格式
    times = sorted(hourly_data.keys())
    plot_data = {tag: [] for tag in all_tags}

    for t in times:
        for tag in all_tags:
            plot_data[tag].append(hourly_data[t].get(tag, 0))

    # 畫圖
    plt.figure(figsize=(12, 6))
    for tag in all_tags:
        plt.plot(times, plot_data[tag], label=tag)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gcf().autofmt_xdate()

    plt.title("每小時各功能總耗時趨勢")
    plt.xlabel("時間")
    plt.ylabel("耗時（秒）")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"✅ 折線圖已儲存至 {save_path}")

"""