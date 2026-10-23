<?php
// Simple test script to verify click and view recording functionality
session_start();

// Include the main dashboard file to reuse functions
require_once 'dashboard8.php';

// Test database connection
$pdo = getDatabase();
if (!$pdo) {
    die("ERROR: Could not connect to database\n");
}

echo "Testing Click and View Recording Functions...\n\n";

// Test 1: Check if required tables exist
$tables_to_check = ['ad_clicks', 'developers', 'ads_cache'];
foreach ($tables_to_check as $table) {
    try {
        $stmt = $pdo->query("SELECT 1 FROM $table LIMIT 1");
        echo "✓ Table '$table' exists\n";
    } catch (PDOException $e) {
        echo "✗ Table '$table' does not exist: " . $e->getMessage() . "\n";
    }
}

// Test 2: Check if columns exist in ad_clicks table
try {
    $stmt = $pdo->query("SHOW COLUMNS FROM ad_clicks LIKE 'click_time'");
    $result = $stmt->fetch();
    if ($result) {
        echo "✓ Column 'click_time' exists in ad_clicks table\n";
    } else {
        echo "✗ Column 'click_time' does not exist in ad_clicks table\n";
    }
} catch (PDOException $e) {
    echo "✗ Error checking columns: " . $e->getMessage() . "\n";
}

// Test 3: Check if columns exist in ads_cache table
try {
    $stmt = $pdo->query("SHOW COLUMNS FROM ads_cache LIKE 'click_count'");
    $result = $stmt->fetch();
    if ($result) {
        echo "✓ Column 'click_count' exists in ads_cache table\n";
    } else {
        echo "✗ Column 'click_count' does not exist in ads_cache table\n";
    }
    
    $stmt = $pdo->query("SHOW COLUMNS FROM ads_cache LIKE 'impression_count'");
    $result = $stmt->fetch();
    if ($result) {
        echo "✓ Column 'impression_count' exists in ads_cache table\n";
    } else {
        echo "✗ Column 'impression_count' does not exist in ads_cache table\n";
    }
} catch (PDOException $e) {
    echo "✗ Error checking ads_cache columns: " . $e->getMessage() . "\n";
}

// Test 4: Simulate a click recording if we have a developer
if (isset($_SESSION['developer'])) {
    $developer = getDeveloperByUsername($_SESSION['developer']['username']);
    if ($developer) {
        echo "\nTesting click recording for developer: " . $developer['username'] . "\n";
        
        // Simulate recording a click
        $success = recordAdClick($developer['id'], 'test_ad_123', 'test_client_456', 'test_zone', 0.001);
        if ($success) {
            echo "✓ Click recording successful\n";
            
            // Update developer totals
            $stmt = $pdo->prepare("UPDATE developers SET total_clicks = total_clicks + 1, total_earned = total_earned + ? WHERE id = ?");
            $stmt->execute([0.001, $developer['id']]);
            echo "✓ Developer totals updated\n";
        } else {
            echo "✗ Click recording failed\n";
        }
    } else {
        echo "\nNo authenticated developer found. Please log in first.\n";
    }
} else {
    echo "\nNo authenticated developer found. Please log in first.\n";
}

echo "\nTest completed.\n";
?>