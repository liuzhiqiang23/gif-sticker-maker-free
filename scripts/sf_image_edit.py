#!/usr/bin/env python3
"""
硅基流动 Qwen-Image-Edit 指令式图编辑 — 表情包流水线的"形象保真"首选。
和纯文生图（cogview）不同，编辑模型看得到原图：三角帽、五官、服装都能保住。

Usage:
  python sf_image_edit.py -i photo.jpg -o sticker_hi.png "变成 Funko Pop 手办，保持五官服装不变，右手挥手打招呼"
  python sf_image_edit.py -i photo.jpg -o out.png "..." --size 1024x1024

Env: SILICONFLOW_API_KEY (required)  — https://cloud.siliconflow.cn
计费：按张计费（约 ¥0.2-0.4/张，比免费档强一个档次）；端点 /v1/images/generations。
输出尺寸跟随请求 image_size，模型可能就近取整（如 1392x744），构图交给指令描述。
"""

import os
import sys
import base64
import argparse
import requests

API_BASE = "https://api.siliconflow.cn/v1/images/generations"


def api_key():
    key = os.getenv("SILICONFLOW_API_KEY")
    if not key:
        raise SystemExit("ERROR: SILICONFLOW_API_KEY is not set.\n  export SILICONFLOW_API_KEY='sk-...'")
    return key


def image_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"


def main():
    p = argparse.ArgumentParser(description="Qwen-Image-Edit via SiliconFlow (identity-preserving edit)")
    p.add_argument("prompt", help="Edit instruction (中文即可)")
    p.add_argument("-i", "--image", required=True, help="Source photo")
    p.add_argument("-o", "--output", required=True, help="Output PNG path")
    p.add_argument("--model", default="Qwen/Qwen-Image-Edit")
    p.add_argument("--size", default="1024x1024", help="Requested image_size")
    args = p.parse_args()

    r = requests.post(
        API_BASE,
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        json={"model": args.model, "prompt": args.prompt,
              "image": image_to_data_uri(args.image), "image_size": args.size},
        timeout=240,
    )
    if r.status_code != 200:
        raise SystemExit(f"ERROR {r.status_code}: {r.text[:300]}")
    j = r.json()
    items = j.get("images") or j.get("data") or []
    if not items or not items[0].get("url"):
        raise SystemExit(f"ERROR: unexpected response: {str(j)[:300]}")
    img = requests.get(items[0]["url"], timeout=120)
    img.raise_for_status()
    with open(args.output, "wb") as f:
        f.write(img.content)
    print(f"OK: {len(img.content):,} bytes -> {args.output}")


if __name__ == "__main__":
    main()
