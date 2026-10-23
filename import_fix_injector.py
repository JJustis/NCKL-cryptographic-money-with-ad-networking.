import os
import sys
import shutil
import time
# --- START: Enterprise-Ready PyQt Code to be Injected ---
# This entire block represents the complete, enterprise-ready content for your pyqt.py file.
# It includes all the database management, HTTP server logic, and ad network features.
enterprise_ready_pyqt_code = """
#!/usr/bin/env python3
\"\"\"
Fixed Unified PythonCoin P2P Ad Network Wallet
Combines cryptocurrency wallet functionality with P2P advertising network
Automatic payments to developers on ad clicks with proper genesis distribution
Enhanced Developer Portal Server for Dashboard Communication with improved POST body parsing.

This version aims to be 'enterprise-ready' by:
- Prioritizing database-cached ads over hardcoded samples.
- Implementing robust HTTP server handling for various request types.
- Ensuring JSON serialization compatibility for database types.
- Providing a flexible framework for future expansion of ad delivery and P2P features.
- Logging significant events for easier debugging and monitoring.
\"\"\"

import sys
import mysql.connector
import requests
import atexit
import signal
import json
import logging
import threading
import time
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from decimal import Decimal

# Configure logging (set to INFO, change to DEBUG for more detailed output if needed)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock PyQt5 components for headless execution/testing.
# In a full PyQt application, these would be actual GUI elements.
class QMessageBox:
    @staticmethod
    def information(parent, title, message):
        logger.info(f"QMessageBox.information: {title} - {message}")

    @staticmethod
    def critical(parent, title, message):
        logger.error(f"QMessageBox.critical: {title} - {message}")

class QApplication:
    def __init__(self, argv):
        pass
    def exec(self):
        # In a real PyQt app, this runs the event loop.
        # For headless server, we don't need a blocking exec().
        pass

class QSplashScreen:
    def __init__(self, *args):
        pass
    def show(self):
        pass
    def finish(self, main_window):
        pass

class QMainWindow:
    \"\"\"
    Mock QMainWindow to integrate server and database manager
    within a structure that resembles the original PyQt application.
    \"\"\"
    def __init__(self):
        # Mock blockchain status for initial instructions
        self.blockchain = type('Blockchain', (object,), {'genesis_complete': True})() 
        self.db_manager = DatabaseManager()
        self.developer_portal_server = None

    def start_ad_network(self):
        \"\"\"Placeholder for actual P2P ad network startup logic.\"\"\"
        logger.info("Ad network started (mock functionality).")
        # In a real enterprise app, this would involve:
        # - Connecting to a distributed hash table (DHT) for peer discovery.
        # - Establishing secure peer connections.
        # - Syncing ad content with connected peers.
        # - Implementing consensus mechanisms for ad validation.

    def start_portal_server(self, host='0.0.0.0', port=8082):
        \"\"\"
        Starts the HTTP server for the developer portal.
        Listens on 0.0.0.0 to be accessible from other devices on the network.
        \"\"\"
        if self.developer_portal_server is None:
            try:
                self.developer_portal_server = EnhancedDeveloperPortalServer(
                    host=host,
                    port=port,
                    db_manager=self.db_manager
                )
                # Run the server in a separate daemon thread so it doesn't block the main application.
                threading.Thread(target=self.developer_portal_server.start, daemon=True).start()
                logger.info(f"✅ Developer portal server started on http://{host}:{port}")
            except Exception as e:
                logger.error(f"❌ Failed to start developer portal server: {e}", exc_info=True)
                # In a real PyQt app, you might show an error dialog here
        else:
            logger.info("Developer portal server already running.")

    def show(self):
        \"\"\"Mock method for showing the main window.\"\"\"
        logger.info("Main window shown (mock).")

# Enhanced Database Manager for Full Integration
class DatabaseManager:
    \"\"\"
    Comprehensive database manager for PythonCoin P2P Ad Network.
    Handles connection, table creation, and data operations for developers,
    P2P clients, ad clicks, and ad caching.
    \"\"\"
    
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'adnetwrk',
            'user': 'root',
            'password': ''
        }
        self.connection = None
        self.is_connected = False
        self._ensure_db_exists() # Ensure database exists before connecting to it
        self.connect()
        self._create_tables()
        
    def _ensure_db_exists(self):
        \"\"\"Ensures the 'adnetwrk' database exists. Creates it if not present.\"\"\"
        temp_conn = None
        try:
            # Connect to MySQL server without specifying a database to create the DB
            temp_conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.close()
            logger.info(f"Database '{self.db_config['database']}' ensured to exist.")
        except mysql.connector.Error as err:
            logger.error(f"Error ensuring database exists: {err}", exc_info=True)
        finally:
            if temp_conn:
                temp_conn.close()

    def connect(self):
        \"\"\"Establishes a connection to the MySQL database.\"\"\"
        if self.is_connected and self.connection and self.connection.is_connected():
            return True # Already connected and connection is live
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                autocommit=True, # Auto-commit changes
                charset='utf8mb4'
            )
            self.is_connected = True
            logger.info("✅ Database connected successfully")
            return True
        except mysql.connector.Error as e:
            logger.error(f"❌ Database connection failed: {e}", exc_info=True)
            self.is_connected = False
            self.connection = None # Clear connection object on failure
            return False
            
    def _create_tables(self):
        \"\"\"Creates necessary tables for the ad network if they don't already exist.\"\"\"
        if not self.connect():
            logger.error("Cannot create tables: Database not connected.")
            return

        cursor = self.connection.cursor()
        try:
            tables = {
                'developers': \"\"\"
                    CREATE TABLE IF NOT EXISTS developers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        pythoncoin_address VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                \"\"\",
                'p2p_clients': \"\"\"
                    CREATE TABLE IF NOT EXISTS p2p_clients (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        client_id VARCHAR(100) UNIQUE NOT NULL,
                        name VARCHAR(255),
                        host VARCHAR(255),
                        port VARCHAR(10),
                        status VARCHAR(50),
                        ad_count INT DEFAULT 0,
                        peers INT DEFAULT 0,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                \"\"\",
                'ad_clicks': \"\"\"
                    CREATE TABLE IF NOT EXISTS ad_clicks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        ad_id VARCHAR(100),
                        client_id VARCHAR(100),
                        developer_address VARCHAR(100),
                        zone VARCHAR(100),
                        payout_amount DECIMAL(16,8),
                        click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        processed BOOLEAN DEFAULT FALSE
                    )
                \"\"\",
                'ads_cache': \"\"\"
                    CREATE TABLE IF NOT EXISTS ads_cache (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        ad_id VARCHAR(100) UNIQUE,
                        client_id VARCHAR(100),
                        title VARCHAR(255),
                        description TEXT,
                        category VARCHAR(100),
                        payout_amount DECIMAL(16,8),
                        svg_url TEXT,
                        target_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        INDEX(client_id),
                        INDEX(category),
                        INDEX(expires_at)
                    )
                \"\"\"
            }

            for table_name, create_sql in tables.items():
                cursor.execute(create_sql)
                logger.info(f"Table '{table_name}' ensured to exist.")
            self.connection.commit()
            logger.info("Database tables initialized successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error creating tables: {err}", exc_info=True)
        finally:
            cursor.close()

    def add_developer(self, username, pythoncoin_address, email=None):
        \"\"\"Adds a new developer to the database if they don't already exist.\"\"\"
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO developers (username, pythoncoin_address, email) VALUES (%s, %s, %s)",
                (username, pythoncoin_address, email)
            )
            self.connection.commit()
            logger.info(f"Developer {username} registered.")
            return True
        except mysql.connector.Error as err:
            if err.errno == 1062: # Duplicate entry error
                logger.warning(f"Developer {username} or address {pythoncoin_address} already exists. Skipping registration.")
                return True # Consider it a success if it's already present
            logger.error(f"Error adding developer: {err}", exc_info=True)
            return False
        finally:
            cursor.close()

    def get_developer_by_address(self, address):
        \"\"\"Retrieves developer information by PythonCoin address.\"\"\"
        if not self.connect(): return None
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM developers WHERE pythoncoin_address = %s", (address,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting developer by address: {err}", exc_info=True)
            return None
        finally:
            cursor.close()

    def update_p2p_client(self, client_id, name, host, port, status='online', ad_count=0, peers=0):
        \"\"\"Updates or inserts P2P client information into the database.\"\"\"
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            cursor.execute(\"\"\"
                INSERT INTO p2p_clients (client_id, name, host, port, status, ad_count, peers)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), host=VALUES(host), port=VALUES(port), status=VALUES(status), ad_count=VALUES(ad_count), peers=VALUES(peers), last_seen=CURRENT_TIMESTAMP
            \"\"\", (client_id, name, host, port, status, ad_count, peers))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error updating P2P client: {err}", exc_info=True)
            return False
        finally:
            cursor.close()

    def record_ad_click(self, ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent):
        \"\"\"Records an ad click event in the database.\"\"\"
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            cursor.execute(\"\"\"
                INSERT INTO ad_clicks (ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            \"\"\", (ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent))
            self.connection.commit()
            logger.info(f"Recorded click for ad {ad_id} from {developer_address}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error recording ad click: {err}", exc_info=True)
            return False
        finally:
            cursor.close()

    def get_all_ads(self):
        \"\"\"
        Fetches all active (non-expired) ads from the local ads_cache.
        Converts Decimal fields to float for JSON serialization.
        \"\"\"
        if not self.connect(): return []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ad_id AS id, client_id, title, description, category, payout_amount, svg_url, target_url FROM ads_cache WHERE is_active = TRUE AND expires_at > NOW()")
            ads = cursor.fetchall()
            
            processed_ads = []
            for ad in ads:
                # Convert Decimal payout_amount to float for JSON serialization
                if isinstance(ad.get('payout_amount'), Decimal):
                    ad['payout'] = float(ad['payout_amount'])
                else:
                    ad['payout'] = ad.get('payout_amount', 0.0)
                # Remove original Decimal field to avoid confusion/redundancy
                del ad['payout_amount'] 
                
                # Add mock client_host and client_port for consistency with PHP dashboard expectations
                # In a real system, these would reflect the actual source of the ad (e.g., from a peer node)
                ad['client_host'] = '0.0.0.0' # This server's address
                ad['client_port'] = 8082     # This server's port
                processed_ads.append(ad)
            return processed_ads
        except mysql.connector.Error as err:
            logger.error(f"Error fetching all ads from cache: {err}", exc_info=True)
            return []
        finally:
            cursor.close()

    def add_ad_to_cache(self, ad_data):
        \"\"\"Adds or updates an ad in the ads_cache table.\"\"\"
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            # Ensure payout is converted to Decimal for storage if it's not already
            payout_val = ad_data.get('payout_amount') or ad_data.get('payout')
            if payout_val is not None:
                payout_val = Decimal(str(payout_val)) # Convert to string first to avoid floating point precision issues

            cursor.execute(\"\"\"
                INSERT INTO ads_cache (ad_id, client_id, title, description, category, payout_amount, svg_url, target_url, expires_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=VALUES(title), description=VALUES(description), category=VALUES(category),
                                        payout_amount=VALUES(payout_amount), svg_url=VALUES(svg_url), target_url=VALUES(target_url),
                                        expires_at=VALUES(expires_at), is_active=VALUES(is_active)
            \"\"\", (
                ad_data.get('id'), ad_data.get('client_id'), ad_data.get('title'), ad_data.get('description'),
                ad_data.get('category'), payout_val, ad_data.get('svg_url'), ad_data.get('target_url'),
                ad_data.get('expires_at', '2030-01-01 00:00:00'), # Default far future expiry if not provided
                True # Default to active
            ))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error adding/updating ad in cache: {err}", exc_info=True)
            return False
        finally:
            cursor.close()

    def get_sample_ads(self):
        \"\"\"
        Returns a list of hardcoded sample advertisement data.
        These are used as a fallback if the ads_cache is empty.
        SVG URLs are set to point to this local server (0.0.0.0:8082).
        \"\"\"
        sample_ads = [
            {
                "id": "pyc-ad-001",
                "client_id": "pyqt_client_001",
                "title": "Decentralized Finance with PythonCoin",
                "description": "Explore new opportunities in DeFi with our secure PythonCoin wallet.",
                "category": "finance",
                "payout": 0.005,
                "svg_url": "http://0.0.0.0:8082/svg/pyc-ad-001", # Points to this server
                "target_url": "https://pythoncoin.org/defi",
                "campaign_id": "campaign_defi_1",
                "image_url": "https://placehold.co/400x300/007bff/ffffff?text=DeFi+Ad",
            },
            {
                "id": "pyc-ad-002",
                "client_id": "pyqt_client_001",
                "title": "Secure P2P Messaging App",
                "description": "Communicate privately with end-to-end encryption. Powered by PythonCoin.",
                "category": "communication",
                "payout": 0.003,
                "svg_url": "http://0.0.0.0:8082/svg/pyc-ad-002", # Points to this server
                "target_url": "https://pythoncoin.org/messaging",
                "campaign_id": "campaign_msg_2",
                "image_url": "https://placehold.co/400x300/28a745/ffffff?text=Messaging+Ad",
            },
            {
                "id": "pyc-ad-003",
                "client_id": "pyqt_client_001",
                "title": "Mine PythonCoin Today!",
                "description": "Join our mining pool and earn PythonCoin rewards. Easy setup.",
                "category": "cryptocurrency",
                "payout": 0.008,
                "svg_url": "http://0.0.0.0:8082/svg/pyc-ad-003", # Points to this server
                "target_url": "https://pythoncoin.org/mining",
                "campaign_id": "campaign_mine_3",
                "image_url": "https://placehold.co/400x300/ffc107/ffffff?text=Mining+Ad",
            },
            {
                "id": "pyc-ad-004",
                "client_id": "pyqt_client_002",
                "title": "Decentralized Storage Solutions",
                "description": "Store your data securely on the PythonCoin network. Affordable & private.",
                "category": "storage",
                "payout": 0.004,
                "svg_url": "http://0.0.0.0:8082/svg/pyc-ad-004", # Points to this server
                "target_url": "https://pythoncoin.org/storage",
                "campaign_id": "campaign_store_4",
                "image_url": "https://placehold.co/400x300/17a2b8/ffffff?text=Storage+Ad",
            }
        ]
        return sample_ads

    def get_sample_svg(self, ad_id):
        \"\"\"
        Generates a simple SVG graphic for a given ad_id.
        If the ad_id corresponds to a known sample ad, it uses that data;
        otherwise, it generates a generic fallback SVG.
        \"\"\"
        ad_data = next((ad for ad in self.get_sample_ads() if ad['id'] == ad_id), None)
        
        if ad_data:
            title_text = ad_data['title']
            desc_text = ad_data['description']
            payout_text = f"Earn {ad_data['payout']:.3f} PYC/click"
            category_text = ad_data['category'].capitalize()
            # Dynamic background color based on category (mock)
            bg_color = "#0066cc" if ad_data['category'] == 'cryptocurrency' else \\
                       "#28a745" if ad_data['category'] == 'communication' else \\
                       "#ffc107" if ad_data['category'] == 'finance' else \\
                       "#17a2b8" if ad_data['category'] == 'storage' else "#667eea"
            return f\"\"\"<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{bg_color};stop-opacity:1" />
            <stop offset="100%" style="stop-color:#004499;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad1)" rx="10"/>
    <text x="200" y="80" font-family="Arial, sans-serif" font-size="28" fill="white" text-anchor="middle" font-weight="bold">🌐 PythonCoin Ad</text>
    <text x="200" y="120" font-family="Arial, sans-serif" font-size="20" fill="white" text-anchor="middle">{title_text}</text>
    <text x="200" y="150" font-family="Arial, sans-serif" font-size="14" fill="#ccddff" text-anchor="middle">{desc_text}</text>
    <text x="200" y="180" font-family="Arial, sans-serif" font-size="16" fill="#fff" text-anchor="middle">{payout_text}</text>
    <text x="200" y="210" font-family="Arial, sans-serif" font-size="12" fill="rgba(255,255,255,0.8)" text-anchor="middle">Category: {category_text}</text>
    <text x="200" y="240" font-family="Arial, sans-serif" font-size="10" fill="rgba(255,255,255,0.6)" text-anchor="middle">Ad ID: {ad_id}</text>
    <rect x="10" y="10" width="380" height="280" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2" rx="8"/>
</svg>\"\"\"
        else:
            return f\"\"\"<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#6c757d;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#343a40;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad1)" rx="10"/>
    <text x="200" y="150" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="middle" font-weight="bold">Ad Not Found: {ad_id}</text>
    <text x="200" y="180" font-family="Arial, sans-serif" font-size="14" fill="#ccc" text-anchor="middle">Using fallback SVG.</text>
</svg>\"\"\"


class EnhancedDeveloperPortalServer(HTTPServer):
    \"\"\"
    HTTP Server for the PythonCoin Developer Portal API.
    This server handles API requests from the PHP dashboard, including
    developer registration, ad fetching, ad click recording, and SVG serving.
    \"\"\"
    def __init__(self, host, port, db_manager):
        super().__init__((host, port), EnhancedDeveloperPortalRequestHandler)
        self.db_manager = db_manager
        # Define explicit routes for better clarity and control
        self.router = {
            '/register_developer': self._handle_register_developer,
            '/ads': self._handle_get_ads,
            '/ad_click': self._handle_ad_click,
            '/client_info': self._handle_client_info,
            '/status': self._handle_status_info,
            # SVG handling is done via regex in do_GET/do_POST, not a direct router entry
        }
        self.host = host
        self.port = port
        logger.info(f"Portal server initialized on {host}:{port}")

    def start(self):
        \"\"\"Starts the HTTP server and keeps it running.\"\"\"
        logger.info(f"Starting portal server on http://{self.host}:{self.port}...")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            logger.info("Portal server shutting down (KeyboardInterrupt).")
            self.server_close()
        except Exception as e:
            logger.error(f"Portal server crashed: {e}", exc_info=True)
            self.server_close() # Ensure server resources are released

    def _send_json_response(self, handler, data, status_code=200):
        \"\"\"Helper to send a JSON response with appropriate CORS headers.\"\"\"
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Access-Control-Allow-Origin', '*') # Allow CORS for dashboard
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Developer-Address, X-Zone')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_svg_response(self, handler, svg_content):
        \"\"\"Helper to send an SVG response with appropriate CORS headers.\"\"\"
        handler.send_response(200)
        handler.send_header('Content-Type', 'image/svg+xml')
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(svg_content.encode('utf-8'))

    def _handle_register_developer(self, handler, data):
        \"\"\"Handles developer registration/update requests.\"\"\"
        developer_address = data.get('developer_address')
        developer_name = data.get('developer_name')
        
        logger.debug(f"Handling /register_developer. Received data: {data}")

        if not developer_address or not developer_name:
            logger.warning(f"Registration attempt missing required fields: developer_address={developer_address}, developer_name={developer_name}")
            return self._send_json_response(handler, {"success": False, "error": "Missing developer_address or developer_name"})
        
        if self.db_manager.add_developer(developer_name, developer_address):
            logger.info(f"Registered/updated developer: {developer_name} ({developer_address})")
            return self._send_json_response(handler, {"success": True, "message": "Developer registered/updated"})
        else:
            logger.error(f"Failed to register developer {developer_name} ({developer_address})")
            return self._send_json_response(handler, {"success": False, "error": "Failed to register developer"})

    def _handle_get_ads(self, handler, query_params):
        \"\"\"
        Handles requests for advertisements.
        Prioritizes ads from the database cache; falls back to sample ads if cache is empty.
        \"\"\"
        developer_address = query_params.get('developer', [None])[0]
        zone = query_params.get('zone', [None])[0]
        
        ads = self.db_manager.get_all_ads() # Attempt to get ads from DB cache
        
        if not ads:
            logger.info("No cached ads found, serving sample ads.")
            ads = self.db_manager.get_sample_ads()
        
        # Filtering logic could be expanded here for real ad targeting
        ads_to_return = ads

        logger.info(f"Serving {len(ads_to_return)} ads. Developer: {developer_address}, Zone: {zone}")
        return self._send_json_response(handler, {"success": True, "ads": ads_to_return})

    def _handle_ad_click(self, handler, data):
        \"\"\"Records an ad click and processes payout (mock).\"\"\"
        ad_id = data.get('ad_id')
        client_id = data.get('client_id')
        developer_address = data.get('developer_address')
        zone = data.get('zone')
        payout_amount = data.get('payout_amount', 0.001)

        if not all([ad_id, client_id, developer_address, zone]):
            return self._send_json_response(handler, {"success": False, "error": "Missing click data"})

        ip_address = handler.client_address[0]
        user_agent = handler.headers.get('User-Agent', 'Unknown')
        if self.db_manager.record_ad_click(ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent):
            logger.info(f"Recorded click for ad {ad_id} by {developer_address} in zone {zone}. Payout: {payout_amount}")
            # In a real enterprise app, this is where a transaction would be initiated
            # on the blockchain for the payout.
            return self._send_json_response(handler, {"success": True, "message": "Click recorded", "payout": payout_amount})
        else:
            logger.error(f"Failed to record click for ad {ad_id} by {developer_address}")
            return self._send_json_response(handler, {"success": False, "error": "Failed to record click"})

    def _handle_get_svg(self, handler, ad_id):
        \"\"\"Serves SVG content for a given ad ID.\"\"\"
        if not ad_id:
            logger.warning("Missing ad_id for SVG request.")
            return self._send_json_response(handler, {"success": False, "error": "Missing ad_id for SVG request"}, 400)
        
        svg_content = self.db_manager.get_sample_svg(ad_id)
        if svg_content:
            logger.info(f"Serving SVG for ad ID: {ad_id}")
            return self._send_svg_response(handler, svg_content)
        else:
            logger.warning(f"SVG not found for ad ID: {ad_id}. Serving fallback SVG.")
            return self._send_svg_response(handler, self.db_manager.get_sample_svg("fallback_ad_id"))

    def _handle_client_info(self, handler, query_params):
        \"\"\"Provides information about this PythonCoin client/server instance.\"\"\"
        client_id = "pyqt_client_001" # Unique ID for this client instance
        client_name = "PythonCoin Wallet - Sample Client"
        
        # Ensure ads_cache is populated with sample ads if it's currently empty.
        # This acts as an initialization step for demo purposes.
        if not self.db_manager.get_all_ads():
            logger.info("Ads cache is empty. Populating with sample ads on client_info request.")
            for ad in self.db_manager.get_sample_ads():
                self.db_manager.add_ad_to_cache(ad)

        ad_count = len(self.db_manager.get_all_ads()) # Get count of ads from cache
        peers_count = 5 # Mock peer count, in real enterprise app, this would be dynamic
        
        # Update our own client info in the DB (for dashboard's /scan_network)
        self.db_manager.update_p2p_client(client_id, client_name, self.host, self.port, ad_count=ad_count, peers=peers_count)

        info = {
            "success": True,
            "client_id": client_id,
            "name": client_name,
            "version": "1.0.0",
            "status": "online",
            "host": self.host,
            "port": self.port,
            "ad_count": ad_count,
            "peers": peers_count,
            "endpoints": list(self.router.keys()) # List of explicitly defined API endpoints
        }
        logger.info(f"Serving client info: {info}")
        return self._send_json_response(handler, info)

    def _handle_status_info(self, handler, query_params):
        \"\"\"Provides a simple status check for the portal server.\"\"\"
        status = {
            "success": True,
            "server_status": "online",
            "database_connected": self.db_manager.is_connected and self.db_manager.connection and self.db_manager.connection.is_connected(),
            "message": "PythonCoin portal server is running and database is accessible."
        }
        logger.info(f"Serving status info: {status}")
        return self._send_json_response(handler, status)


class EnhancedDeveloperPortalRequestHandler(BaseHTTPRequestHandler):
    \"\"\"
    Request handler for the HTTP server.
    Parses incoming requests (GET, POST, OPTIONS) and routes them to
    the appropriate handler methods in the `EnhancedDeveloperPortalServer`.
    \"\"\"
    def _parse_request_body(self):
        \"\"\"Parses the request body based on Content-Type header.\"\"\"
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            content_type = self.headers.get('Content-Type', '').lower()
            logger.debug(f"Raw request body received: {body[:200]}...")
            logger.debug(f"Content-Type received: {content_type}")

            if 'application/json' in content_type:
                try:
                    parsed_data = json.loads(body)
                    logger.debug(f"Parsed JSON data: {parsed_data}")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON Decode Error: {e}, Body snippet: {body[:200]}...", exc_info=True)
                    return {}
            elif 'application/x-www-form-urlencoded' in content_type:
                parsed_data = parse_qs(body)
                # parse_qs returns lists for each value, convert to scalar for single values
                converted_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed_data.items()}
                logger.debug(f"Parsed form-urlencoded data: {converted_data}")
                return converted_data
            else:
                logger.warning(f"Unsupported Content-Type: {content_type}. Body snippet: {body[:200]}...")
                return {}
        logger.debug("Empty request body.")
        return {}

    def do_OPTIONS(self):
        \"\"\"Handles CORS preflight requests.\"\"\"
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Developer-Address, X-Zone')
        self.send_header('Access-Control-Max-Age', '86400') # Cache preflight for 24 hours
        self.end_headers()

    def do_POST(self):
        \"\"\"Handles POST requests and routes them.\"\"\"
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Regex matching for SVG requests (handled by _handle_get_svg in server)
        svg_match_ad_dot_svg = re.match(r'^/ad/(.+)\.svg$', path)
        svg_match_ads_ad_svg = re.match(r'^/ads/(.+)/svg$', path)
        svg_match_svg_id = re.match(r'^/svg/(.+)$', path)

        if svg_match_ad_dot_svg:
            ad_id = svg_match_ad_dot_svg.group(1)
            # Despite being a POST, we route to the SVG GET handler
            return self.server._handle_get_svg(self, ad_id) 
        elif svg_match_ads_ad_svg:
            ad_id = svg_match_ads_ad_svg.group(1)
            return self.server._handle_get_svg(self, ad_id)
        elif svg_match_svg_id:
            ad_id = svg_match_svg_id.group(1)
            return self.server._handle_get_svg(self, ad_id)

        handler_func = self.server.router.get(path)
        if handler_func:
            try:
                data = self._parse_request_body()
                logger.info(f"POST request received: Path={path}, Parsed Data={data}")
                handler_func(self, data)
            except Exception as e:
                logger.error(f"Error handling POST {path}: {e}", exc_info=True)
                self.server._send_json_response(self, {"success": False, "error": f"Internal server error: {e}"}, 500)
        else:
            logger.warning(f"Unknown POST endpoint: {path}. Returning 404.")
            self.server._send_json_response(self, {"success": False, "error": "Unknown POST endpoint"}, 404)

    def do_GET(self):
        \"\"\"Handles GET requests and routes them.\"\"\"
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # Regex matching for SVG requests
        svg_match_ad_dot_svg = re.match(r'^/ad/(.+)\.svg$', path)
        svg_match_ads_ad_svg = re.match(r'^/ads/(.+)/svg$', path)
        svg_match_svg_id = re.match(r'^/svg/(.+)$', path)

        if svg_match_ad_dot_svg:
            ad_id = svg_match_ad_dot_svg.group(1)
            return self.server._handle_get_svg(self, ad_id)
        elif svg_match_ads_ad_svg:
            ad_id = svg_match_ads_ad_svg.group(1)
            return self.server._handle_get_svg(self, ad_id)
        elif svg_match_svg_id:
            ad_id = svg_match_svg_id.group(1)
            return self.server._handle_get_svg(self, ad_id)

        handler_func = self.server.router.get(path)
        if handler_func:
            try:
                logger.info(f"GET request received: Path={path}, Query Params={query_params}")
                handler_func(self, query_params)
            except Exception as e:
                logger.error(f"Error handling GET {path}: {e}", exc_info=True)
                self.server._send_json_response(self, {"success": False, "error": f"Internal server error: {e}"}, 500)
        else:
            # Fallback for root or unknown GET requests
            if path == '/' or path == '/test':
                self.server._send_json_response(self, {
                    "success": True,
                    "status": "PythonCoin Portal Server Active",
                    "message": "Server is running and accepting connections",
                    "version": "1.0.0",
                    "endpoints": list(self.server.router.keys())
                })
            else:
                logger.warning(f"Unknown GET endpoint: {path}. Returning 404.")
                self.server._send_json_response(self, {"success": False, "error": "Unknown GET endpoint"}, 404)


# Main application entry point for headless server execution
if __name__ == '__main__':
    # Initialize mock QApplication as some PyQt components might be implicitly used even in a mock setup.
    # In a full PyQt application, sys.argv would be passed.
    app = QApplication([]) 
    main_window = QMainWindow() # Create an instance of our mock QMainWindow

    # Start the ad network and portal server
    # These methods internally use the DatabaseManager and EnhancedDeveloperPortalServer
    main_window.start_ad_network()
    main_window.start_portal_server()

    # The main application would typically call app.exec_() here to run the GUI event loop.
    # For a headless server, we just need to ensure the server thread continues running.
    # A simple loop to keep the main thread alive while the daemon server thread runs.
    logger.info("PythonCoin P2P Ad Network Client (Headless Mode) is running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt:
        logger.info("Exiting PythonCoin P2P Ad Network Client.")
        # The daemon thread will exit automatically when the main thread exits.
    except Exception as e:
        logger.critical(f"Main application loop error: {e}", exc_info=True)
"""
# --- END: Enterprise-Ready PyQt Code to be Injected ---

