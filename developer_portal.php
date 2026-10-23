<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nickles P2P Ad Network - Enhanced Developer Portal</title>
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
                🌐 Nickles P2P Ad Network
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
                    <div class="stat-label">NCKL Generated</div>
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
            
            return [headers, ...rows].map(row => row.map(field => `"${field}"`).join(',')).join('\n');
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
        
        console.log('Enhanced Nickles P2P Ad Network Portal Loaded');
    </script>
</body>
</html>