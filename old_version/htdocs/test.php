<!-- 製作一個網頁來顯示推薦給使用者的地點 -->
<?php
// route_finder.php

// 確保設置了您的Google Maps API密鑰
$api_key = 'AIzaSyAlrONk6sDRUMmEkkjAsYxfuPvMVz7wSls';

// 獲取用戶輸入
$destination = isset($_GET['destination']) ? $_GET['destination'] : '';
$current_address = isset($_GET['current_address']) ? $_GET['current_address'] : '';

$route_data = null;
$error_message = '';

function geocode($address) {
    global $api_key;
    $url = "https://maps.googleapis.com/maps/api/geocode/json?address=" . urlencode($address) . "&key={$api_key}&language=zh-TW";
    $response = file_get_contents($url);
    $data = json_decode($response, true);
    if ($data['status'] == 'OK') {
        return $data['results'][0]['geometry']['location'];
    }
    return null;
}

function clean_html_instructions($instruction) {
    $instruction = preg_replace('/<br\s*\/?>/i', "\n", $instruction);
    $instruction = strip_tags($instruction);
    $instruction = html_entity_decode($instruction, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    return $instruction;
}

if ($destination && $current_address) {
    $origin_location = geocode($current_address);
    $dest_location = geocode($destination);

    if ($origin_location && $dest_location) {
        $url = "https://maps.googleapis.com/maps/api/directions/json?origin={$origin_location['lat']},{$origin_location['lng']}&destination={$dest_location['lat']},{$dest_location['lng']}&key={$api_key}&language=zh-TW";

        $response = file_get_contents($url);
        $data = json_decode($response, true);

        if ($data['status'] == 'OK') {
            $route_data = $data['routes'][0]['legs'][0];
            foreach ($route_data['steps'] as &$step) {
                $step['html_instructions'] = clean_html_instructions($step['html_instructions']);
            }
        } else {
            $error_message = "無法獲取路線信息。請確保您輸入了有效的地址。";
        }
    } else {
        $error_message = "無法解析一個或兩個地址。請確保您輸入了有效的地址。";
    }
}
?>

<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澎湖景點推薦</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=<?php echo $api_key; ?>&callback=initMap&language=zh-TW" async defer></script>
    <style>
        #map { height: 400px; width: 100%; margin-bottom: 20px; }
        .step { margin-bottom: 10px; }
        .google-maps-button {
            background-color: #4285F4;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-bottom: 20px;
        }
        .google-maps-button:hover {
            background-color: #3367D6;
        }
    </style>
</head>
<body>
    <h1>澎湖景點推薦</h1>
    
    <form>
        您的當前地址：<input type="text" name="current_address" value="<?php echo htmlspecialchars($current_address); ?>" required><br>
        目的地地址：<input type="text" name="destination" value="<?php echo htmlspecialchars($destination); ?>" required><br>
        <input type="submit" value="獲取路線">
    </form>

    <?php if ($error_message): ?>
        <p style="color: red;"><?php echo $error_message; ?></p>
    <?php endif; ?>

    <?php if ($route_data): ?>
        <h2>從 <?php echo htmlspecialchars($current_address); ?> 到 <?php echo htmlspecialchars($destination); ?> 的路線：</h2>
        <p>總距離：<?php echo $route_data['distance']['text']; ?></p>
        <p>預計行程時間：<?php echo $route_data['duration']['text']; ?></p>

        <div id="map"></div>

        <button class="google-maps-button" onclick="openGoogleMaps()">在 Google 地圖中打開</button>

        <h3>詳細步驟：</h3>
        <ol>
            <?php foreach ($route_data['steps'] as $step): ?>
                <li class="step">
                    <?php echo nl2br(htmlspecialchars($step['html_instructions'])); ?><br>
                    距離：<?php echo $step['distance']['text']; ?> | 
                    預計時間：<?php echo $step['duration']['text']; ?>
                </li>
            <?php endforeach; ?>
        </ol>

        <script>
            function initMap() {
                var directionsService = new google.maps.DirectionsService();
                var directionsRenderer = new google.maps.DirectionsRenderer();
                var map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 7,
                    center: {lat: <?php echo $origin_location['lat']; ?>, lng: <?php echo $origin_location['lng']; ?>}
                });
                directionsRenderer.setMap(map);

                var request = {
                    origin: '<?php echo addslashes($current_address); ?>',
                    destination: '<?php echo addslashes($destination); ?>',
                    travelMode: 'DRIVING'
                };
                directionsService.route(request, function(result, status) {
                    if (status === 'OK') {
                        directionsRenderer.setDirections(result);
                    }
                });
            }

            function openGoogleMaps() {
                var origin = encodeURIComponent('<?php echo addslashes($current_address); ?>');
                var destination = encodeURIComponent('<?php echo addslashes($destination); ?>');
                var url = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}&travelmode=driving`;
                window.open(url, '_blank');
            }
        </script>
    <?php endif; ?>
</body>
</html>