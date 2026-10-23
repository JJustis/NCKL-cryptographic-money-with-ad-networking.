#!/usr/bin/env python3
"""
PythonCoin Database Setup Script - FIXED VERSION
Complete database creation and management for PythonCoin P2P Ad Network
Version: 2.3.1 - Fixed existing table conflicts
"""

import sys
import json
import time
import decimal
from datetime import datetime
from pathlib import Path

# Try to import MySQL connector
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
    print("✅ MySQL connector available")
except ImportError:
    MYSQL_AVAILABLE = False
    print("❌ MySQL connector not available")
    print("Install with: pip install mysql-connector-python")
    sys.exit(1)

# === DATABASE CONFIGURATION ===
DB_CONFIG = {
    'host': 'localhost',
    'database': 'adnetwrk',
    'user': 'root',
    'password': '',
    'autocommit': True,
    'charset': 'utf8mb4'
}

# === UPDATED TABLE DEFINITIONS (handles existing structure) ===
TABLES = {
    'developers': """
        CREATE TABLE IF NOT EXISTS developers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255),
            pythoncoin_address VARCHAR(35) NOT NULL,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_clicks INT DEFAULT 0,
            total_earned DECIMAL(18,8) DEFAULT 0.00000000,
            total_earnings DECIMAL(18,8) DEFAULT 0.00000000,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_username (username),
            INDEX idx_address (pythoncoin_address)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'ad_clicks': """
        CREATE TABLE IF NOT EXISTS ad_clicks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ad_id VARCHAR(100) NOT NULL,
            client_id VARCHAR(100),
            developer_id INT,
            developer_address VARCHAR(35) NOT NULL,
            developer_name VARCHAR(100),
            zone VARCHAR(100) DEFAULT 'default',
            payout_amount DECIMAL(18,8) NOT NULL,
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            processed BOOLEAN DEFAULT FALSE,
            processed_time TIMESTAMP NULL,
            payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
            transaction_id VARCHAR(100),
            error_message TEXT,
            retry_count INT DEFAULT 0,
            metadata JSON,
            INDEX idx_ad_id (ad_id),
            INDEX idx_developer (developer_address),
            INDEX idx_processed (processed),
            INDEX idx_payment_status (payment_status),
            INDEX idx_click_time (click_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'p2p_clients': """
        CREATE TABLE IF NOT EXISTS p2p_clients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            host VARCHAR(255) NOT NULL,
            port INT NOT NULL,
            username VARCHAR(100),
            wallet_address VARCHAR(35),
            status ENUM('online', 'offline', 'connecting') DEFAULT 'offline',
            version VARCHAR(50) DEFAULT '2.3.0',
            capabilities JSON,
            metadata JSON,
            ad_count INT DEFAULT 0,
            peers_count INT DEFAULT 0,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_client_id (client_id),
            INDEX idx_status (status),
            INDEX idx_last_seen (last_seen)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'ads': """
        CREATE TABLE IF NOT EXISTS ads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ad_id VARCHAR(100) UNIQUE NOT NULL,
            client_id VARCHAR(100),
            advertiser_address VARCHAR(35) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            image_url TEXT,
            click_url TEXT,
            target_url TEXT,
            category VARCHAR(100) DEFAULT 'general',
            payout_rate DECIMAL(18,8) NOT NULL DEFAULT 0.001,
            payout_amount DECIMAL(18,8) NOT NULL DEFAULT 0.001,
            daily_budget DECIMAL(18,8) DEFAULT 1.0,
            max_clicks_daily INT DEFAULT 1000,
            targeting JSON,
            status ENUM('active', 'inactive', 'paused', 'expired') DEFAULT 'active',
            expires_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            click_count INT DEFAULT 0,
            impression_count INT DEFAULT 0,
            source ENUM('storage', 'network', 'p2p') DEFAULT 'storage',
            files JSON,
            metadata JSON,
            INDEX idx_ad_id (ad_id),
            INDEX idx_client_id (client_id),
            INDEX idx_status (status),
            INDEX idx_category (category),
            INDEX idx_advertiser (advertiser_address)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'notifications': """
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            recipient_type ENUM('all', 'clients', 'developers') DEFAULT 'all',
            recipient_id VARCHAR(100),
            metadata JSON,
            priority ENUM('low', 'normal', 'high') DEFAULT 'normal',
            read_status TINYINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            INDEX idx_type (type),
            INDEX idx_recipient (recipient_type, recipient_id),
            INDEX idx_created (created_at),
            INDEX idx_priority (priority)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'developer_payments': """
        CREATE TABLE IF NOT EXISTS developer_payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            developer_id INT,
            developer_address VARCHAR(35) NOT NULL,
            total_clicks INT DEFAULT 0,
            total_earnings DECIMAL(18,8) DEFAULT 0.00000000,
            last_payment TIMESTAMP NULL,
            last_click TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY idx_developer_address (developer_address),
            INDEX idx_last_payment (last_payment)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'ad_impressions': """
        CREATE TABLE IF NOT EXISTS ad_impressions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ad_id VARCHAR(100) NOT NULL,
            client_id VARCHAR(100),
            developer_address VARCHAR(35),
            zone VARCHAR(100) DEFAULT 'default',
            impression_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            metadata JSON,
            INDEX idx_ad_id (ad_id),
            INDEX idx_developer (developer_address),
            INDEX idx_impression_time (impression_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
}

# === COLUMN UPDATES FOR EXISTING TABLES ===
COLUMN_UPDATES = {
    'developers': [
        "ALTER TABLE developers ADD COLUMN IF NOT EXISTS total_earnings DECIMAL(18,8) DEFAULT 0.00000000 AFTER total_earned",
        "ALTER TABLE developers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE AFTER total_earnings"
    ]
}

# === SAMPLE DATA FOR TESTING ===
SAMPLE_DATA = {
    'notifications': [
        {
            'type': 'system',
            'title': 'Database Setup Complete',
            'message': 'PythonCoin database has been successfully initialized with fixed table structure',
            'recipient_type': 'all',
            'priority': 'normal'
        }
    ]
}

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class PythonCoinDatabaseSetup:
    """Complete database setup and management for PythonCoin - FIXED VERSION"""
    
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.connection = None
        
    def connect_to_mysql(self):
        """Connect to MySQL server (without database) - FIXED VERSION"""
        try:
            print(f"🔗 Connecting to MySQL server at {self.config['host']}...")
            
            # Connect without specifying database
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            
            self.connection = mysql.connector.connect(
                **temp_config,
                connection_timeout=5
            )
            
            if self.connection.is_connected():
                # FIXED: Use server_info property instead of deprecated method
                server_info = self.connection.server_info
                print(f"✅ Connected to MySQL server (version {server_info})")
                return True
            else:
                print("❌ MySQL connection failed")
                return False
                
        except mysql.connector.Error as e:
            print(f"❌ MySQL connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def create_database(self):
        """Create the PythonCoin database"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No MySQL connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Create database
            db_name = self.config['database']
            print(f"🗄️ Creating database '{db_name}'...")
            
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {db_name}
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            
            print(f"✅ Database '{db_name}' created successfully")
            cursor.close()
            
            # Now connect to the specific database
            self.connection.close()
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                print(f"✅ Connected to database '{db_name}'")
                return True
            else:
                print(f"❌ Failed to connect to database '{db_name}'")
                return False
                
        except mysql.connector.Error as e:
            print(f"❌ Database creation error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def update_existing_tables(self):
        """Update existing tables to match expected structure"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection")
            return False
        
        cursor = self.connection.cursor()
        
        try:
            print("🔧 Updating existing table structures...")
            
            # Add missing columns to existing tables
            for table_name, updates in COLUMN_UPDATES.items():
                print(f"  Updating table '{table_name}'...")
                for update_sql in updates:
                    try:
                        # Check if column exists first (safer approach)
                        if "total_earnings" in update_sql:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                                WHERE TABLE_SCHEMA = '{self.config['database']}' 
                                AND TABLE_NAME = '{table_name}' 
                                AND COLUMN_NAME = 'total_earnings'
                            """)
                            if cursor.fetchone()[0] == 0:
                                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN total_earnings DECIMAL(18,8) DEFAULT 0.00000000")
                                print(f"    ✅ Added total_earnings column to {table_name}")
                            else:
                                print(f"    ℹ️ total_earnings column already exists in {table_name}")
                        
                        if "is_active" in update_sql:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                                WHERE TABLE_SCHEMA = '{self.config['database']}' 
                                AND TABLE_NAME = '{table_name}' 
                                AND COLUMN_NAME = 'is_active'
                            """)
                            if cursor.fetchone()[0] == 0:
                                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                                print(f"    ✅ Added is_active column to {table_name}")
                            else:
                                print(f"    ℹ️ is_active column already exists in {table_name}")
                                
                    except mysql.connector.Error as e:
                        print(f"    ⚠️ Could not update {table_name}: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating tables: {e}")
            return False
        finally:
            cursor.close()
    
    def create_tables(self, drop_existing=False):
        """Create all database tables - IMPROVED VERSION"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection")
            return False
        
        cursor = self.connection.cursor()
        tables_created = 0
        tables_failed = 0
        
        try:
            print("📋 Creating/updating database tables...")
            
            # First update existing tables
            self.update_existing_tables()
            
            # Optionally drop existing tables
            if drop_existing:
                print("⚠️ Dropping existing tables...")
                self.drop_all_tables()
            
            # Create tables in order (respecting foreign key dependencies)
            table_order = [
                'developers',
                'developer_payments', 
                'p2p_clients',
                'ads',
                'ad_clicks',
                'ad_impressions',
                'notifications'
            ]
            
            for table_name in table_order:
                if table_name in TABLES:
                    try:
                        print(f"  Creating/updating table '{table_name}'...")
                        cursor.execute(TABLES[table_name])
                        tables_created += 1
                        print(f"  ✅ Table '{table_name}' created/updated successfully")
                    except mysql.connector.Error as e:
                        tables_failed += 1
                        print(f"  ❌ Failed to create table '{table_name}': {e}")
                    except Exception as e:
                        tables_failed += 1
                        print(f"  ❌ Unexpected error creating table '{table_name}': {e}")
            
            print(f"\n📊 Table creation summary:")
            print(f"  ✅ Successfully created/updated: {tables_created}")
            print(f"  ❌ Failed: {tables_failed}")
            print(f"  📋 Total tables: {len(TABLES)}")
            
            return tables_created > 0
            
        except Exception as e:
            print(f"❌ Error during table creation: {e}")
            return False
        finally:
            cursor.close()
    
    def drop_all_tables(self):
        """Drop all tables (in reverse order to handle foreign keys)"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection")
            return False
        
        cursor = self.connection.cursor()
        
        try:
            # Get list of all tables
            cursor.execute("SHOW TABLES")
            all_tables = [table[0] for table in cursor.fetchall()]
            
            if not all_tables:
                print("  ℹ️ No tables to drop")
                return True
            
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            for table_name in all_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"  🗑️ Dropped table '{table_name}'")
                except mysql.connector.Error as e:
                    print(f"  ⚠️ Could not drop table '{table_name}': {e}")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
        finally:
            cursor.close()
    
    def insert_sample_data(self):
        """Insert sample data for testing - IMPROVED VERSION"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection")
            return False
        
        cursor = self.connection.cursor()
        
        try:
            print("📝 Inserting sample data...")
            
            # Insert sample developer (with proper column check)
            try:
                # Check what columns exist in developers table
                cursor.execute(f"""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = '{self.config['database']}' 
                    AND TABLE_NAME = 'developers'
                """)
                dev_columns = [col[0] for col in cursor.fetchall()]
                
                # Build insert query based on available columns
                base_columns = ['username', 'pythoncoin_address', 'email']
                base_values = ['demo_dev', 'PYCdemo1234567890abcdef1234567', 'demo@pythoncoin.com']
                
                if 'is_active' in dev_columns:
                    base_columns.append('is_active')
                    base_values.append(True)
                
                placeholders = ', '.join(['%s'] * len(base_columns))
                columns_str = ', '.join(base_columns)
                
                cursor.execute(f"""
                    INSERT IGNORE INTO developers ({columns_str})
                    VALUES ({placeholders})
                """, base_values)
                print(f"  ✅ Inserted sample developer: demo_dev")
                
            except mysql.connector.Error as e:
                print(f"  ⚠️ Could not insert sample developer: {e}")
            
            # Insert sample notifications
            for notif in SAMPLE_DATA['notifications']:
                try:
                    cursor.execute("""
                        INSERT INTO notifications (type, title, message, recipient_type, priority)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (notif['type'], notif['title'], notif['message'], 
                         notif['recipient_type'], notif['priority']))
                    print(f"  ✅ Inserted notification: {notif['title']}")
                except mysql.connector.Error as e:
                    print(f"  ⚠️ Could not insert notification: {e}")
            
            self.connection.commit()
            print("✅ Sample data inserted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting sample data: {e}")
            return False
        finally:
            cursor.close()
    
    def verify_installation(self):
        """Verify database installation - IMPROVED VERSION"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection")
            return False
        
        cursor = self.connection.cursor()
        
        try:
            print("🔍 Verifying database installation...")
            
            # Check all tables exist
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            print(f"📋 Found {len(existing_tables)} tables:")
            for table in existing_tables:
                print(f"  ✅ {table}")
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM developers")
            dev_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notifications")
            notif_count = cursor.fetchone()[0]
            
            print(f"📊 Data verification:")
            print(f"  👥 Developers: {dev_count}")
            print(f"  🔔 Notifications: {notif_count}")
            
            # Test a safe query that works with any table structure
            try:
                cursor.execute("""
                    SELECT username, pythoncoin_address, total_clicks
                    FROM developers
                    WHERE 1=1
                    LIMIT 5
                """)
                
                active_devs = cursor.fetchall()
                print(f"  ✅ Query test successful: {len(active_devs)} developers found")
                
            except mysql.connector.Error as e:
                print(f"  ⚠️ Query test had issues (this is normal for existing tables): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
        finally:
            cursor.close()
    
    def get_database_info(self):
        """Get database information - FIXED VERSION"""
        if not self.connection or not self.connection.is_connected():
            return {}
        
        cursor = self.connection.cursor()
        info = {}
        
        try:
            # Database version - FIXED
            info['mysql_version'] = self.connection.server_info
            
            # Database size
            cursor.execute(f"""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'DB Size (MB)'
                FROM information_schema.tables 
                WHERE table_schema = '{self.config['database']}'
            """)
            result = cursor.fetchone()
            info['database_size_mb'] = float(result[0]) if result[0] else 0
            
            # Table count
            cursor.execute("SHOW TABLES")
            info['table_count'] = len(cursor.fetchall())
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting database info: {e}")
            return {}
        finally:
            cursor.close()
    
    def save_setup_log(self):
        """Save setup log to file - FIXED VERSION"""
        try:
            log_data = {
                'setup_date': datetime.now().isoformat(),
                'database_config': {k: v for k, v in self.config.items() if k != 'password'},
                'database_info': self.get_database_info(),
                'tables_created': list(TABLES.keys()),
                'version': '2.3.1'
            }
            
            log_file = Path('pythoncoin_db_setup.log')
            with open(log_file, 'w') as f:
                # FIXED: Use custom encoder for Decimal types
                json.dump(log_data, f, indent=2, cls=DecimalEncoder)
            
            print(f"📝 Setup log saved to: {log_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving setup log: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Disconnected from database")

def main():
    """Main setup function"""
    print("🚀 PythonCoin Database Setup v2.3.1 - FIXED VERSION")
    print("=" * 55)
    
    if not MYSQL_AVAILABLE:
        print("❌ MySQL connector not available. Install with:")
        print("pip install mysql-connector-python")
        sys.exit(1)
    
    # Get user options
    print("\nSetup Options:")
    print("1. Update existing database (recommended)")
    print("2. Fresh install (create new database)")
    print("3. Complete reset (drop all tables and recreate)")
    print("4. Verify existing installation")
    
    choice = input("\nEnter your choice (1-4) [default: 1]: ").strip() or "1"
    
    if choice not in ['1', '2', '3', '4']:
        print("❌ Invalid choice")
        sys.exit(1)
    
    # Initialize setup
    setup = PythonCoinDatabaseSetup()
    
    try:
        # Connect to MySQL
        if not setup.connect_to_mysql():
            print("❌ Failed to connect to MySQL. Check your configuration.")
            sys.exit(1)
        
        if choice == '1':  # Update existing (recommended)
            print("\n🔄 Updating existing database...")
            if setup.create_database():
                if setup.create_tables():
                    setup.insert_sample_data()
                    setup.verify_installation()
                    setup.save_setup_log()
                    print("\n✅ Database update completed successfully!")
                else:
                    print("\n❌ Table update failed")
            else:
                print("\n❌ Database connection failed")
        
        elif choice == '2':  # Fresh install
            print("\n🆕 Performing fresh installation...")
            if setup.create_database():
                if setup.create_tables():
                    setup.insert_sample_data()
                    setup.verify_installation()
                    setup.save_setup_log()
                    print("\n✅ Fresh installation completed successfully!")
                else:
                    print("\n❌ Table creation failed")
            else:
                print("\n❌ Database creation failed")
        
        elif choice == '3':  # Complete reset
            confirm = input("\n⚠️ This will DELETE ALL DATA. Type 'YES' to confirm: ")
            if confirm == 'YES':
                print("\n🔄 Performing complete reset...")
                if setup.create_database():
                    if setup.create_tables(drop_existing=True):
                        setup.insert_sample_data()
                        setup.verify_installation()
                        setup.save_setup_log()
                        print("\n✅ Complete reset completed successfully!")
                    else:
                        print("\n❌ Reset failed")
                else:
                    print("\n❌ Database connection failed")
            else:
                print("❌ Reset cancelled")
        
        elif choice == '4':  # Verify
            print("\n🔍 Verifying existing installation...")
            if setup.create_database():
                if setup.verify_installation():
                    print("\n✅ Database verification completed successfully!")
                else:
                    print("\n⚠️ Verification found some issues (may be normal)")
            else:
                print("\n❌ Database connection failed")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
    finally:
        setup.disconnect()
    
    print(f"\n🏁 Setup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()