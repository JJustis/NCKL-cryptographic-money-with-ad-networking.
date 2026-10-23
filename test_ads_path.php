<?php
// Test script to check ads_storage path detection
echo "<h1>Testing Ads Storage Path Detection</h1>";

// Try the same paths as the dashboard
$possiblePaths = [
    realpath(dirname(__FILE__) . '/../livepy/pythoncoin/ads_storage/active'),
    realpath(dirname(__FILE__) . '/../../pythoncoin/ads_storage/active'),
    realpath(dirname(__FILE__) . '/ads_storage/active'),
    realpath('./ads_storage/active'),
    realpath('../ads_storage/active'),
    realpath('/livepy/pythoncoin/ads_storage/active'),
    realpath($_SERVER['DOCUMENT_ROOT'] . '/../livepy/pythoncoin/ads_storage/active'),
    realpath($_SERVER['DOCUMENT_ROOT'] . '/livepy/pythoncoin/ads_storage/active')
];

echo "<h2>Current directory: " . getcwd() . "</h2>";
echo "<h2>Script directory: " . dirname(__FILE__) . "</h2>";
echo "<h2>Document root: " . $_SERVER['DOCUMENT_ROOT'] . "</h2>";

echo "<h2>Testing paths:</h2>";
$adsPath = null;
foreach ($possiblePaths as $i => $path) {
    $exists = $path && is_dir($path);
    echo "<p>Path $i: <code>$path</code> - " . ($exists ? "✅ EXISTS" : "❌ Not found") . "</p>";
    
    if ($exists && !$adsPath) {
        $adsPath = $path;
        echo "<p><strong>Using this path: $adsPath</strong></p>";
        
        // List files in this directory
        $files = scandir($adsPath);
        echo "<h3>Files in ads_storage/active:</h3><ul>";
        foreach ($files as $file) {
            if ($file !== '.' && $file !== '..') {
                echo "<li>$file</li>";
            }
        }
        echo "</ul>";
    }
}

if (!$adsPath) {
    echo "<p><strong>❌ No valid ads_storage path found!</strong></p>";
}
?>