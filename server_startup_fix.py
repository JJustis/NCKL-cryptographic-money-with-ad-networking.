#!/usr/bin/env python3
"""
HTTP Server Startup Fix for PythonCoin PyQt Wallet
Fixes the "urlopen error: no connection could be made" issue
"""

import os
import re
import shutil
import socket
from datetime import datetime

def check_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=8082, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if check_port_available(port):
            return port
    return None

def inject_server_fixes():
    """Inject HTTP server startup fixes into pyqt.py"""
    
    # Backup original file
    if os.path.exists('pyqt.py'):
        backup_name = f'pyqt_server_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('pyqt.py', backup_name)
        print(f"✅ Backed up original file to: {backup_name}")
    
    # Read the original file
    with open('pyqt.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Enhanced HTTP server implementation
    enhanced_server_code = '''
class EnhancedDeveloperPortalServer(QThread):
    """Enhanced HTTP server with proper error handling and port management"""
    
    status_update = pyqtSignal(str)
    click_received = pyqtSignal(dict)
    developer_registered = pyqtSignal(str, str)
    client_notification = pyqtSignal(dict)
    
    def __init__(self, wallet, blockchain, port=8082):
        super().__init__()
        self.wallet = wallet
        self.blockchain = blockchain
        self.requested_port = port
        self.actual_port = None
        self.running = False
        self.server = None
        self.httpd = None
        self.registered_developers = {}
        self.click_payments = []
        self.ads_served = 0
        self.active_clients = {}
        self.js_file_hashes = {}
        
        # Database integration
        self.db_manager = None
        self.wallet_instance = None
        
        # Create directories
        self.js_dir = os.path.join(os.getcwd(), 'js')
        self.client_ads_dir = os.path.join(os.getcwd(), 'client_ads')
        self.notifications_dir = os.path.join(os.getcwd(), 'notifications')
        
        for directory in [self.js_dir, self.client_ads_dir, self.notifications_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def check_port_available(self, port):
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    def find_available_port(self, start_port=8082, max_attempts=10):
        """Find an available port starting from start_port"""
        for i in range(max_attempts):
            port = start_port + i
            if self.check_port_available(port):
                return port
        return None
    
    def run(self):
        """Start the enhanced HTTP server with proper error handling"""
        try:
            from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
            import urllib.parse
            import socketserver
            import threading
            
            self.running = True
            
            # Find available port
            available_port = self.find_available_port(self.requested_port)
            if not available_port:
                self.status_update.emit(f"❌ No available ports found starting from {self.requested_port}")
                return
            
            self.actual_port = available_port
            if available_port != self.requested_port:
                self.status_update.emit(f"⚠️ Port {self.requested_port} busy, using port {available_port}")
            
            self.status_update.emit(f"🚀 Starting server on 127.0.0.1:{self.actual_port}")
            
            class EnhancedPythonCoinHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.server_instance = kwargs.pop('server_instance', None)
                    super().__init__(*args, **kwargs)
                
                def log_message(self, format, *args):
                    pass  # Suppress default logging
                
                def do_OPTIONS(self):
                    """Handle CORS preflight requests"""
                    try:
                        self.send_response(200)
                        self.send_cors_headers()
                        self.end_headers()
                    except Exception as e:
                        self.server_instance.status_update.emit(f"OPTIONS error: {str(e)}")
                
                def send_cors_headers(self):
                    """Send CORS headers"""
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
                
                def do_GET(self):
                    """Handle GET requests with enhanced error handling"""
                    try:
                        parsed_path = urllib.parse.urlparse(self.path)
                        path = parsed_path.path
                        query = urllib.parse.parse_qs(parsed_path.query)
                        
                        self.send_response(200)
                        self.send_cors_headers()
                        
                        # Route handling with error protection
                        if path == '/':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            status_response = json.dumps({
                                'status': 'PythonCoin Portal Server Active',
                                'port': self.server_instance.actual_port,
                                'wallet': self.server_instance.wallet.address[:8] + '...' if self.server_instance.wallet else 'None',
                                'blockchain_height': len(self.server_instance.blockchain.chain) if self.server_instance.blockchain else 0,
                                'server_time': datetime.now().isoformat(),
                                'endpoints': [
                                    '/client_info', '/discover_clients', '/active_clients',
                                    '/custom_ADDRESS.js', '/verify_js/FILENAME',
                                    '/notifications', '/ads', '/stats', '/portal'
                                ]
                            })
                            self.wfile.write(status_response.encode())
                            
                        elif path == '/client_info':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_client_info()
                            self.wfile.write(response.encode())
                            
                        elif path == '/test':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            test_response = json.dumps({
                                'success': True,
                                'message': 'Server is working!',
                                'port': self.server_instance.actual_port,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.wfile.write(test_response.encode())
                            
                        elif path == '/portal':
                            self.send_header('Content-Type', 'text/html')
                            self.end_headers()
                            html_content = self.server_instance.generate_developer_portal_html()
                            self.wfile.write(html_content.encode())
                            
                        elif path == '/stats':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_stats()
                            self.wfile.write(response.encode())
                            
                        else:
                            # Default response for unknown paths
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            default_response = json.dumps({
                                'status': 'endpoint_not_found',
                                'available_endpoints': ['/test', '/client_info', '/portal', '/stats']
                            })
                            self.wfile.write(default_response.encode())
                            
                    except Exception as e:
                        try:
                            self.send_response(500)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            error_response = json.dumps({'success': False, 'error': str(e)})
                            self.wfile.write(error_response.encode())
                        except:
                            pass
                        self.server_instance.status_update.emit(f"GET error: {str(e)}")
                
                def do_POST(self):
                    """Handle POST requests with enhanced error handling"""
                    try:
                        content_length = int(self.headers.get('Content-Length', 0))
                        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
                        
                        try:
                            data = json.loads(post_data.decode('utf-8'))
                        except:
                            data = {}
                        
                        self.send_response(200)
                        self.send_cors_headers()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        
                        path = urllib.parse.urlparse(self.path).path
                        
                        if path == '/register_developer':
                            response = self.server_instance.handle_register_developer(data)
                        elif path == '/click':
                            response = self.server_instance.handle_click(data)
                        elif path == '/impression':
                            response = self.server_instance.handle_impression(data)
                        else:
                            response = json.dumps({'success': False, 'error': 'Unknown endpoint'})
                        
                        self.wfile.write(response.encode())
                        
                    except Exception as e:
                        try:
                            self.send_response(500)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            error_response = json.dumps({'success': False, 'error': str(e)})
                            self.wfile.write(error_response.encode())
                        except:
                            pass
                        self.server_instance.status_update.emit(f"POST error: {str(e)}")
            
            # Create handler factory
            def handler_factory(*args, **kwargs):
                return EnhancedPythonCoinHandler(*args, server_instance=self, **kwargs)
            
            # Use ThreadingHTTPServer for better performance
            class OptimizedServer(ThreadingHTTPServer):
                allow_reuse_address = True
                daemon_threads = True
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.timeout = 1.0
            
            # Create and start server
            try:
                self.httpd = OptimizedServer(('127.0.0.1', self.actual_port), handler_factory)
                self.httpd.timeout = 1.0
                
                self.status_update.emit(f"✅ Server created successfully on port {self.actual_port}")
                
                # Test the server immediately
                self.test_server_connection()
                
                # Start serving requests
                while self.running:
                    try:
                        self.httpd.handle_request()
                    except OSError as e:
                        if self.running:  # Only log if we're supposed to be running
                            self.status_update.emit(f"Server handle error: {str(e)}")
                            break
                    except Exception as e:
                        if self.running:
                            self.status_update.emit(f"Server error: {str(e)}")
                        break
                        
            except OSError as e:
                self.status_update.emit(f"❌ Failed to bind to port {self.actual_port}: {str(e)}")
                self.running = False
            except Exception as e:
                self.status_update.emit(f"❌ Server creation failed: {str(e)}")
                self.running = False
                
        except ImportError as e:
            self.status_update.emit(f"❌ Import error: {str(e)}")
            self.running = False
        except Exception as e:
            self.status_update.emit(f"❌ Server startup failed: {str(e)}")
            self.running = False
        finally:
            if self.httpd:
                try:
                    self.httpd.server_close()
                except:
                    pass
            self.status_update.emit("🛑 Server stopped")
    
    def test_server_connection(self):
        """Test server connection after startup"""
        try:
            import urllib.request
            import time
            
            # Give server a moment to fully start
            time.sleep(0.5)
            
            test_url = f"http://127.0.0.1:{self.actual_port}/test"
            
            req = urllib.request.Request(test_url)
            req.add_header('User-Agent', 'PythonCoin-Test')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('success'):
                    self.status_update.emit(f"✅ Server test successful on port {self.actual_port}")
                    return True
                    
        except Exception as e:
            self.status_update.emit(f"⚠️ Server test failed: {str(e)}")
            return False
    
    def handle_client_info(self):
        """Handle client info requests"""
        try:
            client_info = {
                'client_id': f'pyc_{self.wallet.address[:8]}' if self.wallet else 'pyc_unknown',
                'name': f'PythonCoin Wallet - {self.wallet.address[:8]}...' if self.wallet else 'PythonCoin Wallet',
                'status': 'online',
                'host': '127.0.0.1',
                'port': self.actual_port,
                'wallet_address': self.wallet.address if self.wallet else '',
                'server_version': '2.1.0',
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            return json.dumps({'success': True, 'client': client_info})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_stats(self):
        """Get server statistics"""
        try:
            stats = {
                'server_port': self.actual_port,
                'server_status': 'online' if self.running else 'offline',
                'wallet_address': self.wallet.address if self.wallet else '',
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                'ads_served': self.ads_served,
                'registered_developers': len(self.registered_developers),
                'total_clicks': len(self.click_payments),
                'last_updated': datetime.now().isoformat()
            }
            
            return json.dumps({'success': True, 'stats': stats})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_register_developer(self, data):
        """Handle developer registration"""
        try:
            developer = data.get('developer', '')
            pythoncoin_address = data.get('pythoncoin_address', '')
            
            if not developer or not pythoncoin_address:
                return json.dumps({'success': False, 'error': 'Missing developer or pythoncoin_address'})
            
            self.registered_developers[developer] = pythoncoin_address
            self.developer_registered.emit(developer, pythoncoin_address)
            
            return json.dumps({'success': True, 'message': 'Developer registered successfully'})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_click(self, data):
        """Handle ad click"""
        try:
            click_data = {
                'developer': data.get('developer', 'Unknown'),
                'amount': float(data.get('payout_amount', 0.001)),
                'ad_id': data.get('ad_id', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            self.click_payments.append(click_data)
            self.click_received.emit(click_data)
            
            return json.dumps({
                'success': True,
                'payment_processing': True,
                'amount': click_data['amount']
            })
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_impression(self, data):
        """Handle ad impression"""
        try:
            self.ads_served += 1
            return json.dumps({'success': True, 'impressions': self.ads_served})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def generate_developer_portal_html(self):
        """Generate developer portal HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>PythonCoin Developer Portal</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #0066cc; }}
        .status {{ padding: 10px; background: #d4edda; border-radius: 5px; margin: 20px 0; }}
        .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        button {{ background: #0066cc; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 PythonCoin Developer Portal</h1>
        
        <div class="status">
            ✅ Server is running on port {self.actual_port}
        </div>
        
        <div class="info">
            <h3>Server Information</h3>
            <p><strong>Status:</strong> Online</p>
            <p><strong>Port:</strong> {self.actual_port}</p>
            <p><strong>Wallet:</strong> {self.wallet.address[:16] + '...' if self.wallet else 'None'}</p>
            <p><strong>Blockchain Height:</strong> {len(self.blockchain.chain) if self.blockchain else 0}</p>
            <p><strong>Ads Served:</strong> {self.ads_served}</p>
            <p><strong>Registered Developers:</strong> {len(self.registered_developers)}</p>
        </div>
        
        <div class="info">
            <h3>API Endpoints</h3>
            <ul>
                <li><code>GET /test</code> - Test server connection</li>
                <li><code>GET /client_info</code> - Get client information</li>
                <li><code>GET /stats</code> - Get server statistics</li>
                <li><code>POST /register_developer</code> - Register as developer</li>
                <li><code>POST /click</code> - Record ad click</li>
                <li><code>POST /impression</code> - Record ad impression</li>
            </ul>
        </div>
        
        <button onclick="testConnection()">Test Connection</button>
        <button onclick="getStats()">Get Stats</button>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
            function testConnection() {{
                fetch('/test')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('result').innerHTML = 
                            '<div class="status">✅ Connection test successful!</div>';
                    }})
                    .catch(error => {{
                        document.getElementById('result').innerHTML = 
                            '<div style="background: #f8d7da; padding: 10px; border-radius: 5px;">❌ Connection failed: ' + error + '</div>';
                    }});
            }}
            
            function getStats() {{
                fetch('/stats')
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            document.getElementById('result').innerHTML = 
                                '<div class="info"><h4>Current Stats:</h4><pre>' + JSON.stringify(data.stats, null, 2) + '</pre></div>';
                        }}
                    }})
                    .catch(error => {{
                        document.getElementById('result').innerHTML = 
                            '<div style="background: #f8d7da; padding: 10px; border-radius: 5px;">❌ Stats failed: ' + error + '</div>';
                    }});
            }}
        </script>
    </div>
</body>
</html>"""
    
    def stop(self):
        """Properly stop the server"""
        try:
            self.running = False
            
            if self.httpd:
                try:
                    self.httpd.shutdown()
                    self.httpd.server_close()
                except:
                    pass
                self.httpd = None
            
            self.status_update.emit("🛑 Portal server stopped")
            
        except Exception as e:
            self.status_update.emit(f"Error stopping server: {str(e)}")
'''

    # Enhanced start_portal_server method
    enhanced_start_method = '''
    def start_portal_server(self):
        """Start the enhanced developer portal server with better error handling"""
        if not self.wallet:
            QMessageBox.warning(self, "Portal Error", "No wallet loaded")
            return
        
        if self.portal_server and self.portal_server.isRunning():
            self.log_message("Portal server is already running")
            return
        
        try:
            # Stop any existing server first
            if self.portal_server:
                self.stop_portal_server()
                self.portal_server.wait(2000)  # Wait for cleanup
            
            self.log_message("🚀 Creating enhanced portal server...")
            
            # Create enhanced portal server
            self.portal_server = EnhancedDeveloperPortalServer(
                wallet=self.wallet, 
                blockchain=self.blockchain, 
                port=8082
            )
            
            # Pass database manager to server
            if hasattr(self, 'db_manager') and self.db_manager:
                self.portal_server.db_manager = self.db_manager
                self.portal_server.wallet_instance = self
            
            # Connect signals
            self.portal_server.status_update.connect(self.on_portal_status_update)
            self.portal_server.click_received.connect(self.on_portal_click_received)
            self.portal_server.developer_registered.connect(self.on_developer_registered)
            
            # Start the server
            self.log_message("🔄 Starting portal server thread...")
            self.portal_server.start()
            
            # Update UI state
            self.portal_enabled = True
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Starting...")
            if hasattr(self, 'start_portal_btn'):
                self.start_portal_btn.setEnabled(False)
            if hasattr(self, 'stop_portal_btn'):
                self.stop_portal_btn.setEnabled(True)
            
            self.log_message("✅ Portal server startup initiated")
            
            # Test connection after a delay
            QTimer.singleShot(3000, self.test_portal_connection)
            
        except Exception as e:
            self.log_message(f"❌ Error starting portal server: {str(e)}")
            QMessageBox.critical(self, "Portal Error", f"Failed to start server: {str(e)}")
            
            # Reset UI state on failure
            self.portal_enabled = False
            if hasattr(self, 'start_portal_btn'):
                self.start_portal_btn.setEnabled(True)
            if hasattr(self, 'stop_portal_btn'):
                self.stop_portal_btn.setEnabled(False)
    
    def test_portal_connection(self):
        """Test portal connection after startup"""
        try:
            if not self.portal_server:
                return
            
            actual_port = getattr(self.portal_server, 'actual_port', 8082)
            
            import urllib.request
            test_url = f"http://127.0.0.1:{actual_port}/test"
            
            req = urllib.request.Request(test_url)
            req.add_header('User-Agent', 'PythonCoin-Wallet-Test')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('success'):
                    self.log_message(f"✅ Portal server test successful on port {actual_port}")
                    if hasattr(self, 'portal_status'):
                        self.portal_status.setText(f"Status: Online ✅ (Port {actual_port})")
                    
                    # Open portal in browser for testing
                    try:
                        import webbrowser
                        webbrowser.open(f"http://127.0.0.1:{actual_port}/portal")
                    except:
                        pass
                else:
                    self.log_message("⚠️ Portal server test returned error")
                    
        except Exception as e:
            self.log_message(f"⚠️ Portal connection test failed: {str(e)}")
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Error ❌")
'''

    # Apply the fixes
    print("🔧 Applying HTTP server startup fixes...")
    
    # Replace the existing EnhancedDeveloperPortalServer class
    server_class_pattern = r'class EnhancedDeveloperPortalServer\(QThread\):.*?(?=class [A-Z]|\Z)'
    content = re.sub(server_class_pattern, enhanced_server_code, content, flags=re.DOTALL)
    
    # Replace the start_portal_server method
    start_method_pattern = r'def start_portal_server\(self\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\Z)'
    content = re.sub(start_method_pattern, enhanced_start_method, content, flags=re.DOTALL)
    
    # Add the test method if it doesn't exist
    if 'def test_portal_connection(self):' not in content:
        # Find where to insert the test method (after start_portal_server)
        insert_pattern = r'(def start_portal_server\(self\):.*?pass|def start_portal_server\(self\):.*?setEnabled\(False\))'
        if re.search(insert_pattern, content, flags=re.DOTALL):
            content = re.sub(insert_pattern, f'\\1\n\n{enhanced_start_method}', content, flags=re.DOTALL)
    
    # Write the enhanced file
    with open('pyqt.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied HTTP server startup fixes!")
    return True

def create_simple_test_server():
    """Create a simple test server to verify port availability"""
    test_code = '''
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            'status': 'Test server is working!',
            'timestamp': datetime.now().isoformat(),
            'port': self.server.server_port
        }
        self.wfile.write(json.dumps(response).encode())

def test_port(port):
    try:
        server = HTTPServer(('127.0.0.1', port), TestHandler)
        print(f"✅ Test server started on port {port}")
        print(f"🌐 Visit: http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Test server failed on port {port}: {e}")

if __name__ == "__main__":
    test_port(8082)
'''
    
    with open('test_server.py', 'w') as f:
        f.write(test_code)
    
    print("📝 Created test_server.py - run it to test port availability:")
    print("   python test_server.py")

if __name__ == "__main__":
    print("🔧 PythonCoin HTTP Server Startup Fix")
    print("=" * 50)
    
    if not os.path.exists('pyqt.py'):
        print("❌ Error: pyqt.py file not found in current directory")
        exit(1)
    
    # Check if port 8082 is available
    if check_port_available(8082):
        print("✅ Port 8082 is available")
    else:
        print("⚠️ Port 8082 is busy - script will find alternative port")
    
    # Apply the fixes
    success = inject_server_fixes()
    
    if success:
        print("\n🎉 Server startup fixes applied successfully!")
        print("\n📋 Fixes applied:")
        print("   • Enhanced error handling for HTTP server")
        print("   • Automatic port detection and fallback")
        print("   • Better server lifecycle management")
        print("   • Improved connection testing")
        print("   • Enhanced logging and diagnostics")
        print("   • CORS headers for web requests")
        print("   • Threaded server for better performance")
        
        print("\n🚀 Next steps:")
        print("   1. Run: python pyqt.py")
        print("   2. Click 'Start Portal Server' in the Developer Portal tab")
        print("   3. Check the console for server status messages")
        print("   4. Server will automatically open in browser for testing")
        
        # Create test server
        create_simple_test_server()
        
    else:
        print("❌ Failed to apply fixes")
        
    print("\n" + "=" * 50)