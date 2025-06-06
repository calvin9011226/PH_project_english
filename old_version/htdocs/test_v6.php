<!-- 讓使用者整趟旅程下來的距離可以最短,by GA ,還沒測試過-->
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
        <button onclick="toggleAllMarkers()">顯示/隱藏所有景點</button>
        <button onclick="showNextRoute()">顯示下一段路線</button>
        <button onclick="calculateOptimizedRoute()">優化路線</button>
    </div>
    <div id="map"></div>

    <script>
        var map;
        var markers = [];
        var infoWindows = [];
        var showAllMarkers = true;
        var userMarker;
        var directionsService;
        var directionsRenderer;
        var JS_number = <?php echo json_encode($number); ?>;
        var JS_place = <?php echo json_encode($place); ?>;
        var JS_latitude = <?php echo json_encode($latitude); ?>;
        var JS_longitude = <?php echo json_encode($longitude); ?>;
        var userLat = <?php echo $userLat ? $userLat : 'null'; ?>;
        var userLng = <?php echo $userLng ? $userLng : 'null'; ?>;
        var currentRouteIndex = -1;
        var optimizedRoute = [];

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

            calculateOptimizedRoute();
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
                closeAllInfoWindows();
                infoWindows[i].open(map, marker);
            });
        }

        function calculateOptimizedRoute() {
            var points = markers.map(marker => marker.getPosition());
            if (userMarker) {
                points.unshift(userMarker.getPosition());
            }
            
            // 遺傳算法參數
            const populationSize = 50;
            const generations = 100;
            const mutationRate = 0.01;
            
            // 初始化種群
            let population = [];
            for (let i = 0; i < populationSize; i++) {
                population.push(shuffle(Array.from({length: points.length}, (_, i) => i)));
            }
            
            // 進行遺傳算法迭代
            for (let gen = 0; gen < generations; gen++) {
                // 評估適應度
                let fitnesses = population.map(individual => 1 / routeDistance(individual, points));
                
                // 選擇
                let newPopulation = [];
                for (let i = 0; i < populationSize; i++) {
                    let parent1 = selectParent(population, fitnesses);
                    let parent2 = selectParent(population, fitnesses);
                    
                    // 交叉
                    let child = crossover(parent1, parent2);
                    
                    // 變異
                    if (Math.random() < mutationRate) {
                        mutate(child);
                    }
                    
                    newPopulation.push(child);
                }
                
                population = newPopulation;
            }
            
            // 選擇最佳路線
            let bestRoute = population.reduce((best, current) => 
                routeDistance(current, points) < routeDistance(best, points) ? current : best
            );
            
            optimizedRoute = bestRoute;
            
            // 更新 currentRouteIndex
            currentRouteIndex = -1;
            
            // 顯示優化後的第一段路線
            showNextRoute();
        }

        function routeDistance(route, points) {
            let distance = 0;
            for (let i = 0; i < route.length - 1; i++) {
                distance += google.maps.geometry.spherical.computeDistanceBetween(points[route[i]], points[route[i+1]]);
            }
            return distance;
        }

        function selectParent(population, fitnesses) {
            let totalFitness = fitnesses.reduce((a, b) => a + b, 0);
            let r = Math.random() * totalFitness;
            let sum = 0;
            for (let i = 0; i < population.length; i++) {
                sum += fitnesses[i];
                if (sum > r) {
                    return population[i];
                }
            }
            return population[population.length - 1];
        }

        function crossover(parent1, parent2) {
            let crossPoint = Math.floor(Math.random() * parent1.length);
            let child = parent1.slice(0, crossPoint);
            for (let i = 0; i < parent2.length; i++) {
                if (!child.includes(parent2[i])) {
                    child.push(parent2[i]);
                }
            }
            return child;
        }

        function mutate(route) {
            let i = Math.floor(Math.random() * route.length);
            let j = Math.floor(Math.random() * route.length);
            [route[i], route[j]] = [route[j], route[i]];
        }

        function shuffle(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
        }

        function showNextRoute() {
            closeAllInfoWindows();
            currentRouteIndex++;
            if (currentRouteIndex >= optimizedRoute.length - 1) {
                currentRouteIndex = -1;
                directionsRenderer.setDirections({routes: []});
                return;
            }

            var start = optimizedRoute[currentRouteIndex];
            var end = optimizedRoute[currentRouteIndex + 1];
            var startPoint = start === 0 && userMarker ? userMarker.getPosition() : markers[start - 1].getPosition();
            var endPoint = end === 0 ? userMarker.getPosition() : markers[end - 1].getPosition();

            directionsService.route({
                origin: startPoint,
                destination: endPoint,
                travelMode: google.maps.TravelMode.DRIVING
            }, function(response, status) {
                if (status === google.maps.DirectionsStatus.OK) {
                    directionsRenderer.setDirections(response);
                    var route = response.routes[0];
                    var leg = route.legs[0];
                    var distanceInKm = (leg.distance.value / 1000).toFixed(2);
                    var content = "";

                    if (start === 0 && userMarker) {
                        content = "從您的位置到" + JS_place[end - 1] + ": 距離: " + distanceInKm + " km";
                    } else if (end === 0 && userMarker) {
                        content = "從" + JS_place[start - 1] + "回到您的位置: 距離: " + distanceInKm + " km";
                    } else {
                        content = "從" + JS_place[start - 1] + "到" + JS_place[end - 1] + ": 距離: " + distanceInKm + " km";
                    }

                    var infoWindow = end === 0 ? infoWindows[start - 1] : infoWindows[end - 1];
                    var originalContent = infoWindow.getContent().split('<br>')[0];
                    infoWindow.setContent(originalContent + "<br>" + content);
                    infoWindow.open(map, end === 0 ? markers[start - 1] : markers[end - 1]);

                    map.panTo(endPoint);
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

        function getRandomDuration(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        function closeAllInfoWindows() {
            for (var i = 0; i < infoWindows.length; i++) {
                infoWindows[i].close();
            }
        }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls&callback=initMap&libraries=geometry" async defer></script>
</body>
</html>