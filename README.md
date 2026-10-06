# gif-sticker-maker-free 🍋

**照片 → Funko Pop 动图表情包**，一条龙流水线：形象保真静态化 → 动画 → 去水印/去角标 → 字幕 → 压体积（微信表情 ≤1MB）。

改编自 [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) 的 `gif-sticker-maker`（MIT），把 MiniMax 付费图片/视频 API 全部替换为**智谱 bigmodel 免费档 + 硅基流动 Qwen-Image-Edit**，并补齐了实战中踩出来的全部坑（去章、字幕时序、限流、体积）。

## 安装

```bash
git clone https://github.com/liuzhiqiang23/gif-sticker-maker-free.git
cp -r gif-sticker-maker-free ~/.zcode/skills/gif-sticker-maker
```

兼容任何 SKILL.md 格式的 agent（ZCode / Claude Code / qwen / codex…）。

## 用法

对 agent 说：**"把这张照片做成表情包"**，附上照片即可。默认产出 4 张：打招呼（嗨~）/ 大笑（哈哈哈）/ 哭泣（呜呜呜）/ 比心（爱你哦），字幕语言自动跟随对话语言。

## 双引擎说明

| 步骤 | 首选（形象保真） | 免费兜底 |
|---|---|---|
| 静图生成 | `sf_image_edit.py` — 硅基流动 Qwen-Image-Edit（**看得到原图**，帽子/五官/服装全保留，约 ¥0.2-0.4/张） | `cogview_image.py` — 智谱 cogview-3-flash（免费，纯文生图，形象会漂移） |
| 动画 | `cogvideox_video.py` — 智谱 cogvideox-flash（免费档，图生视频） | 同左 |

### 照片隐私

使用 `sf_image_edit.py` 时，源图片会发送给硅基流动的图像生成服务处理。请勿上传身份证件、医疗资料、未成年人照片或其他敏感图片；上传前请自行确认服务商的数据处理与留存条款。本项目不会替服务商承诺图片的保存期限或使用方式。

- `BIGMODEL_API_KEY`：动画必需（免费档）；key 在 https://open.bigmodel.cn
- `SILICONFLOW_API_KEY`：形象保真必需（按张计费）；key 在 https://cloud.siliconflow.cn

## 时序铁律（踩坑结晶，勿改）

```
无字静图 → 动画 → GIF（去角标+压体积） → 最后逐帧叠字幕
```

视频模型（cogvideox-flash）会把输入图上的文字重画成乱码，**提示词救不了**；
字幕必须等 GIF 转完后用 `add_caption.py xxx.gif "字幕"` 逐帧叠加（已内置 GIF 支持）。

其他内置能力：
- `remove_corner_stamp.py` — cogview/cogvideox 免费档强制盖"AI生成"角标（`watermark:false` 无效），逐行背景渐变擦除，无接缝
- `mp4_to_gif.py` — 帧率采样防慢动作、逐帧去角标、微信表情口诀 `--fps 8 --width 240 --trim 0.75 --colors 128`（28 帧 270-500KB）
- 免费档限流 1302：并发 ≤2、提交间隔 ≥16 秒

## 效果

输入一张 630px 的表情包原图，产出 4 张 240×240 同角色 GIF（挥手/大笑/流泪/比心），形象全程锁定，单张 270-500KB。

## License

MIT（见 [LICENSE](./LICENSE)）：原版 © MiniMax-AI，免费版改编 © liuzhiqiang23。
本仓库只含代码与文字；生成的画作属于使用者，不随仓库分发。
