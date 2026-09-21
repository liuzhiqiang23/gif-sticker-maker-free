---
name: gif-sticker-maker
description: |
  Convert photos (people, pets, objects, logos) into 4 animated GIF stickers with captions.
  Use when: user wants to create cartoon stickers, GIF expressions, emoji packs, animated avatars,
  or convert photos to Funko Pop / Pop Mart blind box style animations.
  Triggers: sticker, GIF, cartoon, emoji, expression pack, avatar animation.
license: MIT
metadata:
  version: "2.0-free"
  category: creative-tools
  style: Funko Pop / Pop Mart
  output_format: GIF
  output_count: 4
  api: 智谱 bigmodel (CogView-3-Flash 图片免费 / CogVideoX-Flash 视频免费)
  derived_from: MiniMax-AI/skills gif-sticker-maker v1.2 (MIT)
---

# GIF Sticker Maker (免费版)

Convert user photos into 4 animated GIF stickers (Funko Pop / Pop Mart style).
Free edition: all AI calls go to 智谱 bigmodel free endpoints (CogView-3-Flash / CogVideoX-Flash).

## Style Spec

- Funko Pop / Pop Mart blind box 3D figurine
- C4D / Octane rendering quality
- White background, soft studio lighting
- Caption: black text + white outline, bottom of image

## Prerequisites

Before starting any generation step, ensure:

