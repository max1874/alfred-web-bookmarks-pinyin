from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # 使应用作为菜单栏应用运行
        'CFBundleName': "Bookmarks Sync",
        'CFBundleDisplayName': "Bookmarks Sync",
        'CFBundleIdentifier': "com.yourdomain.bookmarkssync",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
    },
    'packages': ['rumps', 'pypinyin', 'jieba', 'yaml'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 