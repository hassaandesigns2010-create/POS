# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for POS Application
"""
import os

# Main script path - use absolute path
main_script = os.path.abspath('main.py')

# Collect all data files
datas = []
# Include configuration files
if os.path.exists('config'):
    datas.append(('config', 'config'))

# Include assets if they exist
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

# Hidden imports to ensure proper module detection
hiddenimports = [
    'pos_app',
    'pos_app.controllers',
    'pos_app.views', 
    'pos_app.models',
    'pos_app.utils',
    'pos_app.database',
]

# Binary exclusions
binaries = []

# Analysis options
a = Analysis(
    [main_script],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Exclude development/testing modules
        'pytest',
        'unittest',
        'test',
        'tests',
        # Exclude problematic modules
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        # Exclude PyQt6 to avoid Qt binding conflicts (we use PySide6)
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    upx_dir=None,
    console=False,  # Windows GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# EXE options
exe = EXE(
    a,
    app_name='POSSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add icon path here if you have one
)

# Collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='POSSystem',
    debug=False,
    bootloader_ignore_signals=False,
    console=False,  # Windows GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
