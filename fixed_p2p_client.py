#!/usr/bin/env python3
"""
QA Python Injector Script for PythonCoin P2P Ad Network
Tests and fixes developer portal, P2P client registration, and payment automation
"""

import mysql.connector
import requests
import json
import time
import threading
import logging
import uuid
import hashlib
import socket
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PYC-QA-Injector")

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    database: str = "adnetwrk"
    username: str = "root"
    password: str = ""

@dataclass
class ServerConfig:
    api_url: str = "http://secupgrade.com/livepy/pythoncoin/api.php"
    commands_url: str = "http://secupgrade.com/livepy/pythoncoin/commands.php"
    js_server: str = "http://localhost:8082"

class QAInjector:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.server_config = ServerConfig()
        self.db_connection = None
        self.test_results = []
        
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            self.db_connection = mysql.connector.connect(
                host=self.db_config.host,
                database=self.db_config.database,
                user=self.db_config.username,
                password=self.db_config.password
            )
            logger.info("✅ Database connection established")
            return True
        except mysql.connector.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def setup_database_tables(self):
        """Create or update required database tables"""
        if not self.db_connection:
            return False
            
        cursor = self.db_connection.cursor()
        
        # Create tables with proper schema
        tables = {
            "ad_members": """
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
                ) ENGINE=InnoDB
            """,
            
            "p2p_clients": """
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
                    metadata JSON NULL,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_client_id (client_id),
                    INDEX idx_status (status),
                    INDEX idx_last_seen (last_seen),
                    FOREIGN KEY (username) REFERENCES ad_members(username) ON DELETE SET NULL
                ) ENGINE=InnoDB
            """,
            
            "ad_clicks": """
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
                    INDEX idx_ad_id (ad_id),
                    INDEX idx_client_id (client_id),
                    INDEX idx_payment_processed (payment_processed),
                    INDEX idx_click_time (click_time),
                    FOREIGN KEY (username) REFERENCES ad_members(username) ON DELETE CASCADE,
                    FOREIGN KEY (client_id) REFERENCES p2p_clients(client_id) ON DELETE SET NULL
                ) ENGINE=InnoDB
            """,
            
            "embeds": """
                CREATE TABLE IF NOT EXISTS embeds (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    embed_id VARCHAR(100) UNIQUE NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    zone VARCHAR(50) NOT NULL,
                    width VARCHAR(20) DEFAULT '400px',
                    height VARCHAR(20) DEFAULT '300px',
                    rotation_interval INT DEFAULT 30,
                    config JSON NULL,
                    clicks INT DEFAULT 0,
                    impressions INT DEFAULT 0,
                    status ENUM('active', 'inactive', 'paused') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_embed_id (embed_id),
                    INDEX idx_username (username),
                    INDEX idx_status (status),
                    FOREIGN KEY (username) REFERENCES ad_members(username) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """,
            
            "embed_clients": """
                CREATE TABLE IF NOT EXISTS embed_clients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    embed_id VARCHAR(100) NOT NULL,
                    client_id VARCHAR(100) NOT NULL,
                    priority INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_embed_id (embed_id),
                    INDEX idx_client_id (client_id),
                    FOREIGN KEY (embed_id) REFERENCES embeds(embed_id) ON DELETE CASCADE,
                    FOREIGN KEY (client_id) REFERENCES p2p_clients(client_id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """,
            
            "analytics": """
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
                    INDEX idx_username (username),
                    INDEX idx_event_type (event_type),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (username) REFERENCES ad_members(username) ON DELETE SET NULL
                ) ENGINE=InnoDB
            """,
            
            "payment_queue": """
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
                    INDEX idx_username (username),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (click_id) REFERENCES ad_clicks(id) ON DELETE CASCADE,
                    FOREIGN KEY (username) REFERENCES ad_members(username) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """
        }
        
        try:
            for table_name, sql in tables.items():
                cursor.execute(sql)
                logger.info(f"✅ Table {table_name} created/verified")
            
            self.db_connection.commit()
            logger.info("✅ All database tables setup completed")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
        finally:
            cursor.close()
    
    def inject_test_data(self):
        """Inject test data for QA testing"""
        cursor = self.db_connection.cursor()
        
        try:
            # Test users
            test_users = [
                ('testdev1', 'test_hash_1', 'PYC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0', 0.05000000),
                ('testdev2', 'test_hash_2', 'PYC2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1', 0.03000000),
                ('qauser', 'test_hash_3', 'PYC3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2', 0.10000000)
            ]
            
            for username, password_hash, address, balance in test_users:
                cursor.execute("""
                    INSERT IGNORE INTO ad_members (username, password_hash, pythoncoin_address, exp)
                    VALUES (%s, %s, %s, %s)
                """, (username, password_hash, address, balance))
            
            # Test P2P clients
            test_clients = [
                ('client_test_1', 'Test Python Client 1', '127.0.0.1', 8082, 'testdev1', 'PYC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0'),
                ('client_test_2', 'Test Python Client 2', '127.0.0.1', 8083, 'testdev2', 'PYC2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1'),
                ('client_qa_1', 'QA Test Client', '192.168.1.100', 8082, 'qauser', 'PYC3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2')
            ]
            
            for client_id, name, host, port, username, wallet in test_clients:
                cursor.execute("""
                    INSERT IGNORE INTO p2p_clients (client_id, name, host, port, username, wallet_address, status, ad_count)
                    VALUES (%s, %s, %s, %s, %s, %s, 'online', 5)
                """, (client_id, name, host, port, username, wallet))
            
            # Test clicks for payment processing
            test_clicks = [
                ('testdev1', 'ad_test_1', 'embed_1', 'client_test_1', 'main', 0.00200000),
                ('testdev1', 'ad_test_2', 'embed_1', 'client_test_2', 'sidebar', 0.00150000),
                ('testdev2', 'ad_test_3', 'embed_2', 'client_test_1', 'header', 0.00300000),
                ('qauser', 'ad_qa_1', 'embed_qa', 'client_qa_1', 'main', 0.00250000)
            ]
            
            for username, ad_id, embed_id, client_id, zone, amount in test_clicks:
                cursor.execute("""
                    INSERT INTO ad_clicks (username, ad_id, embed_id, client_id, zone, pyc_earned, payment_processed)
                    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                """, (username, ad_id, embed_id, client_id, zone, amount))
            
            self.db_connection.commit()
            logger.info("✅ Test data injected successfully")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Test data injection failed: {e}")
            return False
        finally:
            cursor.close()
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        tests = [
            {
                'name': 'Test Connection',
                'url': f"{self.server_config.api_url}?action=test_connection",
                'method': 'GET'
            },
            {
                'name': 'Get Advertisers',
                'url': f"{self.server_config.api_url}?action=get_advertisers",
                'method': 'GET'
            },
            {
                'name': 'Register Client',
                'url': self.server_config.commands_url,
                'method': 'POST',
                'data': {
                    'action': 'register_client',
                    'client_id': 'qa_test_client',
                    'name': 'QA Test Client',
                    'username': 'qauser',
                    'host': '127.0.0.1',
                    'port': 8082
                }
            },
            {
                'name': 'Record Click',
                'url': self.server_config.api_url,
                'method': 'POST',
                'data': {
                    'action': 'record_click',
                    'username': 'qauser',
                    'ad_id': 'qa_test_ad',
                    'embed_id': 'qa_embed',
                    'client_id': 'qa_test_client'
                }
            }
        ]
        
        results = []
        for test in tests:
            try:
                if test['method'] == 'GET':
                    response = requests.get(test['url'], timeout=10)
                else:
                    response = requests.post(
                        test['url'], 
                        json=test.get('data', {}),
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        logger.info(f"✅ {test['name']}: PASSED")
                        results.append({'test': test['name'], 'status': 'PASSED', 'response': data})
                    else:
                        logger.warning(f"⚠️ {test['name']}: API returned error - {data.get('message', 'Unknown error')}")
                        results.append({'test': test['name'], 'status': 'API_ERROR', 'error': data.get('message')})
                else:
                    logger.error(f"❌ {test['name']}: HTTP {response.status_code}")
                    results.append({'test': test['name'], 'status': 'HTTP_ERROR', 'code': response.status_code})
                    
            except Exception as e:
                logger.error(f"❌ {test['name']}: Exception - {str(e)}")
                results.append({'test': test['name'], 'status': 'EXCEPTION', 'error': str(e)})
                
            time.sleep(1)  # Rate limiting
        
        return results
    
    def test_payment_processing(self):
        """Test the payment processing system"""
        cursor = self.db_connection.cursor()
        
        try:
            # Get unprocessed clicks
            cursor.execute("""
                SELECT c.id, c.username, c.pyc_earned, m.pythoncoin_address, c.client_id
                FROM ad_clicks c
                JOIN ad_members m ON c.username = m.username
                WHERE c.payment_processed = FALSE
                LIMIT 5
            """)
            
            unprocessed_clicks = cursor.fetchall()
            
            if not unprocessed_clicks:
                logger.info("No unprocessed clicks found for payment testing")
                return True
            
            for click_id, username, amount, address, client_id in unprocessed_clicks:
                # Add to payment queue
                cursor.execute("""
                    INSERT INTO payment_queue (click_id, username, pythoncoin_address, amount, client_id, status)
                    VALUES (%s, %s, %s, %s, %s, 'pending')
                """, (click_id, username, address, amount, client_id))
                
                logger.info(f"✅ Added payment to queue: {amount} PYC to {username} ({address[:8]}...)")
            
            self.db_connection.commit()
            logger.info("✅ Payment processing test completed")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Payment processing test failed: {e}")
            return False
        finally:
            cursor.close()
    
    def fix_portal_issues(self):
        """Fix common portal issues"""
        fixes_applied = []
        
        # Fix 1: Ensure auth.php exists
        auth_php_content = '''<?php
// Authentication handler for P2P Ad Network
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
    $addr = $input['pythoncoin_address'] ?? '';
    
    $stmt = $pdo->prepare("SELECT * FROM ad_members WHERE username = ?");
    $stmt->execute([$user]);
    $member = $stmt->fetch();
    
    if ($member && password_verify($pass, $member['password_hash'])) {
        echo json_encode(['success' => true, 'user' => $member]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
    }
} elseif ($action === 'register') {
    $user = $input['username'] ?? '';
    $pass = $input['password'] ?? '';
    $addr = $input['pythoncoin_address'] ?? '';
    
    $hash = password_hash($pass, PASSWORD_DEFAULT);
    
    try {
        $stmt = $pdo->prepare("INSERT INTO ad_members (username, password_hash, pythoncoin_address) VALUES (?, ?, ?)");
        $stmt->execute([$user, $hash, $addr]);
        echo json_encode(['success' => true, 'message' => 'Registration successful']);
    } catch(PDOException $e) {
        echo json_encode(['success' => false, 'message' => 'Registration failed']);
    }
}
?>'''
        
        try:
            with open('auth.php', 'w') as f:
                f.write(auth_php_content)
            fixes_applied.append("Created auth.php")
            logger.info("✅ Created auth.php file")
        except Exception as e:
            logger.error(f"❌ Failed to create auth.php: {e}")
        
        return fixes_applied
    
    def create_p2p_client_registration(self):
        """Create enhanced P2P client with auto-registration"""
        client_code = '''#!/usr/bin/env python3
"""
Enhanced P2P Client with MySQL Auto-Registration and Payment Processing
"""

import mysql.connector
import requests
import json
import time
import threading
import uuid
from datetime import datetime

class EnhancedP2PClient:
    def __init__(self, username, wallet_address, client_name="Python P2P Client"):
        self.username = username
        self.wallet_address = wallet_address
        self.client_name = client_name
        self.client_id = f"pyc_client_{uuid.uuid4().hex[:8]}"
        self.host = "127.0.0.1"
        self.port = 8082
        self.running = False
        
        # Database config
        self.db_config = {
            'host': 'localhost',
            'database': 'adnetwrk',
            'user': 'root',
            'password': ''
        }
        
        # Server config
        self.server_config = {
            'api_url': 'https://secupgrade.com/livepy/pythoncoin/api.php',
            'commands_url': 'https://secupgrade.com/livepy/pythoncoin/commands.php'
        }
        
        self.db_connection = None
        
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            print(f"✅ Database connected for client {self.client_id}")
            return True
        except mysql.connector.Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def register_with_server(self):
        """Register this client with the central server"""
        registration_data = {
            'action': 'register_client',
            'client_id': self.client_id,
            'name': self.client_name,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'wallet_address': self.wallet_address,
            'ad_count': 10,
            'capabilities': ['ad_serving', 'payment_processing']
        }
        
        try:
            response = requests.post(
                self.server_config['api_url'],
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Registered with central server: {self.client_id}")
                    return True
            
            print(f"❌ Server registration failed: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def register_with_database(self):
        """Register client directly in database"""
        if not self.db_connection:
            return False
            
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO p2p_clients (client_id, name, host, port, username, wallet_address, status, ad_count)
                VALUES (%s, %s, %s, %s, %s, %s, 'online', 10)
                ON DUPLICATE KEY UPDATE
                status = 'online',
                last_seen = CURRENT_TIMESTAMP,
                wallet_address = VALUES(wallet_address)
            """, (self.client_id, self.client_name, self.host, self.port, self.username, self.wallet_address))
            
            self.db_connection.commit()
            print(f"✅ Registered in database: {self.client_id}")
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database registration failed: {e}")
            return False
        finally:
            cursor.close()
    
    def check_for_payments(self):
        """Check database for pending payments to process"""
        if not self.db_connection:
            return
            
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute("""
                SELECT pq.id, pq.username, pq.pythoncoin_address, pq.amount, pq.click_id
                FROM payment_queue pq
                WHERE pq.status = 'pending' AND pq.client_id = %s
                LIMIT 5
            """, (self.client_id,))
            
            pending_payments = cursor.fetchall()
            
            for payment_id, username, address, amount, click_id in pending_payments:
                if self.process_payment(payment_id, username, address, amount, click_id):
                    print(f"💰 Payment processed: {amount} PYC to {username}")
                else:
                    print(f"❌ Payment failed: {amount} PYC to {username}")
                    
        except mysql.connector.Error as e:
            print(f"❌ Payment check failed: {e}")
        finally:
            cursor.close()
    
    def process_payment(self, payment_id, username, address, amount, click_id):
        """Process a payment (simulated for now)"""
        cursor = self.db_connection.cursor()
        
        try:
            # Simulate payment processing
            tx_id = f"tx_{uuid.uuid4().hex[:16]}"
            
            # Update payment queue
            cursor.execute("""
                UPDATE payment_queue 
                SET status = 'completed', tx_id = %s, processed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (tx_id, payment_id))
            
            # Update click record
            cursor.execute("""
                UPDATE ad_clicks 
                SET payment_processed = TRUE, payment_tx_id = %s, processed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (tx_id, click_id))
            
            # Update user balance
            cursor.execute("""
                UPDATE ad_members 
                SET exp = exp + %s
                WHERE username = %s
            """, (amount, username))
            
            self.db_connection.commit()
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Payment processing failed: {e}")
            self.db_connection.rollback()
            
            # Mark payment as failed
            cursor.execute("""
                UPDATE payment_queue 
                SET status = 'failed', error_message = %s
                WHERE id = %s
            """, (str(e), payment_id))
            self.db_connection.commit()
            return False
        finally:
            cursor.close()
    
    def send_heartbeat(self):
        """Send heartbeat to server"""
        try:
            response = requests.get(
                f"{self.server_config['commands_url']}?action=heartbeat&client_id={self.client_id}",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Start the enhanced P2P client"""
        print(f"🚀 Starting Enhanced P2P Client: {self.client_id}")
        
        if not self.connect_database():
            print("❌ Cannot start without database connection")
            return
        
        if not self.register_with_database():
            print("❌ Database registration failed")
            return
        
        if not self.register_with_server():
            print("⚠️ Server registration failed, continuing with database only")
        
        self.running = True
        
        # Start payment processing thread
        payment_thread = threading.Thread(target=self.payment_monitor, daemon=True)
        payment_thread.start()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.heartbeat_monitor, daemon=True)
        heartbeat_thread.start()
        
        print(f"✅ Enhanced P2P Client running: {self.client_id}")
        
        try:
            while self.running:
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()
    
    def payment_monitor(self):
        """Monitor for payments to process"""
        while self.running:
            try:
                self.check_for_payments()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"❌ Payment monitor error: {e}")
                time.sleep(60)
    
    def heartbeat_monitor(self):
        """Send regular heartbeats"""
        while self.running:
            try:
                self.send_heartbeat()
                time.sleep(60)  # Heartbeat every minute
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                time.sleep(120)
    
    def stop(self):
        """Stop the client"""
        self.running = False
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE p2p_clients SET status = 'offline' WHERE client_id = %s", (self.client_id,))
            self.db_connection.commit()
            self.db_connection.close()
        print(f"⏹️ Enhanced P2P Client stopped: {self.client_id}")

if __name__ == "__main__":
    client = EnhancedP2PClient(
        username="testdev1",
        wallet_address="PYC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0",
        client_name="Test Python Client"
    )
    client.start()
'''
        
        try:
            with open('enhanced_p2p_client.py', 'w') as f:
                f.write(client_code)
            logger.info("✅ Created enhanced_p2p_client.py")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create enhanced P2P client: {e}")
            return False
    
    def run_full_qa_suite(self):
        """Run complete QA test suite"""
        logger.info("🚀 Starting Full QA Test Suite for PythonCoin P2P Ad Network")
        
        # Step 1: Database setup
        if not self.connect_database():
            logger.error("❌ QA Suite aborted: Database connection failed")
            return False
        
        if not self.setup_database_tables():
            logger.error("❌ QA Suite aborted: Database setup failed")
            return False
        
        # Step 2: Inject test data
        if not self.inject_test_data():
            logger.error("❌ QA Suite aborted: Test data injection failed")
            return False
        
        # Step 3: Test API endpoints
        logger.info("🔍 Testing API endpoints...")
        api_results = self.test_api_endpoints()
        
        # Step 4: Test payment processing
        logger.info("💰 Testing payment processing...")
        if not self.test_payment_processing():
            logger.error("❌ Payment processing test failed")
        
        # Step 5: Fix portal issues
        logger.info("🔧 Applying portal fixes...")
        fixes = self.fix_portal_issues()
        
        # Step 6: Create enhanced P2P client
        logger.info("📦 Creating enhanced P2P client...")
        if not self.create_p2p_client_registration():
            logger.error("❌ Enhanced P2P client creation failed")
        
        # Summary
        logger.info("📊 QA Test Suite Summary:")
        logger.info(f"   Database Setup: ✅ PASSED")
        logger.info(f"   Test Data: ✅ PASSED")
        logger.info(f"   API Tests: {len([r for r in api_results if r['status'] == 'PASSED'])}/{len(api_results)} PASSED")
        logger.info(f"   Portal Fixes: {len(fixes)} applied")
        
        return True

if __name__ == "__main__":
    qa = QAInjector()
    qa.run_full_qa_suite()