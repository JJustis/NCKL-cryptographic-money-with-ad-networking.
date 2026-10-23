#!/usr/bin/env python3
"""
Enhanced PythonCoin Application Injector with MySQL Database Integration
This script injects database connectivity, ad file hosting, and developer portal integration
into the existing pyqt.py application.
"""

import os
import re
import shutil
import time
import json
import urllib.parse
import hashlib
import logging
from datetime import datetime

# Setup logging for injector
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PythonCoin-Enhanced-Injector")

class EnhancedPythonCoinInjector:
    def __init__(self, source_file="pyqt.py"):
        self.source_file = source_file
        self.backup_file = f"{source_file}.backup.{int(time.time())}"
        self.enhanced_file = f"{source_file}.enhanced"
        
    def inject_enhancements(self):
        """Main injection method with database integration"""
        print("🚀 Enhanced PythonCoin Injector with MySQL Integration Starting...")
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Read original file
        content = self.read_file()
        
        # Step 3: Inject database and payment enhancements
        content = self.inject_mysql_integration(content)
        content = self.inject_payment_verification(content)
        content = self.inject_ad_file_hosting(content)
        content = self.inject_developer_portal_integration(content)
        content = self.inject_blockchain_payment_processor(content)
        content = self.inject_real_time_ad_updates(content)
        content = self.patch_server_class_for_database(content)
        
        # Step 4: Write enhanced file
        self.write_enhanced_file(content)
        
        print("✅ Enhanced injection complete!")
        print(f"📁 Original file backed up as: {self.backup_file}")
        print(f"📁 Enhanced file created as: {self.enhanced_file}")
        print(f"🔄 To use enhanced version: mv {self.enhanced_file} {self.source_file}")
        
    def create_backup(self):
        """Create backup of original file"""
        if os.path.exists(self.source_file):
            shutil.copy2(self.source_file, self.backup_file)
            print(f"📋 Backup created: {self.backup_file}")
        else:
            raise FileNotFoundError(f"Source file {self.source_file} not found!")
    
    def read_file(self):
        """Read the original file"""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_enhanced_file(self, content):
        """Write the enhanced file"""
        with open(self.enhanced_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def inject_mysql_integration(self, content):
        """Inject MySQL database integration"""
        print("🗄️ Injecting MySQL database integration...")
        
        mysql_code = '''
# ============================================================================
# INJECTED: MySQL Database Integration
# ============================================================================

import mysql.connector
from mysql.connector import Error
import threading
from datetime import datetime, timedelta

class DatabaseManager:
    """Enhanced database manager for PythonCoin payments and ad tracking"""
    
    def __init__(self):
        self.connection = None
        self.connection_config = {
            'host': 'localhost',
            'database': 'pythoncoin_network',
            'user': 'pythoncoin_user',
            'password': 'secure_password',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection_lock = threading.Lock()
        self.last_connection_attempt = 0
        self.connection_retry_delay = 30  # 30 seconds between retry attempts
        
    def connect(self):
        """Establish database connection with retry logic"""
        current_time = time.time()
        
        # Don't retry too frequently
        if current_time - self.last_connection_attempt < self.connection_retry_delay:
            return False
        
        self.last_connection_attempt = current_time
        
        try:
            if self.connection and self.connection.is_connected():
                return True
            
            self.connection = mysql.connector.connect(**self.connection_config)
            
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                self.create_tables_if_not_exist()
                return True
                
        except Error as e:
            logger.warning(f"Database connection failed: {e}")
            self.connection = None
            return False
        
        return False
    
    def create_tables_if_not_exist(self):
        """Create necessary tables for the PythonCoin network"""
        try:
            cursor = self.connection.cursor()
            
            # Developers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS developers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    pythoncoin_address VARCHAR(64) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    total_earned DECIMAL(16, 8) DEFAULT 0.00000000,
                    total_clicks INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    status ENUM('active', 'suspended') DEFAULT 'active'
                )
            """)
            
            # Ad clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_clients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(64) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    host VARCHAR(45) NOT NULL,
                    port INT NOT NULL,
                    wallet_address VARCHAR(64),
                    status ENUM('online', 'offline') DEFAULT 'offline',
                    ad_count INT DEFAULT 0,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    capabilities JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Advertisements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS advertisements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ad_id VARCHAR(64) UNIQUE NOT NULL,
                    client_id VARCHAR(64) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    image_url VARCHAR(500),
                    click_url VARCHAR(500),
                    payout_rate DECIMAL(16, 8) NOT NULL,
                    advertiser_address VARCHAR(64),
                    status ENUM('active', 'paused', 'expired') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    total_clicks INT DEFAULT 0,
                    total_spent DECIMAL(16, 8) DEFAULT 0.00000000,
                    INDEX idx_client_id (client_id),
                    INDEX idx_status (status),
                    FOREIGN KEY (client_id) REFERENCES ad_clients(client_id)
                )
            """)
            
            # Click events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS click_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    event_id VARCHAR(64) UNIQUE NOT NULL,
                    ad_id VARCHAR(64) NOT NULL,
                    developer_username VARCHAR(50) NOT NULL,
                    developer_address VARCHAR(64) NOT NULL,
                    advertiser_address VARCHAR(64) NOT NULL,
                    payout_amount DECIMAL(16, 8) NOT NULL,
                    payment_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
                    blockchain_tx_id VARCHAR(64) NULL,
                    client_ip VARCHAR(45),
                    user_agent TEXT,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP NULL,
                    INDEX idx_ad_id (ad_id),
                    INDEX idx_developer (developer_username),
                    INDEX idx_payment_status (payment_status),
                    FOREIGN KEY (ad_id) REFERENCES advertisements(ad_id),
                    FOREIGN KEY (developer_username) REFERENCES developers(username)
                )
            """)
            
            # Payment transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    transaction_id VARCHAR(64) UNIQUE NOT NULL,
                    click_event_id INT NOT NULL,
                    from_address VARCHAR(64) NOT NULL,
                    to_address VARCHAR(64) NOT NULL,
                    amount DECIMAL(16, 8) NOT NULL,
                    blockchain_tx_id VARCHAR(64) NULL,
                    status ENUM('pending', 'confirmed', 'failed') DEFAULT 'pending',
                    confirmations INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP NULL,
                    INDEX idx_transaction_id (transaction_id),
                    INDEX idx_status (status),
                    FOREIGN KEY (click_event_id) REFERENCES click_events(id)
                )
            """)
            
            # JS generation requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS js_generation_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    request_id VARCHAR(64) UNIQUE NOT NULL,
                    developer_username VARCHAR(50) NOT NULL,
                    selected_clients JSON NOT NULL,
                    js_filename VARCHAR(200) NOT NULL,
                    js_hash VARCHAR(64) NOT NULL,
                    preferences JSON,
                    download_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_downloaded TIMESTAMP NULL,
                    INDEX idx_developer (developer_username),
                    FOREIGN KEY (developer_username) REFERENCES developers(username)
                )
            """)
            
            cursor.close()
            logger.info("Database tables created/verified successfully")
            
        except Error as e:
            logger.error(f"Error creating database tables: {e}")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute database query with connection management"""
        with self.connection_lock:
            if not self.connect():
                return None
            
            try:
                cursor = self.connection.cursor(dictionary=True if fetch else False)
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                    cursor.close()
                    return result
                else:
                    self.connection.commit()
                    result = cursor.lastrowid or cursor.rowcount
                    cursor.close()
                    return result
                    
            except Error as e:
                logger.error(f"Database query error: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                return None
    
    def record_click_event(self, ad_id, developer_username, developer_address, 
                          advertiser_address, payout_amount, client_ip=None, user_agent=None):
        """Record a click event in the database"""
        event_id = f"click_{int(time.time() * 1000)}_{hash(developer_username + ad_id) % 10000}"
        
        query = """
            INSERT INTO click_events 
            (event_id, ad_id, developer_username, developer_address, advertiser_address, 
             payout_amount, client_ip, user_agent) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (event_id, ad_id, developer_username, developer_address, 
                 advertiser_address, payout_amount, client_ip, user_agent)
        
        result = self.execute_query(query, params)
        if result:
            logger.info(f"Click event recorded: {event_id}")
            return event_id
        return None
    
    def update_payment_status(self, click_event_id, status, blockchain_tx_id=None):
        """Update payment status for a click event"""
        query = """
            UPDATE click_events 
            SET payment_status = %s, blockchain_tx_id = %s, processed_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """
        params = (status, blockchain_tx_id, click_event_id)
        
        return self.execute_query(query, params)
    
    def get_pending_payments(self):
        """Get all pending payments that need blockchain processing"""
        query = """
            SELECT ce.*, a.advertiser_address, a.payout_rate
            FROM click_events ce
            JOIN advertisements a ON ce.ad_id = a.ad_id
            WHERE ce.payment_status = 'pending'
            ORDER BY ce.clicked_at ASC
            LIMIT 100
        """
        
        return self.execute_query(query, fetch=True) or []
    
    def register_developer(self, username, pythoncoin_address, password_hash):
        """Register a new developer"""
        query = """
            INSERT INTO developers (username, pythoncoin_address, password_hash) 
            VALUES (%s, %s, %s)
        """
        params = (username, pythoncoin_address, password_hash)
        
        return self.execute_query(query, params)
    
    def authenticate_developer(self, username, password_hash):
        """Authenticate developer login"""
        query = """
            SELECT * FROM developers 
            WHERE username = %s AND password_hash = %s AND status = 'active'
        """
        params = (username, password_hash)
        
        result = self.execute_query(query, params, fetch=True)
        if result:
            # Update last login
            self.execute_query(
                "UPDATE developers SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                (username,)
            )
            return result[0]
        return None
    
    def update_client_status(self, client_id, name, host, port, wallet_address=None, 
                           status='online', ad_count=0, capabilities=None):
        """Update or insert client status"""
        query = """
            INSERT INTO ad_clients (client_id, name, host, port, wallet_address, status, ad_count, capabilities, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name), host = VALUES(host), port = VALUES(port),
            wallet_address = VALUES(wallet_address), status = VALUES(status),
            ad_count = VALUES(ad_count), capabilities = VALUES(capabilities),
            last_seen = CURRENT_TIMESTAMP
        """
        params = (client_id, name, host, port, wallet_address, status, ad_count, 
                 json.dumps(capabilities) if capabilities else None)
        
        return self.execute_query(query, params)
    
    def get_online_clients(self):
        """Get all online advertising clients"""
        query = """
            SELECT * FROM ad_clients 
            WHERE status = 'online' AND last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            ORDER BY last_seen DESC
        """
        
        return self.execute_query(query, fetch=True) or []
    
    def update_advertisement(self, ad_id, client_id, title, description, category,
                           image_url, click_url, payout_rate, advertiser_address, expires_at=None):
        """Update or insert advertisement"""
        query = """
            INSERT INTO advertisements 
            (ad_id, client_id, title, description, category, image_url, click_url, 
             payout_rate, advertiser_address, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title), description = VALUES(description),
            category = VALUES(category), image_url = VALUES(image_url),
            click_url = VALUES(click_url), payout_rate = VALUES(payout_rate),
            advertiser_address = VALUES(advertiser_address), expires_at = VALUES(expires_at)
        """
        params = (ad_id, client_id, title, description, category, image_url, 
                 click_url, payout_rate, advertiser_address, expires_at)
        
        return self.execute_query(query, params)
    
    def get_active_advertisements(self, client_id=None):
        """Get active advertisements, optionally filtered by client"""
        if client_id:
            query = """
                SELECT * FROM advertisements 
                WHERE client_id = %s AND status = 'active' 
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """
            params = (client_id,)
        else:
            query = """
                SELECT * FROM advertisements 
                WHERE status = 'active' 
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """
            params = None
        
        return self.execute_query(query, params, fetch=True) or []
    
    def record_js_generation(self, developer_username, selected_clients, js_filename, 
                           js_hash, preferences=None):
        """Record JavaScript generation request"""
        request_id = f"js_{int(time.time() * 1000)}_{hash(developer_username + js_filename) % 10000}"
        
        query = """
            INSERT INTO js_generation_requests 
            (request_id, developer_username, selected_clients, js_filename, js_hash, preferences)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (request_id, developer_username, json.dumps(selected_clients), 
                 js_filename, js_hash, json.dumps(preferences) if preferences else None)
        
        result = self.execute_query(query, params)
        if result:
            logger.info(f"JS generation recorded: {request_id}")
            return request_id
        return None
    
    def get_developer_stats(self, username):
        """Get comprehensive stats for a developer"""
        query = """
            SELECT 
                d.total_earned,
                d.total_clicks,
                COUNT(DISTINCT jr.id) as js_generations,
                COUNT(DISTINCT ce.id) as recent_clicks,
                COALESCE(SUM(ce.payout_amount), 0) as recent_earnings
            FROM developers d
            LEFT JOIN js_generation_requests jr ON d.username = jr.developer_username
            LEFT JOIN click_events ce ON d.username = ce.developer_username 
                AND ce.clicked_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
            WHERE d.username = %s
            GROUP BY d.username
        """
        params = (username,)
        
        result = self.execute_query(query, params, fetch=True)
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

'''
        
        # Find the best place to inject (after imports, before main classes)
        injection_point = content.find("# ============================================================================")
        if injection_point == -1:
            injection_point = content.find("class CryptoP2PManager")
        
        if injection_point != -1:
            content = content[:injection_point] + mysql_code + content[injection_point:]
            print("✅ MySQL integration injected successfully")
        else:
            print("⚠️ Could not find injection point for MySQL integration")
        
        return content
    
    def inject_payment_verification(self, content):
        """Inject payment verification and blockchain transaction processing"""
        print("💰 Injecting payment verification system...")
        
        payment_code = '''
# ============================================================================
# INJECTED: Payment Verification and Processing System
# ============================================================================

class PaymentProcessor:
    """Handles payment verification and blockchain transaction processing"""
    
    def __init__(self, database_manager, blockchain, wallet):
        self.db = database_manager
        self.blockchain = blockchain
        self.wallet = wallet
        self.processing_queue = []
        self.processing_thread = None
        self.running = False
        
    def start_processing(self):
        """Start the payment processing thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_payments_loop, daemon=True)
        self.processing_thread.start()
        logger.info("Payment processing thread started")
    
    def stop_processing(self):
        """Stop the payment processing thread"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Payment processing thread stopped")
    
    def _process_payments_loop(self):
        """Main payment processing loop"""
        while self.running:
            try:
                # Get pending payments from database
                pending_payments = self.db.get_pending_payments()
                
                for payment in pending_payments:
                    if not self.running:
                        break
                    
                    try:
                        self._process_single_payment(payment)
                    except Exception as e:
                        logger.error(f"Error processing payment {payment['id']}: {e}")
                        # Mark as failed
                        self.db.update_payment_status(payment['id'], 'failed')
                
                # Wait before next batch
                time.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"Payment processing loop error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _process_single_payment(self, payment):
        """Process a single payment transaction"""
        try:
            # Mark as processing
            self.db.update_payment_status(payment['id'], 'processing')
            
            # Check if we have sufficient balance
            if hasattr(self.wallet, 'get_balance'):
                balance = self.wallet.get_balance()
            else:
                balance = 0
            
            if balance < payment['payout_amount']:
                logger.warning(f"Insufficient balance for payment {payment['id']}: {balance} < {payment['payout_amount']}")
                # Keep as pending, will retry later
                self.db.update_payment_status(payment['id'], 'pending')
                return
            
            # Create blockchain transaction
            tx = self.wallet.send(payment['developer_address'], payment['payout_amount'])
            
            if tx:
                # Update database with transaction ID
                self.db.update_payment_status(payment['id'], 'completed', tx.tx_id)
                
                # Update developer earnings
                self.db.execute_query(
                    "UPDATE developers SET total_earned = total_earned + %s, total_clicks = total_clicks + 1 WHERE username = %s",
                    (payment['payout_amount'], payment['developer_username'])
                )
                
                # Update advertisement stats
                self.db.execute_query(
                    "UPDATE advertisements SET total_clicks = total_clicks + 1, total_spent = total_spent + %s WHERE ad_id = %s",
                    (payment['payout_amount'], payment['ad_id'])
                )
                
                logger.info(f"Payment processed successfully: {payment['payout_amount']} PYC to {payment['developer_username']}")
                
            else:
                # Transaction failed
                self.db.update_payment_status(payment['id'], 'failed')
                logger.error(f"Blockchain transaction failed for payment {payment['id']}")
                
        except Exception as e:
            logger.error(f"Error processing payment {payment['id']}: {e}")
            self.db.update_payment_status(payment['id'], 'failed')
    
    def queue_payment(self, ad_id, developer_username, developer_address, 
                     advertiser_address, payout_amount, client_ip=None, user_agent=None):
        """Queue a new payment for processing"""
        try:
            # Record in database
            event_id = self.db.record_click_event(
                ad_id, developer_username, developer_address,
                advertiser_address, payout_amount, client_ip, user_agent
            )
            
            if event_id:
                logger.info(f"Payment queued: {payout_amount} PYC for {developer_username}")
                return event_id
            else:
                logger.error("Failed to queue payment - database error")
                return None
                
        except Exception as e:
            logger.error(f"Error queueing payment: {e}")
            return None
    
    def get_payment_status(self, event_id):
        """Get payment status by event ID"""
        query = "SELECT payment_status, blockchain_tx_id FROM click_events WHERE event_id = %s"
        result = self.db.execute_query(query, (event_id,), fetch=True)
        
        if result:
            return {
                'status': result[0]['payment_status'],
                'transaction_id': result[0]['blockchain_tx_id']
            }
        return None

'''
        
        # Inject before main window class
        injection_point = content.find("class UnifiedPythonCoinWallet")
        if injection_point != -1:
            content = content[:injection_point] + payment_code + content[injection_point:]
            print("✅ Payment verification system injected successfully")
        else:
            print("⚠️ Could not find injection point for payment system")
        
        return content
    
    def inject_ad_file_hosting(self, content):
        """Inject ad file hosting capabilities"""
        print("📁 Injecting ad file hosting system...")
        
        hosting_code = '''
# ============================================================================
# INJECTED: Ad File Hosting System
# ============================================================================

class AdFileManager:
    """Manages ad file storage and serving"""
    
    def __init__(self, base_directory="ad_files"):
        self.base_directory = base_directory
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create directories
        os.makedirs(self.base_directory, exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, 'videos'), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, 'temp'), exist_ok=True)
    
    def save_ad_file(self, file_data, filename, ad_id):
        """Save an uploaded ad file"""
        try:
            # Validate file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.allowed_extensions:
                raise ValueError(f"File type {file_ext} not allowed")
            
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File size too large: {len(file_data)} bytes")
            
            # Generate safe filename
            safe_filename = f"{ad_id}_{int(time.time())}{file_ext}"
            
            # Determine subdirectory
            if file_ext in {'.mp4', '.webm'}:
                subdir = 'videos'
            else:
                subdir = 'images'
            
            # Save file
            file_path = os.path.join(self.base_directory, subdir, safe_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Return URL path
            return f"/ad_files/{subdir}/{safe_filename}"
            
        except Exception as e:
            logger.error(f"Error saving ad file: {e}")
            return None
    
    def get_file_path(self, file_url):
        """Get local file path from URL"""
        try:
            # Remove leading slash and ad_files prefix
            rel_path = file_url.lstrip('/').replace('ad_files/', '')
            return os.path.join(self.base_directory, rel_path)
        except:
            return None
    
    def delete_ad_file(self, file_url):
        """Delete an ad file"""
        try:
            file_path = self.get_file_path(file_url)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            logger.error(f"Error deleting ad file: {e}")
        return False
    
    def cleanup_old_files(self, days_old=30):
        """Clean up files older than specified days"""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            
            for root, dirs, files in os.walk(self.base_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

'''
        
        # Inject after the payment system
        injection_point = content.find("class UnifiedPythonCoinWallet")
        if injection_point != -1:
            content = content[:injection_point] + hosting_code + content[injection_point:]
            print("✅ Ad file hosting system injected successfully")
        else:
            print("⚠️ Could not find injection point for ad file hosting")
        
        return content
    
    def inject_developer_portal_integration(self, content):
        """Inject integration with secupgrade.com developer portal"""
        print("🌐 Injecting developer portal integration...")
        
        portal_integration_code = '''
# ============================================================================
# INJECTED: Developer Portal Integration (secupgrade.com)
# ============================================================================

class DeveloperPortalIntegration:
    """Integration with secupgrade.com developer portal"""
    
    def __init__(self, database_manager, payment_processor, ad_file_manager):
        self.db = database_manager
        self.payment_processor = payment_processor
        self.ad_file_manager = ad_file_manager
        self.external_portal_url = "https://secupgrade.com/livepy/pythoncoin/"
        
    def handle_external_portal_request(self, request_data):
        """Handle requests from external developer portal"""
        try:
            action = request_data.get('action')
            
            if action == 'get_client_info':
                return self.get_client_info()
            elif action == 'get_available_ads':
                return self.get_available_ads()
            elif action == 'generate_custom_js':
                return self.generate_custom_js_for_portal(request_data)
            elif action == 'record_ad_click':
                return self.record_external_click(request_data)
            elif action == 'verify_payment':
                return self.verify_payment_status(request_data)
            elif action == 'update_ad_content':
                return self.update_ad_content(request_data)
            else:
                return {'success': False, 'error': 'Unknown action'}
                
        except Exception as e:
            logger.error(f"Error handling portal request: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_client_info(self):
        """Get client information for external portal"""
        try:
            # Get wallet and blockchain info
            wallet_info = {
                'client_id': f'pyc_client_{int(time.time())}',
                'name': 'PythonCoin Wallet Client',
                'version': '2.1.0',
                'capabilities': ['ad_serving', 'payments', 'file_hosting', 'real_time_updates'],
                'status': 'online'
            }
            
            # Add database stats if available
            if self.db.connect():
                ads = self.db.get_active_advertisements()
                wallet_info['ad_count'] = len(ads)
                wallet_info['categories'] = list(set(ad['category'] for ad in ads if ad['category']))
            
            return {'success': True, 'client_info': wallet_info}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_available_ads(self):
        """Get available advertisements for external portal"""
        try:
            if not self.db.connect():
                return {'success': False, 'error': 'Database connection failed'}
            
            ads = self.db.get_active_advertisements()
            
            # Format ads for external portal
            formatted_ads = []
            for ad in ads:
                formatted_ad = {
                    'id': ad['ad_id'],
                    'title': ad['title'],
                    'description': ad['description'],
                    'category': ad['category'],
                    'image_url': ad['image_url'],
                    'click_url': ad['click_url'],
                    'payout': float(ad['payout_rate']),
                    'advertiser': ad['advertiser_address'][:8] + '...' if ad['advertiser_address'] else 'Unknown',
                    'created_at': ad['created_at'].isoformat() if ad['created_at'] else None
                }
                formatted_ads.append(formatted_ad)
            
            return {'success': True, 'ads': formatted_ads, 'total': len(formatted_ads)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_custom_js_for_portal(self, request_data):
        """Generate custom JavaScript for external developer portal"""
        try:
            developer_username = request_data.get('developer_username')
            developer_address = request_data.get('developer_address')
            selected_clients = request_data.get('selected_clients', [])
            preferences = request_data.get('preferences', {})
            
            if not developer_username or not developer_address:
                return {'success': False, 'error': 'Missing developer information'}
            
            # Generate enhanced JavaScript code
            js_content = self.generate_enhanced_portal_js(
                developer_username, developer_address, selected_clients, preferences
            )
            
            # Create filename and hash
            js_filename = f"pyc_portal_{developer_username}_{int(time.time())}.js"
            js_hash = hashlib.sha256(js_content.encode()).hexdigest()
            
            # Save JavaScript file
            js_dir = os.path.join(os.getcwd(), 'js_portal')
            os.makedirs(js_dir, exist_ok=True)
            
            js_filepath = os.path.join(js_dir, js_filename)
            with open(js_filepath, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # Record in database
            if self.db.connect():
                self.db.record_js_generation(
                    developer_username, selected_clients, js_filename, js_hash, preferences
                )
            
            return {
                'success': True,
                'js_filename': js_filename,
                'js_url': f'http://127.0.0.1:8082/js_portal/{js_filename}',
                'js_hash': js_hash,
                'features': ['multi_client', 'auto_payment', 'real_time_updates', 'portal_integration']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_enhanced_portal_js(self, developer_username, developer_address, selected_clients, preferences):
        """Generate enhanced JavaScript for portal integration"""
        # Use string formatting instead of f-string to avoid conflicts
        js_template = """// PythonCoin Portal Integration JavaScript
// Developer: {developer_username}
// Address: {developer_address}
// Generated: {timestamp}
// Portal: secupgrade.com integration

(function() {{
    'use strict';
    
    var PYC_PORTAL_CONFIG = {{
        developer: '{developer_username}',
        address: '{developer_address}',
        clients: {selected_clients_json},
        preferences: {preferences_json},
        portalApi: 'https://secupgrade.com/livepy/pythoncoin/api.php',
        clientApi: 'http://127.0.0.1:8082',
        version: '2.1.0',
        features: ['auto_payment', 'real_time_updates', 'portal_sync']
    }};
    
    var currentAd = null;
    var rotationTimer = null;
    var paymentQueue = [];
    
    function initPortalIntegration() {{
        console.log('[PYC-PORTAL] Initializing portal integration');
        
        // Find ad zones
        var zones = document.querySelectorAll('[data-pyc-zone]');
        console.log('[PYC-PORTAL] Found ' + zones.length + ' ad zones');
        
        zones.forEach(function(zone) {{
            var zoneName = zone.getAttribute('data-pyc-zone');
            loadAdForZone(zone, zoneName);
        }});
        
        // Start rotation if enabled
        if (PYC_PORTAL_CONFIG.preferences.autoRotate) {{
            startAdRotation();
        }}
        
        // Start payment processing
        startPaymentProcessing();
    }}
    
    function loadAdForZone(container, zoneName) {{
        console.log('[PYC-PORTAL] Loading ad for zone: ' + zoneName);
        
        // Get ads from client
        fetch(PYC_PORTAL_CONFIG.clientApi + '/available_ads?zone=' + zoneName)
            .then(function(response) {{ return response.json(); }})
            .then(function(data) {{
                if (data.success && data.ads && data.ads.length > 0) {{
                    displayAd(container, data.ads[0], zoneName);
                }} else {{
                    showPlaceholder(container, 'No ads available');
                }}
            }})
            .catch(function(error) {{
                console.warn('[PYC-PORTAL] Error loading ads:', error);
                showPlaceholder(container, 'Loading ads...');
            }});
    }}
    
    function displayAd(container, ad, zoneName) {{
        currentAd = ad;
        
        var adHtml = '<div class="pyc-portal-ad" style="' +
            'border: 2px solid #0066cc; border-radius: 12px; padding: 20px; ' +
            'background: linear-gradient(135deg, #fff 0%, #f8fffe 50%, #f0f9ff 100%); ' +
            'position: relative; cursor: pointer; transition: all 0.3s ease;">' +
            
            '<div style="position: absolute; top: 10px; right: 10px; ' +
            'background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; ' +
            'padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">' +
            '💎 PYC Portal</div>' +
            
            '<h3 style="color: #0066cc; margin: 0 0 10px 0; font-size: 18px;">' + ad.title + '</h3>' +
            '<p style="color: #666; margin: 0 0 15px 0; font-size: 14px;">' + ad.description + '</p>' +
            
            '<div style="display: flex; justify-content: space-between; align-items: center;">' +
            '<span style="color: #0066cc; font-weight: 600; font-size: 12px;">📱 ' + ad.category + ' • 🌐 Portal Network</span>' +
            '<span style="background: linear-gradient(45deg, #28a745, #20c997); color: white; ' +
            'padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold;">' +
            '+' + (ad.payout || 0.001).toFixed(6) + ' PYC</span>' +
            '</div>' +
            '</div>';
        
        container.innerHTML = adHtml;
        
        // Add click handler
        container.querySelector('.pyc-portal-ad').onclick = function() {{
            handleAdClick(ad, zoneName);
        }};
        
        // Add hover effects
        var adElement = container.querySelector('.pyc-portal-ad');
        adElement.addEventListener('mouseenter', function() {{
            this.style.transform = 'translateY(-3px) scale(1.02)';
            this.style.boxShadow = '0 12px 35px rgba(0,102,204,0.3)';
        }});
        adElement.addEventListener('mouseleave', function() {{
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 6px 20px rgba(0,102,204,0.15)';
        }});
    }}
    
    function handleAdClick(ad, zoneName) {{
        console.log('[PYC-PORTAL] Ad clicked:', ad.id);
        
        // Show earning animation
        showEarningPopup(ad.payout || 0.001);
        
        // Queue payment
        queuePayment(ad, zoneName);
        
        // Open ad URL
        if (ad.click_url && ad.click_url !== '#') {{
            setTimeout(function() {{
                window.open(ad.click_url, '_blank');
            }}, 600);
        }}
    }}
    
    function queuePayment(ad, zoneName) {{
        var payment = {{
            ad_id: ad.id,
            developer_username: PYC_PORTAL_CONFIG.developer,
            developer_address: PYC_PORTAL_CONFIG.address,
            payout_amount: ad.payout || 0.001,
            zone: zoneName,
            timestamp: Date.now(),
            processed: false
        }};
        
        paymentQueue.push(payment);
        console.log('[PYC-PORTAL] Payment queued:', payment);
    }}
    
    function startPaymentProcessing() {{
        setInterval(function() {{
            if (paymentQueue.length > 0) {{
                var payment = paymentQueue.shift();
                processPayment(payment);
            }}
        }}, 2000); // Process every 2 seconds
    }}
    
    function processPayment(payment) {{
        console.log('[PYC-PORTAL] Processing payment:', payment);
        
        // Send to client for blockchain processing
        fetch(PYC_PORTAL_CONFIG.clientApi + '/record_click', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                ad_id: payment.ad_id,
                developer_username: payment.developer_username,
                developer_address: payment.developer_address,
                payout_amount: payment.payout_amount,
                zone: payment.zone,
                source: 'portal_integration'
            }})
        }})
        .then(function(response) {{ return response.json(); }})
        .then(function(data) {{
            if (data.success) {{
                console.log('[PYC-PORTAL] Payment processed successfully');
                showSuccessNotification('Payment processed: ' + payment.payout_amount.toFixed(6) + ' PYC');
            }} else {{
                console.error('[PYC-PORTAL] Payment processing failed:', data.error);
            }}
        }})
        .catch(function(error) {{
            console.error('[PYC-PORTAL] Payment error:', error);
            // Re-queue for retry
            paymentQueue.push(payment);
        }});
    }}
    
    function showEarningPopup(amount) {{
        var popup = document.createElement('div');
        popup.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); ' +
            'background: linear-gradient(135deg, #28a745, #20c997, #17a2b8); color: white; ' +
            'padding: 30px 40px; border-radius: 20px; z-index: 10001; text-align: center; ' +
            'font-family: "Segoe UI", Arial, sans-serif; font-weight: bold; ' +
            'box-shadow: 0 20px 60px rgba(40, 167, 69, 0.4); ' +
            'animation: portalPopupAnimation 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);';
        
        popup.innerHTML = '<div style="font-size: 36px; margin-bottom: 10px;">💰</div>' +
            '<div style="font-size: 22px; margin-bottom: 8px;">PythonCoin Earned!</div>' +
            '<div style="font-size: 18px; opacity: 0.95;">+' + amount.toFixed(6) + ' PYC</div>' +
            '<div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">Portal Network</div>';
        
        document.body.appendChild(popup);
        setTimeout(function() {{ popup.remove(); }}, 3500);
    }}
    
    function showSuccessNotification(message) {{
        var notification = document.createElement('div');
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000; ' +
            'background: #28a745; color: white; padding: 15px 20px; border-radius: 8px; ' +
            'font-weight: bold; box-shadow: 0 4px 12px rgba(0,0,0,0.3);';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(function() {{ notification.remove(); }}, 4000);
    }}
    
    function showPlaceholder(container, message) {{
        container.innerHTML = '<div style="text-align: center; padding: 40px; ' +
            'border: 2px dashed #ccc; border-radius: 12px; color: #666;">' +
            '<h3>🔍 PythonCoin Portal</h3><p>' + message + '</p></div>';
    }}
    
    function startAdRotation() {{
        var interval = (PYC_PORTAL_CONFIG.preferences.rotationInterval || 30) * 1000;
        rotationTimer = setInterval(function() {{
            var zones = document.querySelectorAll('[data-pyc-zone]');
            zones.forEach(function(zone) {{
                var zoneName = zone.getAttribute('data-pyc-zone');
                loadAdForZone(zone, zoneName);
            }});
        }}, interval);
    }}
    
    // Add animation styles
    if (!document.querySelector('#pyc-portal-styles')) {{
        var style = document.createElement('style');
        style.id = 'pyc-portal-styles';
        style.textContent = '@keyframes portalPopupAnimation {{' +
            '0% {{ transform: translate(-50%, -50%) scale(0.3) rotate(-10deg); opacity: 0; }}' +
            '50% {{ transform: translate(-50%, -50%) scale(1.05) rotate(2deg); opacity: 1; }}' +
            '100% {{ transform: translate(-50%, -50%) scale(1) rotate(0deg); opacity: 1; }}' +
            '}}';
        document.head.appendChild(style);
    }}
    
    // Initialize when ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initPortalIntegration);
    }} else {{
        initPortalIntegration();
    }}
    
    console.log('[PYC-PORTAL] Portal integration JavaScript loaded');
    
}})();""".format(
            developer_username=developer_username,
            developer_address=developer_address,
            timestamp=datetime.now().isoformat(),
            selected_clients_json=json.dumps(selected_clients),
            preferences_json=json.dumps(preferences)
        )
        
        return js_template
    
    def record_external_click(self, request_data):
        """Record click from external portal"""
        try:
            ad_id = request_data.get('ad_id')
            developer_username = request_data.get('developer_username')
            developer_address = request_data.get('developer_address')
            payout_amount = float(request_data.get('payout_amount', 0))
            
            if not all([ad_id, developer_username, developer_address]):
                return {'success': False, 'error': 'Missing required fields'}
            
            # Queue payment
            event_id = self.payment_processor.queue_payment(
                ad_id, developer_username, developer_address,
                'portal_advertiser', payout_amount,
                request_data.get('client_ip'), request_data.get('user_agent')
            )
            
            if event_id:
                return {'success': True, 'event_id': event_id, 'message': 'Payment queued for processing'}
            else:
                return {'success': False, 'error': 'Failed to queue payment'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment_status(self, request_data):
        """Verify payment status for external portal"""
        try:
            event_id = request_data.get('event_id')
            if not event_id:
                return {'success': False, 'error': 'Missing event_id'}
            
            status = self.payment_processor.get_payment_status(event_id)
            return {'success': True, 'payment_status': status}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_ad_content(self, request_data):
        """Update ad content from external portal"""
        try:
            ad_id = request_data.get('ad_id')
            if not ad_id:
                return {'success': False, 'error': 'Missing ad_id'}
            
            # Update ad in database
            updated = self.db.update_advertisement(
                ad_id,
                request_data.get('client_id', 'portal_client'),
                request_data.get('title', ''),
                request_data.get('description', ''),
                request_data.get('category', 'general'),
                request_data.get('image_url', ''),
                request_data.get('click_url', ''),
                float(request_data.get('payout_rate', 0.001)),
                request_data.get('advertiser_address', ''),
                request_data.get('expires_at')
            )
            
            if updated:
                return {'success': True, 'message': 'Ad content updated successfully'}
            else:
                return {'success': False, 'error': 'Failed to update ad content'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

'''
        
        # Inject before main window class
        injection_point = content.find("class UnifiedPythonCoinWallet")
        if injection_point != -1:
            content = content[:injection_point] + portal_integration_code + content[injection_point:]
            print("✅ Developer portal integration injected successfully")
        else:
            print("⚠️ Could not find injection point for portal integration")
        
        return content
    
    def inject_blockchain_payment_processor(self, content):
        """Inject enhanced blockchain payment processing"""
        print("⛓️ Injecting blockchain payment processor...")
        
        blockchain_processor_code = '''
# ============================================================================
# INJECTED: Enhanced Blockchain Payment Processor
# ============================================================================

class BlockchainPaymentProcessor:
    """Enhanced blockchain payment processing with automatic transaction creation"""
    
    def __init__(self, wallet, blockchain, database_manager):
        self.wallet = wallet
        self.blockchain = blockchain
        self.db = database_manager
        self.auto_processing = True
        self.min_payout_threshold = 0.000001  # Minimum payout amount
        self.batch_processing = True
        self.batch_size = 10
        
    def process_developer_payment(self, developer_address, amount, event_id, advertiser_address=None):
        """Process payment to developer with enhanced error handling"""
        try:
            # Validate amount
            if amount < self.min_payout_threshold:
                logger.warning(f"Payment amount too small: {amount}")
                return False
            
            # Check wallet balance
            try:
                balance = self.wallet.get_balance() if hasattr(self.wallet, 'get_balance') else 0
            except:
                balance = 0
            
            if balance < amount:
                logger.warning(f"Insufficient balance: {balance} < {amount}")
                return False
            
            # Create blockchain transaction
            tx = self.wallet.send(developer_address, amount)
            
            if tx:
                # Update database with transaction details
                if self.db.connect():
                    self.db.update_payment_status(event_id, 'completed', tx.tx_id)
                
                logger.info(f"Payment sent: {amount} PYC to {developer_address[:8]}... (TX: {tx.tx_id[:16]}...)")
                return tx.tx_id
            else:
                logger.error(f"Transaction failed for payment {event_id}")
                if self.db.connect():
                    self.db.update_payment_status(event_id, 'failed')
                return False
                
        except Exception as e:
            logger.error(f"Error processing payment {event_id}: {e}")
            if self.db.connect():
                self.db.update_payment_status(event_id, 'failed')
            return False
    
    def batch_process_payments(self):
        """Process multiple payments in batch for efficiency"""
        try:
            if not self.db.connect():
                return
            
            # Get pending payments
            pending_payments = self.db.get_pending_payments()
            
            if not pending_payments:
                return
            
            # Group payments by developer for batch processing
            developer_payments = {}
            for payment in pending_payments[:self.batch_size]:
                dev_addr = payment['developer_address']
                if dev_addr not in developer_payments:
                    developer_payments[dev_addr] = []
                developer_payments[dev_addr].append(payment)
            
            # Process payments for each developer
            for dev_addr, payments in developer_payments.items():
                total_amount = sum(p['payout_amount'] for p in payments)
                
                # Check if we should batch or send individually
                if len(payments) > 1 and total_amount > 0.001:
                    # Send batch payment
                    batch_tx_id = self.process_batch_payment(dev_addr, payments, total_amount)
                    if batch_tx_id:
                        # Update all payments in batch
                        for payment in payments:
                            self.db.update_payment_status(payment['id'], 'completed', batch_tx_id)
                else:
                    # Send individual payments
                    for payment in payments:
                        self.process_developer_payment(
                            payment['developer_address'],
                            payment['payout_amount'],
                            payment['id'],
                            payment.get('advertiser_address')
                        )
                        
        except Exception as e:
            logger.error(f"Error in batch payment processing: {e}")
    
    def process_batch_payment(self, developer_address, payments, total_amount):
        """Process multiple payments as a single transaction"""
        try:
            # Check balance
            balance = self.wallet.get_balance() if hasattr(self.wallet, 'get_balance') else 0
            if balance < total_amount:
                return None
            
            # Create single transaction for total amount
            tx = self.wallet.send(developer_address, total_amount)
            
            if tx:
                logger.info(f"Batch payment sent: {total_amount} PYC to {developer_address[:8]}... for {len(payments)} clicks")
                return tx.tx_id
            
        except Exception as e:
            logger.error(f"Error processing batch payment: {e}")
        
        return None
    
    def verify_transaction_on_blockchain(self, tx_id):
        """Verify transaction exists on blockchain"""
        try:
            # Search through blockchain for transaction
            for block in self.blockchain.chain:
                for tx in block.transactions:
                    if getattr(tx, 'tx_id', '') == tx_id:
                        return {
                            'confirmed': True,
                            'block_index': block.index,
                            'timestamp': block.timestamp,
                            'transaction': tx
                        }
            
            # Check pending transactions
            for tx in self.blockchain.pending_transactions:
                if getattr(tx, 'tx_id', '') == tx_id:
                    return {
                        'confirmed': False,
                        'pending': True,
                        'transaction': tx
                    }
            
            return {'confirmed': False, 'found': False}
            
        except Exception as e:
            logger.error(f"Error verifying transaction {tx_id}: {e}")
            return {'error': str(e)}
    
    def get_payment_history(self, developer_address, limit=100):
        """Get payment history for a developer"""
        try:
            if not self.db.connect():
                return []
            
            query = """
                SELECT ce.*, a.title as ad_title 
                FROM click_events ce
                LEFT JOIN advertisements a ON ce.ad_id = a.ad_id
                WHERE ce.developer_address = %s 
                ORDER BY ce.clicked_at DESC 
                LIMIT %s
            """
            
            return self.db.execute_query(query, (developer_address, limit), fetch=True) or []
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return []
    
    def calculate_developer_earnings(self, developer_username, period_days=30):
        """Calculate developer earnings for a specific period"""
        try:
            if not self.db.connect():
                return {'total': 0, 'clicks': 0}
            
            query = """
                SELECT 
                    COUNT(*) as total_clicks,
                    COALESCE(SUM(payout_amount), 0) as total_earned,
                    COUNT(CASE WHEN payment_status = 'completed' THEN 1 END) as paid_clicks,
                    COALESCE(SUM(CASE WHEN payment_status = 'completed' THEN payout_amount ELSE 0 END), 0) as confirmed_earnings
                FROM click_events 
                WHERE developer_username = %s 
                AND clicked_at > DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            result = self.db.execute_query(query, (developer_username, period_days), fetch=True)
            
            if result:
                return {
                    'total_clicks': result[0]['total_clicks'],
                    'total_earned': float(result[0]['total_earned']),
                    'paid_clicks': result[0]['paid_clicks'],
                    'confirmed_earnings': float(result[0]['confirmed_earnings']),
                    'pending_earnings': float(result[0]['total_earned']) - float(result[0]['confirmed_earnings'])
                }
            
            return {'total_clicks': 0, 'total_earned': 0, 'paid_clicks': 0, 'confirmed_earnings': 0, 'pending_earnings': 0}
            
        except Exception as e:
            logger.error(f"Error calculating earnings: {e}")
            return {'error': str(e)}

'''
        
        # Inject before main window class
        injection_point = content.find("class UnifiedPythonCoinWallet")
        if injection_point != -1:
            content = content[:injection_point] + blockchain_processor_code + content[injection_point:]
            print("✅ Blockchain payment processor injected successfully")
        else:
            print("⚠️ Could not find injection point for blockchain processor")
        
        return content
    
    def inject_real_time_ad_updates(self, content):
        """Inject real-time ad updates system"""
        print("🔄 Injecting real-time ad updates...")
        
        real_time_updates_code = '''
# ============================================================================
# INJECTED: Real-time Ad Updates System
# ============================================================================

class RealTimeAdUpdates:
    """Manages real-time advertisement updates"""
    
    def __init__(self, database_manager, ad_file_manager):
        self.db = database_manager
        self.ad_file_manager = ad_file_manager
        self.update_listeners = set()
        self.ad_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
    def register_update_listener(self, callback):
        """Register a callback for ad updates"""
        self.update_listeners.add(callback)
    
    def unregister_update_listener(self, callback):
        """Unregister an update listener"""
        self.update_listeners.discard(callback)
    
    def notify_listeners(self, event_type, ad_data):
        """Notify all listeners of ad updates"""
        for callback in self.update_listeners:
            try:
                callback(event_type, ad_data)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")
    
    def update_ad_content(self, ad_id, updates):
        """Update advertisement content in real-time"""
        try:
            if not self.db.connect():
                return False
            
            # Get current ad data
            current_ad = self.get_cached_ad(ad_id)
            if not current_ad:
                return False
            
            # Apply updates
            updated_fields = {}
            for field, value in updates.items():
                if field in ['title', 'description', 'category', 'click_url', 'payout_rate', 'image_url']:
                    updated_fields[field] = value
            
            if not updated_fields:
                return False
            
            # Update in database
            success = self.db.update_advertisement(
                ad_id,
                current_ad['client_id'],
                updated_fields.get('title', current_ad['title']),
                updated_fields.get('description', current_ad['description']),
                updated_fields.get('category', current_ad['category']),
                updated_fields.get('image_url', current_ad['image_url']),
                updated_fields.get('click_url', current_ad['click_url']),
                updated_fields.get('payout_rate', current_ad['payout_rate']),
                current_ad['advertiser_address'],
                current_ad['expires_at']
            )
            
            if success:
                # Clear cache
                self.invalidate_ad_cache(ad_id)
                
                # Notify listeners
                self.notify_listeners('ad_updated', {'ad_id': ad_id, 'updates': updated_fields})
                
                logger.info(f"Ad {ad_id} updated successfully")
                return True
            
        except Exception as e:
            logger.error(f"Error updating ad {ad_id}: {e}")
        
        return False
    
    def get_cached_ad(self, ad_id):
        """Get advertisement from cache or database"""
        try:
            # Check cache first
            if ad_id in self.ad_cache:
                cached_data, timestamp = self.ad_cache[ad_id]
                if time.time() - timestamp < self.cache_expiry:
                    return cached_data
            
            # Fetch from database
            if not self.db.connect():
                return None
            
            query = "SELECT * FROM advertisements WHERE ad_id = %s"
            result = self.db.execute_query(query, (ad_id,), fetch=True)
            
            if result:
                ad_data = result[0]
                # Cache the result
                self.ad_cache[ad_id] = (ad_data, time.time())
                return ad_data
            
        except Exception as e:
            logger.error(f"Error getting cached ad {ad_id}: {e}")
        
        return None
    
    def invalidate_ad_cache(self, ad_id=None):
        """Invalidate advertisement cache"""
        if ad_id:
            self.ad_cache.pop(ad_id, None)
        else:
            self.ad_cache.clear()
    
    def upload_ad_file(self, ad_id, file_data, filename):
        """Upload new file for advertisement"""
        try:
            # Save file
            file_url = self.ad_file_manager.save_ad_file(file_data, filename, ad_id)
            
            if file_url:
                # Update ad in database
                current_ad = self.get_cached_ad(ad_id)
                if current_ad:
                    self.update_ad_content(ad_id, {'image_url': file_url})
                    
                    # Delete old file if different
                    old_file_url = current_ad.get('image_url')
                    if old_file_url and old_file_url != file_url:
                        self.ad_file_manager.delete_ad_file(old_file_url)
                
                logger.info(f"File uploaded for ad {ad_id}: {file_url}")
                return file_url
            
        except Exception as e:
            logger.error(f"Error uploading file for ad {ad_id}: {e}")
        
        return None
    
    def get_ad_performance_stats(self, ad_id):
        """Get real-time performance statistics for an ad"""
        try:
            if not self.db.connect():
                return {}
            
            query = """
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(CASE WHEN payment_status = 'completed' THEN 1 END) as paid_clicks,
                    COALESCE(SUM(payout_amount), 0) as total_payout,
                    COUNT(CASE WHEN clicked_at > DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 END) as clicks_24h,
                    COUNT(CASE WHEN clicked_at > DATE_SUB(NOW(), INTERVAL 1 HOUR) THEN 1 END) as clicks_1h
                FROM click_events 
                WHERE ad_id = %s
            """
            
            result = self.db.execute_query(query, (ad_id,), fetch=True)
            
            if result:
                stats = result[0]
                return {
                    'total_clicks': stats['total_clicks'],
                    'paid_clicks': stats['paid_clicks'],
                    'total_payout': float(stats['total_payout']),
                    'clicks_24h': stats['clicks_24h'],
                    'clicks_1h': stats['clicks_1h'],
                    'conversion_rate': (stats['paid_clicks'] / max(stats['total_clicks'], 1)) * 100
                }
            
        except Exception as e:
            logger.error(f"Error getting ad stats for {ad_id}: {e}")
        
        return {}
    
    def get_trending_ads(self, limit=10):
        """Get trending advertisements based on recent activity"""
        try:
            if not self.db.connect():
                return []
            
            query = """
                SELECT 
                    a.ad_id, a.title, a.category, a.payout_rate,
                    COUNT(ce.id) as recent_clicks,
                    COALESCE(SUM(ce.payout_amount), 0) as recent_earnings
                FROM advertisements a
                LEFT JOIN click_events ce ON a.ad_id = ce.ad_id 
                    AND ce.clicked_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                WHERE a.status = 'active' 
                    AND (a.expires_at IS NULL OR a.expires_at > NOW())
                GROUP BY a.ad_id
                HAVING recent_clicks > 0
                ORDER BY recent_clicks DESC, recent_earnings DESC
                LIMIT %s
            """
            
            return self.db.execute_query(query, (limit,), fetch=True) or []
            
        except Exception as e:
            logger.error(f"Error getting trending ads: {e}")
            return []

'''
        
        # Inject before main window class
        injection_point = content.find("class UnifiedPythonCoinWallet")
        if injection_point != -1:
            content = content[:injection_point] + real_time_updates_code + content[injection_point:]
            print("✅ Real-time ad updates system injected successfully")
        else:
            print("⚠️ Could not find injection point for real-time updates")
        
        return content
    
    def patch_server_class_for_database(self, content):
        """Patch the existing server class to integrate with database"""
        print("🔧 Patching server class for database integration...")
        
        # Find EnhancedDeveloperPortalServer class and add database integration
        server_patch = '''
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
        self.active_clients = {}
        self.js_file_hashes = {}
        
        # INJECTED: Database and enhanced components
        self.database_manager = DatabaseManager()
        self.ad_file_manager = AdFileManager()
        self.payment_processor = PaymentProcessor(self.database_manager, self.blockchain, self.wallet)
        self.portal_integration = DeveloperPortalIntegration(
            self.database_manager, self.payment_processor, self.ad_file_manager
        )
        self.blockchain_processor = BlockchainPaymentProcessor(
            self.wallet, self.blockchain, self.database_manager
        )
        self.real_time_updates = RealTimeAdUpdates(
            self.database_manager, self.ad_file_manager
        )
        
        # Create directories
        self.js_dir = os.path.join(os.getcwd(), 'js')
        self.client_ads_dir = os.path.join(os.getcwd(), 'client_ads')
        self.notifications_dir = os.path.join(os.getcwd(), 'notifications')
        self.js_portal_dir = os.path.join(os.getcwd(), 'js_portal')
        
        for directory in [self.js_dir, self.client_ads_dir, self.notifications_dir, self.js_portal_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Start payment processing
        self.payment_processor.start_processing()
        
        print("Enhanced server initialized with database integration")'''
        
        # Replace the __init__ method in EnhancedDeveloperPortalServer
        init_pattern = r"(class EnhancedDeveloperPortalServer.*?def __init__\(self, wallet, blockchain, port=8082\):.*?)(\n    def )"
        match = re.search(init_pattern, content, re.DOTALL)
        
        if match:
            # Find the end of the __init__ method
            init_content = match.group(1)
            next_method = match.group(2)
            
            # Replace the __init__ content
            new_init = init_content.split('def __init__(self, wallet, blockchain, port=8082):')[0] + 'def __init__(self, wallet, blockchain, port=8082):' + server_patch
            content = content.replace(match.group(0), new_init + next_method)
            print("✅ Server class patched successfully")
        else:
            print("⚠️ Could not find server class __init__ method for patching")
        
        # Add new HTTP endpoints
        new_endpoints = '''
                        elif path == '/record_click':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_record_click_with_database(data)
                            self.wfile.write(response.encode())
                            
                        elif path == '/available_ads':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_get_available_ads_from_database()
                            self.wfile.write(response.encode())
                            
                        elif path == '/update_ad_content':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_update_ad_content(data)
                            self.wfile.write(response.encode())
                            
                        elif path == '/payment_status':
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            response = self.server_instance.handle_payment_status(data)
                            self.wfile.write(response.encode())
                            
                        elif path.startswith('/js_portal/'):
                            js_filename = path.split('/')[-1]
                            self.send_header('Content-Type', 'application/javascript')
                            self.send_header('Cache-Control', 'no-cache')
                            self.end_headers()
                            js_content = self.server_instance.serve_portal_js_file(js_filename)
                            self.wfile.write(js_content.encode())
                            
                        elif path.startswith('/ad_files/'):
                            self.send_header('Content-Type', 'application/octet-stream')
                            self.end_headers()
                            file_content = self.server_instance.serve_ad_file(path)
                            if file_content:
                                self.wfile.write(file_content)'''
        
        # Find where to inject the new endpoints
        endpoints_pattern = r"(elif path == '/stats':.*?self\.wfile\.write\(response\.encode\(\)\))"
        match = re.search(endpoints_pattern, content, re.DOTALL)
        
        if match:
            content = content.replace(match.group(1), match.group(1) + new_endpoints)
            print("✅ New HTTP endpoints added successfully")
        else:
            print("⚠️ Could not find endpoints section for new routes")
        
        # Add the new handler methods
        new_methods = '''
    
    def handle_record_click_with_database(self, data):
        """Handle click recording with database integration"""
        try:
            ad_id = data.get('ad_id', '')
            developer_username = data.get('developer_username', '')
            developer_address = data.get('developer_address', '')
            payout_amount = float(data.get('payout_amount', 0))
            
            if not all([ad_id, developer_username, developer_address]):
                return json.dumps({'success': False, 'error': 'Missing required fields'})
            
            # Queue payment through processor
            event_id = self.payment_processor.queue_payment(
                ad_id, developer_username, developer_address,
                'client_advertiser', payout_amount
            )
            
            if event_id:
                return json.dumps({
                    'success': True,
                    'event_id': event_id,
                    'message': 'Click recorded and payment queued'
                })
            else:
                return json.dumps({'success': False, 'error': 'Failed to record click'})
                
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_get_available_ads_from_database(self):
        """Get available ads from database"""
        try:
            if not self.database_manager.connect():
                return json.dumps({'success': False, 'error': 'Database connection failed'})
            
            ads = self.database_manager.get_active_advertisements()
            
            formatted_ads = []
            for ad in ads:
                formatted_ad = {
                    'id': ad['ad_id'],
                    'title': ad['title'],
                    'description': ad['description'],
                    'category': ad['category'],
                    'image_url': ad['image_url'],
                    'click_url': ad['click_url'],
                    'payout': float(ad['payout_rate']),
                    'advertiser': ad['advertiser_address'][:8] + '...' if ad['advertiser_address'] else 'Unknown'
                }
                formatted_ads.append(formatted_ad)
            
            return json.dumps({
                'success': True,
                'ads': formatted_ads,
                'total': len(formatted_ads)
            })
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_update_ad_content(self, data):
        """Handle ad content updates"""
        try:
            return json.dumps(self.real_time_updates.update_ad_content(
                data.get('ad_id'),
                data.get('updates', {})
            ))
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def handle_payment_status(self, data):
        """Handle payment status requests"""
        try:
            event_id = data.get('event_id')
            status = self.payment_processor.get_payment_status(event_id)
            return json.dumps({'success': True, 'status': status})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    def serve_portal_js_file(self, filename):
        """Serve portal JavaScript files"""
        try:
            js_path = os.path.join(self.js_portal_dir, filename)
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error serving JS file {filename}: {e}")
        
        return f"// Error: Could not load {filename}"
    
    def serve_ad_file(self, file_path):
        """Serve advertisement files"""
        try:
            local_path = self.ad_file_manager.get_file_path(file_path)
            if local_path and os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error serving ad file {file_path}: {e}")
        
        return None'''
        
        # Find the end of the server class and add new methods
        class_end_pattern = r"(    def stop\(self\):.*?\"Enhanced portal server stopped\".*?\n)"
        match = re.search(class_end_pattern, content, re.DOTALL)
        
        if match:
            content = content.replace(match.group(1), new_methods + "\n\n    " + match.group(1))
            print("✅ New handler methods added to server class")
        else:
            print("⚠️ Could not find server class end for method injection")
        
        return content

def main():
    """Main function to run the enhanced injector"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced PythonCoin Injector with MySQL Integration')
    parser.add_argument('--source', '-s', default='pyqt.py', help='Source file to enhance (default: pyqt.py)')
    parser.add_argument('--apply', '-a', action='store_true', help='Apply enhancements directly to source file')
    parser.add_argument('--backup-only', '-b', action='store_true', help='Only create backup, do not enhance')
    
    args = parser.parse_args()
    
    # Check if source file exists
    if not os.path.exists(args.source):
        print(f"❌ Error: Source file '{args.source}' not found!")
        return 1
    
    try:
        injector = EnhancedPythonCoinInjector(args.source)
        
        if args.backup_only:
            injector.create_backup()
            print(f"✅ Backup created: {injector.backup_file}")
            return 0
        
        # Perform injection
        injector.inject_enhancements()
        
        if args.apply:
            # Apply enhancements directly
            shutil.move(injector.enhanced_file, args.source)
            print(f"✅ Enhancements applied directly to {args.source}")
            print(f"📋 Original backed up as: {injector.backup_file}")
        else:
            print(f"📁 Enhanced version available as: {injector.enhanced_file}")
            print(f"🔄 To apply: python {__file__} --apply")
        
        print("\n🚀 Enhanced Injection Summary:")
        print("   ✅ MySQL database integration")
        print("   ✅ Payment verification and processing")
        print("   ✅ Ad file hosting system")
        print("   ✅ Developer portal integration (secupgrade.com)")
        print("   ✅ Blockchain payment processor")
        print("   ✅ Real-time ad updates")
        print("   ✅ Enhanced server class with database support")
        
        print("\n🗄️ Database Setup Required:")
        print("   • Create MySQL database: pythoncoin_network")
        print("   • Create user: pythoncoin_user")
        print("   • Install: pip install mysql-connector-python")
        print("   • Tables will be created automatically")
        
        print("\n🌐 Integration Features:")
        print("   • Automatic blockchain transactions for ad clicks")
        print("   • Real-time ad content updates")
        print("   • Payment verification in MySQL database")
        print("   • File hosting for ad images/videos")
        print("   • Portal JavaScript generation for secupgrade.com")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during injection: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())