<?php
// Enhanced API with Real-Time Client Registration
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$config = include 'config.php';
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/click_recorder.php';
$host = $config['database']['host'];
$dbname = $config['database']['dbname'];
$username = $config['database']['username'];
$password = $config['database']['password'];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    error_log("Database connection failed: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed']);
    exit;
}

// Parse input
$input = sec_unwrap_input(json_decode(file_get_contents('php://input'), true), $config);
$action = $input['action'] ?? ($_GET['action'] ?? '');

// Route requests
switch($action) {
    case 'public_key':
        echo json_encode(['success' => true, 'v' => 1, 'alg' => 'ECDH-P256+HKDF-SHA256+AES-256-GCM', 'public_key' => sec_public_key_b64()]);
        break;
    case 'client_register_live':
        clientRegisterLive($pdo, $input);
        break;
    case 'client_update_status':
        clientUpdateStatus($pdo, $input);
        break;
    case 'client_shutdown':
        clientShutdown($pdo, $input);
        break;
    case 'get_live_clients':
        getLiveClients($pdo);
        break;
    case 'client_heartbeat':
        clientHeartbeat($pdo, $input);
        break;
    case 'update_client_ads':
        updateClientAds($pdo, $input);
        break;
    case 'record_click':
        recordClick($pdo, $input);
        break;
    case 'get_advertisers':
        getAdvertisers($pdo);
        break;
    case 'record_impression': // ADDED
        recordImpression($pdo, $input); // ADDED
        break; // ADDED
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid action']);
}

