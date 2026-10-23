<?php
// cron_jobs.php - Maintenance tasks to run periodically

// Update P2P client statuses
function updateClientStatuses() {
    global $pdo;
    
    // Mark clients as offline if not seen in last 5 minutes
    $stmt = $pdo->prepare("UPDATE p2p_clients SET status = 'offline' WHERE last_seen < DATE_SUB(NOW(), INTERVAL 5 MINUTE) AND status != 'offline'");
    $stmt->execute();
    
    echo "Updated client statuses\n";
}

// Clean old analytics data
function cleanOldAnalytics() {
    global $pdo;
    
    // Remove analytics older than 90 days
    $stmt = $pdo->prepare("DELETE FROM analytics WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY)");
    $stmt->execute();
    
    echo "Cleaned old analytics data\n";
}

// Aggregate daily statistics
function aggregateDailyStats() {
    // This would aggregate user statistics for reporting
    echo "Aggregated daily statistics\n";
}

// Run maintenance tasks
if (php_sapi_name() === 'cli') {
    try {
        $host = 'localhost';
        $dbname = 'adnetwrk';
        $username = 'root';
        $password = '';
        
        $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        updateClientStatuses();
        cleanOldAnalytics();
        aggregateDailyStats();
        
        echo "Maintenance tasks completed\n";
        
    } catch(PDOException $e) {
        echo "Maintenance error: " . $e->getMessage() . "\n";
    }
}
?> register($pdo, $data) {
    $username = trim($data['username'] ?? '');
    $password = $data['password'] ?? '';
    
    if (empty($username) || empty($password)) {
        echo json_encode(['success' => false, 'message' => 'Username and password required']);
        return;
    }
    
    if (strlen($password) < 6) {
        echo json_encode(['success' => false, 'message' => 'Password must be at least 6 characters']);
        return;
    }
    
    // Check if username exists
    $stmt = $pdo->prepare("SELECT username FROM members WHERE username = ?");
    $stmt->execute([$username]);
    
    if ($stmt->fetch()) {
        echo json_encode(['success' => false, 'message' => 'Username already exists']);
        return;
    }
    
    // Create user
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $pdo->prepare("INSERT INTO ad_members (username, password, exp, created_at) VALUES (?, ?, 0, NOW())");
    
    try {
        $stmt->execute([$username, $hashedPassword]);
        
        // Create user directory structure
        $userDir = "users/$username";
        if (!file_exists($userDir)) {
            mkdir($userDir, 0755, true);
        }
        
        // Create subdirectories
        mkdir("$userDir/embeds", 0755, true);
        mkdir("$userDir/analytics", 0755, true);
        mkdir("$userDir/logs", 0755, true);
        
        // Create initial files
        createInitialUserFiles($username, $userDir);
        
        echo json_encode(['success' => true, 'message' => 'Registration successful']);
    } catch(PDOException $e) {
        echo json_encode(['success' => false, 'message' => 'Registration failed']);
    }
}

function createInitialUserFiles($username, $userDir) {
    // Create clicks.xml
    $clicksXml = '<?xml version="1.0" encoding="UTF-8"?>
<clicks>
    <user>' . htmlspecialchars($username) . '</user>
    <total>0</total>
    <created>' . date('c') . '</created>
    <records></records>
</clicks>';
    file_put_contents("$userDir/clicks.xml", $clicksXml);
    
    // Create embeds.json
    $embedsData = [
        'user' => $username,
        'created' => date('c'),
        'embeds' => []
    ];
    file_put_contents("$userDir/embeds.json", json_encode($embedsData, JSON_PRETTY_PRINT));
    
    // Create analytics.json
    $analyticsData = [
        'user' => $username,
        'created' => date('c'),
        'stats' => [
            'total_clicks' => 0,
            'total_impressions' => 0,
            'total_exp' => 0,
            'embeds_created' => 0
        ],
        'daily_stats' => []
    ];
    file_put_contents("$userDir/analytics.json", json_encode($analyticsData, JSON_PRETTY_PRINT));
}

function login($pdo, $data) {
    $username = trim($data['username'] ?? '');
    $password = $data['password'] ?? '';
    
    if (empty($username) || empty($password)) {
        echo json_encode(['success' => false, 'message' => 'Username and password required']);
        return;
    }
    
    $stmt = $pdo->prepare("SELECT username, password, exp, created_at FROM ad_members WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($user && password_verify($password, $user['password'])) {
        unset($user['password']);
        
        // Update last login
        $updateStmt = $pdo->prepare("UPDATE ad_members SET last_login = NOW() WHERE username = ?");
        $updateStmt->execute([$username]);
        
        echo json_encode(['success' => true, 'user' => $user]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
    }
}
?>

