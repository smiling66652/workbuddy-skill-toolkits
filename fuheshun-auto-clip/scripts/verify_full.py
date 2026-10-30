# -*- coding: utf-8 -*-
"""剪辑1 · 全片核验（一次性抽帧，几秒跑完；不要逐次 -ss，会超时）

用法:
    python verify_full.py <成片.mp4>                        # 运动量 + 虚化连续性
    python verify_full.py <成片.mp4> --mat "8.62,12.20,..." # 额外把跳变点与素材边界对比

输出:
    运动量曲线（每 5s 均值 / 最小）、定格判定、虚化跳变点、跳变点是否落在素材边界
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageFilter, ImageStat

FF = shutil.which('ffmpeg')

MO_FPS = 2.0          # 运动量采样帧率
BG_FPS = 5.0          # 虚化采样帧率
BG_ROI = (0, 250, 150, 1750)   # 左侧竖条：避开头像(x270-810)/条(居中)/字幕(居中)
MO_SCALE = (270, 480)

FREEZE_TH = 0.8       # 运动量 < 此值判"定格"
BG_JUMP_TH = 0.8      # 背景细节 Δ/低值 > 此值报警（素材切换点本身 Δ≈4，属设计内）


def extract(v, fps, pattern_dir, scale=None):
    os.makedirs(pattern_dir, exist_ok=True)
    vf = f'fps={fps}' + (f',scale={scale[0]}:{scale[1]}' if scale else '')
    subprocess.run([FF, '-y', '-v', 'error', '-i', v, '-vf', vf,
                    os.path.join(pattern_dir, 'f%05d.png')], check=True)
    return sorted(f for f in os.listdir(pattern_dir) if f.endswith('.png'))


def motion(v):
    d = tempfile.mkdtemp()
    try:
        files = extract(v, MO_FPS, d, MO_SCALE)
        ims = [Image.open(os.path.join(d, f)).convert('L') for f in files]
        ds = [(i / MO_FPS,
               ImageStat.Stat(ImageChops.difference(ims[i], ims[i - 1])).mean[0])
              for i in range(1, len(ims))]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if not ds:
        print('[运动量] 抽帧失败')
        return []
    vals = [x[1] for x in ds]
    print(f'[运动量] 帧数 {len(ims)} fps={MO_FPS}  均值={sum(vals)/len(vals):.2f}  最小={min(vals):.2f}')
    bad = [(t, x) for t, x in ds if x < FREEZE_TH]
    if bad:
        print(f'  !! 疑似定格 {len(bad)} 处（阈值 {FREEZE_TH}）:')
        for t, x in bad[:20]:
            print(f'     {t:6.2f}s  运动量={x:5.2f}')
    else:
        print(f'  OK 无定格（全部 >= {FREEZE_TH}）')
    print('  每 5s:')
    dmax = max(1, int(ds[-1][0]))
    for s in range(0, dmax, 5):
        xs = [x for t, x in ds if s <= t < s + 5]
        if xs:
            print(f'    {s:3d}-{s+5:3d}s  均值={sum(xs)/len(xs):6.2f}  最小={min(xs):6.2f}')
    return ds


def bg(v):
    d = tempfile.mkdtemp()
    try:
        files = extract(v, BG_FPS, d)
        rows = []
        for i, f in enumerate(files):
            g = Image.open(os.path.join(d, f)).convert('L')
            e = g.crop(BG_ROI).filter(ImageFilter.FIND_EDGES)
            px = list(e.get_flattened_data()) if hasattr(e, 'get_flattened_data') else list(e.getdata())
            rows.append((i / BG_FPS, sum(px) / len(px)))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if not rows:
        print('[虚化] 抽帧失败')
        return []
    lo = max(1.0, min(e for _, e in rows))
    jumps = [(rows[i - 1][0], rows[i][0], abs(rows[i][1] - rows[i - 1][1]) / lo)
             for i in range(1, len(rows))]
    hard = [j for j in jumps if j[2] > BG_JUMP_TH]
    print(f'[虚化] 帧数 {len(rows)} fps={BG_FPS} ROI={BG_ROI}  报警跳变 {len(hard)}/{len(jumps)}')
    for a, b, x in hard:
        print(f'     {a:6.2f} -> {b:6.2f}   Δ={x:.2f}')
    return hard


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    v = sys.argv[1]
    mat = None
    if '--mat' in sys.argv:
        mat = [float(x) for x in sys.argv[sys.argv.index('--mat') + 1].split(',') if x.strip()]
    print(f'=== {os.path.basename(v)} ===')
    motion(v)
    print()
    hard = bg(v)
    if mat and hard:
        print('\n--- 跳变点归类 ---')
        print('    素材切换边界 Δ≈2~5；bw 虚化曲线过渡 Δ≈0.8~1.2；连续硬闪才会 >1.2 且不在边界')
        print('    注: 0.00->0.20 恒定误报（开场淡入），属正常')
        for a, b, x in hard:
            hit = [m for m in mat if abs(m - b) < 0.3]
            if hit:
                tag = f'素材边界 {hit[0]:g} → 设计内硬切，忽略'
            elif x < 1.3:
                tag = '非边界但 Δ<1.3 → 虚化曲线过渡，正常'
            else:
                tag = '★ 非边界且 Δ 大 → 必须回看该帧'
            print(f'  {a:6.2f}->{b:6.2f}  Δ={x:5.2f}  {tag}')


if __name__ == '__main__':
    main()
