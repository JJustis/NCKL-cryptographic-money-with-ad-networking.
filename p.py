#!/usr/bin/env python3
"""
PyQt Wallet Enhancement Injection Script
Adds SVG image support and automatic payments system
"""
import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the original file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def inject_svg_image_support(content):
    """Inject SVG image background support"""
    
    # Find the generate_svg_ad method
    svg_method_pattern = r'(def generate_svg_ad\(self, metadata\):.*?)(template = template\.replace\(placeholder, str\(value\)\))'
    
    # Enhanced SVG template with image support
    enhanced_svg_template = '''        # Enhanced SVG template with image support
        svg_template = """<svg width="400" height="280" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff"/>
            <stop offset="50%" style="stop-color:#f8fffe"/>
            <stop offset="100%" style="stop-color:#f0f9ff"/>
        </linearGradient>
        <linearGradient id="badgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ff6b35"/>
            <stop offset="100%" style="stop-color:#f7931e"/>
        </linearGradient>
        <linearGradient id="payoutGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#28a745"/>
            <stop offset="100%" style="stop-color:#20c997"/>
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#0066cc" flood-opacity="0.15"/>
        </filter>
        <pattern id="bgImage" patternUnits="userSpaceOnUse" width="400" height="280">
            <rect width="400" height="280" fill="url(#bgGrad)"/>
            {{#AD_IMAGE_URL}}
            <image href="{{AD_IMAGE_URL}}" x="0" y="0" width="400" height="280" opacity="0.3" preserveAspectRatio="xMidYMid slice"/>
            {{/AD_IMAGE_URL}}
        </pattern>
    </defs>
    
    <!-- Main container with image background -->
    <rect x="8" y="8" width="384" height="264" rx="16" ry="16" 
          fill="url(#bgImage)" stroke="#0066cc" stroke-width="2" filter="url(#shadow)">
        <animate attributeName="stroke-width" values="2;3;2" dur="3s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Semi-transparent overlay for text readability -->
    <rect x="8" y="8" width="384" height="264" rx="16" ry="16" 
          fill="rgba(255,255,255,0.85)" stroke="none"/>
    
    <!-- Animated top border -->
    <rect x="8" y="8" width="384" height="4" rx="2" ry="2">
        <animate attributeName="fill" values="#ff6b35;#f7931e;#0066cc;#28a745;#ff6b35" dur="5s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Badge -->
    <rect x="300" y="20" width="85" height="28" rx="14" ry="14" fill="url(#badgeGrad)"/>
    <text x="342" y="37" text-anchor="middle" fill="white" font-family="Arial, sans-serif" 
          font-size="11" font-weight="bold">💎 PYC</text>
    
    <!-- Title with background for readability -->
    <rect x="20" y="45" width="360" height="25" rx="4" ry="4" fill="rgba(255,255,255,0.9)"/>
    <text x="24" y="62" fill="#0066cc" font-family="Arial, sans-serif" font-size="22" font-weight="bold">
        {{AD_TITLE}}
    </text>
    
    <!-- Description with background -->
    <rect x="20" y="75" width="360" height="80" rx="4" ry="4" fill="rgba(255,255,255,0.9)"/>
    <foreignObject x="24" y="80" width="350" height="70">
        <div xmlns="http://www.w3.org/1999/xhtml" 
             style="color: #374151; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; padding: 5px;">
            {{AD_DESCRIPTION}}
        </div>
    </foreignObject>
    
    <!-- Category -->
    <rect x="20" y="190" width="250" height="20" rx="4" ry="4" fill="rgba(255,255,255,0.9)"/>
    <text x="24" y="203" fill="#0066cc" font-family="Arial, sans-serif" 
          font-size="14" font-weight="600">📱 {{AD_CATEGORY}} • 🌐 P2P Network</text>
    
    <!-- Payout button with hover effect -->
    <g id="payoutButton">
        <rect x="280" y="180" width="110" height="35" rx="17" ry="17" fill="url(#payoutGrad)" filter="url(#shadow)">
            <animate attributeName="y" values="180;178;180" dur="2s" repeatCount="indefinite"/>
        </rect>
        <text x="335" y="200" text-anchor="middle" fill="white" font-family="Arial, sans-serif" 
              font-size="13" font-weight="bold">+{{AD_PAYOUT}} PYC</text>
    </g>
    
    <!-- Stats -->
    <rect x="20" y="240" width="120" height="24" rx="12" ry="12" 
          fill="rgba(0,102,204,0.9)" stroke="rgba(0,102,204,0.3)" stroke-width="1"/>
    <text x="80" y="254" text-anchor="middle" fill="white" font-family="Arial, sans-serif" 
          font-size="10" font-weight="600">ID: {{AD_ID_SHORT}}</text>
    
    <!-- Click area -->
    <rect x="0" y="0" width="400" height="280" fill="transparent" style="cursor: pointer"
          onclick="handleAdClick('{{AD_ID}}')"/>
    
    <script type="application/ecmascript"><![CDATA[
        function handleAdClick(adId) {
            if (window.pythonCoinWallet) {
                window.pythonCoinWallet.recordClick(adId);
            }
            
            const clickUrl = '{{AD_CLICK_URL}}';
            if (clickUrl && clickUrl !== '#') {
                window.open(clickUrl, '_blank');
            }
        }
    ]]></script>
</svg>"""'''
    
    # Replace the existing template assignment
    replacement = r'\1' + enhanced_svg_template + r'''
        
        # Prepare image handling
        image_url = metadata.get('image_url', '')
        
        # Convert local file paths to data URLs for embedding
        if image_url and image_url.startswith('file://'):
            try:
                import base64
                from pathlib import Path
                
                file_path = image_url.replace('file://', '')
                if Path(file_path).exists():
                    with open(file_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                        file_ext = Path(file_path).suffix.lower()
                        
                        # Determine MIME type
                        mime_types = {
                            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                            '.png': 'image/png', '.gif': 'image/gif',
                            '.webp': 'image/webp', '.svg': 'image/svg+xml'
                        }
                        mime_type = mime_types.get(file_ext, 'image/png')
                        
                        # Create data URL
                        image_url = f"data:{mime_type};base64,{img_data}"
                else:
                    image_url = ""  # File not found
            except Exception as e:
                print(f"Error processing image: {e}")
                image_url = ""
        
        # Enhanced replacements with image support
        replacements = {
            '{{AD_ID}}': metadata['id'],
            '{{AD_ID_SHORT}}': metadata['id'][:8],
            '{{AD_TITLE}}': metadata['title'][:30] + ('...' if len(metadata['title']) > 30 else ''),
            '{{AD_DESCRIPTION}}': metadata['description'][:100] + ('...' if len(metadata['description']) > 100 else ''),
            '{{AD_CATEGORY}}': metadata['category'].title(),
            '{{AD_CLICK_URL}}': metadata['click_url'],
            '{{AD_PAYOUT}}': f"{metadata['payout_rate']:.8f}",
            '{{AD_IMAGE_URL}}': image_url,
            '{{#AD_IMAGE_URL}}': '' if image_url else '<!--',
            '{{/AD_IMAGE_URL}}': '' if image_url else '-->'
        }
        
        # Apply replacements
        for placeholder, value in replacements.items():
            svg_template = svg_template.replace(placeholder, str(value))
        
        return svg_template'''
    
    # Apply the replacement
    if re.search(svg_method_pattern, content, re.DOTALL):
        content = re.sub(svg_method_pattern, replacement, content, flags=re.DOTALL)
        print("✅ Enhanced SVG image support injection completed")
    else:
        print("❌ Could not find generate_svg_ad method to enhance")
    
    return content

