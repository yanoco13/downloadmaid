"""設定ファイルの読み書きモジュール。

設定は ~/.downloadmaid/config.yaml に保存される。
初回起動時はプロジェクト付属の config.yaml をコピーする。
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path.home() / ".downloadmaid"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def _default_config_path() -> Path:
    """バンドル済み or ソース実行時のデフォルト設定ファイルパスを返す。"""
    if getattr(sys, "frozen", False):
        # PyInstaller でバンドルされた場合
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).parent.parent
    return base / "config.yaml"


def ensure_config() -> None:
    """設定ディレクトリと設定ファイルが存在することを保証する。"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        default = _default_config_path()
        if default.exists():
            shutil.copy(default, CONFIG_FILE)
        else:
            # フォールバック: 最低限の設定を書き出す
            CONFIG_FILE.write_text(
                "watch_folder: ~/Downloads\nrules: {}\n",
                encoding="utf-8",
            )


def load() -> dict[str, Any]:
    """設定ファイルを読み込んで辞書として返す。"""
    ensure_config()
    with CONFIG_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def save(data: dict[str, Any]) -> None:
    """辞書を設定ファイルに書き込む。"""
    ensure_config()
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def get_watch_folder() -> Path:
    """監視フォルダのパスを返す。"""
    data = load()
    return Path(os.path.expanduser(data.get("watch_folder", "~/Downloads")))


def get_rules() -> list[dict[str, Any]]:
    """仕分けルールを [{extensions, destination}] のリストとして返す。"""
    data = load()
    rules_raw = data.get("rules") or {}
    rules = []
    for _name, rule in rules_raw.items():
        exts = [e.lower() for e in (rule.get("extensions") or [])]
        dest = os.path.expanduser(rule.get("destination", ""))
        if exts and dest:
            rules.append({"extensions": exts, "destination": Path(dest)})
    return rules


def open_config_in_editor() -> None:
    """OSのデフォルトエディタで設定ファイルを開く。"""
    import subprocess

    ensure_config()
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-t", str(CONFIG_FILE)])
    elif sys.platform == "win32":
        os.startfile(str(CONFIG_FILE))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(CONFIG_FILE)])


def open_log_in_editor() -> None:
    """OSのデフォルトアプリでログファイルを開く。"""
    import subprocess

    log_file = CONFIG_DIR / "maid.log"
    if not log_file.exists():
        log_file.write_text("", encoding="utf-8")

    if sys.platform == "darwin":
        subprocess.Popen(["open", "-t", str(log_file)])
    elif sys.platform == "win32":
        os.startfile(str(log_file))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(log_file)])
