#!/usr/bin/env python3
"""
Kill POS processes and rebuild EXE
"""
import os
import subprocess
import time

def kill_pos_processes():
    """Kill any running POS processes"""
    try:
        # Kill POSSystem.exe processes
        result = subprocess.run(['taskkill', '/F', '/IM', 'POSSystem.exe'], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Killed POSSystem.exe processes")
        else:
            print("⚠️  No POSSystem.exe processes found")
    except Exception as e:
        print(f"Error killing processes: {e}")

def clean_and_build():
    """Clean and rebuild"""
    # Kill processes
    kill_pos_processes()
    time.sleep(2)
    
    # Clean directories
    import shutil
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Cleaned {dir_name}")
            except Exception as e:
                print(f"⚠️  Could not clean {dir_name}: {e}")
    
    # Build
    os.system('python build_pos_exe.py')

if __name__ == "__main__":
    clean_and_build()
