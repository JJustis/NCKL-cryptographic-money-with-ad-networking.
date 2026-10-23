<?php
// Debug script to test click recording
session_start();

// Database connection
function getDatabase() {
    try {
        $pdo = new PDO(
            "mysql:host=localhost;dbname=adnetwrk;charset=utf8mb4",
            'root',
            '',
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]
        );
        return $pdo;
    } catch (PDOException $e) {
        echo "Database connection failed: " . $e->getMessage();
        return null;
    }
}

function getDeveloperByUsername($username) {
    $pdo = getDatabase();
    if (!$pdo) return null;
    
    $stmt = $pdo->prepare("SELECT * FROM developers WHERE username = ?");
    $stmt->execute([$username]);
    return $stmt->fetch();
}

function recordAdClick($developerId, $adId, $clientId, $zone, $payoutAmount) {
    echo "DEBUG: Recording click - Developer: $developerId, Ad: $adId, Payout: $payoutAmount\n";
    
    $pdo = getDatabase();
    if (!$pdo) return false;
    
    try {
        $stmt = $pdo->prepare("
            INSERT INTO ad_clicks (developer_id, ad_id, client_id, zone, payout_amount, ip_address, user_agent) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ");
        $result = $stmt->execute([
            $developerId, $adId, $clientId, $zone, $payoutAmount,
            $_SERVER['REMOTE_ADDR'] ?? 'debug', $_SERVER['HTTP_USER_AGENT'] ?? 'Debug Script'
        ]);
        
        if ($result) {
            echo "DEBUG: Click recorded successfully!\n";
        } else {
            echo "DEBUG: Click recording failed!\n";
        }
        
        return $result;
    } catch (PDOException $e) {
        echo "DEBUG: Error - " . $e->getMessage() . "\n";
        return false;
    }
}

echo "=== PyCoin Click Recording Debug ===\n";

// Check if developer session exists
if (isset($_SESSION['developer'])) {
    echo "Developer session found: " . $_SESSION['developer']['username'] . "\n";
} else {
    echo "No developer session found!\n";
    echo "Setting up test session...\n";
    
    // Get a developer for testing
    $developer = getDeveloperByUsername('Admin');
    if ($developer) {
        $_SESSION['developer'] = [
            'id' => $developer['id'],
            'username' => $developer['username'],
            'pythoncoin_address' => $developer['pythoncoin_address']
        ];
        echo "Test session created for: " . $developer['username'] . "\n";
    } else {
        echo "No Admin developer found!\n";
        exit;
    }
}

// Test different payout scenarios
echo "\n=== Testing Payout Recording ===\n";

$testCases = [
    ['storage_ad_test', 'storage', 0.0000009, 'Storage ad test'],
    ['live_ad_test', 'live_client', 0.000005, 'Live ad test'],
    ['custom_ad_test', 'custom_client', 0.123456789, 'Custom amount test']
];

foreach ($testCases as $test) {
    echo "\n--- Testing: {$test[3]} ---\n";
    
    $developer = getDeveloperByUsername($_SESSION['developer']['username']);
    if ($developer) {
        $success = recordAdClick(
            $developer['id'], 
            $test[0], 
            $test[1], 
            'debug_zone', 
            $test[2]
        );
        
        if ($success) {
            echo "✅ Test passed - {$test[2]} PYC recorded\n";
        } else {
            echo "❌ Test failed\n";
        }
    }
}

// Check what was actually recorded
echo "\n=== Checking Database Results ===\n";

$pdo = getDatabase();
$stmt = $pdo->prepare("
    SELECT ac.*, d.username 
    FROM ad_clicks ac 
    LEFT JOIN developers d ON ac.developer_id = d.id 
    WHERE ac.ip_address = 'debug' 
    ORDER BY ac.click_time DESC 
    LIMIT 5
");
$stmt->execute();
$results = $stmt->fetchAll();

foreach ($results as $result) {
    echo "Click ID: {$result['id']}, Ad: {$result['ad_id']}, Payout: {$result['payout_amount']}, Dev: {$result['username']}\n";
}

echo "\n=== Debug Complete ===\n";
?>