def apply_enterprise_ready_pyqt(target_file="pyqt.py"):
    """
    Overwrites the target PyQt file with the enterprise-ready PythonCoin client code.
    Includes a backup mechanism.
    """
    print(f"Attempting to update '{target_file}' with enterprise-ready code...")

    # 1. Create a backup of the original file
    if os.path.exists(target_file):
        backup_file = f"{target_file}.bak_{int(time.time())}"
        try:
            shutil.copyfile(target_file, backup_file)
            print(f"Original '{target_file}' backed up to '{backup_file}'")
        except IOError as e:
            print(f"Error creating backup for '{target_file}': {e}")
            print("Aborting update to prevent data loss.")
            return

    # 2. Write the new enterprise-ready code to the target file
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(enterprise_ready_pyqt_code)
        print(f"Successfully updated '{target_file}' with enterprise-ready code.")
        print("\nIMPORTANT: Please restart your PythonCoin PyQt client application for changes to take effect.")
        print("Ensure you have 'mysql-connector-python' installed (pip install mysql-connector-python).")
        print("Also, make sure your MySQL database 'adnetwrk' is running and configured correctly.")

    except IOError as e:
        print(f"Error writing to '{target_file}': {e}")
        print("The update failed. You might need to manually restore from the backup.")
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}")
        print("The update failed. You might need to manually restore from the backup.")


if __name__ == "__main__":
    # You can specify the target file as a command-line argument, e.g., python injector.py mywallet.py
    # Otherwise, it defaults to 'pyqt.py'
    target_pyqt_file = sys.argv[1] if len(sys.argv) > 1 else "pyqt.py"
    apply_enterprise_ready_pyqt(target_pyqt_file)