#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test ad_clicks retrieval
"""

import mysql.connector
import json
from datetime import datetime

def test_mysql_connection():
    """Test basic MySQL connection"""
    try:
        print("Testing MySQL connection...")
        connection = mysql.connector.connect(
            host='localhost',
            database='adnetwrk',
            user='root',
            password='',
            charset='utf8mb4'
        )
        print("MySQL connection successful")
        return connection
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        return None

def check_table_structure(connection):
    """Check the ad_clicks table structure"""
    try:
        print("\n🔄 Checking ad_clicks table structure...")
        cursor = connection.cursor()
        cursor.execute("DESCRIBE ad_clicks")
        columns = cursor.fetchall()
        
        print("📋 Table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]})")
        
        cursor.close()
        return [col[0] for col in columns]  # Return column names
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return []

def count_total_rows(connection):
    """Count total rows in ad_clicks table"""
    try:
        print("\n🔄 Counting total rows...")
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ad_clicks")
        count = cursor.fetchone()[0]
        cursor.close()
        print(f"📊 Total rows in ad_clicks: {count}")
        return count
    except Exception as e:
        print(f"❌ Error counting rows: {e}")
        return 0

def show_sample_data(connection):
    """Show a few sample rows"""
    try:
        print("\n🔄 Fetching sample data...")
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ad_clicks ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        cursor.close()
        
        print(f"📋 Sample data ({len(rows)} rows):")
        for i, row in enumerate(rows):
            print(f"  Row {i+1}:")
            for key, value in row.items():
                print(f"    {key}: {value}")
            print()
        
        return rows
    except Exception as e:
        print(f"❌ Error fetching sample data: {e}")
        return []

def test_pyqt_query(connection):
    """Test the exact query used in PyQt application"""
    try:
        print("\n🔄 Testing PyQt query...")
        cursor = connection.cursor(dictionary=True)
        
        # This is the exact query from the PyQt app
        query = """
            SELECT id, ad_id as transaction_hash, developer_address as wallet_address, 
                   payout_amount as amount, 'credit' as transaction_type,
                   click_time as timestamp, status, zone, developer_name,
                   client_id, ip_address, user_agent
            FROM ad_clicks 
            ORDER BY click_time DESC 
            LIMIT 1000
        """
        
        print("🔍 Query:")
        print(query)
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"📊 Query returned {len(results)} rows")
        
        if results:
            print("📋 First result:")
            for key, value in results[0].items():
                print(f"  {key}: {value}")
        else:
            print("⚠️ No results returned!")
        
        return results
    except Exception as e:
        print(f"❌ Error with PyQt query: {e}")
        return []

def test_column_existence(connection):
    """Test if required columns exist"""
    try:
        print("\n🔄 Testing column existence...")
        cursor = connection.cursor()
        
        required_columns = ['id', 'ad_id', 'developer_address', 'payout_amount', 'click_time', 'status', 'zone', 'developer_name', 'client_id']
        
        for col in required_columns:
            try:
                cursor.execute(f"SELECT {col} FROM ad_clicks LIMIT 1")
                print(f"  ✅ Column '{col}' exists")
            except Exception as e:
                print(f"  ❌ Column '{col}' missing or error: {e}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error testing columns: {e}")

def main():
    """Main debug function"""
    print("🚀 Starting ad_clicks debug session...")
    print("=" * 60)
    
    # Test connection
    connection = test_mysql_connection()
    if not connection:
        return
    
    # Check table structure
    columns = check_table_structure(connection)
    if not columns:
        connection.close()
        return
    
    # Count rows
    row_count = count_total_rows(connection)
    if row_count == 0:
        print("⚠️ No data in ad_clicks table!")
        connection.close()
        return
    
    # Show sample data
    sample_data = show_sample_data(connection)
    
    # Test column existence
    test_column_existence(connection)
    
    # Test PyQt query
    pyqt_results = test_pyqt_query(connection)
    
    # Close connection
    connection.close()
    
    print("=" * 60)
    print("🎯 Debug Summary:")
    print(f"  - Database connection: ✅")
    print(f"  - Table exists: ✅")
    print(f"  - Total rows: {row_count}")
    print(f"  - Sample data: {'✅' if sample_data else '❌'}")
    print(f"  - PyQt query results: {len(pyqt_results)} rows")
    
    if pyqt_results:
        print("✅ The query should work in PyQt!")
    else:
        print("❌ There's an issue with the PyQt query!")

if __name__ == "__main__":
    main()