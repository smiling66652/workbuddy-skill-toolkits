---
name: 二级：AI生成（MiniMax CLI）
---

# 二级：AI生成（MiniMax CLI）

**适用场景**：用户需要生成图片、视频、语音、音乐等多模态内容

---

## 工具对比

| 工具 | 速度 | 质量 | 费用 | 推荐场景 |
|------|------|------|------|------------|
| **MiniMax CLI（mmx）** | 快 | 高 | 按量付费 | 文生图/视频/语音 |
| **OpenAI DALL-E** | 中 | 非常高 | 按张付费 | 高质量图片生成 |
| **OpenAI Whisper** | 中 | 非常高 | 按分钟付费 | 语音转文字 |
| **Stable Diffusion** | 慢 | 高 | 本地免费 | 本地图片生成 |

---

## 三级执行：MiniMax CLI（推荐）

**触发词**：生成图片、画一张、生成视频、转文字、语音合成

### 安装

```bash
# 全局安装
npm install -g mmx-cli

# 验证安装
mmx --version
```

### 配置 API Key

```bash
# 方法1：交互式配置
mmx auth login

# 方法2：非交互式配置
mmx auth login --api-key sk-xxxxx

# 查看配置状态
mmx auth status

# 查看剩余配额
mmx quota
```

**获取 API Key**：访问 [MiniMax 平台](https://api.minimax.io/)

---

### 文本生成

```bash
# 基础对话
mmx text chat --message "Write a poem"

# 指定模型+流式输出
mmx text chat --model MiniMax-M2.7-highspeed --message "Hello" --stream

# 带系统提示词
mmx text chat --system "You are a coding assistant" --message "Fizzbuzz in Go"

# 多轮对话
mmx text chat --message "user:Hi" --message "assistant:Hey!" --message "How are you?"

# 从文件读取对话内容+JSON格式输出
cat messages.json | mmx text chat --messages-file - --output json
```

---

### 图片生成

```bash
# 基础文生图
mmx image "A cat in a spacesuit"

# 生成3张16:9比例的图片
mmx image generate --prompt "A cat" --n 3 --aspect-ratio 16:9

# 指定输出目录
mmx image generate --prompt "Logo" --out-dir ./out/
```

**注意事项**：
- 按比例生成多张图片时，会自动创建 `out-dir`
- 图片格式：PNG/JPG
- 比例选项：1:1、16:9、9:16、4:3、3:4

---

### 视频生成

```bash
# 生成视频并自动下载
mmx video generate --prompt "Ocean waves at sunset" --download sunset.mp4

# 异步生成（不等待结果）
mmx video generate --prompt "A robot painting" --async

# 查询指定任务状态
mmx video task get --task-id 123456

# 通过文件ID下载视频
mmx video download --file-id 176844028768320 --out video.mp4
```

**注意事项**：
- 视频生成时间较长（几分钟到几十分钟）
- 建议用 `--async` 异步生成，然后轮询任务状态
- 下载的视频格式：MP4

---

### 语音合成

```bash
# 基础语音合成
mmx speech synthesize --text "Hello!" --out hello.mp3

# 流式输出（直接播放）
mmx speech synthesize --text "Stream me" --stream | mpv -

# 指定音色+调节语速
mmx speech synthesize --text "Hi" --voice English_magnetic_voiced_man --speed 1.2

# 从标准输入读取文本生成
echo "Breaking news" | mmx speech synthesize --text-file - --out news.mp3

# 查看所有可用音色
mmx speech voices
```

**可用音色**（部分）：
- `Chinese_magnetic_voiced_woman` — 中文磁性女声
- `Chinese_magnetic_voiced_man` — 中文磁性男声
- `English_magnetic_voiced_woman` — 英文磁性女声
- `English_magnetic_voiced_man` — 英文磁性男声

---

## 三级执行：OpenAI DALL-E（高质量图片）

**触发词**：生成高质量图片、DALL-E生成

```python
# 需要 OPENAI_API_KEY
import openai

response = openai.Image.create(
    prompt="A cat in a spacesuit",
    n=1,
    size="1024x1024"
)
image_url = response['data'][0]['url']
print(image_url)
```

---

## 三级执行：OpenAI Whisper（语音转文字）

**触发词**：转文字、语音转文字、转录音频

```python
# 需要 OPENAI_API_KEY
import openai

audio_file = open("audio.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript['text'])
```

---

## 使用建议

1. **快速生成** → MiniMax CLI（mmx）
2. **高质量图片** → OpenAI DALL-E
3. **语音转文字** → OpenAI Whisper API 或本地 Whisper
4. **成本控制** → 注意按量付费，避免批量生成时超预算
5. **网络连接** → MiniMax API 需要访问 `api.minimax.io`（国内）或 `api.minimaxi.com`（国外）
