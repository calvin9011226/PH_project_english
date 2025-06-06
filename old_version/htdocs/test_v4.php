<!-- 將距離計算的方式:從使用者位置到每個景點改成:從使用者位置到第一個景點,再從第一個景點到第二個景點,以此類推 -->
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
            font-family: Arial, sans-serif;
        }
        #map {
            height: 85%;
            width: 100%;
        }
        h1 {
            text-align: center;
            margin: 10px 0;
            color: #333;
        }
        #controls {
            text-align: center;
            margin-bottom: 10px;
        }
        button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>澎湖景點規劃</h1>
    <div id="controls">
        <button onclick="toggleAllMarkersAndInfo()">顯示/隱藏所有景點</button>
    </div>
    <div id="map"></div>

    <script>
        var map;
        var markers = [];
        var infoWindows = [];
        var showAll = true;
        var userMarker;
        var directionsService;
        var directionsRenderer;
        var JS_number = <?php echo json_encode($number); ?>;
        var JS_place = <?php echo json_encode($place); ?>;
        var JS_latitude = <?php echo json_encode($latitude); ?>;
        var JS_longitude = <?php echo json_encode($longitude); ?>;
        var userLat = <?php echo $userLat ? $userLat : 'null'; ?>;
        var userLng = <?php echo $userLng ? $userLng : 'null'; ?>;

        function initMap() {
            directionsService = new google.maps.DirectionsService();
            directionsRenderer = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                preserveViewport: true
            });

            var center = userLat && userLng ? {lat: userLat, lng: userLng} : {lat: 23.57226, lng: 119.57102};
            map = new google.maps.Map(document.getElementById('map'), {
                center: center,
                zoom: 15,
                mapId: "5cb7f499bf3d65",
            });

            directionsRenderer.setMap(map);

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
                createMarker(i);
            }

            calculateAndDisplayRoute();
        }

        function createMarker(i) {
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

            marker.addListener('click', function() {
                infoWindows[i].open(map, marker);
            });
        }

        function calculateAndDisplayRoute() {
            var waypoints = markers.map(function(marker) {
                return {
                    location: marker.getPosition(),
                    stopover: true
                };
            });

            var origin = userMarker ? userMarker.getPosition() : markers[0].getPosition();
            var destination = markers[markers.length - 1].getPosition();

            directionsService.route({
                origin: origin,
                destination: destination,
                waypoints: waypoints,
                optimizeWaypoints: false,
                travelMode: google.maps.TravelMode.DRIVING
            }, function(response, status) {
                if (status === google.maps.DirectionsStatus.OK) {
                    directionsRenderer.setDirections(response);
                    var route = response.routes[0];

                    var totalDistance = 0;
                    for (var i = 0; i < route.legs.length; i++) {
                        var leg = route.legs[i];
                        totalDistance += leg.distance.value;

                        var distanceInKm = (leg.distance.value / 1000).toFixed(2);
                        var content = "距離: " + distanceInKm + " km<br>";

                        if (i === 0 && userMarker) {
                            content = "從您的位置到" + JS_place[0] + ": " + content;
                        } else if (i > 0) {
                            content = "從" + JS_place[i-1] + "到" + JS_place[i] + ": " + content;
                        }

                        infoWindows[i].setContent(infoWindows[i].getContent() + "<br>" + content);

                        if (showAll) {
                            infoWindows[i].open(map, markers[i]);
                        }
                    }

                    var totalDistanceInKm = (totalDistance / 1000).toFixed(2);
                    alert("總行程距離: " + totalDistanceInKm + " km");
                }
            });
        }

        function toggleAllMarkersAndInfo() {
            showAll = !showAll;
            markers.forEach(function(marker, i) {
                if (showAll) {
                    marker.setMap(map);
                    infoWindows[i].open(map, marker);
                } else {
                    marker.setMap(null);
                    infoWindows[i].close();
                }
            });
        }

        function getRandomDuration(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap" async defer></script>
</body>
</html>