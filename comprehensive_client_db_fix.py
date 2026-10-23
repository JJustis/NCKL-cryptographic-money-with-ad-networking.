#!/usr/bin/env python3
"""
Comprehensive Client Database Integration Fix for PythonCoin PyQt Wallet
Fixes missing methods, portal server state issues, and ensures proper database updates
"""

import os
import re
import shutil
from datetime import datetime

def inject_comprehensive_client_fixes():
    """Inject comprehensive client and database fixes into pyqt.py"""
    
    # Backup original file
    if os.path.exists('pyqt.py'):
        backup_name = f'pyqt_comprehensive_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('pyqt.py', backup_name)
        print(f"✅ Backed up original file to: {backup_name}")
    
    # Read the original file
    with open('pyqt.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Missing methods that need to be added
    missing_methods = '''
    def test_portal_connection(self):
        """Test portal connection after startup - FIXED VERSION"""
        try:
            if not self.portal_server:
                self.log_message("⚠️ No portal server instance to test")
                return False
            
            # Get the actual port from server
            actual_port = getattr(self.portal_server, 'actual_port', None)
            if not actual_port:
                actual_port = getattr(self.portal_server, 'requested_port', 8082)
            
            self.log_message(f"🔍 Testing portal connection on port {actual_port}")
            
            import urllib.request
            import time
            
            # Give server a moment to fully start
            time.sleep(1)
            
            test_url = f"http://127.0.0.1:{actual_port}/test"
            
            req = urllib.request.Request(test_url)
            req.add_header('User-Agent', 'PythonCoin-Wallet-Test')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get('success'):
                    self.log_message(f"✅ Portal server test successful on port {actual_port}")
                    if hasattr(self, 'portal_status'):
                        self.portal_status.setText(f"Status: Online ✅ (Port {actual_port})")
                    
                    # Register client in database now that server is working
                    self.register_client_in_database()
                    
                    # Start periodic database updates
                    self.start_database_sync()
                    
                    return True
                else:
                    self.log_message("⚠️ Portal server test returned error")
                    return False
                    
        except Exception as e:
            self.log_message(f"⚠️ Portal connection test failed: {str(e)}")
            if hasattr(self, 'portal_status'):
                self.portal_status.setText(f"Status: Error ❌ - {str(e)}")
            return False
    
    def get_local_ip(self):
        """Get local IP address for client registration"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def register_client_in_database(self):
        """Register this client in the database with complete information - ENHANCED"""
        try:
            if not self.db_connected:
                # Try to reconnect to database
                self.db_connected = self.db_manager.connect()
                if not self.db_connected:
                    self.log_message("❌ Cannot register client - database not connected")
                    return False
            
            if not self.wallet:
                self.log_message("⚠️ Cannot register client - wallet not loaded")
                return False
            
            self.log_message("📝 Registering client in database...")
            
            # Get current balance safely
            current_balance = 0.0
            try:
                if hasattr(self, 'override_wallet_get_balance'):
                    current_balance = self.override_wallet_get_balance()
                elif hasattr(self.wallet, 'get_balance'):
                    current_balance = self.wallet.get_balance()
            except Exception as e:
                self.log_message(f"⚠️ Could not get balance: {str(e)}")
            
            # Get server port
            server_port = self.port
            if self.portal_server and hasattr(self.portal_server, 'actual_port'):
                server_port = self.portal_server.actual_port
            
            # Comprehensive client information
            client_data = {
                'client_id': self.client_id,
                'name': f'PythonCoin Wallet - {self.wallet.address[:8]}...',
                'host': self.get_local_ip(),
                'port': server_port,
                'username': f'user_{self.wallet.address[:8]}',
                'wallet_address': self.wallet.address,
                'version': '2.1.0',
                'capabilities': ['ad_serving', 'payments', 'p2p', 'mining', 'blockchain'],
                'metadata': {
                    'start_time': datetime.now().isoformat(),
                    'python_version': sys.version,
                    'platform': os.name,
                    'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                    'wallet_balance': current_balance,
                    'mining_status': 'active' if (self.mining_thread and self.mining_thread.isRunning()) else 'inactive',
                    'server_status': 'online' if self.portal_enabled else 'offline',
                    'last_balance_update': datetime.now().isoformat(),
                    'payment_address': self.wallet.address,
                    'client_type': 'desktop_wallet'
                },
                'ad_count': len(self.ads)
            }
            
            # Register in database
            success = self.db_manager.register_client(client_data)
            
            if success:
                self.log_message(f"✅ Client registered in database: {self.client_id}")
                self.log_message(f"💰 Payment address: {self.wallet.address}")
                self.log_message(f"💎 Current balance: {current_balance:.8f} PYC")
                
                # Create startup notification
                self.create_system_notification("client_startup", 
                    f"PythonCoin client {self.client_id} started successfully with {current_balance:.6f} PYC")
                
                return True
            else:
                self.log_message("❌ Failed to register client in database")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error registering client: {str(e)}")
            import traceback
            self.log_message(f"Stack trace: {traceback.format_exc()}")
            return False
    
    def start_database_sync(self):
        """Start periodic database synchronization"""
        try:
            if not hasattr(self, 'db_sync_timer'):
                self.db_sync_timer = QTimer()
                self.db_sync_timer.timeout.connect(self.update_client_in_database)
                self.db_sync_timer.start(15000)  # Update every 15 seconds
                self.log_message("✅ Database sync timer started (15 second intervals)")
            
        except Exception as e:
            self.log_message(f"❌ Error starting database sync: {str(e)}")
    
    def update_client_in_database(self):
        """Update client information in database - ENHANCED"""
        try:
            if not self.db_connected or not self.wallet:
                return
            
            # Get current balance
            current_balance = 0.0
            try:
                if hasattr(self, 'override_wallet_get_balance'):
                    current_balance = self.override_wallet_get_balance()
                elif hasattr(self.wallet, 'get_balance'):
                    current_balance = self.wallet.get_balance()
            except:
                pass
            
            # Get server port
            server_port = self.port
            if self.portal_server and hasattr(self.portal_server, 'actual_port'):
                server_port = self.portal_server.actual_port
            
            # Updated metadata with payment tracking
            updated_metadata = {
                'last_update': datetime.now().isoformat(),
                'blockchain_height': len(self.blockchain.chain) if self.blockchain else 0,
                'wallet_balance': current_balance,
                'mining_status': 'active' if (self.mining_thread and self.mining_thread.isRunning()) else 'inactive',
                'server_status': 'online' if self.portal_enabled else 'offline',
                'connected_peers': len([p for p in self.peers.values() if p.status == 'connected']),
                'ads_served': self.stats.get('ads_served', 0),
                'total_clicks': len(self.click_events),
                'total_payments': self.stats.get('payments_sent', 0),
                'revenue_generated': self.stats.get('revenue_generated', 0.0),
                'uptime_seconds': int(time.time() - self.stats.get('uptime_start', time.time())),
                'payment_address': self.wallet.address,
                'server_port': server_port,
                'last_balance_update': datetime.now().isoformat()
            }
            
            # Update in database
            query = """
                UPDATE p2p_clients 
                SET metadata = %s, ad_count = %s, last_seen = CURRENT_TIMESTAMP,
                    status = 'online', wallet_address = %s, port = %s
                WHERE client_id = %s
            """
            
            success = self.db_manager.execute_query(query, (
                json.dumps(updated_metadata),
                len(self.ads),
                self.wallet.address,
                server_port,
                self.client_id
            ))
            
            if success:
                # Only log every 5th update to avoid spam
                if not hasattr(self, '_db_update_count'):
                    self._db_update_count = 0
                self._db_update_count += 1
                
                if self._db_update_count % 5 == 0:
                    self.log_message(f"✅ Database updated (#{self._db_update_count}) - Balance: {current_balance:.6f} PYC")
            
        except Exception as e:
            self.log_message(f"❌ Error updating client in database: {str(e)}")
    
    def create_system_notification(self, notification_type, message, priority='normal'):
        """Create system notification in database"""
        try:
            if not self.db_connected:
                return
            
            notification_data = {
                'type': notification_type,
                'title': f'Client {self.client_id[:8]}',
                'message': message,
                'recipient_type': 'system',
                'metadata': {
                    'client_id': self.client_id,
                    'wallet_address': self.wallet.address if self.wallet else '',
                    'timestamp': datetime.now().isoformat(),
                    'balance': self.get_current_balance() if hasattr(self, 'get_current_balance') else 0.0
                },
                'priority': priority
            }
            
            self.db_manager.create_notification(notification_data)
            
        except Exception as e:
            self.log_message(f"❌ Error creating notification: {str(e)}")
    
    def get_current_balance(self):
        """Get current wallet balance safely"""
        try:
            if not self.wallet:
                return 0.0
            
            if hasattr(self, 'override_wallet_get_balance'):
                return self.override_wallet_get_balance()
            elif hasattr(self.wallet, 'get_balance'):
                return self.wallet.get_balance()
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def check_portal_server_state(self):
        """Check and fix portal server state issues"""
        try:
            # Reset portal state if server is not actually running
            if hasattr(self, 'portal_server'):
                if self.portal_server is None or not self.portal_server.isRunning():
                    self.portal_enabled = False
                    if hasattr(self, 'portal_status'):
                        self.portal_status.setText("Status: Offline")
                    if hasattr(self, 'start_portal_btn'):
                        self.start_portal_btn.setEnabled(True)
                    if hasattr(self, 'stop_portal_btn'):
                        self.stop_portal_btn.setEnabled(False)
                    self.log_message("🔧 Fixed portal server state - was marked as running but wasn't")
                    return False
                else:
                    return True
            else:
                self.portal_enabled = False
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error checking portal state: {str(e)}")
            return False
    
    def force_stop_portal_server(self):
        """Force stop portal server and reset state"""
        try:
            self.log_message("🛑 Force stopping portal server...")
            
            if hasattr(self, 'portal_server') and self.portal_server:
                try:
                    self.portal_server.running = False
                    if self.portal_server.isRunning():
                        self.portal_server.terminate()
                        self.portal_server.wait(3000)
                except:
                    pass
                self.portal_server = None
            
            # Reset state
            self.portal_enabled = False
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Offline")
            if hasattr(self, 'start_portal_btn'):
                self.start_portal_btn.setEnabled(True)
            if hasattr(self, 'stop_portal_btn'):
                self.stop_portal_btn.setEnabled(False)
            
            self.log_message("✅ Portal server force stopped and state reset")
            
        except Exception as e:
            self.log_message(f"❌ Error force stopping portal: {str(e)}")
'''

    # Enhanced start_portal_server method that checks state first
    enhanced_start_portal_server = '''
    def start_portal_server(self):
        """Start the enhanced developer portal server with state checking"""
        if not self.wallet:
            QMessageBox.warning(self, "Portal Error", "No wallet loaded")
            return
        
        # Check if server is actually running
        if not self.check_portal_server_state():
            self.log_message("🔧 Portal server state was incorrect, proceeding with startup...")
        elif self.portal_server and self.portal_server.isRunning():
            self.log_message("⚠️ Portal server is already running")
            # Test the existing connection
            self.test_portal_connection()
            return
        
        try:
            # Force stop any existing server first
            self.force_stop_portal_server()
            
            # Get and validate port
            server_port = 8082
            try:
                if hasattr(self, 'validate_port'):
                    server_port = self.validate_port(self.port if hasattr(self, 'port') else 8082, 8082)
                else:
                    server_port = int(self.port) if hasattr(self, 'port') else 8082
                        
            except Exception as e:
                self.log_message(f"⚠️ Port validation failed: {str(e)}, using 8082")
                server_port = 8082
            
            self.log_message(f"🚀 Creating portal server on port {server_port}...")
            
            # Create new portal server
            self.portal_server = EnhancedDeveloperPortalServer(
                wallet=self.wallet, 
                blockchain=self.blockchain, 
                port=server_port
            )
            
            # Pass database manager and wallet instance
            if hasattr(self, 'db_manager') and self.db_manager:
                self.portal_server.db_manager = self.db_manager
                self.portal_server.wallet_instance = self
            
            # Connect signals
            self.portal_server.status_update.connect(self.on_portal_status_update)
            self.portal_server.click_received.connect(self.on_portal_click_received)
            self.portal_server.developer_registered.connect(self.on_developer_registered)
            if hasattr(self.portal_server, 'client_notification'):
                self.portal_server.client_notification.connect(self.on_client_notification)
            
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
            
            # Test connection after startup
            QTimer.singleShot(4000, self.test_portal_connection)
            
        except Exception as e:
            self.log_message(f"❌ Error starting portal server: {str(e)}")
            import traceback
            self.log_message(f"Stack trace: {traceback.format_exc()}")
            
            QMessageBox.critical(self, "Portal Error", 
                               f"Failed to start server: {str(e)}\\n\\n"
                               f"Check the console for detailed error information.")
            
            # Reset state on failure
            self.force_stop_portal_server()
'''

    # Enhanced signal handlers
    enhanced_signal_handlers = '''
    def on_portal_status_update(self, status):
        """Handle portal server status updates with database integration"""
        self.log_message(f"🌐 Portal: {status}")
        
        if "server started" in status.lower() or "✅" in status:
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Online ✅")
        elif "error" in status.lower() or "❌" in status:
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Error ❌")
        
        # Update database with server status
        if self.db_connected and "started successfully" in status.lower():
            self.update_client_in_database()
    
    def on_client_notification(self, notification_data):
        """Handle client notifications from portal server"""
        try:
            notification_type = notification_data.get('type', 'general')
            message = notification_data.get('message', '')
            
            self.log_message(f"📢 Portal notification: {message}")
            
            # Store notification in database
            if self.db_connected:
                self.create_system_notification(notification_type, message)
                
        except Exception as e:
            self.log_message(f"❌ Error handling notification: {str(e)}")
    
    def on_portal_click_received(self, click_data):
        """Handle ad click from portal with enhanced database tracking"""
        try:
            developer = click_data.get('developer', 'Unknown')
            amount = click_data.get('amount', 0)
            ad_id = click_data.get('ad_id', '')
            
            self.log_message(f"💰 Portal click: {amount:.6f} PYC -> {developer}")
            
            # Record in database if connected
            if self.db_connected and ad_id:
                click_record = {
                    'ad_id': ad_id,
                    'client_id': self.client_id,
                    'zone': click_data.get('zone', 'default'),
                    'payout_amount': amount,
                    'ip_address': click_data.get('ip_address', '127.0.0.1'),
                    'user_agent': click_data.get('user_agent', ''),
                    'metadata': {
                        'developer': developer,
                        'timestamp': datetime.now().isoformat(),
                        'payment_address': self.wallet.address if self.wallet else '',
                        'client_balance_before': self.get_current_balance()
                    }
                }
                
                try:
                    self.db_manager.record_ad_click(click_record)
                    self.log_message("✅ Click recorded in database")
                except Exception as e:
                    self.log_message(f"❌ Error recording click: {str(e)}")
            
            # Update stats and save blockchain
            self.stats['clicks'] = self.stats.get('clicks', 0) + 1
            self.stats['revenue_generated'] = self.stats.get('revenue_generated', 0.0) + amount
            
            if hasattr(self, 'save_blockchain'):
                self.save_blockchain()
            
            # Update database after click
            self.update_client_in_database()
                
        except Exception as e:
            self.log_message(f"❌ Error handling portal click: {str(e)}")
'''

    # Enhanced init_database method
    enhanced_init_database = '''
    def init_database(self):
        """Initialize database connection and setup client registration"""
        try:
            self.db_connected = self.db_manager.connect()
            
            if self.db_connected:
                self.log_message("✅ Database connected successfully")
                
                # Schedule client registration after wallet is loaded
                QTimer.singleShot(5000, self.delayed_database_registration)
                
                # Schedule periodic cleanup
                QTimer.singleShot(10000, self.setup_database_maintenance)
                
            else:
                self.log_message("❌ Database connection failed - will retry in 30 seconds")
                # Retry connection after 30 seconds
                QTimer.singleShot(30000, self.init_database)
                
        except Exception as e:
            self.log_message(f"❌ Database initialization error: {str(e)}")
            self.db_connected = False
            # Retry after 30 seconds
            QTimer.singleShot(30000, self.init_database)
    
    def delayed_database_registration(self):
        """Delayed database registration after wallet is ready"""
        try:
            if self.wallet and self.db_connected:
                self.log_message("📋 Performing delayed database registration...")
                success = self.register_client_in_database()
                if success:
                    self.start_database_sync()
                else:
                    # Retry registration in 15 seconds
                    QTimer.singleShot(15000, self.delayed_database_registration)
            else:
                # Wallet not ready yet, try again in 5 seconds
                QTimer.singleShot(5000, self.delayed_database_registration)
                
        except Exception as e:
            self.log_message(f"❌ Delayed registration error: {str(e)}")
    
    def setup_database_maintenance(self):
        """Setup periodic database maintenance tasks"""
        try:
            if not hasattr(self, 'db_maintenance_timer'):
                self.db_maintenance_timer = QTimer()
                self.db_maintenance_timer.timeout.connect(self.perform_database_maintenance)
                self.db_maintenance_timer.start(300000)  # Every 5 minutes
                self.log_message("✅ Database maintenance timer started (5 minute intervals)")
            
        except Exception as e:
            self.log_message(f"❌ Error setting up maintenance: {str(e)}")
    
    def perform_database_maintenance(self):
        """Perform periodic database maintenance"""
        try:
            if not self.db_connected:
                return
            
            # Update client status
            self.update_client_in_database()
            
            # Clean up old sessions
            cleanup_query = """
                UPDATE developer_sessions 
                SET status = 'inactive'
                WHERE last_activity < DATE_SUB(NOW(), INTERVAL 2 HOUR)
                AND status = 'active'
                AND client_id = %s
            """
            
            self.db_manager.execute_query(cleanup_query, (self.client_id,))
            
            # Log maintenance completion
            self.log_message("🧹 Database maintenance completed")
            
        except Exception as e:
            self.log_message(f"❌ Database maintenance error: {str(e)}")
'''

    print("🔧 Applying comprehensive client and database fixes...")
    
    # Add missing methods to the class
    if 'def test_portal_connection(self):' not in content:
        # Find a good place to insert methods (before closeEvent)
        close_event_pattern = r'(def closeEvent\(self, event\):)'
        content = re.sub(close_event_pattern, f'{missing_methods}\n\n    \\1', content)
    
    # Replace the start_portal_server method
    start_portal_pattern = r'def start_portal_server\(self\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\n\n# |$)'
    content = re.sub(start_portal_pattern, enhanced_start_portal_server.strip(), content, flags=re.DOTALL)
    
    # Add enhanced signal handlers if they don't exist
    if 'def on_portal_status_update(self, status):' in content:
        # Replace existing handlers
        portal_status_pattern = r'def on_portal_status_update\(self, status\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\n\n# |$)'
        content = re.sub(portal_status_pattern, enhanced_signal_handlers.strip(), content, flags=re.DOTALL)
    else:
        # Add new handlers
        close_event_pattern = r'(def closeEvent\(self, event\):)'
        content = re.sub(close_event_pattern, f'{enhanced_signal_handlers}\n\n    \\1', content)
    
    # Replace init_database method
    if 'def init_database(self):' in content:
        init_db_pattern = r'def init_database\(self\):.*?(?=\n    def [a-z]|\n\n    def [a-z]|\n\n# |$)'
        content = re.sub(init_db_pattern, enhanced_init_database.strip(), content, flags=re.DOTALL)
    else:
        # Add init_database method
        init_ui_pattern = r'(def init_ui\(self\):.*?self\.create_developer_portal_tab\(\))'
        content = re.sub(init_ui_pattern, f'\\1\n\n{enhanced_init_database}', content, flags=re.DOTALL)
    
    # Write the enhanced file
    with open('pyqt.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied comprehensive client and database fixes!")
    return True

def create_database_monitor_script():
    """Create a script to monitor database updates"""
    monitor_code = '''#!/usr/bin/env python3
"""
Database Monitor for PythonCoin Client
Monitors real-time database updates
"""

import mysql.connector
import json
import time
from datetime import datetime

def monitor_database():
    """Monitor database for client updates"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            database='adnetwrk',
            user='root',
            password=''
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Monitoring PythonCoin client database updates...")
        print("=" * 60)
        
        last_check = {}
        
        while True:
            try:
                # Check p2p_clients table
                cursor.execute("SELECT * FROM p2p_clients ORDER BY last_seen DESC LIMIT 10")
                clients = cursor.fetchall()
                
                print(f"\\n📊 P2P Clients ({datetime.now().strftime('%H:%M:%S')}):")
                print("-" * 40)
                
                for client in clients:
                    client_id = client['client_id']
                    name = client['name']
                    wallet_addr = client['wallet_address']
                    status = client['status']
                    last_seen = client['last_seen']
                    
                    # Parse metadata if available
                    metadata = {}
                    try:
                        if client['metadata']:
                            metadata = json.loads(client['metadata'])
                    except:
                        pass
                    
                    balance = metadata.get('wallet_balance', 0)
                    server_status = metadata.get('server_status', 'unknown')
                    
                    print(f"  🔗 {client_id[:8]}... | {name[:20]}")
                    print(f"      💰 Address: {wallet_addr[:16]}...")
                    print(f"      💎 Balance: {balance:.6f} PYC")
                    print(f"      📡 Status: {status} | Server: {server_status}")
                    print(f"      🕐 Last seen: {last_seen}")
                    print()
                
                # Check for recent ad clicks
                cursor.execute("""
                    SELECT * FROM ad_clicks 
                    WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    ORDER BY created_at DESC LIMIT 5
                """)
                clicks = cursor.fetchall()
                
                if clicks:
                    print("💰 Recent Ad Clicks:")
                    print("-" * 20)
                    for click in clicks:
                        print(f"  🎯 Ad: {click['ad_id'][:8]}... | Amount: {click['payout_amount']:.6f} PYC")
                        print(f"      📅 Time: {click['created_at']}")
                        print()
                
                # Check notifications
                cursor.execute("""
                    SELECT * FROM notifications 
                    WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    ORDER BY created_at DESC LIMIT 3
                """)
                notifications = cursor.fetchall()
                
                if notifications:
                    print("📢 Recent Notifications:")
                    print("-" * 25)
                    for notif in notifications:
                        print(f"  📣 {notif['title']}: {notif['message']}")
                        print(f"      📅 Time: {notif['created_at']}")
                        print()
                
                time.sleep(10)  # Update every 10 seconds
                
                # Clear screen for next update
                print("\\n" + "=" * 60)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(5)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\\nMake sure:")
        print("  1. MySQL server is running")
        print("  2. 'adnetwrk' database exists")
        print("  3. Required tables are created")
    
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    print("📊 PythonCoin Database Monitor")
    print("Press Ctrl+C to stop")
    print("=" * 30)
    monitor_database()
'''
    
    with open('monitor_database.py', 'w') as f:
        f.write(monitor_code)
    
    print("📊 Created monitor_database.py - run it to see real-time database updates:")
    print("   python monitor_database.py")

if __name__ == "__main__":
    print("🔧 PythonCoin Comprehensive Client Database Fix")
    print("=" * 60)
    
    if not os.path.exists('pyqt.py'):
        print("❌ Error: pyqt.py file not found in current directory")
        exit(1)
    
    # Apply the fixes
    success = inject_comprehensive_client_fixes()
    
    if success:
        print("\n🎉 Comprehensive fixes applied successfully!")
        print("\n📋 Issues Fixed:")
        print("   ✅ Added missing test_portal_connection method")
        print("   ✅ Fixed 'portal server already running' state issues")
        print("   ✅ Enhanced database client registration")
        print("   ✅ Added real-time payment address tracking")
        print("   ✅ Implemented periodic database updates (15 sec)")
        print("   ✅ Added database maintenance (5 min)")
        print("   ✅ Enhanced click tracking with payment info")
        print("   ✅ Added balance monitoring in database")
        print("   ✅ Improved server state management")
        print("   ✅ Added comprehensive error handling")
        
        print("\n🚀 What happens now:")
        print("   • Client will register in database on startup")
        print("   • Payment address gets tracked in real-time")
        print("   • Balance updates every 15 seconds")
        print("   • All clicks and payments are logged")
        print("   • Server state is properly managed")
        
        print("\n📊 Database Tables Updated:")
        print("   • p2p_clients - Client info, payment addresses, balances")
        print("   • ad_clicks - Click tracking with payment amounts")
        print("   • notifications - System events and alerts")
        print("   • developer_sessions - Developer portal activity")
        
        print("\n🔍 Monitor your database:")
        print("   python monitor_database.py")
        
        # Create database monitor
        create_database_monitor_script()
        
    else:
        print("❌ Failed to apply fixes")
        
    print("\n" + "=" * 60)