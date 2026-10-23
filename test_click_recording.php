<?php
// Test script to simulate ad click recording
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

// Get developer function
function getDeveloperByUsername($username) {
    $pdo = getDatabase();
    if (!$pdo) return null;
    
    $stmt = $pdo->prepare("SELECT * FROM developers WHERE username = ?");
    $stmt->execute([$username]);
    return $stmt->fetch();
}

// Record ad click function
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
        echo "Record ad click error: " . $e->getMessage() . "\n";
        return false;
    }
}

echo "Testing ad click recording...\n";

// Get a test developer
$developer = getDeveloperByUsername('Admin');
if (!$developer) {
    echo "No Admin developer found!\n";
    exit;
}

echo "Found developer: " . $developer['username'] . " (ID: " . $developer['id'] . ")\n";

// Get an ad from ads_cache to get the real payout amount
$pdo = getDatabase();
$stmt = $pdo->prepare("SELECT * FROM ads_cache LIMIT 1");
$stmt->execute();
$ad = $stmt->fetch();

if (!$ad) {
    echo "No ads found in ads_cache!\n";
    exit;
}

echo "Found ad: " . $ad['ad_id'] . " with payout: " . $ad['payout_amount'] . "\n";

// Test recording a real click (not a view)
$success = recordAdClick(
    $developer['id'], 
    $ad['ad_id'] . '_REAL_CLICK', // Mark it as a real click
    $ad['client_id'], 
    'test_zone', 
    $ad['payout_amount']  // Use the real payout amount
);

if ($success) {
    echo "✅ Successfully recorded click with payout: " . $ad['payout_amount'] . "\n";
    
    // Verify the record
    $stmt = $pdo->prepare("SELECT * FROM ad_clicks ORDER BY click_time DESC LIMIT 1");
    $stmt->execute();
    $lastClick = $stmt->fetch();
    
    echo "Last recorded click:\n";
    echo "  ID: " . $lastClick['id'] . "\n";
    echo "  Ad ID: " . $lastClick['ad_id'] . "\n";
    echo "  Payout: " . $lastClick['payout_amount'] . "\n";
    echo "  Time: " . $lastClick['click_time'] . "\n";
} else {
    echo "❌ Failed to record click\n";
}
?>