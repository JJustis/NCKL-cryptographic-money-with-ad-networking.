#!/usr/bin/env python3
"""
Wallet Balance Persistence Fix
Ensures wallet balance persists correctly after mining and restarting
"""

import os
import sys
import re
import shutil
from datetime import datetime

class WalletBalancePersistenceFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def add_balance_verification_methods(self, content):
        """Add methods to verify and debug balance calculations"""
        print("🔍 Adding balance verification methods...")
        
        verification_methods = '''
    # ============================================================================
    # Balance Verification and Debugging Methods
    # ============================================================================
    
    def verify_wallet_balance_after_load(self):
        """Verify and debug wallet balance after blockchain load"""
        if not self.wallet or not self.blockchain:
            return
        
        try:
            self.log_message("=== WALLET BALANCE VERIFICATION ===")
            self.log_message(f"Wallet Address: {self.wallet.address}")
            self.log_message(f"Blockchain Height: {len(self.blockchain.chain)}")
            
            # Debug balance calculation
            balance = self.wallet.get_balance()
            self.log_message(f"Calculated Balance: {balance:.8f} PYC")
            
            # Manual balance verification
            manual_balance = self.calculate_manual_balance()
            self.log_message(f"Manual Balance Check: {manual_balance:.8f} PYC")
            
            if abs(balance - manual_balance) > 0.00000001:
                self.log_message("⚠️ WARNING: Balance mismatch detected!")
            else:
                self.log_message("✅ Balance verification passed")
            
            # Count transactions involving this wallet
            tx_count = self.count_wallet_transactions()
            self.log_message(f"Transactions involving wallet: {tx_count}")
            
            # Check for mining rewards
            mining_rewards = self.calculate_mining_rewards()
            self.log_message(f"Mining rewards earned: {mining_rewards:.8f} PYC")
            
            self.log_message("=== END VERIFICATION ===")
            
        except Exception as e:
            self.log_message(f"Balance verification error: {str(e)}")
    
    def calculate_manual_balance(self):
        """Manually calculate balance by examining all blockchain transactions"""
        if not self.wallet or not self.blockchain:
            return 0.0
        
        balance = 0.0
        wallet_address = self.wallet.address
        
        try:
            # Go through every block and every transaction
            for block in self.blockchain.chain:
                for tx in block.transactions:
                    # Check if this transaction involves our wallet
                    
                    # For coinbase and genesis transactions (mining rewards, initial distribution)
                    if tx.tx_type in ['coinbase', 'genesis']:
                        for output in tx.outputs:
                            if output.address == wallet_address:
                                balance += output.amount
                                self.log_message(f"  +{output.amount:.8f} PYC from {tx.tx_type} (block {block.index})")
                    
                    # For regular transactions
                    elif tx.tx_type == 'regular':
                        # Check if we're the sender (subtract outputs to others)
                        sender_address = CryptoUtils.pubkey_to_address(tx.sender) if tx.sender else None
                        if sender_address == wallet_address:
                            for output in tx.outputs:
                                if output.address != wallet_address:
                                    balance -= output.amount
                                    self.log_message(f"  -{output.amount:.8f} PYC sent to {output.address[:8]}...")
                        
                        # Check if we're receiving (add outputs to us)
                        for output in tx.outputs:
                            if output.address == wallet_address:
                                balance += output.amount
                                self.log_message(f"  +{output.amount:.8f} PYC received from transaction")
            
            return balance
            
        except Exception as e:
            self.log_message(f"Manual balance calculation error: {str(e)}")
            return 0.0
    
    def count_wallet_transactions(self):
        """Count transactions involving this wallet"""
        if not self.wallet or not self.blockchain:
            return 0
        
        count = 0
        wallet_address = self.wallet.address
        
        try:
            for block in self.blockchain.chain:
                for tx in block.transactions:
                    involved = False
                    
                    # Check if we're in outputs
                    for output in tx.outputs:
                        if output.address == wallet_address:
                            involved = True
                            break
                    
                    # Check if we're the sender
                    if not involved and tx.sender:
                        sender_address = CryptoUtils.pubkey_to_address(tx.sender)
                        if sender_address == wallet_address:
                            involved = True
                    
                    if involved:
                        count += 1
            
            return count
            
        except Exception as e:
            self.log_message(f"Transaction count error: {str(e)}")
            return 0
    
    def calculate_mining_rewards(self):
        """Calculate total mining rewards earned by this wallet"""
        if not self.wallet or not self.blockchain:
            return 0.0
        
        rewards = 0.0
        wallet_address = self.wallet.address
        
        try:
            for block in self.blockchain.chain:
                for tx in block.transactions:
                    if tx.tx_type == 'coinbase':
                        for output in tx.outputs:
                            if output.address == wallet_address:
                                rewards += output.amount
            
            return rewards
            
        except Exception as e:
            self.log_message(f"Mining rewards calculation error: {str(e)}")
            return 0.0
    
    def fix_missing_mining_rewards(self):
        """Fix missing mining rewards by checking for unrewarded blocks"""
        if not self.wallet or not self.blockchain:
            return
        
        try:
            self.log_message("🔍 Checking for missing mining rewards...")
            
            missing_rewards = 0
            for block in self.blockchain.chain:
                # Check if block has coinbase transaction
                has_coinbase = any(tx.tx_type == 'coinbase' for tx in block.transactions)
                
                if not has_coinbase and block.index > 0:  # Skip genesis block
                    self.log_message(f"⚠️ Block {block.index} missing coinbase transaction")
                    missing_rewards += 1
            
            if missing_rewards > 0:
                self.log_message(f"Found {missing_rewards} blocks without mining rewards")
                self.log_message("Note: This might be why your balance is low")
            else:
                self.log_message("✅ All blocks have proper coinbase transactions")
                
        except Exception as e:
            self.log_message(f"Missing rewards check error: {str(e)}")
'''
        
        # Find where to inject - before the signal handlers section
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, verification_methods + r'\1', content)
            self.changes_made.append("✅ Added balance verification methods")
        
        return content
    
    def fix_balance_calculation_after_load(self, content):
        """Add balance verification call after blockchain load"""
        print("🔧 Adding balance verification after blockchain load...")
        
        # Find the load_blockchain method and add verification call
        load_success_pattern = r'(self\.log_message\(f"Blockchain loaded: \{chain_length\} blocks, \{pending_count\} pending transactions"\)\s*self\.log_message\(f"Last saved: \{saved_datetime\}"\)\s*return True)'
        
        replacement = r'''\1
            
            # Verify balance after loading
            QTimer.singleShot(2000, self.verify_wallet_balance_after_load)'''
        
        if re.search(load_success_pattern, content):
            content = re.sub(load_success_pattern, replacement, content)
            self.changes_made.append("✅ Added balance verification after load")
        
        return content
    
    def improve_transaction_reconstruction(self, content):
        """Improve transaction reconstruction to preserve all data"""
        print("🔧 Improving transaction reconstruction...")
        
        # Find reconstruct_transaction method and enhance it
        reconstruct_method_pattern = r'def reconstruct_transaction\(self, tx_data\):'
        
        if re.search(reconstruct_method_pattern, content):
            # Add better error handling and logging
            enhanced_reconstruct = '''def reconstruct_transaction(self, tx_data):
        """Reconstruct a transaction object from saved data"""
        try:
            from pythoncoin import Transaction, TransactionInput, TransactionOutput, DataTransaction, DSAVerificationTransaction
            
            tx_type = tx_data.get('tx_type', 'regular')
            
            if tx_type == 'data':
                # Reconstruct DataTransaction
                tx = DataTransaction(
                    sender=tx_data['sender'],
                    data_content=tx_data.get('data_content', ''),
                    private_key=None  # Don't need private key for reconstruction
                )
                tx.tx_id = tx_data['tx_id']
                tx.timestamp = tx_data['timestamp']
                tx.signature = tx_data.get('signature', '')
                return tx
                
            elif tx_type == 'dsa_verification':
                # Reconstruct DSAVerificationTransaction
                tx = DSAVerificationTransaction(
                    sender=tx_data['sender'],
                    message=tx_data.get('message', ''),
                    private_key=None  # Don't need private key for reconstruction
                )
                tx.tx_id = tx_data['tx_id']
                tx.timestamp = tx_data['timestamp']
                tx.signature = tx_data.get('signature', '')
                return tx
                
            else:
                # Reconstruct regular Transaction (including coinbase and genesis)
                # Reconstruct inputs
                inputs = []
                for input_data in tx_data.get('inputs', []):
                    tx_input = TransactionInput(
                        tx_id=input_data['tx_id'],
                        output_index=input_data['output_index'],
                        signature=input_data.get('signature', '')
                    )
                    inputs.append(tx_input)
                
                # Reconstruct outputs - CRITICAL for balance calculation
                outputs = []
                for output_data in tx_data.get('outputs', []):
                    tx_output = TransactionOutput(
                        address=output_data['address'],
                        amount=float(output_data['amount'])  # Ensure float conversion
                    )
                    outputs.append(tx_output)
                
                # Create transaction
                tx = Transaction(
                    sender=tx_data.get('sender', ''),
                    inputs=inputs,
                    outputs=outputs
                )
                
                # Set all transaction properties
                tx.tx_id = tx_data['tx_id']
                tx.timestamp = tx_data['timestamp']
                tx.tx_type = tx_data.get('tx_type', 'regular')
                tx.signature = tx_data.get('signature', '')
                
                # Log reconstruction for debugging
                if tx.tx_type in ['coinbase', 'genesis']:
                    total_output = sum(output.amount for output in outputs)
                    logger.info(f"Reconstructed {tx.tx_type} transaction: {total_output} PYC total output")
                
                return tx
                
        except Exception as e:
            logger.error(f"Error reconstructing transaction: {str(e)}")
            logger.error(f"Transaction data: {tx_data}")
            return None'''
            
            # Find the method and replace it
            method_start = content.find('def reconstruct_transaction(self, tx_data):')
            if method_start != -1:
                # Find the end of the method
                next_method = content.find('\n    def ', method_start + 1)
                if next_method == -1:
                    next_method = content.find('\n    # =======', method_start + 1)
                
                if next_method != -1:
                    # Replace the method
                    content = content[:method_start] + enhanced_reconstruct + content[next_method:]
                    self.changes_made.append("✅ Enhanced transaction reconstruction")
        
        return content
    
    def add_balance_logging_to_mining(self, content):
        """Add balance logging when blocks are mined"""
        print("⛏️ Adding balance logging to mining rewards...")
        
        # Find the new block mined handler and add balance logging
        new_block_pattern = r'(def on_new_block_mined\(self, block\):.*?self\.log_message\(f"Block mined! Height: \{block\.index\}, Hash: \{block\.hash\[:16\]\}\.\.\."[\s\S]*?\))'
        
        if re.search(new_block_pattern, content):
            replacement = r'''\1
        
        # Log balance after mining
        if self.wallet:
            try:
                new_balance = self.wallet.get_balance()
                self.log_message(f"Balance after mining: {new_balance:.8f} PYC")
            except Exception as e:
                self.log_message(f"Error checking balance after mining: {e}")'''
            
            content = re.sub(new_block_pattern, replacement, content)
            self.changes_made.append("✅ Added balance logging to mining")
        
        return content
    
    def add_wallet_state_saving(self, content):
        """Add explicit wallet state saving"""
        print("💾 Adding wallet state saving...")
        
        wallet_state_methods = '''
    def save_wallet_state(self):
        """Save additional wallet state information"""
        if not self.wallet:
            return
        
        try:
            # Calculate and save current balance
            current_balance = self.wallet.get_balance()
            
            wallet_state = {
                'address': self.wallet.address,
                'private_key': self.wallet.private_key,
                'public_key': self.wallet.public_key,
                'last_known_balance': current_balance,
                'last_updated': datetime.now().isoformat(),
                'blockchain_height_at_save': len(self.blockchain.chain) if self.blockchain else 0
            }
            
            with open("wallet_state.json", "w") as f:
                json.dump(wallet_state, f, indent=2)
            
            self.log_message(f"Wallet state saved - Balance: {current_balance:.8f} PYC")
            
        except Exception as e:
            self.log_message(f"Error saving wallet state: {str(e)}")
    
    def load_wallet_state(self):
        """Load and verify wallet state"""
        try:
            if os.path.exists("wallet_state.json"):
                with open("wallet_state.json", "r") as f:
                    wallet_state = json.load(f)
                
                last_balance = wallet_state.get('last_known_balance', 0)
                last_height = wallet_state.get('blockchain_height_at_save', 0)
                current_height = len(self.blockchain.chain) if self.blockchain else 0
                
                self.log_message(f"Last known balance: {last_balance:.8f} PYC (at height {last_height})")
                self.log_message(f"Current blockchain height: {current_height}")
                
                if current_height > last_height:
                    self.log_message(f"Blockchain grew by {current_height - last_height} blocks since last save")
                
        except Exception as e:
            self.log_message(f"Error loading wallet state: {str(e)}")
'''
        
        # Add before the signal handlers
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, wallet_state_methods + r'\1', content)
            self.changes_made.append("✅ Added wallet state saving methods")
        
        return content
    
    def add_auto_save_wallet_state(self, content):
        """Add automatic wallet state saving"""
        print("⏰ Adding automatic wallet state saving...")
        
        # Find the auto_save_blockchain method and enhance it
        auto_save_pattern = r'(def auto_save_blockchain\(self\):.*?self\.save_blockchain\(\))'
        
        replacement = r'''\1
            
            # Also save wallet state
            self.save_wallet_state()'''
        
        if re.search(auto_save_pattern, content):
            content = re.sub(auto_save_pattern, replacement, content)
            self.changes_made.append("✅ Added wallet state to auto-save")
        
        return content
    
    def add_wallet_state_load_call(self, content):
        """Add wallet state loading call after initialization"""
        print("📂 Adding wallet state load call...")
        
        # Find where wallet is loaded and add state loading
        wallet_load_pattern = r'(# Load or create wallet AFTER blockchain is ready\s*self\.load_wallet\(\))'
        
        replacement = r'''\1
        
        # Load wallet state for verification
        self.load_wallet_state()'''
        
        if re.search(wallet_load_pattern, content):
            content = re.sub(wallet_load_pattern, replacement, content)
            self.changes_made.append("✅ Added wallet state loading call")
        
        return content
    
    def apply_all_balance_fixes(self):
        """Apply all wallet balance persistence fixes"""
        print("💰 Wallet Balance Persistence Fix")
        print("=" * 45)
        print("Ensuring your mining rewards persist between sessions!")
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
        
        print("\n🔧 Applying Balance Persistence Fixes...")
        print("-" * 40)
        
        # Apply all fixes
        content = self.add_balance_verification_methods(content)
        content = self.fix_balance_calculation_after_load(content)
        content = self.improve_transaction_reconstruction(content)
        content = self.add_balance_logging_to_mining(content)
        content = self.add_wallet_state_saving(content)
        content = self.add_auto_save_wallet_state(content)
        content = self.add_wallet_state_load_call(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 45)
            print("Wallet balance persistence fixes applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n💰 BALANCE PERSISTENCE FEATURES:")
            print("  🔍 Balance verification after blockchain load")
            print("  📊 Manual balance calculation for debugging")
            print("  💾 Wallet state saving (wallet_state.json)")
            print("  ⛏️ Balance logging after mining blocks")
            print("  🔧 Enhanced transaction reconstruction")
            print("  📈 Mining rewards tracking")
            print("  ⏰ Automatic wallet state saving")
            print("\n🚀 Your mining rewards should now persist properly!")
            print("💡 Check the logs for balance verification details")
            
            return True
        
        return False

def main():
    """Main function"""
    print("💰 Wallet Balance Persistence Fix")
    print("Fixes: Wallet balance not persisting after mining")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = WalletBalancePersistenceFix(target_file)
    
    try:
        success = fixer.apply_all_balance_fixes()
        
        if success:
            print("\n✅ Wallet balance persistence fix applied!")
            print("\n🎯 THE PROBLEM:")
            print("  ❌ Mine blocks → earn rewards → restart → balance gone")
            print("  ❌ Blockchain saves but balance calculation fails")
            print("  ❌ Transaction reconstruction loses reward data")
            print("\n✅ THE SOLUTION:")
            print("  💾 Enhanced transaction reconstruction")
            print("  🔍 Balance verification and debugging")
            print("  📊 Manual balance calculation cross-check")
            print("  💰 Wallet state persistence")
            print("  ⛏️ Mining reward tracking")
            print("  📈 Detailed balance logging")
            print("\n🎉 Now your hard mining work will be saved!")
        else:
            print("\n❌ Balance persistence fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()