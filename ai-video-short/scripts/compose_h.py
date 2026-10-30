"""把 seg1 + seg2 前 5s 的竖版源素材，重构成 1920x1080 横屏版本，粤语字幕 + CTA 重新适配。

输入（均位于 $VF_OUT）：
  seg1.mp4 / seg2.mp4（已生成的竖版片段）
  narration_cantonese.mp3 + subs_cantonese.json（make_canto.py 产物）
输出：$VF_OUT/<OUT_NAME，默认 AI内容新规-15s-粤语女声-CTA-横屏.mp4>

CTA 文案通过环境变量注入（脱敏：默认占位，运行时由你的私人配置提供）：
  CTA_TITLE / CTA_NAME / CTA_SUB
注意：由正方形 1080×1080 扩到 16:9 会有轻微水平拉伸；要完全无拉伸需重新生成 16:9 源片段。
前台渲染约 2 分钟，请用后台运行。
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
FINAL = os.path.join(
    OUT_DIR, os.environ.get("OUT_NAME", "AI内容新规-15s-粤语女声-CTA-横屏.mp4")
)

W, H = 1920, 1080
FPS = 30
SRC_W, SRC_H = 1080, 1920
CROP_TOP = (SRC_H - SRC_W) // 2  # 420
CROP_BOTTOM = CROP_TOP + SRC_W  # 1500
FONT_PATH = os.environ.get("VF_FONT", "C:/Windows/Fonts/msyhbd.ttc")
FONT_SIZE = 48
LINE_GAP = 20
CHARS_PER_LINE = 18
BOTTOM_MARGIN = 160
CTA_DUR = 2.5

CTA_TITLE = os.environ.get("CTA_TITLE", "关注公众号")
CTA_NAME = os.environ.get("CTA_NAME", "你的公众号名称")
CTA_SUB = os.environ.get("CTA_SUB", "每天陪你读懂 AI 与财商")


def wrap(text, n):
    chunks = [text[i:i + n] for i in range(0, len(text), n)] or [text]
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
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(10, 12, 20, 150))
    cx = W // 2
    d.line([(cx - 300, 470), (cx + 300, 470)], fill=(255, 209, 102, 230), width=4)

    font_big = ImageFont.truetype(FONT_PATH, 72)
    font_mid = ImageFont.truetype(FONT_PATH, 54)
    font_sm = ImageFont.truetype(FONT_PATH, 36)

    def center(text, y, font, fill):
        b = d.textbbox((0, 0), text, font=font)
        x = (W - (b[2] - b[0])) / 2 - b[0]
        d.text((x, y), text, font=font, fill=fill)

    center(CTA_TITLE, 510, font_mid, (255, 255, 255, 255))
    center(CTA_NAME, 590, font_big, (255, 209, 102, 255))
    center(CTA_SUB, 695, font_sm, (220, 224, 235, 235))
    return np.array(img)


def reframe_clip(clip):
    """把 1080x1920 竖版素材裁成中心 1080x1080 正方形，再扩成 1920x1080 横屏。"""
    return (
        clip.cropped(y1=CROP_TOP, y2=CROP_BOTTOM)
        .resized((W, H))
        .with_fps(FPS)
        .without_audio()
    )


def main():
    subs = json.load(
        open(os.path.join(OUT_DIR, "subs_cantonese.json"), encoding="utf-8")
    )

    seg1 = reframe_clip(VideoFileClip(os.path.join(OUT_DIR, "seg1.mp4")))
    seg2 = reframe_clip(
        VideoFileClip(os.path.join(OUT_DIR, "seg2.mp4")).subclipped(0, 5.0)
    )
    print("seg1 -> %.2fs %dx%d" % (seg1.duration, seg1.w, seg1.h))
    print("seg2(trim) -> %.2fs %dx%d" % (seg2.duration, seg2.w, seg2.h))

    video = concatenate_videoclips([seg1, seg2], method="compose")
    print("video_duration = %.2fs" % video.duration)

    audio = AudioFileClip(os.path.join(OUT_DIR, "narration_cantonese.mp3"))
    print("audio_duration = %.2fs" % audio.duration)

    layers = [video]
    for s in subs:
        start = s["offset"] / 1e7
        dur = s["duration"] / 1e7
        sub_img = make_subtitle_image(s["text"])
        ic = (
            ImageClip(sub_img)
            .with_duration(dur)
            .with_start(start)
            .with_position(("center", H - BOTTOM_MARGIN - sub_img.shape[0]))
        )
        layers.append(ic)

    cta = (
        ImageClip(make_cta_image())
        .with_duration(CTA_DUR)
        .with_start(video.duration - CTA_DUR)
        .with_position((0, 0))
    )
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
