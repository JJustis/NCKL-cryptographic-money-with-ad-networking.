#!/usr/bin/env python3
"""
Unified PythonCoin Injection Script
Automatically modifies pyqt.py with enhanced features including:
- HTML/SVG ad storage system
- Enhanced network configuration
- IP discovery and peer management
- Automatic backup and restore capabilities
"""

import os
import sys
import re
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

class PythonCoinInjector:
    def __init__(self, target_file='pyqt.py'):
        self.target_file = target_file
        self.backup_dir = None
        self.original_content = None
        self.modified_content = None
        
    def print_header(self):
        """Print injection header"""
        print("=" * 70)
        print("🚀 PythonCoin Unified Injection Script")
        print("=" * 70)
        print("Automatically enhancing pyqt.py with advanced features")
        print()
    
    def validate_target_file(self):
        """Validate that the target file exists and is valid"""
        if not os.path.exists(self.target_file):
            print(f"❌ Target file not found: {self.target_file}")
            return False
        
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it's a valid PythonCoin file
            if 'class UnifiedPythonCoinWallet' not in content:
                print(f"❌ {self.target_file} doesn't appear to be a valid PythonCoin wallet file")
                return False
            
            self.original_content = content
            print(f"✅ Target file validated: {self.target_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error reading target file: {e}")
            return False
    
    def create_backup(self):
        """Create timestamped backup of original file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/injection_{timestamp}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            backup_file = self.backup_dir / self.target_file
            shutil.copy2(self.target_file, backup_file)
            
            # Also create a .original backup
            original_backup = f"{self.target_file}.original"
            if not os.path.exists(original_backup):
                shutil.copy2(self.target_file, original_backup)
            
            print(f"✅ Backup created: {backup_file}")
            print(f"✅ Original backup: {original_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def inject_imports(self, content):
        """Inject additional imports needed for enhanced features"""
        print("📦 Injecting enhanced imports...")
        
        # Find existing imports section
        import_pattern = r'(from pathlib import Path\n)'
        if 'from pathlib import Path' in content:
            return content  # Already has required imports
        
        # Find a good place to insert imports (after existing imports)
        insert_point = content.find('# Setup logging')
        if insert_point == -1:
            insert_point = content.find('from PyQt5.QtWidgets import')
            if insert_point == -1:
                print("⚠️ Could not find import section")
                return content
        
        # Additional imports needed
        additional_imports = """
