# -*- coding: utf-8 -*-
"""验收: 检查 webm 总时长 / 角色叠加(中心应为角色色) / 水印区白像素残留。

角色中心像素坐标(按 CHAR_X/Y 与角色尺寸推算；示例为 418x447 角色叠在 1340,460 时中心约 1549,683)
可用环境变量覆盖: CHECK_CX / CHECK_CY
"""
import os, subprocess, re
from PIL import Image
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("EXPLAINER_WORKDIR", os.path.join(HERE, "work"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
FINAL = os.path.join(BASE, "explainer_final.webm")
CX = int(os.environ.get("CHECK_CX", "1549"))
CY = int(os.environ.get("CHECK_CY", "683"))


def duration_of(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    return float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))


def main():
    dur = duration_of(FINAL)
    print("总时长(秒):", round(dur, 2), " 大小(MB):", round(os.path.getsize(FINAL) / 1024 / 1024, 2))
    for t in [2, 12, 22, 32]:
        fr = os.path.join(BASE, f"chk_{t}.png")
        subprocess.run([FF, "-hide_banner", "-y", "-ss", str(t), "-i", FINAL, "-frames:v", "1", fr],
                       capture_output=True)
        im = Image.open(fr).convert("RGB")
        print(f"t={t}s 角色中心像素={im.getpixel((CX, CY))}")
        os.remove(fr)
    fr = os.path.join(BASE, "chk_wm.png")
    subprocess.run([FF, "-hide_banner", "-y", "-ss", "1", "-i", FINAL, "-frames:v", "1", fr],
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
