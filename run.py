#!/usr/bin/env python
"""
Simple runner for Driver Monitoring System
"""

import subprocess
import sys
import os

def main():
    print("Starting Driver Monitoring System...")
    
    # Check if virtual environment exists
    if os.path.exists("venv"):
        # Activate virtual environment
        if sys.platform == "win32":
            activate_script = "venv\\Scripts\\activate"
        else:
            activate_script = "source venv/bin/activate"
        print(f"Activate venv with: {activate_script}")
    
    # Run main system
    try:
        # Import and run main
        import main
        # If main has a run function
        if hasattr(main, 'DriverMonitoringSystem'):
            system = main.DriverMonitoringSystem()
            system.run()
        else:
            # Direct execution
            exec(open('main.py').read())
    except KeyboardInterrupt:
        print("\n\nSystem stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: python test_system.py")

if __name__ == "__main__":
    main()