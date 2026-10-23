#!/usr/bin/env python3
"""
Emergency Patch for pyqt.py - Fix immediate AttributeError issues
This will quickly patch the specific lines causing errors
"""

import os
import shutil
import datetime

def create_backup():
    """Create a backup of the current pyqt.py file"""
    if not os.path.exists('pyqt.py'):
        print("❌ Error: pyqt.py file not found!")
        return False
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'pyqt_emergency_backup_{timestamp}.py'
    
    try:
        shutil.copy2('pyqt.py', backup_name)
        print(f"✅ Emergency backup created: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def apply_emergency_patch():
    """Apply emergency patches to fix immediate errors"""
    
    print("🚨 Emergency Patch for PythonCoin Wallet")
    print("=" * 50)
    
    # Create backup first
    if not create_backup():
        return False
    
    # Read the file
    try:
        with open('pyqt.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading pyqt.py: {e}")
        return False
    
    print("📖 Reading pyqt.py...")
    
    # Find and fix the problematic lines
    patches_applied = 0
    
    for i, line in enumerate(lines):
        # Fix line 2168: self.setup_optimized_timers()
        if 'self.setup_optimized_timers()' in line and line.strip().startswith('self.setup_optimized_timers()'):
            print(f"🔧 Commenting out line {i+1}: setup_optimized_timers() call")
            lines[i] = line.replace('self.setup_optimized_timers()', '# self.setup_optimized_timers()  # Temporarily disabled')
            patches_applied += 1
        
        # Fix line 3164: self.optimized_update_ui()
        if 'self.optimized_update_ui()' in line and line.strip().startswith('self.optimized_update_ui()'):
            print(f"🔧 Fixing line {i+1}: replacing optimized_update_ui() with original_update_ui()")
            lines[i] = line.replace('self.optimized_update_ui()', 'self.original_update_ui()')
            patches_applied += 1
        
        # Look for the original update_ui method and rename it
        if line.strip().startswith('def update_ui(self):') and 'original_update_ui' not in line:
            print(f"🔧 Renaming update_ui method to original_update_ui at line {i+1}")
            lines[i] = line.replace('def update_ui(self):', 'def original_update_ui(self):')
            patches_applied += 1
    
    # Add a simple update_ui method that calls original_update_ui
    # Find a good place to insert it (after the original_update_ui method)
    insertion_point = None
    for i, line in enumerate(lines):
        if line.strip().startswith('def original_update_ui(self):'):
            # Find the end of this method
            j = i + 1
            indent_level = len(line) - len(line.lstrip())
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() and not next_line.startswith(' ' * (indent_level + 1)) and not next_line.strip().startswith('#'):
                    insertion_point = j
                    break
                j += 1
            break
    
    if insertion_point:
        # Insert a simple update_ui method
        new_method = [
            '\n',
            '    def update_ui(self):\n',
            '        """Update UI - emergency patch version"""\n',
            '        try:\n',
            '            self.original_update_ui()\n',
            '        except Exception as e:\n',
            '            self.log_message(f"UI update error: {str(e)}")\n',
            '\n'
        ]
        lines[insertion_point:insertion_point] = new_method
        patches_applied += 1
        print("🔧 Added simple update_ui method")
    
    # Add basic missing methods to prevent other errors
    # Find the closeEvent method or end of class
    close_event_pos = None
    for i, line in enumerate(lines):
        if 'def closeEvent(self, event):' in line:
            close_event_pos = i
            break
    
    if close_event_pos:
        # Add basic missing methods before closeEvent
        basic_methods = [
            '\n',
            '    # Emergency patch methods\n',
            '    def setup_optimized_timers(self):\n',
            '        """Emergency patch - basic timer setup"""\n',
            '        try:\n',
            '            # Keep existing update timer but with longer interval\n',
            '            if hasattr(self, "update_timer"):\n',
            '                self.update_timer.stop()\n',
            '                self.update_timer.start(5000)  # 5 seconds\n',
            '        except Exception as e:\n',
            '            self.log_message(f"Timer setup error: {str(e)}")\n',
            '\n',
            '    def optimized_update_ui(self):\n',
            '        """Emergency patch - basic UI update"""\n',
            '        try:\n',
            '            if hasattr(self, "original_update_ui"):\n',
            '                self.original_update_ui()\n',
            '            else:\n',
            '                self.update_wallet_display()\n',
            '        except Exception as e:\n',
            '            self.log_message(f"UI update error: {str(e)}")\n',
            '\n',
            '    def debug_balance_calculation(self):\n',
            '        """Emergency patch - basic balance debug"""\n',
            '        if self.wallet and self.blockchain:\n',
            '            try:\n',
            '                balance = self.wallet.get_balance() if hasattr(self.wallet, "get_balance") else 0\n',
            '                self.log_message(f"Balance: {balance:.8f} PYC")\n',
            '            except Exception as e:\n',
            '                self.log_message(f"Balance debug error: {str(e)}")\n',
            '\n'
        ]
        
        lines[close_event_pos:close_event_pos] = basic_methods
        patches_applied += 1
        print("🔧 Added basic missing methods")
    
    # Write the patched file
    try:
        with open('pyqt.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except Exception as e:
        print(f"❌ Error writing patched file: {e}")
        return False
    
    print(f"✅ Emergency patch applied successfully!")
    print(f"🔧 Applied {patches_applied} patches")
    print("🚀 Try running the wallet now!")
    
    return True

if __name__ == "__main__":
    try:
        success = apply_emergency_patch()
        if success:
            print("\n" + "=" * 50)
            print("✨ Emergency patch completed!")
            print("💡 Run 'python pyqt.py' to test the wallet")
            print("⚠️  This is a quick fix - run the full injector later for complete functionality")
        else:
            print("\n" + "=" * 50)
            print("❌ Emergency patch failed")
    except KeyboardInterrupt:
        print("\n⚠️  Patch cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
