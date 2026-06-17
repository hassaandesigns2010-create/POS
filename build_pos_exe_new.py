#!/usr/bin/env python3
"""
Build executable for POS Application
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
    """Create PyInstaller spec file for POS application"""
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
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'pyparsing',
        'numpy',
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
        'pyparsing.testing',
        'matplotlib.testing',
        'matplotlib.tests',
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
    name='POSSystem',
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
    
    with open('pos_system.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created pos_system.spec file")

def build_exe():
    """Build the POS executable"""
    print("🔨 Building POS System executable...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name} directory")
    
    # Build the EXE
    try:
        result = subprocess.run([
            'pyinstaller', 
            'pos_system.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"📦 Executable created: {os.path.abspath('dist/POSSystem.exe')}")
        
        # Create run script
        run_script = '''@echo off
echo Starting POS System...
POSSystem.exe
pause'''
        
        with open('dist/run_pos_system.bat', 'w') as f:
            f.write(run_script)
        
        print("✅ Created run_pos_system.bat")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def main():
    """Main build process"""
    print("🚀 Building POS Application Executable")
    print("=" * 60)
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_exe():
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETE!")
        print("=" * 60)
        print("📦 Executable created:")
        print(f"   • dist/POSSystem.exe - Main POS application")
        print(f"   • dist/run_pos_system.bat - Easy launcher")
        print("\n📋 Usage:")
        print("   • Double-click POSSystem.exe to run")
        print("   • Or use run_pos_system.bat for console output")
        print("\n📁 All files are in the 'dist' folder")
        print("\n⚠️  Note: Make sure PostgreSQL is running and accessible")
    else:
        print("❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
