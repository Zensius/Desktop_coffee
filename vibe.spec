# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['vibe.py'],
    pathex=[],
    binaries=[('D:\\anaconda\\DLLs\\_tkinter.pyd', '.'), ('D:\\anaconda\\Library\\bin\\tcl86t.dll', '.'), ('D:\\anaconda\\Library\\bin\\tk86t.dll', '.')],
    datas=[('gif', 'gif')],
    hiddenimports=[],
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
    name='vibe',
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