def inject_automatic_payments_system(content):
    """Inject automatic payments system"""
    
    # Add transaction queue and UI elements after the dashboard tab creation
    dashboard_injection = '''
        # Create transaction queue management tab
        self.create_transaction_queue_tab()'''
    
    # Find where to inject the transaction queue tab
    tab_creation_pattern = r'(self\.create_developer_portal_tab\(\))'
    content = re.sub(tab_creation_pattern, r'\1' + dashboard_injection, content)
    
    # Add the transaction queue tab method
    transaction_queue_method = '''
    def create_transaction_queue_tab(self):
        """Create transaction queue management tab for automatic payments"""
        queue_widget = QWidget()
        queue_layout = QVBoxLayout()
        queue_widget.setLayout(queue_layout)
        
        # Transaction Queue Status
        status_group = QGroupBox("💰 Automatic Payment System")
        status_layout = QVBoxLayout()
        
        self.payment_system_status = QLabel("Status: Ready for incoming requests")
        self.payment_system_status.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        status_layout.addWidget(self.payment_system_status)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.enable_auto_payments_btn = QPushButton("🔴 Enable Auto-Payments")
        self.enable_auto_payments_btn.clicked.connect(self.toggle_auto_payments)
        self.enable_auto_payments_btn.setStyleSheet("background-color: #28a745;")
        controls_layout.addWidget(self.enable_auto_payments_btn)
        
        self.clear_queue_btn = QPushButton("🗑️ Clear Queue")
        self.clear_queue_btn.clicked.connect(self.clear_transaction_queue)
        controls_layout.addWidget(self.clear_queue_btn)
        
        refresh_queue_btn = QPushButton("🔄 Refresh")
        refresh_queue_btn.clicked.connect(self.update_transaction_queue_display)
        controls_layout.addWidget(refresh_queue_btn)
        
        status_layout.addLayout(controls_layout)
        status_group.setLayout(status_layout)
        queue_layout.addWidget(status_group)
        
        # Pending Transactions Queue
        pending_group = QGroupBox("📋 Pending Payment Requests")
        pending_layout = QVBoxLayout()
        
        # Transaction queue table
        self.transaction_queue_table = QTableWidget()
        self.transaction_queue_table.setColumnCount(6)
        self.transaction_queue_table.setHorizontalHeaderLabels([
            "Time", "From", "To", "Amount", "Status", "Select"
        ])
        
        queue_header = self.transaction_queue_table.horizontalHeader()
        queue_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        pending_layout.addWidget(self.transaction_queue_table)
        
        # Batch processing controls
        batch_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("☑️ Select All")
        self.select_all_btn.clicked.connect(self.select_all_transactions)
        batch_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("◻️ Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_transactions)
        batch_layout.addWidget(self.deselect_all_btn)
        
        batch_layout.addStretch()
        
        # Submit button
        self.submit_selected_btn = QPushButton("💸 Submit Selected Payments")
        self.submit_selected_btn.clicked.connect(self.submit_selected_transactions)
        self.submit_selected_btn.setStyleSheet("background-color: #007bff; font-size: 16px; padding: 12px;")
        self.submit_selected_btn.setMinimumHeight(50)
        batch_layout.addWidget(self.submit_selected_btn)
        
        pending_layout.addLayout(batch_layout)
        pending_group.setLayout(pending_layout)
        queue_layout.addWidget(pending_group)
        
        # Auto-payment settings
        settings_group = QGroupBox("⚙️ Auto-Payment Settings")
        settings_layout = QFormLayout()
        
        self.auto_approve_limit = QDoubleSpinBox()
        self.auto_approve_limit.setDecimals(8)
        self.auto_approve_limit.setRange(0, 1000)
        self.auto_approve_limit.setValue(0.1)  # Auto-approve payments under 0.1 PYC
        settings_layout.addRow("Auto-approve limit (PYC):", self.auto_approve_limit)
        
        self.require_confirmation = QCheckBox("Require confirmation for large payments")
        self.require_confirmation.setChecked(True)
        settings_layout.addRow("", self.require_confirmation)
        
        settings_group.setLayout(settings_layout)
        queue_layout.addWidget(settings_group)
        
        # Initialize transaction queue system
        self.transaction_queue = []
        self.auto_payments_enabled = False
        
        # Start transaction queue monitoring
        self.setup_transaction_queue_monitoring()
        
        self.tab_widget.addTab(queue_widget, "💰 Payments")
    
    def setup_transaction_queue_monitoring(self):
        """Setup monitoring for incoming transaction requests"""
        try:
            # Timer to check for new transaction requests
            self.transaction_monitor_timer = QTimer()
            self.transaction_monitor_timer.timeout.connect(self.check_incoming_transactions)
            self.transaction_monitor_timer.start(2000)  # Check every 2 seconds
            
            self.log_message("✅ Transaction queue monitoring started")
            
        except Exception as e:
            self.log_message(f"❌ Error setting up transaction monitoring: {str(e)}")
    
    def check_incoming_transactions(self):
        """Check for incoming transaction requests through the node server"""
        try:
            # Check if node is running and has pending requests
            if hasattr(self, 'node') and self.node:
                # Look for incoming transaction requests in node's pending queue
                if hasattr(self.node, 'pending_payment_requests'):
                    new_requests = getattr(self.node, 'pending_payment_requests', [])
                    
                    for request in new_requests:
                        self.add_transaction_to_queue(request)
                    
                    # Clear processed requests
                    if new_requests:
                        self.node.pending_payment_requests = []
                        self.update_transaction_queue_display()
                        
                        if self.auto_payments_enabled:
                            self.process_auto_payments()
            
        except Exception as e:
            pass  # Silent fail for monitoring
    
    def add_transaction_to_queue(self, request):
        """Add a transaction request to the queue"""
        try:
            transaction_data = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'from_address': request.get('from', 'Unknown'),
                'to_address': request.get('to', ''),
                'amount': float(request.get('amount', 0)),
                'message': request.get('message', ''),
                'status': 'pending',
                'selected': False,
                'auto_eligible': float(request.get('amount', 0)) <= self.auto_approve_limit.value()
            }
            
            # Add to queue if not duplicate
            if not any(t['from_address'] == transaction_data['from_address'] and 
                      t['to_address'] == transaction_data['to_address'] and
                      t['amount'] == transaction_data['amount'] and
                      t['status'] == 'pending'
                      for t in self.transaction_queue):
                self.transaction_queue.append(transaction_data)
                self.log_message(f"📨 New payment request: {transaction_data['amount']:.6f} PYC from {transaction_data['from_address'][:8]}...")
                
                # Show notification
                if hasattr(self, 'statusBar'):
                    self.statusBar.showMessage(f"New payment request: {transaction_data['amount']:.6f} PYC", 5000)
                
                return True
            
        except Exception as e:
            self.log_message(f"❌ Error adding transaction to queue: {str(e)}")
            
        return False
    
    def update_transaction_queue_display(self):
        """Update the transaction queue display table"""
        try:
            if not hasattr(self, 'transaction_queue_table'):
                return
            
            # Clear existing rows
            self.transaction_queue_table.setRowCount(0)
            
            # Add pending transactions
            pending_transactions = [t for t in self.transaction_queue if t['status'] == 'pending']
            self.transaction_queue_table.setRowCount(len(pending_transactions))
            
            for row, transaction in enumerate(pending_transactions):
                # Time
                time_str = datetime.fromisoformat(transaction['timestamp']).strftime("%H:%M:%S")
                time_item = QTableWidgetItem(time_str)
                self.transaction_queue_table.setItem(row, 0, time_item)
                
                # From
                from_item = QTableWidgetItem(f"{transaction['from_address'][:8]}...")
                self.transaction_queue_table.setItem(row, 1, from_item)
                
                # To
                to_item = QTableWidgetItem(f"{transaction['to_address'][:8]}...")
                self.transaction_queue_table.setItem(row, 2, to_item)
                
                # Amount
                amount_item = QTableWidgetItem(f"{transaction['amount']:.8f} PYC")
                if transaction['auto_eligible']:
                    amount_item.setForeground(QColor(40, 167, 69))  # Green for auto-eligible
                else:
                    amount_item.setForeground(QColor(220, 53, 69))  # Red for manual approval
                self.transaction_queue_table.setItem(row, 3, amount_item)
                
                # Status
                status_text = "✅ Auto-eligible" if transaction['auto_eligible'] else "⚠️ Manual approval"
                status_item = QTableWidgetItem(status_text)
                self.transaction_queue_table.setItem(row, 4, status_item)
                
                # Select checkbox
                select_checkbox = QCheckBox()
                select_checkbox.setChecked(transaction['selected'])
                select_checkbox.stateChanged.connect(
                    lambda state, t_id=transaction['id']: self.update_transaction_selection(t_id, state == 2)
                )
                self.transaction_queue_table.setCellWidget(row, 5, select_checkbox)
            
            # Update status
            if hasattr(self, 'payment_system_status'):
                pending_count = len(pending_transactions)
                selected_count = len([t for t in pending_transactions if t['selected']])
                auto_eligible_count = len([t for t in pending_transactions if t['auto_eligible']])
                
                status_text = f"Status: {pending_count} pending ({selected_count} selected, {auto_eligible_count} auto-eligible)"
                self.payment_system_status.setText(status_text)
            
        except Exception as e:
            self.log_message(f"❌ Error updating queue display: {str(e)}")
    
    def toggle_auto_payments(self):
        """Toggle automatic payments on/off"""
        try:
            self.auto_payments_enabled = not self.auto_payments_enabled
            
            if self.auto_payments_enabled:
                self.enable_auto_payments_btn.setText("🟢 Auto-Payments ON")
                self.enable_auto_payments_btn.setStyleSheet("background-color: #28a745;")
                self.log_message("✅ Automatic payments enabled")
                
                # Process any eligible transactions immediately
                self.process_auto_payments()
            else:
                self.enable_auto_payments_btn.setText("🔴 Auto-Payments OFF")
                self.enable_auto_payments_btn.setStyleSheet("background-color: #dc3545;")
                self.log_message("⏸️ Automatic payments disabled")
                
        except Exception as e:
            self.log_message(f"❌ Error toggling auto-payments: {str(e)}")
    
    def process_auto_payments(self):
        """Process payments that are eligible for automatic approval"""
        try:
            if not self.auto_payments_enabled:
                return
            
            auto_processed = 0
            for transaction in self.transaction_queue:
                if (transaction['status'] == 'pending' and 
                    transaction['auto_eligible'] and 
                    transaction['amount'] <= self.auto_approve_limit.value()):
                    
                    # Process the payment
                    success = self.execute_transaction_payment(transaction)
                    if success:
                        transaction['status'] = 'completed_auto'
                        auto_processed += 1
            
            if auto_processed > 0:
                self.log_message(f"🤖 Auto-processed {auto_processed} payments")
                self.update_transaction_queue_display()
                
        except Exception as e:
            self.log_message(f"❌ Error in auto-payment processing: {str(e)}")
    
    def select_all_transactions(self):
        """Select all pending transactions"""
        try:
            for transaction in self.transaction_queue:
                if transaction['status'] == 'pending':
                    transaction['selected'] = True
            
            self.update_transaction_queue_display()
            
        except Exception as e:
            self.log_message(f"❌ Error selecting all transactions: {str(e)}")
    
    def deselect_all_transactions(self):
        """Deselect all transactions"""
        try:
            for transaction in self.transaction_queue:
                transaction['selected'] = False
            
            self.update_transaction_queue_display()
            
        except Exception as e:
            self.log_message(f"❌ Error deselecting transactions: {str(e)}")
    
    def update_transaction_selection(self, transaction_id, selected):
        """Update selection state of a specific transaction"""
        try:
            for transaction in self.transaction_queue:
                if transaction['id'] == transaction_id:
                    transaction['selected'] = selected
                    break
                    
        except Exception as e:
            self.log_message(f"❌ Error updating selection: {str(e)}")
    
    def submit_selected_transactions(self):
        """Submit all selected transactions for payment"""
        try:
            selected_transactions = [t for t in self.transaction_queue 
                                   if t['selected'] and t['status'] == 'pending']
            
            if not selected_transactions:
                QMessageBox.warning(self, "No Selection", "Please select transactions to process")
                return
            
            # Calculate total amount
            total_amount = sum(t['amount'] for t in selected_transactions)
            
            # Check balance
            current_balance = self.get_current_balance()
            
            if total_amount > current_balance:
                QMessageBox.warning(self, "Insufficient Funds", 
                                   f"Total amount: {total_amount:.8f} PYC\\n"
                                   f"Available balance: {current_balance:.8f} PYC")
                return
            
            # Confirm submission
            reply = QMessageBox.question(self, "Confirm Payments", 
                                       f"Submit {len(selected_transactions)} payments for a total of {total_amount:.8f} PYC?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Process each selected transaction
                successful_payments = 0
                failed_payments = 0
                
                for transaction in selected_transactions:
                    success = self.execute_transaction_payment(transaction)
                    if success:
                        transaction['status'] = 'completed_manual'
                        successful_payments += 1
                    else:
                        transaction['status'] = 'failed'
                        failed_payments += 1
                
                # Show results
                QMessageBox.information(self, "Payment Results", 
                                       f"Payment processing complete:\\n"
                                       f"✅ Successful: {successful_payments}\\n"
                                       f"❌ Failed: {failed_payments}")
                
                self.log_message(f"💸 Batch payment complete: {successful_payments} successful, {failed_payments} failed")
                self.update_transaction_queue_display()
                
        except Exception as e:
            self.log_message(f"❌ Error submitting transactions: {str(e)}")
            QMessageBox.critical(self, "Payment Error", f"Error processing payments: {str(e)}")
    
    def execute_transaction_payment(self, transaction):
        """Execute a single transaction payment"""
        try:
            if not self.wallet or not self.blockchain:
                return False
            
            # Create and send transaction
            tx = self.wallet.send(transaction['to_address'], transaction['amount'])
            
            if tx:
                self.log_message(f"💰 Payment sent: {transaction['amount']:.6f} PYC to {transaction['to_address'][:8]}...")
                
                # Update stats
                self.stats['payments_sent'] = self.stats.get('payments_sent', 0) + 1
                
                # Save blockchain state
                if hasattr(self, 'save_blockchain'):
                    self.save_blockchain()
                
                return True
            else:
                self.log_message(f"❌ Payment failed: {transaction['amount']:.6f} PYC to {transaction['to_address'][:8]}...")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Transaction execution error: {str(e)}")
            return False
    
    def clear_transaction_queue(self):
        """Clear completed/failed transactions from queue"""
        try:
            original_count = len(self.transaction_queue)
            
            # Keep only pending transactions
            self.transaction_queue = [t for t in self.transaction_queue if t['status'] == 'pending']
            
            cleared_count = original_count - len(self.transaction_queue)
            
            if cleared_count > 0:
                self.log_message(f"🗑️ Cleared {cleared_count} completed transactions from queue")
                self.update_transaction_queue_display()
            else:
                QMessageBox.information(self, "Queue Clean", "No completed transactions to clear")
                
        except Exception as e:
            self.log_message(f"❌ Error clearing queue: {str(e)}")'''
    
    # Find a good place to inject the new methods (after the existing methods)
    class_methods_pattern = r'(def closeEvent\(self, event\):.*?event\.accept\(\))'
    
    if re.search(class_methods_pattern, content, re.DOTALL):
        content = re.sub(class_methods_pattern, r'\1' + transaction_queue_method, content, flags=re.DOTALL)
        print("✅ Automatic payments system injection completed")
    else:
        print("❌ Could not find suitable location for payments system injection")
    
    return content

