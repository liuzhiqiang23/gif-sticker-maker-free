#!/usr/bin/env python3
"""
MP4 → GIF 批量转换 — 用 imageio（自带 ffmpeg，无需系统安装）。
内置：帧率采样（保持实时速度）、右下角"AI生成"角标逐行清理（cogvideox 免费档强制盖章）、
体积压缩（卡通平色关抖动）。

Usage:
  python mp4_to_gif.py sticker_hi.mp4 sticker_laugh.mp4
  python mp4_to_gif.py *.mp4 --fps 8 --width 240 --no-dither

依赖: pip install imageio imageio-ffmpeg numpy
"""

import os
import sys
import argparse
import numpy as np
import imageio.v3 as iio
from PIL import Image


def de_stamp_frame(frame: np.ndarray) -> np.ndarray:
    """清理一帧的右下角角标：逐行在角标左右采样色之间做横向渐变插值（保暗角渐变）。"""
    h, w = frame.shape[:2]
    x0, y0 = int(w * 0.72), int(h * 0.905)
    x1, y1 = int(w * 0.995), int(h * 0.998)
    left = frame[y0:y1, x0 - 40:x0 - 4].astype(np.float32)
    right = frame[y0:y1, x1:min(x1 + 6, w)].astype(np.float32)
    l_std = left.std(axis=(1, 2))
    l_mean = left.mean(axis=1)                                   # (rows, 3)
    r_mean = right.mean(axis=1) if right.shape[1] else l_mean
    t = np.linspace(0.0, 1.0, x1 - x0, dtype=np.float32)[None, :, None]  # (1, n, 1)
    for i in range(y1 - y0):
        if l_std[i] < 25:  # 左侧光滑（背景行）才清理
            fill = l_mean[i][None, :] * (1 - t[0]) + r_mean[i][None, :] * t[0]
            frame[y0 + i, x0:x1] = np.clip(fill, 0, 255).astype(frame.dtype)
    return frame


def mp4_to_gif(input_path: str, output_path: str, fps: int = 8, width: int = 240,
               dither: bool = False, de_stamp: bool = True, trim: float = 0.0,
               colors: int = 256) -> bool:
    if not os.path.isfile(input_path):
        print(f"SKIP: {input_path} not found", file=sys.stderr)
        return False
    try:
        meta = iio.immeta(input_path)
        src_fps = float(meta.get("fps") or fps)
        step = max(1, round(src_fps / fps))  # 采样保持实时速度，否则 GIF 变慢动作
        frames = []
        for i, frame in enumerate(iio.imiter(input_path)):
            if i % step:
                continue
            if de_stamp:
                frame = de_stamp_frame(frame)
            hh = round(frame.shape[0] * width / frame.shape[1])
            frames.append(Image.fromarray(frame).resize((width, hh), Image.LANCZOS))
        if not frames:
            print(f"FAIL: no frames in {input_path}", file=sys.stderr)
            return False
        if trim > 0 and len(frames) > 4:
            frames = frames[:max(4, int(len(frames) * trim))]
        duration_ms = round(1000 / fps)
        pal = frames[0].quantize(colors=colors, method=Image.MEDIANCUT)
        pal_frames = [f.quantize(palette=pal, dither=Image.FLOYDSTEINBERG if dither else Image.NONE)
                      for f in frames]
        pal_frames[0].save(output_path, save_all=True, append_images=pal_frames[1:],
                           duration=duration_ms, loop=0, optimize=True)
    except Exception as e:
        print(f"FAIL: {input_path} -> {e}", file=sys.stderr)
        return False
    size = os.path.getsize(output_path)
    print(f"OK: {len(frames)} frames, {size:,} bytes ({size/1024:.0f} KB) -> {output_path}")
    return True


def main():
    p = argparse.ArgumentParser(description="Batch MP4 -> GIF (sample fps, de-stamp, size-tuned)")
    p.add_argument("inputs", nargs="+", help="MP4 file(s)")
    p.add_argument("-o", "--output", default=None, help="Output path (single input only)")
    p.add_argument("--fps", type=int, default=8, help="GIF frame rate (default 8)")
    p.add_argument("--width", type=int, default=240, help="GIF width px (default 240)")
    p.add_argument("--dither", action="store_true", help="Enable Floyd-Steinberg dithering (bigger file)")
    p.add_argument("--no-de-stamp", action="store_true", help="Skip AI-stamp cleanup")
    p.add_argument("--trim", type=float, default=0.0, help="Keep only first N fraction of video (e.g. 0.75)")
    p.add_argument("--colors", type=int, default=256, help="Palette colors (default 256; 128 smaller)")
    args = p.parse_args()

    if args.output and len(args.inputs) > 1:
        raise SystemExit("ERROR: -o/--output only works with a single input file")

    ok = fail = 0
    for mp4 in args.inputs:
        gif_path = args.output or os.path.splitext(mp4)[0] + ".gif"
        if mp4_to_gif(mp4, gif_path, args.fps, args.width, args.dither, not args.no_de_stamp, args.trim, args.colors):
            ok += 1
        else:
            fail += 1
    print(f"\nDone: {ok} converted, {fail} failed")


if __name__ == "__main__":
    main()
