#!/usr/bin/env python3
"""
CogVideoX 图生视频 — 智谱 bigmodel 免费档 (cogvideox-flash)，异步任务轮询。

Usage:
  python cogvideox_video.py "Figurine waves cheerfully" --image sticker.png -o sticker.mp4

Env: BIGMODEL_API_KEY (required)  — https://open.bigmodel.cn
cogvideox-flash 免费（有并发/频率限制）；cogvideox-3 为付费高清档。
输出约 5 秒。本脚本仅取视频、不含音频。
"""

import os
import sys
import time
import base64
import argparse
import requests

API_BASE = "https://open.bigmodel.cn/api/paas/v4"


def api_key():
    key = os.getenv("BIGMODEL_API_KEY") or os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise SystemExit("ERROR: BIGMODEL_API_KEY is not set.\n  export BIGMODEL_API_KEY='your-key'")
    return key


def image_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"


def submit(prompt: str, model: str, image_path: str, quality: str, size: str) -> str:
    body = {"model": model, "prompt": prompt, "quality": quality,
            "with_audio": False, "size": size, "fps": 30}
    if image_path:
        body["image_url"] = [image_to_data_uri(image_path)]
    r = requests.post(f"{API_BASE}/videos/generations",
                      headers={"Authorization": f"Bearer {api_key()}",
                               "Content-Type": "application/json"},
                      json=body, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"ERROR {r.status_code}: {r.text[:300]}")
    j = r.json()
    if j.get("task_status") not in ("PROCESSING", "SUCCESS") or "id" not in j:
        raise SystemExit(f"ERROR: unexpected submit response: {str(j)[:300]}")
    return j["id"]


def poll(task_id: str, timeout_min: int = 15) -> str:
    """Poll async task until SUCCESS; return video URL."""
    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:
        r = requests.get(f"{API_BASE}/async-result/{task_id}",
                         headers={"Authorization": f"Bearer {api_key()}"}, timeout=60)
        if r.status_code != 200:
            raise SystemExit(f"ERROR {r.status_code}: {r.text[:300]}")
        j = r.json()
        status = j.get("task_status")
        if status == "SUCCESS":
            for v in j.get("video_result") or []:
                if v.get("url"):
                    return v["url"]
            raise SystemExit(f"ERROR: SUCCESS but no video url: {str(j)[:300]}")
        if status == "FAIL":
            raise SystemExit(f"ERROR: task FAILED: {str(j)[:300]}")
        print(f"  [{time.strftime('%H:%M:%S')}] {status} ...", flush=True)
        time.sleep(10)
    raise SystemExit(f"ERROR: timed out after {timeout_min} min (task {task_id})")


def main():
    p = argparse.ArgumentParser(description="CogVideoX image-to-video (bigmodel, cogvideox-flash free)")
    p.add_argument("prompt", help="Motion description for the sticker")
    p.add_argument("--image", required=True, help="Input sticker PNG (image-to-video)")
    p.add_argument("-o", "--output", required=True, help="Output MP4 path")
    p.add_argument("--model", default="cogvideox-flash", help="cogvideox-flash (free) / cogvideox-3 (paid)")
    p.add_argument("--quality", default="quality", choices=["quality", "speed"])
    p.add_argument("--size", default="1080x1920", help="Output size; 1024x1024 for square input")
    p.add_argument("--wait", type=int, default=15, help="Poll timeout in minutes")
    args = p.parse_args()

    task_id = submit(args.prompt, args.model, args.image, args.quality, args.size)
    print(f"task: {task_id}")
    url = poll(task_id, args.wait)
    vid = requests.get(url, timeout=300)
    vid.raise_for_status()
    with open(args.output, "wb") as f:
        f.write(vid.content)
    print(f"OK: {len(vid.content):,} bytes -> {args.output}")


if __name__ == "__main__":
    main()
