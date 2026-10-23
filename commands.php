<?php
// commands.php - Real P2P Ad Network API endpoints
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

// Database configuration
$config = include 'config.php';
require_once __DIR__ . '/dbconfig.php';
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/curl_polyfill.php';
$host = $config['database']['host'];
$dbname = $config['database']['dbname'];
$username = $config['database']['username'];
$password = $config['database']['password'];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed']);
    exit;
}

// Parse input
$input = sec_unwrap_input(json_decode(file_get_contents('php://input'), true), $config);
$action = $input['action'] ?? ($_GET['action'] ?? '');

// Route to appropriate handler
switch($action) {
    case 'register_online':
        registerClientOnline($pdo, $input);
        break;
    case 'get_live_peers':
        getLivePeers($pdo);
        break;
    case 'scan_network':
        scanNetworkForClients($pdo);
        break;
    case 'get_live_ads':
        getLiveAds($pdo, $input);
        break;
    case 'record_event':
        recordEvent($pdo, $input);
        break;
    case 'heartbeat':
        handleHeartbeat($pdo, $input);
        break;
    case 'upload_js':
        uploadCustomJS($pdo, $input);
        break;
    case 'test_connection':
        testConnection();
        break;
    case 'connect_to_client':
        connectToClient($pdo, $input);
        break;
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid action: ' . $action]);
}