function clientRegisterLive($pdo, $data) {
    $clientId = $data['client_id'] ?? '';
    $username = $data['username'] ?? '';
    $walletAddress = $data['wallet_address'] ?? '';
    $clientName = $data['client_name'] ?? '';
    $host = $data['host'] ?? $_SERVER['REMOTE_ADDR'];
    $port = $data['port'] ?? 8332;
    $version = $data['version'] ?? '1.0';
    $capabilities = $data['capabilities'] ?? [];
    $adInventory = $data['ad_inventory'] ?? [];
    $metadata = $data['metadata'] ?? [];
    
    if (empty($clientId) || empty($username) || empty($walletAddress)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Missing required fields']);
        return;
    }
    if (!sec_rate_limit('register', 30, 60)) sec_fail(429, 'Too many requests');
    if (!sec_safe_id($clientId, 100) || !sec_safe_id($username) || !sec_safe_id($walletAddress, 100)
        || !sec_valid_host($host) || !sec_valid_port($port)
        || !is_array($adInventory) || count($adInventory) > 100) {
        sec_fail(400, 'Invalid registration data');
    }
    $clientName = mb_substr(strip_tags((string)$clientName), 0, 100);
    
    try {
        $pdo->beginTransaction();
        
        // Register/update client
        $stmt = $pdo->prepare("
            INSERT INTO p2p_clients 
            (client_id, name, host, port, username, wallet_address, status, version, 
             capabilities, metadata, ad_count, last_seen, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, 'online', ?, ?, ?, ?, NOW(), NOW())
            ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            host = VALUES(host),
            port = VALUES(port),
            wallet_address = VALUES(wallet_address),
            status = 'online',
            version = VALUES(version),
            capabilities = VALUES(capabilities),
            metadata = VALUES(metadata),
            ad_count = VALUES(ad_count),
            last_seen = NOW()
        ");
        
        $stmt->execute([
            $clientId, $clientName, $host, $port, $username, $walletAddress,
            $version, json_encode($capabilities), json_encode($metadata), count($adInventory)
        ]);
        
        // Update client ads inventory
        if (!empty($adInventory)) {
            // Clear existing ads for this client
            $stmt = $pdo->prepare("DELETE FROM client_ads WHERE client_id = ?");
            $stmt->execute([$clientId]);
            
            // Insert new ads
            $stmt = $pdo->prepare("
                INSERT INTO client_ads (client_id, ad_id, title, description, category, 
                                      payout_rate, click_url, image_url, targeting_tags, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ");
            
            foreach ($adInventory as $ad) {
                if (!is_array($ad) || !sec_safe_id($ad['ad_id'] ?? '', 100)
                    || !sec_valid_url($ad['click_url'] ?? '')
                    || (($ad['image_url'] ?? '') !== '' && !sec_valid_url($ad['image_url']))) {
                    throw new PDOException('Invalid ad in inventory');
                }
                $ad['payout_rate'] = min(max((float)($ad['payout_rate'] ?? 0.002), 0), 0.01);
                $stmt->execute([
                    $clientId, $ad['ad_id'], $ad['title'], $ad['description'],
                    $ad['category'], $ad['payout_rate'], $ad['click_url'],
                    $ad['image_url'] ?? '', json_encode($ad['targeting_tags'] ?? []),
                    $ad['active'] ?? true
                ]);
            }
        }
        
        // Log registration event
        $stmt = $pdo->prepare("
            INSERT INTO analytics (username, event_type, client_id, data, created_at)
            VALUES (?, 'client_registered', ?, ?, NOW())
        ");
        $stmt->execute([$username, $clientId, json_encode($data)]);
        
        $pdo->commit();
        
        echo json_encode([
            'success' => true,
            'message' => 'Client registered successfully',
            'client_id' => $clientId,
            'registered_at' => date('c')
        ]);
        
    } catch(PDOException $e) {
        $pdo->rollBack();
        error_log("Client registration failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Registration failed']);
    }
}

function getLiveClients($pdo) {
    try {
        $stmt = $pdo->prepare("
            SELECT c.*, 
                   COUNT(ca.id) as actual_ad_count,
                   TIMESTAMPDIFF(SECOND, c.last_seen, NOW()) as seconds_since_seen
            FROM p2p_clients c
            LEFT JOIN client_ads ca ON c.client_id = ca.client_id AND ca.active = 1
            WHERE c.status = 'online' 
            AND c.last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            GROUP BY c.client_id
            ORDER BY c.last_seen DESC
        ");
        $stmt->execute();
        $clients = $stmt->fetchAll();
        
        // Enrich with real-time data
        foreach ($clients as &$client) {
            $client['uptime'] = formatUptime($client['seconds_since_seen']);
            $client['capabilities'] = json_decode($client['capabilities'] ?? '[]', true);
            $client['stats'] = json_decode($client['stats'] ?? '{}', true);
            $client['metadata'] = json_decode($client['metadata'] ?? '{}', true);
        }
        
        echo json_encode([
            'success' => true,
            'clients' => $clients,
            'total_count' => count($clients),
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        error_log("Get live clients failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to get clients']);
    }
}

function clientHeartbeat($pdo, $data) {
    $clientId = $data['client_id'] ?? ($_GET['client_id'] ?? '');
    
    if (empty($clientId) || !sec_safe_id($clientId, 100)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Client ID required']);
        return;
    }
    
    try {
        $stmt = $pdo->prepare("
            UPDATE p2p_clients 
            SET last_seen = NOW(), status = 'online'
            WHERE client_id = ?
        ");
        $stmt->execute([$clientId]);
        
        if ($stmt->rowCount() > 0) {
            echo json_encode([
                'success' => true,
                'heartbeat_received' => true,
                'server_time' => date('c')
            ]);
        } else {
            http_response_code(404);
            echo json_encode(['success' => false, 'message' => 'Client not found']);
        }
        
    } catch(PDOException $e) {
        error_log("Heartbeat failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Heartbeat failed']);
    }
}

function recordClick($pdo, $data) {
    // Same recorder the dashboard uses: the click lands in ad_clicks with everything the Qt payment step reads.
    // The payout comes from the ad's own record on the server, never from the request.
    $res = clk_record_click($pdo, [
        'ad_id' => $data['ad_id'] ?? '',
        'client_id' => $data['client_id'] ?? '',
        'zone' => $data['zone'] ?? '',
        'embed_id' => $data['embed_id'] ?? '', 'load_id' => $data['load_id'] ?? '',
        'developer_address' => $data['developer_address'] ?? '',
        'developer_username' => $data['username'] ?? ($data['developer'] ?? ''),
    ]);
    if (!$res['ok']) {
        $code = ($res['error'] === 'Too many clicks') ? 429 : 400;
        sec_fail($code, $res['error']);
    }
    echo json_encode([
        'success' => true,
        'click_id' => $res['id'],
        'pyc_earned' => $res['amount'],
        'payment_queued' => true,
        'timestamp' => date('c')
    ]);
}

function getAdvertisers($pdo) {
    try {
        $stmt = $pdo->prepare("
            SELECT c.*, 
                   COUNT(ca.id) as ad_count,
                   TIMESTAMPDIFF(SECOND, c.last_seen, NOW()) as seconds_since_seen
            FROM p2p_clients c
            LEFT JOIN client_ads ca ON c.client_id = ca.client_id AND ca.active = 1
            WHERE c.status = 'online' 
            AND c.last_seen > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
            GROUP BY c.client_id
            ORDER BY c.last_seen DESC
        ");
        $stmt->execute();
        $clients = $stmt->fetchAll();
        
        $advertisers = [];
        foreach ($clients as $client) {
            $advertisers[] = [
                'client_id' => $client['client_id'],
                'name' => $client['name'],
                'status' => 'online',
                'ad_count' => (int)$client['ad_count'],
                'category' => $client['category'],
                'host' => $client['host'],
                'port' => (int)$client['port'],
                'last_seen' => $client['last_seen'],
                'uptime' => formatUptime($client['seconds_since_seen']),
                'wallet_address' => $client['wallet_address']
            ];
        }
        
        echo json_encode([
            'success' => true,
            'advertisers' => $advertisers,
            'total_count' => count($advertisers),
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        error_log("Get advertisers failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to get advertisers']);
    }
}

function recordImpression($pdo, $data) {
    // Views are kept in ad_impressions and never mixed into ad_clicks.
    $ok = clk_record_impression($pdo, [
        'ad_id' => $data['ad_id'] ?? '',
        'client_id' => $data['client_id'] ?? '',
        'zone' => $data['zone'] ?? '',
        'embed_id' => $data['embed_id'] ?? '',
        'developer_address' => $data['developer_address'] ?? '',
    ]);
    if (!$ok) {
        sec_fail(400, 'Impression not recorded');
    }
    echo json_encode(['success' => true, 'message' => 'Impression recorded successfully', 'timestamp' => date('c')]);
}

function formatUptime($seconds) {
    if ($seconds < 60) return $seconds . 's';
    if ($seconds < 3600) return floor($seconds / 60) . 'm';
    if ($seconds < 86400) return floor($seconds / 3600) . 'h';
    return floor($seconds / 86400) . 'd';
}

// Add client_ads table if it doesn't exist
try {
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS client_ads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(100) NOT NULL,
            ad_id VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'general',
            payout_rate DECIMAL(10,8) DEFAULT 0.00200000,
            click_url VARCHAR(500),
            image_url VARCHAR(500),
            targeting_tags JSON,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_client_id (client_id),
            INDEX idx_ad_id (ad_id),
            INDEX idx_active (active)
        ) ENGINE=InnoDB
    ");
} catch(PDOException $e) {
    error_log("Table creation failed: " . $e->getMessage());
}
?>