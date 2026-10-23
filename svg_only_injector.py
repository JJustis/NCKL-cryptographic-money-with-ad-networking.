#!/usr/bin/env python3
"""
PythonCoin Dashboard SVG-Only Adblock Injector
Modifies dashboard8.php to only display SVG ads, ignoring HTML/JSON files
"""

import os
import shutil
import re
import datetime
from pathlib import Path

class DashboardSVGInjector:
    def __init__(self, dashboard_file="dashboard8.php"):
        self.dashboard_file = Path(dashboard_file)
        self.backup_file = None
        self.modifications_made = []
        
    def create_backup(self):
        """Create a timestamped backup of the dashboard file"""
        if not self.dashboard_file.exists():
            raise FileNotFoundError(f"Dashboard file not found: {self.dashboard_file}")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.dashboard_file.with_name(f"dashboard8_backup_{timestamp}.php")
        
        shutil.copy2(self.dashboard_file, self.backup_file)
        print(f"✅ Backup created: {self.backup_file}")
        return str(self.backup_file)
    
    def read_dashboard_content(self):
        """Read the dashboard file content"""
        with open(self.dashboard_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_dashboard_content(self, content):
        """Write modified content back to dashboard file"""
        with open(self.dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def inject_svg_only_modifications(self, content):
        """Apply all SVG-only modifications to the dashboard content"""
        
        # 1. Update the header comment
        content = self.update_header_comment(content)
        
        # 2. Replace displayStorageAd function
        content = self.replace_display_storage_ad(content)
        
        # 3. Remove displayHtmlAd function
        content = self.remove_display_html_ad(content)
        
        # 4. Update loadStorageAds function to filter SVG only
        content = self.update_load_storage_ads(content)
        
        # 5. Update usage instructions
        content = self.update_usage_instructions(content)
        
        # 6. Update version references
        content = self.update_version_references(content)
        
        return content
    
    def update_header_comment(self, content):
        """Update header comments to reflect SVG-only mode"""
        old_pattern = r"(// Supports: ads_storage/active folder with SVG/HTML/JSON ad trios)"
        new_text = "// Supports: ads_storage/active folder - SVG files only"
        
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_text, content)
            self.modifications_made.append("Updated header comment to SVG-only")
        
        return content
    
    def replace_display_storage_ad(self, content):
        """Replace displayStorageAd function to only use SVG"""
        
        # Find the displayStorageAd function and replace its content
        pattern = r"(code \+= '    function displayStorageAd\(\) \{\\n';.*?)(code \+= '        // Check if ad has HTML wrapper\\n';.*?code \+= '        \}\\n';.*?code \+= '    \}\\n\\n';)"
        
        replacement = '''code += '        var randomAd = PYC_AD_CONFIG.storageAdsLoaded[Math.floor(Math.random() * PYC_AD_CONFIG.storageAdsLoaded.length)];\\n';
            code += '        PYC_AD_CONFIG.lastAdSource = "storage";\\n';
            code += '        \\n';
            code += '        console.log("Displaying storage SVG ad:", randomAd.id);\\n';
            code += '        \\n';
            code += '        // Always display as SVG - ignore HTML files\\n';
            code += '        displaySvgAd(randomAd, {client_id: "storage"});\\n';
            code += '    }\\n\\n';'''
        
        # More specific pattern to target the exact function
        specific_pattern = r"(code \+= '    function displayStorageAd\(\) \{\\n';.*?code \+= '        \}\\n';.*?code \+= '        \\n';.*?)(code \+= '        // Check if ad has HTML wrapper\\n';.*?code \+= '    \}\\n\\n';)"
        
        if re.search(specific_pattern, content, re.DOTALL):
            content = re.sub(specific_pattern, r'\1' + replacement, content, flags=re.DOTALL)
            self.modifications_made.append("Replaced displayStorageAd function for SVG-only")
        else:
            # Alternative approach - find and replace the HTML check section
            html_check_pattern = r"(code \+= '        // Check if ad has HTML wrapper\\n';.*?code \+= '        \} else \{\\n';.*?code \+= '            displaySvgAd\(randomAd, \{client_id: \"storage\"\}\);\\n';.*?code \+= '        \}\\n';)"
            
            svg_only_replacement = '''code += '        // Always display as SVG - ignore HTML files\\n';
            code += '        displaySvgAd(randomAd, {client_id: "storage"});\\n';'''
            
            if re.search(html_check_pattern, content, re.DOTALL):
                content = re.sub(html_check_pattern, svg_only_replacement, content, flags=re.DOTALL)
                self.modifications_made.append("Removed HTML wrapper check from displayStorageAd")
        
        return content
    
    def remove_display_html_ad(self, content):
        """Remove the entire displayHtmlAd function"""
        
        # Pattern to match the entire displayHtmlAd function
        pattern = r"(code \+= '    function displayHtmlAd\(ad\) \{\\n';.*?code \+= '    \}\\n\\n';)"
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            self.modifications_made.append("Removed displayHtmlAd function completely")
        
        return content
    
    def update_load_storage_ads(self, content):
        """Update loadStorageAds to filter for SVG-only content"""
        
        # Find and replace the storage ads loading section
        pattern = r"(code \+= '                if \(data\.success && data\.ads && data\.ads\.length > 0\) \{\\n';)(.*?)(code \+= '                    PYC_AD_CONFIG\.storageAdsLoaded = data\.ads;\\n';)"
        
        replacement = r'''\1\2code += '                    // Filter to only include ads that have SVG content\\n';
            code += '                    PYC_AD_CONFIG.storageAdsLoaded = data.ads.filter(function(ad) {\\n';
            code += '                        return ad.svg_url || ad.files && ad.files.svg;\\n';
            code += '                    });\\n';'''
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            self.modifications_made.append("Added SVG filtering to loadStorageAds")
        
        return content
    
    def update_usage_instructions(self, content):
        """Update usage instructions to reflect SVG-only mode"""
        
        # Update the usage instructions comment block
        old_instructions = r"(code \+= ' \* 5\. HTML ads supported with full interactivity\\n';)"
        new_instructions = "code += ' * 5. HTML files ignored - only SVG content displayed\\n';"
        
        if re.search(old_instructions, content):
            content = re.sub(old_instructions, new_instructions, content)
            self.modifications_made.append("Updated usage instructions for SVG-only")
        
        # Add new instruction about JSON files
        json_instruction_pattern = r"(code \+= ' \* 5\. HTML files ignored - only SVG content displayed\\n';)"
        json_instruction_replacement = '''code += ' * 5. HTML files ignored - only SVG content displayed\\n';
            code += ' * 6. JSON files ignored - metadata not used for display\\n';'''
        
        content = re.sub(json_instruction_pattern, json_instruction_replacement, content)
        
        return content
    
    def update_version_references(self, content):
        """Update version references to indicate SVG-only mode"""
        
        # Update console.log version messages
        pattern = r"(console\.log\(\"PythonCoin Enhanced Ad Block v2\.2\.0 - Storage \+ Network Support\"\);)"
        replacement = 'console.log("PythonCoin Enhanced Ad Block v2.2.0 - SVG Only Mode");'
        
        content = re.sub(pattern, replacement, content)
        
        # Update initialization message
        pattern2 = r"(code \+= '        console\.log\(\"PythonCoin Enhanced Ad Block v2\.2\.0 - Storage \+ Network Support\"\);\\n';)"
        replacement2 = "code += '        console.log(\"PythonCoin Enhanced Ad Block v2.2.0 - SVG Only Mode\");\\n';"
        
        content = re.sub(pattern2, replacement2, content)
        
        self.modifications_made.append("Updated version references for SVG-only mode")
        
        return content
    
    def add_svg_only_config_flag(self, content):
        """Add svgOnly flag to the PYC_AD_CONFIG"""
        
        pattern = r"(code \+= '        preferStorageAds: true\\n';)"
        replacement = '''code += '        preferStorageAds: true,\\n';
            code += '        svgOnly: true\\n';'''
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            self.modifications_made.append("Added svgOnly configuration flag")
        
        return content
    
    def verify_modifications(self, content):
        """Verify that modifications were applied correctly"""
        checks = {
            "SVG-only header comment": "SVG files only" in content,
            "HTML function removed": "displayHtmlAd" not in content,
            "SVG filtering added": "filter(function(ad)" in content,
            "SVG-only mode message": "SVG Only Mode" in content,
            "Updated instructions": "HTML files ignored" in content
        }
        
        print("\n🔍 Verification Results:")
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        return all(checks.values())
    
    def run_injection(self):
        """Main method to run the SVG-only injection process"""
        try:
            print("🚀 Starting PythonCoin Dashboard SVG-Only Injection...")
            print(f"📁 Target file: {self.dashboard_file}")
            
            # Create backup
            backup_path = self.create_backup()
            
            # Read original content
            print("📖 Reading dashboard content...")
            content = self.read_dashboard_content()
            
            # Apply modifications
            print("🔧 Applying SVG-only modifications...")
            modified_content = self.inject_svg_only_modifications(content)
            
            # Verify modifications
            if self.verify_modifications(modified_content):
                print("✅ All modifications verified successfully")
            else:
                print("⚠️  Some modifications may not have been applied correctly")
            
            # Write modified content
            print("💾 Writing modified content...")
            self.write_dashboard_content(modified_content)
            
            # Summary
            print("\n📊 Injection Summary:")
            print(f"  📁 Original file: {self.dashboard_file}")
            print(f"  💾 Backup created: {backup_path}")
            print(f"  🔧 Modifications applied: {len(self.modifications_made)}")
            
            for i, mod in enumerate(self.modifications_made, 1):
                print(f"    {i}. {mod}")
            
            print("\n✅ SVG-Only injection completed successfully!")
            print("\n📋 What changed:")
            print("  • Ad blocks now only display SVG files")
            print("  • HTML ad display function removed")
            print("  • JSON files ignored for display")
            print("  • Storage ads filtered to SVG-only")
            print("  • Updated version messages and instructions")
            
            print(f"\n🔄 To restore original: cp {backup_path} {self.dashboard_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during injection: {str(e)}")
            if self.backup_file and self.backup_file.exists():
                print(f"🔄 Backup available at: {self.backup_file}")
            return False

def main():
    """Main function to run the injector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inject SVG-only modifications into PythonCoin Dashboard")
    parser.add_argument("--file", "-f", default="dashboard8.php", 
                       help="Path to dashboard8.php file (default: dashboard8.php)")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="Show what would be changed without modifying files")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("This would apply the following changes:")
        print("  1. Replace displayStorageAd function for SVG-only display")
        print("  2. Remove displayHtmlAd function completely")
        print("  3. Add SVG filtering to storage ad loading")
        print("  4. Update version messages and instructions")
        print("  5. Create timestamped backup file")
        return
    
    injector = DashboardSVGInjector(args.file)
    success = injector.run_injection()
    
    if success:
        print("\n🎉 Ready to test! The dashboard now generates SVG-only ad blocks.")
    else:
        print("\n💥 Injection failed. Check the error messages above.")

if __name__ == "__main__":
    main()
