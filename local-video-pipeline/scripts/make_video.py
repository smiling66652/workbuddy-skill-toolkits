# -*- coding: utf-8 -*-
"""
本地视频合成流水线（纯 CPU，无需 GPU）
用法:
  python make_video.py <输出.mp4> <标题> <副标题> <文案文件.txt>
文案文件: 每行一句/一屏要点，自动逐句配音配图。
"""
import os, re, sys, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 根目录可由环境变量 VIDEO_PIPELINE_HOME 覆盖；默认脚本所在目录（本机安装时为 D:/LocalLLM/video）
BASE = os.environ.get("VIDEO_PIPELINE_HOME", os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
TTS_M  = f"{BASE}/models/vits-piper-zh_CN-huayan-medium"
WORK   = os.path.join(BASE, "work")
FFMPEG = os.path.join(BASE, "bin", "ffmpeg.exe")
WHISPER_M = f"{BASE}/models/faster-whisper-small"
FONT_B = "C:/Windows/Fonts/msyhbd.ttc"
FONT_N = "C:/Windows/Fonts/msyh.ttc"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ---------- 1. 文案切句 ----------
def split_sentences(text):
    sents = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r'(?<=[。！？!?；;])', line)
        sents += [p.strip() for p in parts if p.strip()]
    return sents

# ---------- 2. TTS ----------
_tts = None
def get_tts():
    global _tts
    if _tts is None:
        import sherpa_onnx
        vits = sherpa_onnx.OfflineTtsVitsModelConfig(
            model=f"{TTS_M}/zh_CN-huayan-medium.onnx",
            tokens=f"{TTS_M}/tokens.txt",
            data_dir=f"{TTS_M}/espeak-ng-data")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(vits=vits),
            max_num_sentences=1)
        _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts

def tts_wav(text, path):
    audio = get_tts().generate(text)
    w = np.clip(np.array(audio.samples), -1, 1)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(audio.sample_rate)
        f.writeframes((w * 32767).astype("<i2").tobytes())
    return len(w) / audio.sample_rate

def concat_wavs(paths, out):
    data, rate = [], None
    for p in paths:
        with wave.open(p, "rb") as f:
            rate = f.getframerate()
            data.append(f.readframes(f.getnframes()))
    with wave.open(out, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for d in data:
            f.writeframes(d)

# ---------- 3. 封面与内容卡片 ----------
def make_cover(out, title, subtitle, accent="#C0392B", bg="#1A2430"):
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 26, H], fill=accent)
    d.line([(120, 150), (620, 150)], fill=accent, width=8)
    f1 = font(FONT_B, 110)
    while d.textlength(title, font=f1) > W - 240: f1 = font(FONT_B, f1.size - 4)
    d.text((120, 300), title, fill="white", font=f1)
    if subtitle:
        f2 = font(FONT_N, 52)
        while d.textlength(subtitle, font=f2) > W - 240: f2 = font(FONT_N, f2.size - 4)
        d.text((120, 300 + f1.size + 90), subtitle, fill="#B8C4CE", font=f2)
    d.text((120, H - 140), "AI 本地流水线生成", fill="#5D6D7E", font=font(FONT_N, 34))
    img.save(out)

def make_card(out, text, idx, total, accent="#C0392B", bg="#202B38"):
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 26, H], fill=accent)
    # 文字自动换行
    f = font(FONT_N, 64); max_w = W - 300; line_h = f.size + 26
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) > max_w or ch == "\n":
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    y = (H - len(lines) * line_h) // 2 - 60
    for ln in lines:
        d.text((150, y), ln, fill="white", font=f); y += line_h
    d.text((150, H - 120), f"{idx} / {total}", fill="#5D6D7E", font=font(FONT_N, 36))
    img.save(out)

# ---------- 4. 字幕 ----------
def make_srt_from_script(sents, durs, srt_path, t0=2.5, pad=0.6):
    """文案即字幕（100% 准确）。t0=封面时长，pad=每句尾停顿。"""
    def ts(t):
        h, m = int(t // 3600), int(t % 3600 // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    with open(srt_path, "w", encoding="utf-8") as f:
        t = t0
        for i, (s, d) in enumerate(zip(sents, durs), 1):
            f.write(f"{i}\n{ts(t)} --> {ts(t + d + pad * 0.6)}\n{s}\n\n")
            t += d + pad

def make_srt_asr(wav_path, srt_path):
    """外部音频场景才用 ASR（small 模型中文错字率偏高，medium 更稳）"""
    from faster_whisper import WhisperModel
    model = WhisperModel(WHISPER_M, device="cpu", compute_type="int8")
    segs, info = model.transcribe(wav_path, language="zh", vad_filter=True)
    def ts(t):
        h, m = int(t // 3600), int(t % 3600 // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segs, 1):
            f.write(f"{i}\n{ts(seg.start)} --> {ts(seg.end)}\n{seg.text.strip()}\n\n")

# ---------- 5. ffmpeg 合成 ----------
def render(imgs, durs, wav, srt, out_mp4):
    list_file = os.path.join(WORK, "concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for img, dur in zip(imgs, durs):
            f.write(f"file '{img}'\nduration {dur:.2f}\n")
        f.write(f"file '{imgs[-1]}'\n")
    # cwd=WORK，字幕用相对路径，规避 Windows 盘符冒号转义问题
    cmd = [FFMPEG, "-y",
           "-f", "concat", "-safe", "0", "-i", list_file,
           "-i", wav,
           "-vf", "subtitles=subs.srt:force_style='FontSize=15,Outline=1,MarginV=40'",
           "-c:v", "libx264", "-preset", "fast", "-r", "25", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest",
           out_mp4]
    r = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if r.returncode != 0:
        print("FFMPEG_FAIL:", r.stderr[-1500:]); sys.exit(1)

# ---------- 主流程 ----------
def main():
    out_mp4, title, subtitle, script_file = sys.argv[1:5]
    text = open(script_file, encoding="utf-8").read()
    sents = split_sentences(text)
    print(f"[1/5] 文案切句: {len(sents)} 句")
    os.makedirs(WORK, exist_ok=True)
    wavs, durs = [], []
    for i, s in enumerate(sents):
        p = f"{WORK}/seg_{i:02d}.wav"
        durs.append(tts_wav(s, p)); wavs.append(p)
        print(f"  TTS {i+1}/{len(sents)}: {durs[-1]:.1f}s  {s[:18]}…")
    print("[2/5] 合并音频")
    concat_wavs(wavs, f"{WORK}/voice.wav")
    cover = f"{WORK}/img_00.png"
    make_cover(cover, title, subtitle)
    imgs = [cover]
    img_durs = [2.5]
    for i, s in enumerate(sents):
        p = f"{WORK}/img_{i+1:02d}.png"
        make_card(p, s, i + 1, len(sents))
        imgs.append(p); img_durs.append(durs[i] + 0.6)
    print("[3/5] 图片就绪:", len(imgs), "张")
    print("[4/5] 生成字幕（文案直出，100% 准确）")
    make_srt_from_script(sents, durs, f"{WORK}/subs.srt")
    print("[5/5] ffmpeg 合成")
    render(imgs, img_durs, f"{WORK}/voice.wav", f"{WORK}/subs.srt", out_mp4)
    sz = os.path.getsize(out_mp4)
    print(f"完成: {out_mp4}  ({sz/1e6:.1f} MB)")

if __name__ == "__main__":
    main()
