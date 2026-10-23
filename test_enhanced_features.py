#!/usr/bin/env python3
"""
Enhanced PyQt Features Test Script
Tests the injected enterprise features including database and enhanced endpoints
"""
import requests
import json
import time

def test_enhanced_endpoints():
    """Test all enhanced endpoints"""
    base_url = "http://localhost:8082"
    
    print("🧪 Testing Enhanced PyQt Features")
    print("=" * 50)
    
    # Test 1: Enhanced test endpoint
    print("\n1. Testing enhanced test endpoint...")
    try:
        response = requests.post(f"{base_url}/test_enhanced", 
                               json={"test": "enhanced_features"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('enhanced_features'):
                print("   ✅ Enhanced features detected!")
                print(f"   Available endpoints: {data.get('endpoints', [])}")
            else:
                print("   ❌ Enhanced features not detected")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - is PyQt server running?")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 2: Enhanced developer registration
    print("\n2. Testing enhanced developer registration...")
    try:
        registration_data = {
            "developer": "enhanced_test_dev",
            "pythoncoin_address": "enhanced_test_address_123456789",
            "email": "test@enhanced.com"
        }
        
        response = requests.post(f"{base_url}/register_developer", 
                               json=registration_data, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Enhanced registration successful!")
                if data.get('enhanced_features'):
                    print("   ✅ Enhanced features confirmed!")
                    print(f"   Server info: {data.get('server_info', {})}")
                else:
                    print("   ⚠️ Registration worked but enhanced features not detected")
            else:
                print(f"   ❌ Registration failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Registration test error: {e}")
    
    # Test 3: Enhanced click tracking
    print("\n3. Testing enhanced click tracking...")
    try:
        click_data = {
            "ad_id": "enhanced_test_ad_001",
            "developer_address": "enhanced_test_address_123456789",
            "zone": "test_zone",
            "payout_amount": 0.005
        }
        
        response = requests.post(f"{base_url}/enhanced_click", 
                               json=click_data, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('enhanced_features'):
                print("   ✅ Enhanced click tracking successful!")
                print(f"   Processed payout: {data.get('payout_amount')} PYC")
            else:
                print(f"   ❌ Click tracking failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Click test error: {e}")
    
    # Test 4: Database connectivity (if enhanced database is available)
    print("\n4. Testing database integration...")
    print("   Check PyQt console output for database connection messages")
    print("   Look for: '✅ Enhanced database connected successfully'")
    
    print("\n🎉 Enhanced features testing completed!")
    print("\nNext steps:")
    print("1. Check PyQt console for detailed logs")
    print("2. Verify database tables were created (if MySQL is configured)")
    print("3. Test with the PHP dashboard integration")

if __name__ == "__main__":
    test_enhanced_endpoints()
