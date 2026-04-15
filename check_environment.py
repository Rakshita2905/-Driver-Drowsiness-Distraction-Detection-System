"""
Environment Checker for Driver Monitoring System
Run this to verify everything is set up correctly
"""

import sys
import os
import importlib

def check_python():
    """Check Python version"""
    print("\n📌 Python Version:")
    version = sys.version_info
    print(f"   {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ OK")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_packages():
    """Check required packages"""
    print("\n📌 Required Packages:")
    packages = [
        'cv2', 'mediapipe', 'numpy', 'scipy', 
        'pygame', 'yaml', 'pandas', 'sklearn'
    ]
    
    all_ok = True
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check required directories"""
    print("\n📌 Required Directories:")
    directories = ['src', 'logs', 'screenshots', 'models', 'datasets', 'tests']
    
    all_ok = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   ⚠️  {directory}/ - CREATING...")
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ {directory}/ created")
    
    return True

def check_files():
    """Check required files"""
    print("\n📌 Required Files:")
    files = ['main.py', 'config.yaml', 'requirements.txt']
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            all_ok = False
    
    return all_ok

def check_camera():
    """Check camera availability"""
    print("\n📌 Camera:")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✅ Camera detected")
            cap.release()
            return True
        else:
            print("   ⚠️  No camera detected")
            return False
    except:
        print("   ❌ Could not test camera")
        return False

def main():
    """Main checker function"""
    print("="*60)
    print("🔍 Environment Checker - Driver Monitoring System")
    print("="*60)
    
    results = []
    
    results.append(("Python", check_python()))
    results.append(("Packages", check_packages()))
    results.append(("Directories", check_directories()))
    results.append(("Files", check_files()))
    results.append(("Camera", check_camera()))
    
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 Environment is ready!")
        print("\n🚀 Run: python main.py")
    else:
        print("\n⚠️  Some checks failed. Please fix issues.")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Check camera connection")
        print("   3. Ensure all files are present")
    
    print("="*60)

if __name__ == "__main__":
    main()