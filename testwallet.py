#!/usr/bin/env python3
"""
Fixed Unified PythonCoin P2P Ad Network Wallet
Combines cryptocurrency wallet functionality with P2P advertising network
Automatic payments to developers on ad clicks with proper genesis distribution
Enhanced Developer Portal Server for Dashboard Communication with improved POST body parsing.
"""

import sys
import mysql.connector
import requests
import atexit
import signal
import json
import logging
import threading
import time # Added for time.sleep()
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from decimal import Decimal # Import Decimal type

# Configure logging (set to INFO, change to DEBUG for more detailed output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock PyQt5 components for headless execution/testing
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
        # For headless, we can simulate or just return.
        pass

class QSplashScreen:
    def __init__(self, *args):
        pass
    def show(self):
        pass
    def finish(self, main_window):
        pass

class QMainWindow:
    def __init__(self):
        self.blockchain = type('Blockchain', (object,), {'genesis_complete': True})() # Mock blockchain
        self.db_manager = DatabaseManager()
        self.developer_portal_server = None

    def start_ad_network(self):
        logger.info("Ad network started (mock).")

    def start_portal_server(self, host='0.0.0.0', port=8082): # Changed host to '0.0.0.0'
        if self.developer_portal_server is None:
            try:
                self.developer_portal_server = EnhancedDeveloperPortalServer(
                    host=host,
                    port=port,
                    db_manager=self.db_manager
                )
                threading.Thread(target=self.developer_portal_server.start, daemon=True).start()
                logger.info(f"✅ Developer portal server started on http://{host}:{port}")
            except Exception as e:
                logger.error(f"❌ Failed to start developer portal server: {e}")
        else:
            logger.info("Developer portal server already running.")

    def show(self):
        logger.info("Main window shown (mock).")

