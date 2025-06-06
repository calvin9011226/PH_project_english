<?php

  $DB_HOST = '127.0.0.1'; // 主機
  $DB_USER = 'root';  // 登入 MySQL server 的帳號
  $DB_PASS = '0936052321'; // 密碼
  $DB_NAME = 'penghu'; // 要登入的資料庫名稱
  $DB_PAGE = "SELECT * FROM realtimehotel";
  $conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);

  $i= 0;
  $number=array();
  $place=array();
  $latitude=array();
  $longitude=array();
  if (!mysqli_select_db($conn, $DB_NAME)) {
    die("連接失敗" );
  }
  $result = mysqli_query($conn, $DB_PAGE);
  while ($row = mysqli_fetch_array($result, MYSQLI_BOTH)) {
    $place[$i]=$row['name'];
    $latitude[$i]=$row['緯度'];
    $longitude[$i]=$row['經度'];
    $url_[$i]=$row['url'];
    $i++;
  }

  ?>
  <!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>澎湖民宿規劃</title>
    
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
        <h1>澎湖民宿規劃</h1>
    
    <div id="map"></div>
    </div>

    <script type="text/JavaScript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" ></script>
    
    <script>

     ;//PHP array to JS array
        var JS_number = ["<?php echo join("\", \"", $number); ?>"]
        var JS_place = ["<?php echo join("\", \"", $place); ?>"];
        var JS_latitude = ["<?php echo join("\", \"", $latitude); ?>"];
        var JS_longitude = ["<?php echo join("\", \"", $longitude); ?>"];
        var JS_url = ["<?php echo join("\", \"", $url_); ?>"];
        console.log(JS_longitude[0])
        var map;
        function initMap(){
            
          

            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat:23.20 ,lng:119.30},
                zoom: 15,
                mapId: "5cb7f499bf3d65",
                
            });
         
      
            
            var marker, i, Date, CSVtime;
            var count = 0;
            var measle = new google.maps.Marker({
                    position: new google.maps.LatLng(JS_latitude[0],JS_longitude[0]),
                    map: map,
                    icon: {
                        url:"https://i.imgur.com/RcsQXFc.png",//https://i.imgur.com/RcsQXFc.png -> redcircle 
                        scaledSize: new google.maps.Size(25, 25),
                        anchor: new google.maps.Point(4, 4),
                        
                    },
                    opacity: 0.5
                });


                var infowindow = new google.maps.InfoWindow({
                    position: new google.maps.LatLng(JS_latitude[0],JS_longitude[0]),
                    map: map,
                    content: '當前位置',
                    //content：包含要在資訊視窗中顯示的一串文字或一個 DOM 節點。
                    maxWidth: 150,
                    maxHeight:100,
                });


                


            for (i = 1; i < JS_number.length; i++) {//130275
                var measle = new google.maps.Marker({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    icon: {
                        url: "https:developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",//https://i.imgur.com/RcsQXFc.png -> redcircle 
                        //url:"https:developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",
                        scaledSize: new google.maps.Size(25, 25),
                        anchor: new google.maps.Point(4, 4),
                        
                    },
                    opacity: 0.5
                });
                var contentString = JS_place[i];
                var content_url = JS_url[i]
                //
                var content = document.createElement('div');
                var additionalContent = document.createElement('p');
                additionalContent.textContent = contentString ;
                content.appendChild(additionalContent);
                var img = document.createElement('img');
                img.src = JS_url[i];
                content.appendChild(img);
                //                           
                                                
                 //InfoWindow 會在地圖上方特定位置的彈出式視窗中顯示內容 (通常為文字或圖片)。
                //資訊視窗是由一個內容區域和一個錐形柄所組成，錐形柄的尖端會連接地圖上的指定位置。
                //資訊視窗會以對話方塊的形式顯示在螢幕閱讀器中。
                var infowindow = new google.maps.InfoWindow({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    content: content,
                    //content：包含要在資訊視窗中顯示的一串文字或一個 DOM 節點。
                    maxWidth: 150,
                    maxHeight:100,
                });

            }

            }
        
    </script>
         <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCa5Ww5XHTu4cJCSSfZaxf1GGUTHyyYIx0&callback=initMap"
      async
    ></script>

</html>




