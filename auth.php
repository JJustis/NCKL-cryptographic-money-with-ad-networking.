<?php
// Authentication handler for Enhanced P2P Ad Network
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$config = include 'config.php';
$host = $config['database']['host'];
$dbname = $config['database']['dbname'];
$username = $config['database']['username'];
$password = $config['database']['password'];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$action = $input['action'] ?? '';

if ($action === 'login') {
    $user = $input['username'] ?? '';
    $pass = $input['password'] ?? '';
    
    if (empty($user) || empty($pass)) {
        echo json_encode(['success' => false, 'message' => 'Username and password required']);
        exit;
    }
    
    $stmt = $pdo->prepare("SELECT * FROM ad_members WHERE username = ?");
    $stmt->execute([$user]);
    $member = $stmt->fetch();
    
    if ($member && password_verify($pass, $member['password_hash'])) {
        // Update last login
        $updateStmt = $pdo->prepare("UPDATE ad_members SET last_login = NOW() WHERE username = ?");
        $updateStmt->execute([$user]);
        
        echo json_encode([
            'success' => true, 
            'user' => [
                'username' => $member['username'],
                'pythoncoin_address' => $member['pythoncoin_address'],
                'exp' => (float)$member['exp'],
                'total_clicks' => (int)$member['total_clicks'],
                'created_at' => $member['created_at']
            ]
        ]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
    }
    
} elseif ($action === 'register') {
    $user = $input['username'] ?? '';
    $pass = $input['password'] ?? '';
    $addr = $input['pythoncoin_address'] ?? '';
    
    if (empty($user) || empty($pass) || empty($addr)) {
        echo json_encode(['success' => false, 'message' => 'All fields are required']);
        exit;
    }
    
    $hash = password_hash($pass, PASSWORD_DEFAULT);
    
    try {
        $stmt = $pdo->prepare("INSERT INTO ad_members (username, password_hash, pythoncoin_address) VALUES (?, ?, ?)");
        $stmt->execute([$user, $hash, $addr]);
        
        echo json_encode(['success' => true, 'message' => 'Registration successful']);
    } catch(PDOException $e) {
        if ($e->getCode() == '23000') {
            echo json_encode(['success' => false, 'message' => 'Username already exists']);
        } else {
            echo json_encode(['success' => false, 'message' => 'Registration failed']);
        }
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Invalid action']);
}
?>