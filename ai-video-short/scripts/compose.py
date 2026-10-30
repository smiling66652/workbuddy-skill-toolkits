"""拼接三段竖屏素材 + 中文配音 + 硬字幕，输出 30 秒 1080x1920 成片。

输入（均位于 $VF_OUT）：
  seg1.mp4 / seg2.mp4 / seg3.mp4（已生成的竖版片段）
  narration.mp3 + subs.json（make_narration.py 产物）
输出：$VF_OUT/<OUT_NAME，默认 AI内容新规-30s-竖版.mp4>

注意：前台渲染约 2 分钟，超过 Bash 前台超时会被打断，请用后台运行。
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, VideoFileClip, concatenate_videoclips

OUT_DIR = os.environ.get("VF_OUT", os.path.join(os.getcwd(), "output"))
FINAL = os.path.join(OUT_DIR, os.environ.get("OUT_NAME", "AI内容新规-30s-竖版.mp4"))

W, H = 1080, 1920
FPS = 30
FONT_PATH = os.environ.get("VF_FONT", "C:/Windows/Fonts/msyhbd.ttc")
FONT_SIZE = 62
LINE_GAP = 24
CHARS_PER_LINE = 13
BOTTOM_MARGIN = 420


def wrap(text: str, n: int):
    return [text[i:i + n] for i in range(0, len(text), n)] or [text]


def make_subtitle_image(text: str):
    lines = wrap(text, CHARS_PER_LINE)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    widths, heights = [], []
    for ln in lines:
        b = dummy.textbbox((0, 0), ln, font=font)
        widths.append(b[2] - b[0])
        heights.append(b[3] - b[1])
    line_h = max(heights) + LINE_GAP
    box_w = max(widths) + 80
    box_h = line_h * len(lines) + 40

    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 20
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=font)
        x = (box_w - (b[2] - b[0])) / 2 - b[0]
        d.text((x + 3, y + 3), ln, font=font, fill=(0, 0, 0, 235))
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255))
        y += line_h
    return np.array(img)


def main():
    subs = json.load(open(os.path.join(OUT_DIR, "subs.json"), encoding="utf-8"))

    clips = []
    for name in ("seg1.mp4", "seg2.mp4", "seg3.mp4"):
        p = os.path.join(OUT_DIR, name)
        c = VideoFileClip(p)
        c = c.resized((W, H)).with_fps(FPS).without_audio()
        clips.append(c)
        print("%s -> %.2fs %dx%d" % (name, c.duration, c.w, c.h))

    video = concatenate_videoclips(clips, method="compose")
    print("video_duration = %.2fs" % video.duration)

    audio = AudioFileClip(os.path.join(OUT_DIR, "narration.mp3"))
    print("audio_duration = %.2fs" % audio.duration)

    layers = [video]
    for s in subs:
        start = s["start"]
        dur = s["dur"]
        img = make_subtitle_image(s["text"])
        ic = (ImageClip(img)
              .with_duration(dur)
              .with_start(start)
              .with_position(("center", H - BOTTOM_MARGIN - img.shape[0])))
        layers.append(ic)

    final = CompositeVideoClip(layers, size=(W, H)).with_duration(video.duration)
    final = final.with_audio(audio)

    final.write_videofile(
        FINAL,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="12M",
        preset="medium",
        logger=None,
    )
    print("FINAL_SIZE_MB = %.2f" % (os.path.getsize(FINAL) / 1024 / 1024))


main()
