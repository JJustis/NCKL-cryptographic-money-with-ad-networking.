# Create test ad clicks with real payouts for testing the payment system
import mysql.connector
from datetime import datetime, timedelta
import random

def create_test_clicks():
    # Connect to database
    conn = mysql.connector.connect(
        host='localhost',
        database='adnetwrk',
        user='root',
        password='',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Get developer info
    cursor.execute("SELECT * FROM developers WHERE username = 'Admin'")
    developer = cursor.fetchone()
    if not developer:
        print("No Admin developer found!")
        return
    
    print(f"Using developer: {developer['username']} (ID: {developer['id']})")
    
    # Create test clicks with realistic payout amounts
    test_clicks = [
        # Live ads (higher negotiated payouts)
        {
            'ad_id': 'live_crypto_course_001',
            'payout': 0.000005,  # Live ad negotiated rate
            'zone': 'header',
            'minutes_ago': 5,
            'source': 'live'
        },
        {
            'ad_id': 'live_wallet_software_002', 
            'payout': 0.000005,  # Live ad negotiated rate
            'zone': 'sidebar',
            'minutes_ago': 15,
            'source': 'live'
        },
        {
            'ad_id': 'live_mining_pool_003',
            'payout': 0.000005,  # Live ad negotiated rate
            'zone': 'footer',
            'minutes_ago': 30,
            'source': 'live'
        },
        # Storage ads (fixed lower payouts)
        {
            'ad_id': 'storage_exchange_promo_004',
            'payout': 0.0000009,  # Storage ad fixed rate
            'zone': 'content',
            'minutes_ago': 45,
            'source': 'storage'
        },
        {
            'ad_id': 'storage_defi_platform_005',
            'payout': 0.0000009,  # Storage ad fixed rate
            'zone': 'banner',
            'minutes_ago': 60,
            'source': 'storage'
        },
        {
            'ad_id': 'storage_nft_marketplace_006',
            'payout': 0.0000009,  # Storage ad fixed rate
            'zone': 'sidebar',
            'minutes_ago': 75,
            'source': 'storage'
        }
    ]
    
    print(f"Creating {len(test_clicks)} test ad clicks with real payouts...")
    
    for i, click_data in enumerate(test_clicks):
        # Calculate click time
        click_time = datetime.now() - timedelta(minutes=click_data['minutes_ago'])
        
        # Insert click
        cursor.execute("""
            INSERT INTO ad_clicks 
            (developer_id, ad_id, client_id, zone, payout_amount, 
             click_time, ip_address, user_agent, processed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            developer['id'],
            click_data['ad_id'],
            f'test_client_{i+1:03d}',
            click_data['zone'],
            click_data['payout'],
            click_time,
            f'192.168.1.{100+i}',
            'Test Browser/1.0',
            0  # Not processed yet
        ))
    
    conn.commit()
    
    # Verify the clicks
    cursor.execute("""
        SELECT ac.*, d.username 
        FROM ad_clicks ac 
        LEFT JOIN developers d ON ac.developer_id = d.id 
        WHERE ac.payout_amount > 0 
        ORDER BY ac.click_time DESC 
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    print(f"\nCreated clicks:")
    total_payout = 0
    for r in results:
        total_payout += float(r['payout_amount'])
        status = "PAID" if r['processed'] else "PENDING"
        print(f"  ID: {r['id']} | {r['username']} | {r['ad_id']} | {r['payout_amount']} PYC | {status}")
    
    print(f"\nTotal pending payouts: {total_payout:.8f} PYC")
    
    conn.close()
    print("Test clicks created successfully!")
    print("You can now test the Payment tab in the PyQt application.")

if __name__ == "__main__":
    create_test_clicks()