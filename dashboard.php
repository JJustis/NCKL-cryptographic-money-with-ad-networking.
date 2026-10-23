<?php
/**
 * PythonCoin Developer Dashboard (Complete PHP Version)
 * Full-featured developer portal for PythonCoin P2P Ad Network
 * Uses the same 'adnetwrk' database as the Python Qt client
 */

session_start();

// Configuration - Using same database as Python Qt client
define('PYTHONCOIN_SERVER_URL', 'http://127.0.0.1:8082');
define('DASHBOARD_VERSION', '2.1.0');
define('REFRESH_INTERVAL', 30);

// Database configuration - Same as Python Qt client
$db_config = [
    'host' => 'localhost',
    'database' => 'adnetwrk',
    'username' => 'root',
    'password' => ''
];

// Database connection
function getDatabase() {
    global $db_config;
    try {
        $pdo = new PDO(
            "mysql:host={$db_config['host']};dbname={$db_config['database']};charset=utf8mb4",
            $db_config['username'],
            $db_config['password'],
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
            ]
        );
        return $pdo;
    } catch (PDOException $e) {
        return null;
    }
}

// Initialize database tables if they don't exist
function initializeTables() {
    $pdo = getDatabase();
    if (!$pdo) return false;
    
    try {
        // Create developers table if not exists
        $pdo->exec("CREATE TABLE IF NOT EXISTS developers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            pythoncoin_address VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            total_clicks INT DEFAULT 0,
            total_earned DECIMAL(16,8) DEFAULT 0.00000000,
            is_active BOOLEAN DEFAULT TRUE
        )");
        
        // Create developer_sessions table
        $pdo->exec("CREATE TABLE IF NOT EXISTS developer_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            developer_id INT,
            session_token VARCHAR(255),
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            FOREIGN KEY (developer_id) REFERENCES developers(id)
        )");
        
        // Create ad_clicks table
        $pdo->exec("CREATE TABLE IF NOT EXISTS ad_clicks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            developer_id INT,
            ad_id VARCHAR(100),
            client_id VARCHAR(100),
            zone VARCHAR(100),
            payout_amount DECIMAL(16,8),
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            processed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (developer_id) REFERENCES developers(id)
        )");
        
        // Create developer_embeds table
        $pdo->exec("CREATE TABLE IF NOT EXISTS developer_embeds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            developer_id INT,
            embed_name VARCHAR(100),
            zone_id VARCHAR(100),
            width VARCHAR(20),
            height VARCHAR(20),
            rotation_interval INT DEFAULT 30,
            selected_clients JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            total_impressions INT DEFAULT 0,
            total_clicks INT DEFAULT 0,
            FOREIGN KEY (developer_id) REFERENCES developers(id)
        )");
        
        return true;
    } catch (PDOException $e) {
        error_log("Database initialization error: " . $e->getMessage());
        return false;
    }
}

// Initialize tables
initializeTables();

// Helper Functions
class PythonCoinAPI {
    private $serverUrl;
    
    public function __construct($serverUrl = PYTHONCOIN_SERVER_URL) {
        $this->serverUrl = $serverUrl;
    }
    
    public function makeRequest($endpoint, $data = null, $method = 'GET') {
        $url = $this->serverUrl . $endpoint;
        $ch = curl_init();
        
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'User-Agent: PythonCoin-Dashboard/2.1.0'
        ]);
        
        if ($method === 'POST' && $data) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200 && $response) {
            return json_decode($response, true);
        }
        
        return ['success' => false, 'error' => 'Connection failed', 'http_code' => $httpCode];
    }
    
    // All API methods
    public function getClientInfo() { return $this->makeRequest('/client_info'); }
    public function discoverClients() { return $this->makeRequest('/discover_clients'); }
    public function getActiveClients() { return $this->makeRequest('/active_clients'); }
    public function getStats() { return $this->makeRequest('/stats'); }
    public function getNotifications() { return $this->makeRequest('/notifications'); }
    public function getAds() { return $this->makeRequest('/ads'); }
    
    public function selectClient($developerAddress, $clientId, $categories = []) {
        return $this->makeRequest('/select_client', [
            'developer_address' => $developerAddress,
            'client_id' => $clientId,
            'categories' => $categories
        ], 'POST');
    }
    
    public function generateCustomJS($developerAddress, $preferences = []) {
        return $this->makeRequest('/generate_custom_js', [
            'developer_address' => $developerAddress,
            'client_preferences' => $preferences
        ], 'POST');
    }
    
    public function registerDeveloper($developer, $address) {
        return $this->makeRequest('/register_developer', [
            'developer' => $developer,
            'pythoncoin_address' => $address
        ], 'POST');
    }
}

// Database functions
function getDeveloperByUsername($username) {
    $pdo = getDatabase();
    if (!$pdo) return null;
    
    $stmt = $pdo->prepare("SELECT * FROM developers WHERE username = ?");
    $stmt->execute([$username]);
    return $stmt->fetch();
}

function createDeveloper($username, $password, $pythoncoinAddress, $email = null) {
    $pdo = getDatabase();
    if (!$pdo) return false;
    
    $passwordHash = password_hash($password, PASSWORD_DEFAULT);
    
    try {
        $stmt = $pdo->prepare("INSERT INTO developers (username, password_hash, pythoncoin_address, email) VALUES (?, ?, ?, ?)");
        return $stmt->execute([$username, $passwordHash, $pythoncoinAddress, $email]);
    } catch (PDOException $e) {
        return false;
    }
}

function updateDeveloperLogin($developerId) {
    $pdo = getDatabase();
    if (!$pdo) return false;
    
    $stmt = $pdo->prepare("UPDATE developers SET last_login = CURRENT_TIMESTAMP WHERE id = ?");
    return $stmt->execute([$developerId]);
}

