<!-- 測試版:將行程規劃做成map,並且未來要吃使用者位置-->
<?php
$DB_HOST = '127.0.0.1'; // 主機
$DB_USER = 'root';  // 登入 MySQL server 的帳號
$DB_PASS = 'nclab722'; // 密碼
$DB_NAME = 'penghu'; // 要登入的資料庫名稱
$DB_PAGE = "SELECT * FROM plan";

$conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);

$i = 0;
$number = array();
$place = array();
$latitude = array();
$longitude = array();

if (!mysqli_select_db($conn, $DB_NAME)) {
    die("連接失敗");
}

$result = mysqli_query($conn, $DB_PAGE);
while ($row = mysqli_fetch_array($result, MYSQLI_BOTH)) {
    $number[$i] = $row['no'];
    $place[$i] = $row['設置點'];
    $latitude[$i] = $row['緯度'];
    $longitude[$i] = $row['經度'];
    $i++;
}

mysqli_close($conn);
?>

<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>澎湖景點規劃</title>
    <style>
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        #map {
            height: 90%;
            width: 100%;
        }
        h1 {
            text-align: center;
            margin: 10px 0;
        }
        #controls {
            text-align: center;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>澎湖景點規劃</h1>
    <div id="controls">
        <button onclick="toggleAllDistances()">顯示/隱藏所有距離</button>
    </div>
    <div id="map"></div>

    <script>
        var map;
        var markers = [];
        var infoWindows = [];
        var distanceInfoWindows = [];
        var showAllDistances = false;

        var JS_number = <?php echo json_encode($number); ?>;
        var JS_place = <?php echo json_encode($place); ?>;
        var JS_latitude = <?php echo json_encode($latitude); ?>;
        var JS_longitude = <?php echo json_encode($longitude); ?>;

        function initMap() {
            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 23.57226, lng: 119.57102},
                zoom: 15,
                mapId: "5cb7f499bf3d65",
            });
            
            // 創建標記和信息窗口
            for (var i = 0; i < JS_number.length; i++) {
                var position = new google.maps.LatLng(JS_latitude[i], JS_longitude[i]);
                var marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    icon: {
                        url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
                        scaledSize: new google.maps.Size(32, 32),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(16, 32),
                    },
                    opacity: 0.8
                });
                
                var duration = getRandomDuration(30, 90);
                var contentString = JS_place[i] + "<br>建議停留時間：" + duration + " 分鐘";
                
                var infoWindow = new google.maps.InfoWindow({
                    content: contentString
                });

                markers.push(marker);
                infoWindows.push(infoWindow);

                // 為每個標記添加點擊事件
                marker.addListener('click', (function(marker, i) {
                    return function() {
                        infoWindows[i].open(map, marker);
                    }
                })(marker, i));
            }

            // 計算並顯示距離
            for (var i = 0; i < markers.length - 1; i++) {
                for (var j = i + 1; j < markers.length; j++) {
                    calculateAndDisplayRoute(markers[i], markers[j], i, j);
                }
            }
        }

        function calculateAndDisplayRoute(markerA, markerB, indexA, indexB) {
            var directionsService = new google.maps.DirectionsService();
            var directionsRenderer = new google.maps.DirectionsRenderer({
                map: map,
                suppressMarkers: true,
                preserveViewport: true
            });

            directionsService.route({
                origin: markerA.getPosition(),
                destination: markerB.getPosition(),
                travelMode: google.maps.TravelMode.DRIVING
            }, function(response, status) {
                if (status === google.maps.DirectionsStatus.OK) {
                    directionsRenderer.setDirections(response);
                    var route = response.routes[0];
                    var distanceInMeters = route.legs[0].distance.value;
                    var distanceInKm = (distanceInMeters / 1000).toFixed(2);

                    var midpoint = route.legs[0].steps[Math.floor(route.legs[0].steps.length / 2)].start_location;
                    var infoWindow = new google.maps.InfoWindow({
                        position: midpoint,
                        content: distanceInKm + " km"
                    });
                    distanceInfoWindows.push(infoWindow);

                    if (showAllDistances) {
                        infoWindow.open(map);
                    }
                }
            });
        }

        function getRandomDuration(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        function toggleAllDistances() {
            showAllDistances = !showAllDistances;
            distanceInfoWindows.forEach(function(infoWindow) {
                if (showAllDistances) {
                    infoWindow.open(map);
                } else {
                    infoWindow.close();
                }
            });
        }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap" async defer></script>
</body>
</html>