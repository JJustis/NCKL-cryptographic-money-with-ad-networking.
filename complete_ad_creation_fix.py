#!/usr/bin/env python3
"""
Complete Ad Creation Fix with SVG Support + Mining Tab Fix
This script fixes all three issues:
1. Adds SVG ad creation
2. Enhances JS generation for dashboard compatibility
3. Fixes mining tab not appearing
"""

import os
import re
import shutil
from datetime import datetime

def fix_ad_creation_and_mining():
    """Fix ad creation with SVG support and mining tab issues"""
    
    filename = "pyqt2_enhanced.py"
    backup_filename = f"pyqt2_enhanced_complete_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if not os.path.exists(filename):
        print(f"❌ Error: {filename} not found!")
        return False
    
    print(f"📁 Creating backup: {backup_filename}")
    shutil.copy2(filename, backup_filename)
    
    print(f"📖 Reading {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix the create_ad_trio method to include SVG generation
    print("🎨 Adding SVG ad generation...")
    content = add_svg_generation(content)
    
    # 2. Enhance JS generation for dashboard compatibility
    print("📜 Enhancing JS generation...")
    content = enhance_js_generation(content)
    
    # 3. Fix mining tab creation
    print("⛏️ Fixing mining tab...")
    content = fix_mining_tab_creation(content)
    
    # 4. Ensure mining tab is in create_tabs method
    print("📋 Updating create_tabs method...")
    content = ensure_mining_in_tabs(content)
    
    print(f"💾 Writing fixed {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Complete fix applied successfully!")
    print("📁 Backup saved as:", backup_filename)
    print("\nFixed issues:")
    print("✅ SVG ad generation")
    print("✅ Enhanced JS for dashboard compatibility") 
    print("✅ Mining tab creation")
    print("✅ Tab registration")
    
    return True

def add_svg_generation(content):
    """Add SVG generation to create_ad_trio method"""
    
    # Enhanced create_ad_trio method with SVG support
    enhanced_create_ad_trio = '''
    def create_ad_trio(self, ad_data):
        """Create ad trio files (HTML, JSON metadata, SVG, JS) matching dashboard expectations"""
        try:
            ad_id = ad_data.get('id', str(uuid.uuid4()))
            advertiser_address = ad_data.get('advertiser_address', 'unknown')
            
            # Create metadata matching dashboard format
            metadata = {
                'id': ad_id,
                'title': ad_data.get('title', ''),
                'description': ad_data.get('description', ''),
                'category': ad_data.get('category', 'general'),
                'click_url': ad_data.get('click_url', ''),
                'image_url': ad_data.get('image_url', ''),
                'payout_rate': float(ad_data.get('payout_rate', 0.001)),
                'advertiser_address': advertiser_address,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                'status': 'active',
                'format': 'svg',  # Set to SVG format like the example
                'targeting': ad_data.get('targeting', {
                    'interests': ['general'],
                    'geographic': 'Global',
                    'budget_daily': 1.0,
                    'max_clicks_daily': 1000,
                    'min_age': 18,
                    'max_age': 65
                }),
                'click_count': 0,
                'impression_count': 0,
                'revenue_generated': 0.0,
                'conversion_rate': 0.0
            }
            
            # Generate HTML content
            html_content = self.generate_enhanced_ad_html(metadata)
            
            # Generate SVG content (NEW!)
            svg_content = self.generate_ad_svg(metadata)
            
            # Generate JavaScript adblock
            js_content = self.generate_ad_block_js(metadata)
            
            # Save files
            active_dir = self.base_dir / "active"
            
            # Save JSON metadata
            meta_file = active_dir / f"{ad_id}_meta.json"
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Save HTML
            html_file = active_dir / f"{ad_id}_html.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save SVG (NEW!)
            svg_file = active_dir / f"{ad_id}_svg.svg"
            with open(svg_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # Save JavaScript adblock
            js_file = active_dir / f"{advertiser_address}_adblock.js"
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # Update metadata with file path
            metadata['file_path'] = str(svg_file)
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created ad trio for {ad_id}: HTML, SVG, JSON, JS")
            
            return {
                'success': True,
                'ad_id': ad_id,
                'files': {
                    'meta': str(meta_file),
                    'html': str(html_file),
                    'svg': str(svg_file),
                    'js': str(js_file)
                },
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error creating ad trio: {e}")
            return {
                'success': False,
                'error': f'Failed to create ad files: {str(e)}'
            }

    def generate_ad_svg(self, metadata):
        """Generate SVG version of the advertisement"""
        try:
            title = metadata.get('title', 'Advertisement')
            description = metadata.get('description', '')
            category = metadata.get('category', 'general').title()
            payout = metadata.get('payout_rate', 0.001)
            image_url = metadata.get('image_url', '')
            
            # Create responsive SVG ad
            svg_content = f'''<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <!-- Gradient definitions -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="40%" style="stop-color:#f8fffe;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f0f9ff;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="payoutGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#28a745;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#20c997;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
      <stop offset="25%" style="stop-color:#f7931e;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#0066cc;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#28a745;stop-opacity:1" />
      <animateTransform attributeName="gradientTransform" attributeType="XML" type="translate" values="-100,0;100,0;-100,0" dur="3s" repeatCount="indefinite"/>
    </linearGradient>
    
    <!-- Filter for shadow -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="rgba(0,102,204,0.15)"/>
    </filter>
    
    <!-- Pattern for image placeholder -->
    <pattern id="imgPattern" patternUnits="userSpaceOnUse" width="100" height="100">
      <rect width="100" height="100" fill="#f0f9ff"/>
      <circle cx="50" cy="40" r="15" fill="#0066cc" opacity="0.3"/>
      <rect x="20" y="60" width="60" height="4" fill="#0066cc" opacity="0.2"/>
      <rect x="25" y="70" width="50" height="4" fill="#0066cc" opacity="0.15"/>
    </pattern>
  </defs>
  
  <!-- Main container -->
  <rect x="10" y="10" width="380" height="280" rx="16" ry="16" fill="url(#bgGrad)" stroke="#0066cc" stroke-width="2" filter="url(#shadow)" style="cursor: pointer;">
    <animate attributeName="stroke" values="#0066cc;#0056b3;#0066cc" dur="2s" repeatCount="indefinite"/>
  </rect>
  
  <!-- Top gradient border -->
  <rect x="10" y="10" width="380" height="4" rx="2" ry="2" fill="url(#borderGrad)"/>
  
  <!-- PYC Network badge -->
  <rect x="290" y="25" width="90" height="25" rx="12" fill="linear-gradient(45deg, #ff6b35, #f7931e)" opacity="0.9"/>
  <text x="335" y="40" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="10" font-weight="bold">💎 PYC Network</text>
  
  <!-- Image area -->
  {f'<image x="25" y="50" width="350" height="120" href="{image_url}" preserveAspectRatio="xMidYMid slice">' if image_url else '<rect x="25" y="50" width="350" height="120" fill="url(#imgPattern)" rx="8">'}
    <animateTransform attributeName="transform" type="scale" values="1;1.02;1" dur="4s" repeatCount="indefinite"/>
  {'</image>' if image_url else '</rect>'}
  
  <!-- Title -->
  <text x="25" y="195" fill="#0066cc" font-family="Arial, sans-serif" font-size="18" font-weight="bold">
    <tspan>{title[:35]}{'...' if len(title) > 35 else ''}</tspan>
  </text>
  
  <!-- Description -->
  <text x="25" y="215" fill="#374151" font-family="Arial, sans-serif" font-size="14" opacity="0.9">
    <tspan>{description[:50]}{'...' if len(description) > 50 else ''}</tspan>
  </text>
  
  <!-- Footer line -->
  <line x1="25" y1="235" x2="375" y2="235" stroke="rgba(0,102,204,0.1)" stroke-width="1"/>
  
  <!-- Category -->
  <text x="25" y="255" fill="#0066cc" font-family="Arial, sans-serif" font-size="12" font-weight="600">
    📱 {category} • P2P Network
  </text>
  
  <!-- Payout button -->
  <rect x="280" y="242" width="95" height="26" rx="13" fill="url(#payoutGrad)" style="cursor: pointer;">
    <animate attributeName="opacity" values="1;0.8;1" dur="2s" repeatCount="indefinite"/>
  </rect>
  <text x="327" y="258" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="11" font-weight="bold">
    +{payout:.8f} PYC
  </text>
  
  <!-- Stats badge -->
  <rect x="25" y="270" width="80" height="20" rx="10" fill="rgba(0,102,204,0.1)"/>
  <text x="65" y="282" text-anchor="middle" fill="#0066cc" font-family="Arial, sans-serif" font-size="9" font-weight="600">
    ID: {metadata['id'][:8]}
  </text>
  
  <!-- Click handler -->
  <rect x="10" y="10" width="380" height="280" rx="16" fill="transparent" style="cursor: pointer;" onclick="handleAdClick('{metadata['id']}')"/>
  
  <!-- Hover effects -->
  <style>
    <![CDATA[
    svg:hover rect:first-of-type {{
      filter: url(#shadow) brightness(1.05);
    }}
    ]]>
  </style>
</svg>'''
            
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generating SVG: {e}")
            return self.generate_fallback_svg(metadata)
    
    def generate_fallback_svg(self, metadata):
        """Generate simple fallback SVG if main generation fails"""
        return f'''<svg width="400" height="200" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="200" fill="#f0f9ff" stroke="#0066cc" stroke-width="2" rx="8"/>
  <text x="200" y="80" text-anchor="middle" fill="#0066cc" font-family="Arial" font-size="16" font-weight="bold">
    {metadata.get('title', 'Advertisement')}
  </text>
  <text x="200" y="110" text-anchor="middle" fill="#666" font-family="Arial" font-size="12">
    {metadata.get('description', '')[:40]}
  </text>
  <rect x="150" y="130" width="100" height="30" fill="#28a745" rx="15"/>
  <text x="200" y="150" text-anchor="middle" fill="white" font-family="Arial" font-size="12" font-weight="bold">
    +{metadata.get('payout_rate', 0.001):.6f} PYC
  </text>
</svg>'''
'''
    
    # Replace the existing create_ad_trio method
    pattern = r'def create_ad_trio\(self, ad_data\):.*?return \{[^}]*\}'
    content = re.sub(pattern, enhanced_create_ad_trio.strip(), content, flags=re.DOTALL)
    
    return content

def enhance_js_generation(content):
    """Enhance JS generation for dashboard compatibility"""
    
    enhanced_js_method = '''
    def generate_ad_block_js(self, metadata):
        """Generate JavaScript adblock content matching dashboard expectations"""
        return f\'\'\'// PythonCoin P2P Ad Block Enhanced v2.3.0 - Dashboard Compatible
// Generated: {datetime.now().isoformat()}
// Ad ID: {metadata["id"]}
// Advertiser: {metadata["advertiser_address"]}
// Compatible with dashboard8.php

(function() {{
    "use strict";
    
    const PYTHONCOIN_CONFIG = {{
        adId: "{metadata["id"]}",
        advertiserAddress: "{metadata["advertiser_address"]}",
        payoutRate: {metadata["payout_rate"]},
        clickUrl: "{metadata["click_url"]}",
        title: "{metadata["title"]}",
        description: "{metadata["description"]}",
        category: "{metadata["category"]}",
        imageUrl: "{metadata.get("image_url", "")}",
        createdAt: "{metadata["created_at"]}",
        format: "{metadata.get("format", "html")}",
        targeting: {json.dumps(metadata.get("targeting", {}))}
    }};
    
    // Dashboard8.php compatibility layer
    window.PythonCoinAds = window.PythonCoinAds || [];
    window.PythonCoinAds.push(PYTHONCOIN_CONFIG);
    
    function createPythonCoinAd() {{
        const adZones = document.querySelectorAll("[data-pyc-zone], [data-pythoncoin-zone], .pythoncoin-ad-zone");
        
        if (adZones.length === 0) {{
            // Create default zone if none exists
            const defaultZone = document.createElement("div");
            defaultZone.setAttribute("data-pyc-zone", "default");
            document.body.appendChild(defaultZone);
            adZones = [defaultZone];
        }}
        
        adZones.forEach(zone => {{
            const adContainer = document.createElement("div");
            adContainer.className = "pythoncoin-ad-container";
            
            const imageStyle = PYTHONCOIN_CONFIG.imageUrl ? 
                `background-image: url("${{PYTHONCOIN_CONFIG.imageUrl}}"); background-size: cover; background-position: center;` : "";
            
            // Check if SVG version should be used
            const useSvg = PYTHONCOIN_CONFIG.format === "svg" || zone.hasAttribute("data-svg");
            
            if (useSvg) {{
                // Load SVG version
                adContainer.innerHTML = `
                    <div style="width: 100%; max-width: 400px; margin: 15px auto;">
                        <object data="/ads_storage/active/${{PYTHONCOIN_CONFIG.adId}}_svg.svg" 
                                type="image/svg+xml" 
                                style="width: 100%; height: auto; cursor: pointer;"
                                onclick="handlePythonCoinClick()">
                            <!-- Fallback HTML ad -->
                            <div class="pythoncoin-ad-fallback" onclick="handlePythonCoinClick()" style="
                                border: 2px solid #0066cc;
                                border-radius: 12px;
                                padding: 20px;
                                background: linear-gradient(135deg, #fff 0%, #f0f9ff 100%);
                                margin: 15px 0;
                                cursor: pointer;
                                transition: all 0.3s ease;
                                font-family: 'Segoe UI', Arial, sans-serif;
                                ${{imageStyle}}
                            ">
                                <h3 style="color: #0066cc; margin: 0 0 10px 0;">${{PYTHONCOIN_CONFIG.title}}</h3>
                                <p style="margin: 0 0 15px 0;">${{PYTHONCOIN_CONFIG.description}}</p>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #0066cc;">${{PYTHONCOIN_CONFIG.category}}</span>
                                    <span style="background: #28a745; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">
                                        +${{PYTHONCOIN_CONFIG.payoutRate.toFixed(8)}} PYC
                                    </span>
                                </div>
                            </div>
                        </object>
                    </div>
                `;
            }} else {{
                // Use HTML version
                adContainer.innerHTML = `
                    <div class="pythoncoin-ad" onclick="handlePythonCoinClick()" style="
                        border: 2px solid #0066cc;
                        border-radius: 12px;
                        padding: 20px;
                        background: linear-gradient(135deg, #fff 0%, #f0f9ff 100%);
                        margin: 15px 0;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        position: relative;
                        overflow: hidden;
                        min-height: 150px;
                        ${{imageStyle}}
                    ">
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,249,255,0.8) 100%); z-index: 1;"></div>
                        <div style="position: relative; z-index: 2;">
                            <div style="position: absolute; top: -10px; right: -10px; background: rgba(0,102,204,0.9); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">💎 PYC Network</div>
                            <h3 style="color: #0066cc; font-size: 20px; font-weight: bold; margin: 0 0 10px 0;">${{PYTHONCOIN_CONFIG.title}}</h3>
                            <p style="margin: 0 0 15px 0; background: rgba(255,255,255,0.95); padding: 10px; border-radius: 6px;">${{PYTHONCOIN_CONFIG.description}}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.95); padding: 10px; border-radius: 6px;">
                                <span style="background: #6f42c1; color: white; padding: 6px 12px; border-radius: 15px; font-size: 12px; text-transform: uppercase;">${{PYTHONCOIN_CONFIG.category}}</span>
                                <span style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;">
                                    +${{PYTHONCOIN_CONFIG.payoutRate.toFixed(8)}} PYC
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            }}
            
            zone.appendChild(adContainer);
        }});
    }}
    
    window.handlePythonCoinClick = function() {{
        console.log("[PYC] Ad clicked:", PYTHONCOIN_CONFIG.adId);
        
        // Visual feedback
        const adElement = document.querySelector(".pythoncoin-ad, .pythoncoin-ad-fallback");
        if (adElement) {{
            adElement.style.transform = "scale(0.98)";
            setTimeout(() => {{
                adElement.style.transform = "scale(1)";
            }}, 150);
        }}
        
        // Dashboard8.php compatible tracking
        if (window.dashboardTracker) {{
            window.dashboardTracker.recordClick(PYTHONCOIN_CONFIG);
        }}
        
        // Standard PythonCoin wallet tracking
        if (window.pythonCoinWallet) {{
            window.pythonCoinWallet.recordClick(PYTHONCOIN_CONFIG.adId, {{
                timestamp: new Date().toISOString(),
                advertiser: PYTHONCOIN_CONFIG.advertiserAddress,
                payout: PYTHONCOIN_CONFIG.payoutRate
            }});
        }}
        
        // Server-side tracking
        fetch("/click", {{
            method: "POST",
            headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify({{
                ad_id: PYTHONCOIN_CONFIG.adId,
                advertiser_address: PYTHONCOIN_CONFIG.advertiserAddress,
                payout_amount: PYTHONCOIN_CONFIG.payoutRate,
                timestamp: new Date().toISOString(),
                tracking_data: {{
                    format: PYTHONCOIN_CONFIG.format,
                    targeting: PYTHONCOIN_CONFIG.targeting,
                    user_agent: navigator.userAgent,
                    referrer: document.referrer
                }}
            }})
        }}).then(response => response.json())
        .then(data => {{
            console.log("[PYC] Click recorded:", data);
            showPythonCoinFeedback();
        }})
        .catch(error => console.error("[PYC] Click recording failed:", error));
        
        // Open click URL
        if (PYTHONCOIN_CONFIG.clickUrl && PYTHONCOIN_CONFIG.clickUrl !== "#") {{
            setTimeout(() => {{
                window.open(PYTHONCOIN_CONFIG.clickUrl, "_blank", "noopener,noreferrer");
            }}, 200);
        }}
    }};
    
    function showPythonCoinFeedback() {{
        const feedback = document.createElement("div");
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            font-weight: bold;
            z-index: 10000;
            animation: pycFeedbackPulse 2s ease-out forwards;
            box-shadow: 0 10px 30px rgba(40, 167, 69, 0.4);
        `;
        feedback.textContent = `Earned ${{PYTHONCOIN_CONFIG.payoutRate.toFixed(8)}} PYC!`;
        
        if (!document.getElementById("pyc-feedback-styles")) {{
            const style = document.createElement("style");
            style.id = "pyc-feedback-styles";
            style.textContent = `
                @keyframes pycFeedbackPulse {{
                    0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.5); }}
                    20% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.1); }}
                    30% {{ transform: translate(-50%, -50%) scale(1); }}
                    100% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.8); }}
                }}
            `;
            document.head.appendChild(style);
        }}
        
        document.body.appendChild(feedback);
        setTimeout(() => {{
            if (feedback.parentNode) {{
                feedback.parentNode.removeChild(feedback);
            }}
        }}, 2000);
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === "loading") {{
        document.addEventListener("DOMContentLoaded", createPythonCoinAd);
    }} else {{
        createPythonCoinAd();
    }}
    
    // Dashboard8.php integration
    window.PYTHONCOIN_STATS = function() {{
        return {{
            adId: PYTHONCOIN_CONFIG.adId,
            advertiser: PYTHONCOIN_CONFIG.advertiserAddress,
            payout: PYTHONCOIN_CONFIG.payoutRate,
            version: "2.3.0",
            loaded: true,
            dashboard_compatible: true,
            format: PYTHONCOIN_CONFIG.format
        }};
    }};
    
    // Global PythonCoin API
    window.PythonCoinAPI = window.PythonCoinAPI || {{
        getAds: () => window.PythonCoinAds || [],
        recordClick: (adId) => window.handlePythonCoinClick(),
        getStats: () => window.PYTHONCOIN_STATS()
    }};
}})();

/* Dashboard8.php Compatible Usage:
 * 1. Include this script: <script src="ADVERTISER_ADDRESS_adblock.js"></script>
 * 2. Add ad zones: <div data-pyc-zone="header"></div>
 * 3. For SVG ads: <div data-pyc-zone="main" data-svg></div>
 * 4. Access stats: window.PYTHONCOIN_STATS()
 * 5. List all ads: window.PythonCoinAPI.getAds()
 */\'\'\'
'''
    
    # Replace the existing generate_ad_block_js method
    pattern = r'def generate_ad_block_js\(self, metadata\):.*?return f\'\'\'.*?\'\'\''
    content = re.sub(pattern, enhanced_js_method.strip(), content, flags=re.DOTALL)
    
    return content

def fix_mining_tab_creation(content):
    """Ensure mining tab creation method exists and is complete"""
    
    # Check if create_mining_tab method exists
    if "def create_mining_tab(self):" not in content:
        print("⛏️ Adding complete mining tab method...")
        
        # Add the complete mining tab method
        mining_tab_method = '''
    def create_mining_tab(self):
        """Create mining and blockchain tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mining status and controls
        mining_group = QGroupBox("⛏️ Mining Operations")
        mining_layout = QVBoxLayout(mining_group)
        
        # Status display
        status_layout = QHBoxLayout()
        self.mining_status_label = QLabel("Status: Stopped")
        self.mining_status_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.mining_status_label.setStyleSheet("color: #dc3545;")
        
        self.hashrate_label = QLabel("Hashrate: 0 H/s")
        self.hashrate_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.blocks_mined_label = QLabel("Blocks Mined: 0")
        self.blocks_mined_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        status_layout.addWidget(self.mining_status_label)
        status_layout.addWidget(self.hashrate_label)
        status_layout.addWidget(self.blocks_mined_label)
        mining_layout.addLayout(status_layout)
        
        # Mining controls
        controls_layout = QHBoxLayout()
        self.start_mining_btn = QPushButton("🚀 Start Mining")
        self.start_mining_btn.clicked.connect(self.start_mining)
        self.stop_mining_btn = QPushButton("🛑 Stop Mining")
        self.stop_mining_btn.clicked.connect(self.stop_mining)
        self.stop_mining_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_mining_btn)
        controls_layout.addWidget(self.stop_mining_btn)
        mining_layout.addLayout(controls_layout)
        
        layout.addWidget(mining_group)
        
        # Blockchain info
        blockchain_group = QGroupBox("🔗 Blockchain Information")
        blockchain_layout = QFormLayout(blockchain_group)
        
        self.blockchain_height_label = QLabel("0")
        blockchain_layout.addRow("Height:", self.blockchain_height_label)
        
        self.pending_tx_label = QLabel("0")
        blockchain_layout.addRow("Pending TX:", self.pending_tx_label)
        
        self.genesis_status_label = QLabel("Not Created")
        blockchain_layout.addRow("Genesis:", self.genesis_status_label)
        
        layout.addWidget(blockchain_group)
        
        # Mining earnings
        earnings_group = QGroupBox("💰 Mining Earnings")
        earnings_layout = QFormLayout(earnings_group)
        
        self.total_earnings_label = QLabel("0.00000000 PYC")
        self.total_earnings_label.setStyleSheet("color: #28a745; font-weight: bold;")
        earnings_layout.addRow("Total Earned:", self.total_earnings_label)
        
        layout.addWidget(earnings_group)
        
        # Initialize mining attributes
        if not hasattr(self, 'mining_thread'):
            self.mining_thread = None
            self.mining_enabled = False
            self.total_blocks_mined = 0
        
        self.tab_widget.addTab(widget, "⛏️ Mining")

    def start_mining(self):
        """Start the mining process"""
        try:
            if hasattr(self, 'mining_thread') and self.mining_thread and self.mining_thread.mining:
                self.log_message("⚠️ Mining already running")
                return
            
            if not hasattr(self, 'blockchain') or not self.blockchain:
                self.log_message("❌ No blockchain available")
                QMessageBox.warning(self, "Mining Error", "No blockchain available for mining")
                return
            
            # Create genesis block if needed
            if not self.blockchain.genesis_complete:
                self.blockchain.create_genesis_block([self.wallet.address])
                self.log_message("✅ Genesis block created")
                if hasattr(self, 'genesis_status_label'):
                    self.genesis_status_label.setText("✅ Created")
            
            # Create mining thread
            self.mining_thread = CryptoMiningThread(self.blockchain, self.wallet, self)
            self.mining_thread.status_update.connect(self.on_mining_status)
            self.mining_thread.block_mined.connect(self.on_block_mined)
            self.mining_thread.hashrate_update.connect(self.on_hashrate_update)
            
            self.mining_thread.start_mining()
            self.mining_enabled = True
            
            self.log_message("🚀 Mining started!")
            
            # Update UI
            if hasattr(self, 'mining_status_label'):
                self.mining_status_label.setText("Status: Mining ⛏️")
                self.mining_status_label.setStyleSheet("color: #28a745;")
            if hasattr(self, 'start_mining_btn'):
                self.start_mining_btn.setEnabled(False)
            if hasattr(self, 'stop_mining_btn'):
                self.stop_mining_btn.setEnabled(True)
            
        except Exception as e:
            self.log_message(f"❌ Mining start error: {e}")
            QMessageBox.critical(self, "Mining Error", f"Failed to start mining:\\n{str(e)}")

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
            if hasattr(self, 'mining_status_label'):
                self.mining_status_label.setText("Status: Stopped")
                self.mining_status_label.setStyleSheet("color: #dc3545;")
            if hasattr(self, 'start_mining_btn'):
                self.start_mining_btn.setEnabled(True)
            if hasattr(self, 'stop_mining_btn'):
                self.stop_mining_btn.setEnabled(False)
            if hasattr(self, 'hashrate_label'):
                self.hashrate_label.setText("Hashrate: 0 H/s")
            
        except Exception as e:
            self.log_message(f"❌ Mining stop error: {e}")

    def on_mining_status(self, message):
        """Handle mining status updates"""
        self.log_message(message)

    def on_block_mined(self, block_data):
        """Handle block mined event"""
        try:
            self.total_blocks_mined += 1
            block_reward = 50.0
            
            self.log_message(f"🎉 Block {block_data['index']} mined! Reward: {block_reward} PYC")
            
            # Update UI
            if hasattr(self, 'blocks_mined_label'):
                self.blocks_mined_label.setText(f"Blocks Mined: {self.total_blocks_mined}")
            
            if hasattr(self, 'total_earnings_label'):
                total_earned = self.total_blocks_mined * block_reward
                self.total_earnings_label.setText(f"{total_earned:.8f} PYC")
            
            # Update main wallet balance
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
'''
        
        # Find a good place to insert the mining methods (before closeEvent)
        if "def closeEvent(self, event):" in content:
            content = content.replace("def closeEvent(self, event):", mining_tab_method + "\n    def closeEvent(self, event):")
        else:
            # Insert before the last method
            content = content.replace("def show_about(self):", mining_tab_method + "\n    def show_about(self):")
    
    return content

def ensure_mining_in_tabs(content):
    """Ensure mining tab is included in create_tabs method"""
    
    # Check if create_tabs method includes mining tab
    if "self.create_mining_tab()" not in content:
        print("📋 Adding mining tab to create_tabs method...")
        
        # Find create_tabs method and add mining tab
        pattern = r'(def create_tabs\(self\):.*?)(self\.create_developers_tab\(\))'
        replacement = r'\1\2\n        self.create_mining_tab()'
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return content

if __name__ == "__main__":
    print("🚀 PythonCoin Complete Fix Script")
    print("=" * 50)
    
    try:
        success = fix_ad_creation_and_mining()
        if success:
            print("\n🎉 All fixes applied successfully!")
            print("\nYour wallet now has:")
            print("✅ SVG ad generation")
            print("✅ Enhanced dashboard8.php compatible JS")
            print("✅ Working mining tab")
            print("\n🚀 Run: python pyqt2_enhanced.py")
        else:
            print("\n❌ Fix failed. Please check the error messages above.")
    except Exception as e:
        print(f"\n💥 Script error: {e}")
        print("Please check your file and try again.")
