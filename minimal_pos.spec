# -*- mode: python ; coding: utf-8 -*-
"""
Minimal PyInstaller spec file for POS Application
"""
import os

# Analysis options
a = Analysis(
    scripts=['main.py'],
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
    ],
    excludes=[
        'pytest',
        'unittest',
        'test',
        'tests',
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
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
    console=False,
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
