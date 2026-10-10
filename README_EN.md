# gif-sticker-maker-free 🍋

**English | [中文](./README.md)**

**Turn a photo into animated Funko Pop-style stickers.** This end-to-end workflow preserves the subject, creates an animation, removes watermarks and corner stamps, adds captions, and compresses the result to WeChat sticker size (under 1 MB).

Adapted from MiniMax-AI/skills' **gif-sticker-maker** (MIT). This version replaces the paid MiniMax image and video APIs with Zhipu BigModel's free tier and SiliconFlow Qwen-Image-Edit, and adds practical fixes for stamps, caption timing, rate limits, and file size.

## Install

~~~bash
git clone https://github.com/liuzhiqiang23/gif-sticker-maker-free.git
cp -r gif-sticker-maker-free ~/.zcode/skills/gif-sticker-maker
~~~

Compatible with agents that support the SKILL.md format, including ZCode, Claude Code, Qwen, and Codex.

## Use

Tell your agent, “Turn this photo into a sticker,” and attach a photo. By default, it creates four stickers: a greeting, laughter, crying, and a heart gesture. Captions follow the language of the conversation.

## Two-engine workflow

| Step | Preferred option (preserves likeness) | Free fallback |
|---|---|---|
| Image generation | **sf_image_edit.py** — SiliconFlow Qwen-Image-Edit sees the source image and preserves details such as the hat, facial features, and clothes (about ¥0.2–0.4 per image). | **cogview_image.py** — Zhipu cogview-3-flash is free text-to-image, but the subject may drift. |
| Animation | **cogvideox_video.py** — Zhipu cogvideox-flash, free-tier image-to-video. | Same option. |

### Photo privacy

When you use sf_image_edit.py, the source photo is sent to SiliconFlow's image-generation service. Do not upload IDs, medical records, photos of minors, or other sensitive images. Review the provider's data-handling and retention terms before uploading. This project makes no claims about how long the provider stores images or how they may be used.

- **BIGMODEL_API_KEY** is required for animation on the free tier; get one at [open.bigmodel.cn](https://open.bigmodel.cn).
- **SILICONFLOW_API_KEY** is required for likeness-preserving edits, which are billed per image; get one at [cloud.siliconflow.cn](https://cloud.siliconflow.cn).

## Caption timing

~~~text
Text-free image → animation → GIF (remove corner marks and compress) → add captions frame by frame
~~~

The video model (cogvideox-flash) redraws text from input images as gibberish; prompts cannot reliably prevent this. Add captions only after GIF conversion with add_caption.py, which supports frame-by-frame GIF captions.

Other built-in tools:

- **remove_corner_stamp.py** removes the forced “AI-generated” corner mark from free CogView/CogVideoX outputs. The watermark:false parameter does not disable it; this script removes it with a row-wise background gradient.
- **mp4_to_gif.py** samples frames to avoid slow motion, removes corner marks frame by frame, and applies WeChat-friendly settings: --fps 8 --width 240 --trim 0.75 --colors 128. A 28-frame GIF is typically 270–500 KB.
- Free-tier rate limit 1302: keep concurrency at 2 or less and wait at least 16 seconds between submissions.

## Example output

Starting from a 630-pixel sticker image, the workflow creates four 240 × 240 GIFs with the same character (waving, laughing, crying, and making a heart). Each file is typically 270–500 KB.

## License

MIT (see [LICENSE](./LICENSE)). Original version © MiniMax-AI; free-tier adaptation © liuzhiqiang23.

This repository contains code and text only. Images generated with it belong to their users and are not distributed with the repository.
