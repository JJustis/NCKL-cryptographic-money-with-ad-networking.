#!/usr/bin/env python3
"""
PythonCoin Dashboard Auto-Patcher
Automatically injects fixes into dashboard7.php
"""

import os
import re
import shutil
from datetime import datetime

class DashboardPatcher:
    def __init__(self, file_path="dashboard7.php"):
        self.file_path = file_path
        self.backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.content = ""
        
    def load_file(self):
        """Load the PHP file content"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ Loaded {self.file_path} ({len(self.content)} characters)")
            return True
        except FileNotFoundError:
            print(f"❌ File {self.file_path} not found!")
            return False
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    def create_backup(self):
        """Create backup of original file"""
        try:
            shutil.copy2(self.file_path, self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def inject_helper_functions(self):
        """Inject helper functions after the existing functions"""
        helper_functions = '''
// ENHANCED HELPER FUNCTIONS - Auto-injected by PythonCoin Patcher
function discoverClientEndpoints($host, $port) {
    $endpointsToTest = ['/', '/status', '/info', '/client_info', '/ads', '/register', '/register_developer'];
    $workingEndpoints = [];
    $clientBaseUrl = "http://{$host}:{$port}";
    
    foreach ($endpointsToTest as $endpoint) {
        $url = $clientBaseUrl . $endpoint;
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 1);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200 && $response) {
            $workingEndpoints[] = [
                'endpoint' => $endpoint,
                'http_code' => $httpCode,
                'is_json' => json_decode($response, true) !== null
            ];
        }
    }
    
    return [
        'client_url' => $clientBaseUrl,
        'working_endpoints' => $workingEndpoints,
        'total_working' => count($workingEndpoints)
    ];
}

function generateFallbackSVG($adId, $message = 'PythonCoin Ad') {
    $cleanAdId = htmlspecialchars($adId);
    $cleanMessage = htmlspecialchars($message);
    
    return '<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#0066cc;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#004499;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad1)" rx="10"/>
    <text x="200" y="100" font-family="Arial, sans-serif" font-size="28" fill="white" text-anchor="middle" font-weight="bold">🌐 PythonCoin</text>
    <text x="200" y="130" font-family="Arial, sans-serif" font-size="18" fill="white" text-anchor="middle">P2P Advertising Network</text>
    <text x="200" y="160" font-family="Arial, sans-serif" font-size="14" fill="#ccddff" text-anchor="middle">' . $cleanMessage . '</text>
    <text x="200" y="190" font-family="Arial, sans-serif" font-size="12" fill="#ccddff" text-anchor="middle">Ad ID: ' . $cleanAdId . '</text>
    <text x="200" y="220" font-family="Arial, sans-serif" font-size="10" fill="rgba(255,255,255,0.8)" text-anchor="middle">Fallback Mode - Check PyQt Client Connection</text>
    <rect x="10" y="10" width="380" height="280" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2" rx="8"/>
    <circle cx="50" cy="50" r="8" fill="rgba(255,255,255,0.6)">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
    </circle>
</svg>';
}

function getEnhancedNetworkSampleAds() {
    return [
        [
            'id' => 'network_ad_001',
            'ad_id' => 'network_ad_001',
            'client_id' => 'pyc_client_001',
            'title' => 'PythonCoin Wallet Pro',
            'description' => 'Advanced cryptocurrency wallet with P2P advertising features',
            'category' => 'cryptocurrency',
            'payout' => 0.005,
            'payout_amount' => 0.005,
            'svg_url' => '?ajax=proxy_svg&client_host=127.0.0.1&client_port=8082&ad_id=network_ad_001',
            'target_url' => 'https://pythoncoin.org',
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 'network_ad_002',
            'ad_id' => 'network_ad_002',
            'client_id' => 'pyc_client_001',
            'title' => 'P2P Ad Network Integration',
            'description' => 'Learn how to integrate P2P advertising into your applications',
            'category' => 'education',
            'payout' => 0.003,
            'payout_amount' => 0.003,
            'svg_url' => '?ajax=proxy_svg&client_host=127.0.0.1&client_port=8082&ad_id=network_ad_002',
            'target_url' => 'https://docs.pythoncoin.org',
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 'network_ad_003',
            'ad_id' => 'network_ad_003',
            'client_id' => 'pyc_client_001',
            'title' => 'Decentralized Advertising Platform',
            'description' => 'Next-generation advertising platform built on blockchain technology',
            'category' => 'technology',
            'payout' => 0.002,
            'payout_amount' => 0.002,
            'svg_url' => '?ajax=proxy_svg&client_host=127.0.0.1&client_port=8082&ad_id=network_ad_003',
            'target_url' => 'https://pythoncoin.org/advertising',
            'created_at' => date('Y-m-d H:i:s')
        ]
    ];
}

function getAdsFromSelectedClients($selectedClientIds = []) {
    $allAds = [];
    
    if (empty($selectedClientIds)) {
        // Fallback to sample ads if no clients selected
        return getEnhancedNetworkSampleAds();
    }
    
    foreach ($selectedClientIds as $clientData) {
        $host = $clientData['host'] ?? '127.0.0.1';
        $port = $clientData['port'] ?? '8082';
        $clientId = $clientData['client_id'] ?? 'unknown';
        
        // Try to get ads from this client
        $adsUrl = "http://{$host}:{$port}/ads";
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $adsUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 3);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept: application/json']);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200 && $response) {
            $decoded = json_decode($response, true);
            if ($decoded && isset($decoded['ads']) && is_array($decoded['ads'])) {
                foreach ($decoded['ads'] as $ad) {
                    $ad['client_host'] = $host;
                    $ad['client_port'] = $port;
                    $ad['source_client'] = $clientId;
                    $ad['svg_url'] = "?ajax=proxy_svg&client_host={$host}&client_port={$port}&ad_id=" . urlencode($ad['id'] ?? 'unknown');
                    $allAds[] = $ad;
                }
            }
        }
    }
    
    // If no ads from real clients, return sample ads
    if (empty($allAds)) {
        return getEnhancedNetworkSampleAds();
    }
    
    return $allAds;
}
'''
        
        # Find a good place to inject the helper functions
        injection_point = "// Initialize API\n$api = new PythonCoinAPI();"
        if injection_point in self.content:
            self.content = self.content.replace(injection_point, helper_functions + "\n\n" + injection_point)
            print("✅ Helper functions injected")
            return True
        else:
            print("❌ Could not find injection point for helper functions")
            return False
    
    def update_ajax_handlers(self):
        """Update AJAX handlers with enhanced versions"""
        
        # Enhanced proxy_register case
        proxy_register_code = '''case 'proxy_register':
    $clientHost = $_POST['client_host'] ?? '';
    $clientPort = $_POST['client_port'] ?? '8082';
    $developerAddress = $_POST['developer_address'] ?? '';
    $developerName = $_POST['developer_name'] ?? '';
    $zone = $_POST['zone'] ?? '';
    
    if ($clientHost && $developerAddress) {
        // First discover what endpoints work
        $discoveryResult = discoverClientEndpoints($clientHost, $clientPort);
        
        if (empty($discoveryResult['working_endpoints'])) {
            echo json_encode([
                'success' => false, 
                'error' => 'No working endpoints found on client',
                'client_url' => "http://{$clientHost}:{$clientPort}",
                'discovery' => $discoveryResult
            ]);
            break;
        }
        
        // Try registration endpoints that were discovered to work
        $registrationEndpoints = ['/register_developer', '/register', '/register_js'];
        $workingEndpoints = array_column($discoveryResult['working_endpoints'], 'endpoint');
        
        $success = false;
        $attempts = [];
        
        foreach ($registrationEndpoints as $endpoint) {
            if (in_array($endpoint, $workingEndpoints)) {
                $registerUrl = "http://{$clientHost}:{$clientPort}{$endpoint}";
                $postData = json_encode([
                    'developer_address' => $developerAddress,
                    'developer_name' => $developerName,
                    'zone' => $zone,
                    'host' => $_SERVER['HTTP_HOST'] ?? '',
                    'timestamp' => time()
                ]);
                
                $ch = curl_init();
                curl_setopt($ch, CURLOPT_URL, $registerUrl);
                curl_setopt($ch, CURLOPT_POST, true);
                curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_TIMEOUT, 3);
                curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
                
                $response = curl_exec($ch);
                $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                curl_close($ch);
                
                $attempts[] = ['endpoint' => $endpoint, 'http_code' => $httpCode];
                
                if ($httpCode === 200 && $response) {
                    $decoded = json_decode($response, true);
                    if ($decoded && isset($decoded['success']) && $decoded['success']) {
                        echo json_encode(['success' => true, 'endpoint' => $endpoint, 'response' => $decoded]);
                        $success = true;
                        break;
                    }
                }
            }
        }
        
        if (!$success) {
            echo json_encode([
                'success' => false, 
                'error' => 'Registration failed on all discovered endpoints',
                'working_endpoints' => $workingEndpoints,
                'attempts' => $attempts
            ]);
        }
    } else {
        echo json_encode(['success' => false, 'error' => 'Missing required parameters']);
    }
    break;'''

        # Enhanced proxy_ads case
        proxy_ads_code = '''case 'proxy_ads':
    $clientHost = $_POST['client_host'] ?? '';
    $clientPort = $_POST['client_port'] ?? '8082';
    $zone = $_POST['zone'] ?? '';
    $developerAddress = $_POST['developer_address'] ?? '';
    
    if ($clientHost) {
        $discoveryResult = discoverClientEndpoints($clientHost, $clientPort);
        $workingEndpoints = array_column($discoveryResult['working_endpoints'] ?? [], 'endpoint');
        
        if (!in_array('/ads', $workingEndpoints)) {
            echo json_encode([
                'success' => false,
                'error' => '/ads endpoint not available on client',
                'working_endpoints' => $workingEndpoints,
                'fallback' => 'using_sample_ads'
            ]);
            break;
        }
        
        $adsUrl = "http://{$clientHost}:{$clientPort}/ads";
        if ($zone || $developerAddress) {
            $params = [];
            if ($zone) $params['zone'] = $zone;
            if ($developerAddress) $params['developer'] = $developerAddress;
            $adsUrl .= '?' . http_build_query($params);
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $adsUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'X-Developer-Address: ' . $developerAddress,
            'X-Zone: ' . $zone,
            'Accept: application/json'
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200 && $response) {
            $decoded = json_decode($response, true);
            if ($decoded !== null) {
                echo json_encode($decoded);
            } else {
                echo json_encode([
                    'success' => false,
                    'error' => 'Client returned non-JSON response',
                    'fallback' => 'using_sample_ads'
                ]);
            }
        } else {
            echo json_encode([
                'success' => false, 
                'error' => 'HTTP request failed', 
                'http_code' => $httpCode,
                'fallback' => 'using_sample_ads'
            ]);
        }
    } else {
        echo json_encode(['success' => false, 'error' => 'Missing client host']);
    }
    break;'''

        # Enhanced proxy_svg case
        proxy_svg_code = '''case 'proxy_svg':
    $clientHost = $_POST['client_host'] ?? '';
    $clientPort = $_POST['client_port'] ?? '8082';
    $adId = $_POST['ad_id'] ?? '';
    
    if ($clientHost && $adId) {
        $svgUrls = [
            "http://{$clientHost}:{$clientPort}/ad/{$adId}.svg",
            "http://{$clientHost}:{$clientPort}/svg/{$adId}",
            "http://{$clientHost}:{$clientPort}/ads/{$adId}/svg"
        ];
        
        $svgContent = null;
        
        foreach ($svgUrls as $svgUrl) {
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $svgUrl);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 3);
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept: image/svg+xml,text/plain']);
            
            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($httpCode === 200 && $response && (stripos($response, '<svg') !== false || stripos($response, '<?xml') !== false)) {
                $svgContent = $response;
                break;
            }
        }
        
        if ($svgContent) {
            header('Content-Type: image/svg+xml');
            echo $svgContent;
        } else {
            header('Content-Type: image/svg+xml');
            echo generateFallbackSVG($adId, 'Client SVG Not Available');
        }
    } else {
        header('Content-Type: image/svg+xml');
        echo generateFallbackSVG($adId ?? 'unknown', 'Missing Parameters');
    }
    break;'''

        # New cases to add
        new_cases = '''
            case 'discover_endpoints':
                $clientHost = $_POST['client_host'] ?? '127.0.0.1';
                $clientPort = $_POST['client_port'] ?? '8082';
                
                $discoveryResult = discoverClientEndpoints($clientHost, $clientPort);
                echo json_encode([
                    'success' => true,
                    'client_url' => "http://{$clientHost}:{$clientPort}",
                    'working_endpoints' => $discoveryResult['working_endpoints'],
                    'total_working' => $discoveryResult['total_working']
                ]);
                break;
                
            case 'get_ads_from_selected':
                $selectedClients = json_decode($_POST['selected_clients'] ?? '[]', true);
                $ads = getAdsFromSelectedClients($selectedClients);
                
                echo json_encode([
                    'success' => true,
                    'ads' => $ads,
                    'source' => 'selected_clients',
                    'client_count' => count($selectedClients),
                    'ad_count' => count($ads)
                ]);
                break;
        '''
        
        # Replace existing cases or add new ones
        replacements = [
            ('case \'proxy_register\':', proxy_register_code),
            ('case \'proxy_ads\':', proxy_ads_code),  
            ('case \'proxy_svg\':', proxy_svg_code)
        ]
        
        for old_pattern, new_code in replacements:
            if old_pattern in self.content:
                # Find the end of the case block
                start_pos = self.content.find(old_pattern)
                if start_pos != -1:
                    # Find the break; statement that ends this case
                    break_pos = self.content.find('break;', start_pos)
                    if break_pos != -1:
                        # Replace everything from case to break;
                        end_pos = break_pos + 6  # length of 'break;'
                        old_case = self.content[start_pos:end_pos]
                        self.content = self.content.replace(old_case, new_code)
                        print(f"✅ Updated {old_pattern}")
                    else:
                        print(f"❌ Could not find break; for {old_pattern}")
                else:
                    print(f"❌ Could not find {old_pattern}")
        
        # Add new cases before the default case
        default_case_pos = self.content.find('default:')
        if default_case_pos != -1:
            self.content = self.content[:default_case_pos] + new_cases + '\n            ' + self.content[default_case_pos:]
            print("✅ Added new AJAX cases")
        
        return True
    
    def update_javascript_functions(self):
        """Update JavaScript functions for better ad preview"""
        
        js_updates = '''
        // ENHANCED LIVE AD PREVIEW FUNCTIONS - Auto-injected
        function loadAdsFromSelectedClients() {
            if (selectedClients.length === 0) {
                addLog('No clients selected - loading sample ads', 'warning');
                loadLiveAds();
                return;
            }
            
            addLog('Loading ads from ' + selectedClients.length + ' selected clients...', 'info');
            
            var statusDiv = document.getElementById('adStatusInfo');
            if (statusDiv) {
                statusDiv.innerHTML = '<div class="alert alert-warning">🔄 Loading ads from selected P2P clients...</div>';
            }
            
            fetch('?ajax=get_ads_from_selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'selected_clients=' + encodeURIComponent(JSON.stringify(selectedClients))
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success && data.ads) {
                    liveAds = data.ads;
                    displayLiveAds();
                    addLog('Loaded ' + data.ads.length + ' ads from ' + data.client_count + ' selected clients', 'success');
                    
                    if (statusDiv) {
                        statusDiv.innerHTML = '<div class="alert alert-success">✅ Loaded ' + data.ads.length + ' ads from ' + data.client_count + ' selected clients</div>';
                    }
                } else {
                    addLog('Failed to load ads from selected clients', 'error');
                    if (statusDiv) {
                        statusDiv.innerHTML = '<div class="alert alert-error">❌ Failed to load ads from selected clients</div>';
                    }
                    // Fallback to regular ad loading
                    loadLiveAds();
                }
            })
            .catch(function(error) {
                addLog('Error loading ads from selected clients: ' + error.message, 'error');
                if (statusDiv) {
                    statusDiv.innerHTML = '<div class="alert alert-error">❌ Network error loading ads from selected clients</div>';
                }
                // Fallback to regular ad loading
                loadLiveAds();
            });
        }
        
        // Override the refresh ads function to use selected clients
        function refreshAds() {
            addLog('Refreshing ads from selected clients...', 'info');
            loadAdsFromSelectedClients();
        }
        
        // Auto-refresh ads when clients are selected/deselected
        function updateSelectedClientsDisplay() {
            var container = document.getElementById('selectedClientsDisplay');
            
            if (selectedClients.length === 0) {
                container.innerHTML = '<span style="color: #666; font-style: italic;">Select P2P clients from the Network tab</span>';
                return;
            }
            
            // Clear container first
            container.innerHTML = '';
            
            for (var i = 0; i < selectedClients.length; i++) {
                var client = selectedClients[i];
                
                var clientTag = document.createElement('div');
                clientTag.className = 'client-tag';
                clientTag.textContent = client.name + ' ';
                
                var removeBtn = document.createElement('button');
                removeBtn.className = 'remove-client';
                removeBtn.textContent = '×';
                removeBtn.setAttribute('data-client-id', client.client_id);
                removeBtn.addEventListener('click', function() {
                    removeClientSelection(this.getAttribute('data-client-id'));
                });
                
                clientTag.appendChild(removeBtn);
                container.appendChild(clientTag);
            }
            
            // Auto-refresh ads when selection changes
            if (selectedClients.length > 0) {
                setTimeout(function() {
                    loadAdsFromSelectedClients();
                }, 500);
            }
        }
        '''
        
        # Find a place to inject the JavaScript updates
        js_injection_point = "console.log('PythonCoin P2P Ad Network Developer Portal initialized successfully');"
        if js_injection_point in self.content:
            self.content = self.content.replace(js_injection_point, js_updates + "\n        " + js_injection_point)
            print("✅ JavaScript functions updated")
            return True
        else:
            print("❌ Could not find JavaScript injection point")
            return False
    
    def save_file(self):
        """Save the modified content back to file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            print(f"✅ Successfully updated {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def run_patches(self):
        """Run all patches in sequence"""
        print("🚀 Starting PythonCoin Dashboard Auto-Patcher...")
        print("=" * 50)
        
        # Load file
        if not self.load_file():
            return False
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Apply patches
        patches = [
            ("Injecting helper functions", self.inject_helper_functions),
            ("Updating AJAX handlers", self.update_ajax_handlers),
            ("Updating JavaScript functions", self.update_javascript_functions),
        ]
        
        for patch_name, patch_func in patches:
            print(f"\n📝 {patch_name}...")
            if not patch_func():
                print(f"❌ Failed to apply patch: {patch_name}")
                print(f"💡 You can restore from backup: {self.backup_path}")
                return False
        
        # Save file
        if not self.save_file():
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All patches applied successfully!")
        print(f"📁 Original file backed up to: {self.backup_path}")
        print(f"✨ {self.file_path} has been enhanced with:")
        print("   • Endpoint discovery capabilities")
        print("   • Enhanced error handling")
        print("   • Live ad preview from selected clients")
        print("   • Fallback SVG generation")
        print("   • Improved P2P client communication")
        print("\n🔧 Test the dashboard to verify all functionality works!")
        
        return True

def main():
    import sys
    
    # Get file path from command line argument or use default
    file_path = sys.argv[1] if len(sys.argv) > 1 else "dashboard7.php"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found!")
        print("💡 Usage: python3 patcher.py [dashboard_file.php]")
        return
    
    # Run patcher
    patcher = DashboardPatcher(file_path)
    success = patcher.run_patches()
    
    if success:
        print(f"\n🌟 Ready to test! Open {file_path} in your browser")
    else:
        print(f"\n💥 Patching failed. Check the errors above.")

if __name__ == "__main__":
    main()