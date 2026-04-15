#!/usr/bin/env python
"""
Quick Start Script for Driver Monitoring System
This script handles everything automatically
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🚗 DRIVER DROWSINESS DETECTION SYSTEM 🚗             ║
    ║                                                          ║
    ║     Real-time Driver Monitoring with AI                  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_camera():
    """Check if camera is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            return True
        return False
    except:
        return False

def main():
    """Main start function"""
    print_banner()
    
    # Check camera
    print("📷 Checking camera...")
    if check_camera():
        print("   ✅ Camera detected")
    else:
        print("   ⚠️  Camera not found. Please connect a camera.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check if we're in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("\n📦 Setting up virtual environment...")
        if not os.path.exists("venv"):
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        
        # Run with virtual environment
        if sys.platform == "win32":
            python_exe = "venv\\Scripts\\python.exe"
        else:
            python_exe = "venv/bin/python"
        
        print("   ✅ Virtual environment ready")
        print("\n🚀 Starting system in virtual environment...")
        subprocess.run([python_exe, "main.py"])
    else:
        # Already in virtual environment
        print("\n🚀 Starting system...")
        import main
        system = main.DriverMonitoringSystem()
        system.run()

if __name__ == "__main__":
    main()