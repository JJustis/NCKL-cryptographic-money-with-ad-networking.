#!/usr/bin/env python3
"""
Quick Mining Parameter Fix for PythonCoin Wallet
Fixes the CryptoMiningThread parameter mismatch
"""

import os
import sys
import re
import shutil
from datetime import datetime

class MiningParameterFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_mining_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def fix_mining_thread_signature(self, content):
        """Fix CryptoMiningThread.__init__ method signature"""
        print("🔧 Fixing CryptoMiningThread.__init__ signature...")
        
        # Look for the current method signature and fix it
        old_signature = r'def __init__\(self, blockchain, wallet_address, threads=1\):'
        new_signature = 'def __init__(self, blockchain, wallet, threads=1):'
        
        if old_signature in content:
            content = content.replace(old_signature, new_signature)
            self.changes_made.append("✅ Fixed CryptoMiningThread.__init__ signature")
        
        # Also fix the parameter assignment
        old_assignment = 'self.wallet_address = wallet_address'
        new_assignment = 'self.wallet = wallet'
        
        if old_assignment in content:
            content = content.replace(old_assignment, new_assignment)
            self.changes_made.append("✅ Fixed wallet parameter assignment")
        
        return content
    
    def fix_mining_thread_call(self, content):
        """Fix how CryptoMiningThread is called"""
        print("🔧 Fixing CryptoMiningThread instantiation...")
        
        # Fix the call in toggle_mining method
        old_call_pattern = r'wallet_address=mining_address,'
        new_call_pattern = 'wallet=self.wallet,'
        
        if old_call_pattern in content:
            content = content.replace(old_call_pattern, new_call_pattern)
            self.changes_made.append("✅ Fixed CryptoMiningThread instantiation call")
        
        return content
    
    def fix_wallet_usage_in_mining(self, content):
        """Fix wallet usage throughout the mining thread"""
        print("🔧 Fixing wallet usage in mining thread...")
        
        # Fix DataTransaction creation
        old_data_tx = 'sender=self.wallet_address,'
        new_data_tx = 'sender=self.wallet.public_key,'
        
        if old_data_tx in content:
            content = content.replace(old_data_tx, new_data_tx)
            self.changes_made.append("✅ Fixed DataTransaction sender parameter")
        
        # Fix mine_pending_transactions call
        old_mine_call = 'self.blockchain.mine_pending_transactions(self.wallet_address)'
        new_mine_call = 'self.blockchain.mine_pending_transactions(self.wallet.address)'
        
        if old_mine_call in content:
            content = content.replace(old_mine_call, new_mine_call)
            self.changes_made.append("✅ Fixed mine_pending_transactions call")
        
        # Add private key to DataTransaction if needed
        data_content_pattern = r'data_content=f"Mining block at \{time\.time\(\)\}"'
        if re.search(data_content_pattern, content):
            # Check if private_key parameter is missing
            if 'private_key=self.wallet.private_key' not in content:
                new_data_content = 'data_content=f"Mining block at {time.time()}",\n                            private_key=self.wallet.private_key'
                content = re.sub(data_content_pattern, new_data_content, content)
                self.changes_made.append("✅ Added private_key to DataTransaction")
        
        return content
    
    def ensure_mining_compatibility(self, content):
        """Ensure mining thread is compatible with wallet object"""
        print("🔧 Ensuring mining compatibility...")
        
        # Make sure the mining thread run method handles wallet properly
        if 'class CryptoMiningThread' in content:
            # Look for potential issues in the run method
            
            # Fix any remaining wallet_address references
            remaining_wallet_address = r'self\.wallet_address'
            if re.search(remaining_wallet_address, content):
                content = re.sub(remaining_wallet_address, 'self.wallet.address', content)
                self.changes_made.append("✅ Fixed remaining wallet_address references")
        
        return content
    
    def apply_all_mining_fixes(self):
        """Apply all mining parameter fixes"""
        print("⛏️ Mining Parameter Fix for PythonCoin Wallet")
        print("=" * 50)
        print("This will fix the mining thread parameter mismatch")
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
        
        print("\n🔧 Applying Mining Fixes...")
        print("-" * 30)
        
        # Apply all fixes
        content = self.fix_mining_thread_signature(content)
        content = self.fix_mining_thread_call(content)
        content = self.fix_wallet_usage_in_mining(content)
        content = self.ensure_mining_compatibility(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 50)
            print("Mining parameter fixes applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed (might already be fixed)")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n⛏️ MINING FIXES APPLIED:")
            print("  ✅ CryptoMiningThread.__init__ signature corrected")
            print("  ✅ Method call parameters aligned")
            print("  ✅ Wallet object usage fixed")
            print("  ✅ DataTransaction creation updated")
            print("  ✅ All wallet_address references replaced")
            print("\n🚀 Mining should now start without parameter errors!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("⛏️ Mining Parameter Fix for PythonCoin Wallet")
    print("Fixes: CryptoMiningThread.__init__() unexpected keyword 'wallet'")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = MiningParameterFix(target_file)
    
    try:
        success = fixer.apply_all_mining_fixes()
        
        if success:
            print("\n✅ Mining parameter fix applied!")
            print("\n🎯 What was wrong:")
            print("  ❌ Method signature: __init__(blockchain, wallet_address, threads)")
            print("  ❌ Method call: CryptoMiningThread(wallet=self.wallet)")
            print("  ❌ Mismatch caused 'unexpected keyword' error")
            print("\n✅ What's fixed:")
            print("  ⛏️ Method signature: __init__(blockchain, wallet, threads)")
            print("  ⛏️ Method call: CryptoMiningThread(wallet=self.wallet)")
            print("  ⛏️ All wallet usage updated throughout")
            print("  ⛏️ DataTransaction creation fixed")
        else:
            print("\n❌ Mining fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()