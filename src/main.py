"""DownloadMaid エントリーポイント。

pystray でシステムトレイに常駐する。
メニューから監視の開始/一時停止・設定・ログ・自動起動を操作できる。
"""

from __future__ import annotations

import sys
import threading
from io import BytesIO

from PIL import Image, ImageDraw
import pystray

from . import autostart, config as cfg
from .watcher import Watcher

# ------------------------------------------------------------------ アイコン --

_ICON_SIZE = 64


def _make_icon(active: bool) -> Image.Image:
    """状態に応じたアイコン画像を生成する。
    active=True → 緑（監視中）
    active=False → 灰（停止/一時停止）
    """
    img = Image.new("RGBA", (_ICON_SIZE, _ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景の丸
    color = (52, 199, 89, 255) if active else (142, 142, 147, 255)
    draw.ellipse([4, 4, _ICON_SIZE - 4, _ICON_SIZE - 4], fill=color)

    # 矢印（↓）をシンプルな三角形で表現
    mid = _ICON_SIZE // 2
    draw.polygon(
        [(mid - 14, 18), (mid + 14, 18), (mid, 38)],
        fill=(255, 255, 255, 230),
    )
    draw.rectangle([mid - 5, 36, mid + 5, 48], fill=(255, 255, 255, 230))

    return img


# ------------------------------------------------------------------ トレイ ---

class TrayApp:
    def __init__(self) -> None:
        self._watcher = Watcher()
        self._icon: pystray.Icon | None = None

    # --- メニューアクション ---

    def _toggle_watch(self) -> None:
        if self._watcher.is_paused:
            self._watcher.resume()
        elif self._watcher.is_running:
            self._watcher.pause()
        else:
            self._watcher.start()
        self._refresh_menu()

    def _open_config(self) -> None:
        cfg.open_config_in_editor()

    def _open_log(self) -> None:
        cfg.open_log_in_editor()

    def _toggle_autostart(self) -> None:
        if autostart.is_enabled():
            autostart.disable()
        else:
            autostart.enable()
        self._refresh_menu()

    def _quit(self) -> None:
        self._watcher.stop()
        if self._icon:
            self._icon.stop()

    # --- メニュー再構築 ---

    def _build_menu(self) -> pystray.Menu:
        if self._watcher.is_paused:
            watch_label = "▶ 再開"
        elif self._watcher.is_running:
            watch_label = "⏸ 一時停止"
        else:
            watch_label = "▶ 監視を開始"

        autostart_label = (
            "✓ ログイン時に自動起動"
            if autostart.is_enabled()
            else "  ログイン時に自動起動"
        )

        return pystray.Menu(
            pystray.MenuItem(watch_label, self._toggle_watch),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙  設定ファイルを開く", self._open_config),
            pystray.MenuItem("📋 ログを開く", self._open_log),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(autostart_label, self._toggle_autostart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("終了", self._quit),
        )

    def _refresh_menu(self) -> None:
        if self._icon is None:
            return
        active = self._watcher.is_running
        self._icon.icon = _make_icon(active)
        self._icon.menu = self._build_menu()

    # --- 起動 ---

    def run(self) -> None:
        cfg.ensure_config()
        self._watcher.start()

        self._icon = pystray.Icon(
            name="DownloadMaid",
            icon=_make_icon(True),
            title="DownloadMaid",
            menu=self._build_menu(),
        )
        self._icon.run()


# ------------------------------------------------------------------ main ----

def main() -> None:
    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()
