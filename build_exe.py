#!/usr/bin/env python3
"""
Build executable for Stock Analysis Tools
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
    """Create PyInstaller spec file for stock analysis"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['comprehensive_stock_analysis.py'],
    pathex=['C:\\Users\\pc\\Music\\pos_app'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'psycopg2',
        'psycopg2.extras',
        'pathlib',
        'datetime',
        're'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='StockAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='stock_icon.ico' if os.path.exists('stock_icon.ico') else None,
)
'''
    
    with open('stock_analyzer.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created stock_analyzer.spec file")

def create_icon():
    """Create a simple icon file (optional)"""
    # This is optional - if no icon exists, EXE will have default icon
    pass

def build_exe():
    """Build the executable"""
    print("🔨 Building Stock Analyzer executable...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Build the EXE
    try:
        result = subprocess.run([
            'pyinstaller', 
            '--onefile',
            '--console',
            '--name=StockAnalyzer',
            'comprehensive_stock_analysis.py'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"📦 Executable created: {os.path.abspath('dist/StockAnalyzer.exe')}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_quick_exe():
    """Build quick stock fix executable"""
    print("🔨 Building Quick Stock Fix executable...")
    
    try:
        result = subprocess.run([
            'pyinstaller', 
            '--onefile',
            '--console',
            '--name=QuickStockFix',
            'quick_stock_fix.py'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Quick Stock Fix build completed!")
        print(f"📦 Executable created: {os.path.abspath('dist/QuickStockFix.exe')}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Quick Stock Fix build failed: {e}")
        return False
    
    return True

def create_standalone_script():
    """Create a standalone script that doesn't require database connection"""
    standalone_script = '''#!/usr/bin/env python3
"""
Standalone Stock Analysis Tool - Analyzes backup files without database connection
"""

import os
import re
from datetime import datetime
from pathlib import Path

def analyze_backups_only():
    """Analyze backup files without database connection"""
    
    print("=" * 80)
    print("STANDALONE STOCK ANALYSIS - BACKUP FILES ONLY")
    print("=" * 80)
    
    backup_dir = Path("C:/Users/pc/Documents/backups")
    backup_files = sorted(backup_dir.glob("pos_backup_*.sql"))
    
    if not backup_files:
        print("No backup files found!")
        return
    
    print(f"Found {len(backup_files)} backup files")
    print()
    
    backup_analysis = {}
    
    for backup_file in backup_files:
        print(f"Analyzing: {backup_file.name}")
        
        # Extract date from filename
        date_match = re.search(r'(\\d{8})_(\\d{6})', backup_file.name)
        if date_match:
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            backup_date = datetime.strptime(date_str, "%Y%m%d %H%M%S")
        else:
            backup_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count products and stock
            product_count = content.count('COPY public.products')
            
            # Simple stock extraction (basic approach)
            stock_pattern = r'\\t(\\d+\\.?\\d*)\\t'
            stock_matches = re.findall(stock_pattern, content)
            
            total_stock = 0
            for match in stock_matches[:1000]:  # Limit to avoid memory issues
                try:
                    total_stock += float(match)
                except:
                    pass
            
            backup_analysis[backup_file.name] = {
                'date': backup_date,
                'product_count': product_count,
                'estimated_stock': total_stock,
                'file_size': backup_file.stat().st_size
            }
            
            print(f"  Date: {backup_date}")
            print(f"  Products: ~{product_count}")
            print(f"  Estimated Stock: {total_stock:,.0f}")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Show timeline
    print("BACKUP TIMELINE:")
    print("-" * 50)
    
    for name, data in sorted(backup_analysis.items(), key=lambda x: x[1]['date']):
        print(f"{data['date']}: {name}")
        print(f"  Products: {data['product_count']}, Stock: {data['estimated_stock']:,.0f}")
    
    print("\\nAnalysis complete!")

if __name__ == "__main__":
    analyze_backups_only()
'''
    
    with open('standalone_stock_analysis.py', 'w', encoding='utf-8') as f:
        f.write(standalone_script)
    
    print("Created standalone_stock_analysis.py")

def main():
    """Main build process"""
    print("🚀 Building Stock Analysis Tools Executable")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir('C:/Users/pc/Music/pos_app')
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create standalone script
    create_standalone_script()
    
    # Build main executable
    if build_exe():
        # Build quick fix executable
        create_quick_exe()
        
        print("\\n" + "=" * 60)
        print("🎉 BUILD COMPLETE!")
        print("=" * 60)
        print("📦 Executables created:")
        print(f"   • dist/StockAnalyzer.exe - Comprehensive analysis")
        print(f"   • dist/QuickStockFix.exe - Quick stock fixes")
        print(f"   • standalone_stock_analysis.py - Backup-only analysis")
        print("\\n📋 Usage:")
        print("   • StockAnalyzer.exe - Full database analysis")
        print("   • QuickStockFix.exe - Fix zero stock issues")
        print("   • standalone_stock_analysis.py - Analyze backups only")
        print("\\n📁 All files are in the 'dist' folder")
    else:
        print("❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
