# -*- coding: utf-8 -*-
"""STEP 2 · 合成数字人讲解短视频(无字幕版):
   背景视频(循环) + 角色透明素材(GIF/PNG序列, 循环) + 配音  -> 各段 webm -> 拼接成片

输入 : <WORK>/scenes.json   (gen_audio 产出)  + <WORK>/bg_videos/*.mp4  + 角色透明素材
输出 : <WORK>/explainer_final.webm

环境变量(均可选):
  EXPLAINER_WORKDIR  工作目录
  CHAR_GIF           角色透明素材路径，默认 <技能目录>/assets/character.gif (用户自备)
  CHAR_X / CHAR_Y    角色在 1920x1080 画布上的叠加坐标(像素)，默认 1340 / 460
"""
import os, subprocess, json
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("EXPLAINER_WORKDIR", os.path.join(HERE, "work"))
FF = imageio_ffmpeg.get_ffmpeg_exe()
CHAR_GIF = os.environ.get("CHAR_GIF", os.path.join(HERE, "assets", "character.gif"))
SEG = os.path.join(BASE, "seg")
os.makedirs(SEG, exist_ok=True)

CHAR_X = int(os.environ.get("CHAR_X", "1340"))
CHAR_Y = int(os.environ.get("CHAR_Y", "460"))


def build_filter():
    # 背景缩放 16:9 + 去生成式视频角标水印(右下角约 1680,1012,234,60) + 叠角色透明素材
    return ("[0:v]scale=1920:1080,setsar=1,delogo=x=1680:y=1012:w=234:h=60[bg];"
            f"[bg][1:v]overlay={CHAR_X}:{CHAR_Y}:format=auto[vout]")


def main():
    scenes = json.load(open(os.path.join(BASE, "scenes.json"), encoding="utf-8"))
    fxtxt = build_filter()
    seg_files = []
    for s in scenes:
        k = s["key"]
        out = os.path.join(SEG, f"{k}.webm")
        cmd = [FF, "-hide_banner", "-y",
               "-stream_loop", "-1", "-i", s["bg"],
               "-stream_loop", "-1", "-i", CHAR_GIF,
               "-i", s["audio"],
               "-filter_complex", fxtxt, "-map", "[vout]", "-map", "2:a",
               "-t", f"{s['dur']:.2f}",
               "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30",
               "-row-mt", "1", "-cpu-used", "2", "-pix_fmt", "yuv420p",
               "-c:a", "libvorbis", "-b:a", "128k", "-ar", "44100", out]
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        seg_files.append(out)
        print(k, "rc", r.returncode, "dur", s["dur"])
        if r.returncode != 0:
            print(r.stderr[-1500:])
    final = os.path.join(BASE, "explainer_final.webm")
    n = len(seg_files)
    conc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[outv][outa]"
    cmd = [FF, "-hide_banner", "-y"] + [x for f in seg_files for x in ("-i", f)]
    cmd += ["-filter_complex", conc, "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-row-mt", "1",
            "-cpu-used", "2", "-pix_fmt", "yuv420p",
            "-c:a", "libvorbis", "-b:a", "128k", final]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    print("CONCAT rc", r.returncode)
    if r.returncode != 0:
        print(r.stderr[-1500:])
    print("FINAL", final, os.path.getsize(final) if os.path.exists(final) else "MISSING")


if __name__ == "__main__":
    main()
