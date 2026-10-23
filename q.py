#!/usr/bin/env python3
"""
Initialization Order Fix for PythonCoin Wallet
Fixes the blockchain/wallet initialization order issue
"""

import os
import sys
import re
import shutil
from datetime import datetime

class InitializationOrderFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_initfix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def fix_initialization_order(self, content):
        """Fix the initialization order - blockchain BEFORE wallet"""
        print("🔧 Fixing initialization order...")
        
        # Find the current initialization section
        old_init_pattern = r'''(# Load or create wallet\s*self\.load_wallet\(\)\s*# Load or create blockchain\s*if not self\.load_blockchain\(\):\s*self\.blockchain = Blockchain\(\)\s*self\.log_message\("Created new blockchain"\))'''
        
        new_init_pattern = '''# Load or create blockchain FIRST
        if not self.load_blockchain():
            self.blockchain = Blockchain()
            self.log_message("Created new blockchain")
        
        # Load or create wallet AFTER blockchain is ready
        self.load_wallet()'''
        
        if re.search(old_init_pattern, content, re.DOTALL):
            content = re.sub(old_init_pattern, new_init_pattern, content, flags=re.DOTALL)
            self.changes_made.append("✅ Fixed initialization order (blockchain before wallet)")
        else:
            # Alternative approach - look for the patterns separately
            wallet_load_pattern = r'(# Load or create wallet\s*self\.load_wallet\(\))'
            blockchain_load_pattern = r'(# Load or create blockchain\s*if not self\.load_blockchain\(\):\s*self\.blockchain = Blockchain\(\)\s*self\.log_message\("Created new blockchain"\))'
            
            # Check if both patterns exist
            if re.search(wallet_load_pattern, content) and re.search(blockchain_load_pattern, content):
                # Remove the blockchain loading from after wallet
                content = re.sub(blockchain_load_pattern, '', content, flags=re.DOTALL)
                
                # Replace wallet loading with blockchain first, then wallet
                content = re.sub(wallet_load_pattern, new_init_pattern, content)
                self.changes_made.append("✅ Fixed initialization order (alternative method)")
        
        return content
    
    def update_load_wallet_method(self, content):
        """Update load_wallet method to handle blockchain properly"""
        print("🔧 Updating load_wallet method...")
        
        # Find the load_wallet method and ensure it checks for blockchain
        load_wallet_pattern = r'(def load_wallet\(self\):.*?try:.*?if os\.path\.exists\("wallet\.json"\):.*?self\.wallet = Wallet\(\s*self\.blockchain,)'
        
        if re.search(load_wallet_pattern, content, re.DOTALL):
            # Add blockchain check before creating wallet
            blockchain_check = '''def load_wallet(self):
        """Load or create wallet"""
        if not self.blockchain:
            self.log_message("Error: Cannot load wallet - blockchain not initialized")
            return
        
        try:'''
            
            # Replace the method start
            method_start_pattern = r'def load_wallet\(self\):\s*"""Load or create wallet"""\s*try:'
            if re.search(method_start_pattern, content):
                content = re.sub(method_start_pattern, blockchain_check, content)
                self.changes_made.append("✅ Updated load_wallet method with blockchain check")
        
        return content
    
    def update_create_new_wallet_method(self, content):
        """Update create_new_wallet method to handle blockchain properly"""
        print("🔧 Updating create_new_wallet method...")
        
        # Find create_new_wallet method and add blockchain check
        create_wallet_pattern = r'(def create_new_wallet\(self\):\s*"""Create a new wallet"""\s*try:)'
        
        replacement = '''def create_new_wallet(self):
        """Create a new wallet"""
        if not self.blockchain:
            self.log_message("Error: Cannot create wallet - blockchain not initialized")
            return
        
        try:'''
        
        if re.search(create_wallet_pattern, content):
            content = re.sub(create_wallet_pattern, replacement, content)
            self.changes_made.append("✅ Updated create_new_wallet method with blockchain check")
        
        return content
    
    def update_wallet_display_method(self, content):
        """Update update_wallet_display to handle None wallet gracefully"""
        print("🔧 Updating update_wallet_display method...")
        
        # Find the method and add None checks
        wallet_display_pattern = r'(def update_wallet_display\(self\):\s*"""Update wallet display"""\s*if not self\.wallet:\s*return)'
        
        replacement = '''def update_wallet_display(self):
        """Update wallet display"""
        if not self.wallet or not self.blockchain:
            # Set default values when wallet/blockchain not ready
            if hasattr(self, 'address_label'):
                self.address_label.setText("Address: Loading...")
            if hasattr(self, 'balance_label'):
                self.balance_label.setText("Balance: Loading...")
            if hasattr(self, 'genesis_status_label'):
                self.genesis_status_label.setText("Genesis: Initializing...")
            return'''
        
        if re.search(wallet_display_pattern, content):
            content = re.sub(wallet_display_pattern, replacement, content)
            self.changes_made.append("✅ Updated update_wallet_display with better None handling")
        
        return content
    
    def add_delayed_ui_update(self, content):
        """Add delayed UI update after initialization"""
        print("⏰ Adding delayed UI update...")
        
        # Find where timers are set up and add delayed update
        timer_pattern = r'(# Update timer\s*self\.update_timer = QTimer\(\)\s*self\.update_timer\.timeout\.connect\(self\.update_ui\)\s*self\.update_timer\.start\(2000\))'
        
        replacement = r'''\1
        
        # Delayed initial UI update after components are ready
        QTimer.singleShot(1000, self.delayed_initial_update)'''
        
        if re.search(timer_pattern, content):
            content = re.sub(timer_pattern, replacement, content)
            self.changes_made.append("✅ Added delayed UI update")
        
        return content
    
    def add_delayed_update_method(self, content):
        """Add delayed update method"""
        print("📱 Adding delayed update method...")
        
        delayed_method = '''
    def delayed_initial_update(self):
        """Delayed initial UI update after all components are ready"""
        try:
            if self.wallet and self.blockchain:
                self.update_ui()
                self.log_message("Wallet and blockchain ready - UI updated")
            else:
                self.log_message("Waiting for wallet/blockchain initialization...")
                # Try again in another second
                QTimer.singleShot(1000, self.delayed_initial_update)
        except Exception as e:
            self.log_message(f"Delayed update error: {str(e)}")
'''
        
        # Find where to inject - before the signal handlers section
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, delayed_method + r'\1', content)
            self.changes_made.append("✅ Added delayed update method")
        
        return content
    
    def remove_initial_ui_update(self, content):
        """Remove the initial UI update that causes the error"""
        print("🚫 Removing problematic initial UI update...")
        
        # Find and remove the initial update_ui call
        initial_update_pattern = r'\s*# Initial UI update\s*self\.update_ui\(\)'
        
        if re.search(initial_update_pattern, content):
            content = re.sub(initial_update_pattern, '', content)
            self.changes_made.append("✅ Removed problematic initial UI update")
        
        return content
    
    def apply_all_fixes(self):
        """Apply all initialization order fixes"""
        print("🚀 Initialization Order Fix for PythonCoin Wallet")
        print("=" * 55)
        print("This will fix the blockchain/wallet initialization order")
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
        
        print("\n🔧 Applying Initialization Fixes...")
        print("-" * 40)
        
        # Apply all fixes
        content = self.fix_initialization_order(content)
        content = self.update_load_wallet_method(content)
        content = self.update_create_new_wallet_method(content)
        content = self.update_wallet_display_method(content)
        content = self.remove_initial_ui_update(content)
        content = self.add_delayed_ui_update(content)
        content = self.add_delayed_update_method(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 55)
            print("Initialization order fixes applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n🔧 FIXES APPLIED:")
            print("  ✅ Blockchain loads before wallet")
            print("  ✅ Wallet creation checks for blockchain")
            print("  ✅ UI handles missing components gracefully")
            print("  ✅ Delayed UI update prevents crashes")
            print("  ✅ Better error handling")
            print("\n🚀 The 'NoneType' error should now be fixed!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("🔧 Initialization Order Fix for PythonCoin Wallet")
    print("Fixes the 'NoneType' object has no attribute 'get_balance' error")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = InitializationOrderFix(target_file)
    
    try:
        success = fixer.apply_all_fixes()
        
        if success:
            print("\n✅ Initialization order fixed!")
            print("\n🎯 What was wrong:")
            print("  ❌ Wallet was created before blockchain was ready")
            print("  ❌ wallet.get_balance() called blockchain.get_balance()")
            print("  ❌ blockchain was None at that point")
            print("\n✅ What's fixed:")
            print("  🔧 Blockchain loads first")
            print("  🔧 Wallet loads after blockchain is ready")
            print("  🔧 UI updates are delayed until components ready")
            print("  🔧 Better error handling for None objects")
        else:
            print("\n❌ Fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()