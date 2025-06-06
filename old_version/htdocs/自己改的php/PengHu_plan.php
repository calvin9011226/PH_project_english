<!DOCTYPE html>
<html>

    <head>
        
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>澎湖景點資料庫</title>
        
     <style>
        
        html{
                width: 100%;
                height: 100%;
            }
            #map{
                position: absolute;/*absolute relative  */
                top: 100;
                left: 100;
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
    <h1>澎湖景點資料庫</h1>
    

    <?php

        $DB_HOST = '127.0.0.1'; // 主機
        $DB_USER = 'root';  // 登入 MySQL server 的帳號
        $DB_PASS = 'nclab722'; // 密碼
        $DB_NAME = 'penghu'; // 要登入的資料庫名稱
        $DB_PAGE = "SELECT * FROM test";
        $conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);


        $i= 0;
        $no=array();
        $time=array();
        $setpoint=array();
        $UserID_MemID=array();
        $latitude=array();
        $longitude=array();



        if (!mysqli_select_db($conn, $DB_NAME)) 
        {
            die("連接失敗" );
        }
        $result = mysqli_query($conn, $DB_PAGE);

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


        for ($x = 0; $x < $length = count($no); $x++) 
        {
        printf("%s,%s,%s,%s,%s,%s<br>",$no[$x],$time[$x], $UserID_MemID[$x],$setpoint[$x],$latitude[$x],$longitude[$x]);
        }
    ?>


    <div id="map"></div>


    <script type="text/JavaScript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" ></script>
    
    <script>

        var JS_number = ["<?php echo join("\", \"", $no); ?>"];//PHP array to JS array
        var JS_time = ["<?php echo join("\", \"", $time); ?>"];
        var JS_UserID_MemID=["<?php echo join("\", \"", $UserID_MemID); ?>"];
        var JS_setpoint= ["<?php echo join("\", \"", $setpoint); ?>"];
        var JS_latitude = ["<?php echo join("\", \"", $latitude); ?>"];
        var JS_longitude = ["<?php echo join("\", \"", $longitude); ?>"];
        // console.log(JS_longitude[0])
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
                var contentString = JS_place[i];
                 //InfoWindow 會在地圖上方特定位置的彈出式視窗中顯示內容 (通常為文字或圖片)。
                //資訊視窗是由一個內容區域和一個錐形柄所組成，錐形柄的尖端會連接地圖上的指定位置。
                //資訊視窗會以對話方塊的形式顯示在螢幕閱讀器中。
                var infowindow = new google.maps.InfoWindow({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    content: contentString,
                    //content：包含要在資訊視窗中顯示的一串文字或一個 DOM 節點。
                    maxWidth: 400
                });

            }

          }
    </script>
         <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap"
      async
    ></script>

</html>