# Enhanced Database Manager for Full Integration
class DatabaseManager:
    """Comprehensive database manager for PythonCoin P2P Ad Network"""
    
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'adnetwrk',
            'user': 'root',
            'password': ''
        }
        self.connection = None
        self.is_connected = False
        self._ensure_db_exists()
        self.connect()
        self._create_tables()
        
    def _ensure_db_exists(self):
        """Ensures the 'adnetwrk' database exists."""
        temp_conn = None
        try:
            # Connect to MySQL server without specifying a database
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
            logger.error(f"Error ensuring database exists: {err}")
        finally:
            if temp_conn:
                temp_conn.close()

    def connect(self):
        """Connect to database"""
        if self.is_connected and self.connection.is_connected():
            return True
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                autocommit=True,
                charset='utf8mb4'
            )
            self.is_connected = True
            logger.info("✅ Database connected successfully")
            return True
        except mysql.connector.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.is_connected = False
            return False
            
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        if not self.connect():
            logger.error("Cannot create tables: Database not connected.")
            return

        cursor = self.connection.cursor()
        try:
            tables = {
                'developers': """
                    CREATE TABLE IF NOT EXISTS developers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        pythoncoin_address VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'p2p_clients': """
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
                """,
                'ad_clicks': """
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
                """,
                'ads_cache': """
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
                """
            }

            for table_name, create_sql in tables.items():
                cursor.execute(create_sql)
                logger.info(f"Table '{table_name}' ensured to exist.")
            self.connection.commit()
            logger.info("Database tables initialized successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error creating tables: {err}")
        finally:
            cursor.close()

    def add_developer(self, username, pythoncoin_address, email=None):
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
            if err.errno == 1062: # Duplicate entry
                logger.warning(f"Developer {username} or address {pythoncoin_address} already exists.")
                return True # Consider it a success if it's already there
            logger.error(f"Error adding developer: {err}")
            return False
        finally:
            cursor.close()

    def get_developer_by_address(self, address):
        if not self.connect(): return None
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM developers WHERE pythoncoin_address = %s", (address,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting developer by address: {err}")
            return None
        finally:
            cursor.close()

    def update_p2p_client(self, client_id, name, host, port, status='online', ad_count=0, peers=0):
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO p2p_clients (client_id, name, host, port, status, ad_count, peers)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), host=VALUES(host), port=VALUES(port), status=VALUES(status), ad_count=VALUES(ad_count), peers=VALUES(peers), last_seen=CURRENT_TIMESTAMP
            """, (client_id, name, host, port, status, ad_count, peers))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error updating P2P client: {err}")
            return False
        finally:
            cursor.close()

    def record_ad_click(self, ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent):
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO ad_clicks (ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent))
            self.connection.commit()
            logger.info(f"Recorded click for ad {ad_id} from {developer_address}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error recording ad click: {err}")
            return False
        finally:
            cursor.close()

    def get_all_ads(self):
        """Fetches all active ads from the local ads_cache."""
        if not self.connect(): return []
        cursor = self.connection.cursor(dictionary=True)
        try:
            # Fetch ads where is_active is true and not expired
            cursor.execute("SELECT ad_id AS id, client_id, title, description, category, payout_amount, svg_url, target_url FROM ads_cache WHERE is_active = TRUE AND expires_at > NOW()")
            ads = cursor.fetchall()
            
            # Convert Decimal payout_amount to float for JSON serialization
            for ad in ads:
                if isinstance(ad.get('payout_amount'), Decimal):
                    ad['payout'] = float(ad['payout_amount'])
                else:
                    ad['payout'] = ad.get('payout_amount', 0.0) # Ensure it's always a float
                del ad['payout_amount'] # Remove original Decimal field
                
                # Add mock client_host and client_port for consistency with PHP dashboard expectations
                # Assuming ads served are from this current server instance (0.0.0.0:8082)
                ad['client_host'] = '0.0.0.0'
                ad['client_port'] = 8082
            return ads
        except mysql.connector.Error as err:
            logger.error(f"Error fetching all ads from cache: {err}")
            return []
        finally:
            cursor.close()

    def add_ad_to_cache(self, ad_data):
        """Adds or updates an ad in the ads_cache."""
        if not self.connect(): return False
        cursor = self.connection.cursor()
        try:
            # Ensure payout is converted to Decimal for storage if it's not already
            payout_val = ad_data.get('payout_amount') or ad_data.get('payout')
            if payout_val is not None:
                payout_val = Decimal(str(payout_val)) # Convert to string first to avoid floating point issues

            cursor.execute("""
                INSERT INTO ads_cache (ad_id, client_id, title, description, category, payout_amount, svg_url, target_url, expires_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=VALUES(title), description=VALUES(description), category=VALUES(category),
                                        payout_amount=VALUES(payout_amount), svg_url=VALUES(svg_url), target_url=VALUES(target_url),
                                        expires_at=VALUES(expires_at), is_active=VALUES(is_active)
            """, (
                ad_data.get('id'), ad_data.get('client_id'), ad_data.get('title'), ad_data.get('description'),
                ad_data.get('category'), payout_val, ad_data.get('svg_url'), ad_data.get('target_url'),
                ad_data.get('expires_at', '2030-01-01 00:00:00'), # Default far future expiry
                True
            ))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"Error adding/updating ad in cache: {err}")
            return False
        finally:
            cursor.close()

    def get_sample_ads(self):
        """Returns a list of sample advertisement data, ensuring SVG URLs point to 0.0.0.0."""
        sample_ads = [
            {
                "id": "pyc-ad-001",
                "client_id": "pyqt_client_001",
                "title": "Decentralized Finance with PythonCoin",
                "description": "Explore new opportunities in DeFi with our secure PythonCoin wallet.",
                "category": "finance",
                "payout": 0.005,
                "svg_url": "http://127.0.0.1:8082/svg/pyc-ad-001",
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
                "svg_url": "http://127.0.0.1:8082/svg/pyc-ad-002",
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
                "svg_url": "http://127.0.0.1:8082/svg/pyc-ad-003",
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
                "svg_url": "http://127.0.0.1:8082/svg/pyc-ad-004",
                "target_url": "https://pythoncoin.org/storage",
                "campaign_id": "campaign_store_4",
                "image_url": "https://placehold.co/400x300/17a2b8/ffffff?text=Storage+Ad",
            }
        ]
        # Update svg_url to use 0.0.0.0
        updated_ads = []
        for ad in sample_ads:
            ad_copy = ad.copy()
            ad_copy['svg_url'] = ad_copy['svg_url'].replace('127.0.0.1', '0.0.0.0')
            updated_ads.append(ad_copy)
        return updated_ads


