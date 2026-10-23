<?php
require_once 'dashboard8.php';

echo "<h1>Testing scanActiveAdsStorage() Function</h1>";

$ads = scanActiveAdsStorage();

echo "<h2>Found " . count($ads) . " ads:</h2>";

if (empty($ads)) {
    echo "<p>❌ No ads returned from scanActiveAdsStorage()!</p>";
} else {
    echo "<div style='margin: 20px 0;'>";
    foreach ($ads as $ad) {
        echo "<div style='border: 1px solid #ccc; margin: 10px; padding: 10px; background: #f9f9f9;'>";
        echo "<h3>" . htmlspecialchars($ad['title']) . "</h3>";
        echo "<p><strong>ID:</strong> " . htmlspecialchars($ad['id']) . "</p>";
        echo "<p><strong>Type:</strong> " . htmlspecialchars($ad['ad_type'] ?? 'unknown') . "</p>";
        echo "<p><strong>Format:</strong> " . htmlspecialchars($ad['format'] ?? 'unknown') . "</p>";
        echo "<p><strong>Description:</strong> " . htmlspecialchars($ad['description']) . "</p>";
        echo "<p><strong>Payout:</strong> " . htmlspecialchars($ad['payout_amount']) . "</p>";
        if (isset($ad['svg_url'])) {
            echo "<p><strong>SVG URL:</strong> " . htmlspecialchars($ad['svg_url']) . "</p>";
        }
        if (isset($ad['html_url'])) {
            echo "<p><strong>HTML URL:</strong> " . htmlspecialchars($ad['html_url']) . "</p>";
        }
        echo "</div>";
    }
    echo "</div>";
}
?>