# main.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['/main.py'],
             binaries=[],
             datas=[('D:\\matek\\Office\\Prog\\vízjelező\\watermark.png', '.'), 
                    ('D:\\matek\\Office\\Prog\\vízjelező\\logo.ico', '.'),
                    ('D:\\matek\\Office\\Prog\\vízjelező\\watermarker.ui', '.'),
                    ('D:\\matek\\Office\\Prog\\vízjelező\\AMArialRDBD.ttf', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Vízjelező',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='D:\\matek\\Office\\Prog\\vízjelező\\logowhite.ico' )