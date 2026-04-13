@echo off
REM Windows 用 PyInstaller ビルドスクリプト
REM 使い方: build_win.bat

echo === DownloadMaid Windows ビルド ===

REM 依存ライブラリをインストール
pip install -r requirements.txt

REM アイコン生成
python gen_icons.py

REM ビルド
pyinstaller ^
  --onefile ^
  --windowed ^
  --name DownloadMaid ^
  --icon assets\icon.ico ^
  --add-data "config.yaml;." ^
  src\main.py

echo.
echo 完了: dist\DownloadMaid.exe に実行ファイルが生成されました
echo 起動: dist\DownloadMaid.exe
pause
