#!/usr/bin/env python3
"""
Build executable for the main POS Application
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

def create_pos_spec_file():
    """Create PyInstaller spec file for POS application"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\pc\\Music\\pos_app'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('views', 'views'),
        ('models', 'models'),
        ('utils', 'utils'),
        ('controllers', 'controllers'),
        ('assets', 'assets'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'psycopg2',
        'psycopg2.extras',
        'sqlalchemy',
        'pathlib',
        'datetime',
        're',
        'json',
        'logging',
        'decimal',
        'fractions',
        'hashlib',
        'uuid',
        'threading',
        'queue',
        'time',
        'random',
        'math',
        'statistics',
        'csv',
        'xlsxwriter',
        'openpyxl',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.platypus',
        'reportlab.lib.units',
        'barcode',
        'barcode.writer',
        'qrcode',
        'qrcode.image',
        'qrcode.image.pil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
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
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('pos_system.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created pos_system.spec file")

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'config',
        'views',
        'models',
        'utils',
        'controllers'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_or_dir in required_files:
        if os.path.exists(file_or_dir):
            existing_files.append(file_or_dir)
        else:
            missing_files.append(file_or_dir)
    
    if not os.path.exists('main.py'):
        missing_files.append('main.py')
    
    if missing_files:
        print(f"⚠️  Missing optional files/directories: {missing_files}")
        print(f"✅ Found required files/directories: {existing_files}")
        if 'main.py' in missing_files:
            print("❌ main.py is required but missing!")
            return False
        else:
            print("⚠️  Some optional directories missing, but main.py exists")
            return True
    
    print("✅ All required files/directories found")
    return True

def build_pos_exe():
    """Build the POS application executable"""
    print("🔨 Building POS Application executable...")
    
    # Clean previous builds with error handling
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Cleaned {dir_name}")
            except PermissionError as e:
                print(f"⚠️  Could not clean {dir_name} (files in use): {e}")
                print("   Continuing with build...")
            except Exception as e:
                print(f"⚠️  Error cleaning {dir_name}: {e}")
    
    # Build the EXE
    try:
        result = subprocess.run([
            'pyinstaller', 
            '--onefile',
            '--windowed',  # No console window for GUI app
            '--name=POSSystem',
            '--hidden-import=PySide6',
            '--hidden-import=psycopg2',
            '--hidden-import=sqlalchemy',
            '--exclude-module=PyQt6',
            '--exclude-module=PyQt6.QtCore',
            '--exclude-module=PyQt6.QtWidgets',
            '--exclude-module=PyQt6.QtGui',
            'main.py'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"📦 Executable created: {os.path.abspath('dist/POSSystem.exe')}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script"""
    installer_script = '''@echo off
echo POS System Installer
echo =====================
echo.

echo Creating installation directory...
if not exist "C:\\POSSystem" mkdir "C:\\POSSystem"

echo Copying files...
copy "dist\\POSSystem.exe" "C:\\POSSystem\\"
xcopy "config" "C:\\POSSystem\\config\\" /E /I /Y
xcopy "assets" "C:\\POSSystem\\assets\\" /E /I /Y
xcopy "static" "C:\\POSSystem\\static\\" /E /I /Y

echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\POSSystem.lnk'); $Shortcut.TargetPath = 'C:\\POSSystem\\POSSystem.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run POS System from your desktop or from C:\\POSSystem\\POSSystem.exe
echo.
pause
'''
    
    with open('install_pos.bat', 'w') as f:
        f.write(installer_script)
    
    print("✅ Created install_pos.bat installer script")

def create_readme():
    """Create README for the executable"""
    readme_content = '''# POS System - Executable Version

## Installation

1. Run `install_pos.bat` to install the application
2. The application will be installed to `C:\\POSSystem`
3. A desktop shortcut will be created

## Manual Installation

1. Create a folder `C:\\POSSystem`
2. Copy `POSSystem.exe` to this folder
3. Copy the `config`, `assets`, and `static` folders to the same location
4. Run `POSSystem.exe`

## Requirements

- Windows 10 or later
- PostgreSQL database server running
- Database connection configured in `config/database.json`

## Configuration

Edit `config/database.json` to configure your database connection:

```json
{
    "host": "localhost",
    "port": 5432,
    "database": "pos_network",
    "user": "admin",
    "password": "admin"
}
```

## Troubleshooting

- If the application doesn't start, check the database connection
- Make sure PostgreSQL is running
- Verify the database exists and credentials are correct
- Check the logs in the application directory

## Support

For support, contact the system administrator.
'''
    
    with open('README_EXE.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created README_EXE.md")

def main():
    """Main build process"""
    print("🚀 Building POS Application Executable")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir('C:/Users/pc/Music/pos_app')
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Check requirements
    if not check_requirements():
        print("❌ Cannot build due to missing files")
        return
    
    # Create spec file
    create_pos_spec_file()
    
    # Build the executable
    if build_pos_exe():
        # Create additional files
        create_installer_script()
        create_readme()
        
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETE!")
        print("=" * 60)
        print("📦 Files created:")
        print(f"   • dist/POSSystem.exe - Main application")
        print(f"   • install_pos.bat - Installation script")
        print(f"   • README_EXE.md - Installation guide")
        print("\n📋 Next Steps:")
        print("   1. Run install_pos.bat to install")
        print("   2. Or manually copy dist/POSSystem.exe and required folders")
        print("   3. Configure database connection in config/database.json")
        print("   4. Run POSSystem.exe")
        print("\n📁 All files are in the 'dist' folder")
    else:
        print("❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
