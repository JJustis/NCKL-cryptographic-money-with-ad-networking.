<?php
/**
 * Ad Click Verification System
 * Ensures correct payout amounts are recorded for ad clicks
 */

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
        return null;
    }
}

function verifyClickPayouts() {
    $pdo = getDatabase();
    if (!$pdo) return ['success' => false, 'error' => 'Database connection failed'];
    
    $results = [
        'total_clicks' => 0,
        'verified_clicks' => 0,
        'storage_clicks' => 0,
        'live_clicks' => 0,
        'incorrect_payouts' => 0,
        'issues' => []
    ];
    
    try {
        // Get all ad clicks with details
        $stmt = $pdo->prepare("
            SELECT ac.*, d.username 
            FROM ad_clicks ac 
            LEFT JOIN developers d ON ac.developer_id = d.id 
            ORDER BY ac.click_time DESC 
            LIMIT 100
        ");
        $stmt->execute();
        $clicks = $stmt->fetchAll();
        
        $results['total_clicks'] = count($clicks);
        
        foreach ($clicks as $click) {
            $ad_id = $click['ad_id'];
            $payout = (float)$click['payout_amount'];
            $is_view = strpos($ad_id, '_view') !== false;
            
            // Skip view events (they should have 0 payout)
            if ($is_view) {
                if ($payout == 0) {
                    $results['verified_clicks']++;
                } else {
                    $results['issues'][] = "View event {$click['id']} has non-zero payout: {$payout}";
                    $results['incorrect_payouts']++;
                }
                continue;
            }
            
            // Determine expected payout based on ad source
            $expected_payout = null;
            
            // Check if it's a storage ad
            if (strpos($ad_id, 'storage_') === 0 || $click['client_id'] === 'storage') {
                $expected_payout = 0.0000009;
                $results['storage_clicks']++;
            }
            // Check if it's a live/P2P client ad
            else if (strpos($ad_id, 'live_') === 0 || 
                     $click['client_id'] !== 'storage' && 
                     $click['client_id'] !== '' && 
                     $payout > 0) {
                $expected_payout = 0.000005; // Default live rate
                $results['live_clicks']++;
            }
            
            // Verify payout amount
            if ($expected_payout !== null) {
                $tolerance = 0.0000001; // Small tolerance for floating point comparison
                
                if (abs($payout - $expected_payout) < $tolerance) {
                    $results['verified_clicks']++;
                } else {
                    $results['issues'][] = "Click {$click['id']} ({$ad_id}): Expected {$expected_payout}, got {$payout}";
                    $results['incorrect_payouts']++;
                }
            } else {
                // Unknown ad type - flag for manual review
                if ($payout > 0) {
                    $results['issues'][] = "Click {$click['id']} ({$ad_id}): Unknown ad type with payout {$payout}";
                    $results['incorrect_payouts']++;
                } else {
                    $results['verified_clicks']++;
                }
            }
        }
        
        $results['success'] = true;
        $results['verification_rate'] = $results['total_clicks'] > 0 ? 
            round(($results['verified_clicks'] / $results['total_clicks']) * 100, 2) : 0;
        
        return $results;
        
    } catch (Exception $e) {
        return ['success' => false, 'error' => $e->getMessage()];
    }
}

function fixIncorrectPayouts() {
    $pdo = getDatabase();
    if (!$pdo) return ['success' => false, 'error' => 'Database connection failed'];
    
    $fixes = [
        'storage_ads_fixed' => 0,
        'live_ads_fixed' => 0,
        'views_fixed' => 0,
        'total_fixed' => 0
    ];
    
    try {
        // Fix storage ads with incorrect payouts
        $stmt = $pdo->prepare("
            UPDATE ad_clicks 
            SET payout_amount = 0.0000009 
            WHERE (ad_id LIKE 'storage_%' OR client_id = 'storage') 
            AND ad_id NOT LIKE '%_view' 
            AND payout_amount != 0.0000009
        ");
        $stmt->execute();
        $fixes['storage_ads_fixed'] = $stmt->rowCount();
        
        // Fix view events with non-zero payouts
        $stmt = $pdo->prepare("
            UPDATE ad_clicks 
            SET payout_amount = 0 
            WHERE ad_id LIKE '%_view' 
            AND payout_amount != 0
        ");
        $stmt->execute();
        $fixes['views_fixed'] = $stmt->rowCount();
        
        // Fix live ads with storage rates (be careful here)
        $stmt = $pdo->prepare("
            UPDATE ad_clicks 
            SET payout_amount = 0.000005 
            WHERE ad_id LIKE 'live_%' 
            AND ad_id NOT LIKE '%_view' 
            AND payout_amount != 0.000005
        ");
        $stmt->execute();
        $fixes['live_ads_fixed'] = $stmt->rowCount();
        
        $fixes['total_fixed'] = $fixes['storage_ads_fixed'] + $fixes['views_fixed'] + $fixes['live_ads_fixed'];
        $fixes['success'] = true;
        
        return $fixes;
        
    } catch (Exception $e) {
        return ['success' => false, 'error' => $e->getMessage()];
    }
}

// Handle AJAX requests
if (isset($_GET['action'])) {
    header('Content-Type: application/json');
    
    switch ($_GET['action']) {
        case 'verify':
            echo json_encode(verifyClickPayouts());
            break;
            
        case 'fix':
            echo json_encode(fixIncorrectPayouts());
            break;
            
        default:
            echo json_encode(['success' => false, 'error' => 'Unknown action']);
    }
    exit;
}

// HTML Interface
?>
<!DOCTYPE html>
<html>
<head>
    <title>Ad Click Verification System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background-color: #0056b3; }
        .fix-button { background-color: #dc3545; }
        .fix-button:hover { background-color: #c82333; }
        .results { margin-top: 20px; }
        .issue { background-color: #f8f9fa; padding: 5px; margin: 2px 0; border-left: 3px solid #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ad Click Verification System</h1>
        <p>This tool verifies that ad clicks are recording the correct payout amounts based on their source.</p>
        
        <div>
            <button class="button" onclick="verifyClicks()">🔍 Verify Ad Clicks</button>
            <button class="button fix-button" onclick="fixClicks()">🔧 Fix Incorrect Payouts</button>
        </div>
        
        <div id="results" class="results"></div>
    </div>
    
    <script>
        function verifyClicks() {
            document.getElementById('results').innerHTML = '<div class="status">🔄 Verifying ad clicks...</div>';
            
            fetch('?action=verify')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let html = '<div class="status success">';
                        html += '<h3>Verification Results</h3>';
                        html += `<p><strong>Total Clicks:</strong> ${data.total_clicks}</p>`;
                        html += `<p><strong>Verified Clicks:</strong> ${data.verified_clicks}</p>`;
                        html += `<p><strong>Storage Clicks:</strong> ${data.storage_clicks}</p>`;
                        html += `<p><strong>Live Clicks:</strong> ${data.live_clicks}</p>`;
                        html += `<p><strong>Incorrect Payouts:</strong> ${data.incorrect_payouts}</p>`;
                        html += `<p><strong>Verification Rate:</strong> ${data.verification_rate}%</p>`;
                        html += '</div>';
                        
                        if (data.issues.length > 0) {
                            html += '<div class="status warning"><h3>Issues Found:</h3>';
                            data.issues.forEach(issue => {
                                html += `<div class="issue">${issue}</div>`;
                            });
                            html += '</div>';
                        }
                        
                        document.getElementById('results').innerHTML = html;
                    } else {
                        document.getElementById('results').innerHTML = 
                            `<div class="status error">Error: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = 
                        `<div class="status error">Network error: ${error.message}</div>`;
                });
        }
        
        function fixClicks() {
            if (!confirm('This will automatically fix incorrect payout amounts. Continue?')) {
                return;
            }
            
            document.getElementById('results').innerHTML = '<div class="status">🔧 Fixing incorrect payouts...</div>';
            
            fetch('?action=fix')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let html = '<div class="status success">';
                        html += '<h3>Fix Results</h3>';
                        html += `<p><strong>Storage Ads Fixed:</strong> ${data.storage_ads_fixed}</p>`;
                        html += `<p><strong>Live Ads Fixed:</strong> ${data.live_ads_fixed}</p>`;
                        html += `<p><strong>View Events Fixed:</strong> ${data.views_fixed}</p>`;
                        html += `<p><strong>Total Fixed:</strong> ${data.total_fixed}</p>`;
                        html += '</div>';
                        
                        document.getElementById('results').innerHTML = html;
                    } else {
                        document.getElementById('results').innerHTML = 
                            `<div class="status error">Error: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = 
                        `<div class="status error">Network error: ${error.message}</div>`;
                });
        }
    </script>
</body>
</html>