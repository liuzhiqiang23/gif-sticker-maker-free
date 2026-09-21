#!/usr/bin/env python3
"""
CogView 文生图 — 智谱 bigmodel 免费端点 (cogview-3-flash)。

Usage:
  python cogview_image.py "A cat in space" -o cat.png
  python cogview_image.py "Funko Pop figurine waving" -o sticker.png --size 1024x1024

Env: BIGMODEL_API_KEY (required)  — https://open.bigmodel.cn
免费模型 cogview-3-flash；如需更高质量可 --model cogview-4 (付费)。
"""

import os
import sys
import argparse
import requests

API_BASE = "https://open.bigmodel.cn/api/paas/v4/images/generations"


def api_key():
    key = os.getenv("BIGMODEL_API_KEY") or os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise SystemExit("ERROR: BIGMODEL_API_KEY is not set.\n  export BIGMODEL_API_KEY='your-key'")
    return key


def generate_image(prompt: str, model: str = "cogview-3-flash", size: str = "1024x1024") -> str:
    """Generate one image, return its URL."""
    r = requests.post(
        API_BASE,
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        json={"model": model, "prompt": prompt, "size": size, "watermark": False},
        timeout=120,
    )
    if r.status_code != 200:
        raise SystemExit(f"ERROR {r.status_code}: {r.text[:300]}")
    data = r.json().get("data") or []
    if not data or "url" not in data[0]:
        raise SystemExit(f"ERROR: unexpected response: {str(r.json())[:300]}")
    return data[0]["url"]


def main():
    p = argparse.ArgumentParser(description="CogView text-to-image (bigmodel free endpoint)")
    p.add_argument("prompt")
    p.add_argument("-o", "--output", required=True, help="Output PNG path")
    p.add_argument("--size", default="1024x1024", help="e.g. 1024x1024, 864x1152, 1152x864")
    p.add_argument("--model", default="cogview-3-flash", help="cogview-3-flash (free) / cogview-4 (paid)")
    args = p.parse_args()

    url = generate_image(args.prompt, args.model, args.size)
    img = requests.get(url, timeout=120)
    img.raise_for_status()
    with open(args.output, "wb") as f:
        f.write(img.content)
    print(f"OK: {len(img.content):,} bytes -> {args.output}")


if __name__ == "__main__":
    main()