1. **Python deps**: `pip install requests imageio imageio-ffmpeg` (imageio-ffmpeg bundles ffmpeg; no system install)
2. **`BIGMODEL_API_KEY`** is exported (e.g. `export BIGMODEL_API_KEY='your-key'`, get one at https://open.bigmodel.cn — both image and video calls are free tiers)
3. Nothing else — no system ffmpeg needed

If any prerequisite is missing, set it up first. Do NOT proceed to generation without them.

## Workflow

### Step 0: Collect Captions

Ask user (in their language):
> "Would you like to customize the captions for your stickers, or use the defaults?"

- **Custom**: Collect 4 short captions (1–3 words). Actions auto-match caption meaning.
- **Default**: Look up [captions table](references/captions.md) by **detected user language**. **Never mix languages.**

### Step 1: Generate 4 Static Sticker Images

**Path A — 形象保真（推荐，需 `SILICONFLOW_API_KEY`）**：`scripts/sf_image_edit.py`
用 Qwen-Image-Edit 做**指令式编辑**——模型看得到原图，三角帽/五官/服装全部保留，只会做风格化。
纯文生图（Path B）只靠文字想象，形象会明显漂移；用户在意"像不像本人"时必须走 Path A。

1. Identify subject type (person / animal / object / logo).
2. For each of the 4 stickers, build an edit instruction: 保持原图身份特征不变 + Funko Pop 风格化 + 对应动作（挥手/大笑/流泪/比心）+ 正面全身 + 纯白背景。
3. Run (rate-limit friendly: 2 并发以内):

```bash
python3 scripts/sf_image_edit.py -i <source_photo> -o output/sticker_hi.png "变成 Funko Pop 风格乙烯基手办，严格保持角色特征不变，右手举起挥手打招呼，正面全身站姿，C4D 渲染，纯白背景"
```

4. 输出可能是横构图（如 1392x744）→ 居中裁方图后再叠字幕。
5. 计费按张（约 ¥0.2-0.4）；无强制水印。

**Path B — 纯免费兜底（仅 `BIGMODEL_API_KEY`）**：`scripts/cogview_image.py`（cogview-3-flash，免费）
注意 cogview 看不到原图，只有文字描述可用；人脸/角色细节必然漂移，需在提示词里写全特征。

```bash
python3 scripts/cogview_image.py "<prompt>" -o output/sticker_hi.png --size 864x1152
```

**Path B 免费档 gotchas（verified 2026-09）:**
- The endpoint stamps a "AI生成" badge at the bottom-right even with `watermark: false` sent.
  Remove it with `scripts/remove_corner_stamp.py <images...>` (per-row background extend, no seams).
- CogView cannot render captions reliably (often garbles or skips text). Do NOT ask the model for
  captions. Generate clean art, then overlay text with `scripts/add_caption.py <img> "<caption>" ...`
  (black text, thick white outline, bottom center; uses Microsoft YaHei on Windows).
  Path A 的 Qwen-Edit 输出无水印、也不需要叠字（后续动画后按需叠）。

### ⚠️ 时序铁律：先动画，后叠字（verified 2026-09）
cogvideox-flash 会把输入图上的字幕重画成乱码（中英文皆崩，提示词救不了）。
**送进 Step 2 动画的静图必须无字**；字幕在 Step 3 转完 GIF 后用
`scripts/add_caption.py xxx.gif "字幕"` 逐帧叠加（已支持 GIF）。
若静图已带字：底部字幕区可用逐行左右渐变填充抹掉后重动画。

### Step 1.5: De-stamp + Caption（仅 Path B 需要；Path A 跳过去章）

```bash
python3 scripts/remove_corner_stamp.py output/sticker_hi.png output/sticker_laugh.png output/sticker_cry.png output/sticker_love.png
python3 scripts/add_caption.py output/sticker_hi.png "嗨~" output/sticker_laugh.png "哈哈哈" output/sticker_cry.png "呜呜呜" output/sticker_love.png "爱你哦"
```

Captions MUST match the user's language column in [captions.md](references/captions.md).
Then eyeball every sticker before animating (identity, action, caption placement).

### Step 2: Animate Each Image → Video

**Tool**: `scripts/cogvideox_video.py` (cogvideox-flash, free tier; each video takes ~1–5 min async)

For each sticker image, build a prompt from [video-prompt-template.txt](assets/video-prompt-template.txt), then:

```bash
python3 scripts/cogvideox_video.py "<motion prompt>" --image output/sticker_hi.png -o output/sticker_hi.mp4
python3 scripts/cogvideox_video.py "<motion prompt>" --image output/sticker_laugh.png -o output/sticker_laugh.mp4
python3 scripts/cogvideox_video.py "<motion prompt>" --image output/sticker_cry.png -o output/sticker_cry.mp4
python3 scripts/cogvideox_video.py "<motion prompt>" --image output/sticker_love.png -o output/sticker_love.mp4
```

All 4 calls are independent — but submit **at most 2 concurrently** (free tier limit, verified);
a 4-way burst gets HTTP 429 / code 1302. If rejected, wait and retry rather than switching models.
`--size` 要跟输入图配：方图用 `--size 1024x1024`，竖图默认 `1080x1920`。

### Step 3: Convert Videos → GIF

**Tool**: `scripts/mp4_to_gif.py` (imageio, local, no API)

```bash
python3 scripts/mp4_to_gif.py output/sticker_hi.mp4 output/sticker_laugh.mp4 output/sticker_cry.mp4 output/sticker_love.mp4
```

Outputs GIF files alongside each MP4. WeChat sticker recipe (≤1MB verified):
`--fps 8 --width 240 --trim 0.75 --colors 128` → 28 帧 300-500KB。
内置逐帧 AI 角标清理（cogvideox 也会盖章）与帧率采样（防慢动作）。

### Step 3.5: Caption the GIFs（时序铁律的最后一步）

```bash
python3 scripts/add_caption.py output/sticker_hi.gif "嗨~" output/sticker_laugh.gif "哈哈哈" output/sticker_cry.gif "呜呜呜" output/sticker_love.gif "爱你哦"
```

### Step 4: Deliver

Output format (strict order):
1. Brief status line (e.g. "4 stickers created:")
2. `<deliver_assets>` block with all GIF files
3. **NO text after deliver_assets**

```xml
<deliver_assets>
<item><path>output/sticker_hi.gif</path></item>
<item><path>output/sticker_laugh.gif</path></item>
<item><path>output/sticker_cry.gif</path></item>
<item><path>output/sticker_love.gif</path></item>
</deliver_assets>
```

## Default Actions

| # | Action | Filename ID | Animation |
|---|--------|-------------|-----------|
| 1 | Happy waving | hi | Wave hand, slight head tilt |
| 2 | Laughing hard | laugh | Shake with laughter, eyes squint |
| 3 | Crying tears | cry | Tears stream, body trembles |
| 4 | Heart gesture | love | Heart hands, eyes sparkle |

See [references/captions.md](references/captions.md) for multilingual caption defaults.

## Rules

- Detect user's language, all outputs follow it
- Captions MUST come from [captions.md](references/captions.md) matching user's language column — never mix languages
- All image prompts must be in **English** regardless of user language (only caption text is localized)
- `<deliver_assets>` must be LAST in response, no text after
- NEVER print or store the API key; always read it from the environment
