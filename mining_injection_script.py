#!/usr/bin/env python3
"""
Mining Tab Injection Script for PythonCoin Complete Wallet
This script automatically injects complete mining functionality into pyqt2_enhanced.py
"""

import os
import re
import shutil
from datetime import datetime

def inject_mining_functionality():
    """Main injection function"""
    print("🚀 PythonCoin Mining Tab Injection Script")
    print("=" * 50)
    
    # File paths
    source_file = "pyqt2_enhanced.py"
    backup_file = f"pyqt2_enhanced_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    # Check if source file exists
    if not os.path.exists(source_file):
        print(f"❌ Source file '{source_file}' not found!")
        print("Please ensure pyqt2_enhanced.py is in the current directory.")
        return False
    
    # Create backup
    print(f"💾 Creating backup: {backup_file}")
    shutil.copy2(source_file, backup_file)
    
    # Read the source file
    print(f"📖 Reading source file: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if mining tab already exists
    if "create_mining_tab" in content:
        print("⚠️ Mining tab functionality already exists!")
        response = input("Do you want to update it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Injection cancelled.")
            return False
    
    # Perform injections
    print("🔧 Injecting mining functionality...")
    
    # 1. Inject mining methods into CompletePythonCoinWallet class
    content = inject_mining_methods(content)
    
    # 2. Update create_tabs method
    content = update_create_tabs_method(content)
    
    # 3. Update __init__ method
    content = update_init_method(content)
    
    # 4. Update update_ui method
    content = update_ui_method(content)
    
    # 5. Update closeEvent method
    content = update_close_event_method(content)
    
    # 6. Enhance EnhancedBlockchain class
    content = enhance_blockchain_class(content)
    
    # 7. Update CryptoMiningThread class
    content = update_mining_thread_class(content)
    
    # Write the modified content back
    print(f"💾 Writing enhanced file: {source_file}")
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Mining tab injection completed successfully!")
    print(f"📁 Backup saved as: {backup_file}")
    print("🎯 Mining tab is now available in your wallet!")
    print("\nTo access the mining tab:")
    print("1. Run your enhanced wallet: python pyqt2_enhanced.py")
    print("2. Look for the '⛏️ Mining' tab")
    print("3. Click 'Start Mining' to begin earning PYC!")
    
    return True

def inject_mining_methods(content):
    """Inject all mining-related methods into the CompletePythonCoinWallet class"""
    
    mining_methods = '''
    def create_mining_tab(self):
        """Create mining and blockchain tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mining status and controls
        mining_group = QGroupBox("⛏️ Mining Operations")
        mining_layout = QVBoxLayout(mining_group)
        
        # Status display row
        status_layout = QHBoxLayout()
        
        # Mining status indicator
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #dee2e6; 
                border-radius: 8px; 
                background: #f8f9fa; 
                padding: 15px;
                margin: 5px;
            }
        """)
        status_frame_layout = QVBoxLayout(status_frame)
        
        self.mining_status_label = QLabel("Status: Stopped")
        self.mining_status_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.mining_status_label.setStyleSheet("color: #dc3545;")  # Red when stopped
        status_frame_layout.addWidget(self.mining_status_label)
        
        # Mining statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #dee2e6; 
                border-radius: 8px; 
                background: #f8f9fa; 
                padding: 15px;
                margin: 5px;
            }
        """)
        stats_frame_layout = QVBoxLayout(stats_frame)
        
        self.hashrate_label = QLabel("Hashrate: 0 H/s")
        self.hashrate_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.blocks_mined_label = QLabel("Blocks Mined: 0")
        self.blocks_mined_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        stats_frame_layout.addWidget(self.hashrate_label)
        stats_frame_layout.addWidget(self.blocks_mined_label)
        
        status_layout.addWidget(status_frame)
        status_layout.addWidget(stats_frame)
        mining_layout.addLayout(status_layout)
        
        # Mining controls
        controls_layout = QHBoxLayout()
        
        self.start_mining_btn = QPushButton("🚀 Start Mining")
        self.start_mining_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.start_mining_btn.clicked.connect(self.start_mining)
        
        self.stop_mining_btn = QPushButton("🛑 Stop Mining")
        self.stop_mining_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_mining_btn.clicked.connect(self.stop_mining)
        self.stop_mining_btn.setEnabled(False)
        
        # Mining progress bar
        self.mining_progress = QProgressBar()
        self.mining_progress.setVisible(False)
        self.mining_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 4px;
            }
        """)
        
        controls_layout.addWidget(self.start_mining_btn)
        controls_layout.addWidget(self.stop_mining_btn)
        controls_layout.addWidget(self.mining_progress)
        controls_layout.addStretch()
        
        mining_layout.addLayout(controls_layout)
        layout.addWidget(mining_group)
        
        # Blockchain information
        blockchain_group = QGroupBox("🔗 Blockchain Information")
        blockchain_layout = QFormLayout(blockchain_group)
        
        # Blockchain stats
        self.blockchain_height_label = QLabel("0")
        self.blockchain_height_label.setFont(QFont('Arial', 12, QFont.Bold))
        blockchain_layout.addRow("Blockchain Height:", self.blockchain_height_label)
        
        self.pending_tx_label = QLabel("0")
        self.pending_tx_label.setFont(QFont('Arial', 12, QFont.Bold))
        blockchain_layout.addRow("Pending Transactions:", self.pending_tx_label)
        
        self.genesis_status_label = QLabel("Not Created")
        self.genesis_status_label.setFont(QFont('Arial', 12, QFont.Bold))
        blockchain_layout.addRow("Genesis Block:", self.genesis_status_label)
        
        self.difficulty_label = QLabel("2")
        self.difficulty_label.setFont(QFont('Arial', 12, QFont.Bold))
        blockchain_layout.addRow("Current Difficulty:", self.difficulty_label)
        
        # Genesis block creation button
        genesis_layout = QHBoxLayout()
        self.create_genesis_btn = QPushButton("🌱 Create Genesis Block")
        self.create_genesis_btn.clicked.connect(self.create_genesis_block_manually)
        self.create_genesis_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        self.refresh_blockchain_btn = QPushButton("🔄 Refresh Info")
        self.refresh_blockchain_btn.clicked.connect(self.refresh_blockchain_info)
        
        genesis_layout.addWidget(self.create_genesis_btn)
        genesis_layout.addWidget(self.refresh_blockchain_btn)
        genesis_layout.addStretch()
        
        blockchain_layout.addRow(genesis_layout)
        layout.addWidget(blockchain_group)
        
        # Mining earnings and statistics
        earnings_group = QGroupBox("💰 Mining Earnings & Statistics")
        earnings_layout = QFormLayout(earnings_group)
        
        self.total_earnings_label = QLabel("0.00000000 PYC")
        self.total_earnings_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.total_earnings_label.setStyleSheet("color: #28a745;")
        earnings_layout.addRow("Total Mining Earnings:", self.total_earnings_label)
        
        self.avg_block_time_label = QLabel("N/A")
        earnings_layout.addRow("Average Block Time:", self.avg_block_time_label)
        
        self.last_block_time_label = QLabel("N/A")
        earnings_layout.addRow("Last Block Mined:", self.last_block_time_label)
        
        self.mining_efficiency_label = QLabel("N/A")
        earnings_layout.addRow("Mining Efficiency:", self.mining_efficiency_label)
        
        layout.addWidget(earnings_group)
        
        # Mining log/activity
        log_group = QGroupBox("📜 Mining Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.mining_log = QPlainTextEdit()
        self.mining_log.setReadOnly(True)
        self.mining_log.setMaximumHeight(150)
        self.mining_log.setStyleSheet("""
            QPlainTextEdit { 
                font-family: 'Consolas', 'Monaco', monospace; 
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)
        self.mining_log.setPlainText("Mining log will appear here when you start mining...")
        
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("🧹 Clear Log")
        clear_log_btn.clicked.connect(lambda: self.mining_log.clear())
        save_log_btn = QPushButton("💾 Save Log")
        save_log_btn.clicked.connect(self.save_mining_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(save_log_btn)
        log_controls.addStretch()
        
        log_layout.addWidget(self.mining_log)
        log_layout.addLayout(log_controls)
        
        layout.addWidget(log_group)
        
        # Update initial blockchain info
        self.refresh_blockchain_info()
        
        self.tab_widget.addTab(widget, "⛏️ Mining")

    def start_mining(self):
        """Start the mining process"""
        try:
            if hasattr(self, 'mining_thread') and self.mining_thread and self.mining_thread.mining:
                self.log_mining_message("⚠️ Mining already running")
                return
            
            if not hasattr(self, 'blockchain') or not self.blockchain:
                self.log_mining_message("❌ No blockchain available")
                QMessageBox.warning(self, "Mining Error", "No blockchain available for mining")
                return
            
            # Create genesis block if needed
            if not self.blockchain.genesis_complete:
                self.blockchain.create_genesis_block([self.wallet.address])
                self.log_mining_message("✅ Genesis block created automatically")
                self.refresh_blockchain_info()
            
            # Create mining thread
            self.mining_thread = CryptoMiningThread(self.blockchain, self.wallet, self)
            self.mining_thread.status_update.connect(self.on_mining_status)
            self.mining_thread.block_mined.connect(self.on_block_mined)
            self.mining_thread.hashrate_update.connect(self.on_hashrate_update)
            
            self.mining_thread.start_mining()
            self.mining_enabled = True
            self.mining_start_time = time.time()
            
            self.log_mining_message("🚀 Mining started!")
            
            # Update UI
            self.mining_status_label.setText("Status: Mining ⛏️")
            self.mining_status_label.setStyleSheet("color: #28a745;")  # Green when mining
            self.start_mining_btn.setEnabled(False)
            self.stop_mining_btn.setEnabled(True)
            self.mining_progress.setVisible(True)
            self.mining_progress.setRange(0, 0)  # Indeterminate progress
            
        except Exception as e:
            self.log_mining_message(f"❌ Mining start error: {e}")
            QMessageBox.critical(self, "Mining Error", f"Failed to start mining:\\n{str(e)}")

    def stop_mining(self):
        """Stop the mining process"""
        try:
            if hasattr(self, 'mining_thread') and self.mining_thread:
                self.mining_thread.stop_mining()
                self.mining_thread.wait(3000)  # Wait up to 3 seconds for thread to stop
                self.mining_thread = None
            
            self.mining_enabled = False
            self.log_mining_message("🛑 Mining stopped")
            
            # Update UI
            self.mining_status_label.setText("Status: Stopped")
            self.mining_status_label.setStyleSheet("color: #dc3545;")  # Red when stopped
            self.start_mining_btn.setEnabled(True)
            self.stop_mining_btn.setEnabled(False)
            self.mining_progress.setVisible(False)
            self.hashrate_label.setText("Hashrate: 0 H/s")
            
        except Exception as e:
            self.log_mining_message(f"❌ Mining stop error: {e}")

    def on_mining_status(self, message):
        """Handle mining status updates"""
        self.log_mining_message(message)
        
        # Update status label with clean message
        clean_message = message.replace("⛏️ ", "").replace("🎉 ", "").replace("⚠️ ", "").replace("❌ ", "")
        if "Mining" in clean_message:
            self.mining_status_label.setText(f"Status: {clean_message}")

    def on_block_mined(self, block_data):
        """Handle block mined event"""
        try:
            self.total_blocks_mined += 1
            block_reward = 50.0  # Standard block reward
            
            self.log_mining_message(f"🎉 Block {block_data['index']} mined! Reward: {block_reward} PYC")
            
            # Update UI
            self.blocks_mined_label.setText(f"Blocks Mined: {self.total_blocks_mined}")
            
            # Update total earnings
            total_earned = self.total_blocks_mined * block_reward
            self.total_earnings_label.setText(f"{total_earned:.8f} PYC")
            
            # Update last block time
            self.last_block_time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Update blockchain info
            self.refresh_blockchain_info()
            
            # Update main wallet balance display
            self.update_ui()
            
            # Calculate mining efficiency
            if self.mining_start_time > 0:
                mining_duration = time.time() - self.mining_start_time
                blocks_per_hour = (self.total_blocks_mined / mining_duration) * 3600
                self.mining_efficiency_label.setText(f"{blocks_per_hour:.2f} blocks/hour")
            
        except Exception as e:
            self.log_mining_message(f"❌ Block mined handler error: {e}")

    def on_hashrate_update(self, hashrate):
        """Handle hashrate updates"""
        try:
            if hashrate > 1000000:
                hashrate_text = f"Hashrate: {hashrate/1000000:.2f} MH/s"
            elif hashrate > 1000:
                hashrate_text = f"Hashrate: {hashrate/1000:.2f} KH/s"
            else:
                hashrate_text = f"Hashrate: {hashrate:.1f} H/s"
            
            self.hashrate_label.setText(hashrate_text)
            
        except Exception as e:
            self.log_mining_message(f"❌ Hashrate update error: {e}")

    def create_genesis_block_manually(self):
        """Manually create genesis block"""
        try:
            if self.blockchain.genesis_complete:
                QMessageBox.information(self, "Genesis Block", "Genesis block already exists!")
                return
            
            reply = QMessageBox.question(
                self, "Create Genesis Block",
                "Create the genesis block now?\\nThis will initialize the blockchain.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.blockchain.create_genesis_block([self.wallet.address])
                self.log_mining_message("🌱 Genesis block created manually")
                self.refresh_blockchain_info()
                QMessageBox.information(self, "Success", "Genesis block created successfully!")
            
        except Exception as e:
            self.log_mining_message(f"❌ Genesis creation error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create genesis block:\\n{str(e)}")

    def refresh_blockchain_info(self):
        """Refresh blockchain information display"""
        try:
            if hasattr(self, 'blockchain') and self.blockchain:
                # Update blockchain height
                height = len(self.blockchain.chain)
                self.blockchain_height_label.setText(str(height))
                
                # Update pending transactions
                pending = len(self.blockchain.pending_transactions) if hasattr(self.blockchain, 'pending_transactions') else 0
                self.pending_tx_label.setText(str(pending))
                
                # Update genesis status
                if self.blockchain.genesis_complete:
                    self.genesis_status_label.setText("✅ Created")
                    self.genesis_status_label.setStyleSheet("color: #28a745;")
                    self.create_genesis_btn.setEnabled(False)
                    self.create_genesis_btn.setText("✅ Genesis Exists")
                else:
                    self.genesis_status_label.setText("❌ Not Created")
                    self.genesis_status_label.setStyleSheet("color: #dc3545;")
                    self.create_genesis_btn.setEnabled(True)
                    self.create_genesis_btn.setText("🌱 Create Genesis Block")
                
                # Update difficulty
                if hasattr(self.blockchain, 'difficulty'):
                    self.difficulty_label.setText(str(self.blockchain.difficulty))
                
                # Calculate average block time if we have multiple blocks
                if height > 1:
                    try:
                        first_block_time = self.blockchain.chain[1].timestamp if hasattr(self.blockchain.chain[1], 'timestamp') else time.time()
                        last_block_time = self.blockchain.chain[-1].timestamp if hasattr(self.blockchain.chain[-1], 'timestamp') else time.time()
                        avg_time = (last_block_time - first_block_time) / (height - 1)
                        self.avg_block_time_label.setText(f"{avg_time:.1f} seconds")
                    except:
                        self.avg_block_time_label.setText("N/A")
                else:
                    self.avg_block_time_label.setText("N/A")
            
        except Exception as e:
            self.log_mining_message(f"❌ Blockchain info refresh error: {e}")

    def log_mining_message(self, message):
        """Log a message to the mining log"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            if hasattr(self, 'mining_log') and self.mining_log:
                self.mining_log.appendPlainText(formatted_message)
                
                # Auto-scroll to bottom
                cursor = self.mining_log.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.mining_log.setTextCursor(cursor)
                
                # Keep only last 100 lines
                if self.mining_log.document().lineCount() > 100:
                    cursor = self.mining_log.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 20)
                    cursor.removeSelectedText()
            
            # Also log to main activity log
            if hasattr(self, 'log_message'):
                self.log_message(f"⛏️ {message}")
            
        except Exception as e:
            print(f"Mining log error: {e}")

    def save_mining_log(self):
        """Save mining log to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Mining Log",
                f"mining_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"PythonCoin Mining Log - {datetime.now()}\\n")
                    f.write("=" * 50 + "\\n")
                    f.write(self.mining_log.toPlainText())
                
                QMessageBox.information(self, "Success", f"Mining log saved to: {filename}")
                self.log_mining_message(f"💾 Mining log saved: {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save mining log:\\n{str(e)}")
            self.log_mining_message(f"❌ Log save error: {e}")
'''
    
    # Find the location to insert the mining methods
    # Look for the end of the CompletePythonCoinWallet class
    class_pattern = r'(class CompletePythonCoinWallet.*?def closeEvent.*?event\.ignore\(\))'
    
    if re.search(class_pattern, content, re.DOTALL):
        # Insert mining methods before closeEvent
        close_event_pattern = r'(\s+def closeEvent\(self, event\):)'
        content = re.sub(close_event_pattern, mining_methods + r'\1', content, flags=re.DOTALL)
    else:
        # Fallback: insert before the last method of the class
        last_method_pattern = r'(\s+def show_about\(self\):.*?QMessageBox\.about.*?\n)'
        content = re.sub(last_method_pattern, r'\1' + mining_methods, content, flags=re.DOTALL)
    
    return content

def update_create_tabs_method(content):
    """Update the create_tabs method to include mining tab"""
    
    # Pattern to find create_tabs method
    pattern = r'(def create_tabs\(self\):.*?)(self\.create_developers_tab\(\))'
    replacement = r'\1\2\n        self.create_mining_tab()'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def update_init_method(content):
    """Update __init__ method to initialize mining attributes"""
    
    mining_init = '''
        # Initialize mining attributes
        self.mining_thread = None
        self.mining_enabled = False
        self.total_blocks_mined = 0
        self.mining_start_time = 0
'''
    
    # Find __init__ method and add mining initialization
    pattern = r'(def __init__\(self\):.*?# Stats\s*\n.*?}\s*\n)'
    replacement = r'\1' + mining_init + '\n'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def update_ui_method(content):
    """Update update_ui method to include mining UI updates"""
    
    mining_ui_updates = '''
            # Update mining info if mining tab exists
            if hasattr(self, 'blockchain_height_label'):
                height = len(self.blockchain.chain) if self.blockchain else 0
                self.blockchain_height_label.setText(str(height))
            
            if hasattr(self, 'pending_tx_label'):
                pending = len(self.blockchain.pending_transactions) if self.blockchain else 0
                self.pending_tx_label.setText(str(pending))
'''
    
    # Find update_ui method and add mining updates
    pattern = r'(def update_ui\(self\):.*?# Update counts.*?\n)'
    replacement = r'\1' + mining_ui_updates + '\n'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def update_close_event_method(content):
    """Update closeEvent method to stop mining"""
    
    mining_close = '''
                # Stop mining safely
                try:
                    if hasattr(self, 'mining_thread') and self.mining_thread:
                        self.mining_thread.stop_mining()
                        self.mining_thread.wait(3000)
                except Exception as e:
                    logger.warning(f"Error stopping mining: {e}")
'''
    
    # Find closeEvent method and add mining cleanup
    pattern = r'(def closeEvent\(self, event\):.*?# Stop portal server safely.*?\n)'
    replacement = r'\1' + mining_close + '\n'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def enhance_blockchain_class(content):
    """Enhance the EnhancedBlockchain class with difficulty property"""
    
    # Add difficulty property to EnhancedBlockchain
    pattern = r'(class EnhancedBlockchain:.*?def __init__\(self\):.*?self\.genesis_complete = False)'
    replacement = r'\1\n        self.difficulty = 2'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def update_mining_thread_class(content):
    """Update CryptoMiningThread class to emit proper signals"""
    
    enhanced_mining_thread = '''
class CryptoMiningThread(QThread):
    status_update = pyqtSignal(str)
    block_mined = pyqtSignal(dict)
    hashrate_update = pyqtSignal(float)
    
    def __init__(self, blockchain, wallet, parent=None):
        super().__init__(parent)
        self.blockchain = blockchain
        self.wallet = wallet
        self.mining = False
        self.blocks_mined = 0
        self.start_time = time.time()
        self.nonces_tried = 0
    
    def start_mining(self):
        self.mining = True
        self.start()
    
    def stop_mining(self):
        self.mining = False
    
    def run(self):
        self.start_time = time.time()
        while self.mining:
            try:
                if not self.blockchain.genesis_complete:
                    self.status_update.emit("⏳ Waiting for genesis block...")
                    self.msleep(1000)
                    continue
                
                # Mine a new block
                block = self.blockchain.mine_pending_transactions(self.wallet.address)
                
                if block and self.mining:
                    self.blocks_mined += 1
                    self.nonces_tried += block.nonce
                    
                    # Calculate hashrate
                    elapsed = time.time() - self.start_time
                    hashrate = self.nonces_tried / max(elapsed, 1)
                    
                    # Emit signals
                    self.status_update.emit(f"Block {block.index} mined! Nonce: {block.nonce}")
                    self.block_mined.emit({
                        "index": block.index,
                        "hash": block.hash,
                        "nonce": block.nonce,
                        "reward": 50.0
                    })
                    self.hashrate_update.emit(hashrate)
                    
                    # Brief pause between blocks
                    self.msleep(2000)
                else:
                    self.status_update.emit("Mining failed, retrying...")
                    self.msleep(5000)
                    
            except Exception as e:
                self.status_update.emit(f"Mining error: {str(e)}")
                self.msleep(5000)
'''
    
    # Replace existing CryptoMiningThread class
    pattern = r'class CryptoMiningThread\(QThread\):.*?(?=class|\Z)'
    content = re.sub(pattern, enhanced_mining_thread + '\n\n', content, flags=re.DOTALL)
    
    return content

if __name__ == "__main__":
    try:
        success = inject_mining_functionality()
        if success:
            print("\n🎉 Injection completed successfully!")
            print("Your PythonCoin wallet now has full mining capabilities!")
        else:
            print("\n❌ Injection failed. Please check the error messages above.")
    except Exception as e:
        print(f"\n💥 Injection script error: {e}")
        print("Please check your source file and try again.")
