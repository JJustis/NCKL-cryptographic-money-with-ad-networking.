#!/usr/bin/env python3
"""
Auto-fix script for PythonCoin PyQt wallet server issues
Fixes the port 8082 developer portal server functionality
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the original file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_pyqt_server(file_path="pyqt.py"):
    """Fix the PythonCoin PyQt server implementation"""
    
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found")
        return False
    
    print(f"🔧 Fixing PythonCoin PyQt server in {file_path}")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix 1: Replace the problematic DeveloperPortalServer class
        print("🔧 Replacing DeveloperPortalServer class...")
        
        # Find the start and end of the DeveloperPortalServer class
        class_start = content.find("class DeveloperPortalServer(QThread):")
        if class_start == -1:
            print("❌ DeveloperPortalServer class not found")
            return False
        
        # Find the end of the class (next class or end of file)
        class_end = content.find("\nclass ", class_start + 1)
        if class_end == -1:
            # Look for function definitions or end of file
            class_end = content.find("\ndef main():", class_start)
            if class_end == -1:
                class_end = len(content)
        
        # Extract the part before and after the class
        before_class = content[:class_start]
        after_class = content[class_end:]
        
        # New improved DeveloperPortalServer implementation
        new_server_class = '''class DeveloperPortalServer(QThread):
    """Enhanced HTTP server for developer portal integration with working port 8082"""
    
    status_update = pyqtSignal(str)
    click_received = pyqtSignal(dict)
    developer_registered = pyqtSignal(str, str)
    
    def __init__(self, wallet, blockchain, port=8082):
        super().__init__()
        self.wallet = wallet
        self.blockchain = blockchain
        self.port = port
        self.running = False
        self.server = None
        self.registered_developers = {}
        self.click_payments = []
        self.ads_served = 0
        
        # Create the js directory if it doesn't exist
        self.js_dir = os.path.join(os.getcwd(), 'js')
        if not os.path.exists(self.js_dir):
            os.makedirs(self.js_dir)
            print(f"Created JS directory: {self.js_dir}")
    
    def run(self):
        """Start the HTTP server using a simple HTTP server instead of aiohttp"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import urllib.parse
            import json
            import threading
            
            self.running = True
            self.status_update.emit(f"Starting developer portal server on port {self.port}")
            
            class PythonCoinHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, server_instance=None, **kwargs):
                    self.server_instance = server_instance
                    super().__init__(*args, **kwargs)
                
                def log_message(self, format, *args):
                    # Suppress default logging
                    pass
                
                def do_OPTIONS(self):
                    """Handle CORS preflight requests"""
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                    self.end_headers()
                
                def do_GET(self):
                    """Handle GET requests"""
                    try:
                        # Parse the path
                        parsed_path = urllib.parse.urlparse(self.path)
                        path = parsed_path.path
                        query = urllib.parse.parse_qs(parsed_path.query)
                        
                        # Add CORS headers
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        
                        if path == '/client_info':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_client_info()
                            self.wfile.write(response.encode())
                            
                        elif path.startswith('/custom_') and path.endswith('.js'):
                            self.send_header('Content-Type', 'application/javascript')
                            self.send_header('Cache-Control', 'no-cache')
                            self.end_headers()
                            js_content = self.server_instance.handle_custom_js(path)
                            self.wfile.write(js_content.encode())
                            
                        elif path == '/ads':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_get_ads()
                            self.wfile.write(response.encode())
                            
                        elif path == '/stats':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_stats()
                            self.wfile.write(response.encode())
                            
                        else:
                            self.send_header('Content-Type', 'text/plain')
                            self.end_headers()
                            self.wfile.write(b'PythonCoin Wallet Server - Port 8082 Active')
                            
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-Type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(f"Server error: {str(e)}".encode())
                
                def do_POST(self):
                    """Handle POST requests"""
                    try:
                        # Read the request body
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        
                        # Parse JSON data
                        try:
                            data = json.loads(post_data.decode('utf-8'))
                        except:
                            data = {}
                        
                        # Add CORS headers
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        
                        # Route to appropriate handler
                        path = urllib.parse.urlparse(self.path).path
                        
                        if path == '/register_developer':
                            response = self.server_instance.handle_register_developer(data)
                        elif path == '/click':
                            response = self.server_instance.handle_click(data)
                        elif path == '/impression':
                            response = self.server_instance.handle_impression(data)
                        else:
                            response = '{"success": false, "error": "Unknown endpoint"}'
                        
                        self.wfile.write(response.encode())
                        
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        error_response = f'{{"success": false, "error": "{str(e)}"}}'
                        self.wfile.write(error_response.encode())
            
            # Create server with custom handler
            def handler(*args, **kwargs):
                return PythonCoinHandler(*args, server_instance=self, **kwargs)
            
            self.server = HTTPServer(('0.0.0.0', self.port), handler)
            self.status_update.emit(f"Developer portal server started on port {self.port}")
            
            # Start server
            while self.running:
                self.server.handle_request()
                
        except Exception as e:
            self.status_update.emit(f"Server error: {str(e)}")
            print(f"Server error: {e}")
    
    def handle_client_info(self):
        """Handle client info requests"""
        try:
            client_info = {
                'client_id': f'pyc_{self.wallet.address[:8]}' if self.wallet else 'pyc_unknown',
                'name': f'PythonCoin Wallet - {self.wallet.address[:8]}...' if self.wallet else 'PythonCoin Wallet',
                'status': 'online',
                'host': '127.0.0.1',
                'port': self.port,
                'ad_count': len(self.get_available_ads()),
                'peers': len(self.registered_developers),
                'category': 'cryptocurrency',
                'uptime': '24h+',
                'bandwidth': 1000,
                'wallet_address': self.wallet.address if self.wallet else '',
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                'capabilities': ['ad_serving', 'payments', 'p2p', 'developer_portal']
            }
            
            return json.dumps({
                'success': True,
                'client': client_info
            })
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            })
    
    def handle_custom_js(self, path):
        """Generate custom JavaScript for developers"""
        try:
            # Extract developer address from path like /custom_ADDRESS.js
            import re
            match = re.search(r'custom_([a-zA-Z0-9]+)\.js', path)
            if not match:
                return "// Error: Invalid custom JS request"
            
            developer_address = match.group(1)
            
            # Generate the custom JavaScript
            ads = self.get_available_ads()
            
            js_content = f'''// PythonCoin Wallet - Custom Ad JavaScript
// Generated for developer: {developer_address}
// Server: {self.wallet.address if self.wallet else 'Unknown'}
// Generated: {datetime.now().isoformat()}

(function() {{
    'use strict';
    
    console.log('[PYC-WALLET] PythonCoin ad network initialized');
    
    const PYC_WALLET_CONFIG = {{
        serverAddress: '{self.wallet.address if self.wallet else 'unknown'}',
        serverPort: {self.port},
        developerAddress: '{developer_address}',
        serverHost: 'http://127.0.0.1:{self.port}',
        ads: {json.dumps(ads)},
        loadTime: new Date().toISOString()
    }};
    
    let currentAdIndex = 0;
    let adRotationInterval = null;
    
    // Initialize the ad system
    function initPYCWalletAds() {{
        console.log('[PYC-WALLET] Initializing ads from PythonCoin wallet server');
        console.log('[PYC-WALLET] Available ads:', PYC_WALLET_CONFIG.ads.length);
        
        if (PYC_WALLET_CONFIG.ads.length > 0) {{
            displayWalletAd(PYC_WALLET_CONFIG.ads[0]);
            if (PYC_WALLET_CONFIG.ads.length > 1) {{
                startAdRotation();
            }}
        }} else {{
            displayNoAdsMessage();
        }}
        
        // Send impression tracking
        trackImpression();
    }}
    
    function displayWalletAd(ad) {{
        const containers = document.querySelectorAll('[data-pyc-zone]');
        console.log('[PYC-WALLET] Found', containers.length, 'ad containers');
        
        containers.forEach(container => {{
            const zone = container.getAttribute('data-pyc-zone') || 'default';
            
            container.innerHTML = ```
                <div class="pyc-ad-container" style="
                    border: 2px solid #0066cc; 
                    border-radius: 12px; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    margin: 15px 0; 
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    box-shadow: 0 4px 12px rgba(0,102,204,0.1);
                " onclick="handlePYCAdClick('${{ad.id}}', '${{zone}}')">
                    <div style="
                        position: absolute; 
                        top: 10px; 
                        right: 10px; 
                        background: linear-gradient(45deg, #ff6b35, #f7931e); 
                        color: white; 
                        padding: 4px 8px; 
                        border-radius: 12px; 
                        font-size: 10px; 
                        font-weight: bold;
                    ">💎 PYC</div>
                    <h3 style="
                        color: #0066cc; 
                        margin: 0 0 10px 0; 
                        font-size: 18px;
                        font-weight: 700;
                    ">${{ad.title}}</h3>
                    <p style="
                        color: #666; 
                        margin: 0 0 15px 0; 
                        font-size: 14px;
                        line-height: 1.5;
                    ">${{ad.description}}</p>
                    <div style="
                        display: flex; 
                        justify-content: space-between; 
                        align-items: center; 
                        font-size: 12px; 
                        margin-top: 15px;
                    ">
                        <span style="color: #0066cc; font-weight: 500;">
                            📱 ${{ad.category}} • 🌐 PythonCoin Network
                        </span>
                        <span style="
                            background: linear-gradient(45deg, #28a745, #20c997); 
                            color: white; 
                            padding: 6px 12px; 
                            border-radius: 20px; 
                            font-size: 11px; 
                            font-weight: bold;
                        ">+${{ad.payout.toFixed(6)}} PYC per click</span>
                    </div>
                </div>
            ```;
            
            // Add hover effect
            const adElement = container.querySelector('.pyc-ad-container');
            if (adElement) {{
                adElement.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 8px 25px rgba(0,102,204,0.2)';
                }});
                adElement.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 4px 12px rgba(0,102,204,0.1)';
                }});
            }}
        }});
    }}
    
    function displayNoAdsMessage() {{
        const containers = document.querySelectorAll('[data-pyc-zone]');
        containers.forEach(container => {{
            container.innerHTML = `
                <div style="
                    border: 2px dashed #ccc; 
                    border-radius: 12px; 
                    padding: 30px; 
                    text-align: center; 
                    color: #666;
                    background: #f8f9fa;
                    margin: 15px 0;
                ">
                    <h3 style="margin: 0 0 10px 0; color: #0066cc;">🌐 PythonCoin Ad Network</h3>
                    <p style="margin: 0;">No ads available at the moment. The network is growing!</p>
                    <small style="color: #999;">Wallet: {self.wallet.address[:8] if self.wallet else 'Unknown'}...</small>
                </div>
            `;
        }});
    }}
    
    // Global click handler
    window.handlePYCAdClick = function(adId, zone) {{
        console.log('[PYC-WALLET] Ad clicked:', adId, 'in zone:', zone);
        
        const ad = PYC_WALLET_CONFIG.ads.find(a => a.id === adId);
        if (!ad) {{
            console.error('[PYC-WALLET] Ad not found:', adId);
            return;
        }}
        
        // Show earning animation
        showEarningPopup(ad.payout);
        
        // Send click data to wallet server
        fetch(PYC_WALLET_CONFIG.serverHost + '/click', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                ad_id: adId,
                developer: 'dev_' + PYC_WALLET_CONFIG.developerAddress.substring(0, 8),
                pythoncoin_address: PYC_WALLET_CONFIG.developerAddress,
                payout_amount: ad.payout,
                zone: zone,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                referrer: document.referrer || 'direct'
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            console.log('[PYC-WALLET] Click processed:', data);
            if (data.success) {{
                console.log('[PYC-WALLET] Payment sent:', data.amount, 'PYC');
                showSuccessMessage('Payment sent: ' + data.amount + ' PYC');
            }} else {{
                console.error('[PYC-WALLET] Payment failed:', data.error);
            }}
        }})
        .catch(error => {{
            console.error('[PYC-WALLET] Click error:', error);
        }});
        
        // Open the ad URL
        if (ad.click_url && ad.click_url !== '#') {{
            setTimeout(() => {{
                window.open(ad.click_url, '_blank');
            }}, 500);
        }}
    }};
    
    function showEarningPopup(amount) {{
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            z-index: 10001;
            text-align: center;
            font-family: Arial, sans-serif;
            font-weight: bold;
            box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
            animation: pycPopupAnimation 0.3s ease-out;
        `;
        
        popup.innerHTML = `
            <div style="font-size: 24px; margin-bottom: 5px;">💰</div>
            <div style="font-size: 18px;">PythonCoin Earned!</div>
            <div style="font-size: 14px; opacity: 0.9;">+${{amount.toFixed(6)}} PYC</div>
        `;
        
        // Add animation keyframes
        if (!document.querySelector('#pyc-popup-styles')) {{
            const style = document.createElement('style');
            style.id = 'pyc-popup-styles';
            style.textContent = `
                @keyframes pycPopupAnimation {{
                    0% {{ transform: translate(-50%, -50%) scale(0.8); opacity: 0; }}
                    100% {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }}
                }}
            `;
            document.head.appendChild(style);
        }}
        
        document.body.appendChild(popup);
        
        setTimeout(() => {{
            popup.style.animation = 'pycPopupAnimation 0.3s ease-out reverse';
            setTimeout(() => popup.remove(), 300);
        }}, 2500);
    }}
    
    function showSuccessMessage(message) {{
        console.log('[PYC-WALLET]', message);
        
        // Could add a toast notification here
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 3000);
    }}
    
    function startAdRotation() {{
        if (adRotationInterval) {{
            clearInterval(adRotationInterval);
        }}
        
        adRotationInterval = setInterval(() => {{
            currentAdIndex = (currentAdIndex + 1) % PYC_WALLET_CONFIG.ads.length;
            displayWalletAd(PYC_WALLET_CONFIG.ads[currentAdIndex]);
            console.log('[PYC-WALLET] Rotated to ad:', currentAdIndex);
        }}, 30000); // Rotate every 30 seconds
    }}
    
    function trackImpression() {{
        // Send impression tracking
        fetch(PYC_WALLET_CONFIG.serverHost + '/impression', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                developer: 'dev_' + PYC_WALLET_CONFIG.developerAddress.substring(0, 8),
                pythoncoin_address: PYC_WALLET_CONFIG.developerAddress,
                timestamp: new Date().toISOString(),
                ads_shown: PYC_WALLET_CONFIG.ads.length,
                user_agent: navigator.userAgent
            }})
        }})
        .catch(error => console.log('[PYC-WALLET] Impression tracking failed:', error));
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initPYCWalletAds);
    }} else {{
        initPYCWalletAds();
    }}
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {{
        if (adRotationInterval) {{
            clearInterval(adRotationInterval);
        }}
    }});
    
    console.log('[PYC-WALLET] PythonCoin ad network script loaded successfully');
    
}})();
'''
            
            # Save the generated JS to file
            filename = f"custm_{developer_address}_.js"
            filepath = os.path.join(self.js_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                print(f"Generated custom JS file: {filepath}")
            except Exception as e:
                print(f"Warning: Could not save JS file: {e}")
            
            return js_content
            
        except Exception as e:
            error_js = f"// Error generating custom JS: {str(e)}"
            print(f"Custom JS generation error: {e}")
            return error_js
    
    def handle_register_developer(self, data):
        """Handle developer registration"""
        try:
            developer = data.get('developer', '')
            pythoncoin_address = data.get('pythoncoin_address', '')
            
            if not developer or not pythoncoin_address:
                return json.dumps({'success': False, 'error': 'Missing developer or pythoncoin_address'})
            
            if not self.is_valid_pythoncoin_address(pythoncoin_address):
                return json.dumps({'success': False, 'error': 'Invalid PythonCoin address'})
            
            self.registered_developers[developer] = pythoncoin_address
            self.developer_registered.emit(developer, pythoncoin_address)
            
            self.status_update.emit(f"Developer registered: {developer} -> {pythoncoin_address[:8]}...")
            
            return json.dumps({'success': True, 'message': 'Developer registered successfully'})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_click(self, data):
        """Handle ad click and process payment"""
        try:
            ad_id = data.get('ad_id', '')
            developer = data.get('developer', '')
            pythoncoin_address = data.get('pythoncoin_address', '')
            payout_amount = float(data.get('payout_amount', 0.001))
            zone = data.get('zone', 'unknown')
            
            if not all([ad_id, developer, pythoncoin_address]):
                return json.dumps({'success': False, 'error': 'Missing required fields'})
            
            # Validate the payment
            if not self.wallet or not self.blockchain:
                return json.dumps({'success': False, 'error': 'Wallet or blockchain not available'})
            
            # Check if we have enough balance
            try:
                if hasattr(self.wallet, 'get_balance'):
                    balance = self.wallet.get_balance()
                elif hasattr(self.blockchain, 'get_balance'):
                    balance = self.blockchain.get_balance(self.wallet.address)
                else:
                    balance = 0
                    
                if balance < payout_amount:
                    return json.dumps({
                        'success': False, 
                        'error': f'Insufficient balance: {balance:.8f} < {payout_amount:.8f}'
                    })
            except Exception as e:
                print(f"Balance check error: {e}")
                balance = 0
            
            # Process the payment
            try:
                tx = self.wallet.send(pythoncoin_address, payout_amount)
                
                if tx:
                    payment_record = {
                        'developer': developer,
                        'address': pythoncoin_address,
                        'amount': payout_amount,
                        'ad_id': ad_id,
                        'zone': zone,
                        'tx_id': tx.tx_id,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.click_payments.append(payment_record)
                    
                    self.click_received.emit({
                        'ad_id': ad_id,
                        'developer': developer,
                        'amount': payout_amount,
                        'zone': zone,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.status_update.emit(f"💰 Click payment: {payout_amount:.6f} PYC -> {developer}")
                    
                    return json.dumps({
                        'success': True,
                        'payment_sent': True,
                        'transaction_id': tx.tx_id,
                        'amount': payout_amount,
                        'balance_after': balance - payout_amount
                    })
                else:
                    return json.dumps({'success': False, 'error': 'Failed to create transaction'})
                    
            except Exception as e:
                return json.dumps({'success': False, 'error': f'Payment failed: {str(e)}'})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_impression(self, data):
        """Handle ad impression tracking"""
        try:
            self.ads_served += 1
            self.status_update.emit(f"📊 Ad impression recorded (Total: {self.ads_served})")
            return json.dumps({'success': True, 'impressions': self.ads_served})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_get_ads(self):
        """Get available ads"""
        try:
            ads = self.get_available_ads()
            return json.dumps({
                'success': True,
                'ads': ads,
                'total': len(ads)
            })
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_stats(self):
        """Get server statistics"""
        try:
            stats = {
                'total_developers': len(self.registered_developers),
                'total_clicks': len(self.click_payments),
                'ads_served': self.ads_served,
                'available_ads': len(self.get_available_ads()),
                'server_uptime': '24h+',
                'wallet_address': self.wallet.address if self.wallet else '',
                'wallet_balance': float(self.wallet.get_balance()) if self.wallet else 0.0,
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                'server_port': self.port,
                'server_status': 'online' if self.running else 'offline'
            }
            
            return json.dumps({'success': True, 'stats': stats})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def get_available_ads(self):
        """Get list of available ads"""
        timestamp = int(datetime.now().timestamp() * 1000)
        
        ads = [
            {
                'id': f'pyc_wallet_ad_{timestamp}_1',
                'title': 'PythonCoin Mining Pool - Join the Network!',
                'description': 'Earn more PYC by joining our decentralized mining pool. Consistent payouts and low fees.',
                'category': 'cryptocurrency',
                'payout': 0.002,
                'click_url': 'https://pythoncoin-mining.example.com',
                'advertiser': 'PythonCoin Mining Collective',
                'created_at': timestamp,
                'expires_at': timestamp + (86400 * 30 * 1000)  # 30 days
            },
            {
                'id': f'pyc_wallet_ad_{timestamp}_2',
                'title': 'Learn Blockchain Development',
                'description': 'Master cryptocurrency and blockchain technology with hands-on courses. Start building DApps today.',
                'category': 'technology',
                'payout': 0.0015,
                'click_url': 'https://blockchain-academy.example.com',
                'advertiser': 'Blockchain Academy',
                'created_at': timestamp,
                'expires_at': timestamp + (86400 * 30 * 1000)
            },
            {
                'id': f'pyc_wallet_ad_{timestamp}_3',
                'title': 'Secure Hardware Wallet',
                'description': 'Protect your PythonCoin with military-grade security. Cold storage solutions for serious investors.',
                'category': 'cryptocurrency',
                'payout': 0.003,
                'click_url': 'https://secure-wallet.example.com',
                'advertiser': 'CryptoSecure',
                'created_at': timestamp,
                'expires_at': timestamp + (86400 * 30 * 1000)
            }
        ]
        
        return ads
    
    def is_valid_pythoncoin_address(self, address):
        """Validate PythonCoin address format"""
        return (address and 
                len(address) >= 26 and 
                len(address) <= 35 and 
                address.isalnum())
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server = None
        self.status_update.emit("Developer portal server stopped")

'''
        
        # Replace the class in the content
        new_content = before_class + new_server_class + after_class
        
        # Fix 2: Add missing imports if not present
        print("🔧 Adding missing imports...")
        
        imports_to_add = [
            "import json",
            "import os", 
            "from datetime import datetime"
        ]
        
        for import_line in imports_to_add:
            if import_line not in new_content:
                # Find the last import line and add after it
                import_pattern = r'(from [^\n]+ import [^\n]+\n|import [^\n]+\n)'
                matches = list(re.finditer(import_pattern, new_content))
                if matches:
                    last_match = matches[-1]
                    insert_pos = last_match.end()
                    new_content = new_content[:insert_pos] + import_line + "\n" + new_content[insert_pos:]
        
        # Fix 3: Update wallet server initialization to avoid aiohttp issues
        print("🔧 Fixing server initialization...")
        
        # Replace aiohttp imports with standard library
        new_content = re.sub(
            r'import aiohttp.*\n',
            '# aiohttp replaced with standard HTTP server\n',
            new_content
        )
        
        new_content = re.sub(
            r'from aiohttp import.*\n',
            '# aiohttp replaced with standard HTTP server\n',
            new_content
        )
        
        new_content = re.sub(
            r'import aiohttp_cors.*\n',
            '# aiohttp_cors replaced with manual CORS handling\n',
            new_content
        )
        
        # Fix 4: Update any aiohttp references in other parts of the code
        print("🔧 Cleaning up aiohttp references...")
        
        # Remove any async/await that might cause issues
        new_content = re.sub(
            r'async def ([^(]+\([^)]*\)):',
            r'def \1:',
            new_content
        )
        
        new_content = re.sub(
            r'await ([^(\n]+)',
            r'\1',
            new_content
        )
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ PythonCoin PyQt server fixes applied successfully!")
        print("\n🔧 Changes made:")
        print("  • Replaced problematic aiohttp server with standard HTTP server")
        print("  • Fixed JavaScript generation and serving functionality")
        print("  • Improved CORS handling for web requests")
        print("  • Enhanced error handling and logging")
        print("  • Added proper custom JS file generation")
        print("  • Fixed wallet balance integration")
        print("  • Added working payment processing")
        print("\n🚀 The server on port 8082 should now work correctly!")
        print(f"  • Original file backed up to: {backup_path}")
        print("  • Run the PyQt application and start the Developer Portal Server")
        print("  • Test by visiting: http://127.0.0.1:8082/client_info")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {str(e)}")
        print(f"Restoring from backup: {backup_path}")
        shutil.copy2(backup_path, file_path)
        return False

def create_test_html():
    """Create a test HTML file to verify the server works"""
    test_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonCoin Wallet Server Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        button {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin: 10px 5px;
        }
        button:hover {
            background: #218838;
        }
        .test-area {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        #results {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐍 PythonCoin Wallet Server Test</h1>
        <p>This page tests the PythonCoin wallet server on port 8082.</p>
        
        <div class="test-area">
            <h2>Server Tests</h2>
            <button onclick="testClientInfo()">Test Client Info</button>
            <button onclick="testCustomJS()">Test Custom JS</button>
            <button onclick="testStats()">Test Stats</button>
            <button onclick="testRegisterDev()">Test Register Developer</button>
            <button onclick="clearResults()">Clear Results</button>
        </div>
        
        <div class="test-area">
            <h2>Ad Zone Test</h2>
            <p>This is where ads from the PythonCoin wallet would appear:</p>
            <div data-pyc-zone="test-zone" style="min-height: 100px; border: 2px dashed rgba(255,255,255,0.3); padding: 20px; text-align: center;">
                Ad zone - Load custom JS to see ads here
            </div>
            <button onclick="loadCustomJS()">Load Custom JS</button>
        </div>
        
        <div class="test-area">
            <h2>Results</h2>
            <div id="results">Ready to test...</div>
        </div>
    </div>

    <script>
        const SERVER_URL = 'http://127.0.0.1:8082';
        
        function log(message) {
            const results = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            results.textContent += `[${timestamp}] ${message}\\n`;
            results.scrollTop = results.scrollHeight;
        }
        
        function clearResults() {
            document.getElementById('results').textContent = '';
        }
        
        async function testClientInfo() {
            try {
                log('Testing client info endpoint...');
                const response = await fetch(`${SERVER_URL}/client_info`);
                const data = await response.json();
                
                if (data.success) {
                    log('✅ Client info successful:');
                    log(JSON.stringify(data.client, null, 2));
                } else {
                    log('❌ Client info failed: ' + data.error);
                }
            } catch (error) {
                log('❌ Client info error: ' + error.message);
            }
        }
        
        async function testCustomJS() {
            try {
                log('Testing custom JS endpoint...');
                const response = await fetch(`${SERVER_URL}/custom_test123.js`);
                const jsCode = await response.text();
                
                if (jsCode.includes('PYC_WALLET_CONFIG')) {
                    log('✅ Custom JS generated successfully');
                    log('JS length: ' + jsCode.length + ' characters');
                } else {
                    log('❌ Custom JS generation failed');
                    log('Response: ' + jsCode.substring(0, 200) + '...');
                }
            } catch (error) {
                log('❌ Custom JS error: ' + error.message);
            }
        }
        
        async function testStats() {
            try {
                log('Testing stats endpoint...');
                const response = await fetch(`${SERVER_URL}/stats`);
                const data = await response.json();
                
                if (data.success) {
                    log('✅ Stats successful:');
                    log(JSON.stringify(data.stats, null, 2));
                } else {
                    log('❌ Stats failed: ' + data.error);
                }
            } catch (error) {
                log('❌ Stats error: ' + error.message);
            }
        }
        
        async function testRegisterDev() {
            try {
                log('Testing developer registration...');
                const response = await fetch(`${SERVER_URL}/register_developer`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        developer: 'test_developer',
                        pythoncoin_address: 'test123456789012345678901234567890'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    log('✅ Developer registration successful');
                    log('Message: ' + data.message);
                } else {
                    log('❌ Developer registration failed: ' + data.error);
                }
            } catch (error) {
                log('❌ Registration error: ' + error.message);
            }
        }
        
        async function loadCustomJS() {
            try {
                log('Loading custom JS into page...');
                
                // Create script element
                const script = document.createElement('script');
                script.src = `${SERVER_URL}/custom_test123.js`;
                script.onload = () => {
                    log('✅ Custom JS loaded successfully');
                    log('Check the ad zone above for advertisements');
                };
                script.onerror = () => {
                    log('❌ Failed to load custom JS');
                };
                
                document.head.appendChild(script);
            } catch (error) {
                log('❌ Load JS error: ' + error.message);
            }
        }
        
        log('PythonCoin Wallet Server Test Page Ready');
        log('Make sure the PyQt wallet is running with Developer Portal Server started');
    </script>
</body>
</html>'''
    
    with open('test_wallet_server.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✅ Created test_wallet_server.html")
    print("   Open this file in a web browser to test the server")

def main():
    """Main function to run the auto-fix"""
    print("🚀 PythonCoin PyQt Server Auto-Fix Script")
    print("=========================================")
    
    # Check if pyqt.py exists
    if not os.path.exists("pyqt.py"):
        print("❌ Error: pyqt.py not found in current directory")
        print("   Please run this script in the same directory as pyqt.py")
        return
    
    # Apply fixes
    success = fix_pyqt_server("pyqt.py")
    
    if success:
        print("\n🎉 Auto-fix completed successfully!")
        
        # Create test file
        create_test_html()
        
        print("\n📝 Next steps:")
        print("1. Run the fixed pyqt.py application")
        print("2. Go to the 'Developer Portal' tab")
        print("3. Click 'Start Portal Server'")
        print("4. Open test_wallet_server.html in a browser")
        print("5. Test the server functionality")
        print("\n🔧 If you encounter issues:")
        print("  • Check the PyQt application logs")
        print("  • Ensure no other service is using port 8082")
        print("  • Try restarting the application")
        
    else:
        print("\n❌ Auto-fix failed!")
        print("   Check the error messages above for details")

if __name__ == "__main__":
    main()
