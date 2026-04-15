import cv2
import sys

def test_camera():
    print("📷 Testing camera...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("   ❌ Camera not found!")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("   ❌ Failed to read frame!")
            return False
        
        print("   ✅ Camera working!")
        cap.release()
        return True
    except Exception as e:
        print(f"   ❌ Camera error: {e}")
        return False

def test_imports():
    print("\n📦 Testing imports...")
    packages = ['cv2', 'mediapipe', 'numpy', 'scipy', 'pygame', 'yaml']
    all_ok = True
    
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Not installed")
            all_ok = False
    
    return all_ok

def main():
    print("="*60)
    print("🔍 System Diagnostic Test")
    print("="*60)
    
    camera_ok = test_camera()
    imports_ok = test_imports()
    
    print("\n" + "="*60)
    if camera_ok and imports_ok:
        print("✅ All tests passed! System is ready.")
        print("\n🚀 Run the system: python main.py")
    else:
        print("❌ Some tests failed. Please fix issues.")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Check camera connection")
        print("   3. Restart VS Code")
    print("="*60)

if __name__ == "__main__":
    main()