class EnhancedDeveloperPortalServer(HTTPServer):
    """
    HTTP Server for the PythonCoin Developer Portal API.
    Handles requests from the PHP dashboard.
    """
    def __init__(self, host, port, db_manager):
        super().__init__((host, port), EnhancedDeveloperPortalRequestHandler)
        self.db_manager = db_manager
        self.router = {
            '/register_developer': self._handle_register_developer,
            '/ads': self._handle_get_ads,
            '/ad_click': self._handle_ad_click, # New endpoint for direct click recording
            '/svg/': self._handle_get_svg, # For serving SVGs
            '/client_info': self._handle_client_info,
            '/status': self._handle_status_info,
        }
        self.host = host
        self.port = port
        logger.info(f"Portal server initialized on {host}:{port}")

    def start(self):
        logger.info(f"Starting portal server on http://{self.host}:{self.port}...")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            logger.info("Portal server shutting down.")
            self.server_close()
        except Exception as e:
            logger.error(f"Portal server crashed: {e}", exc_info=True)

    def _send_json_response(self, handler, data, status_code=200):
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Access-Control-Allow-Origin', '*') # Allow CORS for dashboard
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Developer-Address, X-Zone')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_svg_response(self, handler, svg_content):
        handler.send_response(200)
        handler.send_header('Content-Type', 'image/svg+xml')
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(svg_content.encode('utf-8'))

    def _handle_register_developer(self, handler, data):
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
        developer_address = query_params.get('developer', [None])[0]
        zone = query_params.get('zone', [None])[0]
        
        # Try to get ads from the database cache first
        ads = self.db_manager.get_all_ads()
        
        if not ads:
            logger.info("No cached ads found, serving sample ads.")
            ads = self.db_manager.get_sample_ads()
        
        # Filtering logic (can be expanded if real targeting is implemented)
        ads_to_return = ads
        if developer_address:
            # In a real system, you might filter ads targeted to this developer.
            # For this mock, if developer is specified, we just ensure we return ads.
            pass 

        logger.info(f"Serving {len(ads_to_return)} ads. Developer: {developer_address}, Zone: {zone}")
        return self._send_json_response(handler, {"success": True, "ads": ads_to_return})

    def _handle_ad_click(self, handler, data):
        ad_id = data.get('ad_id')
        client_id = data.get('client_id')
        developer_address = data.get('developer_address')
        zone = data.get('zone')
        payout_amount = data.get('payout_amount', 0.001)

        if not all([ad_id, client_id, developer_address, zone]):
            return self._send_json_response(handler, {"success": False, "error": "Missing click data"})

        # Record the click in the database
        ip_address = handler.client_address[0]
        user_agent = handler.headers.get('User-Agent', 'Unknown')
        if self.db_manager.record_ad_click(ad_id, client_id, developer_address, zone, payout_amount, ip_address, user_agent):
            logger.info(f"Recorded click for ad {ad_id} by {developer_address} in zone {zone}. Payout: {payout_amount}")
            return self._send_json_response(handler, {"success": True, "message": "Click recorded", "payout": payout_amount})
        else:
            logger.error(f"Failed to record click for ad {ad_id} by {developer_address}")
            return self._send_json_response(handler, {"success": False, "error": "Failed to record click"})

    def _handle_get_svg(self, handler, path_parts):
        # path_parts will be like ['svg', 'ad_id']
        if len(path_parts) < 2:
            return self._send_json_response(handler, {"success": False, "error": "Invalid SVG request path"}, 400)
        
        ad_id = path_parts[1]
        if ad_id.endswith('.svg'):
            ad_id = ad_id[:-4] # Remove .svg extension if present
        
        svg_content = self.db_manager.get_sample_svg(ad_id)
        if svg_content:
            logger.info(f"Serving SVG for ad ID: {ad_id}")
            return self._send_svg_response(handler, svg_content)
        else:
            logger.warning(f"SVG not found for ad ID: {ad_id}")
            # Fallback to a generic SVG
            return self._send_svg_response(handler, self.db_manager.get_sample_svg("fallback_ad_id"))

    def _handle_client_info(self, handler, query_params):
        client_id = "pyqt_client_001" # This client's ID
        client_name = "PythonCoin Wallet - Sample Client"
        
        # Before returning info, ensure ads_cache is populated if empty
        if not self.db_manager.get_all_ads():
            logger.info("Ads cache is empty. Populating with sample ads.")
            for ad in self.db_manager.get_sample_ads():
                self.db_manager.add_ad_to_cache(ad)

        ad_count = len(self.db_manager.get_all_ads()) # Get count of ads from cache now
        peers_count = 5 # Mock peer count
        
        # Update our own client info in the DB
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
            "endpoints": list(self.router.keys()) # List of exposed endpoints
        }
        logger.info(f"Serving client info: {info}")
        return self._send_json_response(handler, info)

    def _handle_status_info(self, handler, query_params):
        status = {
            "success": True,
            "server_status": "online",
            "database_connected": self.db_manager.is_connected and self.db_manager.connection.is_connected(),
            "message": "PythonCoin portal server is running and database is accessible."
        }
        logger.info(f"Serving status info: {status}")
        return self._send_json_response(handler, status)


