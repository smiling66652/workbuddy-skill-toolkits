"""粤语女声旁白（15 秒精简版）+ SentenceBoundary 字幕时间戳。

注意：edge_tts 粤语 voice 仅返回 SentenceBoundary（非 WordBoundary），
脚本已据此生成句子级字幕时间戳。
输出 $VF_OUT/narration_cantonese.mp3 与 $VF_OUT/subs_cantonese.json。
把 SCRIPT 替换为你的粤语文案即可复用于任意主题。
"""
import asyncio
import json
import os

import edge_tts

OUT_DIR = os.environ.get("VF_OUT", os.path.join(os.getcwd(), "output"))
os.makedirs(OUT_DIR, exist_ok=True)

# 15 秒精简版 · 粤语口语（配合 seg1 电视场景 + seg2 前 5s 标注徽章）
SCRIPT = (
    "8月31夜，首部全AI连续剧上卫视，AI坐入客厅电视。"
    "9月1新规，AI内容逐集标清。技术规则落地，你准备好未？"
)

VOICE = "zh-HK-HiuGaaiNeural"  # 粤语女声
RATE = "+15%"
OUT_MP3 = os.path.join(OUT_DIR, "narration_cantonese.mp3")
OUT_SUBS = os.path.join(OUT_DIR, "subs_cantonese.json")


async def main():
    comm = edge_tts.Communicate(SCRIPT, VOICE, rate=RATE)
    sentences = []
    with open(OUT_MP3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                sentences.append({
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"],
                })
    with open(OUT_SUBS, "w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2)
    print("DONE", OUT_MP3)
    print("chars=%d sentences=%d" % (len(SCRIPT), len(sentences)))


asyncio.run(main())
