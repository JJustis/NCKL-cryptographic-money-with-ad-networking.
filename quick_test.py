#!/usr/bin/env python3
import requests
import json

def quick_test():
    base_url = "http://localhost:8082"
    
    print("🧪 Quick Server Test")
    print("=" * 30)
    
    # Test /ads endpoint
    print("\n1. Testing /ads endpoint...")
    try:
        response = requests.get(f"{base_url}/ads", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data.get('total', 0)} ads")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test /register_developer
    print("\n2. Testing /register_developer...")
    try:
        response = requests.post(f"{base_url}/register_developer", 
                               json={"developer": "test", "pythoncoin_address": "test123"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Registration successful")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Quick test completed!")

if __name__ == "__main__":
    quick_test()
