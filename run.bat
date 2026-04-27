@echo off
REM 開発用起動スクリプト（ビルドなしで直接実行）
REM 使い方: run.bat

setlocal EnableDelayedExpansion

cd /d "%~dp0"

REM Python 3.10+ を探す
set PYTHON=
for %%c in (python3.13 python3.12 python3.11 python3.10 python3 python) do (
    if not defined PYTHON (
        where %%c >nul 2>&1
        if not errorlevel 1 (
            %%c -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
            if not errorlevel 1 (
                set PYTHON=%%c
            )
        )
    )
)

if not defined PYTHON (
    echo エラー: Python 3.10 以上が見つかりません。
    echo.
    echo https://www.python.org/ からインストールしてください。
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('!PYTHON! --version') do echo 使用する Python: !PYTHON! ^(%%v^)

REM 仮想環境を作成・有効化
if not exist ".venv" (
    echo 仮想環境を作成中...
    !PYTHON! -m venv .venv
)
call .venv\Scripts\activate.bat

REM 依存ライブラリをインストール（未インストールの場合のみ）
pip install -q -r requirements.txt

REM 起動
python -m src.main
