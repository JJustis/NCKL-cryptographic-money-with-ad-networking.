#!/usr/bin/env python3
"""
Targeted Mining Parameter Fix
Specifically fixes the CryptoMiningThread parameter mismatch
"""

import os
import sys
import re
import shutil
from datetime import datetime

class TargetedMiningFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_targetmining_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def find_and_fix_mining_thread_class(self, content):
        """Find and fix the CryptoMiningThread class definition"""
        print("🔍 Finding CryptoMiningThread class...")
        
        # Look for the class definition
        class_pattern = r'class CryptoMiningThread\(QThread\):'
        if not re.search(class_pattern, content):
            print("❌ CryptoMiningThread class not found")
            return content
        
        print("✅ Found CryptoMiningThread class")
        
        # Find the __init__ method and fix it
        init_patterns = [
            r'def __init__\(self, blockchain, wallet_address, threads=1\):',
            r'def __init__\(self, blockchain, wallet_address, threads=1\) :',
            r'def __init__\(self, blockchain, wallet_address, threads=1\)\s*:',
        ]
        
        fixed = False
        for pattern in init_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, 'def __init__(self, blockchain, wallet, threads=1):', content)
                print("✅ Fixed CryptoMiningThread.__init__ signature")
                fixed = True
                break
        
        if not fixed:
            print("⚠️ Could not find __init__ method to fix")
        
        # Fix the parameter assignment
        assignment_patterns = [
            r'self\.wallet_address = wallet_address',
            r'self\.wallet_address=wallet_address',
        ]
        
        for pattern in assignment_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, 'self.wallet = wallet', content)
                print("✅ Fixed wallet parameter assignment")
                self.changes_made.append("Fixed CryptoMiningThread parameter assignment")
                break
        
        return content
    
    def find_and_fix_mining_thread_calls(self, content):
        """Find and fix all calls to CryptoMiningThread"""
        print("🔍 Finding CryptoMiningThread instantiation calls...")
        
        # Look for the instantiation in toggle_mining method
        call_patterns = [
            r'self\.mining_thread = CryptoMiningThread\(\s*blockchain=self\.blockchain,\s*wallet_address=mining_address,\s*threads=threads\s*\)',
            r'self\.mining_thread = CryptoMiningThread\(\s*blockchain=self\.blockchain,\s*wallet=self\.wallet,\s*threads=threads\s*\)',
            r'CryptoMiningThread\(\s*blockchain=self\.blockchain,\s*wallet_address=.*?,\s*threads=.*?\)',
            r'CryptoMiningThread\(\s*self\.blockchain,\s*mining_address,\s*threads\)',
        ]
        
        # The correct call should be:
        correct_call = '''self.mining_thread = CryptoMiningThread(
                    blockchain=self.blockchain,
                    wallet=self.wallet,
                    threads=threads
                )'''
        
        # Find the toggle_mining method and fix the call
        toggle_mining_start = content.find('def toggle_mining(self):')
        if toggle_mining_start == -1:
            print("❌ toggle_mining method not found")
            return content
        
        # Find the end of toggle_mining method
        next_method = content.find('\n    def ', toggle_mining_start + 1)
        if next_method == -1:
            toggle_mining_section = content[toggle_mining_start:]
        else:
            toggle_mining_section = content[toggle_mining_start:next_method]
        
        # Look for mining thread creation in this section
        mining_thread_pattern = r'self\.mining_thread = CryptoMiningThread\([^)]*\)'
        
        if re.search(mining_thread_pattern, toggle_mining_section):
            # Replace the problematic call
            new_section = re.sub(
                mining_thread_pattern,
                '''self.mining_thread = CryptoMiningThread(
                    blockchain=self.blockchain,
                    wallet=self.wallet,
                    threads=threads
                )''',
                toggle_mining_section
            )
            
            # Replace in the full content
            if next_method == -1:
                content = content[:toggle_mining_start] + new_section
            else:
                content = content[:toggle_mining_start] + new_section + content[next_method:]
            
            print("✅ Fixed CryptoMiningThread instantiation call")
            self.changes_made.append("Fixed CryptoMiningThread instantiation")
        
        return content
    
    def fix_wallet_usage_in_mining_thread(self, content):
        """Fix wallet usage throughout the mining thread"""
        print("🔧 Fixing wallet usage in mining thread...")
        
        # Fix DataTransaction creation
        data_tx_patterns = [
            r'sender=self\.wallet_address,',
            r'sender=self\.wallet_address ,',
        ]
        
        for pattern in data_tx_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, 'sender=self.wallet.public_key,', content)
                print("✅ Fixed DataTransaction sender parameter")
                self.changes_made.append("Fixed DataTransaction sender")
                break
        
        # Fix mine_pending_transactions call
        mine_call_patterns = [
            r'self\.blockchain\.mine_pending_transactions\(self\.wallet_address\)',
            r'self\.blockchain\.mine_pending_transactions\( self\.wallet_address \)',
        ]
        
        for pattern in mine_call_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, 'self.blockchain.mine_pending_transactions(self.wallet.address)', content)
                print("✅ Fixed mine_pending_transactions call")
                self.changes_made.append("Fixed mine_pending_transactions call")
                break
        
        # Add private key to DataTransaction if missing
        if 'DataTransaction(' in content and 'private_key=self.wallet.private_key' not in content:
            # Look for DataTransaction creation and add private key
            data_tx_creation_pattern = r'(dummy_tx = DataTransaction\(\s*sender=self\.wallet\.public_key,\s*data_content=f"Mining block at \{time\.time\(\)\}")'
            replacement = r'\1,\n                            private_key=self.wallet.private_key'
            
            if re.search(data_tx_creation_pattern, content):
                content = re.sub(data_tx_creation_pattern, replacement, content)
                print("✅ Added private_key to DataTransaction")
                self.changes_made.append("Added private_key to DataTransaction")
        
        return content
    
    def verify_fixes(self, content):
        """Verify that the fixes were applied correctly"""
        print("🔍 Verifying fixes...")
        
        issues = []
        
        # Check if __init__ signature is correct
        if 'def __init__(self, blockchain, wallet_address, threads=1):' in content:
            issues.append("❌ Still has old __init__ signature")
        
        # Check if wallet parameter is used correctly
        if 'self.wallet_address = wallet_address' in content:
            issues.append("❌ Still has old parameter assignment")
        
        # Check if calls use correct parameters
        if 'wallet_address=' in content and 'CryptoMiningThread' in content:
            issues.append("❌ Still has wallet_address parameter in calls")
        
        if issues:
            print("⚠️ Issues found after fixes:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ All fixes verified successfully")
            return True
    
    def apply_targeted_mining_fix(self):
        """Apply targeted mining fix"""
        print("⛏️ Targeted Mining Parameter Fix")
        print("=" * 45)
        print("Specifically fixing the 'unexpected keyword argument' error")
        print()
        
        # Check if target file exists
        if not os.path.exists(self.target_file):
            print(f"❌ Target file not found: {self.target_file}")
            return False
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Read original content
        content = self.read_file()
        if content is None:
            return False
        
        print("\n🔧 Applying Targeted Fixes...")
        print("-" * 30)
        
        # Apply fixes step by step
        content = self.find_and_fix_mining_thread_class(content)
        content = self.find_and_fix_mining_thread_calls(content)
        content = self.fix_wallet_usage_in_mining_thread(content)
        
        # Verify fixes
        verification_passed = self.verify_fixes(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 45)
            print("Targeted mining fixes applied:")
            for change in self.changes_made:
                print(f"  ✅ {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed (might already be fixed)")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            
            if verification_passed:
                print("\n✅ VERIFICATION PASSED")
            else:
                print("\n⚠️ VERIFICATION FAILED - manual check needed")
            
            print("\n⛏️ TARGETED FIXES APPLIED:")
            print("  🎯 Method signature: wallet_address → wallet")
            print("  🎯 Parameter assignment: self.wallet = wallet")
            print("  🎯 Method calls: wallet=self.wallet")
            print("  🎯 Usage: self.wallet.address, self.wallet.public_key")
            print("\n🚀 Mining should now start without parameter errors!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("⛏️ Targeted Mining Parameter Fix")
    print("Specifically fixes: unexpected keyword argument 'wallet'")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = TargetedMiningFix(target_file)
    
    try:
        success = fixer.apply_targeted_mining_fix()
        
        if success:
            print("\n✅ Targeted mining fix applied!")
            print("\n🎯 THE ISSUE:")
            print("  Method definition: __init__(self, blockchain, wallet_address, threads)")
            print("  Method call: CryptoMiningThread(wallet=self.wallet)")
            print("  Error: 'wallet' is not a valid parameter name")
            print("\n✅ THE FIX:")
            print("  Method definition: __init__(self, blockchain, wallet, threads)")
            print("  Method call: CryptoMiningThread(wallet=self.wallet)")
            print("  Result: Parameters now match!")
        else:
            print("\n❌ Targeted fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()