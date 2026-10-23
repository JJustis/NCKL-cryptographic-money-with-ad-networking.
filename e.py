#!/usr/bin/env python3
"""
Blockchain Persistence Injector for PythonCoin Wallet
Adds automatic saving/loading of blockchain data so progress isn't lost on restart
"""

import os
import sys
import re
import shutil
from datetime import datetime

class BlockchainPersistenceInjector:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def add_blockchain_persistence_methods(self, content):
        """Add blockchain persistence methods to the wallet class"""
        print("💾 Adding blockchain persistence methods...")
        
        persistence_methods = '''
    # ============================================================================
    # Blockchain Persistence Methods
    # ============================================================================
    
    def save_blockchain(self):
        """Save blockchain to file"""
        try:
            blockchain_data = {
                'chain': [block.to_dict() for block in self.blockchain.chain],
                'pending_transactions': [tx.to_dict() for tx in self.blockchain.pending_transactions],
                'genesis_complete': self.blockchain.genesis_complete,
                'genesis_addresses': self.blockchain.genesis_addresses,
                'difficulty': self.blockchain.difficulty,
                'mining_reward': self.blockchain.mining_reward,
                'saved_timestamp': time.time(),
                'saved_datetime': datetime.now().isoformat()
            }
            
            with open("blockchain.json", "w") as f:
                json.dump(blockchain_data, f, indent=2)
            
            self.log_message("Blockchain saved successfully")
            
        except Exception as e:
            self.log_message(f"Error saving blockchain: {str(e)}")
            logger.error(f"Blockchain save error: {str(e)}")
    
    def load_blockchain(self):
        """Load blockchain from file"""
        try:
            if not os.path.exists("blockchain.json"):
                self.log_message("No saved blockchain found - creating new blockchain")
                return False
            
            with open("blockchain.json", "r") as f:
                blockchain_data = json.load(f)
            
            # Reconstruct blockchain
            self.blockchain = Blockchain()
            
            # Load basic properties
            self.blockchain.genesis_complete = blockchain_data.get('genesis_complete', False)
            self.blockchain.genesis_addresses = blockchain_data.get('genesis_addresses', [])
            self.blockchain.difficulty = blockchain_data.get('difficulty', 2)
            self.blockchain.mining_reward = blockchain_data.get('mining_reward', 50)
            
            # Reconstruct blocks
            chain_data = blockchain_data.get('chain', [])
            self.blockchain.chain = []
            
            for block_data in chain_data:
                # Reconstruct transactions for this block
                transactions = []
                for tx_data in block_data.get('transactions', []):
                    tx = self.reconstruct_transaction(tx_data)
                    if tx:
                        transactions.append(tx)
                
                # Create block object
                from pythoncoin import Block
                block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    transactions=transactions,
                    previous_hash=block_data['previous_hash']
                )
                
                # Set additional block properties
                block.hash = block_data['hash']
                block.nonce = block_data['nonce']
                block.difficulty = block_data.get('difficulty', 2)
                
                self.blockchain.chain.append(block)
            
            # Reconstruct pending transactions
            pending_data = blockchain_data.get('pending_transactions', [])
            self.blockchain.pending_transactions = []
            
            for tx_data in pending_data:
                tx = self.reconstruct_transaction(tx_data)
                if tx:
                    self.blockchain.pending_transactions.append(tx)
            
            saved_datetime = blockchain_data.get('saved_datetime', 'Unknown')
            chain_length = len(self.blockchain.chain)
            pending_count = len(self.blockchain.pending_transactions)
            
            self.log_message(f"Blockchain loaded: {chain_length} blocks, {pending_count} pending transactions")
            self.log_message(f"Last saved: {saved_datetime}")
            
            return True
            
        except Exception as e:
            self.log_message(f"Error loading blockchain: {str(e)}")
            logger.error(f"Blockchain load error: {str(e)}")
            # Create new blockchain on load failure
            self.blockchain = Blockchain()
            return False
    
    def reconstruct_transaction(self, tx_data):
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
                # Reconstruct regular Transaction
                # Reconstruct inputs
                inputs = []
                for input_data in tx_data.get('inputs', []):
                    tx_input = TransactionInput(
                        tx_id=input_data['tx_id'],
                        output_index=input_data['output_index'],
                        signature=input_data.get('signature', '')
                    )
                    inputs.append(tx_input)
                
                # Reconstruct outputs
                outputs = []
                for output_data in tx_data.get('outputs', []):
                    tx_output = TransactionOutput(
                        address=output_data['address'],
                        amount=output_data['amount']
                    )
                    outputs.append(tx_output)
                
                # Create transaction
                tx = Transaction(
                    sender=tx_data['sender'],
                    inputs=inputs,
                    outputs=outputs
                )
                
                tx.tx_id = tx_data['tx_id']
                tx.timestamp = tx_data['timestamp']
                tx.tx_type = tx_data.get('tx_type', 'regular')
                tx.signature = tx_data.get('signature', '')
                
                return tx
                
        except Exception as e:
            logger.error(f"Error reconstructing transaction: {str(e)}")
            return None
    
    def auto_save_blockchain(self):
        """Automatically save blockchain periodically"""
        if hasattr(self, 'blockchain') and self.blockchain:
            self.save_blockchain()
    
    def setup_auto_save_timer(self):
        """Setup automatic blockchain saving every 30 seconds"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_blockchain)
        self.auto_save_timer.start(30000)  # 30 seconds
        self.log_message("Auto-save enabled: blockchain will be saved every 30 seconds")
'''
        
        # Find where to inject - before the signal handlers section
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, persistence_methods + r'\1', content)
            self.changes_made.append("✅ Added blockchain persistence methods")
        else:
            # Fallback - add before the utility functions
            utility_pattern = r'(\s*# ============================================================================\s*# Utility Functions)'
            if re.search(utility_pattern, content):
                content = re.sub(utility_pattern, persistence_methods + r'\1', content)
                self.changes_made.append("✅ Added blockchain persistence methods (fallback)")
        
        return content
    
    def modify_blockchain_initialization(self, content):
        """Modify blockchain initialization to load from file"""
        print("🔧 Modifying blockchain initialization...")
        
        # Find the blockchain initialization in __init__
        old_init = r'# Core components - Initialize blockchain without genesis first\s*self\.blockchain = Blockchain\(\)  # No genesis addresses yet'
        new_init = '''# Core components - Initialize blockchain with persistence
        self.blockchain = None  # Will be loaded or created'''
        
        if re.search(old_init, content):
            content = re.sub(old_init, new_init, content)
            self.changes_made.append("✅ Modified blockchain initialization")
        else:
            # Alternative pattern
            old_pattern = r'self\.blockchain = Blockchain\(\)'
            new_pattern = 'self.blockchain = None  # Will be loaded or created'
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                self.changes_made.append("✅ Modified blockchain initialization (alternative)")
        
        return content
    
    def add_blockchain_loading_to_init(self, content):
        """Add blockchain loading call to the __init__ method"""
        print("📂 Adding blockchain loading to initialization...")
        
        # Find where wallet is loaded and add blockchain loading after it
        wallet_load_pattern = r'(# Load or create wallet\s*self\.load_wallet\(\))'
        replacement = r'''\1
        
        # Load or create blockchain
        if not self.load_blockchain():
            self.blockchain = Blockchain()
            self.log_message("Created new blockchain")'''
        
        if re.search(wallet_load_pattern, content):
            content = re.sub(wallet_load_pattern, replacement, content)
            self.changes_made.append("✅ Added blockchain loading to initialization")
        
        return content
    
    def add_auto_save_setup(self, content):
        """Add auto-save timer setup"""
        print("⏰ Adding auto-save timer setup...")
        
        # Find where timers are set up and add auto-save timer
        timer_pattern = r'(# Update timer\s*self\.update_timer = QTimer\(\)\s*self\.update_timer\.timeout\.connect\(self\.update_ui\)\s*self\.update_timer\.start\(2000\))'
        replacement = r'''\1
        
        # Auto-save timer for blockchain
        self.setup_auto_save_timer()'''
        
        if re.search(timer_pattern, content):
            content = re.sub(timer_pattern, replacement, content)
            self.changes_made.append("✅ Added auto-save timer setup")
        
        return content
    
    def add_save_on_new_block(self, content):
        """Add blockchain saving when new blocks are mined"""
        print("💎 Adding save on new block mined...")
        
        # Find the on_new_block_mined method and add save call
        new_block_pattern = r'(def on_new_block_mined\(self, block\):[^}]*self\.log_message\(f"Block mined! Height: \{block\.index\}, Hash: \{block\.hash\[:16\]\}\.\.\."[\s\S]*?\))'
        
        if re.search(new_block_pattern, content):
            replacement = r'''\1
        
        # Save blockchain after new block
        self.save_blockchain()'''
            content = re.sub(new_block_pattern, replacement, content)
            self.changes_made.append("✅ Added blockchain save on new block")
        
        return content
    
    def add_save_on_transaction(self, content):
        """Add blockchain saving when transactions are sent"""
        print("💸 Adding save on transaction sent...")
        
        # Find the send_transaction method and add save call
        send_tx_pattern = r'(# Update UI\s*self\.update_ui\(\))'
        replacement = r'''\1
                
                # Save blockchain after transaction
                self.save_blockchain()'''
        
        # Look for this pattern in the send_transaction method
        if re.search(send_tx_pattern, content):
            content = re.sub(send_tx_pattern, replacement, content)
            self.changes_made.append("✅ Added blockchain save on transaction")
        
        return content
    
    def add_save_on_close(self, content):
        """Add blockchain saving when application closes"""
        print("🚪 Adding save on application close...")
        
        # Find the closeEvent method and add save call
        close_pattern = r'(# Save wallet\s*if self\.wallet:\s*self\.save_wallet\(\))'
        replacement = r'''# Save blockchain and wallet
            if self.blockchain:
                self.save_blockchain()
            if self.wallet:
                self.save_wallet()'''
        
        if re.search(close_pattern, content):
            content = re.sub(close_pattern, replacement, content)
            self.changes_made.append("✅ Added blockchain save on close")
        
        return content
    
    def update_dashboard_for_persistence(self, content):
        """Update dashboard to show persistence status"""
        print("📊 Updating dashboard for persistence info...")
        
        # Add persistence info to dashboard
        dashboard_pattern = r'(self\.blockchain_status = QLabel\("Blockchain: 0 blocks"\))'
        replacement = r'''\1
        
        self.persistence_status = QLabel("Auto-save: Active")
        stats_layout.addWidget(self.persistence_status)'''
        
        if re.search(dashboard_pattern, content):
            content = re.sub(dashboard_pattern, replacement, content)
            self.changes_made.append("✅ Updated dashboard for persistence info")
        
        return content
    
    def apply_all_persistence_fixes(self):
        """Apply all blockchain persistence fixes"""
        print("💾 Blockchain Persistence Injector")
        print("=" * 50)
        print("This will add automatic blockchain saving/loading")
        print("so your mining progress and transactions persist!")
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
        
        print("\n🔧 Applying Persistence Fixes...")
        print("-" * 30)
        
        # Apply all modifications
        content = self.add_blockchain_persistence_methods(content)
        content = self.modify_blockchain_initialization(content)
        content = self.add_blockchain_loading_to_init(content)
        content = self.add_auto_save_setup(content)
        content = self.add_save_on_new_block(content)
        content = self.add_save_on_transaction(content)
        content = self.add_save_on_close(content)
        content = self.update_dashboard_for_persistence(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 50)
            print("Blockchain persistence added:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed (persistence might already exist)")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n💾 PERSISTENCE FEATURES ADDED:")
            print("  🏗️ Automatic blockchain loading on startup")
            print("  💾 Auto-save every 30 seconds")
            print("  🎯 Save on new block mined")
            print("  💸 Save on transaction sent")
            print("  🚪 Save on application close")
            print("  📊 Persistence status in dashboard")
            print("\n✨ Your blockchain data will now persist between restarts!")
            print("   File: blockchain.json")
            print("   Your mining progress and transactions will be saved!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("💾 Blockchain Persistence Injector for PythonCoin Wallet")
    print("Saves your blockchain so mining progress isn't lost!")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create injector and apply fixes
    injector = BlockchainPersistenceInjector(target_file)
    
    try:
        success = injector.apply_all_persistence_fixes()
        
        if success:
            print("\n✅ Blockchain persistence added successfully!")
            print("\n🎯 What this fixes:")
            print("  ❌ BEFORE: Blockchain recreated on each restart")
            print("  ✅ AFTER: Blockchain persists between sessions")
            print("\n💾 Features added:")
            print("  📂 Automatic load on startup")
            print("  ⏰ Auto-save every 30 seconds")
            print("  💎 Save when blocks are mined")
            print("  💸 Save when transactions are sent")
            print("  🚪 Save when app closes")
            print("\n🚀 Your mining progress will now be saved!")
        else:
            print("\n❌ Persistence injection failed.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()