#!/usr/bin/env python3
"""
Complete Mining Thread Fixer - Fixes the missing CryptoMiningThread issue
"""

import os
import re
import sys

class MiningThreadFixer:
    def __init__(self, source_file="pyqt2_enhanced.py"):
        self.source_file = source_file
        self.source_content = ""
        self.fixed_content = ""
        
    def load_and_fix(self):
        """Load file and apply all fixes"""
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.source_content = f.read()
            print(f"✅ Loaded: {self.source_file}")
            
            # Start with source content
            self.fixed_content = self.source_content
            
            # Apply all fixes
            self.fix_missing_mining_thread()
            self.fix_imports()
            self.fix_mining_initialization()
            self.ensure_mining_methods()
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def fix_missing_mining_thread(self):
        """Add the missing CryptoMiningThread class"""
        
        if 'class CryptoMiningThread' not in self.fixed_content:
            print("📝 Adding CryptoMiningThread class...")
            
            # Find where to insert the mining thread (after other mining classes)
            insert_point = self.fixed_content.find('class EnhancedBlockchain:')
            if insert_point == -1:
                insert_point = self.fixed_content.find('# === END MINING CLASSES ===')
            if insert_point == -1:
                # Find PyQt imports and insert after
                insert_point = self.fixed_content.find('from PyQt5.QtGui import')
                if insert_point != -1:
                    insert_point = self.fixed_content.find('\n\n', insert_point)
            
            if insert_point != -1:
                mining_thread_class = '''
class CryptoMiningThread(QThread):
    """Enhanced mining thread with full blockchain integration"""
    
    status_update = pyqtSignal(str)
    block_mined = pyqtSignal(dict)
    hashrate_update = pyqtSignal(float)
    balance_update = pyqtSignal(float)
    
    def __init__(self, blockchain, wallet, parent=None):
        super().__init__(parent)
        self.blockchain = blockchain
        self.wallet = wallet
        self.mining = False
        self.blocks_mined = 0
        self.total_nonces = 0
        self.start_time = 0
        self.daemon = True
        
    def start_mining(self):
        """Start mining process"""
        self.mining = True
        self.start_time = time.time()
        self.status_update.emit("⛏️ Mining started")
        self.start()
        
    def stop_mining(self):
        """Stop mining process"""
        self.mining = False
        self.status_update.emit("🛑 Mining stopped")
        
    def run(self):
        """Main mining loop"""
        if not self.blockchain or not self.wallet:
            self.status_update.emit("❌ Missing blockchain or wallet")
            return
            
        # Wait for genesis block
        while not self.blockchain.genesis_complete and self.mining:
            self.status_update.emit("⏳ Waiting for genesis block...")
            self.msleep(1000)
        
        self.status_update.emit("⛏️ Mining operations started")
        
        while self.mining:
            try:
                # Mine a new block
                new_block = self.blockchain.mine_pending_transactions(self.wallet.address)
                
                if new_block and self.mining:
                    self.blocks_mined += 1
                    self.total_nonces += new_block.nonce
                    
                    # Calculate hashrate
                    elapsed_time = time.time() - self.start_time
                    if elapsed_time > 0:
                        hashrate = self.total_nonces / elapsed_time
                        self.hashrate_update.emit(hashrate)
                    
                    # Emit signals
                    self.status_update.emit(f"🎉 Block {new_block.index} mined! Hash: {new_block.hash[:16]}...")
                    self.block_mined.emit({"index": new_block.index, "hash": new_block.hash, "nonce": new_block.nonce})
                    self.balance_update.emit(self.wallet.get_balance())
                    
                    # Brief pause between blocks
                    self.msleep(2000)
                else:
                    self.status_update.emit("⚠️ Mining failed, retrying...")
                    self.msleep(5000)
                    
            except Exception as e:
                self.status_update.emit(f"❌ Mining error: {str(e)}")
                self.msleep(5000)
    
    def get_mining_stats(self):
        """Get mining statistics"""
        elapsed_time = time.time() - self.start_time if self.start_time > 0 else 1
        hashrate = self.total_nonces / elapsed_time if elapsed_time > 0 else 0
        
        return {
            'blocks_mined': self.blocks_mined,
            'total_nonces': self.total_nonces,
            'hashrate': hashrate,
            'elapsed_time': elapsed_time,
            'mining': self.mining
        }

'''
                
                self.fixed_content = (
                    self.fixed_content[:insert_point] + 
                    mining_thread_class + 
                    self.fixed_content[insert_point:]
                )
                print("✅ Added CryptoMiningThread class")
            else:
                print("❌ Could not find insertion point for mining thread")
                return False
        else:
            print("ℹ️ CryptoMiningThread already exists")
        
        return True
    
    def fix_imports(self):
        """Ensure all necessary imports are present"""
        
        imports_to_add = []
        
        # Check for required imports
        if 'from PyQt5.QtCore import' in self.fixed_content and 'QThread' not in self.fixed_content:
            # Add QThread to existing PyQt5.QtCore import
            qtcore_pattern = r'from PyQt5\.QtCore import \((.*?)\)'
            qtcore_match = re.search(qtcore_pattern, self.fixed_content, re.DOTALL)
            
            if qtcore_match:
                current_imports = qtcore_match.group(1)
                if 'QThread' not in current_imports:
                    new_imports = current_imports.rstrip() + ', QThread'
                    self.fixed_content = self.fixed_content.replace(
                        qtcore_match.group(0),
                        f'from PyQt5.QtCore import ({new_imports})'
                    )
                    print("✅ Added QThread to imports")
        
        # Ensure pyqtSignal is imported
        if 'pyqtSignal' not in self.fixed_content:
            qtcore_pattern = r'from PyQt5\.QtCore import \((.*?)\)'
            qtcore_match = re.search(qtcore_pattern, self.fixed_content, re.DOTALL)
            
            if qtcore_match:
                current_imports = qtcore_match.group(1)
                if 'pyqtSignal' not in current_imports:
                    new_imports = current_imports.rstrip() + ', pyqtSignal'
                    self.fixed_content = self.fixed_content.replace(
                        qtcore_match.group(0),
                        f'from PyQt5.QtCore import ({new_imports})'
                    )
                    print("✅ Added pyqtSignal to imports")
        
        return True
    
    def fix_mining_initialization(self):
        """Fix mining initialization in the main class"""
        
        # Ensure mining variables are initialized
        if 'self.mining_thread = None' not in self.fixed_content:
            print("📝 Adding mining initialization...")
            
            # Find the __init__ method and add mining initialization
            init_pattern = r'(def __init__\(self\):.*?)(self\.show\(\))'
            init_match = re.search(init_pattern, self.fixed_content, re.DOTALL)
            
            if init_match:
                mining_init = '''
            # Initialize mining system
            self.mining_thread = None
            self.mining_enabled = False
            self.total_blocks_mined = 0
            log_message("⛏️ Mining system initialized")
            '''
                
                insert_point = init_match.start(2)
                self.fixed_content = (
                    self.fixed_content[:insert_point] + 
                    mining_init + 
                    self.fixed_content[insert_point:]
                )
                print("✅ Added mining initialization")
        
        return True
    
    def ensure_mining_methods(self):
        """Ensure all mining methods exist"""
        
        # Check if mining methods exist, if not add them
        mining_methods_needed = [
            'def start_mining(self):',
            'def stop_mining(self):',
            'def on_mining_status(self, message):',
            'def on_block_mined(self, block_data):',
            'def on_hashrate_update(self, hashrate):'
        ]
        
        missing_methods = []
        for method in mining_methods_needed:
            if method not in self.fixed_content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"📝 Adding {len(missing_methods)} missing mining methods...")
            
            complete_mining_methods = '''
    def start_mining(self):
        """Start the mining process"""
        try:
            if hasattr(self, 'mining_thread') and self.mining_thread and self.mining_thread.mining:
                self.log_message("⚠️ Mining already running")
                return
            
            if not hasattr(self, 'blockchain') or not self.blockchain:
                self.log_message("❌ No blockchain available")
                return
            
            # Create genesis block if needed
            if not self.blockchain.genesis_complete:
                self.blockchain.create_genesis_block([self.wallet.address])
                self.log_message("✅ Genesis block created")
                
                # Update UI
                if hasattr(self, 'genesis_status_label'):
                    self.genesis_status_label.setText("✅ Created")
            
            # Create mining thread
            self.mining_thread = CryptoMiningThread(self.blockchain, self.wallet, self)
            self.mining_thread.status_update.connect(self.on_mining_status)
            self.mining_thread.block_mined.connect(self.on_block_mined)
            self.mining_thread.hashrate_update.connect(self.on_hashrate_update)
            self.mining_thread.balance_update.connect(self.on_balance_update)
            
            self.mining_thread.start_mining()
            self.mining_enabled = True
            self.log_message("🚀 Mining started!")
            
            # Update UI
            if hasattr(self, 'start_mining_btn'):
                self.start_mining_btn.setText("🛑 Stop Mining")
                self.start_mining_btn.clicked.disconnect()
                self.start_mining_btn.clicked.connect(self.stop_mining)
            
            if hasattr(self, 'mining_status_label'):
                self.mining_status_label.setText("Status: Mining ⛏️")
            
        except Exception as e:
            self.log_message(f"❌ Mining start error: {e}")
    
    def stop_mining(self):
        """Stop the mining process"""
        try:
            if hasattr(self, 'mining_thread') and self.mining_thread:
                self.mining_thread.stop_mining()
                self.mining_thread.wait(3000)
                self.mining_thread = None
            
            self.mining_enabled = False
            self.log_message("🛑 Mining stopped")
            
            # Update UI
            if hasattr(self, 'start_mining_btn'):
                self.start_mining_btn.setText("🚀 Start Mining")
                self.start_mining_btn.clicked.disconnect()
                self.start_mining_btn.clicked.connect(self.start_mining)
            
            if hasattr(self, 'mining_status_label'):
                self.mining_status_label.setText("Status: Stopped")
            
        except Exception as e:
            self.log_message(f"❌ Mining stop error: {e}")
    
    def on_mining_status(self, message):
        """Handle mining status updates"""
        self.log_message(f"⛏️ {message}")
        if hasattr(self, 'mining_status_label'):
            # Clean up the message for display
            clean_message = message.replace("⛏️ ", "").replace("🎉 ", "").replace("⚠️ ", "").replace("❌ ", "")
            self.mining_status_label.setText(f"Status: {clean_message}")
    
    def on_block_mined(self, block_data):
        """Handle block mined event"""
        try:
            self.total_blocks_mined += 1
            self.log_message(f"🎉 Block {block_data['index']} mined! Reward: 50.0 PYC")
            
            # Update UI
            if hasattr(self, 'blocks_mined_label'):
                self.blocks_mined_label.setText(f"Blocks Mined: {self.total_blocks_mined}")
            
            if hasattr(self, 'total_earnings_label'):
                total_earned = self.total_blocks_mined * 50.0
                self.total_earnings_label.setText(f"{total_earned:.8f} PYC")
            
            if hasattr(self, 'blockchain_height_label'):
                self.blockchain_height_label.setText(str(len(self.blockchain.chain)))
            
            # Update balance
            self.update_ui()
            
        except Exception as e:
            self.log_message(f"❌ Block mined handler error: {e}")
    
    def on_hashrate_update(self, hashrate):
        """Handle hashrate updates"""
        try:
            if hasattr(self, 'hashrate_label'):
                if hashrate > 1000000:
                    self.hashrate_label.setText(f"Hashrate: {hashrate/1000000:.2f} MH/s")
                elif hashrate > 1000:
                    self.hashrate_label.setText(f"Hashrate: {hashrate/1000:.2f} KH/s")
                else:
                    self.hashrate_label.setText(f"Hashrate: {hashrate:.1f} H/s")
        except Exception as e:
            self.log_message(f"❌ Hashrate update error: {e}")
    
    def on_balance_update(self, new_balance):
        """Handle balance updates from mining"""
        try:
            # Update balance display
            if hasattr(self, 'balance_label'):
                self.balance_label.setText(f"Balance: {new_balance:.8f} PYC")
            
            if hasattr(self, 'balance_display'):
                self.balance_display.setText(f"{new_balance:.8f}")
                
            if hasattr(self, 'stat_cards') and 'Wallet Balance' in self.stat_cards:
                self.stat_cards['Wallet Balance'].setText(f"{new_balance:.8f} PYC")
                
        except Exception as e:
            self.log_message(f"❌ Error updating balance: {e}")

'''
            
            # Find a good insertion point (before closeEvent)
            insert_point = self.fixed_content.rfind('def closeEvent(self, event):')
            if insert_point == -1:
                insert_point = self.fixed_content.rfind('def main():')
            if insert_point == -1:
                insert_point = len(self.fixed_content) - 500
            
            self.fixed_content = (
                self.fixed_content[:insert_point] + 
                complete_mining_methods + 
                "\n" + 
                self.fixed_content[insert_point:]
            )
            print("✅ Added all mining methods")
        
        return True
    
    def save_fixed_file(self):
        """Save the completely fixed file"""
        try:
            # Create backup
            backup_file = f"{self.source_file}.complete_backup"
            if not os.path.exists(backup_file):
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(self.source_content)
                print(f"💾 Complete backup created: {backup_file}")
            
            # Save fixed file
            with open(self.source_file, 'w', encoding='utf-8') as f:
                f.write(self.fixed_content)
            print(f"✅ Completely fixed file saved: {self.source_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def final_verification(self):
        """Final verification of all components"""
        checks = [
            ('Mining tab method', 'def create_mining_tab(self):'),
            ('Mining tab call', 'self.create_mining_tab()'),
            ('Start mining method', 'def start_mining(self):'),
            ('Stop mining method', 'def stop_mining(self):'),
            ('Mining status handler', 'def on_mining_status(self, message):'),
            ('Block mined handler', 'def on_block_mined(self, block_data):'),
            ('Hashrate handler', 'def on_hashrate_update(self, hashrate):'),
            ('Enhanced blockchain', 'class EnhancedBlockchain:'),
            ('Mining thread', 'class CryptoMiningThread(QThread):'),
            ('QThread import', 'QThread'),
            ('pyqtSignal import', 'pyqtSignal')
        ]
        
        all_good = True
        print("\n📋 Final Verification:")
        for check_name, check_text in checks:
            if check_text in self.fixed_content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing")
                all_good = False
        
        return all_good
    
    def run_complete_fix(self):
        """Run the complete fix process"""
        print("🔧 Starting Complete Mining Thread Fix...")
        
        success = (
            self.load_and_fix() and
            self.save_fixed_file() and
            self.final_verification()
        )
        
        if success:
            print(f"\n🎉 Complete fix successful!")
            print(f"🚀 Your wallet now has full mining support!")
            print(f"\n✨ Features available:")
            print(f"   ⛏️ Mining tab with controls")
            print(f"   📊 Real-time mining statistics")
            print(f"   🔗 Blockchain height tracking")
            print(f"   💰 Mining earnings display")
            print(f"   ⚡ Hashrate monitoring")
            print(f"\n🚀 Run: python {self.source_file}")
        else:
            print(f"\n💥 Some components are still missing!")
            print(f"📝 Try running the fix again or check for errors above")
        
        return success

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete Mining Thread Fix')
    parser.add_argument('--file', default='pyqt2_enhanced.py', help='File to fix')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        print("ℹ️ Available Python files:")
        for f in sorted(os.listdir('.')):
            if f.endswith('.py'):
                print(f"   {f}")
        sys.exit(1)
    
    fixer = MiningThreadFixer(args.file)
    success = fixer.run_complete_fix()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
