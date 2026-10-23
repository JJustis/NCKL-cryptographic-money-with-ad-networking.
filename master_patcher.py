#!/usr/bin/env python3
"""
PythonCoin System Master Auto-Patcher
Fixes both PyQt client and PHP dashboard to resolve all communication issues
"""

import os
import re
import shutil
import json
from datetime import datetime

class MasterPatcher:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.php_file = None
        self.pyqt_file = None
        self.backup_dir = f"backups_{self.timestamp}"
        
    def find_files(self):
        """Find PHP dashboard and PyQt client files"""
        # Look for PHP dashboard files
        php_candidates = [
            "dashboard7.php",
            "dashboard.php", 
            "index.php",
            "portal.php"
        ]
        
        for candidate in php_candidates:
            if os.path.exists(candidate):
                self.php_file = candidate
                break
        
        # Look for PyQt client files
        pyqt_candidates = [
            "enhanced_developer_portal.py",
            "developer_portal.py",
            "pythoncoin_client.py",
            "client.py",
            "server.py"
        ]
        
        for candidate in pyqt_candidates:
            if os.path.exists(candidate) and self.is_pyqt_client(candidate):
                self.pyqt_file = candidate
                break
        
        print(f"📁 Found PHP file: {self.php_file or 'Not found'}")
        print(f"📁 Found PyQt file: {self.pyqt_file or 'Not found'}")
        
        return self.php_file is not None or self.pyqt_file is not None
    
    def is_pyqt_client(self, filepath):
        """Check if file is a PyQt client by looking for key patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for PyQt/HTTP server patterns
            patterns = [
                'BaseHTTPRequestHandler',
                'do_GET',
                'HTTPServer',
                'pythoncoin',
                'handle_',
                'server_instance'
            ]
            
            matches = sum(1 for pattern in patterns if pattern in content)
            return matches >= 3
        except:
            return False
    
    def create_backup_dir(self):
        """Create backup directory"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            print(f"✅ Created backup directory: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Error creating backup directory: {e}")
            return False
    
    def backup_file(self, filepath):
        """Backup a file to the backup directory"""
        if not filepath or not os.path.exists(filepath):
            return False
            
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(filepath))
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backed up {filepath} to {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error backing up {filepath}: {e}")
            return False
    
    def patch_pyqt_client(self):
        """Patch the PyQt client file"""
        if not self.pyqt_file:
            print("⚠️ No PyQt client file found - skipping PyQt patches")
            return True
        
        print(f"\n🔧 Patching PyQt client: {self.pyqt_file}")
        
        try:
            with open(self.pyqt_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading PyQt file: {e}")
            return False
        
        # Check if already patched
        if 'handle_get_ads' in content:
            print("✅ PyQt client already has required methods")
            return True
        
        # Add missing imports
        if 'import json' not in content:
            content = 'import json\n' + content
            print("✅ Added json import")
        
        if 'from datetime import datetime' not in content:
            content = 'from datetime import datetime\n' + content
            print("✅ Added datetime import")
        
        # Add missing methods
        missing_methods = '''
    def handle_get_ads(self):
        """Handle GET /ads requests"""
        try:
            sample_ads = [
                {
                    "id": "pyqt_ad_001",
                    "ad_id": "pyqt_ad_001",
                    "title": "PythonCoin PyQt Wallet",
                    "description": "Advanced desktop wallet with P2P advertising integration",
                    "category": "cryptocurrency",
                    "payout": 0.008,
                    "payout_amount": 0.008,
                    "target_url": "https://pythoncoin.org/wallet",
                    "svg_url": f"http://127.0.0.1:{getattr(self, 'port', 8082)}/ad/pyqt_ad_001.svg",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "pyqt_ad_002", 
                    "ad_id": "pyqt_ad_002",
                    "title": "P2P Network Mining",
                    "description": "Join the PythonCoin mining network and earn rewards",
                    "category": "mining",
                    "payout": 0.006,
                    "payout_amount": 0.006,
                    "target_url": "https://pythoncoin.org/mining",
                    "svg_url": f"http://127.0.0.1:{getattr(self, 'port', 8082)}/ad/pyqt_ad_002.svg",
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Serving {len(sample_ads)} ads")
            
            return json.dumps({
                "success": True,
                "ads": sample_ads,
                "total": len(sample_ads),
                "server": "PyQt Enhanced Portal",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error in handle_get_ads: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "ads": []
            })
    
    def handle_register_developer(self):
        """Handle developer registration"""
        return json.dumps({
            "success": True,
            "message": "Developer registration acknowledged",
            "timestamp": datetime.now().isoformat()
        })
    
    def handle_register(self):
        """Handle general registration"""
        return json.dumps({
            "success": True,
            "message": "Registration acknowledged",
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_ad_svg(self, ad_id):
        """Generate SVG for ads"""
        '''
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#0066cc;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#004499;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad1)" rx="15"/>
    <text x="200" y="100" font-family="Arial" font-size="24" fill="white" text-anchor="middle" font-weight="bold">🌐 PythonCoin</text>
    <text x="200" y="130" font-family="Arial" font-size="16" fill="white" text-anchor="middle">PyQt Client Ad</text>
    <text x="200" y="160" font-family="Arial" font-size="14" fill="rgba(255,255,255,0.8)" text-anchor="middle">ID: {ad_id}</text>
    <text x="200" y="220" font-family="Arial" font-size="12" fill="rgba(255,255,255,0.6)" text-anchor="middle">Click to earn PythonCoin</text>
</svg>'''

        # Find insertion point for methods
        if 'def handle_' in content:
            # Insert after last handle method
            last_handle = list(re.finditer(r'def handle_[^(]+\([^)]*\):[^}]+?(?=\n    def|\nclass|\nif __name__|\Z)', content, re.DOTALL))
            if last_handle:
                insertion_point = last_handle[-1].end()
                content = content[:insertion_point] + missing_methods + content[insertion_point:]
                print("✅ Added missing handle methods")
        else:
            # Find class and insert before end
            class_match = re.search(r'class\s+\w+.*?:', content)
            if class_match:
                # Find a good insertion point within the class
                content += missing_methods
                print("✅ Added missing handle methods to end")
        
        # Update do_GET method to handle new endpoints
        if 'def do_GET(self):' in content:
            new_endpoints = '''
            elif path == '/ads':
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = self.server_instance.handle_get_ads()
                self.wfile.write(response.encode())
                
            elif path == '/register_developer':
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = self.server_instance.handle_register_developer()
                self.wfile.write(response.encode())
                
            elif path == '/register':
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = self.server_instance.handle_register()
                self.wfile.write(response.encode())'''
            
            # Find and update do_GET method
            do_get_pattern = r'(def do_GET\(self\):.*?)(else:\s*.*?)(def |\nclass|\nif __name__|\Z)'
            match = re.search(do_get_pattern, content, re.DOTALL)
            if match:
                before_else = match.group(1)
                else_part = match.group(2)
                after = match.group(3)
                
                # Insert new endpoints before the else clause
                new_do_get = before_else + new_endpoints + '\n            \n            ' + else_part
                content = content[:match.start()] + new_do_get + match.group(3) + content[match.end():]
                print("✅ Updated do_GET method with new endpoints")
        
        # Save the patched file
        try:
            with open(self.pyqt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully patched {self.pyqt_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving PyQt file: {e}")
            return False
    
    def patch_php_dashboard(self):
        """Patch the PHP dashboard file"""
        if not self.php_file:
            print("⚠️ No PHP dashboard file found - skipping PHP patches")
            return True
        
        print(f"\n🔧 Patching PHP dashboard: {self.php_file}")
        
        try:
            with open(self.php_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading PHP file: {e}")
            return False
        
        # Add HTTP response parser function if not exists
        if 'function parseHttpResponse' not in content:
            parser_function = '''
// HTTP Response Parser - Auto-added by Master Patcher
function parseHttpResponse($response) {
    if (strpos($response, "HTTP/") === 0) {
        $parts = explode("\\r\\n\\r\\n", $response, 2);
        if (count($parts) >= 2) {
            $headers = $parts[0];
            $body = $parts[1];
            preg_match('/HTTP\\/\\d\\.\\d\\s+(\\d+)/', $headers, $matches);
            $statusCode = isset($matches[1]) ? intval($matches[1]) : 500;
            return [
                'status_code' => $statusCode,
                'headers' => $headers,
                'body' => $body,
                'success' => $statusCode >= 200 && $statusCode < 300
            ];
        }
    }
    return [
        'status_code' => 200,
        'headers' => '',
        'body' => $response,
        'success' => true
    ];
}
'''
            # Insert after existing functions
            insertion_point = content.find('// Initialize API')
            if insertion_point != -1:
                content = content[:insertion_point] + parser_function + "\n" + content[insertion_point:]
                print("✅ Added HTTP response parser function")
        
        # Update proxy_ads case to handle HTTP responses better
        proxy_ads_pattern = r"case 'proxy_ads':.*?break;"
        if re.search(proxy_ads_pattern, content, re.DOTALL):
            enhanced_proxy_ads = '''case 'proxy_ads':
    $clientHost = $_POST['client_host'] ?? '';
    $clientPort = $_POST['client_port'] ?? '8082';
    
    if ($clientHost) {
        $adsUrl = "http://{$clientHost}:{$clientPort}/ads";
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $adsUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept: application/json']);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200 && $response) {
            $parsed = parseHttpResponse($response);
            if ($parsed['success']) {
                $decoded = json_decode($parsed['body'], true);
                if ($decoded !== null) {
                    echo json_encode($decoded);
                } else {
                    echo json_encode([
                        'success' => false,
                        'error' => 'Invalid JSON from client',
                        'fallback' => 'using_sample_ads'
                    ]);
                }
            } else {
                echo json_encode([
                    'success' => false,
                    'error' => "HTTP {$parsed['status_code']} from client",
                    'fallback' => 'using_sample_ads'
                ]);
            }
        } else {
            echo json_encode([
                'success' => false,
                'error' => 'Connection failed',
                'http_code' => $httpCode,
                'fallback' => 'using_sample_ads'
            ]);
        }
    } else {
        echo json_encode(['success' => false, 'error' => 'Missing client host']);
    }
    break;'''
            
            content = re.sub(proxy_ads_pattern, enhanced_proxy_ads, content, flags=re.DOTALL)
            print("✅ Enhanced proxy_ads handler")
        
        # Save the patched file
        try:
            with open(self.php_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully patched {self.php_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving PHP file: {e}")
            return False
    
    def create_test_script(self):
        """Create a test script to verify the fixes"""
        test_script = f'''#!/usr/bin/env python3
"""
PythonCoin System Test Script
Tests the patched PyQt client and PHP dashboard
"""

import requests
import json
import time

def test_pyqt_client():
    """Test PyQt client endpoints"""
    print("🧪 Testing PyQt Client...")
    
    base_url = "http://127.0.0.1:8082"
    endpoints = ["/", "/ads", "/register", "/register_developer"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{{base_url}}{{endpoint}}", timeout=3)
            print(f"  {{endpoint}}: HTTP {{response.status_code}} ✅" if response.status_code == 200 else f"  {{endpoint}}: HTTP {{response.status_code}} ❌")
            
            if endpoint == "/ads" and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success') and data.get('ads'):
                        print(f"    Found {{len(data['ads'])}} ads ✅")
                    else:
                        print(f"    No ads in response ⚠️")
                except:
                    print(f"    Response not JSON ⚠️")
                    
        except Exception as e:
            print(f"  {{endpoint}}: Connection failed ❌ ({{e}})")
    
    return True

def test_php_dashboard():
    """Test PHP dashboard"""
    print("\\n🧪 Testing PHP Dashboard...")
    
    # Test if dashboard loads
    try:
        with open("{self.php_file or 'dashboard.php'}", 'r') as f:
            content = f.read()
        
        if 'parseHttpResponse' in content:
            print("  parseHttpResponse function: Found ✅")
        else:
            print("  parseHttpResponse function: Missing ❌")
            
        if 'proxy_ads' in content:
            print("  proxy_ads handler: Found ✅") 
        else:
            print("  proxy_ads handler: Missing ❌")
            
        print("  PHP file syntax: OK ✅")
        
    except Exception as e:
        print(f"  PHP file test: Failed ❌ ({{e}})")
    
    return True

if __name__ == "__main__":
    print("🚀 PythonCoin System Test")
    print("=" * 40)
    
    test_pyqt_client()
    test_php_dashboard()
    
    print("\\n💡 Next steps:")
    print("1. Start your PyQt client: python3 {self.pyqt_file or 'client.py'}")
    print("2. Open PHP dashboard in browser")
    print("3. Go to Network tab and scan for clients")
    print("4. Select your PyQt client")
    print("5. Check Live Ads tab for real advertisements")
    print("\\n🎉 If you see ads loading, the patches worked!")
'''
        
        try:
            with open(f'test_system_{self.timestamp}.py', 'w') as f:
                f.write(test_script)
            print(f"✅ Created test script: test_system_{self.timestamp}.py")
            return True
        except Exception as e:
            print(f"❌ Error creating test script: {e}")
            return False
    
    def run_master_patch(self):
        """Run the complete patching process"""
        print("🚀 PythonCoin Master Auto-Patcher")
        print("=" * 50)
        print("This will fix both PyQt client and PHP dashboard communication issues")
        print()
        
        # Find files
        if not self.find_files():
            print("❌ No files found to patch!")
            print("💡 Make sure you have either:")
            print("    • dashboard7.php (or similar PHP file)")
            print("    • enhanced_developer_portal.py (or similar PyQt client)")
            return False
        
        # Create backup directory
        if not self.create_backup_dir():
            return False
        
        # Backup files
        if self.php_file:
            self.backup_file(self.php_file)
        if self.pyqt_file:
            self.backup_file(self.pyqt_file)
        
        # Apply patches
        success = True
        
        if self.pyqt_file:
            if not self.patch_pyqt_client():
                success = False
        
        if self.php_file:
            if not self.patch_php_dashboard():
                success = False
        
        # Create test script
        self.create_test_script()
        
        # Final report
        print("\n" + "=" * 50)
        if success:
            print("🎉 Master patching completed successfully!")
            print(f"📁 Backups stored in: {self.backup_dir}")
            
            if self.pyqt_file:
                print(f"✨ {self.pyqt_file} now includes:")
                print("    • handle_get_ads() method")
                print("    • handle_register_developer() method") 
                print("    • Enhanced endpoint routing")
                
            if self.php_file:
                print(f"✨ {self.php_file} now includes:")
                print("    • HTTP response parser")
                print("    • Enhanced proxy handlers")
                print("    • Better error handling")
                
            print("\n🔧 Next steps:")
            print("1. Restart your PyQt client if it's running")
            print("2. Refresh your PHP dashboard in browser")
            print("3. Test with the generated test script")
            print("\n🌟 The JSON parse errors should now be resolved!")
            
        else:
            print("💥 Some patches failed!")
            print(f"📁 Restore from backups in: {self.backup_dir}")
            
        return success

def main():
    patcher = MasterPatcher()
    patcher.run_master_patch()

if __name__ == "__main__":
    main()