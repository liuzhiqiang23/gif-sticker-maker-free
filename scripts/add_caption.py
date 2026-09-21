#!/usr/bin/env python3
"""
给表情包静图叠加字幕 — 黑字白边，底部居中（CogView 免费档画不稳中文字幕，
统一由本脚本事后叠加，锐利且可控）。

Usage:
  python add_caption.py sticker_hi.png "嗨~"
  python add_caption.py a.png "嗨~" b.png "哈哈哈"   # 成对出现，批量处理
依赖: Pillow（Windows 中文字体用微软雅黑，自动探测）
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",   # 微软雅黑 Bold (中文)
    r"C:\Windows\Fonts\msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(px: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, px)
            except OSError:
                continue
    return ImageFont.load_default()


def caption_image(path: str, text: str, pad_ratio: float = 0.04):
    if path.lower().endswith(".gif"):
        return caption_gif(path, text, pad_ratio)
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    font = load_font(int(w * 0.11))
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=int(w * 0.016))
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) // 2 - bbox[0]
    y = h - th - int(h * pad_ratio) - bbox[1]
    d.text((x, y), text, font=font, fill="black",
           stroke_width=int(w * 0.016), stroke_fill="white")
    img.convert("RGB").save(path)
    print(f"OK: '{text}' -> {path}")


def caption_gif(path: str, text: str, pad_ratio: float = 0.04):
    """逐帧给 GIF 叠字幕（动画后再叠字的标准流程，避免视频模型画崩文字）。"""
    g = Image.open(path)
    durs, frames = [], []
    for i in range(g.n_frames):
        g.seek(i)
        durs.append(g.info.get("duration", 125))
        frames.append(g.convert("RGB"))
    W, H = frames[0].size
    font = load_font(int(W * 0.16))
    out = []
    for fr in frames:
        d = ImageDraw.Draw(fr)
        sw = max(3, int(W * 0.02))
        bb = d.textbbox((0, 0), text, font=font, stroke_width=sw)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        y = H - (bb[3] - bb[1]) - int(H * 0.03) - bb[1]
        d.text((x, y), text, font=font, fill="black", stroke_width=sw, stroke_fill="white")
        out.append(fr.quantize(colors=128, method=Image.MEDIANCUT))
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs[:len(out)], loop=0, optimize=True)
    print(f"OK: '{text}' on {len(out)} gif frames -> {path}")


def main():
    p = argparse.ArgumentParser(description="Overlay caption (black text, white outline)")
    p.add_argument("pairs", nargs="+", help="image path and caption text, in pairs")
    p.add_argument("--font-px", type=int, default=None, help="Font size px (default: 11%% of width)")
    args = p.parse_args()
    if len(args.pairs) % 2:
        raise SystemExit("ERROR: arguments must be image/caption pairs")
    for i in range(0, len(args.pairs), 2):
        caption_image(args.pairs[i], args.pairs[i + 1])


if __name__ == "__main__":
    main()
