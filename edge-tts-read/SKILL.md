---
name: edge-tts-read
description: 文字转语音：微软 Edge 在线音色免费合成，中文多音色，可出字幕文件。触发词：文字转语音、朗读、配音、生成语音、TTS、edge-tts。
display_name: 文字转语音（Edge）
display_name_en: Text to Speech (Edge TTS)
description_zh: 基于 rany2/edge-tts（★1.2万+）的文字转语音技能：调用微软 Edge 浏览器的在线语音合成服务，无需任何密钥与付费账号，数十种中文音色（晓晓/云希/云扬及方言音色）开箱即用，可同时导出字幕文件、调节语速音调。文章朗读、视频配音、通知播报的零成本方案。注意：依赖微软在线服务且属非官方接口，重要生产链路请备选离线方案。
description_en: "Text-to-speech skill based on rany2/edge-tts (12k+ stars): calls Microsoft Edge's online TTS service with no API key or paid account; dozens of Chinese voices including dialects; exports subtitles and adjusts rate/pitch. A zero-cost option for article reading, video narration and notifications. Note: unofficial interface over Microsoft's online service — have an offline fallback for critical production."
version: 1.0.0
author: 移植自 rany2/edge-tts（LGPL-3.0）
---
# 文字转语音（Edge TTS）

底层是 **edge-tts**：调用微软 Edge 浏览器"大声朗读"的在线语音合成服务。**免费、无需密钥**，音色是微软神经网络音色（Azure TTS 同源），中文音色齐全——零成本的文字转语音方案。

**定位提醒**：这是社区对微软在线服务的**非官方调用**，服务可用性不承诺 SLA；重要生产链路请备选离线方案（如 sherpa-onnx 的离线 TTS）。

## 与姊妹技能的分工

| 需求 | 用哪个 |
|---|---|
| 在线免费、音色自然 | 本技能（edge-tts） |
| 完全离线合成 | 本地语音套件（sherpa-onnx）TTS 部分 |
| 语音转文字 | 中文语音转写（FunASR）/ 语音转写（Whisper） |

## 一、安装

```bash
pip install edge-tts
```

纯 Python 轻包（依赖 aiohttp），秒装。**需要联网**（调用微软服务）。

## 二、命令行

```bash
edge-tts --voice zh-CN-XiaoxiaoNeural --text "下午三点开会，请准时参加。" --write-media 通知.mp3
edge-tts --voice zh-CN-XiaoxiaoNeural --file 文章.txt --write-media 文章.mp3 --write-subtitles 文章.vtt
edge-tts --list-voices                       # 全部音色
edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+10% --pitch=+5Hz --text "语速调快" --write-media out.mp3
```

## 三、常用中文音色

| 音色名 | 特点 |
|---|---|
| `zh-CN-XiaoxiaoNeural` | 晓晓·女声（最常用，多情感风格） |
| `zh-CN-YunxiNeural` | 云希·男声（活泼） |
| `zh-CN-YunyangNeural` | 云扬·男声（新闻播报） |
| `zh-CN-YunxiaNeural` | 云夏·女声（少年感） |
| `zh-CN-liaoning-XiaobeiNeural` | 东北话·女声 |
| `zh-HK-HiuMaanNeural` | 粤语·女声 |
| `zh-TW-HsiaoChenNeural` | 台湾腔·女声 |

完整列表以 `--list-voices` 为准（还有陕西、河南等方言音色）。

## 四、Python API

```python
import asyncio, edge_tts

async def main():
    tts = edge_tts.Communicate("今天的数据日报已生成", voice="zh-CN-XiaoxiaoNeural")
    await tts.save("日报播报.mp3")

asyncio.run(main())
```

## 五、批量合成（推荐用脚本）

```bash
python scripts/tts_batch.py 文章目录 -o out                     # 每个 .txt → .mp3
python scripts/tts_batch.py 通知.txt -o out --voice zh-CN-YunyangNeural --subtitle
python scripts/tts_batch.py 目录 -o out --rate "+10%" --dry-run
```

脚本逐个文本文件合成，失败不中断；`--subtitle` 同时产出 .vtt 字幕（按文本行分段）。

## 六、常见坑

1. **报错 NoAudioReceived** → 微软服务抖动或网络受限：重试；换网络；不要高频连续调用
2. **长文本超时** → 按 1500–3000 字分段合成后拼接（脚本已内置分段逻辑）
3. **多音字读错** → 换音色或改写文本（TTS 通病）
4. **语速调节无效** → `--rate=+10%` 的 `+` 必须带上
5. **商用提醒** → 音色属微软服务，正式产品商用前请自行确认使用边界；本项目不打包、不转售该服务

## 七、边界

- 非官方接口，微软随时可能调整——生产环境务必有离线备选
- 不做情感极致控制（SSML 细粒度调节是 Azure 官方 API 的能力）
- 输出 mp3（webm 音频）；要 wav 先转格式
