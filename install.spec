# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['install.py'],
    pathex=['C:\\\\xampp\\\\htdocs\\\\livepy\\\\pythoncoin\\\\dist\\\\livepy\\\\pythoncoin'],
    binaries=[],
    datas=[
        ('adnetwrk(1).sql', '.'),
        ('api.php', '.'),
        ('auth.php', '.'),
        ('BLOCKCHAIN_AUDIT_TAB.md', '.'),
        ('BLOCKCHAIN_CONSENSUS_SYSTEM.md', '.'),
        ('blockchain.json', '.'),
        ('config.php', '.'),
        ('create_blockchain_tables.sql', '.'),
        ('dashboard8.php', '.'),
        ('MINING_SYSTEM.md', '.'),
        ('pyqt.py', '.'),
        ('pythoncoin.py', '.'),
        ('requirements.txt', '.'),
        ('wallet.json', '.'),
        ('ads_storage', 'ads_storage'),
        ('livepy.zip', '.') # Application ZIP file
    ],
    hiddenimports=['requests'], # requests is used for downloading Python installer
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='install',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # This should be a console application to show installation progress
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
