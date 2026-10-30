# -*- coding: utf-8 -*-
"""edge-tts 批量合成封装。

用法:
  python tts_batch.py <文本文件或目录...> -o <输出目录> [--voice zh-CN-XiaoxiaoNeural]
                      [--rate "+10%"] [--pitch "+0Hz"] [--subtitle] [--dry-run]
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

TEXT_EXT = {".txt", ".md"}


def collect(inputs, exts):
    out = []
    for t in inputs:
        p = Path(t)
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [q for q in p.rglob("*") if q.is_file() and q.suffix.lower() in exts]
    return sorted(set(out))


async def synth_one(text: str, voice: str, rate: str, pitch: str, dst: Path, vtt: Path | None):
    import edge_tts
    kw = dict(voice=voice, rate=rate, pitch=pitch)
    # 长文本分段合成（每段约 1800 字），避免服务端超时
    chunks, buf = [], []
    size = 0
    for line in text.splitlines():
        buf.append(line)
        size += len(line)
        if size >= 1800:
            chunks.append("\n".join(buf))
            buf, size = [], 0
    if buf:
        chunks.append("\n".join(buf))
    tmp_files = []
    for idx, chunk in enumerate(chunks):
        tmp = dst.with_suffix(".part%d.mp3" % idx)
        await edge_tts.Communicate(chunk, **kw).save(str(tmp))
        tmp_files.append(tmp)
    if len(tmp_files) == 1:
        tmp_files[0].replace(dst)
    else:
        with open(dst, "wb") as out:
            for tmp in tmp_files:
                out.write(tmp.read_bytes())
                tmp.unlink()
    if vtt is not None:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        vtt.write_text("WEBVTT\n\n" + "\n\n".join(
            "%d\n00:00:%02d.000 --> 00:00:%02d.000\n%s" % (i, min(i * 5, 599), min(i * 5 + 5, 599), ln)
            for i, ln in enumerate(lines[:119], 1)), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="edge-tts 批量合成")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--pitch", default="+0Hz")
    ap.add_argument("--subtitle", action="store_true", help="同时输出 .vtt 字幕（按行估算时间）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = collect(args.inputs, TEXT_EXT)
    if not files:
        print("没有匹配的文本文件（.txt/.md）")
        return 1
    print("待合成 %d 个文件%s\n" % (len(files), "（dry-run）" if args.dry_run else ""))
    if args.dry_run:
        for p in files:
            print("  ", p.name)
        return 0

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("缺少依赖 edge-tts。安装：")
        print("  pip install edge-tts")
        raise SystemExit(2)

    args.output.mkdir(parents=True, exist_ok=True)
    ok, failed = [], []

    async def run():
        for i, p in enumerate(files, 1):
            dst = args.output / (p.stem + ".mp3")
            vtt = args.output / (p.stem + ".vtt") if args.subtitle else None
            try:
                text = p.read_text(encoding="utf-8", errors="replace").strip()
                if not text:
                    raise ValueError("文本为空")
                await synth_one(text, args.voice, args.rate, args.pitch, dst, vtt)
                ok.append(p.name)
                print("[%d/%d] ✓ %s" % (i, len(files), p.name))
            except Exception as exc:  # noqa: BLE001
                failed.append((p.name, str(exc)[:140]))
                print("[%d/%d] ✗ %s -> %s" % (i, len(files), p.name, str(exc)[:140]))

    asyncio.run(run())
    print("\n" + "=" * 60)
    print("成功 %d ｜ 失败 %d ｜ 输出目录：%s" % (len(ok), len(failed), args.output))
    if failed:
        for n, e in failed[:20]:
            print("  - %s ： %s" % (n, e))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
