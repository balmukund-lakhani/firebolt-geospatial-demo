#!/usr/bin/env python3
"""
Quick Setup Script for Firebolt Geospatial Demo
Helps users get started quickly with the demo application.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies")
        print(f"   Error: {e}")
        return False

def check_env_file():
    """Check if .env file exists and guide user"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Please copy .env.example to .env and configure your Firebolt credentials:")
        print("   cp .env.example .env")
        print("   Then edit .env with your actual Firebolt connection details")
        return False

def main():
    """Main setup function"""
    print("🚀 Firebolt Geospatial Demo - Quick Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ready = check_env_file()
    
    print("\n" + "=" * 50)
    
    if env_ready:
        print("🎉 Setup complete! You can now run the demo:")
        print("   streamlit run app_geospatial_demo.py")
    else:
        print("⚙️  Setup almost complete!")
        print("   1. Configure your .env file with Firebolt credentials")
        print("   2. Run: streamlit run app_geospatial_demo.py")
    
    print("\n📚 For detailed setup instructions, see README.md")

if __name__ == "__main__":
    main()