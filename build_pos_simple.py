#!/usr/bin/env python3
"""
Build executable for POS Application (Simple Version - No Matplotlib)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")

def create_spec_file():
    """Create PyInstaller spec file for POS application without matplotlib"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'pos_app',
        'pos_app.controllers',
        'pos_app.views', 
        'pos_app.models',
        'pos_app.utils',
        'pos_app.database',
        'bcrypt',
        'reportlab',
        'psycopg2',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'pytest',
        'unittest',
        'test',
        'tests',
        'tkinter',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'matplotlib',
        'pyparsing',
        'pyparsing.testing',
        'matplotlib.testing',
        'matplotlib.tests',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='POSSystemSimple',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('pos_system_simple.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created pos_system_simple.spec file")

def build_exe():
    """Build the POS executable"""
    print("🔨 Building POS System Simple executable (no analytics)...")
    
    # Clean previous builds (skip if files are in use)
    for dir_name in ['build', 'dist_simple']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"🧹 Cleaned {dir_name} directory")
            except PermissionError:
                print(f"⚠️  Could not clean {dir_name} - files may be in use")
    
    # Build the EXE
    try:
        result = subprocess.run([
            'pyinstaller', 
            '--distpath=dist_simple',
            '--workpath=build_simple',
            'pos_system_simple.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"📦 Executable created: {os.path.abspath('dist_simple/POSSystemSimple.exe')}")
        
        # Create run script
        run_script = '''@echo off
echo Starting POS System (Simple Version)...
POSSystemSimple.exe
pause'''
        
        with open('dist_simple/run_pos_system_simple.bat', 'w') as f:
            f.write(run_script)
        
        print("✅ Created run_pos_system_simple.bat")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_analytics_warning():
    """Create a warning file about disabled analytics"""
    warning = '''
POS SYSTEM - SIMPLE VERSION
===========================

This version has the following limitations:
- Advanced Analytics Center is DISABLED
- Charts and graphs are not available
- Data visualization features are disabled

These features were disabled to ensure the application runs without
matplotlib/pyparsing dependency issues.

All other POS functionality is fully available:
- Sales and billing
- Inventory management  
- Customer management
- Reports (basic text-based)
- Receipt printing
- Database operations

If you need analytics features, please use the Python version
or install the required dependencies manually.
'''
    
    with open('dist_simple/ANALYTICS_DISABLED.txt', 'w') as f:
        f.write(warning)
    
    print("✅ Created analytics warning file")

def main():
    """Main build process"""
    print("🚀 Building POS Application Simple Executable (No Matplotlib)")
    print("=" * 70)
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_exe():
        # Create warning file
        create_analytics_warning()
        
        print("\n" + "=" * 70)
        print("🎉 BUILD COMPLETE!")
        print("=" * 70)
        print("📦 Executable created:")
        print(f"   • dist_simple/POSSystemSimple.exe - Main POS application (no analytics)")
        print(f"   • dist_simple/run_pos_system_simple.bat - Easy launcher")
        print(f"   • dist_simple/ANALYTICS_DISABLED.txt - Feature limitations")
        print("\n📋 Usage:")
        print("   • Double-click POSSystemSimple.exe to run")
        print("   • Or use run_pos_system_simple.bat for console output")
        print("\n⚠️  NOTE:")
        print("   • Advanced Analytics Center is disabled")
        print("   • All other POS features work normally")
        print("   • Make sure PostgreSQL is running and accessible")
        print("\n📁 All files are in the 'dist_simple' folder")
    else:
        print("❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
