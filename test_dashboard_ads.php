<?php
// Simple test to check if dashboard can find ads from storage
require_once 'dashboard8.php';

echo "<h1>Testing Dashboard Ad Discovery</h1>";

$ads = scanActiveAdsStorage();

echo "<h2>Found " . count($ads) . " ads:</h2>";

if (empty($ads)) {
    echo "<p>No ads found!</p>";
    
    // Let's check the directory manually
    $adsPath = realpath('./ads_storage/active');
    if ($adsPath && is_dir($adsPath)) {
        echo "<h3>Files in ads_storage/active:</h3>";
        $files = scandir($adsPath);
        foreach ($files as $file) {
            if ($file !== '.' && $file !== '..') {
                echo "<li>$file</li>";
            }
        }
    } else {
        echo "<p>Could not find ads_storage/active directory</p>";
    }
} else {
    foreach ($ads as $ad) {
        echo "<div style='border: 1px solid #ccc; margin: 10px; padding: 10px;'>";
        echo "<h3>" . htmlspecialchars($ad['title']) . "</h3>";
        echo "<p>ID: " . htmlspecialchars($ad['id']) . "</p>";
        echo "<p>Type: " . htmlspecialchars($ad['ad_type']) . "</p>";
        echo "<p>Description: " . htmlspecialchars($ad['description']) . "</p>";
        echo "<p>Payout: " . htmlspecialchars($ad['payout_amount']) . "</p>";
        if (isset($ad['svg_url'])) {
            echo "<p>SVG URL: " . htmlspecialchars($ad['svg_url']) . "</p>";
        }
        if (isset($ad['html_url'])) {
            echo "<p>HTML URL: " . htmlspecialchars($ad['html_url']) . "</p>";
        }
        echo "</div>";
    }
}
?>