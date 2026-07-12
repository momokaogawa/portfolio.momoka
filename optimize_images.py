"""
images フォルダの中身を軽量化するスクリプト。

これが必要な理由:
  現在の images フォルダには 1枚あたり1〜6MB、合計25MB超の画像が入っていて、
  これが「サイトが重くて画像や文章が出てこない」原因になっています。
  スマホ回線だとこれを毎回全部読み込むのに数十秒〜かかることもあります。

使い方:
  1. このファイルを、リポジトリのルート（index.html がある場所）に置く
  2. ターミナルで以下を実行して Pillow をインストール
       pip install Pillow
  3. 実行
       python optimize_images.py
  4. images フォルダの画像が上書きされ、サイズが大幅に小さくなります
     (元のファイルは images/_original というフォルダに退避されるので、
      仕上がりが気に入らなければ戻せます)
  5. git add -A && git commit -m "画像を軽量化" && git push
"""

import os
import shutil
from pathlib import Path

from PIL import Image

IMAGES_DIR = Path(__file__).parent / "images"
BACKUP_DIR = IMAGES_DIR / "_original"

# ファイル名: (最大幅px, JPEG品質)
# hero/home/invent/max/study のような大きな背景画像は少し大きめに、
# それ以外(サムネイル的に使われるもの)は少し小さめに設定しています。
SETTINGS = {
    "hero.jpg": (1920, 78),
    "home.jpg": (1600, 78),
    "invent.jpg": (1600, 78),
    "about.jpg": (1200, 78),
    "leadership.jpeg": (1200, 78),
    "craft.jpg": (1200, 78),
    "max.jpg": (1400, 78),
    "study.jpg": (1400, 78),
    "kyuyo.jpg": (1400, 78),
    "summit.png": (1400, 78),  # PNGのまま縮小・再圧縮します
}


def optimize():
    if not IMAGES_DIR.exists():
        print(f"images フォルダが見つかりません: {IMAGES_DIR}")
        return

    BACKUP_DIR.mkdir(exist_ok=True)

    total_before = 0
    total_after = 0

    for filename, (max_width, quality) in SETTINGS.items():
        src = IMAGES_DIR / filename
        if not src.exists():
            print(f"スキップ（見つかりません）: {filename}")
            continue

        before_size = src.stat().st_size
        total_before += before_size

        # 元ファイルをバックアップ（初回のみ）
        backup_path = BACKUP_DIR / filename
        if not backup_path.exists():
            shutil.copy2(src, backup_path)

        img = Image.open(backup_path).convert("RGB")

        # 最大幅を超えていたら縮小（アスペクト比は維持）
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        out_path = src
        if filename.lower().endswith(".png"):
            # PNGは透過を保ったまま縮小・再圧縮
            img_png = Image.open(backup_path)
            if img_png.width > max_width:
                ratio = max_width / img_png.width
                new_size = (max_width, int(img_png.height * ratio))
                img_png = img_png.resize(new_size, Image.LANCZOS)
            img_png.save(out_path, "PNG", optimize=True)
        else:
            img.save(out_path, "JPEG", quality=quality, optimize=True, progressive=True)

        after_size = out_path.stat().st_size
        total_after += after_size

        print(
            f"{filename}: {before_size/1024/1024:.2f}MB -> {after_size/1024/1024:.2f}MB"
        )

    print("-" * 40)
    print(
        f"合計: {total_before/1024/1024:.2f}MB -> {total_after/1024/1024:.2f}MB "
        f"({(1 - total_after/total_before)*100:.0f}% 削減)"
    )


if __name__ == "__main__":
    optimize()
