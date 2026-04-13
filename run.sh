#!/usr/bin/env bash
# 開発用起動スクリプト（ビルドなしで直接実行）
# 使い方: bash run.sh
set -euo pipefail

cd "$(dirname "$0")"

# Python 3.10+ を探す（pyobjc が 3.10+ 必須）
find_python() {
  for cmd in python3.13 python3.12 python3.11 python3.10 \
             /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12 \
             /usr/local/bin/python3.12 /usr/local/bin/python3.13; do
    if command -v "$cmd" &>/dev/null; then
      ver=$("$cmd" -c 'import sys; print(sys.version_info[:2])' 2>/dev/null)
      # (3, 10) 以上かチェック
      if "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON=$(find_python || true)

if [ -z "$PYTHON" ]; then
  echo "エラー: Python 3.10 以上が見つかりません。"
  echo ""
  echo "Homebrew でインストールしてください:"
  echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo "  brew install python@3.12"
  exit 1
fi

echo "使用する Python: $PYTHON ($($PYTHON --version))"

# 仮想環境を作成・有効化
if [ ! -d ".venv" ]; then
  echo "仮想環境を作成中..."
  "$PYTHON" -m venv .venv
fi
source .venv/bin/activate

# 依存ライブラリをインストール（未インストールの場合のみ）
pip install -q -r requirements.txt

# 起動
python3 -m src.main
