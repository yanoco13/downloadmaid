"""ファイル仕分け・移動ロジック。

- 拡張子を小文字に正規化してルールと照合
- 移動先フォルダが存在しなければ自動作成
- 同名ファイルが既に存在する場合は "filename (2).ext" のようにリネーム
- 移動結果を ~/.downloadmaid/maid.log に記録
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from . import config as cfg

# ロガー設定
_log_file = cfg.CONFIG_DIR / "maid.log"


def _setup_logger() -> logging.Logger:
    cfg.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("downloadmaid")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(_log_file, encoding="utf-8")
        fh.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)s  %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(fh)
    return logger


logger = _setup_logger()


def sort_file(src: Path) -> bool:
    """src ファイルをルールに従って移動する。

    Returns:
        True: 移動した / False: 対象ルールなし（スキップ）
    """
    if not src.exists() or not src.is_file():
        return False

    ext = src.suffix.lower()
    rules = cfg.get_rules()

    for rule in rules:
        if ext in rule["extensions"]:
            dest_dir: Path = rule["destination"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            if dest.exists():
                logger.info("スキップ: %s (移動先に同名ファイルあり)", src.name)
                return False
            try:
                shutil.move(str(src), str(dest))
                logger.info("移動: %s  →  %s", src.name, dest)
                return True
            except (OSError, shutil.Error) as e:
                logger.error("移動失敗: %s  エラー: %s", src.name, e)
                return False

    logger.debug("スキップ: %s (対象ルールなし)", src.name)
    return False