# Enhanced imports for injection
from pathlib import Path
import shutil
import ipaddress
import threading
"""
        
        # Insert before setup logging or at the beginning of imports
        content = content[:insert_point] + additional_imports + "\n" + content[insert_point:]
        print("✅ Enhanced imports injected")
        return content
    
    def inject_ad_storage_manager(self, content):
        """Inject the complete AdStorageManager class"""
        print("📁 Injecting AdStorageManager class...")
        
        # Check if already injected
        if 'class AdStorageManager:' in content:
            print("⚠️ AdStorageManager already exists")
            return content
        
        # Find insertion point (before main wallet class)
        insertion_point = content.find('class UnifiedPythonCoinWallet(QMainWindow):')
        if insertion_point == -1:
            print("❌ Could not find wallet class")
            return content
        
        ad_storage_code = '''
# ============================================================================
# Enhanced Advertisement Storage System
# ============================================================================

class AdStorageManager:
    """Manages saving and loading of advertisements as HTML/SVG files"""
    
    def __init__(self, base_dir="ads_storage"):
        self.base_dir = Path(base_dir)
        self.setup_directory_structure()
    
    def setup_directory_structure(self):
        """Create directory structure for ad storage"""
        directories = [
            self.base_dir,
            self.base_dir / "active",
            self.base_dir / "inactive", 
            self.base_dir / "templates",
            self.base_dir / "assets" / "images",
            self.base_dir / "assets" / "css",
            self.base_dir / "exports",
            self.base_dir / "analytics"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.create_default_templates()
    
    def create_default_templates(self):
        """Create default HTML/SVG ad templates"""
        
        # Enhanced HTML template with modern design
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{AD_TITLE}} - PythonCoin Network</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        .pyc-ad-container {
            border: 2px solid #0066cc;
            border-radius: 16px;
            padding: 24px;
            background: linear-gradient(135deg, #ffffff 0%, #f8fffe 40%, #f0f9ff 100%);
            margin: 15px auto;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            max-width: 420px;
            font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-shadow: 0 8px 32px rgba(0,102,204,0.12);
            overflow: hidden;
        }
        
        .pyc-ad-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff6b35, #f7931e, #0066cc, #28a745);
            background-size: 300% 100%;
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .pyc-ad-container:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 60px rgba(0,102,204,0.25);
            border-color: #0056b3;
        }
        
        .pyc-ad-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            background: linear-gradient(45deg, #ff6b35, #f7931e);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(255,107,53,0.4);
        }
        
        .pyc-ad-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 16px;
            background: linear-gradient(45deg, #f0f9ff, #e0f2fe);
        }
        
        .pyc-ad-title {
            color: #0066cc;
            margin: 0 0 16px 0;
            font-size: 22px;
            font-weight: 800;
            line-height: 1.3;
            letter-spacing: -0.5px;
        }
        
        .pyc-ad-description {
            color: #374151;
            margin: 0 0 20px 0;
            font-size: 16px;
            line-height: 1.6;
            opacity: 0.9;
        }
        
        .pyc-ad-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid rgba(0,102,204,0.1);
        }
        
        .pyc-ad-category {
            color: #0066cc;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .pyc-ad-payout {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(40,167,69,0.3);
            transition: all 0.3s ease;
        }
        
        .pyc-ad-payout:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 25px rgba(40,167,69,0.4);
        }
        
        .pyc-ad-stats {
            position: absolute;
            bottom: 12px;
            left: 12px;
            background: rgba(0,102,204,0.1);
            color: #0066cc;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 600;
        }
        
        @media (max-width: 480px) {
            .pyc-ad-container {
                margin: 10px;
                padding: 20px;
            }
            
            .pyc-ad-title {
                font-size: 20px;
            }
            
            .pyc-ad-description {
                font-size: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="pyc-ad-container" onclick="handleAdClick('{{AD_ID}}')">
        <div class="pyc-ad-badge">💎 PYC Network</div>
        {{#AD_IMAGE_URL}}
        <img src="{{AD_IMAGE_URL}}" alt="{{AD_TITLE}}" class="pyc-ad-image" 
             onerror="this.style.display='none'">
        {{/AD_IMAGE_URL}}
        <h3 class="pyc-ad-title">{{AD_TITLE}}</h3>
        <p class="pyc-ad-description">{{AD_DESCRIPTION}}</p>
        <div class="pyc-ad-footer">
            <span class="pyc-ad-category">
                <span>📱</span>
                <span>{{AD_CATEGORY}} • P2P Network</span>
            </span>
            <span class="pyc-ad-payout" id="payout-{{AD_ID}}">
                +{{AD_PAYOUT}} PYC
            </span>
        </div>
        <div class="pyc-ad-stats">
            ID: {{AD_ID_SHORT}}
        </div>
    </div>
    
    <script>
        // Enhanced click tracking
        function handleAdClick(adId) {
            console.log('[PYC] Ad clicked:', adId);
            
            // Animate payout button
            const payoutBtn = document.getElementById('payout-' + adId);
            if (payoutBtn) {
                payoutBtn.style.transform = 'scale(1.2)';
                payoutBtn.innerHTML = '✅ Earning...';
                setTimeout(() => {
                    payoutBtn.style.transform = 'scale(1)';
                    payoutBtn.innerHTML = '+{{AD_PAYOUT}} PYC';
                }, 1000);
            }
            
            // Track click with wallet
            if (window.pythonCoinWallet) {
                window.pythonCoinWallet.recordClick(adId, {
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent,
                    viewportSize: window.innerWidth + 'x' + window.innerHeight
                });
            }
            
            // Send to analytics
            fetch('/api/analytics/click', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    ad_id: adId,
                    timestamp: new Date().toISOString(),
                    payout_amount: parseFloat('{{AD_PAYOUT}}')
                })
            }).catch(console.warn);
            
            // Open click URL with delay
            setTimeout(() => {
                const clickUrl = '{{AD_CLICK_URL}}';
                if (clickUrl && clickUrl !== '#') {
                    window.open(clickUrl, '_blank', 'noopener,noreferrer');
                }
            }, 500);
        }
        
        // Track impression
        if (window.pythonCoinWallet) {
            window.pythonCoinWallet.recordImpression('{{AD_ID}}');
        }
        
        // Analytics impression tracking
        fetch('/api/analytics/impression', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ad_id: '{{AD_ID}}',
                timestamp: new Date().toISOString()
            })
        }).catch(console.warn);
    </script>
</body>
</html>"""
        
        # SVG template with animations
        svg_template = """<svg width="400" height="280" xmlns="http://www.w3.org/2000/svg">
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
    </defs>
    
    <!-- Main container with animation -->
    <rect x="8" y="8" width="384" height="264" rx="16" ry="16" 
          fill="url(#bgGrad)" stroke="#0066cc" stroke-width="2" filter="url(#shadow)">
        <animate attributeName="stroke-width" values="2;3;2" dur="3s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Animated top border -->
    <rect x="8" y="8" width="384" height="4" rx="2" ry="2">
        <animate attributeName="fill" values="#ff6b35;#f7931e;#0066cc;#28a745;#ff6b35" dur="5s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Badge -->
    <rect x="300" y="20" width="85" height="28" rx="14" ry="14" fill="url(#badgeGrad)"/>
    <text x="342" y="37" text-anchor="middle" fill="white" font-family="Arial, sans-serif" 
          font-size="11" font-weight="bold">💎 PYC</text>
    
    <!-- Title -->
    <text x="24" y="60" fill="#0066cc" font-family="Arial, sans-serif" font-size="22" font-weight="bold">
        {{AD_TITLE}}
    </text>
    
    <!-- Description -->
    <foreignObject x="24" y="75" width="350" height="80">
        <div xmlns="http://www.w3.org/1999/xhtml" 
             style="color: #374151; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6;">
            {{AD_DESCRIPTION}}
        </div>
    </foreignObject>
    
    <!-- Category -->
    <text x="24" y="200" fill="#0066cc" font-family="Arial, sans-serif" 
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
          fill="rgba(0,102,204,0.1)" stroke="rgba(0,102,204,0.3)" stroke-width="1"/>
    <text x="80" y="254" text-anchor="middle" fill="#0066cc" font-family="Arial, sans-serif" 
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
</svg>"""
        
        # Save templates
        templates = {
            'enhanced_html.template': html_template,
            'enhanced_svg.template': svg_template
        }
        
        for filename, template_content in templates.items():
            template_path = self.base_dir / "templates" / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
    
    def save_ad(self, ad_data, format_type='html'):
        """Save advertisement as HTML or SVG file with enhanced features"""
        try:
            ad_id = ad_data.get('id', str(uuid.uuid4()))
            
            # Enhanced metadata
            metadata = {
                'id': ad_id,
                'title': ad_data.get('title', ''),
                'description': ad_data.get('description', ''),
                'category': ad_data.get('category', 'general'),
                'click_url': ad_data.get('click_url', '#'),
                'image_url': ad_data.get('image_url', ''),
                'payout_rate': ad_data.get('payout_rate', 0.001),
                'advertiser_address': ad_data.get('advertiser_address', ''),
                'targeting': ad_data.get('targeting', {}),
                'created_at': ad_data.get('created_at', datetime.now().isoformat()),
                'expires_at': ad_data.get('expires_at', ''),
                'status': 'active',
                'format': format_type,
                'click_count': 0,
                'impression_count': 0,
                'revenue_generated': 0.0,
                'conversion_rate': 0.0
            }
            
            # Generate content
            if format_type == 'html':
                content = self.generate_html_ad(metadata)
                file_extension = '.html'
            elif format_type == 'svg':
                content = self.generate_svg_ad(metadata)
                file_extension = '.svg'
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Save files
            filename = f"{ad_id}_{format_type}{file_extension}"
            file_path = self.base_dir / "active" / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            metadata['file_path'] = str(file_path)
            
            # Save metadata
            metadata_path = self.base_dir / "active" / f"{ad_id}_meta.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'success': True,
                'ad_id': ad_id,
                'file_path': str(file_path),
                'metadata_path': str(metadata_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_html_ad(self, metadata):
        """Generate enhanced HTML ad from template"""
        template_path = self.base_dir / "templates" / "enhanced_html.template"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except:
            template = "<div><h3>{{AD_TITLE}}</h3><p>{{AD_DESCRIPTION}}</p></div>"
        
        # Enhanced replacements
        replacements = {
            '{{AD_ID}}': metadata['id'],
            '{{AD_ID_SHORT}}': metadata['id'][:8],
            '{{AD_TITLE}}': metadata['title'],
            '{{AD_DESCRIPTION}}': metadata['description'],
            '{{AD_CATEGORY}}': metadata['category'].title(),
            '{{AD_CLICK_URL}}': metadata['click_url'],
            '{{AD_PAYOUT}}': f"{metadata['payout_rate']:.8f}",
            '{{AD_IMAGE_URL}}': metadata.get('image_url', ''),
            '{{#AD_IMAGE_URL}}': '' if metadata.get('image_url') else '<!--',
            '{{/AD_IMAGE_URL}}': '' if metadata.get('image_url') else '-->'
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        return template
    
    def generate_svg_ad(self, metadata):
        """Generate enhanced SVG ad from template"""
        template_path = self.base_dir / "templates" / "enhanced_svg.template"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except:
            template = '<svg><text>{{AD_TITLE}}</text></svg>'
        
        # Truncate text for SVG
        title = metadata['title'][:25] + ('...' if len(metadata['title']) > 25 else '')
        description = metadata['description'][:80] + ('...' if len(metadata['description']) > 80 else '')
        
        replacements = {
            '{{AD_ID}}': metadata['id'],
            '{{AD_ID_SHORT}}': metadata['id'][:8],
            '{{AD_TITLE}}': title,
            '{{AD_DESCRIPTION}}': description,
            '{{AD_CATEGORY}}': metadata['category'].title(),
            '{{AD_CLICK_URL}}': metadata['click_url'],
            '{{AD_PAYOUT}}': f"{metadata['payout_rate']:.8f}"
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        return template
    
    def load_all_ads(self):
        """Load all active advertisements"""
        ads = []
        active_dir = self.base_dir / "active"
        
        try:
            for metadata_file in active_dir.glob("*_meta.json"):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                ads.append(metadata)
        except Exception as e:
            pass
        
        return ads
    
    def update_ad_stats(self, ad_id, clicks=0, impressions=0):
        """Update advertisement statistics"""
        try:
            metadata_file = self.base_dir / "active" / f"{ad_id}_meta.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['click_count'] = metadata.get('click_count', 0) + clicks
                metadata['impression_count'] = metadata.get('impression_count', 0) + impressions
                metadata['last_updated'] = datetime.now().isoformat()
                
                if metadata['impression_count'] > 0:
                    metadata['conversion_rate'] = metadata['click_count'] / metadata['impression_count']
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
        except:
            pass
        
        return False
    
    def get_storage_stats(self):
        """Get comprehensive storage statistics"""
        try:
            active_ads = len(list((self.base_dir / "active").glob("*_meta.json")))
            inactive_ads = len(list((self.base_dir / "inactive").glob("*_meta.json")))
            total_size = sum(f.stat().st_size for f in self.base_dir.rglob("*") if f.is_file())
            
            return {
                'active_ads': active_ads,
                'inactive_ads': inactive_ads,
                'total_ads': active_ads + inactive_ads,
                'storage_size_bytes': total_size,
                'storage_size_mb': total_size / (1024 * 1024),
                'base_directory': str(self.base_dir)
            }
        except:
            return {}

'''
        
        # Insert the class
        content = content[:insertion_point] + ad_storage_code + "\n" + content[insertion_point:]
        print("✅ AdStorageManager class injected")
        return content
    
    def inject_enhanced_init(self, content):
        """Inject enhanced __init__ method with ad storage"""
        print("🔧 Enhancing __init__ method...")
        
        # Find the __init__ method
        init_pattern = r'(def __init__\(self\):.*?)(# Initialize UI FIRST)'
        
        def replacement(match):
            init_part = match.group(1)
            ui_comment = match.group(2)
            
            # Check if ad storage already initialized
            if 'self.ad_storage = AdStorageManager()' in init_part:
                return match.group(0)
            
            # Add ad storage initialization
            enhancement = """        
        # Enhanced Ad Storage System
        self.ad_storage = AdStorageManager()
        
        """
            
            return init_part + enhancement + ui_comment
        
        content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)
        
        # Also add call to load saved ads after wallet loading
        load_ads_call = """        
        # Load saved advertisements from storage
        self.load_saved_ads()
        """
        
        # Insert after wallet loading
        wallet_load_pattern = r'(self\.load_wallet_state\(\))'
        content = re.sub(wallet_load_pattern, r'\1' + load_ads_call, content)
        
        print("✅ __init__ method enhanced")
        return content
    
    def inject_ad_loading_method(self, content):
        """Inject load_saved_ads method"""
        print("📋 Injecting ad loading method...")
        
        if 'def load_saved_ads(self):' in content:
            print("⚠️ load_saved_ads method already exists")
            return content
        
        load_ads_method = '''
    def load_saved_ads(self):
        """Load saved ads from storage with enhanced error handling"""
        try:
            saved_ads = self.ad_storage.load_all_ads()
            
            loaded_ads = []
            for ad_metadata in saved_ads:
                try:
                    ad = AdContent(
                        id=ad_metadata['id'],
                        title=ad_metadata['title'],
                        description=ad_metadata['description'],
                        image_url=ad_metadata.get('image_url', ''),
                        click_url=ad_metadata['click_url'],
                        category=ad_metadata['category'],
                        targeting=ad_metadata.get('targeting', {}),
                        created_at=ad_metadata['created_at'],
                        expires_at=ad_metadata.get('expires_at', ''),
                        peer_source=ad_metadata.get('peer_source', self.client_id),
                        payout_rate=ad_metadata['payout_rate'],
                        advertiser_address=ad_metadata['advertiser_address']
                    )
                    loaded_ads.append(ad)
                except Exception as e:
                    self.log_message(f"⚠️ Error loading ad {ad_metadata.get('id', 'unknown')}: {str(e)}")
                    continue
            
            self.ads = loaded_ads
            self.log_message(f"✅ Loaded {len(self.ads)} saved advertisements from storage")
            
            # Schedule UI update
            if hasattr(self, 'update_my_ads_table'):
                QTimer.singleShot(1000, self.update_my_ads_table)
            
        except Exception as e:
            self.log_message(f"❌ Error loading saved ads: {str(e)}")
            self.ads = []
'''
        
        # Insert after __init__ method
        init_end = content.find('    def init_ui(self):')
        if init_end != -1:
            content = content[:init_end] + load_ads_method + '\n' + content[init_end:]
            print("✅ load_saved_ads method injected")
        
        return content
    
    def inject_enhanced_create_advertisement(self, content):
        """Inject enhanced create_advertisement method"""
        print("🎨 Enhancing create_advertisement method...")
        
        # Find and replace the existing method
        method_pattern = r'(    def create_advertisement\(self\):.*?)(\n    def [a-zA-Z_])'
        
        enhanced_method = '''    def create_advertisement(self):
        """Enhanced advertisement creation with HTML/SVG storage and validation"""
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
        
        # Enhanced validation
        validation_errors = []
        
        if not title:
            validation_errors.append("Title is required")
        elif len(title) < 5:
            validation_errors.append("Title must be at least 5 characters")
        elif len(title) > 100:
            validation_errors.append("Title must be less than 100 characters")
        
        if not description:
            validation_errors.append("Description is required")
        elif len(description) < 20:
            validation_errors.append("Description must be at least 20 characters")
        elif len(description) > 500:
            validation_errors.append("Description must be less than 500 characters")
        
        if not click_url:
            click_url = 'https://example.com'
        elif not click_url.startswith(('http://', 'https://')):
            click_url = 'https://' + click_url
        
        if payout_rate <= 0:
            validation_errors.append("Payout rate must be greater than 0")
        elif payout_rate > 1.0:
            validation_errors.append("Payout rate cannot exceed 1.0 PYC")
        
        if daily_budget <= 0:
            validation_errors.append("Daily budget must be greater than 0")
        
        if validation_errors:
            QMessageBox.warning(self, "Validation Errors", "\\n".join(validation_errors))
            return
        
        # Check balance
        try:
            balance = self.get_current_balance()
        except Exception as e:
            self.log_message(f"Error getting balance: {str(e)}")
            balance = 0.0
        
        if balance < daily_budget:
            QMessageBox.warning(self, "Insufficient Funds", 
                               f"You need at least {daily_budget:.8f} PYC for one day of advertising.\\n"
                               f"Current balance: {balance:.8f} PYC")
            return
        
        try:
            # Show progress dialog
            progress = QProgressDialog("Creating advertisement...", "Cancel", 0, 4, self)
            progress.setWindowTitle("Creating Advertisement")
            progress.setModal(True)
            progress.show()
            QApplication.processEvents()
            
            # Step 1: Generate ad ID and data
            progress.setValue(1)
            progress.setLabelText("Generating advertisement data...")
            QApplication.processEvents()
            
            ad_id = str(uuid.uuid4())
            
            # Get targeting options
            interests = [i.strip() for i in self.target_interests.text().split(',') if i.strip()]
            targeting = {
                'interests': interests,
                'geographic': self.target_geo.currentText(),
                'budget_daily': daily_budget,
                'max_clicks_daily': max_clicks,
                'min_age': 18,
                'max_age': 65
            }
            
            # Step 2: Prepare ad data
            progress.setValue(2)
            progress.setLabelText("Preparing advertisement files...")
            QApplication.processEvents()
            
            ad_data = {
                'id': ad_id,
                'title': title,
                'description': description,
                'image_url': getattr(self, 'current_ad_image', ''),
                'click_url': click_url,
                'category': category,
                'targeting': targeting,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                'peer_source': self.client_id,
                'payout_rate': payout_rate,
                'advertiser_address': self.wallet.address
            }
            
            # Step 3: Save to storage (both HTML and SVG)
            progress.setValue(3)
            progress.setLabelText("Saving advertisement files...")
            QApplication.processEvents()
            
            html_result = self.ad_storage.save_ad(ad_data, 'html')
            svg_result = self.ad_storage.save_ad(ad_data, 'svg')
            
            if not html_result['success']:
                progress.close()
                QMessageBox.critical(self, "Storage Error", 
                                   f"Failed to save HTML version: {html_result.get('error', 'Unknown error')}")
                return
            
            if not svg_result['success']:
                progress.close()
                QMessageBox.critical(self, "Storage Error", 
                                   f"Failed to save SVG version: {svg_result.get('error', 'Unknown error')}")
                return
            
            # Step 4: Create AdContent object and update UI
            progress.setValue(4)
            progress.setLabelText("Finalizing advertisement...")
            QApplication.processEvents()
            
            ad = AdContent(
                id=ad_id,
                title=title,
                description=description,
                image_url=ad_data.get('image_url', ''),
                click_url=click_url,
                category=category,
                targeting=targeting,
                created_at=ad_data['created_at'],
                expires_at=ad_data['expires_at'],
                peer_source=self.client_id,
                payout_rate=payout_rate,
                advertiser_address=self.wallet.address
            )
            
            # Add to local ads
            self.ads.append(ad)
            
            # Update database if connected
            if self.db_connected:
                try:
                    self.update_database_on_ad_creation(ad)
                except Exception as e:
                    self.log_message(f"Database update error: {str(e)}")
            
            # Broadcast to P2P network if connected
            if self.p2p_manager and self.p2p_manager.running:
                try:
                    self.broadcast_new_ad(ad)
                except Exception as e:
                    self.log_message(f"P2P broadcast error: {str(e)}")
            
            # Update UI
            self.update_my_ads_table()
            self.clear_ad_form()
            
            progress.close()
            
            # Show success dialog with detailed info
            success_msg = f"""Advertisement '{title}' created successfully!

📄 Formats Created:
   • HTML: {html_result['file_path']}
   • SVG: {svg_result['file_path']}

💰 Configuration:
   • Payout: {payout_rate:.8f} PYC per click
   • Daily Budget: {daily_budget:.8f} PYC
   • Max Clicks: {max_clicks:,}
   • Category: {category}

🌐 Network Status:
   • Ad ID: {ad_id[:16]}...
   • P2P Network: {'Online' if self.p2p_manager and self.p2p_manager.running else 'Offline'}
   • Database: {'Connected' if self.db_connected else 'Offline'}

Your advertisement is now live and ready to earn PYC!"""
            
            QMessageBox.information(self, "Advertisement Created", success_msg)
            
            self.log_message(f"✅ Created advertisement: {title} (ID: {ad_id[:8]}...)")
            self.log_message(f"📁 HTML: {html_result['file_path']}")
            self.log_message(f"📁 SVG: {svg_result['file_path']}")
            
            self.stats['ads_served'] += 1
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            self.log_message(f"❌ Error creating advertisement: {str(e)}")
            QMessageBox.critical(self, "Creation Error", f"Failed to create advertisement: {str(e)}")
'''
        
        def replacement(match):
            return enhanced_method + match.group(2)
        
        content = re.sub(method_pattern, replacement, content, flags=re.DOTALL)
        print("✅ create_advertisement method enhanced")
        return content
    
    def inject_enhanced_preview_method(self, content):
        """Inject enhanced preview_ad method"""
        print("👁️ Enhancing preview_ad method...")
        
        # Find and replace preview_ad method
        preview_pattern = r'(    def preview_ad\(self\):.*?)(\n    def [a-zA-Z_])'
        
        enhanced_preview = '''    def preview_ad(self):
        """Enhanced preview using storage manager templates with live updates"""
        if not hasattr(self, 'ad_title_input') or not hasattr(self, 'ad_storage'):
            return
        
        try:
            title = self.ad_title_input.text().strip() or "Your Amazing Ad Title Here"
            description = self.ad_description_input.toPlainText().strip() or "Your compelling ad description will appear here. Make it engaging and informative to attract more clicks!"
            category = self.ad_category_combo.currentText() if hasattr(self, 'ad_category_combo') else "technology"
            payout = self.ad_payout_input.value() if hasattr(self, 'ad_payout_input') else 0.00100000
            click_url = self.ad_click_url_input.text().strip() if hasattr(self, 'ad_click_url_input') else "https://example.com"
            
            # Truncate for preview
            if len(title) > 50:
                title = title[:50] + "..."
            if len(description) > 150:
                description = description[:150] + "..."
            
            # Create preview metadata
            preview_metadata = {
                'id': 'preview_' + str(int(datetime.now().timestamp())),
                'title': title,
                'description': description,
                'category': category,
                'click_url': click_url if click_url.startswith(('http://', 'https://')) else f"https://{click_url}",
                'payout_rate': payout,
                'image_url': getattr(self, 'current_ad_image', ''),
                'advertiser_address': self.wallet.address if self.wallet else 'preview_address'
            }
            
            # Generate enhanced HTML preview
            preview_html = self.ad_storage.generate_html_ad(preview_metadata)
            
            # Add preview-specific styling
            preview_css = """
            <style>
                body { 
                    background: #f8f9fa; 
                    padding: 20px; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                .preview-banner {
                    background: linear-gradient(45deg, #17a2b8, #007bff);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-weight: bold;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.8; }
                }
                .preview-info {
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin-top: 20px;
                    font-size: 14px;
                }
                .preview-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }
                .stat-item {
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 6px;
                    text-align: center;
                }
                .stat-value {
                    font-size: 18px;
                    font-weight: bold;
                    color: #0066cc;
                }
                .stat-label {
                    font-size: 12px;
                    color: #6c757d;
                    margin-top: 4px;
                }
            </style>
            """
            
            preview_banner = """
            <div class="preview-banner">
                🎯 LIVE PREVIEW - This is how your ad will appear to users
            </div>
            """
            
            preview_info = f"""
            <div class="preview-info">
                <strong>📊 Preview Information</strong>
                <div class="preview-stats">
                    <div class="stat-item">
                        <div class="stat-value">{len(title)}</div>
                        <div class="stat-label">Title Characters</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{len(description)}</div>
                        <div class="stat-label">Description Characters</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{payout:.6f}</div>
                        <div class="stat-label">PYC Per Click</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{category.title()}</div>
                        <div class="stat-label">Category</div>
                    </div>
                </div>
                <p style="margin-top: 15px; color: #6c757d; font-size: 13px;">
                    💡 Tip: Keep titles under 50 characters and descriptions under 150 characters for best display.
                </p>
            </div>
            """
            
            # Combine all elements
            full_preview = preview_css + preview_banner + preview_html + preview_info
            
            if hasattr(self, 'ad_preview_area'):
                self.ad_preview_area.setHtml(full_preview)
            
        except Exception as e:
            self.log_message(f"❌ Error generating preview: {str(e)}")
            # Fallback to simple preview
            if hasattr(self, 'ad_preview_area'):
                self.ad_preview_area.setHtml(self.get_default_preview_html())
'''
        
        def replacement(match):
            return enhanced_preview + match.group(2)
        
        content = re.sub(preview_pattern, replacement, content, flags=re.DOTALL)
        print("✅ preview_ad method enhanced")
        return content
    
    def inject_ad_management_methods(self, content):
        """Inject additional ad management methods"""
        print("🛠️ Injecting ad management methods...")
        
        management_methods = '''
    def export_advertisement(self, ad_id=None):
        """Export advertisement as standalone HTML file"""
        try:
            if not ad_id:
                if not self.ads:
                    QMessageBox.information(self, "No Ads", "No advertisements available to export")
                    return
                
                ad_titles = [f"{ad.title} ({ad.id[:8]}...)" for ad in self.ads]
                ad_title, ok = QInputDialog.getItem(
                    self, "Export Advertisement", "Select advertisement to export:",
                    ad_titles, 0, False
                )
                
                if not ok:
                    return
                
                # Extract ad_id from selection
                ad_id = ad_title.split('(')[1].split(')')[0].replace('...', '')
                
                # Find full ad_id
                for ad in self.ads:
                    if ad.id.startswith(ad_id):
                        ad_id = ad.id
                        break
            
            # Choose export location
            export_path, _ = QFileDialog.getSaveFileName(
                self, "Export Advertisement", 
                f"pythoncoin_ad_{ad_id[:8]}.html",
                "HTML Files (*.html);;SVG Files (*.svg);;All Files (*)"
            )
            
            if export_path:
                # Determine format from extension
                format_type = 'svg' if export_path.endswith('.svg') else 'html'
                
                # Find the ad file
                ad_file = self.ad_storage.base_dir / "active" / f"{ad_id}_{format_type}.{format_type}"
                
                if ad_file.exists():
                    shutil.copy2(ad_file, export_path)
                    QMessageBox.information(self, "Export Successful", 
                                           f"Advertisement exported to:\\n{export_path}")
                    self.log_message(f"✅ Exported ad {ad_id[:8]}... to {export_path}")
                else:
                    QMessageBox.critical(self, "Export Failed", f"Advertisement file not found:\\n{ad_file}")
            
        except Exception as e:
            self.log_message(f"❌ Error exporting advertisement: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {str(e)}")
    
    def show_ad_storage_stats(self):
        """Show detailed advertisement storage statistics"""
        try:
            stats = self.ad_storage.get_storage_stats()
            
            # Calculate additional metrics
            total_clicks = sum(getattr(ad, 'click_count', 0) for ad in self.ads)
            total_impressions = sum(getattr(ad, 'impression_count', 0) for ad in self.ads)
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            
            stats_text = f"""📊 Advertisement Storage Statistics

📁 Storage Information:
   • Location: {stats.get('base_directory', 'Unknown')}
   • Total Size: {stats.get('storage_size_mb', 0):.2f} MB
   • Files Stored: HTML, SVG, JSON metadata, images

📈 Advertisement Counts:
   • Active Ads: {stats.get('active_ads', 0)}
   • Archived Ads: {stats.get('inactive_ads', 0)}
   • Total Created: {stats.get('total_ads', 0)}

📊 Performance Metrics:
   • Total Clicks: {total_clicks:,}
   • Total Impressions: {total_impressions:,}
   • Average CTR: {avg_ctr:.2f}%
   • Revenue Generated: {sum(getattr(ad, 'revenue_generated', 0) for ad in self.ads):.6f} PYC

🔧 Available Actions:
   • Export ads as standalone files
   • Archive old advertisements  
   • Clean up unused assets
   • View detailed analytics

💡 Storage is automatically managed with periodic cleanup."""
            
            # Create dialog with action buttons
            dialog = QDialog(self)
            dialog.setWindowTitle("Storage Statistics")
            dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout()
            
            # Stats text
            stats_label = QLabel(stats_text)
            stats_label.setWordWrap(True)
            stats_label.setStyleSheet("font-family: monospace; font-size: 11px; padding: 15px;")
            layout.addWidget(stats_label)
            
            # Action buttons
            button_layout = QHBoxLayout()
            
            export_btn = QPushButton("📤 Export Ad")
            export_btn.clicked.connect(lambda: [dialog.accept(), self.export_advertisement()])
            button_layout.addWidget(export_btn)
            
            cleanup_btn = QPushButton("🧹 Cleanup")
            cleanup_btn.clicked.connect(lambda: [dialog.accept(), self.cleanup_ad_storage()])
            button_layout.addWidget(cleanup_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            self.log_message(f"❌ Error getting storage stats: {str(e)}")
            QMessageBox.critical(self, "Stats Error", f"Failed to get statistics: {str(e)}")
    
    def cleanup_ad_storage(self):
        """Clean up old and unused advertisement files"""
        try:
            reply = QMessageBox.question(
                self, "Cleanup Storage",
                "This will:\\n"
                "• Archive ads older than 30 days\\n"
                "• Remove orphaned image files\\n"
                "• Optimize storage structure\\n"
                "• Clear temporary files\\n\\n"
                "Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                cleaned_count = 0
                archived_count = 0
                
                # Archive old ads
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for ad in self.ads[:]:  # Copy to avoid modification during iteration
                    try:
                        created_date = datetime.fromisoformat(ad.created_at.replace('Z', '+00:00'))
                        if created_date < cutoff_date:
                            # Move to inactive
                            active_meta = self.ad_storage.base_dir / "active" / f"{ad.id}_meta.json"
                            inactive_meta = self.ad_storage.base_dir / "inactive" / f"{ad.id}_meta.json"
                            
                            if active_meta.exists():
                                shutil.move(str(active_meta), str(inactive_meta))
                                
                                # Move ad files too
                                for ext in ['html', 'svg']:
                                    active_file = self.ad_storage.base_dir / "active" / f"{ad.id}_{ext}.{ext}"
                                    inactive_file = self.ad_storage.base_dir / "inactive" / f"{ad.id}_{ext}.{ext}"
                                    if active_file.exists():
                                        shutil.move(str(active_file), str(inactive_file))
                                
                                self.ads.remove(ad)
                                archived_count += 1
                    except Exception as e:
                        self.log_message(f"Error archiving ad {ad.id}: {e}")
                        continue
                
                # Clean up orphaned files
                assets_dir = self.ad_storage.base_dir / "assets" / "images"
                if assets_dir.exists():
                    valid_ad_ids = {ad.id for ad in self.ads}
                    
                    for image_file in assets_dir.glob("*"):
                        try:
                            ad_id = image_file.stem
                            if ad_id not in valid_ad_ids:
                                image_file.unlink()
                                cleaned_count += 1
                        except:
                            pass
                
                # Update UI
                if hasattr(self, 'update_my_ads_table'):
                    self.update_my_ads_table()
                
                QMessageBox.information(self, "Cleanup Complete", 
                                       f"Storage cleanup completed!\\n\\n"
                                       f"• Archived {archived_count} old advertisements\\n"
                                       f"• Cleaned {cleaned_count} orphaned files\\n"
                                       f"• Storage optimized")
                
                self.log_message(f"✅ Storage cleanup: {archived_count} archived, {cleaned_count} cleaned")
                
        except Exception as e:
            self.log_message(f"❌ Error during cleanup: {str(e)}")
            QMessageBox.critical(self, "Cleanup Error", f"Cleanup failed: {str(e)}")
    
    def handle_ad_click_with_storage(self, ad_id, developer_address="", zone="default"):
        """Enhanced ad click handler with storage statistics"""
        try:
            # Update storage stats
            self.ad_storage.update_ad_stats(ad_id, clicks=1)
            
            # Update in-memory stats
            self.stats['clicks'] += 1
            
            # Find and update the ad object
            for ad in self.ads:
                if ad.id == ad_id:
                    if not hasattr(ad, 'click_count'):
                        ad.click_count = 0
                    ad.click_count += 1
                    
                    # Calculate revenue
                    revenue = ad.payout_rate
                    if not hasattr(ad, 'revenue_generated'):
                        ad.revenue_generated = 0
                    ad.revenue_generated += revenue
                    
                    break
            
            # Create click event
            click_event = ClickEvent(
                ad_id=ad_id,
                user_id=f"user_{int(datetime.now().timestamp())}",
                developer_address=developer_address or self.wallet.address,
                advertiser_address=self.wallet.address,
                payout_amount=getattr(ad, 'payout_rate', 0.001),
                timestamp=datetime.now().isoformat()
            )
            
            self.click_events.append(click_event)
            
            # Update database if connected
            if self.db_connected:
                try:
                    self.update_database_on_click(click_event.__dict__)
                except Exception as e:
                    self.log_message(f"Database click update error: {str(e)}")
            
            # Update UI
            if hasattr(self, 'update_my_ads_table'):
                self.update_my_ads_table()
            
            self.log_message(f"💰 Ad click recorded: {ad_id[:8]}... (+{getattr(ad, 'payout_rate', 0.001):.6f} PYC)")
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error handling ad click: {str(e)}")
            return False
'''
        
        # Insert before closing of class (before the last methods)
        class_end_pattern = r'(\n    def closeEvent\(self, event\):)'
        
        content = re.sub(class_end_pattern, management_methods + r'\1', content, flags=re.DOTALL)
        print("✅ Ad management methods injected")
        return content
    
    def inject_wizard_enhancements(self):
        """Inject enhancements to the wizard file"""
        if not os.path.exists(self.wizard_path):
            print("⚠️ Wizard file not found, skipping wizard enhancements")
            return True
        
        print("🧙 Enhancing configuration wizard...")
        
        try:
            with open(self.wizard_path, 'r', encoding='utf-8') as f:
                wizard_content = f.read()
            
            # Check if already enhanced
            if 'def scan_local_network(self):' in wizard_content:
                print("⚠️ Wizard already enhanced")
                return True
            
            # Add network scanning capabilities
            enhanced_methods = '''
    def scan_local_network(self):
        """Scan local network for potential PythonCoin peers"""
        import socket
        import threading
        import ipaddress
        
        print("🔍 Scanning local network for potential peers...")
        
        try:
            # Get local network information
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            print(f"Scanning network: {network}")
            
            found_hosts = []
            scan_complete = threading.Event()
            
            def ping_host(ip_addr):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((str(ip_addr), 8082))
                    sock.close()
                    if result == 0:
                        found_hosts.append(str(ip_addr))
                        print(f"   Found potential peer: {ip_addr}")
                except:
                    pass
            
            # Scan in batches to avoid overwhelming the network
            threads = []
            host_list = list(network.hosts())[:100]  # Limit to first 100 IPs
            
            for ip in host_list:
                if str(ip) != local_ip:
                    t = threading.Thread(target=ping_host, args=(ip,))
                    t.daemon = True
                    t.start()
                    threads.append(t)
                    
                    # Limit concurrent threads
                    if len(threads) >= 20:
                        for thread in threads:
                            thread.join(timeout=3)
                        threads = []
            
            # Wait for remaining threads
            for thread in threads:
                thread.join(timeout=3)
            
            if found_hosts:
                print(f"✅ Network scan complete: {len(found_hosts)} potential peers found")
                for i, host in enumerate(found_hosts, 1):
                    print(f"   {i}. {host}")
            else:
                print("❌ No potential peers found on local network")
            
            return found_hosts
                
        except Exception as e:
            print(f"❌ Network scan failed: {str(e)}")
            return []
    
    def test_peer_connectivity(self, ip, port=8082):
        """Test connectivity to a specific peer"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex((ip, port))
                return result == 0
        except:
            return False
    
    def validate_and_resolve_address(self, address):
        """Validate and resolve IP address or hostname"""
        import socket
        
        # Check if it's already a valid IP
        if self.validate_ip(address):
            return address
        
        # Try to resolve hostname
        try:
            resolved_ip = socket.gethostbyname(address)
            print(f"🔍 Resolved {address} → {resolved_ip}")
            return resolved_ip
        except socket.gaierror:
            print(f"❌ Could not resolve: {address}")
            return None
    
    def configure_peers(self):
        """Enhanced peer configuration with network discovery"""
        print("\\n👥 Enhanced Peer Configuration")
        print("=" * 50)
        print("Configure peer nodes for your PythonCoin network")
        print()
        
        # Network scanning option
        print("🔍 Network Discovery Options:")
        print("1. Scan local network automatically")
        print("2. Enter IP addresses manually")
        print("3. Import from file")
        print("4. Skip peer configuration")
        print()
        
        choice = input("Choose option [1-4]: ").strip()
        peers = []
        
        if choice == '1':
            print("\\n🔍 Starting network scan...")
            discovered_peers = self.scan_local_network()
            
            if discovered_peers:
                print("\\n📋 Select peers to add:")
                for i, peer in enumerate(discovered_peers, 1):
                    print(f"   {i}. {peer}")
                
                selection = input("\\nEnter numbers separated by commas (or 'all' for all): ").strip()
                
                if selection.lower() == 'all':
                    peers = discovered_peers[:]
                elif selection:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(',')]
                        peers = [discovered_peers[i] for i in indices if 0 <= i < len(discovered_peers)]
                    except ValueError:
                        print("❌ Invalid selection")
            else:
                print("\\n❌ No peers discovered. You can add them manually.")
                peers = self.manual_peer_entry()
        
        elif choice == '2':
            peers = self.manual_peer_entry()
        
        elif choice == '3':
            peers = self.import_peers_from_file()
        
        elif choice == '4':
            print("⏭️ Skipping peer configuration")
        
        else:
            print("❌ Invalid choice, using manual entry")
            peers = self.manual_peer_entry()
        
        # Test connectivity to selected peers
        if peers:
            print(f"\\n🔍 Testing connectivity to {len(peers)} peers...")
            online_peers = []
            offline_peers = []
            
            for peer in peers:
                print(f"   Testing {peer}... ", end="", flush=True)
                if self.test_peer_connectivity(peer):
                    print("✅ Online")
                    online_peers.append(peer)
                else:
                    print("❌ Offline")
                    offline_peers.append(peer)
            
            print(f"\\n📊 Connectivity Results:")
            print(f"   • Online: {len(online_peers)} peers")
            print(f"   • Offline: {len(offline_peers)} peers")
            
            if offline_peers:
                include_offline = input("\\nInclude offline peers anyway? [y/N]: ").strip().lower()
                if include_offline not in ['y', 'yes']:
                    peers = online_peers
                    print(f"✅ Using {len(peers)} online peers")
        
        self.config['peers'] = peers
        
        if peers:
            print(f"\\n✅ Configured {len(peers)} peers:")
            for peer in peers:
                print(f"   • {peer}")
    
    def manual_peer_entry(self):
        """Manual peer IP entry with enhanced validation"""
        print("\\n✍️ Manual Peer Entry")
        print("-" * 30)
        print("Enter peer IP addresses or hostnames one by one")
        print("💡 Examples: 192.168.1.100, peer.pythoncoin.network, 10.0.0.5")
        print("Press Enter without input to finish")
        print()
        
        peers = []
        while True:
            peer_input = input(f"Peer #{len(peers)+1} (IP/hostname): ").strip()
            if not peer_input:
                break
            
            # Validate and resolve
            resolved_ip = self.validate_and_resolve_address(peer_input)
            if resolved_ip:
                # Test connectivity
                print(f"🔍 Testing connectivity to {resolved_ip}...")
                if self.test_peer_connectivity(resolved_ip):
                    print(f"✅ Connection successful")
                    peers.append(resolved_ip)
                else:
                    print(f"⚠️ Connection failed (peer may be offline)")
                    add_anyway = input("Add peer anyway? [y/N]: ").strip().lower()
                    if add_anyway in ['y', 'yes']:
                        peers.append(resolved_ip)
            else:
                print("❌ Invalid IP address or hostname")
                continue
            
            print(f"✅ Added: {resolved_ip}")
            
            # Option to continue
            if len(peers) >= 10:
                more = input("\\nAdd more peers? [y/N]: ").strip().lower()
                if more not in ['y', 'yes']:
                    break
        
        return peers
    
    def import_peers_from_file(self):
        """Import peers from a text file"""
        print("\\n📁 Import Peers from File")
        print("-" * 30)
        
        filename = input("Enter filename [peers.txt]: ").strip()
        if not filename:
            filename = "peers.txt"
        
        try:
            peers = []
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        resolved = self.validate_and_resolve_address(line)
                        if resolved:
                            peers.append(resolved)
                        else:
                            print(f"⚠️ Line {line_num}: Invalid address '{line}'")
            
            print(f"✅ Imported {len(peers)} valid peers from {filename}")
            return peers
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            print("💡 Create a text file with one IP/hostname per line")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
'''
            
            # Find the configure_peers method and replace it
            peers_method_start = wizard_content.find('    def configure_peers(self):')
            if peers_method_start != -1:
                peers_method_end = wizard_content.find('\n    def ', peers_method_start + 1)
                if peers_method_end == -1:
                    peers_method_end = wizard_content.find('\n    def run_wizard(self):', peers_method_start)
                
                if peers_method_end != -1:
                    # Replace the method
                    new_wizard_content = (
                        wizard_content[:peers_method_start] + 
                        enhanced_methods + 
                        wizard_content[peers_method_end:]
                    )
                    
                    # Write enhanced wizard
                    with open(self.wizard_path, 'w', encoding='utf-8') as f:
                        f.write(new_wizard_content)
                    
                    print("✅ Wizard enhanced with network discovery")
                    return True
            
            print("⚠️ Could not enhance wizard - method not found")
            return True
            
        except Exception as e:
            print(f"❌ Error enhancing wizard: {e}")
            return False
    
    def run_injection(self):
        """Run the complete injection process"""
        self.print_header()
        
        print("This script will automatically enhance your PythonCoin wallet with:")
        print("• 📁 HTML/SVG advertisement storage system")
        print("• 🌐 Enhanced network configuration with IP discovery")
        print("• 📊 Advanced advertisement analytics and management")
        print("• 🛠️ Improved peer connectivity testing")
        print("• 💾 Automatic backup and restore capabilities")
        print()
        
        confirm = input("Continue with automatic injection? [Y/n]: ").strip().lower()
        if confirm not in ['', 'y', 'yes']:
            print("❌ Injection cancelled")
            return False
        
        print("\n🔍 Starting injection process...")
        
        # Step 1: Validate target
        if not self.validate_target_file():
            return False
        
        # Step 2: Create backup
        print("\n📦 Creating backup...")
        if not self.create_backup():
            return False
        
        try:
            # Step 3: Apply modifications
            print("\n🔧 Applying enhancements...")
            
            content = self.original_content
            
            # Apply all injections
            content = self.inject_imports(content)
            content = self.inject_ad_storage_manager(content)
            content = self.inject_enhanced_init(content)
            content = self.inject_ad_loading_method(content)
            content = self.inject_enhanced_create_advertisement(content)
            content = self.inject_enhanced_preview_method(content)
            content = self.inject_ad_management_methods(content)
            
            self.modified_content = content
            
            # Step 4: Write modified content
            print("\n💾 Writing enhanced file...")
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.write(self.modified_content)
            
            # Step 5: Enhance wizard
            print("\n🧙 Enhancing wizard...")
            self.inject_wizard_enhancements()
            
            # Step 6: Create sample ads directory
            print("\n📁 Setting up ad storage...")
            try:
                from pathlib import Path
                storage_manager = AdStorageManager()
                print(f"✅ Ad storage initialized at: {storage_manager.base_dir}")
            except Exception as e:
                print(f"⚠️ Ad storage setup warning: {e}")
            
            # Success message
            print("\n" + "=" * 70)
            print("🎉 INJECTION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print()
            print("📁 Files modified:")
            print(f"   • {self.target_file} (enhanced with all features)")
            if os.path.exists(self.wizard_path):
                print(f"   • {self.wizard_path} (enhanced with network discovery)")
            print()
            print("📦 Backup created:")
            print(f"   • {self.backup_dir}/{self.target_file}")
            print(f"   • {self.target_file}.original")
            print()
            print("📂 Storage system:")
            print("   • ads_storage/ (advertisement files)")
            print("   • ads_storage/active/ (active ads)")
            print("   • ads_storage/templates/ (HTML/SVG templates)")
            print("   • ads_storage/assets/ (images and styles)")
            print()
            print("🚀 Enhanced features available:")
            print("   • HTML and SVG advertisement creation")
            print("   • Automatic peer discovery and testing")
            print("   • Advanced advertisement analytics")
            print("   • Export and management tools")
            print("   • Enhanced network configuration wizard")
            print()
            print("▶️ Next steps:")
            print("   1. Run: python3 pythoncoin_wizard.py")
            print("   2. Configure your network settings")
            print("   3. Start creating advertisements!")
            print()
            print("🛠️ Restore if needed:")
            print(f"   python3 {sys.argv[0]} --restore")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Injection failed: {e}")
            print("\n🔄 Restoring from backup...")
            self.restore_from_backup()
            return False
    
    def restore_from_backup(self):
        """Restore files from backup"""
        try:
            if self.backup_dir and (self.backup_dir / self.target_file).exists():
                shutil.copy2(self.backup_dir / self.target_file, self.target_file)
                print(f"✅ Restored {self.target_file} from backup")
            
            # Also try .original backup
            original_backup = f"{self.target_file}.original"
            if os.path.exists(original_backup):
                shutil.copy2(original_backup, self.target_file)
                print(f"✅ Restored {self.target_file} from .original backup")
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")

def main():
    """Main entry point for the injection script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PythonCoin Unified Injection Script')
    parser.add_argument('--target', default='pyqt.py', help='Target file to inject (default: pyqt.py)')
    parser.add_argument('--wizard', default='pythoncoin_wizard.py', help='Wizard file to enhance')
    parser.add_argument('--restore', action='store_true', help='Restore from backup')
    parser.add_argument('--force', action='store_true', help='Force injection without confirmation')
    
    args = parser.parse_args()
    
    injector = PythonCoinInjector(args.target)
    injector.wizard_path = args.wizard
    
    if args.restore:
        print("🔄 Restoring from backup...")
        injector.restore_from_backup()
    else:
        if args.force:
            # Skip confirmation
            injector.run_injection()
        else:
            injector.run_injection()

if __name__ == "__main__":
    main()
