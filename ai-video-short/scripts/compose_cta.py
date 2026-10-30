"""拼接 seg1(10s) + seg2 前 5s = 15s 竖屏，叠加粤语字幕 + 结尾公众号 CTA 卡片。

输入（均位于 $VF_OUT）：
  seg1.mp4 / seg2.mp4（已生成的竖版片段）
  narration_cantonese.mp3 + subs_cantonese.json（make_canto.py 产物）
输出：$VF_OUT/<OUT_NAME，默认 AI内容新规-15s-粤语女声-CTA.mp4>

CTA 文案通过环境变量注入（脱敏：默认占位，运行时由你的私人配置提供）：
  CTA_TITLE / CTA_NAME / CTA_SUB
注意：前台渲染约 2 分钟，请用后台运行。
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)

OUT_DIR = os.environ.get("VF_OUT", os.path.join(os.getcwd(), "output"))
FINAL = os.path.join(OUT_DIR, os.environ.get("OUT_NAME", "AI内容新规-15s-粤语女声-CTA.mp4"))

W, H = 1080, 1920
FPS = 30
FONT_PATH = os.environ.get("VF_FONT", "C:/Windows/Fonts/msyhbd.ttc")
FONT_SIZE = 62
LINE_GAP = 24
CHARS_PER_LINE = 13
BOTTOM_MARGIN = 420
CTA_DUR = 2.5  # 结尾 CTA 卡片时长

CTA_TITLE = os.environ.get("CTA_TITLE", "关注公众号")
CTA_NAME = os.environ.get("CTA_NAME", "你的公众号名称")
CTA_SUB = os.environ.get("CTA_SUB", "每天陪你读懂 AI 与财商")


def wrap(text, n):
    chunks = [text[i:i + n] for i in range(0, len(text), n)] or [text]
    # 避免末尾只剩一个标点符号独占一行
    if len(chunks) > 1 and len(chunks[-1]) <= 1 and chunks[-1] in "。，！？、；：.":
        chunks[-2] = chunks[-2] + chunks[-1]
        chunks = chunks[:-1]
    return chunks


def make_subtitle_image(text):
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


def make_cta_image():
    """结尾公众号关注卡片（透明底，居中文字 + 半透明暗层保证可读）。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 半透明暗层
    d.rectangle([0, 0, W, H], fill=(10, 12, 20, 150))
    # 顶部装饰细线
    cx = W // 2
    d.line([(cx - 260, 760), (cx + 260, 760)], fill=(255, 209, 102, 230), width=4)

    font_big = ImageFont.truetype(FONT_PATH, 76)
    font_mid = ImageFont.truetype(FONT_PATH, 58)
    font_sm = ImageFont.truetype(FONT_PATH, 40)

    def center(text, y, font, fill):
        b = d.textbbox((0, 0), text, font=font)
        x = (W - (b[2] - b[0])) / 2 - b[0]
        d.text((x, y), text, font=font, fill=fill)

    center(CTA_TITLE, 820, font_mid, (255, 255, 255, 255))
    center(CTA_NAME, 910, font_big, (255, 209, 102, 255))
    center(CTA_SUB, 1030, font_sm, (220, 224, 235, 235))
    return np.array(img)


def main():
    subs = json.load(open(os.path.join(OUT_DIR, "subs_cantonese.json"), encoding="utf-8"))

    seg1 = VideoFileClip(os.path.join(OUT_DIR, "seg1.mp4")).resized((W, H)).with_fps(FPS).without_audio()
    seg2 = (
        VideoFileClip(os.path.join(OUT_DIR, "seg2.mp4"))
        .subclipped(0, 5.0)
        .resized((W, H))
        .with_fps(FPS)
        .without_audio()
    )
    print("seg1 -> %.2fs" % seg1.duration)
    print("seg2(trim) -> %.2fs" % seg2.duration)

    video = concatenate_videoclips([seg1, seg2], method="compose")
    print("video_duration = %.2fs" % video.duration)

    audio = AudioFileClip(os.path.join(OUT_DIR, "narration_cantonese.mp3"))
    print("audio_duration = %.2fs" % audio.duration)

    layers = [video]
    for s in subs:
        start = s["offset"] / 1e7
        dur = s["duration"] / 1e7
        img = make_subtitle_image(s["text"])
        ic = (
            ImageClip(img)
            .with_duration(dur)
            .with_start(start)
            .with_position(("center", H - BOTTOM_MARGIN - img.shape[0]))
        )
        layers.append(ic)

    cta = ImageClip(make_cta_image()).with_duration(CTA_DUR).with_start(video.duration - CTA_DUR).with_position((0, 0))
    layers.append(cta)

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
