# -*- coding: utf-8 -*-
"""STEP 3 · 最终 webm -> mp4 (H.264 yuv420p + AAC) 纯转码 + 程序化验收。

说明: 纯转码(无滤镜链)时 libx264 可用；若报 -22 线程崩溃，先确认是否处于复杂滤镜场景，
      改用 webm 预览或移除非必要滤镜。若在本机被沙箱拦截，运行需关闭沙箱。

输出 : <WORK>/explainer_final.mp4
"""
import os, subprocess, re
from PIL import Image
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("EXPLAINER_WORKDIR", os.path.join(HERE, "work"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = os.path.join(BASE, "explainer_final.webm")
DST = os.path.join(BASE, "explainer_final.mp4")


def duration_of(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    return float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))


def main():
    r = subprocess.run([FF, "-hide_banner", "-y", "-i", SRC,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-preset", "medium", "-crf", "18",
                        "-c:a", "aac", "-b:a", "128k", DST],
                       capture_output=True, text=True, errors="replace")
    print("TRANSCODE rc", r.returncode)
    if r.returncode != 0 or not os.path.exists(DST):
        raise SystemExit("转码失败: " + r.stderr[-300:])
    print("mp4 size MB", round(os.path.getsize(DST) / 1024 / 1024, 2))
    print("mp4 时长(秒):", round(duration_of(DST), 2))

    # 水印区白像素残留(右下角 1680-1914, 1012-1072)
    fr = os.path.join(BASE, "chk_wm.png")
    subprocess.run([FF, "-hide_banner", "-y", "-ss", "1", "-i", DST, "-frames:v", "1", fr],
                   capture_output=True)
    im = Image.open(fr).convert("RGB")
    box = im.crop((1680, 1012, 1914, 1072))
    px = list(box.getdata())
    white = sum(1 for R, G, B in px if R > 230 and G > 230 and B > 230)
    print("水印区白像素占比%:", round(100 * white / len(px), 2))
    os.remove(fr)
    print("验收完成")


if __name__ == "__main__":
    main()
