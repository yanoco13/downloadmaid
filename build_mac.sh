#!/usr/bin/env bash
# macOS 用 PyInstaller ビルドスクリプト
# 使い方: bash build_mac.sh
set -euo pipefail

echo "=== DownloadMaid macOS ビルド ==="

# 仮想環境を作成・有効化
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# 依存ライブラリをインストール
pip install -r requirements.txt

# アイコン生成
python gen_icons.py

# ビルド（--onedir: macOS .app バンドルの推奨形式）
pyinstaller \
  --onedir \
  --windowed \
  --name DownloadMaid \
  --icon assets/icon.icns \
  --add-data "config.yaml:." \
  run_app.py

echo ""
echo "完了: dist/DownloadMaid.app が生成されました"
echo "起動: open dist/DownloadMaid.app"
echo "インストール: dist/DownloadMaid.app を /Applications にドラッグ"