function getDeveloperStats($developerId) {
    $pdo = getDatabase();
    if (!$pdo) return ['clicks' => 0, 'earned' => 0, 'embeds' => 0];
    
    try {
        $stmt = $pdo->prepare("
            SELECT 
                COALESCE(SUM(total_clicks), 0) as total_clicks,
                COALESCE(SUM(total_earned), 0) as total_earned,
                (SELECT COUNT(*) FROM developer_embeds WHERE developer_id = ? AND is_active = 1) as active_embeds
            FROM developers WHERE id = ?
        ");
        $stmt->execute([$developerId, $developerId]);
        return $stmt->fetch() ?: ['total_clicks' => 0, 'total_earned' => 0, 'active_embeds' => 0];
    } catch (PDOException $e) {
        return ['total_clicks' => 0, 'total_earned' => 0, 'active_embeds' => 0];
    }
}

function recordAdClick($developerId, $adId, $clientId, $zone, $payoutAmount) {
    $pdo = getDatabase();
    if (!$pdo) return false;
    
    try {
        $stmt = $pdo->prepare("
            INSERT INTO ad_clicks (developer_id, ad_id, client_id, zone, payout_amount, ip_address, user_agent) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ");
        return $stmt->execute([
            $developerId, $adId, $clientId, $zone, $payoutAmount,
            $_SERVER['REMOTE_ADDR'] ?? '', $_SERVER['HTTP_USER_AGENT'] ?? ''
        ]);
    } catch (PDOException $e) {
        return false;
    }
}

// Initialize API
$api = new PythonCoinAPI();

// Handle AJAX requests
if (isset($_GET['ajax'])) {
    header('Content-Type: application/json');
    
    try {
        switch ($_GET['ajax']) {
            case 'discover_clients':
                $result = $api->discoverClients();
                if (!$result['success']) {
                    // Fallback to database clients if API is unavailable
                    $pdo = getDatabase();
                    if ($pdo) {
                        $stmt = $pdo->query("SELECT * FROM p2p_clients WHERE status = 'online' ORDER BY last_seen DESC");
                        $clients = $stmt->fetchAll();
                        $result = ['success' => true, 'clients' => $clients];
                    }
                }
                echo json_encode($result);
                break;
                
            case 'select_client':
                $result = $api->selectClient(
                    $_POST['developer_address'] ?? '',
                    $_POST['client_id'] ?? '',
                    $_POST['categories'] ?? []
                );
                echo json_encode($result);
                break;
                
            case 'generate_custom_js':
                $result = $api->generateCustomJS(
                    $_POST['developer_address'] ?? '',
                    $_POST['preferences'] ?? []
                );
                echo json_encode($result);
                break;
                
            case 'register_developer':
                $result = $api->registerDeveloper(
                    $_POST['developer'] ?? '',
                    $_POST['address'] ?? ''
                );
                echo json_encode($result);
                break;
                
            case 'get_stats':
                $result = $api->getStats();
                if (!$result['success'] && isset($_SESSION['developer'])) {
                    // Fallback to database stats
                    $developer = getDeveloperByUsername($_SESSION['developer']['username']);
                    if ($developer) {
                        $stats = getDeveloperStats($developer['id']);
                        $result = [
                            'success' => true,
                            'stats' => [
                                'total_developers' => 1,
                                'total_clicks' => $stats['total_clicks'],
                                'total_payments' => $stats['total_earned'],
                                'active_embeds' => $stats['active_embeds'],
                                'server_status' => 'online'
                            ]
                        ];
                    }
                }
                echo json_encode($result);
                break;
                
            case 'get_notifications':
                echo json_encode($api->getNotifications());
                break;
                
            case 'get_ads':
                echo json_encode($api->getAds());
                break;
                
            case 'test_connection':
                $result = $api->getClientInfo();
                echo json_encode($result);
                break;
                
            case 'heartbeat':
                if (isset($_SESSION['developer'])) {
                    $developer = getDeveloperByUsername($_SESSION['developer']['username']);
                    if ($developer) {
                        updateDeveloperLogin($developer['id']);
                    }
                }
                echo json_encode(['success' => true, 'timestamp' => time()]);
                break;
                
            case 'scan_network':
                // Try to get real clients from database first
                $pdo = getDatabase();
                $clients = [];
                
                if ($pdo) {
                    $stmt = $pdo->query("SELECT * FROM p2p_clients WHERE last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE) ORDER BY last_seen DESC");
                    $dbClients = $stmt->fetchAll();
                    
                    foreach ($dbClients as $client) {
                        $clients[] = [
                            'client_id' => $client['client_id'],
                            'name' => $client['name'],
                            'host' => $client['host'],
                            'port' => $client['port'],
                            'status' => $client['status'],
                            'ad_count' => $client['ad_count'] ?? 0,
                            'peers' => 0
                        ];
                    }
                }
                
                // If no clients in database, add mock data for demo
                if (empty($clients)) {
                    $clients = [
                        [
                            'client_id' => 'pyc_client_001',
                            'name' => 'PythonCoin Wallet - Demo',
                            'host' => '127.0.0.1',
                            'port' => 8082,
                            'status' => 'online',
                            'ad_count' => 5,
                            'peers' => 3
                        ]
                    ];
                }
                
                echo json_encode(['success' => true, 'clients' => $clients]);
                break;
                
            case 'record_click':
                if (isset($_SESSION['developer'])) {
                    $developer = getDeveloperByUsername($_SESSION['developer']['username']);
                    if ($developer) {
                        $adId = $_POST['ad_id'] ?? '';
                        $clientId = $_POST['client_id'] ?? '';
                        $zone = $_POST['zone'] ?? '';
                        $payoutAmount = floatval($_POST['payout_amount'] ?? 0.001);
                        
                        $success = recordAdClick($developer['id'], $adId, $clientId, $zone, $payoutAmount);
                        
                        if ($success) {
                            // Update developer totals
                            $pdo = getDatabase();
                            $stmt = $pdo->prepare("UPDATE developers SET total_clicks = total_clicks + 1, total_earned = total_earned + ? WHERE id = ?");
                            $stmt->execute([$payoutAmount, $developer['id']]);
                        }
                        
                        echo json_encode(['success' => $success, 'amount' => $payoutAmount]);
                    } else {
                        echo json_encode(['success' => false, 'error' => 'Developer not found']);
                    }
                } else {
                    echo json_encode(['success' => false, 'error' => 'Not logged in']);
                }
                break;
                
            default:
                echo json_encode(['success' => false, 'error' => 'Unknown action']);
        }
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
    exit;
}

// Handle authentication
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    switch ($_POST['action']) {
        case 'login':
            $username = trim($_POST['username'] ?? '');
            $password = $_POST['password'] ?? '';
            $pythoncoinAddress = trim($_POST['pythoncoin_address'] ?? '');
            
            if ($username && $password && $pythoncoinAddress) {
                $developer = getDeveloperByUsername($username);
                
                if ($developer && password_verify($password, $developer['password_hash'])) {
                    // Update PythonCoin address if different
                    if ($developer['pythoncoin_address'] !== $pythoncoinAddress) {
                        $pdo = getDatabase();
                        $stmt = $pdo->prepare("UPDATE developers SET pythoncoin_address = ? WHERE id = ?");
                        $stmt->execute([$pythoncoinAddress, $developer['id']]);
                        $developer['pythoncoin_address'] = $pythoncoinAddress;
                    }
                    
                    $_SESSION['developer'] = [
                        'id' => $developer['id'],
                        'username' => $developer['username'],
                        'pythoncoin_address' => $developer['pythoncoin_address'],
                        'login_time' => time()
                    ];
                    
                    updateDeveloperLogin($developer['id']);
                    $api->registerDeveloper($username, $pythoncoinAddress);
                    
                    header('Content-Type: application/json');
                    echo json_encode(['success' => true, 'message' => 'Login successful']);
                    exit;
                } else {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
                    exit;
                }
            }
            break;
            
        case 'register':
            $username = trim($_POST['username'] ?? '');
            $password = $_POST['password'] ?? '';
            $confirmPassword = $_POST['confirm_password'] ?? '';
            $pythoncoinAddress = trim($_POST['pythoncoin_address'] ?? '');
            $email = trim($_POST['email'] ?? '');
            
            if ($username && $password && $password === $confirmPassword && $pythoncoinAddress) {
                if (getDeveloperByUsername($username)) {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => false, 'message' => 'Username already exists']);
                    exit;
                }
                
                if (createDeveloper($username, $password, $pythoncoinAddress, $email)) {
                    $developer = getDeveloperByUsername($username);
                    $_SESSION['developer'] = [
                        'id' => $developer['id'],
                        'username' => $developer['username'],
                        'pythoncoin_address' => $developer['pythoncoin_address'],
                        'login_time' => time()
                    ];
                    
                    header('Content-Type: application/json');
                    echo json_encode(['success' => true, 'message' => 'Registration successful']);
                    exit;
                } else {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => false, 'message' => 'Registration failed']);
                    exit;
                }
            }
            break;
            
        case 'logout':
            session_destroy();
            header('Location: ' . $_SERVER['PHP_SELF']);
            exit;
    }
}

