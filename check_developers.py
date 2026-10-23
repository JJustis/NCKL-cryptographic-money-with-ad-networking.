# Check developers table structure
import mysql.connector

def main():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='adnetwrk',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # Check developers table structure
        print("Developers table structure:")
        cursor.execute("DESCRIBE developers")
        dev_columns = cursor.fetchall()
        for col in dev_columns:
            print(f"  {col[0]}: {col[1]}")
        
        # Show sample developers data
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM developers LIMIT 3")
        devs = cursor.fetchall()
        
        print(f"\nSample developers ({len(devs)} rows):")
        for dev in devs:
            print(f"  ID: {dev['id']}, Username: {dev['username']}, Address: {dev['pythoncoin_address']}")
        
        # Test JOIN query
        cursor.execute("""
            SELECT ac.id, ac.ad_id, d.pythoncoin_address, d.username, 
                   ac.payout_amount, ac.click_time, ac.zone, ac.client_id,
                   ac.processed
            FROM ad_clicks ac
            LEFT JOIN developers d ON ac.developer_id = d.id
            ORDER BY ac.click_time DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        print(f"\nJOIN query results ({len(results)} rows):")
        for result in results:
            print(f"  Click ID: {result['id']}, Developer: {result['username']}, Address: {result['pythoncoin_address']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()