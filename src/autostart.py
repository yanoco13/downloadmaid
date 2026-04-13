"""OS起動時の自動起動設定モジュール。

- macOS: ~/Library/LaunchAgents/com.downloadmaid.plist
- Windows: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run レジストリ
"""

import sys
from pathlib import Path


# ------------------------------------------------------------------ macOS ---

_PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.downloadmaid.plist"
_PLIST_LABEL = "com.downloadmaid"


def _get_executable() -> str:
    """実行ファイル（バンドル済み or python スクリプト）のパスを返す。"""
    if getattr(sys, "frozen", False):
        return sys.executable
    # 開発時は `python src/main.py` 相当
    main_py = str(Path(__file__).parent / "main.py")
    return f"{sys.executable} {main_py}"


def _write_plist(exec_path: str) -> None:
    _PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if getattr(sys, "frozen", False):
        program_args = f"<string>{exec_path}</string>"
    else:
        parts = exec_path.split(" ", 1)
        program_args = (
            f"<string>{parts[0]}</string>\n"
            f"        <string>{parts[1]}</string>"
        )

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{_PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
        {program_args}
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
</dict>
</plist>
"""
    _PLIST_PATH.write_text(plist, encoding="utf-8")


# ----------------------------------------------------------------- Windows --

_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REG_VALUE = "DownloadMaid"


def _win_enable(exec_path: str) -> None:
    import winreg  # type: ignore[import]

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY,
                        0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, _REG_VALUE, 0, winreg.REG_SZ, exec_path)


def _win_disable() -> None:
    import winreg  # type: ignore[import]

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, _REG_VALUE)
    except FileNotFoundError:
        pass


def _win_is_enabled() -> bool:
    import winreg  # type: ignore[import]

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as key:
            winreg.QueryValueEx(key, _REG_VALUE)
        return True
    except FileNotFoundError:
        return False


# ------------------------------------------------------------------ Public --

def enable() -> None:
    """自動起動を有効にする。"""
    exec_path = _get_executable()
    if sys.platform == "darwin":
        _write_plist(exec_path)
    elif sys.platform == "win32":
        _win_enable(exec_path)


def disable() -> None:
    """自動起動を無効にする。"""
    if sys.platform == "darwin":
        _PLIST_PATH.unlink(missing_ok=True)
    elif sys.platform == "win32":
        _win_disable()


def is_enabled() -> bool:
    """自動起動が有効かどうかを返す。"""
    if sys.platform == "darwin":
        return _PLIST_PATH.exists()
    elif sys.platform == "win32":
        return _win_is_enabled()
    return False
