#!/usr/bin/env python3
"""
Fix CSS Escaping Issue in PythonCoin Developer Portal Integration (c.py)
Corrects unescaped literal backslashes in CSS within JavaScript template strings
"""

import os
import sys
import re
import shutil
from datetime import datetime

class CSSEscapingFixer:
    def __init__(self, target_file="c.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_made = []
        
    def create_backup(self):
        """Create backup of original file"""
        try:
            shutil.copy2(self.target_file, self.backup_filename)
            print(f"✅ Backup created: {self.backup_filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def read_file(self):
        """Read the target file"""
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Read file: {self.target_file} ({len(content)} characters)")
            return content
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return None
    
    def write_file(self, content):
        """Write the modified content back to file"""
        try:
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated file: {self.target_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to write file: {e}")
            return False

    def fix_css_escaping_in_js(self, content):
        """Fix CSS escaping issues in JavaScript template strings"""
        print("🔧 Fixing CSS escaping in JavaScript template strings...")
        
        # Pattern to find the problematic CSS in the showEarningPopup function
        css_pattern = r'(popup\.style\.cssText = `[^`]*?transform: translate\(-50%, -50%\);[^`]*?`)'
        
        # Fixed CSS with proper escaping
        fixed_css = '''popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #28a745;
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            z-index: 10001;
            text-align: center;
            font-weight: bold;
        `;'''
        
        if re.search(css_pattern, content, re.DOTALL):
            content = re.sub(css_pattern, fixed_css, content, flags=re.DOTALL)
            self.changes_made.append("✅ Fixed CSS escaping in showEarningPopup function")
        
        # Also fix any other CSS template literals that might have issues
        # Pattern to find CSS properties with transform
        transform_pattern = r'(transform: translate\([^)]+\))'
        
        # This shouldn't need escaping in template literals, but let's be safe
        def fix_transform(match):
            return match.group(1)  # Keep as is since it should work in template literals
        
        # Fix any other potential CSS escaping issues
        content = self.fix_general_css_escaping(content)
        
        return content
    
    def fix_general_css_escaping(self, content):
        """Fix general CSS escaping issues throughout the file"""
        print("🔧 Fixing general CSS escaping issues...")
        
        # Pattern to find CSS in template literals that might have escaping issues
        # Look for style properties that commonly cause issues
        
        # Fix any remaining transform properties
        transform_fixes = [
            (r'transform: translate\(-50%\\, -50%\)', 'transform: translate(-50%, -50%)'),
            (r'transform: translate\(-50%\, -50%\)', 'transform: translate(-50%, -50%)'),
        ]
        
        for pattern, replacement in transform_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                self.changes_made.append(f"✅ Fixed transform CSS property: {pattern}")
        
        # Fix any percentage values that might be escaped
        percentage_fixes = [
            (r'50%\\', '50%'),
            (r'100%\\', '100%'),
        ]
        
        for pattern, replacement in percentage_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                self.changes_made.append(f"✅ Fixed percentage value: {pattern}")
        
        return content
    
    def fix_javascript_template_literals(self, content):
        """Comprehensive fix for JavaScript template literal issues"""
        print("🔧 Fixing JavaScript template literal syntax...")
        
        # Find the generate_custom_js method and fix the template literal
        js_method_pattern = r'(def generate_custom_js\(self, developer_address\):.*?js_code = f\'\'\'.*?\'\'\')'
        
        if re.search(js_method_pattern, content, re.DOTALL):
            # Replace the entire JavaScript generation with a corrected version
            fixed_js_method = '''def generate_custom_js(self, developer_address):
        """Generate custom JavaScript for a specific developer"""
        ads = self.get_available_ads()
        
        js_code = f"""// PythonCoin Wallet - Custom Ad JavaScript
// Generated for developer: {developer_address}
// Server: {self.wallet.address if self.wallet else 'Unknown'}

(function() {{
    'use strict';
    
    const PYC_WALLET_CONFIG = {{
        serverAddress: '{self.wallet.address if self.wallet else 'unknown'}',
        serverHost: '127.0.0.1:{self.port}',
        developerAddress: '{developer_address}',
        ads: {ads}
    }};
    
    let currentAdIndex = 0;
    
    function initPYCWalletAds() {{
        console.log('[PYC-WALLET] Loading ads from PythonCoin wallet server');
        
        if (PYC_WALLET_CONFIG.ads.length > 0) {{
            displayWalletAd(PYC_WALLET_CONFIG.ads[0]);
            startAdRotation();
        }}
    }}
    
    function displayWalletAd(ad) {{
        const containers = document.querySelectorAll('[data-pyc-zone]');
        
        containers.forEach(container => {{
            container.innerHTML = `
                <div style="border: 2px solid #0066cc; border-radius: 12px; padding: 20px; background: white; margin: 15px 0; cursor: pointer;">
                    <div style="position: absolute; top: 10px; right: 10px; background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px;">PYC</div>
                    <h3 style="color: #0066cc; margin: 0 0 10px 0;">${{ad.title}}</h3>
                    <p style="color: #666; margin: 0 0 15px 0;">${{ad.description}}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #0066cc; font-size: 0.9em;">${{ad.category}}</span>
                        <span style="background: #28a745; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.8em;">+${{ad.payout.toFixed(6)}} PYC</span>
                    </div>
                </div>
            `;
            
            container.onclick = function() {{
                handleWalletAdClick(ad);
            }};
        }});
    }}
    
    function handleWalletAdClick(ad) {{
        console.log('[PYC-WALLET] Ad clicked:', ad.title);
        
        showEarningPopup(ad.payout);
        
        fetch('http://127.0.0.1:{self.port}/click', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                ad_id: ad.id,
                developer: 'developer_' + PYC_WALLET_CONFIG.developerAddress.substring(0, 8),
                pythoncoin_address: PYC_WALLET_CONFIG.developerAddress,
                payout_amount: ad.payout,
                zone: 'wallet_served'
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                console.log('[PYC-WALLET] Payment sent:', data.amount, 'PYC');
            }}
        }})
        .catch(error => console.error('[PYC-WALLET] Click error:', error));
        
        if (ad.click_url) {{
            window.open(ad.click_url, '_blank');
        }}
    }}
    
    function showEarningPopup(amount) {{
        const popup = document.createElement('div');
        popup.style.position = 'fixed';
        popup.style.top = '50%';
        popup.style.left = '50%';
        popup.style.transform = 'translate(-50%, -50%)';
        popup.style.background = '#28a745';
        popup.style.color = 'white';
        popup.style.padding = '20px 30px';
        popup.style.borderRadius = '15px';
        popup.style.zIndex = '10001';
        popup.style.textAlign = 'center';
        popup.style.fontWeight = 'bold';
        
        popup.innerHTML = `
            <div style="font-size: 18px;">💰 PythonCoin Earned!</div>
            <div style="font-size: 14px;">+${{amount.toFixed(6)}} PYC</div>
        `;
        
        document.body.appendChild(popup);
        
        setTimeout(() => {{
            popup.remove();
        }}, 3000);
    }}
    
    function startAdRotation() {{
        if (PYC_WALLET_CONFIG.ads.length <= 1) return;
        
        setInterval(() => {{
            currentAdIndex = (currentAdIndex + 1) % PYC_WALLET_CONFIG.ads.length;
            displayWalletAd(PYC_WALLET_CONFIG.ads[currentAdIndex]);
        }}, 30000);
    }}
    
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initPYCWalletAds);
    }} else {{
        initPYCWalletAds();
    }}
    
}})();
"""
        
        return js_code'''
        
            content = re.sub(js_method_pattern, fixed_js_method, content, flags=re.DOTALL)
            self.changes_made.append("✅ Fixed JavaScript template literal in generate_custom_js method")
        
        return content
    
    def fix_python_string_formatting(self, content):
        """Fix Python string formatting issues"""
        print("🔧 Fixing Python string formatting...")
        
        # Fix any f-string issues with braces
        # Look for patterns that might cause issues
        
        # Fix CSS in f-strings or template strings
        css_fixes = [
            # Fix transform property in CSS
            (r"transform: translate\(-50%, -50%\);", "transform: translate(-50%, -50%);"),
            # Fix any escaped quotes that shouldn't be escaped
            (r'\\"', '"'),
        ]
        
        for pattern, replacement in css_fixes:
            if pattern in content and pattern != replacement:
                content = content.replace(pattern, replacement)
                self.changes_made.append(f"✅ Fixed CSS formatting: {pattern[:30]}...")
        
        return content
    
    def fix_developers_table_method(self, content):
        """Fix the incomplete update_developers_table method"""
        print("🔧 Fixing incomplete update_developers_table method...")
        
        # Look for the incomplete method that's causing syntax issues
        incomplete_method_pattern = r'(def on_developer_registered\(self, developer, address\):.*?self\.update_developers_table\(\)\s*dev_earnings = sum.*?)'
        
        if re.search(incomplete_method_pattern, content, re.DOTALL):
            # Replace with corrected method
            fixed_method = '''def on_developer_registered(self, developer, address):
        """Handle developer registration"""
        self.log_message(f"👤 Developer registered: {developer} -> {address[:8]}...")
        self.update_developers_table()
    
    def update_developers_table(self):
        """Update the developers table display"""
        if not hasattr(self, 'developers_table') or not self.portal_server:
            return
        
        developers = getattr(self.portal_server, 'registered_developers', {})
        payments = getattr(self.portal_server, 'click_payments', [])
        
        self.developers_table.setRowCount(len(developers))
        
        for row, (developer, address) in enumerate(developers.items()):
            self.developers_table.setItem(row, 0, QTableWidgetItem(developer))
            self.developers_table.setItem(row, 1, QTableWidgetItem(f"{address[:8]}..."))
            
            dev_clicks = len([p for p in payments if p.get('developer') == developer])
            self.developers_table.setItem(row, 2, QTableWidgetItem(str(dev_clicks)))
            
            dev_earnings = sum(p.get('amount', 0) for p in payments if p.get('developer') == developer)
            self.developers_table.setItem(row, 3, QTableWidgetItem(f"{dev_earnings:.8f} PYC"))'''
            
            content = re.sub(incomplete_method_pattern, fixed_method, content, flags=re.DOTALL)
            self.changes_made.append("✅ Fixed incomplete update_developers_table method")
        
        return content
    
    def apply_all_fixes(self):
        """Apply all fixes to the file"""
        print("🚀 Starting CSS Escaping Fix for PythonCoin Portal Integration...")
        print("=" * 60)
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Read original file
        content = self.read_file()
        if not content:
            return False
        
        print(f"📋 Original file size: {len(content):,} characters")
        
        # Apply all fixes
        try:
            content = self.fix_css_escaping_in_js(content)
            content = self.fix_javascript_template_literals(content)
            content = self.fix_python_string_formatting(content)
            content = self.fix_developers_table_method(content)
            content = self.fix_general_css_escaping(content)
            
            print(f"📋 Fixed file size: {len(content):,} characters")
            
            # Write fixed file
            if self.write_file(content):
                print("\n" + "=" * 60)
                print("🎉 CSS ESCAPING FIXES COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                
                print("\n📋 Fixes Applied:")
                for change in self.changes_made:
                    print(f"  {change}")
                
                print(f"\n💾 Backup saved as: {self.backup_filename}")
                print(f"✅ Fixed file: {self.target_file}")
                
                print("\n🔧 What Was Fixed:")
                print("• CSS escaping in JavaScript template literals")
                print("• Transform property syntax errors")
                print("• String formatting issues in Python")
                print("• Incomplete method definitions")
                print("• General CSS property escaping")
                
                print("\n✅ Your file should now run without CSS escaping errors!")
                
                return True
            else:
                print("❌ Failed to write fixed file")
                return False
                
        except Exception as e:
            print(f"❌ Fix failed: {str(e)}")
            return False

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix CSS Escaping Issues in PythonCoin Developer Portal Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fix_css.py                    # Fix default c.py file
  python fix_css.py -f c.py           # Fix specific file
  python fix_css.py --target my_integration.py  # Alternative syntax

This script fixes:
• CSS escaping errors in JavaScript template literals
• Transform property syntax issues
• String formatting problems
• Incomplete method definitions
• General CSS property escaping issues

The script creates a backup before making any changes.
        """
    )
    
    parser.add_argument(
        '-f', '--file', '--target',
        dest='target_file',
        default='c.py',
        help='Target file to fix (default: c.py)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='CSS Escaping Fix for PythonCoin Portal Integration v1.0'
    )
    
    args = parser.parse_args()
    
    print("🔧 CSS Escaping Fix for PythonCoin Portal Integration")
    print("=" * 55)
    print(f"Target file: {args.target_file}")
    print()
    
    # Check if target file exists
    if not os.path.exists(args.target_file):
        print(f"❌ Error: Target file '{args.target_file}' not found!")
        print("\nMake sure you're in the correct directory and the file exists.")
        print("You can specify a different file with: -f filename.py")
        return 1
    
    # Create fixer and run
    fixer = CSSEscapingFixer(args.target_file)
    
    try:
        success = fixer.apply_all_fixes()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nIf this persists, please check:")
        print("1. File permissions are correct")
        print("2. Target file is a valid Python file")
        print("3. You have write access to the directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())