def inject_enhanced_node_server(content):
    """Inject enhanced node server to handle payment requests"""
    
    enhanced_node_server = '''
    def start_enhanced_node_server(self):
        """Start enhanced node server with payment request handling"""
        try:
            if self.node:
                return
            
            host = "0.0.0.0"  # Listen on all interfaces
            port = 5000
            
            if hasattr(self, 'node_host') and self.node_host:
                host_text = self.node_host.text().strip()
                if host_text:
                    host = host_text
            
            if hasattr(self, 'node_port') and self.node_port:
                try:
                    port = self.get_safe_port_from_ui(self.node_port, 5000)
                except:
                    try:
                        port_value = self.node_port.value() if hasattr(self.node_port, 'value') else 5000
                        port = int(port_value)
                        if port < 1024 or port > 65535:
                            port = 5000
                    except:
                        port = 5000
            
            self.log_message(f"🚀 Starting enhanced node server on {host}:{port}")
            
            # Create enhanced node with payment request handling
            self.node = EnhancedPythonCoinNode(
                host=host, 
                port=port, 
                blockchain=self.blockchain, 
                wallet=self.wallet,
                main_wallet_instance=self
            )
            
            # Start node in thread
            threading.Thread(target=self.node.start, daemon=True).start()
            
            if hasattr(self, 'node_status'):
                self.node_status.setText(f"Status: Enhanced node running on {host}:{port}")
            if hasattr(self, 'start_node_button'):
                self.start_node_button.setEnabled(False)
            if hasattr(self, 'stop_node_button'):
                self.stop_node_button.setEnabled(True)
            
            self.log_message(f"✅ Enhanced node server started with payment request handling")
            
        except Exception as e:
            self.log_message(f"❌ Error starting enhanced node: {str(e)}")
            QMessageBox.critical(self, "Node Error", f"Failed to start enhanced node: {str(e)}")'''
    
    # Replace the start_node method
    start_node_pattern = r'(def start_node\(self\):.*?)(\n    def stop_node\(self\):)'
    
    if re.search(start_node_pattern, content, re.DOTALL):
        content = re.sub(start_node_pattern, enhanced_node_server + r'\2', content, flags=re.DOTALL)
        print("✅ Enhanced node server injection completed")
    else:
        print("❌ Could not find start_node method to enhance")
    
    return content

