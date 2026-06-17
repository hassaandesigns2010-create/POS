# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Get current directory and parent directory
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)

a = Analysis(
    ['main.py'],
    pathex=[parent_dir],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('ui', 'ui'),
        ('Logo.png', '.'),
    ],
    hiddenimports=[
        'pos_app',
        'pos_app.controllers',
        'pos_app.views', 
        'pos_app.models',
        'pos_app.utils',
        'pos_app.database',
        'pos_app.widgets',
        'bcrypt',
        'reportlab',
        'reportlab.graphics.barcode',
        'reportlab.graphics.barcode.common',
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.qr',
        'psycopg2',
        'sqlalchemy',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'pytest',
        'unittest',
        'tkinter',
        'PyQt6',
        'matplotlib',
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
