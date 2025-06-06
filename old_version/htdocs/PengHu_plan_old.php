<?php

  $DB_HOST = '127.0.0.1'; // 主機
  $DB_USER = 'root';  // 登入 MySQL server 的帳號
  $DB_PASS = 'nclab722'; // 密碼
  $DB_NAME = 'penghu'; // 要登入的資料庫名稱
  $DB_PAGE = "SELECT * FROM plan";



  $conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);


  $i= 0;
  $number=array();
  $Time=array();
  $place=array();
  $latitude=array();
  $longitude=array();
  if (!mysqli_select_db($conn, $DB_NAME)) {
    die("連接失敗" );
  }
  $result = mysqli_query($conn, $DB_PAGE);
  while ($row = mysqli_fetch_array($result, MYSQLI_BOTH)) {
    $number[$i]=$row['no'];
    #$Time[$i]=$row['Time'];
    $place[$i]=$row['設置點'];
    $latitude[$i]=$row['緯度'];
    $longitude[$i]=$row['經度'];
    $i++;
   
  }
  //printf("%s,%s,%s,%s,%s",$number[1],$Time[1],$place[1],$latitude[1],$longitude[1]);
  ?>
  <!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>澎湖景點規劃</title>
    
     <style>
            html{
                width: 100%;
                height: 100%;
            }
            #map{
                position: absolute;
                top: 10%;
                left: 0;
                height: 100%;
                width: 100%;
        }
            #body {
                height: 100%;
                width: 100%;
                position: relative;
                top: 0;
                left: 0;
            }
     </style>

    </head>
    <div class="body">
        <h1>澎湖景點規劃</h1>
    
    <div id="map"></div>

    <script type="text/JavaScript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" ></script>
    
    <script>

        var JS_number = ["<?php echo join("\", \"", $number); ?>"];//PHP array to JS array
        var JS_Time = ["<?php echo join("\", \"", $Time); ?>"];
        var JS_place = ["<?php echo join("\", \"", $place); ?>"];
        var JS_latitude = ["<?php echo join("\", \"", $latitude); ?>"];
        var JS_longitude = ["<?php echo join("\", \"", $longitude); ?>"];
        //console.log(JS_longitude[0])
        var map;
        function initMap(){

            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 23.57226, lng: 119.57102},
                zoom: 15,
                mapId: "5cb7f499bf3d65",
                
            });
            
            var marker, i, Date, CSVtime;
            var count = 0;


            for (i = 0; i < JS_number.length; i++) {//130275
                var measle = new google.maps.Marker({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    icon: {
                        url: "https://i.imgur.com/iM0IY7A.jpg",//https://i.imgur.com/RcsQXFc.png -> redcircle 
                        scaledSize: new google.maps.Size(25, 25),
                        anchor: new google.maps.Point(4, 4),
                        
                    },
                    opacity: 0.5
                });
                
                function getRandomDuration(min, max) {
                return Math.floor(Math.random() * (max - min + 1)) + min;
                }
                var placeName = JS_place[i];
                var duration = getRandomDuration(30, 90); // 測試用,產生隨機的停留分鐘數
                var contentString = placeName + "<br>可停留：" + duration + " 分鐘";       
                // var contentString = JS_place[i];
                //InfoWindow 會在地圖上方特定位置的彈出式視窗中顯示內容 (通常為文字或圖片)。
                //資訊視窗是由一個內容區域和一個錐形柄所組成，錐形柄的尖端會連接地圖上的指定位置。
                //資訊視窗會以對話方塊的形式顯示在螢幕閱讀器中。
                var infowindow = new google.maps.InfoWindow({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    content: contentString,
                    //content：包含要在資訊視窗中顯示的一串文字或一個 DOM 節點。
                    maxWidth: 1000
                });

            }

          }
    </script>
         <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap"
      async
    ></script>

</html>




