# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
         ('api_utils/api_keys.toml', 'api_utils'),
         ('api_utils/aws_cert.pem', 'api_utils'),
         ('api_utils/aws_keys.json', 'api_utils'),
         ('configs/*','configs'),
         ('cycle_tests/*', 'cycle_tests'),
         ('gwctl_config_files/*', 'gwctl_config_files'),
         ('./api.json', '.'),
         ('gwctl-1.1.0.exe', '.'),
         ('test_data/*', 'test_data')
         ]

a = Analysis(
    ['hcycle.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
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
    name='hcycle',
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
)
