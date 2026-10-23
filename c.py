#!/usr/bin/env python3
"""
Developer Portal Integration for PythonCoin Wallet
Makes the wallet work as a P2P ad client with the developer portal website
"""

import os
import sys
import re
import shutil
from datetime import datetime

class DeveloperPortalIntegration:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_portal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_made = []
        
    def create_backup(self):
        """Create backup of original file"""
        try:
            shutil.copy2(self.target_file, self.backup_filename)
            print(f"✅ Backup created: {self.backup_filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def read_file(self):
        """Read the target file"""
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Read file: {self.target_file} ({len(content)} characters)")
            return content
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return None
    
    def write_file(self, content):
        """Write the modified content back to file"""
        try:
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated file: {self.target_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to write file: {e}")
            return False

    def add_http_server_for_portal(self, content):
        """Add HTTP server to serve ads to developer portal"""
        print("🌐 Adding HTTP server for developer portal integration...")
        
        http_server_class = '''
# Developer Portal Integration - HTTP Server
class DeveloperPortalServer(QThread):
    """HTTP server for developer portal integration"""
    
    status_update = pyqtSignal(str)
    click_received = pyqtSignal(dict)
    developer_registered = pyqtSignal(str, str)
    
    def __init__(self, wallet, blockchain, port=8082):
        super().__init__()
        self.wallet = wallet
        self.blockchain = blockchain
        self.port = port
        self.running = False
        self.app = None
        self.registered_developers = {}
        self.click_payments = []
        
    def run(self):
        """Start the HTTP server for developer portal"""
        try:
            from aiohttp import web, ClientSession
            import aiohttp_cors
            import asyncio
            
            self.running = True
            self.status_update.emit(f"Starting developer portal server on port {self.port}")
            
            self.app = web.Application()
            
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Add routes
            self.app.router.add_get('/client_info', self.handle_client_info)
            self.app.router.add_get('/ads', self.handle_get_ads)
            self.app.router.add_post('/register_developer', self.handle_register_developer)
            self.app.router.add_get('/custom_{address}.js', self.handle_custom_js)
            self.app.router.add_post('/click', self.handle_click)
            self.app.router.add_post('/impression', self.handle_impression)
            self.app.router.add_get('/stats', self.handle_stats)
            self.app.router.add_options('/{path:.*}', self.handle_options)
            
            for route in list(self.app.router.routes()):
                cors.add(route)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            web.run_app(self.app, host='0.0.0.0', port=self.port, loop=loop)
            
        except Exception as e:
            self.status_update.emit(f"Developer portal server error: {str(e)}")
    
    async def handle_options(self, request):
        """Handle CORS preflight requests"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )
    
    async def handle_client_info(self, request):
        """Provide client information for portal discovery"""
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
            
            return web.json_response({
                'success': True,
                'client': client_info
            })
            
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            })
    
    async def handle_get_ads(self, request):
        """Get available ads for developers"""
        try:
            ads = self.get_available_ads()
            return web.json_response({
                'success': True,
                'ads': ads,
                'total': len(ads)
            })
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})
    
    async def handle_register_developer(self, request):
        """Register a developer for payments"""
        try:
            data = await request.json()
            developer = data.get('developer')
            pythoncoin_address = data.get('pythoncoin_address')
            
            if not developer or not pythoncoin_address:
                return web.json_response({'success': False, 'error': 'Missing developer or pythoncoin_address'})
            
            if not self.is_valid_pythoncoin_address(pythoncoin_address):
                return web.json_response({'success': False, 'error': 'Invalid PythonCoin address'})
            
            self.registered_developers[developer] = pythoncoin_address
            self.developer_registered.emit(developer, pythoncoin_address)
            
            self.status_update.emit(f"Developer registered: {developer} -> {pythoncoin_address[:8]}...")
            
            return web.json_response({'success': True, 'message': 'Developer registered successfully'})
            
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})
    
    async def handle_custom_js(self, request):
        """Generate custom JavaScript for specific developer"""
        try:
            path = request.path
            address_match = re.search(r'custom_([a-zA-Z0-9]+)\\.js', path)
            
            if not address_match:
                return web.Response(
                    text="// Error: Invalid custom JS request",
                    content_type='application/javascript'
                )
            
            developer_address = address_match.group(1)
            custom_js = self.generate_custom_js(developer_address)
            
            return web.Response(
                text=custom_js,
                content_type='application/javascript',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache'
                }
            )
            
        except Exception as e:
            return web.Response(
                text=f"// Error generating custom JS: {str(e)}",
                content_type='application/javascript'
            )
    
    async def handle_click(self, request):
        """Handle ad click and process payment"""
        try:
            data = await request.json()
            
            ad_id = data.get('ad_id')
            developer = data.get('developer')
            pythoncoin_address = data.get('pythoncoin_address')
            payout_amount = data.get('payout_amount', 0.001)
            zone = data.get('zone', 'unknown')
            
            if not all([ad_id, developer, pythoncoin_address]):
                return web.json_response({'success': False, 'error': 'Missing required fields'})
            
            payment_result = await self.process_click_payment(
                developer, pythoncoin_address, payout_amount, ad_id, zone
            )
            
            self.click_received.emit({
                'ad_id': ad_id,
                'developer': developer,
                'amount': payout_amount,
                'zone': zone,
                'timestamp': datetime.now().isoformat()
            })
            
            self.status_update.emit(f"💰 Click payment: {payout_amount:.6f} PYC -> {developer}")
            
            return web.json_response({
                'success': True,
                'payment_sent': payment_result,
                'transaction_id': payment_result.get('tx_id') if payment_result else None,
                'amount': payout_amount
            })
            
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})
    
    async def handle_impression(self, request):
        """Handle ad impression tracking"""
        try:
            data = await request.json()
            self.status_update.emit(f"📊 Ad impression: {data.get('ad_id', 'unknown')}")
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})
    
    async def handle_stats(self, request):
        """Get client statistics"""
        try:
            stats = {
                'total_developers': len(self.registered_developers),
                'total_clicks': len(self.click_payments),
                'available_ads': len(self.get_available_ads()),
                'server_uptime': '24h+',
                'wallet_address': self.wallet.address if self.wallet else '',
                'wallet_balance': float(self.wallet.get_balance()) if self.wallet else 0.0,
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0
            }
            
            return web.json_response({'success': True, 'stats': stats})
            
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})
    
    def get_available_ads(self):
        """Get list of available ads"""
        return [
            {
                'id': f'pyc_ad_{int(datetime.now().timestamp())}_1',
                'title': 'PythonCoin Mining Pool - Join Now!',
                'description': 'Earn more PYC with our mining pool. Low fees, instant payouts.',
                'category': 'cryptocurrency',
                'payout': 0.002,
                'click_url': 'https://pythoncoin-pool.example.com',
                'advertiser': 'PythonCoin Mining Pool',
                'expires_at': (datetime.now().timestamp() + 86400 * 30) * 1000
            },
            {
                'id': f'pyc_ad_{int(datetime.now().timestamp())}_2',
                'title': 'Blockchain Development Course',
                'description': 'Learn to build cryptocurrencies like PythonCoin.',
                'category': 'technology',
                'payout': 0.0015,
                'click_url': 'https://blockchain-course.example.com',
                'advertiser': 'Crypto Academy',
                'expires_at': (datetime.now().timestamp() + 86400 * 30) * 1000
            }
        ]
    
    def generate_custom_js(self, developer_address):
        """Generate custom JavaScript for a specific developer"""
        ads = self.get_available_ads()
        
        js_code = f"""// PythonCoin Wallet - Custom Ad JavaScript
// Generated for developer: {developer_address}
// Server: {self.wallet.address if self.wallet else 'Unknown'}

(function() {{
    'use strict';
    
    const PYC_WALLET_CONFIG = {{
        serverAddress: '{self.wallet.address if self.wallet else 'unknown'}',
        serverHost: '127.0.0.1:{self.port}',
        developerAddress: '{developer_address}',
        ads: {ads}
    }};
    
    let currentAdIndex = 0;
    
    function initPYCWalletAds() {{
        console.log('[PYC-WALLET] Loading ads from PythonCoin wallet server');
        
        if (PYC_WALLET_CONFIG.ads.length > 0) {{
            displayWalletAd(PYC_WALLET_CONFIG.ads[0]);
            startAdRotation();
        }}
    }}
    
    function displayWalletAd(ad) {{
        const containers = document.querySelectorAll('[data-pyc-zone]');
        
        containers.forEach(container => {{
            container.innerHTML = `
                <div style="border: 2px solid #0066cc; border-radius: 12px; padding: 20px; background: white; margin: 15px 0; cursor: pointer;">
                    <div style="position: absolute; top: 10px; right: 10px; background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px;">PYC</div>
                    <h3 style="color: #0066cc; margin: 0 0 10px 0;">${{ad.title}}</h3>
                    <p style="color: #666; margin: 0 0 15px 0;">${{ad.description}}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #0066cc; font-size: 0.9em;">${{ad.category}}</span>
                        <span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.8em;">+${{ad.payout.toFixed(6)}} PYC</span>
                    </div>
                </div>
            `;
            
            container.onclick = function() {{
                handleWalletAdClick(ad);
            }};
        }});
    }}
    
    function handleWalletAdClick(ad) {{
        console.log('[PYC-WALLET] Ad clicked:', ad.title);
        
        showEarningPopup(ad.payout);
        
        fetch('http://127.0.0.1:{self.port}/click', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                ad_id: ad.id,
                developer: 'developer_' + PYC_WALLET_CONFIG.developerAddress.substring(0, 8),
                pythoncoin_address: PYC_WALLET_CONFIG.developerAddress,
                payout_amount: ad.payout,
                zone: 'wallet_served'
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                console.log('[PYC-WALLET] Payment sent:', data.amount, 'PYC');
            }}
        }})
        .catch(error => console.error('[PYC-WALLET] Click error:', error));
        
        if (ad.click_url) {{
            window.open(ad.click_url, '_blank');
        }}
    }}
    
    function showEarningPopup(amount) {{
        const popup = document.createElement('div');
        popup.style.position = 'fixed';
        popup.style.top = '50%';
        popup.style.left = '50%';
        popup.style.transform = 'translate(-50%, -50%)';
        popup.style.background = '#28a745';
        popup.style.color = 'white';
        popup.style.padding = '20px 30px';
        popup.style.borderRadius = '15px';
        popup.style.zIndex = '10001';
        popup.style.textAlign = 'center';
        popup.style.fontWeight = 'bold';
        
        popup.innerHTML = `
            <div style="font-size: 18px;">💰 PythonCoin Earned!</div>
            <div style="font-size: 14px;">+${{amount.toFixed(6)}} PYC</div>
        `;
        
        document.body.appendChild(popup);
        
        setTimeout(() => {{
            popup.remove();
        }}, 3000);
    }}
    
    function startAdRotation() {{
        if (PYC_WALLET_CONFIG.ads.length <= 1) return;
        
        setInterval(() => {{
            currentAdIndex = (currentAdIndex + 1) % PYC_WALLET_CONFIG.ads.length;
            displayWalletAd(PYC_WALLET_CONFIG.ads[currentAdIndex]);
        }}, 30000);
    }}
    
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initPYCWalletAds);
    }} else {{
        initPYCWalletAds();
    }}
    
}})();
"""
        
        return js_code
        
        return js_code
    
    async def process_click_payment(self, developer, address, amount, ad_id, zone):
        """Process payment for ad click"""
        try:
            if not self.wallet or not self.blockchain:
                return None
            
            balance = self.wallet.get_balance()
            if balance < amount:
                self.status_update.emit(f"❌ Insufficient balance for payment: {balance:.6f} < {amount:.6f}")
                return None
            
            tx = self.wallet.send(address, amount)
            
            if tx:
                payment_record = {
                    'developer': developer,
                    'address': address,
                    'amount': amount,
                    'ad_id': ad_id,
                    'zone': zone,
                    'tx_id': tx.tx_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.click_payments.append(payment_record)
                
                return {
                    'success': True,
                    'tx_id': tx.tx_id,
                    'amount': amount
                }
            
            return None
            
        except Exception as e:
            self.status_update.emit(f"❌ Payment error: {str(e)}")
            return None
    
    def is_valid_pythoncoin_address(self, address):
        """Validate PythonCoin address format"""
        return (address and 
                len(address) >= 26 and 
                len(address) <= 35 and 
                address.isalnum())
    
    def stop(self):
        """Stop the developer portal server"""
        self.running = False
        self.status_update.emit("Developer portal server stopped")
'''
        
        # Find where to inject - before the main wallet class
        main_class_pattern = r'(class UnifiedPythonCoinWallet\(QMainWindow\):)'
        if re.search(main_class_pattern, content):
            content = re.sub(main_class_pattern, http_server_class + r'\n\n\1', content)
            self.changes_made.append("✅ Added developer portal HTTP server class")
        
        return content
    
    def add_portal_integration_to_wallet(self, content):
        """Add portal integration to the main wallet class"""
        print("🔗 Adding portal integration to wallet...")
        
        # Add portal server instance to __init__
        init_pattern = r'(# P2P Ad Network components\s*self\.client_id = str\(uuid\.uuid4\(\)\)\[:8\]\s*self\.port = 8082)'
        
        replacement = r'''\1
        
        # Developer Portal Integration
        self.portal_server = None
        self.portal_enabled = False'''
        
        if re.search(init_pattern, content):
            content = re.sub(init_pattern, replacement, content)
            self.changes_made.append("✅ Added portal server instance to wallet init")
        
        return content
    
    def add_portal_tab_to_ui(self, content):
        """Add developer portal tab to the UI"""
        print("🎮 Adding developer portal tab...")
        
        # Add portal tab to tab creation
        tab_creation_pattern = r'(self\.create_network_tab\(\)\s*self\.create_ad_creation_tab\(\))'
        
        replacement = r'''\1
        self.create_developer_portal_tab()'''
        
        if re.search(tab_creation_pattern, content):
            content = re.sub(tab_creation_pattern, replacement, content)
            self.changes_made.append("✅ Added developer portal tab creation call")
        
        return content
    
    def add_portal_tab_method(self, content):
        """Add the developer portal tab method"""
        print("📱 Adding developer portal tab method...")
        
        portal_tab_method = '''
    def create_developer_portal_tab(self):
        """Create developer portal integration tab"""
        portal_widget = QWidget()
        portal_layout = QVBoxLayout()
        portal_widget.setLayout(portal_layout)
        
        # Portal server status
        server_group = QGroupBox("🌐 Developer Portal Server")
        server_layout = QVBoxLayout()
        
        self.portal_status = QLabel("Status: Offline")
        self.portal_status.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        server_layout.addWidget(self.portal_status)
        
        # Server controls
        server_controls = QHBoxLayout()
        
        self.start_portal_btn = QPushButton("🚀 Start Portal Server")
        self.start_portal_btn.clicked.connect(self.start_portal_server)
        server_controls.addWidget(self.start_portal_btn)
        
        self.stop_portal_btn = QPushButton("⏹️ Stop Portal Server")
        self.stop_portal_btn.clicked.connect(self.stop_portal_server)
        self.stop_portal_btn.setEnabled(False)
        server_controls.addWidget(self.stop_portal_btn)
        
        test_portal_btn = QPushButton("🔧 Test Server")
        test_portal_btn.clicked.connect(self.test_portal_server)
        server_controls.addWidget(test_portal_btn)
        
        server_layout.addLayout(server_controls)
        server_group.setLayout(server_layout)
        portal_layout.addWidget(server_group)
        
        # Developer registration
        dev_group = QGroupBox("👥 Registered Developers")
        dev_layout = QVBoxLayout()
        
        self.developers_table = QTableWidget()
        self.developers_table.setColumnCount(4)
        self.developers_table.setHorizontalHeaderLabels(["Developer", "Address", "Clicks", "Earnings"])
        
        dev_header = self.developers_table.horizontalHeader()
        dev_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        dev_layout.addWidget(self.developers_table)
        dev_group.setLayout(dev_layout)
        portal_layout.addWidget(dev_group)
        
        # Portal statistics
        stats_group = QGroupBox("📊 Portal Statistics")
        stats_layout = QFormLayout()
        
        self.total_developers_label = QLabel("0")
        stats_layout.addRow("Total Developers:", self.total_developers_label)
        
        self.total_clicks_label = QLabel("0")
        stats_layout.addRow("Total Clicks:", self.total_clicks_label)
        
        self.total_payments_label = QLabel("0.00000000 PYC")
        stats_layout.addRow("Total Payments:", self.total_payments_label)
        
        stats_group.setLayout(stats_layout)
        portal_layout.addWidget(stats_group)
        
        self.tab_widget.addTab(portal_widget, "🌐 Developer Portal")
'''
        
        # Add before signal handlers
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, portal_tab_method + r'\1', content)
            self.changes_made.append("✅ Added developer portal tab method")
        
        return content
    
    def add_portal_server_methods(self, content):
        """Add portal server control methods"""
        print("⚙️ Adding portal server control methods...")
        
        portal_methods = '''
    # Developer Portal Server Methods
    def start_portal_server(self):
        """Start the developer portal server"""
        if not self.wallet:
            QMessageBox.warning(self, "Portal Error", "No wallet loaded")
            return
        
        if self.portal_server and self.portal_server.isRunning():
            QMessageBox.information(self, "Portal Info", "Portal server is already running")
            return
        
        try:
            self.portal_server = DeveloperPortalServer(self.wallet, self.blockchain, 8082)
            
            self.portal_server.status_update.connect(self.on_portal_status_update)
            self.portal_server.click_received.connect(self.on_portal_click_received)
            self.portal_server.developer_registered.connect(self.on_developer_registered)
            
            self.portal_server.start()
            
            self.portal_enabled = True
            self.portal_status.setText("Status: Starting...")
            self.start_portal_btn.setEnabled(False)
            self.stop_portal_btn.setEnabled(True)
            
            self.log_message("Developer portal server starting...")
            
        except Exception as e:
            self.log_message(f"Error starting portal server: {str(e)}")
            QMessageBox.critical(self, "Portal Error", f"Failed to start server: {str(e)}")
    
    def stop_portal_server(self):
        """Stop the developer portal server"""
        try:
            if self.portal_server:
                self.portal_server.stop()
                self.portal_server.wait()
                self.portal_server = None
            
            self.portal_enabled = False
            self.portal_status.setText("Status: Offline")
            self.start_portal_btn.setEnabled(True)
            self.stop_portal_btn.setEnabled(False)
            
            self.log_message("Developer portal server stopped")
            
        except Exception as e:
            self.log_message(f"Error stopping portal server: {str(e)}")
    
    def test_portal_server(self):
        """Test the portal server connection"""
        try:
            import urllib.request
            import json
            
            if not self.portal_enabled:
                QMessageBox.warning(self, "Test Error", "Portal server is not running")
                return
            
            url = "http://127.0.0.1:8082/client_info"
            
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                client_info = data.get('client', {})
                
                QMessageBox.information(self, "Portal Test Success", 
                                       f"✅ Portal server is working!\\n\\n"
                                       f"Client Name: {client_info.get('name', 'Unknown')}\\n"
                                       f"Available Ads: {client_info.get('ad_count', 0)}")
                
                self.log_message("Portal server test successful")
            else:
                QMessageBox.warning(self, "Test Failed", "Portal server returned error")
                
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Portal test failed: {str(e)}")
    
    def on_portal_status_update(self, status):
        """Handle portal server status updates"""
        self.log_message(f"Portal: {status}")
        
        if "server started" in status.lower() or "running" in status.lower():
            self.portal_status.setText("Status: Online ✅")
        elif "error" in status.lower():
            self.portal_status.setText("Status: Error ❌")
    
    def on_portal_click_received(self, click_data):
        """Handle ad click from portal"""
        developer = click_data.get('developer', 'Unknown')
        amount = click_data.get('amount', 0)
        
        self.log_message(f"💰 Portal click: {amount:.6f} PYC -> {developer}")
        self.update_portal_stats()
        
        if hasattr(self, 'save_blockchain'):
            self.save_blockchain()
    
    def on_developer_registered(self, developer, address):
        """Handle developer registration"""
        self.log_message(f"👤 Developer registered: {developer} -> {address[:8]}...")
        self.update_developers_table()
    
    def update_developers_table(self):
        """Update the developers table display"""
        if not hasattr(self, 'developers_table') or not self.portal_server:
            return
        
        developers = getattr(self.portal_server, 'registered_developers', {})
        payments = getattr(self.portal_server, 'click_payments', [])
        
        self.developers_table.setRowCount(len(developers))
        
        for row, (developer, address) in enumerate(developers.items()):
            self.developers_table.setItem(row, 0, QTableWidgetItem(developer))
            self.developers_table.setItem(row, 1, QTableWidgetItem(f"{address[:8]}..."))
            
            dev_clicks = len([p for p in payments if p.get('developer') == developer])
            self.developers_table.setItem(row, 2, QTableWidgetItem(str(dev_clicks)))
            
            dev_earnings = sum(p.get('amount', 0) for p in payments if p.get('developer') == developer)
            self.developers_table.setItem(row, 3, QTableWidgetItem(f"{dev_earnings:.8f} PYC"))(p.get('amount', 0) for p in payments if p.get('developer') == developer)
            self.developers_table.setItem(row, 3, QTableWidgetItem(f"{dev_earnings:.8f} PYC"))
    
    def update_portal_stats(self):
        """Update portal statistics display"""
        if not hasattr(self, 'total_developers_label') or not self.portal_server:
            return
        
        developers = getattr(self.portal_server, 'registered_developers', {})
        payments = getattr(self.portal_server, 'click_payments', [])
        
        self.total_developers_label.setText(str(len(developers)))
        self.total_clicks_label.setText(str(len(payments)))
        
        total_paid = sum(p.get('amount', 0) for p in payments)
        self.total_payments_label.setText(f"{total_paid:.8f} PYC")
'''
        
        # Add before the end of the class (look for common end patterns)
        class_end_patterns = [
            r'(\s*def closeEvent\(self, event\):)',
            r'(\s*def main\(\):)',
            r'(\s*if __name__ == "__main__":)',
            r'(\s*# End of class)',
            r'(\s*$)'  # End of file
        ]
        
        inserted = False
        for pattern in class_end_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, portal_methods + r'\n\1', content, count=1)
                self.changes_made.append("✅ Added portal server control methods")
                inserted = True
                break
        
        if not inserted:
            # If no pattern found, append to end
            content += portal_methods
            self.changes_made.append("✅ Added portal server control methods (appended to end)")
        
        return content
    
    def add_cleanup_to_close_event(self, content):
        """Add portal cleanup to window close event"""
        print("🧹 Adding portal cleanup to close event...")
        
        # Look for existing closeEvent method
        close_event_pattern = r'(def closeEvent\(self, event\):\s*(?:.*?\n)*?\s*)(event\.accept\(\))'
        
        replacement = r'''\1        # Stop portal server if running
        if hasattr(self, 'portal_server') and self.portal_server:
            self.stop_portal_server()
        
        \2'''
        
        if re.search(close_event_pattern, content, re.MULTILINE | re.DOTALL):
            content = re.sub(close_event_pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            self.changes_made.append("✅ Added portal cleanup to existing closeEvent")
        else:
            # If no closeEvent exists, create one
            close_event_method = '''
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop portal server if running
        if hasattr(self, 'portal_server') and self.portal_server:
            self.stop_portal_server()
        
        event.accept()
'''
            
            # Add before main() or end of class
            main_pattern = r'(\ndef main\(\):|\nif __name__ == "__main__":)'
            if re.search(main_pattern, content):
                content = re.sub(main_pattern, close_event_method + r'\1', content)
                self.changes_made.append("✅ Added new closeEvent method with portal cleanup")
            else:
                content += close_event_method
                self.changes_made.append("✅ Added closeEvent method (appended)")
        
        return content
    
    def add_imports(self, content):
        """Add necessary imports for portal functionality"""
        print("📦 Adding required imports...")
        
        # Check if imports already exist
        required_imports = [
            'import uuid',
            'import threading',
            'from datetime import datetime',
            'from PyQt5.QtCore import QThread, pyqtSignal'
        ]
        
        imports_to_add = []
        for imp in required_imports:
            if imp not in content:
                imports_to_add.append(imp)
        
        if imports_to_add:
            # Find existing import section
            import_pattern = r'((?:import|from).*?\n)+'
            
            if re.search(import_pattern, content):
                # Add to existing imports
                new_imports = '\n'.join(imports_to_add) + '\n'
                content = re.sub(import_pattern, lambda m: m.group(0) + new_imports, content, count=1)
                self.changes_made.append(f"✅ Added {len(imports_to_add)} required imports")
            else:
                # Add at beginning
                new_imports = '\n'.join(imports_to_add) + '\n\n'
                content = new_imports + content
                self.changes_made.append(f"✅ Added imports at beginning of file")
        
        return content
    
    def integrate_portal(self):
        """Main integration method"""
        print("🚀 Starting PythonCoin Developer Portal Integration...")
        print("=" * 60)
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Read original file
        content = self.read_file()
        if not content:
            return False
        
        print(f"📋 Original file size: {len(content):,} characters")
        
        # Apply all modifications
        try:
            content = self.add_imports(content)
            content = self.add_http_server_for_portal(content)
            content = self.add_portal_integration_to_wallet(content)
            content = self.add_portal_tab_to_ui(content)
            content = self.add_portal_tab_method(content)
            content = self.add_portal_server_methods(content)
            content = self.add_cleanup_to_close_event(content)
            
            print(f"📋 Modified file size: {len(content):,} characters")
            
            # Write modified file
            if self.write_file(content):
                print("\n" + "=" * 60)
                print("🎉 INTEGRATION COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                
                print("\n📋 Changes Made:")
                for change in self.changes_made:
                    print(f"  {change}")
                
                print(f"\n💾 Backup saved as: {self.backup_filename}")
                print(f"✅ Modified file: {self.target_file}")
                
                print("\n🔧 Next Steps:")
                print("1. Install required dependencies:")
                print("   pip install aiohttp aiohttp-cors")
                print("2. Run your PythonCoin wallet:")
                print(f"   python {self.target_file}")
                print("3. Navigate to the '🌐 Developer Portal' tab")
                print("4. Click '🚀 Start Portal Server' to begin")
                print("5. Test with '🔧 Test Server' button")
                
                print("\n🌐 Portal Features:")
                print("• HTTP server on port 8082")
                print("• Automatic ad serving to developers")
                print("• PythonCoin payments for ad clicks")
                print("• Developer registration system")
                print("• Real-time statistics dashboard")
                print("• Custom JavaScript generation")
                
                print("\n⚠️  Important Notes:")
                print("• Ensure your wallet has sufficient PYC balance for payments")
                print("• Port 8082 must be available and not blocked by firewall")
                print("• Developers can register at: http://localhost:8082/")
                print("• All transactions are recorded on the blockchain")
                
                return True
            else:
                print("❌ Failed to write modified file")
                return False
                
        except Exception as e:
            print(f"❌ Integration failed: {str(e)}")
            return False

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PythonCoin Developer Portal Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python integrate_portal.py                    # Integrate with default pyqt.py
  python integrate_portal.py -f wallet.py      # Integrate with custom file
  python integrate_portal.py --target my_wallet.py  # Alternative syntax

This script will:
1. Create a backup of your original file
2. Add a complete developer portal integration
3. Enable P2P advertising with automatic payments
4. Provide a web API for developers to integrate ads

The integration adds:
• HTTP server for ad serving (port 8082)
• Developer registration system
• Automatic PythonCoin payments for ad clicks
• Statistics dashboard and management UI
• Custom JavaScript generation for developers
        """
    )
    
    parser.add_argument(
        '-f', '--file', '--target',
        dest='target_file',
        default='pyqt.py',
        help='Target PyQt wallet file to modify (default: pyqt.py)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='PythonCoin Developer Portal Integration v1.0'
    )
    
    args = parser.parse_args()
    
    print("🪙 PythonCoin Developer Portal Integration")
    print("=" * 50)
    print(f"Target file: {args.target_file}")
    print()
    
    # Check if target file exists
    if not os.path.exists(args.target_file):
        print(f"❌ Error: Target file '{args.target_file}' not found!")
        print("\nMake sure you're in the correct directory and the file exists.")
        print("You can specify a different file with: -f filename.py")
        return 1
    
    # Create integrator and run
    integrator = DeveloperPortalIntegration(args.target_file)
    
    try:
        success = integrator.integrate_portal()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Integration cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nIf this persists, please check:")
        print("1. File permissions are correct")
        print("2. Target file is a valid Python file")
        print("3. You have write access to the directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())