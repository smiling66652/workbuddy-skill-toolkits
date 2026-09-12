---
name: 二级：YouTube 转录
---

# 二级：YouTube 转录

**适用场景**：用户需要获取 YouTube 视频内容、提取字幕、无需看视频获取信息

---

> ⚠️ **两个前置条件，先确认再动手**
>
> 1. **本机两个工具都没装**：`youtube-transcript-api` 和 `yt-dlp` 实测均缺失。
>    装法：`venv_python -m pip install youtube-transcript-api yt-dlp -i https://pypi.tuna.tsinghua.edu.cn/simple`
> 2. **YouTube 在本机网络需要代理**。命令行工具不会自动走代理，要显式指定：
>    ```bash
>    yt-dlp --proxy socks5://127.0.0.1:10808 --write-auto-sub --skip-download "<URL>"
>    ```

---

## 工具对比

| 工具 | 速度 | 准确率 | 费用 | 状态 |
|------|------|--------|------|------|
| **youtube-transcript-api** | 快 | 高 | 免费 | ❌ 未装 |
| **yt-dlp** | 中 | 高 | 免费 | ❌ 未装 |
| **CDP 直连**（不走 API） | 中 | 高 | 免费 | ✅ **可用**，见下 |
| Whisper API | 慢 | 非常高 | 按量付费 | ❌ 需 `OPENAI_API_KEY` |

## 兜底：CDP 直连（本机当下就能用）

不想装包、或字幕 API 被限流时，用你日常浏览器的登录态直接读转录面板：

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/check-deps.mjs"
curl -s -X POST --data-raw 'https://www.youtube.com/watch?v=<ID>' http://localhost:3456/new
# 展开「显示转录文字」，再用 eval 提取全部字幕行
curl -s -X POST "http://localhost:3456/eval?target=ID" -d '[...document.querySelectorAll("ytd-transcript-segment-renderer")].map(e=>e.innerText).join("\n")'
curl -s "http://localhost:3456/close?target=ID"
```

这条路依赖你的浏览器能访问 YouTube（有代理就行），**不需要 pip 安装任何东西**。

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
