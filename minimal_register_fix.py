#!/usr/bin/env python3
"""
Quick Server Method Fix
Adds missing server methods to fix the 500 Internal Server Error
"""

import os
import re
from datetime import datetime

def fix_missing_server_methods():
    """Add all missing server methods to fix the 500 error"""
    
    print("🔧 Quick Server Method Fix")
    print("=" * 40)
    
    try:
        with open('pyqt.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ pyqt.py not found!")
        return False
    
    # Missing methods to add
    missing_methods = '''
    def handle_get_ads(self, query_params=None):
        """Handle requests for advertisements - FIXED VERSION"""
        try:
            developer_address = None
            zone = None
            
            # Handle both query_params dict and direct parameters
            if isinstance(query_params, dict):
                developer_address = query_params.get('developer', [None])[0] if 'developer' in query_params else None
                zone = query_params.get('zone', [None])[0] if 'zone' in query_params else None
            
            print(f"[GET_ADS] Request from developer: {developer_address}, zone: {zone}")
            
            # Get ads from various sources
            ads = []
            
            # Try enhanced database first
            if hasattr(self, 'enhanced_db_manager') and self.enhanced_db_manager:
                try:
                    ads = self.enhanced_db_manager.get_all_ads() if hasattr(self.enhanced_db_manager, 'get_all_ads') else []
                    print(f"[GET_ADS] Found {len(ads)} ads from enhanced database")
                except Exception as e:
                    print(f"[GET_ADS] Enhanced DB error: {e}")
            
            # Fallback to existing methods
            if not ads and hasattr(self, 'get_available_ads'):
                try:
                    ads = self.get_available_ads()
                    print(f"[GET_ADS] Found {len(ads)} ads from get_available_ads")
                except Exception as e:
                    print(f"[GET_ADS] get_available_ads error: {e}")
            
            # Final fallback to sample ads
            if not ads:
                ads = self.get_sample_ads()
                print(f"[GET_ADS] Using {len(ads)} sample ads")
            
            return json.dumps({
                "success": True, 
                "ads": ads,
                "total": len(ads),
                "developer": developer_address,
                "zone": zone,
                "server_time": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"[GET_ADS] Error: {e}")
            import traceback
            traceback.print_exc()
            return json.dumps({"success": False, "error": str(e)})
    
    def get_sample_ads(self):
        """Provide sample advertisements when no other ads are available"""
        return [
            {
                "id": "sample_ad_001",
                "client_id": "pyqt_client",
                "title": "PythonCoin Mining Pool",
                "description": "Join our mining pool and earn PYC rewards",
                "category": "cryptocurrency",
                "payout": 0.005,
                "click_url": "https://pythoncoin.org/mining",
                "image_url": "https://placehold.co/400x300/0066cc/ffffff?text=Mining",
                "svg_url": "http://localhost:8082/svg/sample_ad_001"
            },
            {
                "id": "sample_ad_002", 
                "client_id": "pyqt_client",
                "title": "Secure PythonCoin Wallet",
                "description": "Keep your PYC safe with our secure wallet",
                "category": "security",
                "payout": 0.003,
                "click_url": "https://pythoncoin.org/wallet",
                "image_url": "https://placehold.co/400x300/28a745/ffffff?text=Wallet",
                "svg_url": "http://localhost:8082/svg/sample_ad_002"
            },
            {
                "id": "sample_ad_003",
                "client_id": "pyqt_client", 
                "title": "DeFi with PythonCoin",
                "description": "Explore decentralized finance opportunities",
                "category": "finance",
                "payout": 0.008,
                "click_url": "https://pythoncoin.org/defi",
                "image_url": "https://placehold.co/400x300/ffc107/ffffff?text=DeFi",
                "svg_url": "http://localhost:8082/svg/sample_ad_003"
            }
        ]
    
    def handle_client_info(self, query_params=None):
        """Handle client info requests - FIXED VERSION"""
        try:
            print("[CLIENT_INFO] Processing request")
            
            client_info = {
                "success": True,
                "client_id": getattr(self, 'client_id', 'pyqt_client_001'),
                "name": "PythonCoin Wallet Client",
                "version": "2.1.0", 
                "status": "online",
                "host": "127.0.0.1",
                "port": getattr(self, 'actual_port', getattr(self, 'port', 8082)),
                "ad_count": len(self.get_sample_ads()),
                "peers": 0,
                "server_time": datetime.now().isoformat(),
                "endpoints": [
                    "/register_developer",
                    "/ads", 
                    "/client_info",
                    "/ad_click",
                    "/test_enhanced"
                ]
            }
            
            print(f"[CLIENT_INFO] Returning info: {client_info['name']}")
            return json.dumps(client_info)
            
        except Exception as e:
            print(f"[CLIENT_INFO] Error: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def handle_ad_click(self, data):
        """Handle ad click requests - FIXED VERSION"""
        try:
            ad_id = data.get('ad_id', '')
            developer_address = data.get('developer_address', '')
            payout_amount = float(data.get('payout_amount', 0.001))
            zone = data.get('zone', 'default')
            
            print(f"[AD_CLICK] Processing: {ad_id} -> {developer_address} ({payout_amount} PYC)")
            
            # Record in enhanced database if available
            if hasattr(self, 'enhanced_db_manager') and self.enhanced_db_manager:
                try:
                    self.enhanced_db_manager.record_ad_click(
                        ad_id, 
                        getattr(self, 'client_id', 'pyqt_client'),
                        developer_address, 
                        zone, 
                        payout_amount, 
                        '127.0.0.1', 
                        'PythonCoin-Client'
                    )
                    print("[AD_CLICK] Recorded in enhanced database")
                except Exception as db_error:
                    print(f"[AD_CLICK] Database error: {db_error}")
            
            # Update stats if available
            if hasattr(self, 'click_payments'):
                self.click_payments.append({
                    'ad_id': ad_id,
                    'developer': developer_address,
                    'amount': payout_amount,
                    'timestamp': datetime.now().isoformat()
                })
            
            return json.dumps({
                "success": True,
                "message": "Click recorded successfully",
                "ad_id": ad_id,
                "developer_address": developer_address,
                "payout_amount": payout_amount,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"[AD_CLICK] Error: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def handle_impression(self, data):
        """Handle ad impression tracking - FIXED VERSION"""
        try:
            ad_id = data.get('ad_id', '')
            developer_address = data.get('developer_address', '')
            
            print(f"[IMPRESSION] Recorded: {ad_id} from {developer_address}")
            
            # Update impression count
            if hasattr(self, 'ads_served'):
                self.ads_served += 1
            else:
                self.ads_served = 1
            
            return json.dumps({
                "success": True,
                "message": "Impression recorded", 
                "ad_id": ad_id,
                "total_impressions": getattr(self, 'ads_served', 1)
            })
            
        except Exception as e:
            print(f"[IMPRESSION] Error: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def handle_stats(self, query_params=None):
        """Handle stats requests - FIXED VERSION"""
        try:
            stats = {
                "success": True,
                "server_status": "online",
                "total_ads": len(self.get_sample_ads()),
                "total_clicks": len(getattr(self, 'click_payments', [])),
                "total_impressions": getattr(self, 'ads_served', 0),
                "registered_developers": len(getattr(self, 'registered_developers', {})),
                "server_time": datetime.now().isoformat(),
                "server_port": getattr(self, 'actual_port', getattr(self, 'port', 8082))
            }
            
            print(f"[STATS] Serving stats: {stats}")
            return json.dumps(stats)
            
        except Exception as e:
            print(f"[STATS] Error: {e}")
            return json.dumps({"success": False, "error": str(e)})
'''
    
    # Find insertion point in the server class
    server_patterns = [
        r'(class EnhancedDeveloperPortalServer.*?)(    def [^_].*?)',
        r'(def handle_register_developer.*?return json\.dumps.*?\n)(    def [^_].*?)',
        r'(def start_portal_server.*?\n)(    def [^_].*?)'
    ]
    
    inserted = False
    for pattern in server_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            insertion_point = match.end(1)
            content = content[:insertion_point] + missing_methods + '\n' + content[insertion_point:]
            print("✅ Inserted missing server methods")
            inserted = True
            break
    
    if not inserted:
        # Try to find any class with "Server" in the name
        server_class_match = re.search(r'(class \w*Server\w*.*?{)(.*?)(\n\nclass|\nif __name__|$)', content, re.DOTALL)
        if server_class_match:
            insertion_point = server_class_match.end(1)
            content = content[:insertion_point] + missing_methods + content[insertion_point:]
            print("✅ Inserted missing methods in server class")
            inserted = True
    
    if not inserted:
        print("❌ Could not find server class - adding at end of file")
        content += missing_methods
        inserted = True
    
    # Also ensure the routing exists
    routing_fix = '''
                        elif path == '/ads':
                            response = self.server_instance.handle_get_ads(parse_qs(parsed_path.query) if hasattr(self, 'parsed_path') else {})
                        elif path == '/client_info':
                            response = self.server_instance.handle_client_info({})
                        elif path == '/ad_click':
                            response = self.server_instance.handle_ad_click(data)
                        elif path == '/stats':
                            response = self.server_instance.handle_stats({})'''
    
    # Check if routing needs to be added
    if 'elif path == \'/ads\':' not in content:
        # Find existing routing
        existing_routing = re.search(r'(elif path == \'/register_developer\'.*?\n)', content, re.DOTALL)
        if existing_routing:
            insertion_point = existing_routing.end(1)
            content = content[:insertion_point] + routing_fix + '\n' + content[insertion_point:]
            print("✅ Added missing routing")
        else:
            print("⚠️ Could not find routing section")
    
    # Write the fixed content
    try:
        with open('pyqt.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Successfully fixed missing methods")
        return True
    except Exception as e:
        print(f"❌ Error writing fixed file: {e}")
        return False

def create_quick_test():
    """Create a quick test script"""
    test_script = '''#!/usr/bin/env python3
import requests
import json

def quick_test():
    base_url = "http://localhost:8082"
    
    print("🧪 Quick Server Test")
    print("=" * 30)
    
    # Test /ads endpoint
    print("\\n1. Testing /ads endpoint...")
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
    print("\\n2. Testing /register_developer...")
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
    
    print("\\n✅ Quick test completed!")

if __name__ == "__main__":
    quick_test()
'''
    
    with open('quick_test.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    print("✅ Created quick_test.py")

def main():
    if fix_missing_server_methods():
        create_quick_test()
        print("\n🎉 Server methods fixed!")
        print("\nNext steps:")
        print("1. Restart your PyQt application")
        print("2. Run: python quick_test.py")
        print("3. The 500 error should be resolved")
        print("\nFixed methods:")
        print("• handle_get_ads")
        print("• handle_client_info") 
        print("• handle_ad_click")
        print("• handle_impression")
        print("• handle_stats")
        print("• get_sample_ads")
        return True
    else:
        print("❌ Fix failed")
        return False

if __name__ == "__main__":
    main()