def inject_enhanced_node_class(content):
    """Inject enhanced node class for handling payment requests"""
    
    enhanced_node_class = '''

class EnhancedPythonCoinNode:
    """Enhanced PythonCoin node with payment request handling"""
    
    def __init__(self, host="0.0.0.0", port=5000, blockchain=None, wallet=None, main_wallet_instance=None):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.wallet = wallet
        self.main_wallet = main_wallet_instance
        self.running = False
        self.server = None
        self.pending_payment_requests = []
        
    def start(self):
        """Start the enhanced node server"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json
            import urllib.parse
            
            self.running = True
            
            class EnhancedNodeHandler(BaseHTTPRequestHandler):
                def log_message(self, format, *args):
                    # Custom logging
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[Node {timestamp}] {format % args}")
                
                def do_OPTIONS(self):
                    """Handle CORS preflight requests"""
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                
                def do_GET(self):
                    """Handle GET requests"""
                    try:
                        parsed_path = urllib.parse.urlparse(self.path)
                        path = parsed_path.path
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        if path == '/status':
                            response = {
                                'success': True,
                                'status': 'Enhanced PythonCoin Node Active',
                                'blockchain_height': len(self.server.blockchain.chain) if self.server.blockchain else 0,
                                'pending_transactions': len(self.server.blockchain.pending_transactions) if self.server.blockchain else 0,
                                'pending_payment_requests': len(self.server.pending_payment_requests),
                                'wallet_address': self.server.wallet.address if self.server.wallet else None,
                                'timestamp': datetime.now().isoformat()
                            }
                        elif path == '/blockchain':
                            # Return blockchain info
                            response = {
                                'success': True,
                                'height': len(self.server.blockchain.chain) if self.server.blockchain else 0,
                                'latest_block': self.server.blockchain.chain[-1].to_dict() if self.server.blockchain and self.server.blockchain.chain else None
                            }
                        elif path == '/pending_requests':
                            # Return pending payment requests
                            response = {
                                'success': True,
                                'pending_requests': self.server.pending_payment_requests,
                                'count': len(self.server.pending_payment_requests)
                            }
                        else:
                            response = {
                                'success': False,
                                'error': 'Unknown endpoint',
                                'available_endpoints': ['/status', '/blockchain', '/pending_requests', '/payment_request']
                            }
                        
                        self.wfile.write(json.dumps(response).encode())
                        
                    except Exception as e:
                        error_response = {'success': False, 'error': str(e)}
                        self.wfile.write(json.dumps(error_response).encode())
                
                def do_POST(self):
                    """Handle POST requests including payment requests"""
                    try:
                        content_length = int(self.headers.get('Content-Length', 0))
                        post_data = self.rfile.read(content_length)
                        
                        parsed_path = urllib.parse.urlparse(self.path)
                        path = parsed_path.path
                        
                        # Parse JSON data
                        try:
                            data = json.loads(post_data.decode('utf-8')) if post_data else {}
                        except json.JSONDecodeError:
                            data = {}
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        if path == '/payment_request':
                            # Handle payment request
                            response = self.server.handle_payment_request(data)
                        elif path == '/transaction':
                            # Handle transaction submission
                            response = self.server.handle_transaction_submission(data)
                        elif path == '/sync':
                            # Handle blockchain sync
                            response = self.server.handle_blockchain_sync(data)
                        else:
                            response = {
                                'success': False,
                                'error': f'Unknown POST endpoint: {path}',
                                'available_endpoints': ['/payment_request', '/transaction', '/sync']
                            }
                        
                        self.wfile.write(json.dumps(response).encode())
                        
                    except Exception as e:
                        error_response = {'success': False, 'error': str(e)}
                        self.wfile.write(json.dumps(error_response).encode())
            
            # Create and configure server
            self.server = HTTPServer((self.host, self.port), EnhancedNodeHandler)
            self.server.blockchain = self.blockchain
            self.server.wallet = self.wallet
            self.server.main_wallet = self.main_wallet
            self.server.pending_payment_requests = self.pending_payment_requests
            self.server.handle_payment_request = self.handle_payment_request
            self.server.handle_transaction_submission = self.handle_transaction_submission
            self.server.handle_blockchain_sync = self.handle_blockchain_sync
            
            print(f"[Node] Enhanced PythonCoin node starting on {self.host}:{self.port}")
            
            # Serve requests
            while self.running:
                try:
                    self.server.handle_request()
                except Exception as e:
                    if self.running:
                        print(f"[Node] Request handling error: {e}")
                    break
                    
        except Exception as e:
            print(f"[Node] Enhanced node startup error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.server:
                self.server.server_close()
            print(f"[Node] Enhanced node stopped")
    
    def handle_payment_request(self, data):
        """Handle incoming payment request"""
        try:
            # Validate payment request data
            required_fields = ['from', 'to', 'amount']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Create payment request
            payment_request = {
                'id': str(uuid.uuid4()),
                'from': data['from'],
                'to': data['to'],
                'amount': float(data['amount']),
                'message': data.get('message', ''),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Add to pending requests
            self.pending_payment_requests.append(payment_request)
            
            print(f"[Node] New payment request: {payment_request['amount']} PYC from {payment_request['from'][:8]}...")
            
            # Notify main wallet if available
            if self.main_wallet and hasattr(self.main_wallet, 'add_transaction_to_queue'):
                self.main_wallet.add_transaction_to_queue(payment_request)
            
            return {
                'success': True,
                'message': 'Payment request received',
                'request_id': payment_request['id'],
                'status': 'pending'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_transaction_submission(self, data):
        """Handle transaction submission"""
        try:
            # Validate transaction data
            if not all(key in data for key in ['to', 'amount']):
                return {'success': False, 'error': 'Missing required transaction fields'}
            
            to_address = data['to']
            amount = float(data['amount'])
            
            # Check if we have a wallet to send from
            if not self.wallet:
                return {'success': False, 'error': 'No wallet available for transaction'}
            
            # Attempt to create and send transaction
            tx = self.wallet.send(to_address, amount)
            
            if tx:
                return {
                    'success': True,
                    'message': 'Transaction submitted successfully',
                    'tx_id': tx.tx_id,
                    'amount': amount,
                    'to': to_address
                }
            else:
                return {'success': False, 'error': 'Failed to create transaction'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_blockchain_sync(self, data):
        """Handle blockchain synchronization request"""
        try:
            if not self.blockchain:
                return {'success': False, 'error': 'No blockchain available'}
            
            # Return current blockchain state
            return {
                'success': True,
                'blockchain_height': len(self.blockchain.chain),
                'latest_hash': self.blockchain.chain[-1].hash if self.blockchain.chain else None,
                'pending_transactions': len(self.blockchain.pending_transactions)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop(self):
        """Stop the enhanced node server"""
        self.running = False
        if self.server:
            self.server.server_close()'''
    
    # Find where to inject the enhanced node class (before the main function)
    main_function_pattern = r'(def main\(\):)'
    
    if re.search(main_function_pattern, content):
        content = re.sub(main_function_pattern, enhanced_node_class + r'\n\n\1', content)
        print("✅ Enhanced node class injection completed")
    else:
        print("❌ Could not find main function to inject enhanced node class")
    
    return content

