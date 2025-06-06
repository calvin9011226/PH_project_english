<?php

  $DB_HOST = '127.0.0.1'; // 主機
  $DB_USER = 'root';  // 登入 MySQL server 的帳號
  $DB_PASS = 'nclab722'; // 密碼
  $DB_NAME = 'penghu'; // 要登入的資料庫名稱
  $DB_PAGE = "SELECT * FROM test";
  $conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);


 //與db做連線
 //這行代碼使用 PHP 中的 MySQLi 擴展建立與 MySQL 數據庫的連接。
 //它創建了一個名為 `$conn` 的新變量，用於保存 `mysqli_connect()` 函數返回的連接對象。
  
  $i= 0;
  $no=array();
  $time=array();
  $setpoint=array();
  $UserID_MemID=array();
  $latitude=array();
  $longitude=array();

  if (!mysqli_select_db($conn, $DB_NAME)) {
    die("連接失敗" );
  }
    $result = mysqli_query($conn, $DB_PAGE);
    //使用函數 mysqli_query 通過給定的數據庫連接 $conn 對數據庫執行 SQL 查詢。
    // 執行查詢的結果存儲在變量 $result 中。
    //第二個參數 $DB_PAGE 表示我們要在數據庫上執行的 SQL 查詢。
    while ($row = mysqli_fetch_array($result, MYSQLI_BOTH)) 
    {
      $no[$i]=$row['no'];
      $time[$i]=$row['time'];
      $UserID_MemID[$i]=$row['UserID_MemID'];
      $setpoint[$i]=$row['setpoint'];
      $latitude[$i]=$row['latitude'];
      $longitude[$i]=$row['longitude'];
      $i++;
    }
    //這是一個 PHP 函數 mysqli_fetch_array() ，用於獲取在 MySQL 數據庫上執行的查詢返回的結果行。
    //該函數接受兩個參數：`$result` 和 `$mode`。這裡的 `$result` 是 mysqli_result 類的對象
    //，它由前面執行 SELECT、SHOW、DESCRIBE 或 EXPLAIN 查詢的 MySQLi 函數返回。`$mode` 指定應該返回什麼類型的數組。
    //printf("%s,%s,%s,%s,%s,%s",$number[1],$Time[1],$UserID[1],$place[1],$latitude[1],$longitude[1]);

//     $length = count($no);

//     for ($x = 0; $x < $length; $x++) {
//     printf("%s,%s,%s,%s,%s,%s<br>",$no[$x],$time[$x], $UserID_MemID[$x],$setpoint[$x],$latitude[$x],$longitude[$x]);
//   }
?>
<!DOCTYPE html>
<html lang="zh-tw">

    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>澎湖人群</title>
        <style type="text/css" media="screen">

        html {
            height: 100%;
            width: 100%;
        }
        header {
            
            background-color: #333;
            color: #fff;
            padding: 10px;
            text-align: center;
            margin-left:auto;
            margin-right:auto;
        }

        #map {
            padding-bottom:150%;
            text-align: center;
            margin-left:auto;
            margin-right:auto;
        }

        #body {
        height: 100%;
        width: 100%;
        position: relative;
        margin-left:auto;
        margin-right:auto;
        }
        footer {
            background-color: #333;
            color: #fff;
            padding: 10px;
            text-align: center;
            margin-left:auto;
            margin-right:auto;
        }
        
        </style>
    </head>
    <div class="body">
    <header>
        <h1>當前人潮</h1>
    </header>
        

    <div id="map"></div>

    <script type="text/JavaScript"  src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    
    <script>
        var JS_number = ["<?php echo join("\", \"", $no); ?>"];//PHP array to JS array
        var JS_Time = ["<?php echo join("\", \"", $time); ?>"];
        var JS_UserID = ["<?php echo join("\", \"", $UserID_MemID); ?>"];
        var JS_place = ["<?php echo join("\", \"", $setpoint); ?>"];
        var JS_latitude = ["<?php echo join("\", \"", $latitude); ?>"];
        var JS_longitude = ["<?php echo join("\", \"", $longitude); ?>"];
        var today_data = new Date();
        // `new` 關鍵字用於創建新的對象構造函數，而 `Date` 是 JavaScript 的內置函數之一，可返回當前日期和時間。
        var today_time = today_data.getHours();
        //下一行獲取“today_data”對象並調用其“getHours”方法。
         //總之，此代碼使用 JavaScript 中的“Date”函數檢索當天的當前小時，並將其存儲在名為“today_time”的變量中。
        var today_AMorPM;
        if (today_time>11){
            today_time = today_time - 12;
            today_AMorPM = "PM"
            console.log(today_time);
        }
        else {
            today_AMorPM = "AM"
            console.log(today_time);
        }
        //在 JavaScript 中，`console.log()` 是一個將數據輸出到 Web 瀏覽器控制台或開發人員工具的函數。
        //`today_time` 是一個包含值的變量，並作為參數傳遞給函數 `console.log()`。 
        //簡單來說就是某個數值輸出到web上
        function initMap() {
            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 23.57226, lng: 119.57102},
                zoom: 15,
                mapId: "5cb7f499bf3d65",
            });
            var i, Date,CSVtime;
            var count = 0;
            var crowdLatLng = [];
                 //window.alert(JS_Time[0]); //js_time 陣列中的第0個 //2/1/2022 1:07:51 PM
            for(i = 0; i < JS_number.length;i++){
                Date = JS_Time[i].split(/\s+/); //js_time 中拆一個出來   
                 // /\s/ splits the array at every kind of whitespace character
                sqltime = Date[1].split(':');
                 //window.alert( Date[2]);//PM
                 //window.alert(sqltime[0]); //1
                 //window.alert(today_time);//當前hr
                 //window.alert(JS_latitude[i]);
                 //window.alert(JS_longitude[i]);
                if (sqltime[0] == today_time && Date[2] == today_AMorPM ){
                    count = count + 1;
                        var latLng = new google.maps.LatLng(JS_latitude[i],JS_longitude[i]);
                        crowdLatLng.push(latLng);
                } 
            }  
            heatmap = new google.maps.visualization.HeatmapLayer({
                        data:crowdLatLng, //給座標
                        radius:20,
                        opacity:1,
                        map: map
                        });      //熱視圖
    
            }
    </script>
    <script async
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&libraries=visualization&callback=initMap">
</script>
<footer>
        <p>© PSRS.</p>
    </footer>
   
    
</html>
    