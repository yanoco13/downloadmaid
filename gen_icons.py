#!/usr/bin/env python3
"""アイコンファイル生成スクリプト。

src/main.py の _make_icon() と同じデザインで
assets/icon.ico (Windows) と assets/icon.icns (macOS) を生成する。

使い方:
  python gen_icons.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).parent / "assets"


def make_icon(size: int) -> Image.Image:
    """指定サイズのアイコン画像を生成する（監視中=緑）。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 座標はすべて 64px 基準からスケール
    r = size / 64

    # 背景の丸（緑）
    pad = round(4 * r)
    draw.ellipse([pad, pad, size - pad, size - pad], fill=(52, 199, 89, 255))

    # 下向き矢印（三角形 + 棒）
    mid = size // 2
    draw.polygon(
        [
            (mid - round(14 * r), round(18 * r)),
            (mid + round(14 * r), round(18 * r)),
            (mid, round(38 * r)),
        ],
        fill=(255, 255, 255, 230),
    )
    draw.rectangle(
        [mid - round(5 * r), round(36 * r), mid + round(5 * r), round(48 * r)],
        fill=(255, 255, 255, 230),
    )

    return img


def gen_ico() -> Path:
    """assets/icon.ico を生成する（Windows 用）。"""
    sizes = [16, 32, 48, 64, 128, 256]
    images = [make_icon(s) for s in sizes]
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / "icon.ico"
    images[0].save(
        out,
        format="ICO",
        append_images=images[1:],
        sizes=[(s, s) for s in sizes],
    )
    print(f"生成: {out}")
    return out


def gen_icns() -> Path:
    """assets/icon.icns を生成する（macOS 用）。iconutil が必要。"""
    iconset = ASSETS / "icon.iconset"
    iconset.mkdir(parents=True, exist_ok=True)

    specs = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for filename, size in specs:
        make_icon(size).save(iconset / filename, format="PNG")

    out = ASSETS / "icon.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(out)],
        check=True,
    )
    shutil.rmtree(iconset)
    print(f"生成: {out}")
    return out


if __name__ == "__main__":
    if sys.platform == "darwin":
        gen_icns()
        gen_ico()
    else:
        gen_ico()
