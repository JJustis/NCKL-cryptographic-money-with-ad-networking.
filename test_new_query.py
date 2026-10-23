# Test the new PyQt query
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
        
        cursor = conn.cursor(dictionary=True)
        
        # Test the new query
        query = """
            SELECT ac.id, ac.ad_id as transaction_hash, 
                   d.pythoncoin_address as wallet_address, 
                   ac.payout_amount as amount, 'credit' as transaction_type,
                   ac.click_time as timestamp, 
                   CASE WHEN ac.processed = 1 THEN 'confirmed' ELSE 'pending' END as status, 
                   ac.zone, d.username as developer_name,
                   ac.client_id, ac.ip_address, ac.user_agent
            FROM ad_clicks ac
            LEFT JOIN developers d ON ac.developer_id = d.id
            ORDER BY ac.click_time DESC 
            LIMIT 5
        """
        
        print("Testing new PyQt query...")
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Query returned {len(results)} rows")
        
        if results:
            print("\nFirst result:")
            for key, value in results[0].items():
                print(f"  {key}: {value}")
            
            print(f"\nAll {len(results)} results:")
            for i, result in enumerate(results):
                print(f"  {i+1}. Developer: {result['developer_name']}, Amount: {result['amount']}, Status: {result['status']}")
        else:
            print("No results!")
        
        conn.close()
        print("\nQuery test successful!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()