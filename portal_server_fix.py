#!/usr/bin/env python3
"""
Fix for EnhancedDeveloperPortalServer class name mismatch
"""

import os
import shutil
import datetime

def fix_portal_server_class():
    """Fix the EnhancedDeveloperPortalServer class name issue"""
    
    print("🔧 Fixing EnhancedDeveloperPortalServer class issue...")
    
    # Create backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'pyqt_portal_fix_backup_{timestamp}.py'
    
    try:
        shutil.copy2('pyqt.py', backup_name)
        print(f"✅ Backup created: {backup_name}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False
    
    # Read file
    try:
        with open('pyqt.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Fix class name inconsistency
    fixes_applied = 0
    
    # Replace double-enhanced class name with single
    if 'class EnhancedEnhancedDeveloperPortalServer' in content:
        content = content.replace('class EnhancedEnhancedDeveloperPortalServer', 'class EnhancedDeveloperPortalServer')
        fixes_applied += 1
        print("🔧 Fixed double-enhanced class name")
    
    # Add missing portal server methods to the main wallet class
    portal_methods = '''
    # ============================================================================
    # Developer Portal Server Methods
    # ============================================================================
    
    def start_portal_server(self):
        """Start the developer portal server"""
        if not self.wallet:
            QMessageBox.warning(self, "Portal Error", "No wallet loaded")
            return
        
        if self.portal_server and self.portal_server.isRunning():
            QMessageBox.information(self, "Portal Info", "Portal server is already running")
            return
        
        try:
            self.portal_server = EnhancedDeveloperPortalServer(self.wallet, self.blockchain, 8082)
            
            # Connect signals if they exist
            if hasattr(self.portal_server, 'status_update'):
                self.portal_server.status_update.connect(self.on_portal_status_update)
            if hasattr(self.portal_server, 'click_received'):
                self.portal_server.click_received.connect(self.on_portal_click_received)
            if hasattr(self.portal_server, 'developer_registered'):
                self.portal_server.developer_registered.connect(self.on_developer_registered)
            
            self.portal_server.start()
            
            self.portal_enabled = True
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Starting...")
            
            self.log_message("Developer portal server starting...")
            
        except Exception as e:
            self.log_message(f"Error starting portal server: {str(e)}")
            QMessageBox.critical(self, "Portal Error", f"Failed to start server: {str(e)}")
    
    def stop_portal_server(self):
        """Stop the developer portal server"""
        try:
            if self.portal_server:
                self.portal_server.stop()
                if hasattr(self.portal_server, 'wait'):
                    self.portal_server.wait()
                self.portal_server = None
            
            self.portal_enabled = False
            if hasattr(self, 'portal_status'):
                self.portal_status.setText("Status: Offline")
            
            self.log_message("Developer portal server stopped")
            
        except Exception as e:
            self.log_message(f"Error stopping portal server: {str(e)}")
    
    def on_portal_status_update(self, status):
        """Handle portal server status updates"""
        self.log_message(f"Portal: {status}")
        
        if hasattr(self, 'portal_status'):
            if "server started" in status.lower() or "running" in status.lower():
                self.portal_status.setText("Status: Online ✅")
            elif "error" in status.lower():
                self.portal_status.setText("Status: Error ❌")
    
    def on_portal_click_received(self, click_data):
        """Handle ad click from portal"""
        developer = click_data.get('developer', 'Unknown')
        amount = click_data.get('amount', 0)
        
        self.log_message(f"💰 Portal click: {amount:.6f} PYC -> {developer}")
        
        if hasattr(self, 'save_blockchain'):
            self.save_blockchain()
    
    def on_developer_registered(self, developer, address):
        """Handle developer registration"""
        self.log_message(f"👤 Developer registered: {developer} -> {address[:8]}...")

'''
    
    # Find insertion point for portal methods
    closeEvent_pos = content.find('def closeEvent(self, event):')
    if closeEvent_pos == -1:
        closeEvent_pos = content.find('    def closeEvent(self, event):')
    
    if closeEvent_pos != -1:
        # Check if portal methods already exist
        if 'def start_portal_server(self):' not in content:
            content = content[:closeEvent_pos] + portal_methods + '\n' + content[closeEvent_pos:]
            fixes_applied += 1
            print("🔧 Added missing portal server methods")
    
    # Add missing signal handlers for mining if they don't exist
    missing_handlers = []
    
    if 'def on_mining_status_update(self, status):' not in content:
        missing_handlers.append('''
    def on_mining_status_update(self, status):
        """Handle mining status updates"""
        if hasattr(self, 'mining_log'):
            self.mining_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {status}")
            self.mining_log.ensureCursorVisible()
''')
    
    if 'def on_mining_hashrate_update(self, hashrate):' not in content:
        missing_handlers.append('''
    def on_mining_hashrate_update(self, hashrate):
        """Handle mining hashrate updates"""
        if hasattr(self, 'mining_hashrate'):
            self.mining_hashrate.setText(f"Hash Rate: {hashrate:.2f} H/s")
        if hasattr(self, 'mining_hashrate_label'):
            self.mining_hashrate_label.setText(f"Hash Rate: {hashrate:.2f} H/s")
''')
    
    if 'def on_new_block_mined(self, block):' not in content:
        missing_handlers.append('''
    def on_new_block_mined(self, block):
        """Handle new block mined"""
        self.stats['blocks_mined'] += 1
        if hasattr(self, 'blocks_mined_count'):
            self.blocks_mined_count.setText(f"Blocks Mined: {self.stats['blocks_mined']}")
        
        self.log_message(f"Block mined! Height: {block.index}, Hash: {block.hash[:16]}...")
''')
    
    if missing_handlers:
        # Add missing handlers before closeEvent
        closeEvent_pos = content.find('def closeEvent(self, event):')
        if closeEvent_pos == -1:
            closeEvent_pos = content.find('    def closeEvent(self, event):')
        
        if closeEvent_pos != -1:
            handlers_code = '\n'.join(missing_handlers) + '\n'
            content = content[:closeEvent_pos] + handlers_code + content[closeEvent_pos:]
            fixes_applied += len(missing_handlers)
            print(f"🔧 Added {len(missing_handlers)} missing signal handlers")
    
    # Write fixed content
    try:
        with open('pyqt.py', 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error writing fixed file: {e}")
        return False
    
    print(f"✅ Portal server fixes applied: {fixes_applied} changes made")
    return True

if __name__ == "__main__":
    try:
        success = fix_portal_server_class()
        if success:
            print("\n🎉 Portal server fix completed!")
            print("💡 Try running 'python pyqt.py' now")
        else:
            print("\n❌ Fix failed")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
