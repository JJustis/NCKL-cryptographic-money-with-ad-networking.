<?php
// update_clicks.php - Enhanced click updates with real-time features
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

require_once __DIR__ . '/security.php';
$config = include __DIR__ . '/config.php';
$input = sec_unwrap_input(json_decode(file_get_contents('php://input'), true), $config);
$username = $input['username'] ?? '';
$adId = $input['ad_id'] ?? '';
$zone = $input['zone'] ?? 'unknown';
$embedId = $input['embed_id'] ?? '';
$timestamp = date('c'); // server time only; never trust the caller's clock

if (empty($username) || empty($adId)) {
    echo json_encode(['success' => false, 'message' => 'Missing required data']);
    exit;
}

require_once __DIR__ . '/security.php';
// username becomes a directory name, so it must be a plain identifier (blocks ../ traversal)
if (!sec_safe_id((string)$username) || !sec_safe_id((string)$adId, 100)
    || ($embedId !== '' && !sec_safe_id((string)$embedId, 100))) {
    sec_fail(400, 'Invalid data');
}
$zone = mb_substr(strip_tags((string)$zone), 0, 50);
if (!sec_rate_limit('update_clicks', 120, 60)) sec_fail(429, 'Too many requests');

// Ensure user directory exists
$userDir = "users/$username";
if (!file_exists($userDir)) {
    mkdir($userDir, 0755, true);
}

$clicksFile = "$userDir/clicks.xml";

// Load or create XML
if (file_exists($clicksFile)) {
    $xml = simplexml_load_file($clicksFile);
} else {
    $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><clicks></clicks>');
    $xml->addChild('user', htmlspecialchars($username));
    $xml->addChild('total', '0');
    $xml->addChild('created', date('c'));
    $xml->addChild('records');
}

// Add enhanced click record
$record = $xml->records->addChild('click');
$record->addChild('ad_id', htmlspecialchars($adId));
$record->addChild('zone', htmlspecialchars($zone));
$record->addChild('embed_id', htmlspecialchars($embedId));
$record->addChild('timestamp', $timestamp);
$record->addChild('date', date('Y-m-d', strtotime($timestamp)));
$record->addChild('hour', date('H', strtotime($timestamp)));
$record->addChild('ip', $_SERVER['REMOTE_ADDR'] ?? 'unknown');
$record->addChild('user_agent', htmlspecialchars($_SERVER['HTTP_USER_AGENT'] ?? 'unknown'));
$record->addChild('referer', htmlspecialchars($_SERVER['HTTP_REFERER'] ?? 'direct'));

// Add geolocation data if available
if (isset($_SERVER['HTTP_CF_IPCOUNTRY'])) {
    $record->addChild('country', htmlspecialchars($_SERVER['HTTP_CF_IPCOUNTRY']));
}

// Update total
$xml->total = (int)$xml->total + 1;

// Save XML with formatting
$dom = new DOMDocument('1.0', 'UTF-8');
$dom->formatOutput = true;
$dom->loadXML($xml->asXML());
$success = $dom->save($clicksFile);

// Update embed-specific stats
updateEmbedStats($username, $embedId, 'click');

// Send real-time notification (if WebSocket server is available)
sendRealTimeUpdate($username, [
    'type' => 'click',
    'ad_id' => $adId,
    'zone' => $zone,
    'timestamp' => $timestamp
]);

if ($success) {
    echo json_encode([
        'success' => true, 
        'total_clicks' => (int)$xml->total,
        'timestamp' => $timestamp
    ]);
} else {
    echo json_encode(['success' => false, 'message' => 'Failed to update clicks file']);
}

function updateEmbedStats($username, $embedId, $type) {
    if (empty($embedId)) return;
    
    $embedsFile = "users/$username/embeds.json";
    
    if (file_exists($embedsFile)) {
        $embeds = json_decode(file_get_contents($embedsFile), true);
        
        // Find and update the specific embed
        foreach ($embeds['embeds'] as &$embed) {
            if ($embed['embed_id'] === $embedId) {
                $embed[$type . 's']++;
                $embed['last_activity'] = date('c');
                break;
            }
        }
        
        file_put_contents($embedsFile, json_encode($embeds, JSON_PRETTY_PRINT));
    }
}

function sendRealTimeUpdate($username, $data) {
    // Store update for real-time retrieval
    $updatesFile = "users/$username/real_time_updates.json";
    
    $updates = [];
    if (file_exists($updatesFile)) {
        $updates = json_decode(file_get_contents($updatesFile), true) ?: [];
    }
    
    $updates[] = [
        'timestamp' => time(),
        'data' => $data
    ];
    
    // Keep only last 50 updates
    $updates = array_slice($updates, -50);
    
    file_put_contents($updatesFile, json_encode($updates, JSON_PRETTY_PRINT));
}
?>