class EnhancedDeveloperPortalRequestHandler(BaseHTTPRequestHandler):
    def _parse_request_body(self):
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
                    logger.error(f"JSON Decode Error: {e}, Body snippet: {body[:200]}...")
                    return {}
            elif 'application/x-www-form-urlencoded' in content_type:
                parsed_data = parse_qs(body)
                # Convert single-element lists to their scalar values
                converted_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed_data.items()}
                logger.debug(f"Parsed form-urlencoded data: {converted_data}")
                return converted_data
            else:
                logger.warning(f"Unsupported Content-Type: {content_type}. Body snippet: {body[:200]}...")
                return {}
        logger.debug("Empty request body.")
        return {}

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Developer-Address, X-Zone')
        self.send_header('Access-Control-Max-Age', '86400') # Cache preflight for 24 hours
        self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Special handling for /svg/ endpoint if a POST is mistakenly sent
        if path.startswith('/svg/'):
            path_parts = [p for p in path.split('/') if p]
            if '/svg/' in self.server.router: # Ensure the router has a handler for /svg/
                return self.server.router['/svg/'](self, path_parts)
            else:
                logger.warning(f"No handler for SVG POST at {path}. Returning 404.")
                self.server._send_json_response(self, {"success": False, "error": "Endpoint not found"}, 404)
                return

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
            logger.warning(f"Unknown POST endpoint: {path}")
            self.server._send_json_response(self, {"success": False, "error": "Unknown POST endpoint"}, 404)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query) # Parse query string parameters

        # Handle special case for SVG requests with /svg/id format
        if path.startswith('/svg/'):
            path_parts = [p for p in path.split('/') if p]
            if '/svg/' in self.server.router: # Ensure the router has a handler for /svg/
                return self.server.router['/svg/'](self, path_parts)
            else:
                logger.warning(f"No handler for SVG GET at {path}. Returning 404.")
                self.server._send_json_response(self, {"success": False, "error": "Endpoint not found"}, 404)
                return
        
        handler_func = self.server.router.get(path)
        if handler_func:
            try:
                logger.info(f"GET request received: Path={path}, Query Params={query_params}")
                handler_func(self, query_params)
            except Exception as e:
                logger.error(f"Error handling GET {path}: {e}", exc_info=True)
                self.server._send_json_response(self, {"success": False, "error": f"Internal server error: {e}"}, 500)
        else:
            logger.warning(f"Unknown GET endpoint: {path}")
            self.server._send_json_response(self, {"success": False, "error": "Unknown GET endpoint"}, 404)

# Main application entry point
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main_window = QMainWindow()

        # Attempt to connect to the database first
        if not main_window.db_manager.connect():
            QMessageBox.critical(None, "Database Error", "Failed to connect to the database. Please ensure MySQL is running and configured correctly.")
            sys.exit(1)

        logger.info("Starting P2P discovery...")
        
        # Auto-start P2P network for genesis coordination
        main_window.start_ad_network()
        
        # Auto-start portal server
        try:
            main_window.start_portal_server()
        except Exception as e:
            logger.error(f"Portal server auto-start failed: {e}")
            QMessageBox.critical(None, "Server Startup Error", f"Failed to start portal server: {str(e)}")
            sys.exit(1) # Exit if portal server cannot start

        splash = QSplashScreen() # Mock splash screen
        splash.show()
        
        # Simulate some delay for splash screen
        # time.sleep(2) # Uncomment if you want to see splash for longer during dev
        
        splash.finish(main_window)
        main_window.show()
        
        # Show initial instructions
        if not main_window.blockchain.genesis_complete:
            QMessageBox.information(
                main_window, 
                "Welcome to PythonCoin!", 
                "🏗️ Genesis Block Coordination\n\n"
                "Your wallet is now discovering peers for initial coin distribution.\n"
                "The genesis block will be created automatically when:\n\n"
                "• Other wallets are found on the network, OR\n"
                "• 30 seconds have passed (single-wallet mode)\n\n"
                "You can start mining once the genesis block is complete!"
            )
        
        # Keep the main thread alive for the daemon server thread
        # The HTTPServer.serve_forever() is blocking, so this will only be reached on exit.
        try:
            while True:
                time.sleep(1) # Sleep to prevent busy-waiting
        except KeyboardInterrupt:
            logger.info("Application interrupted. Shutting down.")
        except Exception as e:
            logger.error(f"Main loop error: {e}", exc_info=True)
        
    except Exception as e:
        QMessageBox.critical(None, "Startup Error", f"Failed to start application: {str(e)}")
        logger.error(f"Application startup error: {e}", exc_info=True)
        sys.exit(1)
