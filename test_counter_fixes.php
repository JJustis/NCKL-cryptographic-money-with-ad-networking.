<?php
/**
 * Test script to verify that the counter fixes are working properly
 */

// Test database connection
function testDatabaseConnection() {
    $db_config = [
        'host' => 'localhost',
        'database' => 'adnetwrk',
        'username' => 'root',
        'password' => ''
    ];

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
        
        echo "✅ Database connection successful\n";
        
        // Test a simple query
        $stmt = $pdo->query("SELECT COUNT(*) as count FROM ad_clicks LIMIT 1");
        $result = $stmt->fetch();
        echo "✅ ad_clicks table accessible, row count test successful\n";
        
        return $pdo;
    } catch (Exception $e) {
        echo "❌ Database connection failed: " . $e->getMessage() . "\n";
        return null;
    }
}

// Test the recordAdClick function
function testRecordAdClick($pdo) {
    if (!$pdo) {
        echo "❌ Cannot test recordAdClick without database connection\n";
        return false;
    }
    
    // Create a mock developer for testing
    $testDevStmt = $pdo->prepare("SELECT id FROM developers LIMIT 1");
    $testDevStmt->execute();
    $developer = $testDevStmt->fetch();
    
    if (!$developer) {
        echo "⚠️ No developers found in database, skipping recordAdClick test\n";
        return true;
    }
    
    // Test the recordAdClick function indirectly by calling it
    $developerId = $developer['id'];
    $adId = 'test_ad_' . time();
    $clientId = 'test_client';
    $zone = 'test_zone';
    $payoutAmount = 0.001;
    
    // Since recordAdClick is defined in dashboard8.php, we'll include it to test
    require_once 'dashboard8.php';
    
    $result = recordAdClick($developerId, $adId, $clientId, $zone, $payoutAmount);
    
    if ($result) {
        echo "✅ recordAdClick function working correctly\n";
        
        // Clean up the test record
        $cleanupStmt = $pdo->prepare("DELETE FROM ad_clicks WHERE ad_id = ? AND client_id = ?");
        $cleanupStmt->execute([$adId . '_view', $clientId]); // Note: recordAdClick adds '_view' for views
        
        return true;
    } else {
        echo "❌ recordAdClick function failed\n";
        return false;
    }
}

echo "Testing Counter Fixes...\n";
echo "=====================\n";

$pdo = testDatabaseConnection();
testRecordAdClick($pdo);

echo "\nTest completed. The main fixes applied were:\n";
echo "1. Fixed undefined \$pdo variable in record_click AJAX handler\n";
echo "2. Added missing safeJsonParse function to dashboard JavaScript\n";
echo "3. Updated record_view function to handle developer identification by address\n";
echo "4. Ensured proper database connections in AJAX handlers\n";
?>