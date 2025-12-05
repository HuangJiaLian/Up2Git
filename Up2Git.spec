# -*- mode: python ; coding: utf-8 -*-
# Up2Git PyInstaller Spec File

import os

block_cipher = None

# Get the project root
project_root = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['up2git_unified.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('icons/*.svg', 'icons'),
        ('icons/*.png', 'icons'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'plyer.platforms.linux.notification',
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
    name='Up2Git',
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
    icon=None,
)
