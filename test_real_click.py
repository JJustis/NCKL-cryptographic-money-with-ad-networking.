# Test real click recording
import mysql.connector
import requests
from datetime import datetime

def test_click_recording():
    # Connect to database
    conn = mysql.connector.connect(
        host='localhost',
        database='adnetwrk',
        user='root',
        password='',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Get a developer
    cursor.execute("SELECT * FROM developers WHERE username = 'Admin'")
    developer = cursor.fetchone()
    if not developer:
        print("No Admin developer found!")
        return
    
    print(f"Found developer: {developer['username']} (ID: {developer['id']})")
    
    # Get an ad with real payout
    cursor.execute("SELECT * FROM ads_cache LIMIT 1")
    ad = cursor.fetchone()
    if not ad:
        print("No ads found!")
        return
    
    print(f"Found ad: {ad['ad_id']} with payout: {ad['payout_amount']}")
    
    # Manually insert a REAL click (not a view) with correct payout
    cursor.execute("""
        INSERT INTO ad_clicks 
        (developer_id, ad_id, client_id, zone, payout_amount, ip_address, user_agent) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        developer['id'],
        ad['ad_id'] + '_REAL_CLICK_TEST',
        ad['client_id'],
        'test_zone',
        ad['payout_amount'],  # Use real payout amount
        '127.0.0.1',
        'Test Script'
    ))
    
    conn.commit()
    click_id = cursor.lastrowid
    print(f"Success! Inserted test click with ID: {click_id}")
    
    # Verify the click
    cursor.execute("SELECT * FROM ad_clicks WHERE id = %s", (click_id,))
    click = cursor.fetchone()
    
    print("Recorded click details:")
    print(f"  ID: {click['id']}")
    print(f"  Ad ID: {click['ad_id']}")
    print(f"  Payout: {click['payout_amount']}")
    print(f"  Developer ID: {click['developer_id']}")
    print(f"  Time: {click['click_time']}")
    
    # Now check recent clicks to compare
    cursor.execute("""
        SELECT ac.*, d.username 
        FROM ad_clicks ac 
        LEFT JOIN developers d ON ac.developer_id = d.id 
        ORDER BY ac.click_time DESC 
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    print(f"\nRecent clicks:")
    for r in recent:
        click_type = "REAL CLICK" if "REAL_CLICK" in r['ad_id'] else "VIEW" if "_view" in r['ad_id'] else "UNKNOWN"
        print(f"  {r['id']}: {r['username']} | {r['ad_id']} | {r['payout_amount']} PYC | {click_type}")
    
    conn.close()

if __name__ == "__main__":
    test_click_recording()