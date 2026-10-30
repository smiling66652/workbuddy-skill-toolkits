# -*- coding: utf-8 -*-
"""剪辑1 · 目检抽帧（看图是本模型第一验证手段，Read 直接支持 PNG/JPG）

用法:
    python contact_sheet.py <成片.mp4> out.png --every 4 --cols 6
    python contact_sheet.py <成片.mp4> out.png --ts 0,0.1,0.2,0.33,0.5,0.7,1.0
    python contact_sheet.py <成片.mp4> out.png --from 79.6 --to 85 --step 0.6

技巧:
    - 接触表看全片版式一致性；单点拼条看首尾。
    - 加 --luma 同时输出每帧平均亮度：0.5s 后仍 <30 = 黑屏 bug（0.2s 内升到 60 属正常淡入）。
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

FF = shutil.which('ffmpeg')
FP = shutil.which('ffprobe')
TW, TH = 150, 267          # 1080x1920 等比缩略
PAD = 16


def probe_dur(v):
    """取时长：优先 ffprobe；同目录没有就走 ffmpeg -f null 解析。"""
    if os.path.exists(FP):
        r = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=nw=1:nk=1', v], capture_output=True, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            pass
    r = subprocess.run([FF, '-i', v, '-f', 'null', '-'], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    for line in r.stderr.splitlines():
        if 'Duration:' in line:
            hms = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = hms.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f'无法取得时长: {v}')


def arg(name, default=None, cast=float):
    if name in sys.argv:
        return cast(sys.argv[sys.argv.index(name) + 1])
    return default


def main():
    v, out = sys.argv[1], sys.argv[2]
    if '--ts' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--ts') + 1].split(',') if x.strip()]
    else:
        every = arg('--every', 4.0)
        t0 = arg('--from', 0.0)
        t1 = arg('--to', None)
        if t1 is None:
            t1 = probe_dur(v)
        step = arg('--step', every)
        ts, t = [], t0
        while t <= t1 + 1e-6:
            ts.append(round(t, 3))
            t += step
    cols = int(arg('--cols', 6, int))
    luma = '--luma' in sys.argv

    d = tempfile.mkdtemp()
    p = os.path.join(d, 'f.png')
    rows = (len(ts) + cols - 1) // cols
    tw = TH * 1080 // 1920
    sheet = Image.new('RGB', (cols * tw, rows * (TH + PAD)), 'white')
    dr = ImageDraw.Draw(sheet)
    try:
        for i, t in enumerate(ts):
            subprocess.run([FF, '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', v,
                            '-frames:v', '1', '-update', '1', p], check=True)
            im = Image.open(p).convert('RGB')
            sheet.paste(im.resize((tw, TH)), ((i % cols) * tw, (i // cols) * (TH + PAD)))
            dr.rectangle([(i % cols) * tw, (i // cols) * (TH + PAD) + TH,
                          (i % cols + 1) * tw, (i // cols) * (TH + PAD) + TH + PAD], fill='black')
            dr.text(((i % cols) * tw + 3, (i // cols) * (TH + PAD) + 2), f'{t:g}s', fill='white')
            if luma:
                g = im.convert('L').resize((60, 107))
                px = list(g.get_flattened_data()) if hasattr(g, 'get_flattened_data') else list(g.getdata())
                print(f'  t={t:7.2f}s  平均亮度={sum(px)/len(px):6.2f}')
        sheet.save(out)
        print(f'OK {out}  {sheet.size}  帧数={len(ts)}')
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    main()
