# -*- coding: utf-8 -*-
"""STEP 1 · 生成角色配音(edge-tts) 并探测时长，输出 scenes.json 供合成。

输入 : <WORK>/script.json   (由用户按台词编写，见 references/sample_script.json)
输出 : <WORK>/scenes.json   (含每段音频绝对路径与时长)

环境变量(均可选):
  EXPLAINER_WORKDIR  工作目录，默认 <技能目录>/work
  EXPLAINER_VOICE   edge-tts 音色，默认 zh-CN-YunxiaNeural(清亮女声，适合数字人)
  EXPLAINER_RATE    语速，默认 +5%
"""
import os, json, re, asyncio, subprocess
import edge_tts
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("EXPLAINER_WORKDIR", os.path.join(HERE, "work"))
AUD = os.path.join(BASE, "audio")
os.makedirs(AUD, exist_ok=True)
BG = os.path.join(BASE, "bg_videos")
FF = imageio_ffmpeg.get_ffmpeg_exe()

VOICE = os.environ.get("EXPLAINER_VOICE", "zh-CN-YunxiaNeural")
RATE = os.environ.get("EXPLAINER_RATE", "+5%")


async def gen(text, out):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(out)


def duration_of(path):
    r = subprocess.run([FF, "-i", path], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mm, ss = (int(m.group(1)), int(m.group(2)), float(m.group(3)))
    return h * 3600 + mm * 60 + ss


def main():
    script = json.load(open(os.path.join(BASE, "script.json"), encoding="utf-8"))
    scenes = []
    for seg in script:
        k = seg["key"]
        text = seg["text"]
        bg = seg["bg"]
        ao = os.path.join(AUD, k + ".mp3")
        asyncio.run(gen(text, ao))
        dur = duration_of(ao)
        scenes.append({
            "key": k,
            "audio": ao,
            "bg": bg if os.path.isabs(bg) else os.path.join(BG, bg),
            "dur": round(dur, 2),
        })
        print(k, "dur", round(dur, 2))
    out_path = os.path.join(BASE, "scenes.json")
    json.dump(scenes, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("AUDIO DONE ->", out_path)


if __name__ == "__main__":
    main()
