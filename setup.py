import os
import subprocess
import sys

def setup():
    print("="*60)
    print("🔧 Driver Monitoring System - Setup")
    print("="*60)
    
    # Create directories
    print("\n📁 Creating directories...")
    for dir_name in ['logs', 'screenshots', 'models', 'datasets', 'tests']:
        os.makedirs(dir_name, exist_ok=True)
        print(f"   ✅ Created: {dir_name}/")
    
    # Install requirements
    print("\n📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   ✅ All packages installed successfully!")
    except Exception as e:
        print(f"   ❌ Error installing packages: {e}")
        print("   Try running: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n📌 Next Steps:")
    print("   1. Run: python test_system.py")
    print("   2. Run: python main.py")
    print("="*60)

if __name__ == "__main__":
    setup()