// Check if user is logged in
$isLoggedIn = isset($_SESSION['developer']);
$currentUser = $_SESSION['developer'] ?? null;

// Get current data if logged in
$clientInfo = null;
$stats = null;
$notifications = null;
$ads = null;
$developerStats = null;

if ($isLoggedIn) {
    $clientInfo = $api->getClientInfo();
    $stats = $api->getStats();
    $notifications = $api->getNotifications();
    $ads = $api->getAds();
    
    // Get developer stats from database
    $developer = getDeveloperByUsername($currentUser['username']);
    if ($developer) {
        $developerStats = getDeveloperStats($developer['id']);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonCoin Developer Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #0066cc;
            --primary-dark: #0056b3;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
            --dark: #343a40;
            --light: #f8f9fa;
            --border: #dee2e6;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-lg: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255,255,255,0.95);
            padding: 15px 0;
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
            <?php echo !$isLoggedIn ? 'display: none;' : ''; ?>
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .network-status {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.9em;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .status-online { background: #d4edda; color: #155724; }
        .status-offline { background: #f8d7da; color: #721c24; }
        .status-connecting { background: #fff3cd; color: #856404; }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .developer-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .api-key-display {
            font-family: monospace;
            background: #f8f9fa;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border);
            font-size: 0.8em;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .logout-btn {
            background: var(--danger);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }
        
        .logout-btn:hover {
            background: #c82333;
        }
        
        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .auth-container {
            max-width: 450px;
            margin: 100px auto;
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 40px;
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(10px);
            <?php echo $isLoggedIn ? 'display: none;' : ''; ?>
        }
        
        .auth-tabs {
            display: flex;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            background: var(--light);
        }
        
        .auth-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            background: var(--light);
            border: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .auth-tab.active {
            background: var(--primary);
            color: white;
        }
        
        .auth-form {
            display: none;
        }
        
        .auth-form.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #4a5568;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .submit-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .dashboard {
            <?php echo !$isLoggedIn ? 'display: none;' : ''; ?>
        }
        
        .dashboard-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border);
            flex-wrap: wrap;
        }
        
        .dashboard-tab {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            color: #718096;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .dashboard-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .panel {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        
        .panel h2 {
            color: var(--primary);
            margin-bottom: 20px;
            font-size: 1.4em;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .grid {
            display: grid;
            gap: 20px;
        }
        
        .grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
        .grid-3 { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
        .grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
        
        .stats-card {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stats-card:hover {
            transform: translateY(-3px);
        }
        
        .stats-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
            position: relative;
            z-index: 1;
        }
        
        .stats-label {
            font-size: 0.9em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .btn-primary { background: var(--primary); color: white; }
        .btn-success { background: var(--success); color: white; }
        .btn-warning { background: var(--warning); color: white; }
        .btn-danger { background: var(--danger); color: white; }
        .btn-info { background: var(--info); color: white; }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .network-client {
            background: white;
            border: 2px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .network-client:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow);
        }
        
        .network-client.selected {
            border-color: var(--success);
            background: #f8fff9;
        }
        
        .client-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .client-info h3 {
            margin: 0 0 5px 0;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .client-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .client-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 10px;
            background: var(--light);
            border-radius: 6px;
        }
        
        .stat-number {
            font-size: 1.2em;
            font-weight: bold;
            color: var(--primary);
        }
        
        .stat-label {
            font-size: 0.8em;
            color: #666;
        }
        
        .code-preview {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            margin: 15px 0;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
            position: relative;
        }
        
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--success);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .embed-form {
            background: var(--light);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .ad-preview {
            border: 2px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            background: white;
        }
        
        .ad-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            border-bottom: 1px solid var(--border);
            transition: background-color 0.3s ease;
        }
        
        .ad-item:hover {
            background-color: var(--light);
        }
        
        .ad-image {
            width: 80px;
            height: 60px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            color: white;
            font-weight: bold;
        }
        
        .ad-content {
            flex: 1;
        }
        
        .ad-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .ad-description {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 4px;
        }
        
        .ad-meta {
            font-size: 0.8em;
            color: #999;
        }
        
        .pythoncoin-address {
            font-family: monospace;
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border);
            font-size: 0.9em;
            word-break: break-all;
        }
        
        .earnings-display {
            background: linear-gradient(135deg, var(--success) 0%, #20c997 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .earnings-amount {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .server-connection {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: var(--light);
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .connection-light {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .light-green { background: var(--success); }
        .light-red { background: var(--danger); }
        .light-yellow { background: var(--warning); }
        
        .real-time-log {
            background: #1a202c;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
            margin: 15px 0;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 2px 0;
        }
        
        .log-timestamp {
            color: #a0aec0;
        }
        
        .log-info { color: #63b3ed; }
        .log-success { color: #68d391; }
        .log-warning { color: #faf089; }
        .log-error { color: #fc8181; }
        
        .selected-clients {
            min-height: 60px;
            border: 2px dashed var(--border);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        
        .client-tag {
            background: var(--primary);
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .remove-client {
            background: rgba(255,255,255,0.3);
            border: none;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 500;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 15px;
            }
            
            .dashboard-tabs {
                overflow-x: auto;
                white-space: nowrap;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header" id="header">
        <div class="header-content">
            <div class="logo">
                🌐 PythonCoin P2P Ad Network
                <span style="font-size: 0.6em; color: #718096;">Developer Portal</span>
            </div>
            <div class="network-status">
                <div class="status-indicator" id="connectionStatus">
                    <div class="status-dot"></div>
                    <span id="statusText">Online</span>
                </div>
                <div class="server-connection">
                    <div class="connection-light light-green" id="serverLight"></div>
                    <span id="serverStatus">Central Server</span>
                </div>
            </div>
            <div class="developer-info">
                <span>Developer: <strong><?php echo htmlspecialchars($currentUser['username'] ?? ''); ?></strong></span>
                <div class="api-key-display" title="Your PythonCoin Address">
                    <?php echo htmlspecialchars(substr($currentUser['pythoncoin_address'] ?? '', 0, 12) . '...'); ?>
                </div>
                <div class="earnings-display" style="padding: 8px 12px; font-size: 0.9em;">
                    <?php echo number_format($developerStats['total_earned'] ?? 0, 8); ?> PYC
                </div>
                <form method="post" style="display: inline;">
                    <input type="hidden" name="action" value="logout">
                    <button type="submit" class="logout-btn">Logout</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Authentication -->
    <div class="auth-container" id="authContainer">
        <div class="logo" style="text-align: center; margin-bottom: 30px;">
            🌐 PythonCoin P2P Ad Network<br>
            <small style="font-size: 0.6em; color: #718096;">Developer Integration Portal</small>
        </div>
        
        <div class="auth-tabs">
            <button class="auth-tab active" onclick="switchTab('login')">Login</button>
            <button class="auth-tab" onclick="switchTab('register')">Register</button>
        </div>
        
        <!-- Login Form -->
        <form class="auth-form active" id="loginForm" onsubmit="login(event)">
            <div class="form-group">
                <label for="loginUsername">Username</label>
                <input type="text" id="loginUsername" name="username" required>
            </div>
            <div class="form-group">
                <label for="loginPassword">Password</label>
                <input type="password" id="loginPassword" name="password" required>
            </div>
            <div class="form-group">
                <label for="loginPyCoinAddress">PythonCoin Address</label>
                <input type="text" id="loginPyCoinAddress" name="pythoncoin_address" placeholder="Your PythonCoin wallet address" required>
                <small style="color: #666; font-size: 0.85em;">This address will receive earnings from ad clicks</small>
            </div>
            <input type="hidden" name="action" value="login">
            <button type="submit" class="submit-btn">Connect to Network</button>
        </form>
        
        <!-- Register Form -->
        <form class="auth-form" id="registerForm" onsubmit="register(event)">
            <div class="form-group">
                <label for="registerUsername">Username</label>
                <input type="text" id="registerUsername" name="username" required>
            </div>
            <div class="form-group">
                <label for="registerPassword">Password</label>
                <input type="password" id="registerPassword" name="password" required minlength="6">
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" name="confirm_password" required>
            </div>
            <div class="form-group">
                <label for="registerPyCoinAddress">PythonCoin Address</label>
                <input type="text" id="registerPyCoinAddress" name="pythoncoin_address" placeholder="Your PythonCoin wallet address" required>
                <small style="color: #666; font-size: 0.85em;">Generate a PythonCoin address from the wallet application</small>
            </div>
            <div class="form-group">
                <label for="registerEmail">Email (Optional)</label>
                <input type="email" id="registerEmail" name="email" placeholder="your@email.com">
            </div>
            <input type="hidden" name="action" value="register">
            <button type="submit" class="submit-btn">Join Network</button>
        </form>
        
        <div id="authMessage"></div>
    </div>

    <!-- Dashboard -->
    <div class="container dashboard" id="dashboard">
        <!-- Dashboard Tabs -->
        <div class="dashboard-tabs">
            <button class="dashboard-tab active" onclick="switchDashboardTab('overview')">📊 Overview</button>
            <button class="dashboard-tab" onclick="switchDashboardTab('network')">🌐 P2P Clients</button>
            <button class="dashboard-tab" onclick="switchDashboardTab('generator')">🔗 JS Generator</button>
            <button class="dashboard-tab" onclick="switchDashboardTab('ads')">📺 Live Ads</button>
        </div>

        <!-- Overview Tab -->
        <div class="tab-content active" id="overviewTab">
            <div class="grid grid-4">
                <div class="stats-card">
                    <div class="stats-number"><?php echo number_format($developerStats['total_clicks'] ?? 0); ?></div>
                    <div class="stats-label">Total Clicks</div>
                </div>
                <div class="stats-card" style="background: linear-gradient(135deg, var(--success) 0%, #20c997 100%);">
                    <div class="stats-number"><?php echo number_format($developerStats['total_earned'] ?? 0, 8); ?></div>
                    <div class="stats-label">PYC Earned</div>
                </div>
                <div class="stats-card" style="background: linear-gradient(135deg, var(--info) 0%, #138496 100%);">
                    <div class="stats-number"><?php echo $developerStats['active_embeds'] ?? 0; ?></div>
                    <div class="stats-label">Active Embeds</div>
                </div>
                <div class="stats-card" style="background: linear-gradient(135deg, var(--warning) 0%, #e0a800 100%);">
                    <div class="stats-number" id="connectedClients">0</div>
                    <div class="stats-label">Connected Clients</div>
                </div>
            </div>
            
            <div class="grid grid-2">
                <div class="panel">
                    <h2>🔄 Real-Time Activity</h2>
                    <div class="real-time-log" id="activityLog">
                        <div class="log-entry"><span class="log-timestamp">[<?php echo date('H:i:s'); ?>]</span> <span class="log-info">Portal initialized</span></div>
                        <?php if ($isLoggedIn): ?>
                        <div class="log-entry"><span class="log-timestamp">[<?php echo date('H:i:s'); ?>]</span> <span class="log-success">Developer <?php echo htmlspecialchars($currentUser['username']); ?> connected</span></div>
                        <?php endif; ?>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>⚡ Quick Actions</h2>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button class="btn btn-primary" onclick="switchDashboardTab('network')">🔍 Scan for P2P Clients</button>
                        <button class="btn btn-success" onclick="switchDashboardTab('generator')">⚡ Generate Ad Block</button>
                        <button class="btn btn-info" onclick="testConnection()">🔧 Test Central Server</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Network Tab -->
        <div class="tab-content" id="networkTab">
            <div class="panel">
                <h2>🌐 Discover P2P Ad Clients</h2>
                <p>Connect to active PythonCoin P2P ad clients to access their advertisement content.</p>
                
                <div style="margin: 20px 0;">
                    <button class="btn btn-primary" onclick="scanForClients()">🔍 Scan Network</button>
                    <button class="btn btn-info" onclick="refreshClients()">🔄 Refresh</button>
                    <button class="btn btn-success" onclick="connectToSelected()">🔗 Connect Selected</button>
                </div>
                
                <div id="clientsList">
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <h3>Click "Scan Network" to discover P2P clients</h3>
                        <p>Looking for Python Qt clients running on port 8082...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Generator Tab -->
        <div class="tab-content" id="generatorTab">
            <div class="panel">
                <h2>⚡ JavaScript Ad Block Generator</h2>
                <p>Generate personalized ad blocks that serve content from selected P2P clients.</p>
                
                <div class="selected-clients" id="selectedClientsDisplay">
                    <span style="color: #666; font-style: italic;">Select P2P clients from the Network tab</span>
                </div>
                
                <div class="embed-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="embedZone">Zone Identifier</label>
                            <input type="text" id="embedZone" value="main-content" placeholder="e.g., sidebar, header">
                        </div>
                        <div class="form-group">
                            <label for="adRotation">Rotation Interval</label>
                            <select id="adRotation">
                                <option value="15">15 seconds</option>
                                <option value="30" selected>30 seconds</option>
                                <option value="60">1 minute</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="embedWidth">Width</label>
                            <input type="text" id="embedWidth" value="400px">
                        </div>
                        <div class="form-group">
                            <label for="embedHeight">Height</label>
                            <input type="text" id="embedHeight" value="300px">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Your PythonCoin Address</label>
                        <div class="pythoncoin-address" id="pythonCoinAddressDisplay">
                            <?php echo htmlspecialchars($currentUser['pythoncoin_address'] ?? 'Loading...'); ?>
                        </div>
                    </div>
                </div>
                
                <div style="margin: 20px 0;">
                    <button class="btn btn-success" onclick="generateAdBlock()">🚀 Generate Ad Block</button>
                    <button class="btn btn-warning" onclick="downloadAdBlock()">💾 Download</button>
                </div>
                
                <div class="code-preview" id="generatedCode" style="display: none;">
                    <button class="copy-btn" onclick="copyToClipboard()">📋 Copy</button>
                    <div id="codeContent"></div>
                </div>
            </div>
        </div>

        <!-- Ads Tab -->
        <div class="tab-content" id="adsTab">
            <div class="panel">
                <h2>📺 Live Advertisement Feed</h2>
                <p>Browse available advertisements from connected P2P clients.</p>
                
                <div style="margin: 20px 0;">
                    <button class="btn btn-primary" onclick="refreshAds()">🔄 Refresh Ads</button>
                </div>
                
                <div class="ad-preview" id="adsList">
                    <?php if ($ads && isset($ads['ads']) && is_array($ads['ads'])): ?>
                        <?php foreach ($ads['ads'] as $ad): ?>
                        <div class="ad-item">
                            <div class="ad-image">📺</div>
                            <div class="ad-content">
                                <div class="ad-title"><?php echo htmlspecialchars($ad['title'] ?? 'Untitled Ad'); ?></div>
                                <div class="ad-description"><?php echo htmlspecialchars($ad['description'] ?? 'No description'); ?></div>
                                <div class="ad-meta"><strong>Category:</strong> <?php echo htmlspecialchars($ad['category'] ?? 'general'); ?> | <strong>Payout:</strong> <?php echo number_format($ad['payout'] ?? 0.001, 8); ?> PYC</div>
                            </div>
                            <button class="btn btn-info" onclick="previewSingleAd('<?php echo htmlspecialchars($ad['id'] ?? ''); ?>')">👁️ Preview</button>
                        </div>
                        <?php endforeach; ?>
                    <?php else: ?>
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <h3>No live ads available</h3>
                        <p>Connect to P2P clients first, then click "Refresh Ads"</p>
                    </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
<script src="pythoncoin-adblock-justis-1750042283028.js"></script><div data-pyc-zone="main-content"></div>
    <script>
        // Global application state
        var currentUser = <?php echo json_encode($currentUser); ?>;
        var selectedClients = [];
        var availableClients = [];
        var liveAds = <?php echo json_encode($ads['ads'] ?? []); ?>;
        var serverConfig = {
            mainApi: window.location.href,
            jsServer: 'http://127.0.0.1:8082'
        };
        
        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            <?php if ($isLoggedIn): ?>
            addLog('Developer <?php echo htmlspecialchars($currentUser['username']); ?> connected', 'success');
            connectToCentralServer();
            <?php endif; ?>
        });
        
        // Authentication Functions
        function switchTab(tab) {
            var tabs = document.querySelectorAll('.auth-tab');
            var forms = document.querySelectorAll('.auth-form');
            
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            for (var i = 0; i < forms.length; i++) {
                forms[i].classList.remove('active');
            }
            
            var activeTab = document.querySelector('[onclick*="' + tab + '"]');
            var activeForm = document.getElementById(tab + 'Form');
            
            if (activeTab) activeTab.classList.add('active');
            if (activeForm) activeForm.classList.add('active');
        }
        
        function switchDashboardTab(tab) {
            var tabs = document.querySelectorAll('.dashboard-tab');
            var contents = document.querySelectorAll('.tab-content');
            
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            var activeTab = document.querySelector('[onclick*="' + tab + '"]');
            var activeContent = document.getElementById(tab + 'Tab');
            
            if (activeTab) activeTab.classList.add('active');
            if (activeContent) activeContent.classList.add('active');
            
            // Load tab-specific data
            if (tab === 'ads') {
                loadLiveAds();
            }
        }
        
        function login(event) {
            event.preventDefault();
            
            var formData = new FormData(event.target);
            var submitBtn = event.target.querySelector('.submit-btn');
            
            submitBtn.textContent = 'Connecting...';
            submitBtn.disabled = true;
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(function() { 
                        window.location.reload(); 
                    }, 1000);
                } else {
                    showMessage(data.message || 'Login failed', 'error');
                }
            })
            .catch(function(error) {
                showMessage('Connection error: ' + error.message, 'error');
            })
            .finally(function() {
                submitBtn.textContent = 'Connect to Network';
                submitBtn.disabled = false;
            });
        }
        
        function register(event) {
            event.preventDefault();
            
            var password = document.getElementById('registerPassword').value;
            var confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                showMessage('Passwords do not match', 'error');
                return;
            }
            
            var formData = new FormData(event.target);
            var submitBtn = event.target.querySelector('.submit-btn');
            
            submitBtn.textContent = 'Creating Account...';
            submitBtn.disabled = true;
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    showMessage('Registration successful! Redirecting...', 'success');
                    setTimeout(function() { 
                        window.location.reload(); 
                    }, 1000);
                } else {
                    showMessage(data.message || 'Registration failed', 'error');
                }
            })
            .catch(function(error) {
                showMessage('Connection error: ' + error.message, 'error');
            })
            .finally(function() {
                submitBtn.textContent = 'Join Network';
                submitBtn.disabled = false;
            });
        }
        
        function connectToCentralServer() {
            updateServerStatus('connecting');
            
            fetch('?ajax=heartbeat')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        updateServerStatus('online');
                        addLog('Connected to central server', 'success');
                    } else {
                        updateServerStatus('offline');
                        addLog('Central server connection failed', 'error');
                    }
                })
                .catch(function(error) {
                    updateServerStatus('offline');
                    addLog('Server connection error: ' + error.message, 'error');
                });
        }
        
        function updateServerStatus(status) {
            var statusEl = document.getElementById('connectionStatus');
            var lightEl = document.getElementById('serverLight');
            var statusTextEl = document.getElementById('statusText');
            var serverStatusEl = document.getElementById('serverStatus');
            
            if (statusEl) statusEl.className = 'status-indicator status-' + status;
            
            if (status === 'online') {
                if (lightEl) lightEl.className = 'connection-light light-green';
                if (statusTextEl) statusTextEl.textContent = 'Connected';
                if (serverStatusEl) serverStatusEl.textContent = 'Central Server Online';
            } else if (status === 'offline') {
                if (lightEl) lightEl.className = 'connection-light light-red';
                if (statusTextEl) statusTextEl.textContent = 'Offline';
                if (serverStatusEl) serverStatusEl.textContent = 'Central Server Offline';
            } else {
                if (lightEl) lightEl.className = 'connection-light light-yellow';
                if (statusTextEl) statusTextEl.textContent = 'Connecting...';
                if (serverStatusEl) serverStatusEl.textContent = 'Connecting to Server...';
            }
        }
        
        function scanForClients() {
            addLog('Scanning network for P2P clients...', 'info');
            
            var scanBtn = document.querySelector('[onclick="scanForClients()"]');
            var originalText = scanBtn.textContent;
            scanBtn.textContent = '🔍 Scanning...';
            scanBtn.disabled = true;
            
            fetch('?ajax=scan_network')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        availableClients = data.clients || [];
                        displayNetworkClients();
                        addLog('Network scan complete: Found ' + availableClients.length + ' P2P clients', 'success');
                        updateConnectedClientsCount();
                    } else {
                        addLog('Network scan failed: ' + (data.message || data.error), 'error');
                    }
                })
                .catch(function(error) {
                    addLog('Scan error: ' + error.message, 'error');
                })
                .finally(function() {
                    scanBtn.textContent = originalText;
                    scanBtn.disabled = false;
                });
        }
        
        function displayNetworkClients() {
            var container = document.getElementById('clientsList');
            
            if (availableClients.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><h3>No P2P clients found</h3><p>Make sure your Python Qt client is running on port 8082</p></div>';
                return;
            }
            
            var html = '';
            for (var i = 0; i < availableClients.length; i++) {
                var client = availableClients[i];
                var isSelected = selectedClients.some(function(c) { return c.client_id === client.client_id; });
                
                html += '<div class="network-client ' + (isSelected ? 'selected' : '') + '">';
                html += '<div class="client-header">';
                html += '<div class="client-info">';
                html += '<h3><span class="status-badge status-' + client.status + '">' + client.status + '</span> ' + client.name + '</h3>';
                html += '<div class="client-meta"><strong>Client ID:</strong> ' + client.client_id + ' | <strong>Address:</strong> ' + client.host + ':' + client.port + '</div>';
                html += '</div>';
                html += '<button class="btn ' + (isSelected ? 'btn-success' : 'btn-primary') + '" onclick="toggleClientSelection(\'' + client.client_id + '\')">';
                html += isSelected ? '✓ Selected' : 'Select';
                html += '</button>';
                html += '</div>';
                html += '<div class="client-stats">';
                html += '<div class="stat-item"><div class="stat-number">' + (client.ad_count || 0) + '</div><div class="stat-label">Ads</div></div>';
                html += '<div class="stat-item"><div class="stat-number">' + (client.peers || 0) + '</div><div class="stat-label">Peers</div></div>';
                html += '</div>';
                html += '</div>';
            }
            
            container.innerHTML = html;
        }
        
        function toggleClientSelection(clientId) {
            var client = availableClients.find(function(c) { return c.client_id === clientId; });
            if (!client || client.status === 'offline') return;
            
            var index = selectedClients.findIndex(function(c) { return c.client_id === clientId; });
            
            if (index > -1) {
                selectedClients.splice(index, 1);
                addLog('Removed ' + client.name + ' from selection', 'info');
            } else {
                selectedClients.push(client);
                addLog('Added ' + client.name + ' to selection', 'info');
            }
            
            displayNetworkClients();
            updateSelectedClientsDisplay();
            updateConnectedClientsCount();
        }
        
        function updateSelectedClientsDisplay() {
            var container = document.getElementById('selectedClientsDisplay');
            
            if (selectedClients.length === 0) {
                container.innerHTML = '<span style="color: #666; font-style: italic;">Select P2P clients from the Network tab</span>';
                return;
            }
            
            var html = '';
            for (var i = 0; i < selectedClients.length; i++) {
                var client = selectedClients[i];
                html += '<div class="client-tag">' + client.name + ' <button class="remove-client" onclick="removeClientSelection(\'' + client.client_id + '\')">×</button></div>';
            }
            
            container.innerHTML = html;
        }
        
        function removeClientSelection(clientId) {
            selectedClients = selectedClients.filter(function(c) { return c.client_id !== clientId; });
            updateSelectedClientsDisplay();
            displayNetworkClients();
            updateConnectedClientsCount();
        }
        
        function updateConnectedClientsCount() {
            var countEl = document.getElementById('connectedClients');
            if (countEl) {
                countEl.textContent = selectedClients.length;
            }
        }
        
        function generateAdBlock() {
            if (selectedClients.length === 0) {
                alert('Please select at least one P2P client from the Network tab');
                return;
            }
            
            var zone = document.getElementById('embedZone').value || 'main-content';
            var rotation = parseInt(document.getElementById('adRotation').value) || 30;
            var width = document.getElementById('embedWidth').value || '400px';
            var height = document.getElementById('embedHeight').value || '300px';
            
            addLog('Generating ad block for zone: ' + zone, 'info');
            
            var adBlockCode = generateJavaScriptAdBlock({
                zone: zone,
                rotation: rotation,
                width: width,
                height: height,
                pythonCoinAddress: currentUser.pythoncoin_address,
                developer: currentUser.username,
                selectedClients: selectedClients,
                serverConfig: serverConfig
            });
            
            document.getElementById('codeContent').textContent = adBlockCode;
            document.getElementById('generatedCode').style.display = 'block';
            
            addLog('Ad block generated successfully', 'success');
        }
        
        function generateJavaScriptAdBlock(config) {
            var clientsJson = JSON.stringify(config.selectedClients);
            
            var code = '// PythonCoin P2P Ad Network - Generated Ad Block\n';
            code += '// Developer: ' + config.developer + '\n';
            code += '// PythonCoin Address: ' + config.pythonCoinAddress + '\n';
            code += '// Generated: ' + new Date().toISOString() + '\n';
            code += '// Zone: ' + config.zone + '\n\n';
            code += '(function() {\n';
            code += '    "use strict";\n\n';
            code += '    var PYC_AD_CONFIG = {\n';
            code += '        zone: "' + config.zone + '",\n';
            code += '        rotation: ' + (config.rotation * 1000) + ',\n';
            code += '        width: "' + config.width + '",\n';
            code += '        height: "' + config.height + '",\n';
            code += '        developer: "' + config.developer + '",\n';
            code += '        pythonCoinAddress: "' + config.pythonCoinAddress + '",\n';
            code += '        centralServer: "' + window.location.href + '",\n';
            code += '        clients: ' + clientsJson + ',\n';
            code += '        currentAdIndex: 0,\n';
            code += '        container: null,\n';
            code += '        rotationTimer: null\n';
            code += '    };\n\n';
            code += '    function initializeAdBlock() {\n';
            code += '        console.log("PythonCoin Ad Block Initializing...", PYC_AD_CONFIG);\n';
            code += '        var container = document.querySelector("[data-pyc-zone=\\"" + PYC_AD_CONFIG.zone + "\\"]");\n';
            code += '        if (!container) {\n';
            code += '            console.error("PYC Ad Zone not found:", PYC_AD_CONFIG.zone);\n';
            code += '            return;\n';
            code += '        }\n';
            code += '        PYC_AD_CONFIG.container = container;\n';
            code += '        container.style.width = PYC_AD_CONFIG.width;\n';
            code += '        container.style.height = PYC_AD_CONFIG.height;\n';
            code += '        container.style.border = "1px solid #ddd";\n';
            code += '        container.style.borderRadius = "8px";\n';
            code += '        container.style.backgroundColor = "#f8f9fa";\n';
            code += '        loadNextAd();\n';
            code += '        if (PYC_AD_CONFIG.rotation > 0) {\n';
            code += '            PYC_AD_CONFIG.rotationTimer = setInterval(loadNextAd, PYC_AD_CONFIG.rotation);\n';
            code += '        }\n';
            code += '    }\n\n';
            code += '    function loadNextAd() {\n';
            code += '        if (PYC_AD_CONFIG.clients.length === 0) {\n';
            code += '            showPlaceholder("No P2P clients connected");\n';
            code += '            return;\n';
            code += '        }\n';
            code += '        var client = PYC_AD_CONFIG.clients[PYC_AD_CONFIG.currentAdIndex % PYC_AD_CONFIG.clients.length];\n';
            code += '        PYC_AD_CONFIG.currentAdIndex++;\n';
            code += '        fetch("http://" + client.host + ":" + client.port + "/ads?zone=" + PYC_AD_CONFIG.zone)\n';
            code += '            .then(function(response) { return response.json(); })\n';
            code += '            .then(function(data) {\n';
            code += '                if (data.ads && data.ads.length > 0) {\n';
            code += '                    displayAd(data.ads[0], client);\n';
            code += '                } else {\n';
            code += '                    showPlaceholder("No ads from " + client.name);\n';
            code += '                }\n';
            code += '            })\n';
            code += '            .catch(function() {\n';
            code += '                showPlaceholder("Loading ads...");\n';
            code += '            });\n';
            code += '    }\n\n';
            code += '    function displayAd(ad, client) {\n';
            code += '        var html = "<div style=\\"padding:15px;height:100%;display:flex;flex-direction:column;justify-content:center;\\">";\n';
            code += '        html += "<h4 style=\\"margin:0 0 8px 0;font-size:14px;text-align:center;\\">" + ad.title + "</h4>";\n';
            code += '        html += "<p style=\\"margin:0 0 10px 0;font-size:12px;color:#666;text-align:center;\\">" + ad.description + "</p>";\n';
            code += '        html += "<div style=\\"text-align:center;\\"><button onclick=\\"recordClick(\\\'" + ad.id + "\\\', \\\'" + client.client_id + "\\\')\\" style=\\"background:#0066cc;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;\\">Learn More</button></div>";\n';
            code += '        html += "</div>";\n';
            code += '        PYC_AD_CONFIG.container.innerHTML = html;\n';
            code += '    }\n\n';
            code += '    function showPlaceholder(message) {\n';
            code += '        PYC_AD_CONFIG.container.innerHTML = "<div style=\\"display:flex;align-items:center;justify-content:center;height:100%;color:#666;\\">" + message + "</div>";\n';
            code += '    }\n\n';
            code += '    window.recordClick = function(adId, clientId) {\n';
            code += '        console.log("Ad clicked:", adId);\n';
            code += '        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_click", {\n';
            code += '            method: "POST",\n';
            code += '            headers: {"Content-Type": "application/x-www-form-urlencoded"},\n';
            code += '            body: "ad_id=" + encodeURIComponent(adId) + "&client_id=" + encodeURIComponent(clientId) + "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + "&payout_amount=0.001"\n';
            code += '        }).then(function(response) { return response.json(); })\n';
            code += '          .then(function(data) {\n';
            code += '              if (data.success) {\n';
            code += '                  console.log("Click recorded successfully");\n';
            code += '              }\n';
            code += '          })\n';
            code += '          .catch(function(e) { console.error("Click record failed:", e); });\n';
            code += '    };\n\n';
            code += '    if (document.readyState === "loading") {\n';
            code += '        document.addEventListener("DOMContentLoaded", initializeAdBlock);\n';
            code += '    } else {\n';
            code += '        initializeAdBlock();\n';
            code += '    }\n';
            code += '})();\n\n';
            code += '// Usage: <div data-pyc-zone="' + config.zone + '"></div>';
            
            return code;
        }
        
        function copyToClipboard() {
            var code = document.getElementById('codeContent').textContent;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(function() {
                    addLog('Ad block code copied to clipboard', 'success');
                    alert('Code copied to clipboard!');
                });
            } else {
                var textArea = document.createElement('textarea');
                textArea.value = code;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Code copied to clipboard!');
            }
        }
        
        function downloadAdBlock() {
            var code = document.getElementById('codeContent').textContent;
            
            if (!code) {
                alert('Generate ad block code first');
                return;
            }
            
            var blob = new Blob([code], { type: 'application/javascript' });
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'pythoncoin-adblock-' + currentUser.username + '-' + Date.now() + '.js';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            addLog('Ad block JavaScript file downloaded', 'success');
        }
        
        function loadLiveAds() {
            addLog('Loading live ads from P2P network...', 'info');
            
            fetch('?ajax=get_ads')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success && data.ads) {
                        liveAds = data.ads;
                        displayLiveAds();
                        addLog('Loaded ' + liveAds.length + ' live ads', 'success');
                    } else {
                        addLog('Failed to load ads: ' + (data.message || data.error), 'error');
                    }
                })
                .catch(function(error) {
                    addLog('Error loading ads: ' + error.message, 'error');
                });
        }
        
        function displayLiveAds() {
            var container = document.getElementById('adsList');
            
            if (liveAds.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><h3>No live ads available</h3><p>Connect to P2P clients first</p></div>';
                return;
            }
            
            var html = '';
            for (var i = 0; i < liveAds.length; i++) {
                var ad = liveAds[i];
                html += '<div class="ad-item">';
                html += '<div class="ad-image">📺</div>';
                html += '<div class="ad-content">';
                html += '<div class="ad-title">' + (ad.title || 'Untitled Ad') + '</div>';
                html += '<div class="ad-description">' + (ad.description || 'No description') + '</div>';
                html += '<div class="ad-meta"><strong>Category:</strong> ' + (ad.category || 'general') + ' | <strong>Payout:</strong> ' + (ad.payout || 0.001).toFixed(8) + ' PYC</div>';
                html += '</div>';
                html += '<button class="btn btn-info" onclick="previewSingleAd(\'' + (ad.id || '') + '\')">👁️ Preview</button>';
                html += '</div>';
            }
            
            container.innerHTML = html;
        }
        
        function previewSingleAd(adId) {
            var ad = liveAds.find(function(a) { return a.id === adId; });
            if (!ad) return;
            
            var previewWindow = window.open('', '_blank', 'width=600,height=500');
            previewWindow.document.write('<html><head><title>Ad Preview</title></head><body style="font-family:Arial;padding:20px;background:#667eea;color:white;"><h2>Ad Preview</h2><h3>' + (ad.title || 'Untitled') + '</h3><p>' + (ad.description || 'No description') + '</p><p><strong>Category:</strong> ' + (ad.category || 'general') + '</p></body></html>');
            previewWindow.document.close();
            
            addLog('Previewed ad: ' + (ad.title || 'Untitled'), 'info');
        }
        
        function testConnection() {
            addLog('Testing central server connection...', 'info');
            updateServerStatus('connecting');
            
            fetch('?ajax=test_connection')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data.success) {
                        updateServerStatus('online');
                        addLog('Central server connection successful', 'success');
                        alert('Connection test successful!');
                    } else {
                        throw new Error(data.message || data.error);
                    }
                })
                .catch(function(error) {
                    updateServerStatus('offline');
                    addLog('Central server connection failed: ' + error.message, 'error');
                    alert('Connection test failed: ' + error.message);
                });
        }
        
        function refreshClients() {
            addLog('Refreshing P2P client list...', 'info');
            scanForClients();
        }
        
        function connectToSelected() {
            if (selectedClients.length === 0) {
                alert('Please select at least one P2P client first');
                return;
            }
            
            addLog('Connecting to ' + selectedClients.length + ' selected clients...', 'info');
            
            for (var i = 0; i < selectedClients.length; i++) {
                var client = selectedClients[i];
                addLog('Connected to ' + client.name, 'success');
            }
        }
        
        function refreshAds() {
            addLog('Refreshing live ads...', 'info');
            loadLiveAds();
        }
        
        function addLog(message, type) {
            var log = document.getElementById('activityLog');
            if (!log) return;
            
            var timestamp = new Date().toLocaleTimeString();
            var entry = document.createElement('div');
            entry.className = 'log-entry log-' + (type || 'info');
            entry.innerHTML = '<span class="log-timestamp">[' + timestamp + ']</span> <span>' + message + '</span>';
            
            log.insertBefore(entry, log.firstChild);
            
            while (log.children.length > 50) {
                log.removeChild(log.lastChild);
            }
            
            log.scrollTop = 0;
        }
        
        function showMessage(message, type) {
            var messageDiv = document.getElementById('authMessage');
            if (messageDiv) {
                messageDiv.innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
                
                setTimeout(function() {
                    messageDiv.innerHTML = '';
                }, 5000);
            }
        }
        
        // Auto-refresh functionality
        setInterval(function() {
            if (currentUser) {
                fetch('?ajax=heartbeat').catch(function() {});
            }
        }, 30000);
        
        console.log('PythonCoin P2P Ad Network Developer Portal initialized');
    </script>
</body>
</html>