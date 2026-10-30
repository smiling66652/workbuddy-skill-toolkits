---
name: local-video-pipeline
display_name: 本地视频合成流水线法
display_name_en: Local Video Pipeline
description: 纯 CPU 本地合成口播视频：文案txt → sherpa-onnx中文配音 → Pillow封面卡片 → 文案直出字幕 → ffmpeg合成1080p MP4，全程离线。触发词：做视频、口播视频、出片、视频合成、配音视频。
description_zh: 纯 CPU 本地视频合成流水线。输入分句文案，自动生成中文配音、封面与逐句要点卡片、精准字幕，ffmpeg 合成 1080p MP4。全程离线、不依赖 GPU、不依赖云 API，适合业务汇报口播与知识短视频。
description_en: Offline text-to-video pipeline on CPU. Turn line-by-line scripts into narrated 1080p MP4 with Chinese TTS (sherpa-onnx), auto cover & caption cards (Pillow), accurate subtitles and ffmpeg assembly. No GPU or cloud API required.
category: office
version: 1.0.1
author: 陈斌
---

# 技能｜本地视频合成流水线法

当用户需要把文字文案做成带配音、字幕的口播视频（且要求本地/离线/不用 GPU）时，按以下步骤执行：

## 〇、环境检查（首次使用必做）

1. 确认流水线根目录（含 `bin/ffmpeg.exe`、`models/`、`make_video.py`）。默认 `D:\LocalLLM\video`，可用环境变量 `VIDEO_PIPELINE_HOME` 覆盖。
2. 若环境缺失，按「二、依赖安装」补齐；Python 解释器用 WorkBuddy 托管 venv（本机：`C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe`，含 Pillow）。

## 一、出片命令（核心用法）

1. 让用户确认文案：**每行一句**（一行=一张卡片+一段配音），句末用。！？；均可，流水线会再细切；单行建议 ≤60 字。
2. 执行：
   ```
   <venv-python> <VIDEO_PIPELINE_HOME>/make_video.py <输出.mp4> <标题> <副标题> <文案.txt>
   ```
3. 交付文件命名带版本号（如 `xxxV1.1.mp4`），不覆盖旧版。

## 二、依赖安装（换机重建时按此执行）

| 组件 | 来源 | 要点 |
|---|---|---|
| ffmpeg 7.1 | pip 装 `imageio-ffmpeg`（清华镜像），从 site-packages 把 `ffmpeg-win-x86_64-*.exe` 复制为 `<home>/bin/ffmpeg.exe` | 免 GitHub |
| TTS 引擎 | pip `sherpa-onnx`（清华镜像） | 新版 API 用 `OfflineTtsConfig(VitsModelConfig(...))` 构造，老 kwargs 写法会 TypeError |
| TTS 模型 | sherpa-onnx releases 的 `vits-piper-zh_CN-huayan-medium.tar.bz2`（67MB）解压到 `<home>/models/` | GitHub 直连/ghfast.top 常失败，**用 `https://gh-proxy.com/` 前缀代理** |
| 备用 ASR | pip `faster-whisper` + hf-mirror 下 `Systran/faster-whisper-small`（483MB）到 `<home>/models/faster-whisper-small/` | 仅给外部录音上字幕 |
| 字体 | Windows 自带微软雅黑（msyh.ttc / msyhbd.ttc） | 缺失时封面会退化 |

## 三、注意边界

- **字幕必须文案直出，禁止用 whisper-small 转自己的 TTS 音频**——实测错字率很高（"承接"→"产阶"级）；whisper 仅用于外部录音，且建议 medium 模型（1.5GB）。
- ffmpeg `subtitles` 滤镜在 Windows 下**绝对路径冒号转义必炸**（`Unable to parse option value ... as image size`）；脚本已用 cwd+相对路径规避，改脚本时勿回退。
- 长句自动换行显示，但配音不分段——单行 ≤60 字。
- 数字读法：文案里写成中文数字（"一百二十"）比阿拉伯数字朗读更稳。
- 内存：TTS+whisper 共约 1GB，可与常驻大模型服务并存；运行时不要再加载其他大模型。

## 四、反例避雷

| 反例 | 后果 | 正确做法 |
|---|---|---|
| 直接 GitHub 直连下模型 | 卡死或 0 字节 | gh-proxy.com 前缀代理，或 hf-mirror |
| whisper 生成 TTS 音频字幕 | 错字满屏 | 文案直出 SRT（流水线已内置） |
| subtitles 滤镜写 D\:/绝对路径 | original_size 解析报错 | cwd + 相对路径（已内置） |
| 文案一行塞整段 500 字 | 卡片挤满、配音一气到底 | 一行一句，每行 ≤60 字 |
| 覆盖旧 mp4 文件名 | 版本丢失 | 文件名带版本号递增 |

## 五、版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0.0 | 2026-09-16 | 首版：文案→TTS→卡片→字幕→ffmpeg 五步流水线，端到端 25.3s 样例验证通过 |
| v1.0.1 | 2026-09-16 | 按开放平台规范重构 frontmatter；脚本路径改为 `VIDEO_PIPELINE_HOME` 环境变量可配置 |
