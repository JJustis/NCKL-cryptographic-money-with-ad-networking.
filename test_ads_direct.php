<?php
// Direct test of scanActiveAdsStorage function without including full dashboard
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>Direct Test of Ad Storage Function</h1>";

// Define the function directly here for testing
function scanActiveAdsStorage() {
    // Try multiple possible paths for the ads_storage directory
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
    
    $adsPath = null;
    foreach ($possiblePaths as $path) {
        if ($path && is_dir($path)) {
            $adsPath = $path;
            error_log("Found ads storage at: $adsPath");
            break;
        }
    }
    
    if (!$adsPath) {
        error_log("Ads storage path not found. Tried: " . implode(', ', array_filter($possiblePaths)));
        return [];
    }
    
    $ads = [];
    $files = scandir($adsPath);
    
    if (!$files) {
        error_log("Could not scan ads storage directory: $adsPath");
        return [];
    }
    
    // Group files by ad ID - Enhanced to support multiple ad types
    $adGroups = [];
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') continue;
        
        // Extract ad ID from filename - support for different ad types
        if (preg_match('/^(.+)_(svg|html|meta|video|image|text)\.(svg|html|json|mp4|jpg|jpeg|png|gif|txt)$/', $file, $matches)) {
            $adId = $matches[1];
            $fileType = $matches[2];
            
            if (!isset($adGroups[$adId])) {
                $adGroups[$adId] = [];
            }
            
            $adGroups[$adId][$fileType] = $file;
        }
    }
    
    echo "<h2>Found " . count($adGroups) . " ad groups</h2>";
    
    // Process ads based on available files
    foreach ($adGroups as $adId => $files) {
        echo "<h3>Processing ad: $adId</h3>";
        echo "<p>Files: " . implode(', ', array_keys($files)) . "</p>";
        
        // All ads require a meta file
        if (!isset($files['meta'])) {
            echo "<p>❌ Skipping - no meta file</p>";
            continue;
        }
        
        $metaFile = $adsPath . '/' . $files['meta'];
        if (!file_exists($metaFile)) {
            echo "<p>❌ Skipping - meta file doesn't exist</p>";
            continue;
        }
        
        // Read metadata first to determine the ad type and format
        $metaContent = file_get_contents($metaFile);
        $metadata = json_decode($metaContent, true);
        
        if (!$metadata || !is_array($metadata)) {
            echo "<p>❌ Skipping - invalid metadata JSON</p>";
            continue;
        }
        
        // Determine ad type from metadata first, then check for required files
        $adType = $metadata['ad_type'] ?? 'unknown';
        $format = $metadata['format'] ?? 'unknown';
        
        echo "<p>Ad type: $adType, Format: $format</p>";
        
        $hasRequiredFiles = false;
        
        // Check if we have the required content file based on format
        if ($format === 'html' && isset($files['html'])) {
            $hasRequiredFiles = true;
            echo "<p>✅ Found required HTML file</p>";
        } elseif ($format === 'svg' && isset($files['svg'])) {
            $hasRequiredFiles = true;
            echo "<p>✅ Found required SVG file</p>";
        } elseif ($format === 'video' && isset($files['video'])) {
            $hasRequiredFiles = true;
            echo "<p>✅ Found required video file</p>";
        } elseif ($format === 'image' && isset($files['image'])) {
            $hasRequiredFiles = true;
            echo "<p>✅ Found required image file</p>";
        } elseif ($format === 'text' && isset($files['text'])) {
            $hasRequiredFiles = true;
            echo "<p>✅ Found required text file</p>";
        } elseif (isset($files['html']) || isset($files['svg'])) {
            // Fallback: if we have either HTML or SVG, consider it valid
            $hasRequiredFiles = true;
            echo "<p>✅ Found fallback HTML/SVG file</p>";
        }
        
        if ($hasRequiredFiles) {
            // Check if ad is active
            $expiresAt = $metadata['expires_at'] ?? null;
            $status = $metadata['status'] ?? 'active';
            
            if ($status === 'active' && (!$expiresAt || strtotime($expiresAt) > time())) {
                echo "<p>✅ Ad is active and not expired</p>";
                
                $ads[] = [
                    'id' => $adId,
                    'title' => $metadata['title'] ?? 'Untitled Ad',
                    'format' => $format,
                    'ad_type' => $adType
                ];
            } else {
                echo "<p>❌ Ad is not active or expired</p>";
            }
        } else {
            echo "<p>❌ Missing required content files for format: $format</p>";
        }
    }
    
    return $ads;
}

$ads = scanActiveAdsStorage();

echo "<h2>Final Result: " . count($ads) . " ads found</h2>";

foreach ($ads as $ad) {
    echo "<div style='border: 1px solid #ccc; margin: 10px; padding: 10px;'>";
    echo "<h3>" . htmlspecialchars($ad['title']) . "</h3>";
    echo "<p>ID: " . htmlspecialchars($ad['id']) . "</p>";
    echo "<p>Type: " . htmlspecialchars($ad['ad_type']) . "</p>";
    echo "<p>Format: " . htmlspecialchars($ad['format']) . "</p>";
    echo "</div>";
}
?>