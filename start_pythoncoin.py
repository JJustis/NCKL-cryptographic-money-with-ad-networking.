#!/usr/bin/env python3
"""
PythonCoin Complete Startup Script
Automatically starts the PyQt application with proper error handling
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    
    required_packages = [
        'PyQt5',
        'requests',
        'qrcode'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    # Check for mysql-connector-python (optional)
    try:
        import mysql.connector
        print("✅ mysql-connector-python is installed (database features enabled)")
    except ImportError:
        print("⚠️  mysql-connector-python not installed (database features limited)")
        print("   Install with: pip install mysql-connector-python")


def start_pythoncoin_wallet():
    """Start the PythonCoin wallet application"""
    
    script_path = Path("pyqt2_fixed.py")
    
    if not script_path.exists():
        print("❌ pyqt2_fixed.py not found!")
        print("Make sure you're in the correct directory.")
        return False
    
    print("🚀 Starting PythonCoin Complete Wallet...")
    print("=" * 50)
    
    try:
        # Start the application
        process = subprocess.run([sys.executable, str(script_path)], 
                               capture_output=False, text=True)
        
        if process.returncode == 0:
            print("✅ Application closed normally")
        else:
            print(f"❌ Application exited with code: {process.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True


def main():
    """Main startup function"""
    
    print("🌐 PythonCoin Complete Wallet Startup Script")
    print("=" * 60)
    print("Version: 2.3.0 - Full Dashboard API Support")
    print("=" * 60)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check requirements
    print("\n🔍 Checking requirements...")
    check_requirements()
    
    # Start the wallet
    print("\n🚀 Starting wallet application...")
    success = start_pythoncoin_wallet()
    
    if not success:
        print("\n❌ Failed to start the application properly")
        print("Check the error messages above for troubleshooting")
    else:
        print("\n✅ Application startup completed")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
