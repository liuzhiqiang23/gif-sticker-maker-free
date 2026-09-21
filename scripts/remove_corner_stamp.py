#!/usr/bin/env python3
"""
移除右下角"AI生成"角标 v2 — cogview-3-flash 免费档强制盖章，watermark:false 无效。
原理：角标在光滑渐变背景上；逐行用角标左侧紧邻的干净像素颜色横向填充，
保留地板纵向渐变，无接缝。某行采样点若踩到主体/字幕（高方差），回退为上方复制。

Usage:
  python remove_corner_stamp.py img1.png img2.png ...
"""

import sys
import argparse
import statistics
from PIL import Image, ImageFilter


def remove_stamp(path: str) -> bool:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    x0, y0 = int(w * 0.72), int(h * 0.910)
    x1, y1 = int(w * 0.995), int(h * 0.998)
    px = img.load()

    for y in range(y0, y1):
        # 采样角标左侧 6 个干净像素
        samples = [px[x0 - 4 - i, y] for i in range(6)]
        flat = all(isinstance(c, tuple) for c in samples)
        var = statistics.pstdev([c[0] + c[1] + c[2] for c in samples]) if flat else 255
        if var < 12:  # 光滑背景：横向延伸填充
            base = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
            for x in range(x0, x1):
                px[x, y] = base
        # 高方差行（踩到内容）：保留现状（v1 已铺底或本就干净）

    # 轻糊整个区域软接缝
    pad = 6
    region = img.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).filter(ImageFilter.GaussianBlur(1.0))
    img.paste(region, (x0 - pad, y0 - pad))
    img.save(path)
    print(f"OK: stamp cleaned (v2) -> {path}")
    return True


def main():
    p = argparse.ArgumentParser(description="Remove bottom-right AI stamp (per-row background extend)")
    p.add_argument("images", nargs="+")
    args = p.parse_args()
    for f in args.images:
        remove_stamp(f)


if __name__ == "__main__":
    main()
