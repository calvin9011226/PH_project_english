<!-- 距離計算:從使用者位置到每個景點的距離分別計算 -->
<?php
$DB_HOST = '127.0.0.1';
$DB_USER = 'root';
$DB_PASS = 'nclab722';
$DB_NAME = 'penghu';
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

$userLat = isset($_GET['lat']) ? floatval($_GET['lat']) : null;
$userLng = isset($_GET['lng']) ? floatval($_GET['lng']) : null;
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
        <button onclick="toggleAllMarkers()">顯示/隱藏所有景點</button>
    </div>
    <div id="map"></div>

    <script>
        var map;
        var markers = [];
        var infoWindows = [];
        var distanceInfoWindows = [];
        var showAllDistances = false;
        var showAllMarkers = true;
        var userMarker;
        var JS_number = <?php echo json_encode($number); ?>;
        var JS_place = <?php echo json_encode($place); ?>;
        var JS_latitude = <?php echo json_encode($latitude); ?>;
        var JS_longitude = <?php echo json_encode($longitude); ?>;
        var userLat = <?php echo $userLat ? $userLat : 'null'; ?>;
        var userLng = <?php echo $userLng ? $userLng : 'null'; ?>;
        // 從 URL 參數中獲取緯度和經度
        $userLat = isset($_GET['lat']) ? floatval($_GET['lat']) : null;
        $userLng = isset($_GET['lng']) ? floatval($_GET['lng']) : null;

        function initMap() {
            var center = userLat && userLng ? {lat: userLat, lng: userLng} : {lat: 23.57226, lng: 119.57102};
            map = new google.maps.Map(document.getElementById('map'), {
                center: center,
                zoom: 15,
                mapId: "5cb7f499bf3d65",
            });
            
            if (userLat && userLng) {
                userMarker = new google.maps.Marker({
                    position: {lat: userLat, lng: userLng},
                    map: map,
                    icon: {
                        url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
                        scaledSize: new google.maps.Size(32, 32),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(16, 32),
                    },
                    title: "您的位置"
                });
            }
            
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

                infoWindow.open(map, marker); // 預設開啟 infoWindow

                marker.addListener('click', (function(marker, i) {
                    return function() {
                        infoWindows[i].open(map, marker);
                    }
                })(marker, i));
            }

            if (userMarker) {
                for (var i = 0; i < markers.length; i++) {
                    calculateAndDisplayRoute(userMarker, markers[i], -1, i);
                }
            }
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
                    var content = distanceInKm + " km";
                    if (indexA === -1) {
                        content = "從您的位置到" + JS_place[indexB] + ": " + content;
                    }
                    var infoWindow = new google.maps.InfoWindow({
                        position: midpoint,
                        content: content
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

        function toggleAllMarkers() {
            showAllMarkers = !showAllMarkers;
            markers.forEach(function(marker, i) {
                if (showAllMarkers) {
                    marker.setMap(map);
                    infoWindows[i].open(map, marker);
                } else {
                    marker.setMap(null);
                    infoWindows[i].close();
                }
            });
        }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap" async defer></script>
</body>
</html>