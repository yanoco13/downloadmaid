"""watchdog を使ったフォルダ監視モジュール。

ファイルが作成されたとき、書き込み完了を待ってから sorter に渡す。
start() / stop() / pause() / resume() で制御できる。
"""

import logging
import threading
import time
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileMovedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from . import config as cfg
from .sorter import sort_file

logger = logging.getLogger("downloadmaid")

# ファイルが書き込み中かどうかを確認するリトライ設定
_STABLE_RETRIES = 8
_STABLE_INTERVAL = 0.5  # 秒


def _wait_until_stable(path: Path, retries: int = _STABLE_RETRIES,
                        interval: float = _STABLE_INTERVAL) -> bool:
    """ファイルサイズが変化しなくなるまで待つ。

    Returns:
        True: 安定した（書き込み完了とみなせる）
        False: タイムアウト
    """
    prev_size = -1
    for _ in range(retries):
        try:
            current_size = path.stat().st_size
        except OSError:
            time.sleep(interval)
            continue
        if current_size == prev_size and current_size >= 0:
            return True
        prev_size = current_size
        time.sleep(interval)
    return False


class _Handler(FileSystemEventHandler):
    def __init__(self, paused_flag: threading.Event) -> None:
        super().__init__()
        self._paused = paused_flag

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        if self._paused.is_set():
            return

        path = Path(event.src_path)

        # 隠しファイル・一時ファイルは無視
        if path.name.startswith(".") or path.suffix.lower() in (".tmp", ".crdownload", ".part"):
            return

        # 別スレッドで書き込み完了を待ってから仕分け
        threading.Thread(target=self._handle, args=(path,), daemon=True).start()

    def on_moved(self, event: FileMovedEvent) -> None:  # type: ignore[override]
        # Windows ではブラウザが .crdownload → .jpg のようにリネームして完了する
        if event.is_directory:
            return
        if self._paused.is_set():
            return

        path = Path(event.dest_path)

        if path.name.startswith(".") or path.suffix.lower() in (".tmp", ".crdownload", ".part"):
            return

        threading.Thread(target=self._handle, args=(path,), daemon=True).start()

    def _handle(self, path: Path) -> None:
        if not _wait_until_stable(path):
            logger.warning("タイムアウト: %s (書き込み完了を確認できませんでした)", path.name)
            return
        if self._paused.is_set():
            return
        sort_file(path)


class Watcher:
    """フォルダ監視の開始・停止・一時停止を管理するクラス。"""

    def __init__(self) -> None:
        self._observer: Observer | None = None
        self._paused = threading.Event()  # set = 一時停止中
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running and not self._paused.is_set()

    @property
    def is_paused(self) -> bool:
        return self._running and self._paused.is_set()

    def start(self) -> None:
        """監視を開始する。すでに起動中の場合は何もしない。"""
        if self._running:
            return

        watch_folder = cfg.get_watch_folder()
        watch_folder.mkdir(parents=True, exist_ok=True)

        self._paused.clear()
        handler = _Handler(self._paused)
        self._observer = Observer()
        self._observer.schedule(handler, str(watch_folder), recursive=False)
        self._observer.start()
        self._running = True
        logger.info("監視開始: %s", watch_folder)

    def stop(self) -> None:
        """監視を停止する。"""
        if self._observer and self._running:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        self._running = False
        self._paused.clear()
        logger.info("監視停止")

    def pause(self) -> None:
        """仕分けを一時停止する（監視は継続するがファイルを移動しない）。"""
        self._paused.set()
        logger.info("一時停止")

    def resume(self) -> None:
        """一時停止から再開する。"""
        self._paused.clear()
        logger.info("再開")

    def restart(self) -> None:
        """設定変更後に監視フォルダを再読み込みして再起動する。"""
        self.stop()
        self.start()
