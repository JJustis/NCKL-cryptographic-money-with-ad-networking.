#!/usr/bin/env python3
"""
Port Validation Fix for PythonCoin PyQt Wallet
Fixes "startup failed non-numerical port" error
"""

import os
import re
import shutil
from datetime import datetime

def inject_port_validation_fix():
    """Inject port validation fixes into pyqt.py"""
    
    # Backup original file
    if os.path.exists('pyqt.py'):
        backup_name = f'pyqt_port_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('pyqt.py', backup_name)
        print(f"✅ Backed up original file to: {backup_name}")
    
    # Read the original file
    with open('pyqt.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Port validation utility methods
    port_validation_methods = '''
    def validate_port(self, port_value, default_port=8082):
        """Validate and convert port value to integer"""
        try:
            # Handle various input types
            if isinstance(port_value, str):
                # Remove any whitespace
                port_value = port_value.strip()
                
                # Handle empty string
                if not port_value:
                    self.log_message(f"⚠️ Empty port value, using default: {default_port}")
                    return default_port
                
                # Convert to integer
                port_int = int(port_value)
            elif isinstance(port_value, (int, float)):
                port_int = int(port_value)
            else:
                self.log_message(f"⚠️ Invalid port type {type(port_value)}, using default: {default_port}")
                return default_port
            
            # Validate port range
            if port_int < 1024 or port_int > 65535:
                self.log_message(f"⚠️ Port {port_int} out of range (1024-65535), using default: {default_port}")
                return default_port
            
            return port_int
            
        except (ValueError, TypeError) as e:
            self.log_message(f"⚠️ Port validation error: {str(e)}, using default: {default_port}")
            return default_port
    
    def get_safe_port_from_ui(self, ui_element=None, default_port=8082):
        """Safely get port value from UI element"""
        try:
            if ui_element is None:
                return default_port
            
            # Handle different UI element types
            if hasattr(ui_element, 'value'):
                # QSpinBox
                port_value = ui_element.value()
            elif hasattr(ui_element, 'text'):
                # QLineEdit
                port_value = ui_element.text()
            else:
                # Unknown type
                self.log_message(f"⚠️ Unknown UI element type: {type(ui_element)}")
                return default_port
            
            return self.validate_port(port_value, default_port)
            
        except Exception as e:
            self.log_message(f"⚠️ Error getting port from UI: {str(e)}")
            return default_port
'''

    # Enhanced __init__ method with port validation
    enhanced_init_snippet = '''
        # P2P Ad Network components with validated port
        self.client_id = str(uuid.uuid4())[:8]
        try:
            self.port = self.validate_port(8082, 8082)  # Ensure port is always valid integer
        except:
            self.port = 8082  # Fallback if validation method not available yet
'''

    # Enhanced EnhancedDeveloperPortalServer __init__ with port validation
    enhanced_server_init = '''
    def __init__(self, wallet, blockchain, port=8082):
        super().__init__()
        self.wallet = wallet
        self.blockchain = blockchain
        
        # Validate port parameter
        try:
            if isinstance(port, str):
                port = port.strip()
                if not port:
                    port = 8082
                self.requested_port = int(port)
            elif isinstance(port, (int, float)):
                self.requested_port = int(port)
            else:
                print(f"⚠️ Invalid port type: {type(port)}, using 8082")
                self.requested_port = 8082
            
            # Validate port range
            if self.requested_port < 1024 or self.requested_port > 65535:
                print(f"⚠️ Port {self.requested_port} out of range, using 8082")
                self.requested_port = 8082
                
        except (ValueError, TypeError) as e:
            print(f"⚠️ Port validation error: {str(e)}, using 8082")
            self.requested_port = 8082
        
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
        
        print(f"✅ Server initialized with port: {self.requested_port}")
'''

    # Enhanced start_portal_server method with port validation
    enhanced_start_portal_method = '''
    def start_portal_server(self):
        """Start the enhanced developer portal server with port validation"""
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
                try:
                    self.portal_server.wait(2000)  # Wait for cleanup
                except:
                    pass
            
            # Get and validate port
            server_port = 8082  # Default port
            try:
                # Try to get port from UI if available
                if hasattr(self, 'validate_port'):
                    server_port = self.validate_port(self.port if hasattr(self, 'port') else 8082, 8082)
                else:
                    # Fallback validation
                    if hasattr(self, 'port'):
                        if isinstance(self.port, (int, float)):
                            server_port = int(self.port)
                        elif isinstance(self.port, str) and self.port.isdigit():
                            server_port = int(self.port)
                        else:
                            server_port = 8082
                    else:
                        server_port = 8082
                        
            except Exception as e:
                self.log_message(f"⚠️ Port validation failed: {str(e)}, using 8082")
                server_port = 8082
            
            self.log_message(f"🚀 Creating portal server on port {server_port}...")
            
            # Create enhanced portal server with validated port
            self.portal_server = EnhancedDeveloperPortalServer(
                wallet=self.wallet, 
                blockchain=self.blockchain, 
                port=server_port  # Ensure this is an integer
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
                self.portal_status.setText(f"Status: Starting on port {server_port}...")
            if hasattr(self, 'start_portal_btn'):
                self.start_portal_btn.setEnabled(False)
            if hasattr(self, 'stop_portal_btn'):
                self.stop_portal_btn.setEnabled(True)
            
            self.log_message(f"✅ Portal server startup initiated on port {server_port}")
            
            # Test connection after a delay
            QTimer.singleShot(3000, self.test_portal_connection)
            
        except Exception as e:
            self.log_message(f"❌ Error starting portal server: {str(e)}")
            import traceback
            self.log_message(f"Stack trace: {traceback.format_exc()}")
            
            QMessageBox.critical(self, "Portal Error", 
                               f"Failed to start server: {str(e)}\\n\\n"
                               f"This might be due to port issues. Check the console for details.")
            
            # Reset UI state on failure
            self.portal_enabled = False
            if hasattr(self, 'start_portal_btn'):
                self.start_portal_btn.setEnabled(True)
            if hasattr(self, 'stop_portal_btn'):
                self.stop_portal_btn.setEnabled(False)
'''

    # Enhanced node start method with port validation
    enhanced_start_node_method = '''
    def start_node(self):
        """Start blockchain node with port validation"""
        if self.node:
            return
        
        try:
            # Get and validate host and port
            host = "127.0.0.1"
            port = 5000
            
            if hasattr(self, 'node_host') and self.node_host:
                host_text = self.node_host.text().strip()
                if host_text:
                    host = host_text
            
            if hasattr(self, 'node_port') and self.node_port:
                try:
                    port = self.get_safe_port_from_ui(self.node_port, 5000)
                except:
                    # Fallback port validation
                    try:
                        port_value = self.node_port.value() if hasattr(self.node_port, 'value') else 5000
                        port = int(port_value)
                        if port < 1024 or port > 65535:
                            port = 5000
                    except:
                        port = 5000
            
            self.log_message(f"🚀 Starting blockchain node on {host}:{port}")
            
            from pythoncoin import Node
            self.node = Node(host=host, port=port)
            self.node.blockchain = self.blockchain
            self.node.wallet = self.wallet
            
            # Start node in thread
            threading.Thread(target=self.node.start, daemon=True).start()
            
            if hasattr(self, 'node_status'):
                self.node_status.setText(f"Status: Node running on {host}:{port}")
            if hasattr(self, 'start_node_button'):
                self.start_node_button.setEnabled(False)
            if hasattr(self, 'stop_node_button'):
                self.stop_node_button.setEnabled(True)
            
            self.log_message(f"✅ Blockchain node started on {host}:{port}")
            
        except Exception as e:
            self.log_message(f"❌ Error starting node: {str(e)}")
            QMessageBox.critical(self, "Node Error", f"Failed to start node: {str(e)}")
'''

    # Enhanced network tab creation with proper port initialization
    enhanced_network_tab_snippet = '''
        self.node_port = QSpinBox()
        self.node_port.setRange(1024, 65535)
        self.node_port.setValue(5000)  # Set default integer value
        host_port_layout.addWidget(self.node_port)
'''

    print("🔧 Applying port validation fixes...")
    
    # Add port validation methods to the class
    if 'def validate_port(self,' not in content:
        # Find a good place to insert the methods (after __init__ and before other methods)
        init_end_pattern = r'(def __init__\(self\):.*?self\.setup_auto_save_timer\(\))'
        if re.search(init_end_pattern, content, flags=re.DOTALL):
            content = re.sub(init_end_pattern, f'\\1\n{port_validation_methods}', content, flags=re.DOTALL)
        else:
            # Fallback: add before first method
            class_start_pattern = r'(class UnifiedPythonCoinWallet\(QMainWindow\):.*?\n\n    def )'
            content = re.sub(class_start_pattern, f'\\1{port_validation_methods}\n\n    def ', content, flags=re.DOTALL)
    
    # Fix the __init__ method port initialization
    init_port_pattern = r'(\s+# P2P Ad Network components\s+self\.client_id = str\(uuid\.uuid4\(\)\)\[:8\]\s+)(self\.port = 8082)'
    content = re.sub(init_port_pattern, f'\\1{enhanced_init_snippet.strip()}', content)
    
    # Fix EnhancedDeveloperPortalServer __init__ method
    server_init_pattern = r'(class EnhancedDeveloperPortalServer\(QThread\):.*?def __init__\(self, wallet, blockchain, port=8082\):)(.*?)(def check_port_available|def run|def test_server_connection)'
    content = re.sub(server_init_pattern, f'\\1{enhanced_server_init}\\3', content, flags=re.DOTALL)
    
    # Fix start_portal_server method
    start_portal_pattern = r'def start_portal_server\(self\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\Z)'
    content = re.sub(start_portal_pattern, enhanced_start_portal_method, content, flags=re.DOTALL)
    
    # Fix start_node method if it exists
    if 'def start_node(self):' in content:
        start_node_pattern = r'def start_node\(self\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\Z)'
        content = re.sub(start_node_pattern, enhanced_start_node_method, content, flags=re.DOTALL)
    
    # Fix node_port QSpinBox initialization
    node_port_pattern = r'(self\.node_port = QSpinBox\(\)\s+self\.node_port\.setRange\(\d+, \d+\)\s+)(self\.node_port\.setValue\(\d+\))'
    content = re.sub(node_port_pattern, f'\\1self.node_port.setValue(5000)  # Ensure integer value', content)
    
    # Add error handling to the HTTPServer creation
    server_creation_pattern = r'(self\.httpd = OptimizedServer\(\(\'127\.0\.0\.1\', self\.actual_port\), handler_factory\))'
    content = re.sub(server_creation_pattern, 
                    'self.httpd = OptimizedServer((\'127.0.0.1\', int(self.actual_port)), handler_factory)', 
                    content)
    
    # Write the enhanced file
    with open('pyqt.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied port validation fixes!")
    return True

def create_port_diagnostic_script():
    """Create a diagnostic script to test port issues"""
    diagnostic_code = '''#!/usr/bin/env python3
"""
Port Diagnostic Script for PythonCoin
Tests various port-related issues
"""

import socket
import sys

def test_port_types():
    """Test different port value types"""
    print("🔍 Testing port value types...")
    
    test_values = [
        8082,           # int
        "8082",         # string
        8082.0,         # float
        "8082.0",       # string float
        " 8082 ",       # string with whitespace
        "",             # empty string
        None,           # None
        "abc",          # invalid string
        -1,             # negative
        99999,          # too high
    ]
    
    for i, value in enumerate(test_values):
        try:
            print(f"  Test {i+1}: {repr(value)} ({type(value).__name__})")
            
            # Test conversion
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    result = "Empty string - would use default"
                else:
                    port_int = int(value)
                    if 1024 <= port_int <= 65535:
                        result = f"✅ Valid port: {port_int}"
                    else:
                        result = f"❌ Out of range: {port_int}"
            elif isinstance(value, (int, float)):
                port_int = int(value)
                if 1024 <= port_int <= 65535:
                    result = f"✅ Valid port: {port_int}"
                else:
                    result = f"❌ Out of range: {port_int}"
            elif value is None:
                result = "None - would use default"
            else:
                result = f"❌ Invalid type: {type(value)}"
                
            print(f"    Result: {result}")
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
        
        print()

def test_socket_binding():
    """Test socket binding on different ports"""
    print("🔍 Testing socket binding...")
    
    test_ports = [8082, 8083, 8084, 5000, 5001]
    
    for port in test_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                print(f"  ✅ Port {port}: Available")
        except OSError as e:
            print(f"  ❌ Port {port}: Busy ({e})")

def test_server_creation():
    """Test HTTP server creation"""
    print("🔍 Testing HTTP server creation...")
    
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class TestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Test server working")
        
        # Test with different port types
        port_tests = [8085, "8085", 8085.0]
        
        for port in port_tests:
            try:
                print(f"  Testing port {repr(port)} ({type(port).__name__})")
                
                # Ensure port is integer
                port_int = int(port)
                
                server = HTTPServer(('127.0.0.1', port_int), TestHandler)
                print(f"    ✅ Server created successfully on port {port_int}")
                server.server_close()
                
            except Exception as e:
                print(f"    ❌ Server creation failed: {str(e)}")
                
    except ImportError as e:
        print(f"  ❌ Cannot import HTTP server: {str(e)}")

def main():
    print("🚀 PythonCoin Port Diagnostic Tool")
    print("=" * 50)
    
    test_port_types()
    test_socket_binding()
    test_server_creation()
    
    print("✅ Diagnostic complete!")
    print("\\nIf you see errors above, they indicate the source of your port issues.")

if __name__ == "__main__":
    main()
'''
    
    with open('port_diagnostic.py', 'w') as f:
        f.write(diagnostic_code)
    
    print("📝 Created port_diagnostic.py - run it to diagnose port issues:")
    print("   python port_diagnostic.py")

if __name__ == "__main__":
    print("🔧 PythonCoin Port Validation Fix")
    print("=" * 50)
    
    if not os.path.exists('pyqt.py'):
        print("❌ Error: pyqt.py file not found in current directory")
        exit(1)
    
    # Apply the fixes
    success = inject_port_validation_fix()
    
    if success:
        print("\n🎉 Port validation fixes applied successfully!")
        print("\n📋 Fixes applied:")
        print("   • Added port validation methods")
        print("   • Fixed non-numerical port handling")
        print("   • Enhanced error messages for port issues")
        print("   • Added fallback port values")
        print("   • Improved UI port element handling")
        print("   • Added type conversion for all port values")
        print("   • Enhanced server initialization")
        
        print("\n🚀 Next steps:")
        print("   1. Run: python port_diagnostic.py (to test)")
        print("   2. Run: python pyqt.py")
        print("   3. All ports will now be properly validated")
        
        # Create diagnostic script
        create_port_diagnostic_script()
        
    else:
        print("❌ Failed to apply fixes")
        
    print("\n" + "=" * 50)