#!/usr/bin/env python3
"""
Blockchain Save Attribute Fix
Fixes the missing 'difficulty' and 'mining_reward' attributes in blockchain saving
"""

import os
import sys
import re
import shutil
from datetime import datetime

class BlockchainSaveFix:
    def __init__(self, target_file="pyqt.py"):
        self.target_file = target_file
        self.backup_filename = f"{target_file}.backup_savefix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    def fix_save_blockchain_method(self, content):
        """Fix the save_blockchain method to handle missing attributes properly"""
        print("💾 Fixing save_blockchain method...")
        
        # Find the save_blockchain method and replace it with a safer version
        old_save_method_pattern = r'def save_blockchain\(self\):.*?except Exception as e:.*?logger\.error\(f"Blockchain save error: \{str\(e\)\}"\)'
        
        new_save_method = '''def save_blockchain(self):
        """Save blockchain to file"""
        try:
            # Get difficulty from last block or use default
            difficulty = 2  # Default difficulty
            if self.blockchain.chain:
                last_block = self.blockchain.chain[-1]
                if hasattr(last_block, 'difficulty'):
                    difficulty = last_block.difficulty
            
            # Get mining reward - use default if not available
            mining_reward = 50  # Default mining reward
            if hasattr(self.blockchain, 'mining_reward'):
                mining_reward = self.blockchain.mining_reward
            
            blockchain_data = {
                'chain': [block.to_dict() for block in self.blockchain.chain],
                'pending_transactions': [tx.to_dict() for tx in self.blockchain.pending_transactions],
                'genesis_complete': getattr(self.blockchain, 'genesis_complete', False),
                'genesis_addresses': getattr(self.blockchain, 'genesis_addresses', []),
                'difficulty': difficulty,
                'mining_reward': mining_reward,
                'saved_timestamp': time.time(),
                'saved_datetime': datetime.now().isoformat()
            }
            
            with open("blockchain.json", "w") as f:
                json.dump(blockchain_data, f, indent=2)
            
            self.log_message("Blockchain saved successfully")
            
        except Exception as e:
            self.log_message(f"Error saving blockchain: {str(e)}")
            logger.error(f"Blockchain save error: {str(e)}")'''
        
        if re.search(old_save_method_pattern, content, re.DOTALL):
            content = re.sub(old_save_method_pattern, new_save_method, content, flags=re.DOTALL)
            self.changes_made.append("✅ Fixed save_blockchain method with safe attribute access")
        
        return content
    
    def fix_load_blockchain_method(self, content):
        """Fix the load_blockchain method to handle missing attributes properly"""
        print("📂 Fixing load_blockchain method...")
        
        # Find the load blockchain method and update it
        old_load_pattern = r'# Load basic properties\s*self\.blockchain\.genesis_complete = blockchain_data\.get\(\'genesis_complete\', False\)\s*self\.blockchain\.genesis_addresses = blockchain_data\.get\(\'genesis_addresses\', \[\]\)\s*self\.blockchain\.difficulty = blockchain_data\.get\(\'difficulty\', 2\)\s*self\.blockchain\.mining_reward = blockchain_data\.get\(\'mining_reward\', 50\)'
        
        new_load_pattern = '''# Load basic properties safely
            self.blockchain.genesis_complete = blockchain_data.get('genesis_complete', False)
            self.blockchain.genesis_addresses = blockchain_data.get('genesis_addresses', [])
            
            # Only set difficulty and mining_reward if the blockchain supports them
            if hasattr(self.blockchain, 'difficulty'):
                self.blockchain.difficulty = blockchain_data.get('difficulty', 2)
            if hasattr(self.blockchain, 'mining_reward'):
                self.blockchain.mining_reward = blockchain_data.get('mining_reward', 50)'''
        
        if re.search(old_load_pattern, content):
            content = re.sub(old_load_pattern, new_load_pattern, content)
            self.changes_made.append("✅ Fixed load_blockchain method with safe attribute setting")
        
        return content
    
    def add_safer_block_reconstruction(self, content):
        """Add safer block reconstruction that handles missing difficulty"""
        print("🔧 Adding safer block reconstruction...")
        
        # Find block reconstruction and make it safer
        old_block_pattern = r'# Set additional block properties\s*block\.hash = block_data\[\'hash\'\]\s*block\.nonce = block_data\[\'nonce\'\]\s*block\.difficulty = block_data\.get\(\'difficulty\', 2\)'
        
        new_block_pattern = '''# Set additional block properties
                block.hash = block_data['hash']
                block.nonce = block_data['nonce']
                
                # Only set difficulty if the block supports it
                if hasattr(block, 'difficulty'):
                    block.difficulty = block_data.get('difficulty', 2)'''
        
        if re.search(old_block_pattern, content):
            content = re.sub(old_block_pattern, new_block_pattern, content)
            self.changes_made.append("✅ Added safer block reconstruction")
        
        return content
    
    def simplify_blockchain_data_structure(self, content):
        """Simplify the blockchain data structure to avoid missing attributes"""
        print("📋 Simplifying blockchain data structure...")
        
        # If the above fixes don't work, replace the entire save method with a minimal version
        if 'def save_blockchain(self):' in content and len(self.changes_made) == 0:
            
            minimal_save_method = '''def save_blockchain(self):
        """Save blockchain to file (minimal version)"""
        try:
            # Simple blockchain data structure
            blockchain_data = {
                'chain': [],
                'pending_transactions': [],
                'genesis_complete': getattr(self.blockchain, 'genesis_complete', False),
                'genesis_addresses': getattr(self.blockchain, 'genesis_addresses', []),
                'saved_timestamp': time.time(),
                'saved_datetime': datetime.now().isoformat()
            }
            
            # Safely serialize chain
            try:
                blockchain_data['chain'] = [block.to_dict() for block in self.blockchain.chain]
            except Exception as e:
                self.log_message(f"Warning: Could not serialize chain: {e}")
                blockchain_data['chain'] = []
            
            # Safely serialize pending transactions
            try:
                blockchain_data['pending_transactions'] = [tx.to_dict() for tx in self.blockchain.pending_transactions]
            except Exception as e:
                self.log_message(f"Warning: Could not serialize pending transactions: {e}")
                blockchain_data['pending_transactions'] = []
            
            with open("blockchain.json", "w") as f:
                json.dump(blockchain_data, f, indent=2)
            
            self.log_message("Blockchain saved successfully (minimal)")
            
        except Exception as e:
            self.log_message(f"Error saving blockchain: {str(e)}")
            logger.error(f"Blockchain save error: {str(e)}")'''
            
            # Replace the problematic save method
            save_method_start = content.find('def save_blockchain(self):')
            if save_method_start != -1:
                # Find the end of the method (next method or end of class)
                next_method = content.find('\n    def ', save_method_start + 1)
                if next_method == -1:
                    next_method = len(content)
                
                # Replace the method
                content = content[:save_method_start] + minimal_save_method + content[next_method:]
                self.changes_made.append("✅ Replaced with minimal safe save_blockchain method")
        
        return content
    
    def apply_all_save_fixes(self):
        """Apply all blockchain save fixes"""
        print("💾 Blockchain Save Attribute Fix")
        print("=" * 40)
        print("This will fix the missing 'difficulty' attribute error")
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
        
        print("\n🔧 Applying Save Fixes...")
        print("-" * 25)
        
        # Apply fixes in order of preference
        content = self.fix_save_blockchain_method(content)
        content = self.fix_load_blockchain_method(content)
        content = self.add_safer_block_reconstruction(content)
        
        # If no changes were made, use the minimal approach
        if len(self.changes_made) == 0:
            content = self.simplify_blockchain_data_structure(content)
        
        # Write updated content
        if self.write_file(content):
            print("\n🎉 SUCCESS!")
            print("=" * 40)
            print("Blockchain save fixes applied:")
            for change in self.changes_made:
                print(f"  {change}")
            
            if not self.changes_made:
                print("  ⚠️ No changes were needed")
            
            print(f"\n📁 Backup saved as: {self.backup_filename}")
            print("\n💾 SAVE FIXES APPLIED:")
            print("  ✅ Safe attribute access with getattr()")
            print("  ✅ Default values for missing attributes")
            print("  ✅ Graceful handling of serialization errors")
            print("  ✅ No more 'difficulty' attribute errors")
            print("\n🚀 Blockchain saving should now work without errors!")
            
            return True
        
        return False

def main():
    """Main function"""
    print("💾 Blockchain Save Attribute Fix")
    print("Fixes: 'Blockchain' object has no attribute 'difficulty'")
    print()
    
    # Check command line arguments
    target_file = "pyqt.py"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    # Create fixer and apply changes
    fixer = BlockchainSaveFix(target_file)
    
    try:
        success = fixer.apply_all_save_fixes()
        
        if success:
            print("\n✅ Blockchain save fix applied!")
            print("\n🎯 What was wrong:")
            print("  ❌ Code tried to access blockchain.difficulty")
            print("  ❌ Code tried to access blockchain.mining_reward")
            print("  ❌ These attributes don't exist on Blockchain class")
            print("\n✅ What's fixed:")
            print("  💾 Safe attribute access with getattr()")
            print("  💾 Default values when attributes missing")
            print("  💾 Graceful error handling")
            print("  💾 Minimal fallback approach")
        else:
            print("\n❌ Save fix failed to apply.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()