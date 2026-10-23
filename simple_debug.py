# Simple debug script for ad_clicks
import mysql.connector

def main():
    print("Starting ad_clicks debug...")
    
    try:
        # Test connection
        print("Connecting to database...")
        conn = mysql.connector.connect(
            host='localhost',
            database='adnetwrk',
            user='root',
            password='',
            charset='utf8mb4'
        )
        print("Connected successfully!")
        
        # Check table structure
        cursor = conn.cursor()
        cursor.execute("DESCRIBE ad_clicks")
        columns = cursor.fetchall()
        
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM ad_clicks")
        count = cursor.fetchone()[0]
        print(f"\nTotal rows: {count}")
        
        # Test PyQt query
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, ad_id as transaction_hash, developer_address as wallet_address, 
                   payout_amount as amount, 'credit' as transaction_type,
                   click_time as timestamp, status, zone, developer_name,
                   client_id, ip_address, user_agent
            FROM ad_clicks 
            ORDER BY click_time DESC 
            LIMIT 5
        """
        
        print("\nExecuting PyQt query...")
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Query returned {len(results)} rows")
        
        if results:
            print("\nFirst result:")
            for key, value in results[0].items():
                print(f"  {key}: {value}")
        else:
            print("No results!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()