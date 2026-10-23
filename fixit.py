#!/usr/bin/env python3
"""
Fixed Multi-File Injector Script for PythonCoin P2P Ad Network
Edits PHP backend, HTML portal, and PyQt client for automatic database registration
"""

import os
import re
import json
import time
from datetime import datetime

class NetworkInjector:
    def __init__(self):
        self.modifications_made = []
        self.backup_suffix = f".backup_{int(time.time())}"
        
    def backup_file(self, filepath):
        """Create backup of file before modification"""
        if os.path.exists(filepath):
            backup_path = filepath + self.backup_suffix
            with open(filepath, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
            print(f"📁 Backed up {filepath} to {backup_path}")
            return backup_path
        return None
    
    def inject_enhanced_api_php(self):
        """Inject enhanced API functionality for real-time client registration"""
        api_content = '''<?php
// Enhanced API with Real-Time Client Registration
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$config = include 'config.php';
$host = $config['database']['host'];
$dbname = $config['database']['dbname'];
$username = $config['database']['username'];
$password = $config['database']['password'];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    error_log("Database connection failed: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed']);
    exit;
}

// Parse input
$input = json_decode(file_get_contents('php://input'), true);
$action = $input['action'] ?? ($_GET['action'] ?? '');

// Route requests
switch($action) {
    case 'client_register_live':
        clientRegisterLive($pdo, $input);
        break;
    case 'client_update_status':
        clientUpdateStatus($pdo, $input);
        break;
    case 'client_shutdown':
        clientShutdown($pdo, $input);
        break;
    case 'get_live_clients':
        getLiveClients($pdo);
        break;
    case 'client_heartbeat':
        clientHeartbeat($pdo, $input);
        break;
    case 'update_client_ads':
        updateClientAds($pdo, $input);
        break;
    case 'record_click':
        recordClick($pdo, $input);
        break;
    case 'process_payments':
        processPayments($pdo, $input);
        break;
    case 'get_advertisers':
        getAdvertisers($pdo);
        break;
    case 'get_user_stats':
        getUserStats($pdo, $_GET['username'] ?? '');
        break;
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid action']);
}

function clientRegisterLive($pdo, $data) {
    $clientId = $data['client_id'] ?? '';
    $username = $data['username'] ?? '';
    $walletAddress = $data['wallet_address'] ?? '';
    $clientName = $data['client_name'] ?? '';
    $host = $data['host'] ?? $_SERVER['REMOTE_ADDR'];
    $port = $data['port'] ?? 8082;
    $version = $data['version'] ?? '1.0';
    $capabilities = $data['capabilities'] ?? [];
    $adInventory = $data['ad_inventory'] ?? [];
    $metadata = $data['metadata'] ?? [];
    
    if (empty($clientId) || empty($username) || empty($walletAddress)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Missing required fields']);
        return;
    }
    
    try {
        $pdo->beginTransaction();
        
        // Register/update client
        $stmt = $pdo->prepare("
            INSERT INTO p2p_clients 
            (client_id, name, host, port, username, wallet_address, status, version, 
             capabilities, metadata, ad_count, last_seen, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, 'online', ?, ?, ?, ?, NOW(), NOW())
            ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            host = VALUES(host),
            port = VALUES(port),
            wallet_address = VALUES(wallet_address),
            status = 'online',
            version = VALUES(version),
            capabilities = VALUES(capabilities),
            metadata = VALUES(metadata),
            ad_count = VALUES(ad_count),
            last_seen = NOW()
        ");
        
        $stmt->execute([
            $clientId, $clientName, $host, $port, $username, $walletAddress,
            $version, json_encode($capabilities), json_encode($metadata), count($adInventory)
        ]);
        
        // Update client ads inventory
        if (!empty($adInventory)) {
            // Clear existing ads for this client
            $stmt = $pdo->prepare("DELETE FROM client_ads WHERE client_id = ?");
            $stmt->execute([$clientId]);
            
            // Insert new ads
            $stmt = $pdo->prepare("
                INSERT INTO client_ads (client_id, ad_id, title, description, category, 
                                      payout_rate, click_url, image_url, targeting_tags, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ");
            
            foreach ($adInventory as $ad) {
                $stmt->execute([
                    $clientId, $ad['ad_id'], $ad['title'], $ad['description'],
                    $ad['category'], $ad['payout_rate'], $ad['click_url'],
                    $ad['image_url'] ?? '', json_encode($ad['targeting_tags'] ?? []),
                    $ad['active'] ?? true
                ]);
            }
        }
        
        // Log registration event
        $stmt = $pdo->prepare("
            INSERT INTO analytics (username, event_type, client_id, data, created_at)
            VALUES (?, 'client_registered', ?, ?, NOW())
        ");
        $stmt->execute([$username, $clientId, json_encode($data)]);
        
        $pdo->commit();
        
        echo json_encode([
            'success' => true,
            'message' => 'Client registered successfully',
            'client_id' => $clientId,
            'registered_at' => date('c')
        ]);
        
    } catch(PDOException $e) {
        $pdo->rollBack();
        error_log("Client registration failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Registration failed']);
    }
}

function getLiveClients($pdo) {
    try {
        $stmt = $pdo->prepare("
            SELECT c.*, 
                   COUNT(ca.id) as actual_ad_count,
                   TIMESTAMPDIFF(SECOND, c.last_seen, NOW()) as seconds_since_seen
            FROM p2p_clients c
            LEFT JOIN client_ads ca ON c.client_id = ca.client_id AND ca.active = 1
            WHERE c.status = 'online' 
            AND c.last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            GROUP BY c.client_id
            ORDER BY c.last_seen DESC
        ");
        $stmt->execute();
        $clients = $stmt->fetchAll();
        
        // Enrich with real-time data
        foreach ($clients as &$client) {
            $client['uptime'] = formatUptime($client['seconds_since_seen']);
            $client['capabilities'] = json_decode($client['capabilities'] ?? '[]', true);
            $client['stats'] = json_decode($client['stats'] ?? '{}', true);
            $client['metadata'] = json_decode($client['metadata'] ?? '{}', true);
        }
        
        echo json_encode([
            'success' => true,
            'clients' => $clients,
            'total_count' => count($clients),
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        error_log("Get live clients failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to get clients']);
    }
}

function clientHeartbeat($pdo, $data) {
    $clientId = $data['client_id'] ?? ($_GET['client_id'] ?? '');
    
    if (empty($clientId)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Client ID required']);
        return;
    }
    
    try {
        $stmt = $pdo->prepare("
            UPDATE p2p_clients 
            SET last_seen = NOW(), status = 'online'
            WHERE client_id = ?
        ");
        $stmt->execute([$clientId]);
        
        if ($stmt->rowCount() > 0) {
            echo json_encode([
                'success' => true,
                'heartbeat_received' => true,
                'server_time' => date('c')
            ]);
        } else {
            http_response_code(404);
            echo json_encode(['success' => false, 'message' => 'Client not found']);
        }
        
    } catch(PDOException $e) {
        error_log("Heartbeat failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Heartbeat failed']);
    }
}

function recordClick($pdo, $data) {
    $username = $data['username'] ?? $data['developer'] ?? '';
    $adId = $data['ad_id'] ?? '';
    $clientId = $data['client_id'] ?? '';
    $embedId = $data['embed_id'] ?? '';
    $zone = $data['zone'] ?? '';
    $ipAddress = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';
    $pycEarned = $data['pyc_earned'] ?? 0.002;
    
    if (empty($username) || empty($adId)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Username and ad_id required']);
        return;
    }
    
    try {
        $pdo->beginTransaction();
        
        // Record click
        $stmt = $pdo->prepare("
            INSERT INTO ad_clicks (username, ad_id, embed_id, client_id, zone, 
                                 ip_address, user_agent, pyc_earned, payment_processed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE)
        ");
        $stmt->execute([$username, $adId, $embedId, $clientId, $zone, $ipAddress, $userAgent, $pycEarned]);
        $clickId = $pdo->lastInsertId();
        
        // Update user stats
        $stmt = $pdo->prepare("
            UPDATE ad_members 
            SET total_clicks = total_clicks + 1, last_login = NOW()
            WHERE username = ?
        ");
        $stmt->execute([$username]);
        
        // Get user's pythoncoin address
        $stmt = $pdo->prepare("SELECT pythoncoin_address FROM ad_members WHERE username = ?");
        $stmt->execute([$username]);
        $user = $stmt->fetch();
        
        if ($user) {
            // Add to payment queue
            $stmt = $pdo->prepare("
                INSERT INTO payment_queue (click_id, username, pythoncoin_address, amount, client_id, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ");
            $stmt->execute([$clickId, $username, $user['pythoncoin_address'], $pycEarned, $clientId]);
        }
        
        $pdo->commit();
        
        echo json_encode([
            'success' => true,
            'click_id' => $clickId,
            'pyc_earned' => $pycEarned,
            'payment_queued' => true,
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        $pdo->rollBack();
        error_log("Record click failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to record click']);
    }
}

function getAdvertisers($pdo) {
    try {
        $stmt = $pdo->prepare("
            SELECT c.*, 
                   COUNT(ca.id) as ad_count,
                   TIMESTAMPDIFF(SECOND, c.last_seen, NOW()) as seconds_since_seen
            FROM p2p_clients c
            LEFT JOIN client_ads ca ON c.client_id = ca.client_id AND ca.active = 1
            WHERE c.status = 'online' 
            AND c.last_seen > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
            GROUP BY c.client_id
            ORDER BY c.last_seen DESC
        ");
        $stmt->execute();
        $clients = $stmt->fetchAll();
        
        $advertisers = [];
        foreach ($clients as $client) {
            $advertisers[] = [
                'client_id' => $client['client_id'],
                'name' => $client['name'],
                'status' => 'online',
                'ad_count' => (int)$client['ad_count'],
                'category' => $client['category'],
                'host' => $client['host'],
                'port' => (int)$client['port'],
                'last_seen' => $client['last_seen'],
                'uptime' => formatUptime($client['seconds_since_seen']),
                'wallet_address' => $client['wallet_address']
            ];
        }
        
        echo json_encode([
            'success' => true,
            'advertisers' => $advertisers,
            'total_count' => count($advertisers),
            'timestamp' => date('c')
        ]);
        
    } catch(PDOException $e) {
        error_log("Get advertisers failed: " . $e->getMessage());
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to get advertisers']);
    }
}

function formatUptime($seconds) {
    if ($seconds < 60) return $seconds . 's';
    if ($seconds < 3600) return floor($seconds / 60) . 'm';
    if ($seconds < 86400) return floor($seconds / 3600) . 'h';
    return floor($seconds / 86400) . 'd';
}

// Add client_ads table if it doesn't exist
try {
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS client_ads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(100) NOT NULL,
            ad_id VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'general',
            payout_rate DECIMAL(10,8) DEFAULT 0.00200000,
            click_url VARCHAR(500),
            image_url VARCHAR(500),
            targeting_tags JSON,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_client_id (client_id),
            INDEX idx_ad_id (ad_id),
            INDEX idx_active (active)
        ) ENGINE=InnoDB
    ");
} catch(PDOException $e) {
    error_log("Table creation failed: " . $e->getMessage());
}
?>'''
        
        self.backup_file('api.php')
        with open('api.php', 'w', encoding='utf-8') as f:
            f.write(api_content)
        self.modifications_made.append("Enhanced api.php with real-time client registration")
        print("✅ Enhanced api.php")
    
    def inject_enhanced_portal_html(self):
        """Inject enhanced developer portal with real-time updates"""
        
        portal_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonCoin P2P Ad Network - Enhanced Developer Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #0066cc;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
            --dark: #343a40;
            --light: #f8f9fa;
            --border: #dee2e6;
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255,255,255,0.95);
            padding: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--primary);
        }
        
        .live-indicator {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.9em;
        }
        
        .status-light {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .light-green { background: var(--success); }
        .light-red { background: var(--danger); }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .panel {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .panel h2 {
            color: var(--primary);
            margin-bottom: 20px;
            font-size: 1.4em;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary) 0%, #0056b3 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .client-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .client-card {
            background: white;
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .client-card.online {
            border-color: var(--success);
            background: #f8fff9;
        }
        
        .client-status {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            background: var(--success);
            color: white;
        }
        
        .client-info h3 {
            margin: 0 0 5px 0;
            color: var(--dark);
        }
        
        .client-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }
        
        .client-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        
        .mini-stat {
            text-align: center;
            padding: 8px;
            background: var(--light);
            border-radius: 6px;
        }
        
        .mini-stat-number {
            font-weight: bold;
            color: var(--primary);
        }
        
        .mini-stat-label {
            font-size: 0.8em;
            color: #666;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            background: var(--primary);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .auto-refresh {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9em;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                🌐 PythonCoin P2P Ad Network
            </div>
            <div class="live-indicator">
                <div class="status-light light-green" id="serverStatus"></div>
                <span>Live Database Connection</span>
                <div id="clientCount">0 Clients Online</div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Live Statistics -->
        <div class="panel">
            <h2>📊 Live Network Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="totalClients">0</div>
                    <div class="stat-label">Active Clients</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, var(--success) 0%, #20c997 100%);">
                    <div class="stat-number" id="totalAds">0</div>
                    <div class="stat-label">Live Advertisements</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, var(--info) 0%, #138496 100%);">
                    <div class="stat-number" id="totalClicks">0</div>
                    <div class="stat-label">Total Clicks</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, var(--warning) 0%, #e0a800 100%);">
                    <div class="stat-number" id="totalRevenue">0.000</div>
                    <div class="stat-label">PYC Generated</div>
                </div>
            </div>
        </div>

        <!-- Live P2P Clients -->
        <div class="panel">
            <h2>🖥️ Live P2P Clients (Real-Time Database)</h2>
            <div style="margin-bottom: 20px;">
                <button class="btn" onclick="refreshClients()">🔄 Refresh</button>
                <button class="btn" onclick="exportClientData()">📊 Export Data</button>
            </div>
            <div class="client-grid" id="clientsGrid">
                <div style="text-align: center; padding: 40px; color: #666;">
                    <h3>Loading live clients from database...</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="auto-refresh" id="autoRefresh" onclick="toggleAutoRefresh()">
        🔄 Auto-refresh: ON
    </div>

    <script>
        let autoRefreshEnabled = true;
        let refreshInterval;
        
        const API_BASE = 'api.php';
        
        // Initialize portal
        document.addEventListener('DOMContentLoaded', function() {
            initializePortal();
        });
        
        function initializePortal() {
            loadLiveClients();
            loadNetworkStats();
            startAutoRefresh();
        }
        
        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            
            refreshInterval = setInterval(() => {
                if (autoRefreshEnabled) {
                    loadLiveClients();
                    loadNetworkStats();
                }
            }, 5000); // Refresh every 5 seconds
        }
        
        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const indicator = document.getElementById('autoRefresh');
            indicator.textContent = autoRefreshEnabled ? '🔄 Auto-refresh: ON' : '⏸️ Auto-refresh: OFF';
            indicator.style.background = autoRefreshEnabled ? 'var(--primary)' : 'var(--danger)';
        }
        
        function loadLiveClients() {
            fetch(API_BASE + '?action=get_live_clients')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayLiveClients(data.clients);
                        updateClientCount(data.total_count);
                        updateServerStatus(true);
                    } else {
                        console.error('Failed to load clients:', data.message);
                        updateServerStatus(false);
                    }
                })
                .catch(error => {
                    console.error('Client loading error:', error);
                    updateServerStatus(false);
                });
        }
        
        function displayLiveClients(clients) {
            const grid = document.getElementById('clientsGrid');
            
            if (clients.length === 0) {
                grid.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #666; grid-column: 1 / -1;">
                        <h3>No live clients found</h3>
                        <p>Start a Python P2P client to see it appear here automatically</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            clients.forEach(client => {
                html += `
                    <div class="client-card online">
                        <div class="client-status">ONLINE</div>
                        <div class="client-info">
                            <h3>🖥️ ${client.name}</h3>
                            <div class="client-meta">
                                <strong>ID:</strong> ${client.client_id}<br>
                                <strong>Address:</strong> ${client.host}:${client.port}<br>
                                <strong>User:</strong> ${client.username || 'N/A'}<br>
                                <strong>Wallet:</strong> ${client.wallet_address ? client.wallet_address.substring(0, 12) + '...' : 'N/A'}<br>
                                <strong>Version:</strong> ${client.version || '1.0'}<br>
                                <strong>Last Seen:</strong> ${client.uptime}
                            </div>
                        </div>
                        <div class="client-stats">
                            <div class="mini-stat">
                                <div class="mini-stat-number">${client.actual_ad_count || 0}</div>
                                <div class="mini-stat-label">Ads</div>
                            </div>
                            <div class="mini-stat">
                                <div class="mini-stat-number">${client.peer_count || 0}</div>
                                <div class="mini-stat-label">Peers</div>
                            </div>
                            <div class="mini-stat">
                                <div class="mini-stat-number">${client.stats ? (client.stats.uptime_seconds || 0) + 's' : '0s'}</div>
                                <div class="mini-stat-label">Uptime</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            grid.innerHTML = html;
        }
        
        function loadNetworkStats() {
            Promise.all([
                fetch(API_BASE + '?action=get_live_clients'),
                fetch(API_BASE + '?action=get_advertisers')
            ]).then(responses => {
                return Promise.all(responses.map(r => r.json()));
            }).then(([clientsData, adsData]) => {
                if (clientsData.success) {
                    document.getElementById('totalClients').textContent = clientsData.total_count;
                }
                
                if (adsData.success) {
                    const totalAds = adsData.advertisers.reduce((sum, client) => sum + (client.ad_count || 0), 0);
                    document.getElementById('totalAds').textContent = totalAds;
                }
            }).catch(error => {
                console.error('Stats loading error:', error);
            });
        }
        
        function updateServerStatus(online) {
            const indicator = document.getElementById('serverStatus');
            indicator.className = online ? 'status-light light-green' : 'status-light light-red';
        }
        
        function updateClientCount(count) {
            document.getElementById('clientCount').textContent = count + ' Clients Online';
        }
        
        function refreshClients() {
            loadLiveClients();
            loadNetworkStats();
        }
        
        function exportClientData() {
            fetch(API_BASE + '?action=get_live_clients')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const csv = convertToCSV(data.clients);
                        downloadCSV(csv, 'p2p_clients_' + new Date().toISOString().slice(0, 10) + '.csv');
                    }
                });
        }
        
        function convertToCSV(clients) {
            const headers = ['Client ID', 'Name', 'Host', 'Port', 'Status', 'Username', 'Wallet Address', 'Ad Count', 'Last Seen'];
            const rows = clients.map(client => [
                client.client_id,
                client.name,
                client.host,
                client.port,
                client.status,
                client.username || '',
                client.wallet_address || '',
                client.actual_ad_count || 0,
                client.last_seen
            ]);
            
            return [headers, ...rows].map(row => row.map(field => `"${field}"`).join(',')).join('\\n');
        }
        
        function downloadCSV(csv, filename) {
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
        
        console.log('Enhanced PythonCoin P2P Ad Network Portal Loaded');
    </script>
</body>
</html>'''
        
        self.backup_file('developer_portal.html')
        with open('developer_portal.php', 'w', encoding='utf-8') as f:
            f.write(portal_content)
        self.modifications_made.append("Created enhanced developer_portal.php with real-time database integration")
        print("✅ Enhanced developer_portal.php created")
    
    def inject_enhanced_pyqt_client(self):
        """Inject enhanced PyQt client code with automatic database registration - FIXED"""
        
        # Read the existing pyqt.py file
        if not os.path.exists('pyqt.py'):
            print("❌ pyqt.py not found")
            return
        
        with open('pyqt.py', 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Backup original
        self.backup_file('pyqt.py')
        
        # Create a simple approach - insert our code at the beginning
        database_code = '''
# Enhanced Database Auto-Registration for P2P Clients
import mysql.connector
import requests
import atexit
import signal

class DatabaseAutoRegistration:
    """Handles automatic database registration for P2P clients"""
    
    def __init__(self, username, wallet_address, client_name="PythonCoin P2P Client", port=8082):
        self.username = username
        self.wallet_address = wallet_address
        self.client_name = client_name
        self.client_id = f"pyc_{username}_{uuid.uuid4().hex[:8]}"
        self.host = self.get_local_ip()
        self.port = port
        self.version = "2.1.0"
        
        # Database config
        self.db_config = {
            'host': 'localhost',
            'database': 'adnetwrk',
            'user': 'root',
            'password': ''
        }
        
        # Server config
        self.server_config = {
            'api_url': 'http://localhost/livepy/pythoncoin/api.php'
        }
        
        self.db_connection = None
        self.registered = False
        
        # Setup cleanup handlers
        atexit.register(self.cleanup_on_exit)
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            self.db_connection = mysql.connector.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                autocommit=True
            )
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def register_client(self, wallet=None, blockchain=None):
        """Register client with database and server"""
        if self.registered:
            return True
        
        # Generate sample ad inventory
        ad_inventory = [
            {
                'ad_id': f'pyc_ad_{self.client_id}_1',
                'title': f'PythonCoin Mining Pool - {self.username}',
                'description': 'Join our decentralized mining pool for consistent PYC rewards',
                'category': 'cryptocurrency',
                'payout_rate': 0.00250000,
                'click_url': 'https://pythoncoin-mining.example.com',
                'image_url': '',
                'targeting_tags': ['mining', 'cryptocurrency', 'python'],
                'active': True
            }
        ]
        
        # Prepare registration data
        registration_data = {
            'action': 'client_register_live',
            'client_id': self.client_id,
            'username': self.username,
            'wallet_address': self.wallet_address,
            'client_name': self.client_name,
            'host': self.host,
            'port': self.port,
            'version': self.version,
            'capabilities': ['ad_serving', 'payment_processing'],
            'ad_inventory': ad_inventory,
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'python_version': sys.version,
                'platform': os.name
            }
        }
        
        # Try to register with server
        success = self.register_with_server(registration_data)
        
        # If server registration fails, try direct database registration
        if not success:
            success = self.register_with_database(registration_data)
        
        if success:
            self.registered = True
            logger.info(f"✅ Client registered successfully: {self.client_id}")
            # Start background heartbeat
            self.start_heartbeat()
        
        return success
    
    def register_with_server(self, data):
        """Register with remote server"""
        try:
            response = requests.post(
                self.server_config['api_url'],
                json=data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"✅ Registered with server")
                    return True
            return False
        except Exception as e:
            logger.error(f"Server registration error: {e}")
            return False
    
    def register_with_database(self, data):
        """Register directly with database"""
        if not self.connect_database():
            return False
        
        cursor = self.db_connection.cursor()
        
        try:
            # Register client
            cursor.execute("""
                INSERT INTO p2p_clients 
                (client_id, name, host, port, username, wallet_address, status, version, 
                 capabilities, metadata, ad_count, last_seen, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, 'online', %s, %s, %s, %s, NOW(), NOW())
                ON DUPLICATE KEY UPDATE 
                status = 'online',
                last_seen = NOW()
            """, (
                data['client_id'], data['client_name'], data['host'], data['port'],
                data['username'], data['wallet_address'], data['version'],
                json.dumps(data['capabilities']), json.dumps(data['metadata']),
                len(data['ad_inventory'])
            ))
            
            logger.info(f"✅ Registered directly with database: {data['client_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Database registration failed: {e}")
            return False
        finally:
            cursor.close()
    
    def start_heartbeat(self):
        """Start heartbeat thread"""
        def heartbeat_worker():
            while self.registered:
                try:
                    # Send heartbeat
                    if self.db_connection:
                        cursor = self.db_connection.cursor()
                        cursor.execute("""
                            UPDATE p2p_clients 
                            SET last_seen = NOW(), status = 'online'
                            WHERE client_id = %s
                        """, (self.client_id,))
                        cursor.close()
                    
                    time.sleep(60)  # Heartbeat every minute
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    time.sleep(120)
        
        heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        heartbeat_thread.start()
    
    def cleanup_on_exit(self):
        """Clean up on exit"""
        if self.registered and self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE p2p_clients 
                    SET status = 'offline', last_seen = NOW()
                    WHERE client_id = %s
                """, (self.client_id,))
                cursor.close()
                self.db_connection.close()
                logger.info(f"✅ Client cleanup completed: {self.client_id}")
            except:
                pass

'''
        
        # Insert the database code after the imports
        import_section = "import sys"
        if import_section in original_content:
            original_content = original_content.replace(import_section, import_section + database_code)
        
        # Find the __init__ method of UnifiedPythonCoinWallet and add database registration
        init_pattern = r'(class UnifiedPythonCoinWallet.*?\n.*?def __init__\(self\):.*?\n.*?super\(\).__init__\(\))'
        
        init_replacement = r'''\1
        
        # Initialize database auto-registration
        self.db_registration = None'''
        
        original_content = re.sub(init_pattern, init_replacement, original_content, flags=re.DOTALL)
        
        # Add registration after wallet load - simpler approach
        load_wallet_method = 'self.log_message("New wallet created successfully")'
        if load_wallet_method in original_content:
            registration_code = '''
        
        # Auto-register with database after wallet is created/loaded
        if self.wallet and hasattr(self.wallet, 'address'):
            try:
                username = f"user_{self.wallet.address[:8]}"
                self.db_registration = DatabaseAutoRegistration(
                    username=username,
                    wallet_address=self.wallet.address,
                    client_name=f"PythonCoin Wallet - {username}",
                    port=8082
                )
                
                # Register in background thread
                registration_thread = threading.Thread(
                    target=lambda: self.db_registration.register_client(self.wallet, self.blockchain),
                    daemon=True
                )
                registration_thread.start()
                
                self.log_message("🔄 Database auto-registration initiated...")
                
            except Exception as e:
                self.log_message(f"❌ Database registration error: {str(e)}")'''
            
            original_content = original_content.replace(load_wallet_method, load_wallet_method + registration_code)
        
        # Write the enhanced file
        with open('pyqt.py', 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        self.modifications_made.append("Enhanced pyqt.py with automatic database registration")
        print("✅ Enhanced pyqt.py with database auto-registration")
    
    def create_auth_php(self):
        """Create authentication handler"""
        auth_content = '''<?php
// Authentication handler for Enhanced P2P Ad Network
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$config = include 'config.php';
$host = $config['database']['host'];
$dbname = $config['database']['dbname'];
$username = $config['database']['username'];
$password = $config['database']['password'];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Database connection failed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$action = $input['action'] ?? '';

if ($action === 'login') {
    $user = $input['username'] ?? '';
    $pass = $input['password'] ?? '';
    
    if (empty($user) || empty($pass)) {
        echo json_encode(['success' => false, 'message' => 'Username and password required']);
        exit;
    }
    
    $stmt = $pdo->prepare("SELECT * FROM ad_members WHERE username = ?");
    $stmt->execute([$user]);
    $member = $stmt->fetch();
    
    if ($member && password_verify($pass, $member['password_hash'])) {
        // Update last login
        $updateStmt = $pdo->prepare("UPDATE ad_members SET last_login = NOW() WHERE username = ?");
        $updateStmt->execute([$user]);
        
        echo json_encode([
            'success' => true, 
            'user' => [
                'username' => $member['username'],
                'pythoncoin_address' => $member['pythoncoin_address'],
                'exp' => (float)$member['exp'],
                'total_clicks' => (int)$member['total_clicks'],
                'created_at' => $member['created_at']
            ]
        ]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
    }
    
} elseif ($action === 'register') {
    $user = $input['username'] ?? '';
    $pass = $input['password'] ?? '';
    $addr = $input['pythoncoin_address'] ?? '';
    
    if (empty($user) || empty($pass) || empty($addr)) {
        echo json_encode(['success' => false, 'message' => 'All fields are required']);
        exit;
    }
    
    $hash = password_hash($pass, PASSWORD_DEFAULT);
    
    try {
        $stmt = $pdo->prepare("INSERT INTO ad_members (username, password_hash, pythoncoin_address) VALUES (?, ?, ?)");
        $stmt->execute([$user, $hash, $addr]);
        
        echo json_encode(['success' => true, 'message' => 'Registration successful']);
    } catch(PDOException $e) {
        if ($e->getCode() == '23000') {
            echo json_encode(['success' => false, 'message' => 'Username already exists']);
        } else {
            echo json_encode(['success' => false, 'message' => 'Registration failed']);
        }
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Invalid action']);
}
?>'''
        
        with open('auth.php', 'w', encoding='utf-8') as f:
            f.write(auth_content)
        self.modifications_made.append("Created auth.php authentication handler")
        print("✅ Created auth.php")
    
    def create_database_schema(self):
        """Create database schema setup script"""
        schema_content = '''-- Enhanced P2P Ad Network Database Schema
-- Run this SQL to create the required database structure

CREATE DATABASE IF NOT EXISTS adnetwrk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE adnetwrk;

-- Members table
CREATE TABLE IF NOT EXISTS ad_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    pythoncoin_address VARCHAR(50) NOT NULL,
    exp DECIMAL(16,8) DEFAULT 0.00000000,
    total_clicks INT DEFAULT 0,
    total_impressions INT DEFAULT 0,
    embeds_created INT DEFAULT 0,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_address (pythoncoin_address)
) ENGINE=InnoDB;

-- P2P Clients table
CREATE TABLE IF NOT EXISTS p2p_clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    host VARCHAR(100) NOT NULL,
    port INT NOT NULL,
    status ENUM('online', 'offline', 'connecting') DEFAULT 'offline',
    category VARCHAR(50) DEFAULT 'general',
    username VARCHAR(50) NULL,
    wallet_address VARCHAR(50) NULL,
    ad_count INT DEFAULT 0,
    peer_count INT DEFAULT 0,
    version VARCHAR(20) DEFAULT '1.0',
    capabilities JSON NULL,
    stats JSON NULL,
    metadata JSON NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_client_id (client_id),
    INDEX idx_status (status),
    INDEX idx_last_seen (last_seen)
) ENGINE=InnoDB;

-- Client Ads table
CREATE TABLE IF NOT EXISTS client_ads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(100) NOT NULL,
    ad_id VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    payout_rate DECIMAL(10,8) DEFAULT 0.00200000,
    click_url VARCHAR(500),
    image_url VARCHAR(500),
    targeting_tags JSON,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_client_id (client_id),
    INDEX idx_ad_id (ad_id),
    INDEX idx_active (active)
) ENGINE=InnoDB;

-- Ad Clicks table
CREATE TABLE IF NOT EXISTS ad_clicks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    ad_id VARCHAR(100) NOT NULL,
    embed_id VARCHAR(100) NULL,
    client_id VARCHAR(100) NULL,
    zone VARCHAR(50) NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    referer TEXT NULL,
    pyc_earned DECIMAL(16,8) DEFAULT 0.00000000,
    payment_processed BOOLEAN DEFAULT FALSE,
    payment_tx_id VARCHAR(100) NULL,
    click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_payment_processed (payment_processed),
    INDEX idx_click_time (click_time)
) ENGINE=InnoDB;

-- Payment Queue table
CREATE TABLE IF NOT EXISTS payment_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    click_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    pythoncoin_address VARCHAR(50) NOT NULL,
    amount DECIMAL(16,8) NOT NULL,
    client_id VARCHAR(100) NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    tx_id VARCHAR(100) NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NULL,
    event_type VARCHAR(50) NOT NULL,
    ad_id VARCHAR(100) NULL,
    embed_id VARCHAR(100) NULL,
    client_id VARCHAR(100) NULL,
    ip_address VARCHAR(45) NULL,
    data JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- Insert sample data
INSERT IGNORE INTO ad_members (username, password_hash, pythoncoin_address, exp) VALUES
('demo', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'PYC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0', 0.05000000);

SELECT 'Enhanced P2P Ad Network database schema created successfully!' as result;
'''
        
        with open('database_schema.sql', 'w', encoding='utf-8') as f:
            f.write(schema_content)
        self.modifications_made.append("Created database_schema.sql")
        print("✅ Created database_schema.sql")
    
    def run_injections(self):
        """Run all file injections"""
        print("🚀 Starting Enhanced P2P Ad Network Injection Process")
        print("=" * 60)
        
        try:
            # 1. Enhanced API
            print("\n📡 Injecting Enhanced API...")
            self.inject_enhanced_api_php()
            
            # 2. Enhanced Portal
            print("\n🌐 Injecting Enhanced Developer Portal...")
            self.inject_enhanced_portal_html()
            
            # 3. Enhanced PyQt Client
            print("\n🖥️ Injecting Enhanced PyQt Client...")
            self.inject_enhanced_pyqt_client()
            
            # 4. Authentication
            print("\n🔐 Creating Authentication Handler...")
            self.create_auth_php()
            
            # 5. Database Schema
            print("\n🗄️ Creating Database Schema...")
            self.create_database_schema()
            
            print("\n" + "=" * 60)
            print("✅ INJECTION PROCESS COMPLETED!")
            print("=" * 60)
            
            print("\n📋 MODIFICATIONS SUMMARY:")
            for i, modification in enumerate(self.modifications_made, 1):
                print(f"   {i}. {modification}")
            
            print("\n🔧 NEXT STEPS:")
            print("   1. Import database_schema.sql into MySQL")
            print("   2. Start XAMPP and ensure MySQL is running")
            print("   3. Run the enhanced PyQt client (python pyqt.py)")
            print("   4. Open developer_portal.php in your browser")
            print("   5. Clients will auto-register when they start!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ INJECTION FAILED: {str(e)}")
            import traceback
            print(f"Error details: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    injector = NetworkInjector()
    injector.run_injections()