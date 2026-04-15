"""
VS Code Optimized Runner for Driver Monitoring System
Run this file directly in VS Code for optimal experience
"""

import os
import sys
import subprocess

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"   ❌ Python 3.8+ required. You have {python_version.major}.{python_version.minor}")
        return False
    
    # Check virtual environment
    if not os.path.exists("venv"):
        print("   ⚠️  Virtual environment not found. Creating...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("   ✅ Virtual environment created")
    
    # Check requirements
    try:
        import cv2
        import mediapipe
        print("   ✅ Required packages installed")
    except ImportError:
        print("   ⚠️  Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   ✅ Requirements installed")
    
    return True

def run_system():
    """Run the main system"""
    print("\n" + "="*60)
    print("🚗 Starting Driver Drowsiness Detection System")
    print("="*60)
    print("\n📌 Controls:")
    print("   Press 'q' - Quit")
    print("   Press 's' - Save screenshot")
    print("   Press 'r' - Reset statistics")
    print("="*60 + "\n")
    
    # Import and run main
    try:
        import main
        if hasattr(main, 'DriverMonitoringSystem'):
            system = main.DriverMonitoringSystem()
            system.run()
        else:
            exec(open('main.py').read())
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: python test_system.py")
        print("   2. Check camera connection")
        print("   3. Ensure all packages installed")

def main():
    """Main entry point"""
    if check_environment():
        run_system()
    else:
        print("\n❌ Environment check failed. Please fix issues and try again.")

if __name__ == "__main__":
    main()