function registerClientOnline($pdo, $data) {
    $clientId = $data['client_id'] ?? '';
    $username = $data['username'] ?? '';
    $host = $data['host'] ?? $_SERVER['REMOTE_ADDR'];
    $port = $data['port'] ?? 8332;
    $capabilities = $data['capabilities'] ?? [];
    
    if (empty($clientId) || empty($username)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Client ID and username required']);
        return;
    }
    if (!sec_rate_limit('register_online', 30, 60)) sec_fail(429, 'Too many requests');
    if (!sec_safe_id($clientId, 100) || !sec_safe_id($username) || !sec_valid_host($host) || !sec_valid_port($port)) {
        sec_fail(400, 'Invalid registration data');
    }
    
    try {
        // Check if user exists
        $stmt = $pdo->prepare("SELECT id, username, exp FROM ad_members WHERE username = ?");
        $stmt->execute([$username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$user) {
            http_response_code(404);
            echo json_encode(['success' => false, 'message' => 'User not found']);
            return;
        }
        
        // Register or update client
        $stmt = $pdo->prepare("
            INSERT INTO p2p_clients (client_id, name, host, port, status, category, last_seen, username) 
            VALUES (?, ?, ?, ?, 'online', 'developer', NOW(), ?) 
            ON DUPLICATE KEY UPDATE 
            status = 'online', 
            last_seen = NOW(),
            host = VALUES(host),
            port = VALUES(port)
        ");
        
        $clientName = $username . ' P2P Client';
        $stmt->execute([$clientId, $clientName, $host, $port, $username]);
        
        echo json_encode([
            'success' => true,
            'message' => 'Client registered successfully',
            'client_id' => $clientId,
            'server_endpoints' => [
                'main_api' => pyc_site()['base_url'] . '/api.php',
                'commands' => pyc_site()['base_url'] . '/commands.php',
                'update_clicks' => pyc_site()['base_url'] . '/update_clicks.php'
            ]
        ]);
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Registration failed: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Registration failed']);
    }
}

function scanNetworkForClients($pdo) {
    // Scanning is expensive (and probes other hosts), so allow it rarely
    if (!sec_rate_limit('scan_network', 2, 60)) sec_fail(429, 'Scan rate limit reached, try again shortly');
    $discoveredClients = [];
    $commonPorts = [8332, 8080, 8083, 8084];
    $localNetworks = ['192.168.1.', '192.168.0.', '10.0.0.', '172.16.0.'];
    
    // Scan database for recently active clients
    try {
        $stmt = $pdo->prepare("
            SELECT client_id, name, host, port, status, category, last_seen, username
            FROM p2p_clients 
            WHERE last_seen > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
            ORDER BY last_seen DESC
        ");
        $stmt->execute();
        $dbClients = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Verify each client is still active
        foreach ($dbClients as $client) {
            if (pingClient($client['host'], $client['port'])) {
                $clientInfo = getClientInfo($client['host'], $client['port']);
                if ($clientInfo) {
                    $client['ad_count'] = $clientInfo['ad_count'] ?? 0;
                    $client['peers'] = $clientInfo['peers'] ?? 0;
                    $client['uptime'] = $clientInfo['uptime'] ?? '0h';
                    $client['bandwidth'] = $clientInfo['bandwidth'] ?? 0;
                    $discoveredClients[] = $client;
                    
                    // Update last seen
                    $updateStmt = $pdo->prepare("UPDATE p2p_clients SET last_seen = NOW() WHERE client_id = ?");
                    $updateStmt->execute([$client['client_id']]);
                } else {
                    // Mark as offline
                    $updateStmt = $pdo->prepare("UPDATE p2p_clients SET status = 'offline' WHERE client_id = ?");
                    $updateStmt->execute([$client['client_id']]);
                }
            }
        }
        
        // Quick scan for new clients on common networks
        foreach ($localNetworks as $network) {
            for ($i = 100; $i <= 110; $i++) {
                $host = $network . $i;
                foreach ($commonPorts as $port) {
                    if (pingClient($host, $port)) {
                        $clientInfo = getClientInfo($host, $port);
                        if ($clientInfo && !clientExists($pdo, $host, $port)) {
                            $newClient = [
                                'client_id' => 'discovered_' . md5($host . $port . time()),
                                'name' => $clientInfo['name'] ?? 'P2P Client ' . $host,
                                'host' => $host,
                                'port' => $port,
                                'status' => 'online',
                                'category' => $clientInfo['category'] ?? 'general',
                                'ad_count' => $clientInfo['ad_count'] ?? 0,
                                'peers' => $clientInfo['peers'] ?? 0,
                                'uptime' => $clientInfo['uptime'] ?? '0h',
                                'bandwidth' => $clientInfo['bandwidth'] ?? 0,
                                'last_seen' => date('Y-m-d H:i:s'),
                                'username' => 'discovered'
                            ];
                            
                            // Add to database
                            $stmt = $pdo->prepare("
                                INSERT INTO p2p_clients (client_id, name, host, port, status, category, last_seen, username) 
                                VALUES (?, ?, ?, ?, ?, ?, NOW(), ?)
                            ");
                            $stmt->execute([
                                $newClient['client_id'],
                                $newClient['name'],
                                $newClient['host'],
                                $newClient['port'],
                                $newClient['status'],
                                $newClient['category'],
                                $newClient['username']
                            ]);
                            
                            $discoveredClients[] = $newClient;
                        }
                        break; // Found client on this host, move to next host
                    }
                }
            }
        }
        
        echo json_encode([
            'success' => true,
            'clients' => $discoveredClients,
            'total_count' => count($discoveredClients),
            'scan_time' => date('c')
        ]);
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Scan failed: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Scan failed']);
    }
}

function getLivePeers($pdo) {
    try {
        // Get active clients from database and verify they're still online
        $stmt = $pdo->prepare("
            SELECT client_id, name, host, port, status, category, last_seen, username
            FROM p2p_clients 
            WHERE status = 'online' AND last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            ORDER BY last_seen DESC
        ");
        $stmt->execute();
        $peers = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Enrich with real-time data
        foreach ($peers as &$peer) {
            $clientInfo = getClientInfo($peer['host'], $peer['port']);
            if ($clientInfo) {
                $peer['ad_count'] = $clientInfo['ad_count'] ?? 0;
                $peer['peer_count'] = $clientInfo['peers'] ?? 0;
                $peer['bandwidth'] = $clientInfo['bandwidth'] ?? 0;
                $peer['uptime'] = $clientInfo['uptime'] ?? '0h';
                $peer['version'] = $clientInfo['version'] ?? '1.0';
            } else {
                // Client is offline, update database
                $updateStmt = $pdo->prepare("UPDATE p2p_clients SET status = 'offline' WHERE client_id = ?");
                $updateStmt->execute([$peer['client_id']]);
                $peer['status'] = 'offline';
            }
        }
        
        // Filter out offline clients
        $peers = array_filter($peers, function($peer) {
            return $peer['status'] === 'online';
        });
        
        echo json_encode([
            'success' => true,
            'peers' => array_values($peers),
            'total_count' => count($peers),
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Failed to fetch peers: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Failed to fetch peers']);
    }
}

function getLiveAds($pdo, $data) {
    $filters = $data['filters'] ?? [];
    
    try {
        // Get active clients
        $stmt = $pdo->prepare("
            SELECT client_id, name, host, port, category 
            FROM p2p_clients 
            WHERE status = 'online' AND last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
        ");
        $stmt->execute();
        $activeClients = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        $allAds = [];
        
        // Fetch ads from each active client
        foreach ($activeClients as $client) {
            $clientAds = getAdsFromClient($client['host'], $client['port']);
            if ($clientAds) {
                foreach ($clientAds as $ad) {
                    $ad['peer_source'] = $client['client_id'];
                    $ad['source'] = $client['name'];
                    $ad['category'] = $ad['category'] ?? $client['category'];
                    $allAds[] = $ad;
                }
            }
        }
        
        // Apply filters
        if (!empty($filters['category'])) {
            $allAds = array_filter($allAds, function($ad) use ($filters) {
                return strcasecmp($ad['category'], $filters['category']) === 0;
            });
        }
        
        if (!empty($filters['min_quality'])) {
            $allAds = array_filter($allAds, function($ad) use ($filters) {
                return ($ad['quality_score'] ?? 0) >= $filters['min_quality'];
            });
        }
        
        echo json_encode([
            'success' => true,
            'ads' => array_values($allAds),
            'total_count' => count($allAds),
            'active_clients' => count($activeClients),
            'filters_applied' => $filters,
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Failed to fetch ads: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Failed to fetch ads']);
    }
}

function connectToClient($pdo, $data) {
    $clientId = $data['client_id'] ?? '';
    $username = $data['username'] ?? '';
    
    if (empty($clientId) || empty($username)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Client ID and username required']);
        return;
    }
    
    try {
        // Get client info from database
        $stmt = $pdo->prepare("SELECT * FROM p2p_clients WHERE client_id = ?");
        $stmt->execute([$clientId]);
        $client = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$client) {
            http_response_code(404);
            echo json_encode(['success' => false, 'message' => 'Client not found']);
            return;
        }
        
        // Test connection to client
        if (!pingClient($client['host'], $client['port'])) {
            echo json_encode(['success' => false, 'message' => 'Client is not responding']);
            return;
        }
        
        // Establish handshake with client
        $handshakeResult = performHandshake($client['host'], $client['port'], $username);
        
        if ($handshakeResult) {
            echo json_encode([
                'success' => true,
                'message' => 'Connected to client successfully',
                'client_info' => $client,
                'connection_id' => $handshakeResult['connection_id'] ?? null,
                'available_endpoints' => [
                    'ads' => "http://{$client['host']}:{$client['port']}/ads",
                    'upload' => "http://{$client['host']}:{$client['port']}/upload",
                    'status' => "http://{$client['host']}:{$client['port']}/status"
                ]
            ]);
        } else {
            echo json_encode(['success' => false, 'message' => 'Handshake failed']);
        }
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Connection failed: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Connection failed']);
    }
}

function recordEvent($pdo, $data) {
    $eventType = $data['event_type'] ?? '';
    $username = $data['username'] ?? '';
    $adId = $data['ad_id'] ?? '';
    $embedId = $data['embed_id'] ?? '';
    $metadata = $data['metadata'] ?? [];
    
    if (empty($eventType) || empty($username)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Event type and username required']);
        return;
    }
    if (!sec_safe_id($username) || !sec_safe_id((string)$eventType, 32)
        || ($adId !== '' && !sec_safe_id((string)$adId, 100))
        || ($embedId !== '' && !sec_safe_id((string)$embedId, 100))
        || !is_array($metadata) || strlen(json_encode($metadata)) > 4096) {
        sec_fail(400, 'Invalid event data');
    }
    if (!sec_rate_limit('event', 120, 60)) sec_fail(429, 'Too many requests');
    
    try {
        // Record in analytics table
        $stmt = $pdo->prepare("
            INSERT INTO analytics (username, event_type, ad_id, embed_id, data, created_at) 
            VALUES (?, ?, ?, ?, ?, NOW())
        ");
        $stmt->execute([$username, $eventType, $adId, $embedId, json_encode($metadata)]);
        
        $expAwarded = 0;
        
        // Award EXP based on event type
        if ($eventType === 'click') {
            $expAwarded = 2; // Base reward for clicks
            
            // EXP only once per IP+ad every 30s
            if (!sec_rate_limit('exp_' . $adId, 1, 30)) $expAwarded = 0;
            // Update user EXP
            $stmt = $pdo->prepare("UPDATE ad_members SET exp = exp + ? WHERE username = ?");
            $stmt->execute([$expAwarded, $username]);
            
            // Notify client about the click
            // Only notify peers that are registered with this server (prevents SSRF)
            if (!empty($metadata['client_host']) && !empty($metadata['client_port'])
                && sec_valid_host($metadata['client_host']) && sec_valid_port($metadata['client_port'])
                && clientExists($pdo, $metadata['client_host'], $metadata['client_port'])) {
                notifyClientOfClick($metadata['client_host'], $metadata['client_port'], $data);
            }
        }
        
        echo json_encode([
            'success' => true,
            'exp_awarded' => $expAwarded,
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Failed to record event: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Failed to record event']);
    }
}

function handleHeartbeat($pdo, $input) {
    $clientId = $input['client_id'] ?? ($_GET['client_id'] ?? '');
    $developer = $input['developer'] ?? ($_GET['developer'] ?? '');
    
    if (empty($clientId) && empty($developer)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Client ID or developer required']);
        return;
    }
    
    try {
        if (!empty($clientId)) {
            // Update client heartbeat
            $stmt = $pdo->prepare("UPDATE p2p_clients SET last_seen = NOW() WHERE client_id = ?");
            $stmt->execute([$clientId]);
            
            if ($stmt->rowCount() > 0) {
                echo json_encode([
                    'success' => true,
                    'message' => 'Heartbeat received',
                    'server_time' => date('c')
                ]);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Client not found']);
            }
        } else {
            // Developer heartbeat
            echo json_encode([
                'success' => true,
                'message' => 'Developer heartbeat received',
                'server_time' => date('c'),
                'server_status' => 'online'
            ]);
        }
        
    } catch(PDOException $e) {
        http_response_code(500);
        error_log('commands.php - Heartbeat failed: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'Heartbeat failed']);
    }
}

function uploadCustomJS($pdo, $data) {
    $userId = $data['user_id'] ?? '';
    $embedId = $data['embed_id'] ?? '';
    $jsContent = $data['js_content'] ?? '';
    $username = $data['username'] ?? '';
    
    if (empty($userId) || empty($jsContent)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'User ID and JS content required']);
        return;
    }
    // Must be a logged-in member, and filename parts must be plain identifiers
    if (!sec_rate_limit('upload_js', 10, 60)) sec_fail(429, 'Too many requests');
    $member = sec_check_login($pdo, $username, $data['password'] ?? '');
    if (!$member) sec_fail(401, 'Authentication required');
    $userId = sec_safe_id((string)$userId, 64);
    $embedId = $embedId === '' ? 'none' : sec_safe_id((string)$embedId, 64);
    if (!$userId || !$embedId || !is_string($jsContent) || strlen($jsContent) > 200000) {
        sec_fail(400, 'Invalid upload');
    }
    
    try {
        // Create JS directory if it doesn't exist
        $jsDir = __DIR__ . '/js';
        if (!is_dir($jsDir)) {
            mkdir($jsDir, 0755, true);
        }
        
        // Generate filename
        $filename = "custom_{$userId}_{$embedId}_" . time() . ".js";
        $filePath = $jsDir . '/' . $filename;
        
        // Save JS file
        if (file_put_contents($filePath, $jsContent) !== false) {
            $jsUrl = "https://" . pyc_site()["public_host"] . ":8332/js/{$filename}";
            
            echo json_encode([
                'success' => true,
                'js_url' => $jsUrl,
                'filename' => $filename,
                'file_size' => strlen($jsContent),
                'timestamp' => date('c')
            ]);
        } else {
            throw new Exception('Failed to write JS file');
        }
        
    } catch(Exception $e) {
        http_response_code(500);
        error_log('commands.php - JS upload failed: ' . $e->getMessage());
        echo json_encode(['success' => false, 'message' => 'JS upload failed']);
    }
}

function testConnection() {
    echo json_encode([
        'success' => true,
        'message' => 'Connection successful',
        'server_info' => [
            'version' => '2.1.0',
            'timestamp' => date('c'),
            'php_version' => PHP_VERSION,
            'server' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'
        ],
        'endpoints' => [
            'main_api' => pyc_site()['base_url'] . '/api.php',
            'commands' => pyc_site()['base_url'] . '/commands.php',
            'js_server' => 'http://' . pyc_site()['public_host'] . ':8332',
            'update_clicks' => pyc_site()['base_url'] . '/update_clicks.php'
        ]
    ]);
}

// Helper Functions

function pingClient($host, $port, $timeout = 2) {
    if (!sec_valid_host($host) || !sec_valid_port($port)) return false;
    $connection = @fsockopen($host, $port, $errno, $errstr, $timeout);
    if ($connection) {
        fclose($connection);
        return true;
    }
    return false;
}

function getClientInfo($host, $port) {
    if (!sec_valid_host($host) || !sec_valid_port($port)) return null;
    $url = "http://{$host}:{$port}/status";
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200 && $response) {
        $data = json_decode($response, true);
        return $data;
    }
    
    return null;
}

function getAdsFromClient($host, $port) {
    if (!sec_valid_host($host) || !sec_valid_port($port)) return [];
    $url = "http://{$host}:{$port}/ads";
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200 && $response) {
        $data = json_decode($response, true);
        return $data['ads'] ?? [];
    }
    
    return [];
}

function performHandshake($host, $port, $username) {
    if (!sec_valid_host($host) || !sec_valid_port($port)) return false;
    $url = "http://{$host}:{$port}/handshake";
    $postData = json_encode([
        'action' => 'connect',
        'username' => $username,
        'server' => pyc_site()['public_host'],
        'timestamp' => time()
    ]);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200 && $response) {
        return json_decode($response, true);
    }
    
    return false;
}

function notifyClientOfClick($host, $port, $clickData) {
    if (!sec_valid_host($host) || !sec_valid_port($port)) return;
    $url = "http://{$host}:{$port}/click_notification";
    $postData = json_encode($clickData);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    
    curl_exec($ch);
    curl_close($ch);
}

function clientExists($pdo, $host, $port) {
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM p2p_clients WHERE host = ? AND port = ?");
    $stmt->execute([$host, $port]);
    return $stmt->fetchColumn() > 0;
}

?>