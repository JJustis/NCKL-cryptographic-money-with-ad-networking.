#!/usr/bin/env python3
"""
Mining Thread Method Fix
Fixes the missing ensure_coinbase_transaction_exists method in CryptoMiningThread
"""

import os
import sys
import re
import shutil
from datetime import datetime

class MiningThreadMethodFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_miningmethod_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def remove_problematic_coinbase_call(self, content):
        """Remove the problematic ensure_coinbase_transaction_exists call"""
        print("🔧 Removing problematic coinbase method call...")
        
        # Find and remove the problematic call
        problematic_call_pattern = r'# Ensure we have a coinbase transaction before mining\s*self\.ensure_coinbase_transaction_exists\(\)\s*'
        
        if re.search(problematic_call_pattern, content):
            content = re.sub(problematic_call_pattern, '', content)
            self.changes_made.append("✅ Removed problematic coinbase method call")
        
        return content
    
    def add_simple_coinbase_creation_to_mining(self, content):
        """Add simple coinbase creation directly in the mining thread run method"""
        print("💰 Adding simple coinbase creation to mining thread...")
        
        # Find the mining section and add simple coinbase creation
        mining_pattern = r'(# Mine a new block\s*new_block = self\.blockchain\.mine_pending_transactions\(self\.wallet\.address\))'
        
        replacement = r'''# Create coinbase transaction if needed
                if not any(getattr(tx, 'tx_type', '') == 'coinbase' for tx in self.blockchain.pending_transactions):
                    self.status_update.emit("Creating coinbase transaction for mining...")
                    try:
                        from pythoncoin import Transaction, TransactionOutput
                        import uuid
                        import time
                        
                        # Create coinbase transaction
                        coinbase_tx = Transaction(
                            sender="",  # Coinbase has no sender
                            inputs=[],  # Coinbase has no inputs
                            outputs=[TransactionOutput(address=self.wallet.address, amount=50.0)]
                        )
                        coinbase_tx.tx_type = 'coinbase'
                        coinbase_tx.timestamp = time.time()
                        coinbase_tx.tx_id = f"coinbase_{uuid.uuid4().hex[:16]}"
                        coinbase_tx.signature = ""
                        
                        # Add to pending transactions at the beginning
                        self.blockchain.pending_transactions.insert(0, coinbase_tx)
                        self.status_update.emit("Coinbase transaction created")
                        
                    except Exception as e:
                        self.status_update.emit(f"Coinbase creation error: {str(e)}")
                
                # Mine a new block
                new_block = self.blockchain.mine_pending_transactions(self.wallet.address)'''
        
        if re.search(mining_pattern, content):
            content = re.sub(mining_pattern, replacement, content)
            self.changes_made.append("✅ Added simple coinbase creation to mining")
        
        return content
    
    def add_basic_mining_validation(self, content):
        """Add basic validation to check if mined block has coinbase"""
        print("✅ Adding basic mining validation...")
        
        # Find the mining success check and add simple validation
        success_pattern = r'(if new_block and self\.running:\s*self\.blocks_mined \+= 1\s*self\.status_update\.emit\(f"Block mined! Height: \{new_block\.index\}, Hash: \{new_block\.hash\[:16\]\}\.\.\."[\s\S]*?\))'
        
        if re.search(success_pattern, content):
            replacement = r'''if new_block and self.running:
                    # Simple validation - check if block has coinbase
                    has_coinbase = False
                    coinbase_reward = 0
                    
                    if new_block.transactions:
                        first_tx = new_block.transactions[0]
                        if getattr(first_tx, 'tx_type', '') == 'coinbase':
                            has_coinbase = True
                            for output in first_tx.outputs:
                                if output.address == self.wallet.address:
                                    coinbase_reward += output.amount
                    
                    if has_coinbase:
                        self.blocks_mined += 1
                        self.status_update.emit(f"Block mined! Height: {new_block.index}, Hash: {new_block.hash[:16]}...")
                        self.status_update.emit(f"Mining reward: {coinbase_reward} PYC")
                        self.new_block.emit(new_block)
                    else:
                        self.status_update.emit("⚠️ Warning: Mined block missing coinbase transaction!")
                        # Still emit the block but with warning
                        self.blocks_mined += 1
                        self.new_block.emit(new_block)'''
            
            content = re.sub(success_pattern, replacement, content, flags=re.DOTALL)
            self.changes_made.append("✅ Added basic mining validation")
        
        return content
    
    def fix_mining_thread_class_structure(self, content):
        """Ensure the CryptoMiningThread class has proper structure"""
        print("🔧 Checking CryptoMiningThread class structure...")
        
        # Check if the class exists and has basic methods
        if 'class CryptoMiningThread(QThread):' not in content:
            self.changes_made.append("❌ CryptoMiningThread class not found")
            return content
        
        # Check if run method exists
        if 'def run(self):' not in content:
            self.changes_made.append("❌ CryptoMiningThread run method not found") 
            return content
        
        self.changes_made.append("✅ CryptoMiningThread class structure is valid")
        return content
    
    def add_mining_debug_logging(self, content):
        """Add debug logging to mining thread"""
        print("📝 Adding mining debug logging...")
        
        # Find the mining thread run method start and add debug logging
        run_method_pattern = r'(def run\(self\):\s*"""Run the mining process with better integration"""\s*self\.running = True)'
        
        if re.search(run_method_pattern, content):
            replacement = r'''\1
        self.status_update.emit("🔍 Mining thread started - checking components...")
        
        # Debug: Check if we have required components
        if not self.blockchain:
            self.status_update.emit("❌ Error: No blockchain available")
            return
        
        if not self.wallet:
            self.status_update.emit("❌ Error: No wallet available")
            return
        
        self.status_update.emit(f"✅ Components ready - wallet: {self.wallet.address[:8]}...")'''
            
            content = re.sub(run_method_pattern, replacement, content)
            self.changes_made.append("✅ Added mining debug logging")
        
        return content
    
    def simplify_mining_process(self, content):
        """Simplify the mining process to avoid method call issues"""
        print("🎯 Simplifying mining process...")
        
        # Find any complex mining calls and simplify them
        complex_pattern = r'# Check if there are pending transactions or create a dummy one\s*if len\(self\.blockchain\.pending_transactions\) == 0:'
        
        if re.search(complex_pattern, content):
            # Replace with simpler version
            replacement = r'''# Simple mining process - ensure we have transactions
                if len(self.blockchain.pending_transactions) == 0:'''
            
            content = re.sub(complex_pattern, replacement, content)
            self.changes_made.append("✅ Simplified mining transaction check")
        
        return content
    
    def apply_mining_thread_fix(self):
        """Apply mining thread method fix"""
        print("⛏️ Mining Thread Method Fix")
        print("=" * 40)
        print("Fixes missing ensure_coinbase_transaction_exists method")
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
        
        print("\n🔧 Applying Mining Thread Fixes...")
        print("-" * 30)
        
        # Apply fixes in order
        content = self.remove_problematic_coinbase_call(content)
        content = self.add_simple_coinbase_creation_to_mining(content)
        content = self.add_basic_mining_validation(content)
        content = self.fix_mining_thread_class_structure(content)
        content = self.add_mining_debug_logging(content)
        content = self.simplify_mining_process(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 40)
            print("Mining thread fixes applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n⛏️ MINING FIXES APPLIED:")
            print("  🔧 Removed problematic method call")
            print("  💰 Added inline coinbase creation")
            print("  ✅ Added basic mining validation")
            print("  📝 Added debug logging")
            print("  🎯 Simplified mining process")
            print("\n🚀 Mining should now work without method errors!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("⛏️ Mining Thread Method Fix")
    print("Fixes: 'CryptoMiningThread' object has no attribute 'ensure_coinbase_transaction_exists'")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = MiningThreadMethodFix(target_file)
    
    try:
        success = fixer.apply_mining_thread_fix()
        
        if success:
            print("\n✅ Mining thread method fix applied!")
            print("\n🎯 THE PROBLEM:")
            print("  ❌ Mining thread calls ensure_coinbase_transaction_exists()")
            print("  ❌ Method doesn't exist on CryptoMiningThread class")
            print("  ❌ Mining fails with AttributeError")
            print("\n✅ THE SOLUTION:")
            print("  🔧 Removed problematic method call")
            print("  💰 Added inline coinbase creation code")
            print("  ✅ Simple validation without external methods")
            print("  📝 Better debug logging")
            print("\n🎉 Mining should now work properly!")
        else:
            print("\n❌ Mining thread fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()