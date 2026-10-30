"""普通话旁白 + WordBoundary 字幕时间戳（edge_tts，免费）。

输出 $VF_OUT/narration.mp3 与 $VF_OUT/subs.json。
可调参数：TEXT / VOICE / RATE。
把 TEXT 替换为你的文案即可复用于任意主题。
"""
import asyncio
import json
import os

import edge_tts

OUT_DIR = os.environ.get("VF_OUT", os.path.join(os.getcwd(), "output"))
os.makedirs(OUT_DIR, exist_ok=True)

TEXT = ("8月31日晚，国内首部全AI生成连续剧《后西游记·花果山篇》登陆卫视黄金档，边审边播。"
        "AI第一次不是幕后工具，而是坐进了客厅的电视里。"
        "一天之后，9月1日，微短剧新规正式施行，AI生成内容，必须逐集标注。"
        "一边是技术狂奔，一边是规则落地。"
        "2026年的内容行业，正在同时踩下油门和刹车。"
        "你，准备好了吗？")

VOICE = "zh-CN-YunjianNeural"
RATE = "+8%"
MP3 = os.path.join(OUT_DIR, "narration.mp3")
SUBS = os.path.join(OUT_DIR, "subs.json")


async def main():
    comm = edge_tts.Communicate(TEXT, VOICE, rate=RATE)
    words = []
    with open(MP3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 1e7,
                    "dur": chunk["duration"] / 1e7,
                })
    with open(SUBS, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)
    total = (words[-1]["start"] + words[-1]["dur"]) if words else 0
    print("words=%d  narration_duration=%.2fs" % (len(words), total))
    print("mp3_bytes=%d" % os.path.getsize(MP3))


asyncio.run(main())
