---
name: ai-explainer-video
display_name: 数字人讲解短视频生成（背景+配音+角色合成）
display_name_en: AI Character Explainer Video Generator
description: 把一段台词做成"数字人/角色讲解"横屏短视频的完整流水线——生成式工具只出纯场景背景与角色透明素材，配音用 edge-tts，后期用 ffmpeg 把背景循环、角色透明素材叠加、配音合成为 webm 再转 mp4。当用户要做"小智讲XX""数字人讲解视频""把台词做成视频""角色出镜科普短片"时使用。含 gen_audio/synth_case/transcode_mp4/validate_case 四个可复用脚本与 ffmpeg 实测踩坑。
description_zh: 数字人/角色讲解类横屏短视频生成流水线，含可复用脚本与 ffmpeg 实测踩坑，脱敏通用。
description_en: Full pipeline to produce a digital-character narrated horizontal short video (AI background + TTS + ffmpeg compositing to webm/mp4), with reusable scripts and verified ffmpeg pitfalls.
agent_created: true
author: 微教瑞
version: 1.0.0
---

# 数字人讲解短视频生成

把一段台词做成"数字人/角色讲解"横屏短视频。适用于微课里的**角色独讲**、**教师+角色双师同台**、
科普/知识类角色出镜短片。本技能是 `ai-teacher-video`（7 步大流水线）的**聚焦 companion**：
专攻"单角色讲解短视频"这一最常见场景，脚本自包含、可一键跑通。

## 四条铁律（违反必返工）

1. **生成式工具只出"纯场景背景"和"角色透明素材"，绝不把含角色整帧丢给图生视频。**
   实测：含角色的整帧交给图生视频，角色会被画歪（眼睛半睁、天线消失）。品牌形象必须可控。
2. **生成式场景图里绝不出现文字。** 提示词写 `absolutely no text no letters no numbers no words no watermark`，
   所有文字（标题/字幕）后期用 `drawtext`（见 ffmpeg 坑 2）或视频剪辑软件精确叠加。
3. **每段背景用 5 秒短片 + `-stream_loop -1` 循环**适配配音时长，而非逐段足量生成。成本差数倍。
4. **成品必须逐项程序化验收**（水印残留、角色叠加、总时长），本模型无预览环境无法看图。

## 标准 4 步流程

| 步 | 动作 | 工具 / 脚本 |
|---|---|---|
| 0 | 写台词表 `script.json`（每段 key/text/bg 文件名） | 人工 / `references/sample_script.json` |
| 1 | 为每镜生成**纯场景背景视频**（无人物、无文字、主体偏左、右侧 1/3 留空给角色） | `VideoGen` resolution=1080P |
| 1b | 准备**角色透明素材**（品牌原版 PNG/GIF，透明通道） | 人工 / `ImageGen` 仅生成场景 |
| 2 | 生成配音（edge-tts，默认 `zh-CN-YunxiaNeural`，+5%）并探测时长 → `scenes.json` | `scripts/gen_audio.py` |
| 3 | 合成每段：背景循环 + 去水印 + 角色 overlay + 配音 → webm；concat 拼成片 | `scripts/synth_case.py` |
| 4 | 最终 webm → mp4(H.264+AAC) 纯转码 + 验收 | `scripts/transcode_mp4.py` / `validate_case.py` |

## 关键实现细节

### 目录与工作区
- 所有脚本用 `imageio_ffmpeg.get_ffmpeg_exe()` 取 ffmpeg，不硬编码路径；用 `os.path.dirname(__file__)` 定位技能目录，可移植。
- 工作目录默认 `<技能目录>/work`，可用环境变量 `EXPLAINER_WORKDIR` 覆盖。
- 角色透明素材默认 `<技能目录>/assets/character.gif`，用 `CHAR_GIF` 覆盖；叠加坐标 `CHAR_X`/`CHAR_Y`（默认 1340/460，画布 1920×1080）。
- 背景视频放在 `<WORK>/bg_videos/` 下，`script.json` 的 `bg` 填文件名即可。

### edge-tts 配音
- 默认音色 `zh-CN-YunxiaNeural`（清亮女声，适合数字人），语速 `+5%`；可用 `EXPLAINER_VOICE` / `EXPLAINER_RATE` 覆盖。
- 生成后**必须实测探测每段时长**（不同音色/语速时长不同），写入 `scenes.json` 供合成对齐。

### ffmpeg 合成（Windows / imageio_ffmpeg）
全部坑见 `references/ffmpeg_pitfalls.md`，核心三点：
- **用内联 `-filter_complex`**，不要 `-filter_complex_script`（本环境不支持）。
- **复杂滤镜链下用 `libvpx-vp9`(webm) + `libvorbis`**；纯转码(webm→mp4)时 `libx264` 可用。
- 中文/引号字幕用 `textfile=` 读取；Windows 路径冒号转义 `\:`。

### VideoGen 输出规格与去水印
- 输出约 1924×1076（近 16:9，非精确 1920×1080），24fps，约 5.04s。合成前先 `scale=1920:1080`。
- 水印固定在右下角 → `delogo=x=1680:y=1012:w=234:h=60`。
- 任务数有上限，超限报 `RequestLimitExceeded.JobNumExceed`，隔几分钟重试。

## 验收清单
- [ ] 总时长 ≈ 各段配音时长之和
- [ ] 水印区白像素残留 < 1%
- [ ] 角色中心像素为角色色（证明已叠加，非黑/背景色）
- [ ] 角色形象与品牌原版一致（未被 AI 改动）
- [ ] 配音与画面时长对齐，无截断

## 与其他技能的关系
- `ai-teacher-video`：更完整的 7 步大流水线（含角色动效序列、面部程序化动画、录屏成片），本技能是其聚焦子集。
- `video-to-transcript`：视频 → 逐字稿（反向流程），常用于把已录制的讲解视频转成文字稿。
