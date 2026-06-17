# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('config', 'config'),
    ('data', 'data'),
    ('backups', 'backups'),
]

a = Analysis(
    ['main.py'],
    pathex=['f:\\pos_app', 'f:\\'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'sqlalchemy.ext.baked',
        'matplotlib.backends.backend_qtagg',
        'PySide6.QtPrintSupport',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
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
    name='SGS Final',
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