def apply_all_injections(filepath):
    """Apply all enhancements to the PyQt file"""
    print(f"🔧 Starting PyQt wallet enhancement injection...")
    print(f"📁 Target file: {filepath}")
    
    # Create backup
    backup_path = backup_file(filepath)
    
    try:
        # Read the original file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Original file size: {len(content)} characters")
        
        # Apply all injections
        print("\n🔄 Applying enhancements...")
        content = inject_svg_image_support(content)
        content = inject_automatic_payments_system(content)
        content = inject_enhanced_node_server(content)
        content = inject_enhanced_node_class(content)
        
        # Write the enhanced file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 Enhanced file size: {len(content)} characters")
        print(f"✅ PyQt wallet enhancement completed successfully!")
        print(f"🔄 Backup available at: {backup_path}")
        
        # Summary of enhancements
        print("\n📋 ENHANCEMENTS APPLIED:")
        print("✅ SVG image background support")
        print("✅ Automatic payments system")
        print("✅ Transaction queue management")
        print("✅ Enhanced node server with payment requests")
        print("✅ Batch payment processing")
        print("✅ Auto-approval for small payments")
        
        print("\n🚀 NEW FEATURES:")
        print("• Images now appear as backgrounds in SVG ads")
        print("• Payment requests can be received on 0.0.0.0:5000")
        print("• Transaction dropdown with select all/submit all")
        print("• Automatic payment processing for small amounts")
        print("• Enhanced node server with API endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during injection: {str(e)}")
        print(f"🔄 Restoring from backup: {backup_path}")
        
        # Restore backup on error
        try:
            shutil.copy2(backup_path, filepath)
            print("✅ File restored from backup")
        except:
            print("❌ Failed to restore backup")
        
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python injection_script.py <path_to_pyqt.py>")
        sys.exit(1)
    
    pyqt_file = sys.argv[1]
    
    if not os.path.exists(pyqt_file):
        print(f"❌ File not found: {pyqt_file}")
        sys.exit(1)
    
    success = apply_all_injections(pyqt_file)
    
    if success:
        print(f"\n🎉 Enhancement complete! You can now run the enhanced wallet:")
        print(f"python {pyqt_file}")
        print("\n💡 The enhanced features include:")
        print("• SVG ads with image backgrounds")
        print("• Automatic payment processing")
        print("• Payment request handling via node server")
        print("• Batch transaction processing")
        sys.exit(0)
    else:
        print(f"\n❌ Enhancement failed. Check the error messages above.")
        sys.exit(1)