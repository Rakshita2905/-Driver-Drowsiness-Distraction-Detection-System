"""
Simple Environment Checker - Only checks essential packages
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

def check_essential_packages():
    """Check only essential packages"""
    print("\n📌 Essential Packages:")
    essential_packages = ['cv2', 'mediapipe', 'numpy', 'yaml']
    
    all_ok = True
    for package in essential_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            all_ok = False
    
    print("\n📌 Optional Packages (not required):")
    optional_packages = ['scipy', 'pygame', 'pandas', 'sklearn']
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} (installed)")
        except ImportError:
            print(f"   ⚠️  {package} (optional - not needed)")
    
    return all_ok

def check_directories():
    """Check required directories"""
    print("\n📌 Required Directories:")
    directories = ['src', 'logs', 'screenshots']
    
    all_ok = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ {directory}/ created")
    
    return True

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
    results.append(("Essential Packages", check_essential_packages()))
    results.append(("Directories", check_directories()))
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
        print("\n🚀 Run: python main_simple.py")
    else:
        print("\n⚠️  Some essential checks failed. Please fix issues.")
    
    print("="*60)

if __name__ == "__main__":
    main()