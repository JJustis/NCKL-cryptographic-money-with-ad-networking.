#!/usr/bin/env python3
"""
Enhanced PythonCoin Mining + Ad Creation Tab Injector (FIXED)
Fixes mining issues AND adds complete ad creation functionality
"""

import os
import sys
import re
import shutil
from datetime import datetime

class EnhancedWalletInjector:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"  # Fixed: renamed from backup_file
        self.changes_made = []
        
    def create_backup(self):  # Fixed: renamed method to avoid conflict
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

    # ============================================================================
    # MINING FIXES
    # ============================================================================
    
    def fix_mining_thread_init(self, content):
        """Fix CryptoMiningThread.__init__ method"""
        print("🔧 Fixing CryptoMiningThread.__init__ method...")
        
        old_init_pattern = r'def __init__\(self, blockchain, wallet_address, threads=1\):'
        new_init_pattern = r'def __init__(self, blockchain, wallet, threads=1):'
        
        if old_init_pattern in content:
            content = content.replace(old_init_pattern, new_init_pattern)
            
            # Also fix the assignment
            old_assignment = 'self.wallet_address = wallet_address'
            new_assignment = 'self.wallet = wallet  # Full wallet object'
            
            if old_assignment in content:
                content = content.replace(old_assignment, new_assignment)
                self.changes_made.append("✅ Fixed CryptoMiningThread.__init__ method")
        
        return content
    
    def fix_data_transaction_creation(self, content):
        """Fix DataTransaction creation in mining thread"""
        print("🔧 Fixing DataTransaction creation...")
        
        # Simple pattern replacement
        simple_old = 'sender=self.wallet_address,'
        simple_new = 'sender=self.wallet.public_key,  # Use public key, not address'
        
        if simple_old in content:
            content = content.replace(simple_old, simple_new)
            
            # Add private key parameter
            data_content_pattern = r'data_content=f"Mining block at \{time\.time\(\)\}"'
            data_content_new = 'data_content=f"Mining block at {time.time()}",\n                            private_key=self.wallet.private_key  # Provide private key for signing'
            
            content = re.sub(data_content_pattern, data_content_new, content)
            self.changes_made.append("✅ Fixed DataTransaction creation")
        
        return content
    
    def fix_mining_thread_call(self, content):
        """Fix the CryptoMiningThread instantiation in toggle_mining"""
        print("🔧 Fixing CryptoMiningThread instantiation...")
        
        old_param = 'wallet_address=mining_address,'
        new_param = 'wallet=self.wallet,  # Pass full wallet object'
        
        if old_param in content:
            content = content.replace(old_param, new_param)
            self.changes_made.append("✅ Fixed CryptoMiningThread instantiation")
        
        return content
    
    def fix_mine_pending_transactions_call(self, content):
        """Fix the mine_pending_transactions call in mining thread"""
        print("🔧 Fixing mine_pending_transactions call...")
        
        old_call = 'new_block = self.blockchain.mine_pending_transactions(self.wallet_address)'
        new_call = 'new_block = self.blockchain.mine_pending_transactions(self.wallet.address)'
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            self.changes_made.append("✅ Fixed mine_pending_transactions call")
        
        return content

    # ============================================================================
    # AD CREATION TAB INJECTION
    # ============================================================================
    
    def add_ad_creation_tab_call(self, content):
        """Add the ad creation tab to the create tabs section"""
        print("🎯 Adding ad creation tab call...")
        
        # Find where tabs are created and add ad creation tab
        tab_creation_pattern = r'(self\.create_dashboard_tab\(\)\s*self\.create_wallet_tab\(\)\s*self\.create_mining_tab\(\)\s*self\.create_network_tab\(\))'
        
        if re.search(tab_creation_pattern, content):
            replacement = r'\1\n        self.create_ad_creation_tab()'
            content = re.sub(tab_creation_pattern, replacement, content)
            self.changes_made.append("✅ Added ad creation tab call")
        else:
            # Alternative pattern - look for the last create_*_tab() call
            if 'self.create_network_tab()' in content:
                content = content.replace(
                    'self.create_network_tab()',
                    'self.create_network_tab()\n        self.create_ad_creation_tab()'
                )
                self.changes_made.append("✅ Added ad creation tab call (alternative)")
        
        return content
    
    def inject_ad_creation_tab_method(self, content):
        """Inject the complete ad creation tab method"""
        print("🎯 Injecting ad creation tab method...")
        
        ad_creation_method = '''
    def create_ad_creation_tab(self):
        """Create ad creation and management tab for home advertisers"""
        ad_creation_widget = QWidget()
        ad_creation_layout = QHBoxLayout()
        ad_creation_widget.setLayout(ad_creation_layout)
        
        # Left panel - Ad creation form
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Ad details form
        form_group = QGroupBox("🎯 Create New Advertisement")
        form_layout = QFormLayout()
        
        self.ad_title_input = QLineEdit()
        self.ad_title_input.setPlaceholderText("Enter catchy ad title...")
        self.ad_title_input.textChanged.connect(self.preview_ad)
        form_layout.addRow("Title:", self.ad_title_input)
        
        self.ad_description_input = QTextEdit()
        self.ad_description_input.setPlaceholderText("Describe your product or service...")
        self.ad_description_input.setMaximumHeight(80)
        self.ad_description_input.textChanged.connect(self.preview_ad)
        form_layout.addRow("Description:", self.ad_description_input)
        
        self.ad_category_combo = QComboBox()
        self.ad_category_combo.addItems([
            "technology", "automotive", "fashion", "travel", 
            "food", "sports", "health", "business", "entertainment", 
            "cryptocurrency", "gaming", "education", "finance",
            "real-estate", "home-services", "beauty", "pets"
        ])
        self.ad_category_combo.currentTextChanged.connect(self.preview_ad)
        form_layout.addRow("Category:", self.ad_category_combo)
        
        self.ad_click_url_input = QLineEdit()
        self.ad_click_url_input.setPlaceholderText("https://your-website.com")
        form_layout.addRow("Click URL:", self.ad_click_url_input)
        
        # Payout settings
        payout_layout = QHBoxLayout()
        self.ad_payout_input = QDoubleSpinBox()
        self.ad_payout_input.setDecimals(8)
        self.ad_payout_input.setRange(0.00000001, 1.0)
        self.ad_payout_input.setValue(0.00100000)  # Default 0.00100000 PYC per click
        self.ad_payout_input.valueChanged.connect(self.preview_ad)
        payout_layout.addWidget(self.ad_payout_input)
        payout_layout.addWidget(QLabel("PYC per click"))
        form_layout.addRow("Payout Rate:", payout_layout)
        
        form_group.setLayout(form_layout)
        left_layout.addWidget(form_group)
        
        # Image upload section
        image_group = QGroupBox("🖼️ Ad Image")
        image_layout = QVBoxLayout()
        
        self.upload_image_btn = QPushButton("📁 Upload Image")
        self.upload_image_btn.clicked.connect(self.upload_ad_image)
        image_layout.addWidget(self.upload_image_btn)
        
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setWordWrap(True)
        self.image_path_label.setStyleSheet("color: #666; font-style: italic;")
        image_layout.addWidget(self.image_path_label)
        
        # Image preview
        self.image_preview_label = QLabel()
        self.image_preview_label.setFixedSize(150, 100)
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; background: #f8f9fa;")
        self.image_preview_label.setText("Image Preview")
        image_layout.addWidget(self.image_preview_label)
        
        image_group.setLayout(image_layout)
        left_layout.addWidget(image_group)
        
        # Targeting options
        targeting_group = QGroupBox("🎯 Targeting Options")
        targeting_layout = QVBoxLayout()
        
        targeting_layout.addWidget(QLabel("Target Interests:"))
        self.target_interests = QLineEdit()
        self.target_interests.setPlaceholderText("technology, gaming, crypto (comma-separated)")
        targeting_layout.addWidget(self.target_interests)
        
        targeting_layout.addWidget(QLabel("Geographic Targeting:"))
        self.target_geo = QComboBox()
        self.target_geo.addItems(["Global", "North America", "Europe", "Asia", "Local"])
        targeting_layout.addWidget(self.target_geo)
        
        targeting_group.setLayout(targeting_layout)
        left_layout.addWidget(targeting_group)
        
        # Budget settings
        budget_group = QGroupBox("💰 Budget Settings")
        budget_layout = QFormLayout()
        
        self.daily_budget_input = QDoubleSpinBox()
        self.daily_budget_input.setDecimals(8)
        self.daily_budget_input.setRange(0.001, 10000)
        self.daily_budget_input.setValue(1.0)
        budget_layout.addRow("Daily Budget (PYC):", self.daily_budget_input)
        
        self.max_clicks_input = QSpinBox()
        self.max_clicks_input.setRange(1, 100000)
        self.max_clicks_input.setValue(1000)
        budget_layout.addRow("Max Clicks/Day:", self.max_clicks_input)
        
        budget_group.setLayout(budget_layout)
        left_layout.addWidget(budget_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self.preview_ad)
        action_layout.addWidget(preview_btn)
        
        create_btn = QPushButton("🚀 Create & Publish")
        create_btn.clicked.connect(self.create_advertisement)
        create_btn.setStyleSheet("background-color: #28a745; font-size: 14px; padding: 10px;")
        action_layout.addWidget(create_btn)
        
        left_layout.addLayout(action_layout)
        left_layout.addStretch()
        
        ad_creation_layout.addWidget(left_panel)
        
        # Right panel - Ad preview and management
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Preview section
        preview_group = QGroupBox("👁️ Live Preview")
        preview_layout = QVBoxLayout()
        
        self.ad_preview_area = QTextEdit()
        self.ad_preview_area.setHtml(self.get_default_preview_html())
        self.ad_preview_area.setMaximumHeight(250)
        self.ad_preview_area.setReadOnly(True)
        preview_layout.addWidget(self.ad_preview_area)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # My ads management
        my_ads_group = QGroupBox("📊 My Advertisements")
        my_ads_layout = QVBoxLayout()
        
        self.my_ads_table = QTableWidget()
        self.my_ads_table.setColumnCount(7)
        self.my_ads_table.setHorizontalHeaderLabels(["Title", "Category", "Payout", "Clicks", "Spent", "Status", "Actions"])
        
        my_ads_header = self.my_ads_table.horizontalHeader()
        my_ads_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        my_ads_layout.addWidget(self.my_ads_table)
        
        # My ads controls
        my_ads_controls = QHBoxLayout()
        
        edit_ad_btn = QPushButton("✏️ Edit Selected")
        edit_ad_btn.clicked.connect(self.edit_advertisement)
        my_ads_controls.addWidget(edit_ad_btn)
        
        pause_ad_btn = QPushButton("⏸️ Pause Selected")
        pause_ad_btn.clicked.connect(self.pause_advertisement)
        my_ads_controls.addWidget(pause_ad_btn)
        
        delete_ad_btn = QPushButton("🗑️ Delete Selected")
        delete_ad_btn.clicked.connect(self.delete_advertisement)
        delete_ad_btn.setStyleSheet("background-color: #dc3545;")
        my_ads_controls.addWidget(delete_ad_btn)
        
        my_ads_controls.addStretch()
        
        refresh_ads_btn = QPushButton("🔄 Refresh")
        refresh_ads_btn.clicked.connect(self.update_my_ads_table)
        my_ads_controls.addWidget(refresh_ads_btn)
        
        my_ads_layout.addLayout(my_ads_controls)
        
        my_ads_group.setLayout(my_ads_layout)
        right_layout.addWidget(my_ads_group)
        
        # Ad network stats
        stats_group = QGroupBox("📈 Ad Network Statistics")
        stats_layout = QVBoxLayout()
        
        self.ad_stats_layout = QVBoxLayout()
        self.update_ad_network_stats()
        stats_layout.addLayout(self.ad_stats_layout)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        ad_creation_layout.addWidget(right_panel)
        
        self.tab_widget.addTab(ad_creation_widget, "🎯 Create Ads")
    
    def get_default_preview_html(self):
        """Get default preview HTML for ad"""
        return """
        <div style="border: 2px solid #0066cc; border-radius: 12px; padding: 15px; background: white; margin: 10px; position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">💎 PYC</div>
            <h3 style="color: #0066cc; margin: 0 0 10px 0; font-size: 18px;">Your Ad Preview</h3>
            <p style="color: #666; margin: 0 0 10px 0; font-size: 14px;">Fill in the form to see your ad preview here...</p>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-top: 10px;">
                <span style="color: #0066cc;">📱 Category • 🌐 P2P Network</span>
                <span style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold;">+0.00100000 PYC per click</span>
            </div>
        </div>
        """
'''
        
        # Find a good place to inject this method - after the last create_*_tab method
        injection_point = None
        
        # Look for the last tab creation method
        tab_methods = [
            'def create_network_tab(self):',
            'def create_mining_tab(self):',
            'def create_wallet_tab(self):',
            'def create_dashboard_tab(self):'
        ]
        
        for method in tab_methods:
            if method in content:
                # Find the end of this method (next method or class method)
                method_start = content.find(method)
                if method_start != -1:
                    # Find the end of the method (next def or end of class)
                    method_end = method_start
                    lines = content[method_start:].split('\n')
                    indent_level = None
                    
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == '':
                            continue
                        
                        if indent_level is None and line.strip():
                            # First non-empty line after method def
                            indent_level = len(line) - len(line.lstrip())
                        
                        if line.strip() and (len(line) - len(line.lstrip())) <= 4:  # Back to class level
                            if line.strip().startswith('def ') or line.strip().startswith('class '):
                                method_end = method_start + len('\n'.join(lines[:i]))
                                break
                    
                    injection_point = method_end
                    break
        
        if injection_point:
            content = content[:injection_point] + ad_creation_method + content[injection_point:]
            self.changes_made.append("✅ Injected ad creation tab method")
        else:
            # Fallback - add before the signal handlers section
            signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
            if re.search(signal_handlers_pattern, content):
                content = re.sub(signal_handlers_pattern, ad_creation_method + r'\1', content)
                self.changes_made.append("✅ Injected ad creation tab method (fallback)")
        
        return content
    
    def inject_ad_creation_methods(self, content):
        """Inject supporting methods for ad creation"""
        print("🎯 Injecting ad creation support methods...")
        
        support_methods = '''
    # ============================================================================
    # Ad Creation Support Methods
    # ============================================================================
    
    def preview_ad(self):
        """Preview the advertisement as user types"""
        if not hasattr(self, 'ad_title_input'):
            return
        
        title = self.ad_title_input.text().strip() or "Your Ad Title Here"
        description = self.ad_description_input.toPlainText().strip() or "Your ad description will appear here..."
        category = self.ad_category_combo.currentText() if hasattr(self, 'ad_category_combo') else "technology"
        payout = self.ad_payout_input.value() if hasattr(self, 'ad_payout_input') else 0.00100000
        
        # Truncate description if too long
        if len(description) > 120:
            description = description[:120] + "..."
        
        preview_html = f"""
        <div style="border: 2px solid #0066cc; border-radius: 12px; padding: 15px; background: white; margin: 10px; position: relative; transition: all 0.3s ease;">
            <div style="position: absolute; top: 10px; right: 10px; background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">💎 PYC</div>
            <h3 style="color: #0066cc; margin: 0 0 10px 0; font-size: 18px; font-weight: 700;">{title}</h3>
            <p style="color: #666; margin: 0 0 10px 0; font-size: 14px; line-height: 1.5;">{description}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-top: 10px;">
                <span style="color: #0066cc;">📱 {category} • 🌐 P2P Network</span>
                <span style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold;">+{payout:.8f} PYC per click</span>
            </div>
        </div>
        """
        
        if hasattr(self, 'ad_preview_area'):
            self.ad_preview_area.setHtml(preview_html)
    
    def upload_ad_image(self):
        """Upload image for advertisement"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Ad Image", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.webp);;All Files (*)"
        )
        
        if file_path:
            self.current_ad_image = file_path
            filename = os.path.basename(file_path)
            self.image_path_label.setText(f"Selected: {filename}")
            self.image_path_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            # Show image preview
            try:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(150, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.image_preview_label.setPixmap(scaled_pixmap)
                    self.image_preview_label.setText("")
                else:
                    self.image_preview_label.setText("Invalid Image")
            except Exception as e:
                self.image_preview_label.setText("Preview Error")
                logger.warning(f"Image preview error: {e}")
    
    def create_advertisement(self):
        """Create and publish advertisement to P2P network"""
        if not self.wallet:
            QMessageBox.warning(self, "Ad Creation Error", "No wallet loaded")
            return
        
        title = self.ad_title_input.text().strip()
        description = self.ad_description_input.toPlainText().strip()
        click_url = self.ad_click_url_input.text().strip()
        category = self.ad_category_combo.currentText()
        payout_rate = self.ad_payout_input.value()
        daily_budget = self.daily_budget_input.value()
        max_clicks = self.max_clicks_input.value()
        
        # Validation
        if not title or not description:
            QMessageBox.warning(self, "Validation Error", "Please fill in title and description")
            return
        
        if len(title) < 5:
            QMessageBox.warning(self, "Validation Error", "Title must be at least 5 characters")
            return
        
        if len(description) < 20:
            QMessageBox.warning(self, "Validation Error", "Description must be at least 20 characters")
            return
        
        if not click_url.startswith(('http://', 'https://')):
            click_url = 'https://' + click_url if click_url else 'https://example.com'
        
        # Check if advertiser has enough balance for at least one day of ads
        balance = self.wallet.get_balance()
        if balance < daily_budget:
            QMessageBox.warning(self, "Insufficient Funds", 
                               f"You need at least {daily_budget:.8f} PYC for one day of advertising.\\n"
                               f"Current balance: {balance:.8f} PYC")
            return
        
        try:
            # Create ad object
            ad_id = str(uuid.uuid4())
            
            # Get image URL (in real implementation, upload to IPFS or similar)
            image_url = ""
            if hasattr(self, 'current_ad_image'):
                image_url = f"file://{self.current_ad_image}"  # Local file for demo
            
            # Get targeting options
            interests = [i.strip() for i in self.target_interests.text().split(',') if i.strip()]
            targeting = {
                'interests': interests,
                'geographic': self.target_geo.currentText(),
                'budget_daily': daily_budget,
                'max_clicks_daily': max_clicks
            }
            
            ad = AdContent(
                id=ad_id,
                title=title,
                description=description,
                image_url=image_url,
                click_url=click_url,
                category=category,
                targeting=targeting,
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(days=30)).isoformat(),
                peer_source=self.client_id,
                payout_rate=payout_rate,
                advertiser_address=self.wallet.address
            )
            
            # Add to local ads
            self.ads.append(ad)
            
            # Broadcast to P2P network if connected
            if self.p2p_manager and self.p2p_manager.running:
                self.broadcast_new_ad(ad)
            
            # Update my ads table
            self.update_my_ads_table()
            
            # Clear form
            self.clear_ad_form()
            
            QMessageBox.information(self, "Success", 
                                   f"Advertisement '{title}' created successfully!\\n\\n"
                                   f"• Payout: {payout_rate:.8f} PYC per click\\n"
                                   f"• Daily Budget: {daily_budget:.8f} PYC\\n"
                                   f"• Max Clicks: {max_clicks:,}\\n\\n"
                                   f"Your ad is now live on the P2P network!")
            
            self.log_message(f"Created new advertisement: {title}")
            
            # Update stats
            self.stats['ads_served'] += 1
            
        except Exception as e:
            self.log_message(f"Error creating advertisement: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to create advertisement: {str(e)}")
    
    def clear_ad_form(self):
        """Clear the ad creation form"""
        self.ad_title_input.clear()
        self.ad_description_input.clear()
        self.ad_click_url_input.clear()
        self.target_interests.clear()
        self.ad_payout_input.setValue(0.00100000)
        self.daily_budget_input.setValue(1.0)
        self.max_clicks_input.setValue(1000)
        self.image_path_label.setText("No image selected")
        self.image_path_label.setStyleSheet("color: #666; font-style: italic;")
        self.image_preview_label.clear()
        self.image_preview_label.setText("Image Preview")
        if hasattr(self, 'current_ad_image'):
            delattr(self, 'current_ad_image')
        self.ad_preview_area.setHtml(self.get_default_preview_html())
    
    def broadcast_new_ad(self, ad):
        """Broadcast new ad to P2P network"""
        if not self.p2p_manager or not self.p2p_manager.running:
            return
        
        broadcast_message = {
            'type': 'new_ad_broadcast',
            'ad_data': ad.to_dict(),
            'broadcaster': self.client_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connected peers
        for peer_id, sock in self.p2p_manager.peer_sockets.items():
            try:
                self.p2p_manager._send_message(sock, broadcast_message)
            except Exception as e:
                logger.error(f"Failed to broadcast ad to peer {peer_id}: {e}")
    
    def update_my_ads_table(self):
        """Update my advertisements table"""
        if not hasattr(self, 'my_ads_table'):
            return
        
        my_ads = [ad for ad in self.ads if ad.advertiser_address == self.wallet.address]
        
        self.my_ads_table.setRowCount(len(my_ads))
        
        for row, ad in enumerate(my_ads):
            # Title
            title_item = QTableWidgetItem(ad.title)
            title_item.setToolTip(ad.description)
            self.my_ads_table.setItem(row, 0, title_item)
            
            # Category
            self.my_ads_table.setItem(row, 1, QTableWidgetItem(ad.category.title()))
            
            # Payout
            payout_item = QTableWidgetItem(f"{ad.payout_rate:.8f}")
            payout_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.my_ads_table.setItem(row, 2, payout_item)
            
            # Count clicks and calculate spent
            ad_clicks = len([c for c in self.click_events if c.ad_id == ad.id])
            spent = ad_clicks * ad.payout_rate
            
            clicks_item = QTableWidgetItem(str(ad_clicks))
            clicks_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.my_ads_table.setItem(row, 3, clicks_item)
            
            spent_item = QTableWidgetItem(f"{spent:.8f}")
            spent_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.my_ads_table.setItem(row, 4, spent_item)
            
            # Status
            status = "Active" if datetime.now().isoformat() < ad.expires_at else "Expired"
            status_item = QTableWidgetItem(status)
            if status == "Active":
                status_item.setForeground(QColor(40, 167, 69))  # Green
            else:
                status_item.setForeground(QColor(220, 53, 69))  # Red
            self.my_ads_table.setItem(row, 5, status_item)
            
            # Actions (simple text for now)
            actions_item = QTableWidgetItem("📊 View Stats")
            self.my_ads_table.setItem(row, 6, actions_item)
    
    def update_ad_network_stats(self):
        """Update ad network statistics display"""
        if not hasattr(self, 'ad_stats_layout'):
            return
        
        # Clear existing widgets
        for i in reversed(range(self.ad_stats_layout.count())): 
            self.ad_stats_layout.itemAt(i).widget().setParent(None)
        
        # Calculate stats
        my_ads = [ad for ad in self.ads if ad.advertiser_address == self.wallet.address]
        total_clicks = len([c for c in self.click_events if any(c.ad_id == ad.id for ad in my_ads)])
        total_spent = sum(c.payout_amount for c in self.click_events if any(c.ad_id == ad.id for ad in my_ads))
        avg_cpc = total_spent / max(1, total_clicks)
        
        # Create stats labels
        stats = [
            f"📊 My Active Ads: {len(my_ads)}",
            f"👆 Total Clicks: {total_clicks:,}",
            f"💸 Total Spent: {total_spent:.8f} PYC",
            f"📈 Average CPC: {avg_cpc:.8f} PYC",
            f"🌐 Network Ads: {len(self.ads)}",
            f"👥 Connected Peers: {len([p for p in self.peers.values() if p.status == 'connected'])}"
        ]
        
        for stat in stats:
            label = QLabel(stat)
            label.setStyleSheet("color: #333; font-size: 12px; padding: 2px;")
            self.ad_stats_layout.addWidget(label)
    
    def edit_advertisement(self):
        """Edit selected advertisement"""
        current_row = self.my_ads_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an advertisement to edit")
            return
        
        my_ads = [ad for ad in self.ads if ad.advertiser_address == self.wallet.address]
        if current_row < len(my_ads):
            ad = my_ads[current_row]
            
            # Populate form with existing data
            self.ad_title_input.setText(ad.title)
            self.ad_description_input.setPlainText(ad.description)
            self.ad_click_url_input.setText(ad.click_url)
            self.ad_payout_input.setValue(ad.payout_rate)
            
            # Set category
            category_index = self.ad_category_combo.findText(ad.category)
            if category_index >= 0:
                self.ad_category_combo.setCurrentIndex(category_index)
            
            # Set targeting
            interests = ad.targeting.get('interests', [])
            self.target_interests.setText(', '.join(interests))
            
            self.preview_ad()
    
    def pause_advertisement(self):
        """Pause/resume selected advertisement"""
        current_row = self.my_ads_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an advertisement")
            return
        
        QMessageBox.information(self, "Ad Paused", "Advertisement has been paused\\n(Feature coming soon)")
    
    def delete_advertisement(self):
        """Delete selected advertisement"""
        current_row = self.my_ads_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an advertisement to delete")
            return
        
        my_ads = [ad for ad in self.ads if ad.advertiser_address == self.wallet.address]
        if current_row < len(my_ads):
            ad_to_remove = my_ads[current_row]
            
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Are you sure you want to delete '{ad_to_remove.title}'?\\n\\n"
                                       f"This action cannot be undone.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.ads.remove(ad_to_remove)
                self.update_my_ads_table()
                QMessageBox.information(self, "Ad Deleted", "Advertisement has been deleted")
                self.log_message(f"Deleted advertisement: {ad_to_remove.title}")
'''
        
        # Inject before the existing signal handlers
        signal_handlers_pattern = r'(\s*# ============================================================================\s*# Signal Handlers)'
        if re.search(signal_handlers_pattern, content):
            content = re.sub(signal_handlers_pattern, support_methods + r'\1', content)
            self.changes_made.append("✅ Injected ad creation support methods")
        
        return content
    
    def update_ui_update_method(self, content):
        """Update the update_ui method to include ad stats"""
        print("🔧 Updating UI update method for ad stats...")
        
        # Look for the update_ui method and add ad stats update
        ui_update_pattern = r'(def update_ui\(self\):.*?self\.update_network_display\(\))'
        
        if re.search(ui_update_pattern, content, re.DOTALL):
            replacement = r'\1\n            self.update_ad_network_stats()'
            content = re.sub(ui_update_pattern, replacement, content, flags=re.DOTALL)
            self.changes_made.append("✅ Updated UI update method for ad stats")
        
        return content

    # ============================================================================
    # MAIN INJECTION ORCHESTRATION
    # ============================================================================
    
    def apply_all_fixes(self):
        """Apply all fixes and enhancements"""
        print("🚀 Enhanced PythonCoin Wallet Injector")
        print("=" * 60)
        print("This will fix mining issues AND add complete ad creation functionality")
        print()
        
        # Check if target file exists
        if not os.path.exists(self.target_file):
            print(f"❌ Target file not found: {self.target_file}")
            return False
        
        # Create backup
        if not self.create_backup():  # Fixed: using renamed method
            return False
        
        # Read original content
        content = self.read_file()
        if content is None:
            return False
        
        # Apply mining fixes first
        print("\n🔧 PHASE 1: Mining Fixes")
        print("-" * 30)
        content = self.fix_mining_thread_init(content)
        content = self.fix_data_transaction_creation(content)
        content = self.fix_mining_thread_call(content)
        content = self.fix_mine_pending_transactions_call(content)
        
        # Apply ad creation enhancements
        print("\n🎯 PHASE 2: Ad Creation Features")
        print("-" * 30)
        content = self.add_ad_creation_tab_call(content)
        content = self.inject_ad_creation_tab_method(content)
        content = self.inject_ad_creation_methods(content)
        content = self.update_ui_update_method(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 60)
            print("All enhancements applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed (file might already be enhanced)")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")  # Fixed: using renamed attribute
            print("\n🚀 NEW FEATURES ADDED:")
            print("  💰 Fixed mining transaction creation")
            print("  🎯 Complete ad creation tab")
            print("  📊 Ad management and statistics")
            print("  🖼️ Image upload for ads")
            print("  🎯 Targeting options")
            print("  💸 Budget controls")
            print("  🌐 P2P ad broadcasting")
            print("  📈 Real-time ad statistics")
            print("\n✨ Your wallet now supports home advertisers making deals with web developers!")
            print("   Default payout: 0.00100000 PYC per click")
            print("   Advertisers can set higher payouts to attract more traffic")
            
            return True
        
        return False

def main():
    """Main function"""
    print("🚀 Enhanced PythonCoin Wallet Injector (FIXED)")
    print("Fixes mining + adds complete ad creation features!")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create injector and apply fixes
    injector = EnhancedWalletInjector(target_file)
    
    try:
        success = injector.apply_all_fixes()
        
        if success:
            print("\n✅ All enhancements applied successfully!")
            print("Your wallet now has:")
            print("  🔧 Fixed mining")
            print("  🎯 Ad creation for home advertisers")
            print("  💰 0.00100000 PYC default per click")
            print("  📊 Complete ad management")
        else:
            print("\n❌ Some enhancements failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()