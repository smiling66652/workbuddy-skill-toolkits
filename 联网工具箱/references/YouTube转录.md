---
name: 二级：YouTube 转录
---

# 二级：YouTube 转录

**适用场景**：用户需要获取YouTube视频内容、提取字幕、无需看视频获取信息

---

## 工具对比

| 工具 | 速度 | 准确率 | 费用 | 推荐场景 |
|------|------|--------|------|------------|
| **youtube-transcript-api** | 快 | 高 | 免费 | 获取字幕文本 |
| **yt-dlp** | 中 | 高 | 免费 | 下载字幕文件 |
| **Whisper API** | 慢 | 非常高 | 按量付费 | 无字幕视频 |

---

## 三级执行：youtube-transcript-api（推荐）

**触发词**：这个YouTube视频讲了什么、帮我看这个视频、提取视频字幕

```bash
# 安装
pip install youtube-transcript-api

# 获取字幕（自动选最佳语言轨道）
python -c "
from youtube_transcript_api import YouTubeTranscriptApi
video_id = 'dQw4w9WgXcQ'  # 从URL提取
transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'en'])
for segment in transcript:
    print(f\"{segment['start']:.1f}s: {segment['text']}\")
"

# 获取字幕并让 LLM 总结
python -c "
from youtube_transcript_api import YouTubeTranscriptApi
video_id = 'dQw4w9WgXcQ'
transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'en'])
full_text = ' '.join([s['text'] for s in transcript])
print(full_text[:2000])  # 取前2000字给LLM总结
"
```

**从URL提取 video_id**：
```python
import re
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = re.search(r"v=([^&]+)", url).group(1)
```

---

## 三级执行：yt-dlp（下载字幕文件）

```bash
# 安装
pip install yt-dlp

# 下载自动字幕（不下载视频）
yt-dlp --write-auto-sub --skip-download "https://youtube.com/watch?v=xxx"

# 下载人工字幕（如果有）
yt-dlp --write-sub --sub-lang zh-Hans,en --skip-download "https://youtube.com/watch?v=xxx"

# 下载并转换为纯文本
yt-dlp --write-auto-sub --skip-download -o "%(id)s.%(ext)s" "URL"
# 然后用工具将 .vtt 转换为纯文本
```

---

## 三级执行：Whisper API（无字幕视频）

**触发词**：这个视频没有字幕、帮我转写这个视频

```bash
# 用 yt-dlp 下载音频
yt-dlp -x --audio-format mp3 -o "%(id)s.%(ext)s" "https://youtube.com/watch?v=xxx"

# 用 Whisper API 转写
# 需要 OPENAI_API_KEY
curl -X POST "https://api.openai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@audio.mp3" \
  -F "model=whisper-1" \
  -F "language=zh"
```

---

## 使用建议

1. **有字幕** → 用 youtube-transcript-api（最快最准）
2. **需要字幕文件** → 用 yt-dlp 下载
3. **无字幕** → 用 Whisper API 转写（需付费）
4. **中文视频** → 优先选 `languages=['zh', 'zh-Hans', 'zh-Hant']`
5. **总结长视频** → 取前2000字给LLM，或分段处理
