#!/usr/bin/env python3
"""
Dashboard-PyQt Communication Test Script
Tests all the endpoints that dashboard8.php uses
"""

import requests
import json
import time

def test_pyqt_endpoints():
    """Test all PyQt server endpoints"""
    
    base_url = "http://127.0.0.1:8082"
    
    endpoints_to_test = [
        ("/", "GET", None),
        ("/test", "GET", None),
        ("/ads", "GET", None),
        ("/client_info", "GET", None),
        ("/stats", "GET", None),
        ("/discover_clients", "GET", None),
        ("/active_clients", "GET", None),
        ("/notifications", "GET", None),
        ("/portal", "GET", None),
        ("/register_developer", "POST", {
            "developer": "test_developer",
            "pythoncoin_address": "PYC1234567890abcdef1234567890",
            "email": "test@example.com"
        }),
        ("/click", "POST", {
            "ad_id": "test_ad_123",
            "client_id": "test_client",
            "developer_address": "PYC1234567890abcdef1234567890",
            "zone": "main",
            "payout_amount": 0.001
        }),
        ("/impression", "POST", {
            "ad_id": "test_ad_123",
            "client_id": "test_client",
            "developer_address": "PYC1234567890abcdef1234567890",
            "zone": "main"
        })
    ]
    
    print("🧪 Testing PyQt Server Endpoints...")
    print("=" * 50)
    
    results = []
    
    for endpoint, method, data in endpoints_to_test:
        url = base_url + endpoint
        print(f"Testing {method} {endpoint}...")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:  # POST
                if endpoint in ["/register_developer", "/click", "/impression"]:
                    response = requests.post(url, json=data, timeout=5)
                else:
                    response = requests.post(url, timeout=5)
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"  ✅ SUCCESS: {response.status_code}")
                    print(f"     Response: {json_data.get('success', 'N/A')}")
                    results.append((endpoint, True, response.status_code))
                except:
                    print(f"  ✅ SUCCESS: {response.status_code} (HTML response)")
                    results.append((endpoint, True, response.status_code))
            else:
                print(f"  ❌ FAILED: {response.status_code}")
                results.append((endpoint, False, response.status_code))
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  CONNECTION REFUSED (Server not running?)")
            results.append((endpoint, False, "Connection Refused"))
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append((endpoint, False, str(e)))
        
        time.sleep(0.5)  # Brief pause between requests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for endpoint, success, status in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {endpoint:<20} - {status}")
    
    print(f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All endpoints working! Dashboard integration should work perfectly.")
    elif success_count > total_count * 0.7:
        print("⚠️  Most endpoints working. Check failed ones for issues.")
    else:
        print("❌ Many endpoints failing. PyQt server may not be running correctly.")
    
    return results


def test_ajax_endpoints():
    """Test AJAX endpoints that dashboard8.php uses"""
    
    dashboard_url = "http://localhost/livepy/pythoncoin/dashboard8.php"
    
    ajax_endpoints = [
        "scan_storage_ads",
        "serve_ad_html",
        "discover_clients",
        "get_ads",
        "test_connection",
        "heartbeat",
        "record_click",
        "record_view"
    ]
    
    print("\n🌐 Testing Dashboard AJAX Endpoints...")
    print("=" * 50)
    
    for ajax_action in ajax_endpoints:
        url = f"{dashboard_url}?ajax={ajax_action}"
        print(f"Testing AJAX: {ajax_action}...")
        
        try:
            if ajax_action in ["record_click", "record_view"]:
                # POST request for recording actions
                response = requests.post(url, data={
                    "ad_id": "test_ad_123",
                    "client_id": "test_client",
                    "zone": "main",
                    "payout_amount": "0.001"
                }, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"  ✅ SUCCESS: {json_data.get('success', 'N/A')}")
                except:
                    print(f"  ✅ SUCCESS: HTML/Other response")
            else:
                print(f"  ❌ FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        
        time.sleep(0.5)


if __name__ == "__main__":
    print("🔧 PythonCoin Dashboard-PyQt Integration Test")
    print("=" * 60)
    print("This script tests communication between dashboard8.php and PyQt server")
    print("Make sure the PyQt application is running first!")
    print("=" * 60)
    
    input("Press Enter to start testing...")
    
    # Test PyQt endpoints
    pyqt_results = test_pyqt_endpoints()
    
    # Test dashboard AJAX endpoints
    test_ajax_endpoints()
    
    print("\n🏁 Testing Complete!")
    print("Check the results above to see which endpoints need attention.")
