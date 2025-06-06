//本支程式查找userID做景點規劃
<?php
// 開啟 CSV 檔案
$file = fopen('C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/penghu_csv_file/plan.csv', 'r');
$i=0;
$latitude=array();
$longitude=array();
$plan = array();
$location = array();
// 要查找的字串
$searchString = 'age';

// 宣告一個空陣列來存儲結果
$results = array();

// 讀取 CSV 檔案中的每一行
while (($line = fgetcsv($file)) !== FALSE) {
    
    // 將該行轉換為字串
    $lineString = implode(',', $line);

    // 使用 strpos 函數檢查該行是否包含指定字串
    if (strpos($lineString, $lineString) !== false) {
        
        // 如果找到指定字串，將該行的數組值添加到結果陣列中
        array_push($results, $lineString);
        $plan = explode(",",$results[$i]);
        array_push( $location,$plan[5] );
        array_push($latitude,$plan[6] );
        array_push($longitude,$plan[7] );
        
        $i++;
       
    }
}
// 關閉 CSV 檔案
fclose($file);

// 輸出結果陣列
//print_r($results[0]);

//print_r($latitude);
//echo '<br>';  
//print_r($longitude);
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
                top:0%;
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
        <h1>澎湖地圖練習</h1>
    
    <div id="map"></div>

    <script type="text/JavaScript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" ></script>
    
    <script>

        var JS_i =["<?php echo $i; ?>"];
        var JS_latitude = ["<?php echo join("\", \"", $latitude); ?>"];
        var JS_longitude = ["<?php echo join("\", \"", $longitude); ?>"];
        var JS_place = ["<?php echo join("\", \"", $location ); ?>"];
        //console.log(JS_longitude[0])
        var map;
        function initMap(){

            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 23.57226, lng: 119.57102},
                zoom: 15,
                mapId: "5cb7f499bf3d65",
                
            });
            
        

            for (i = 0; i < JS_i; i++) {//130275
                var measle = new google.maps.Marker({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    icon: {
                        url: "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",//https://i.imgur.com/RcsQXFc.png -> redcircle 
                        scaledSize: new google.maps.Size(25, 25),
                        anchor: new google.maps.Point(4, 4),
                        
                    },
                    opacity: 1
                });
                var contentString =  JS_place[i];
                 //InfoWindow 會在地圖上方特定位置的彈出式視窗中顯示內容 (通常為文字或圖片)。
                //資訊視窗是由一個內容區域和一個錐形柄所組成，錐形柄的尖端會連接地圖上的指定位置。
                //資訊視窗會以對話方塊的形式顯示在螢幕閱讀器中。
                var infowindow = new google.maps.InfoWindow({
                    position: new google.maps.LatLng(JS_latitude[i],JS_longitude[i]),
                    map: map,
                    content: contentString,
                    //content：包含要在資訊視窗中顯示的一串文字或一個 DOM 節點。
                    maxWidth: 400
                

                })

        }
    }
    </script>
         <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCa5Ww5XHTu4cJCSSfZaxf1GGUTHyyYIx0&callback=initMap"
      async
    ></script>

</html>





