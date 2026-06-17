# -*- mode: python ; coding: utf-8 -*-
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
    name='POSSystemFinal',
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
