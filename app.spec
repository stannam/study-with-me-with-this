# -*- mode: python ; coding: utf-8 -*-
from os import getcwd, path
import sys

root_path = getcwd()
icon_path = path.join(root_path, 'icons', 'icon.ico')
if sys.platform == 'darwin':
    icon_path = path.join(root_path, 'icons', 'icon.icns')
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[(path.join(root_path, 'resource'), 'resource'),
           (path.join(root_path, 'log'), 'log')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,

)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Study with this',
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
    icon=icon_path
)

if sys.platform == 'darwin':
    app = BUNDLE(exe, name='Study with This.app', icon=icon_path)
