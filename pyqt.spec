# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pyqt.py'],
    pathex=[],
    binaries=[],
    datas=[('venv', 'venv'), ('assets', 'assets'), ('libmysql.dll', '.'), ('libcrypto-3-x64.dll', '.'), ('libssl-3-x64.dll', '.')],
    hiddenimports=['mysql.connector', 'mysql.connector.locales.eng'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pyqt',
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
