# -*- coding: utf-8 -*-
"""水印条带终检 —— 定稿素材的底部/顶部条带联系表

为什么不能靠缩略图：素材店/自媒体角标（什么值得买、123RF、小红书、知乎@xxx、iMore）
在缩略图上看不出来，但**截条带按原始像素宽展示**时一眼就能看到。

用法:
    python wm_strip_audit.py <assets_dir> --files a_vm/a_vm_01.jpg,a_pay/a_pay_01.jpg
    python wm_strip_audit.py <assets_dir> --cat a_vm --cat a_pay --per 7
    python wm_strip_audit.py <assets_dir> --all --per 7

输出 `_wm_strip_<n>.png`（每批一张），用 Read 打开目检。
"""
import argparse, os
from PIL import Image, ImageDraw

TB, BB = 0.12, 0.22        # 取上 12% + 下 22%
W = 700


def build(root, files, out):
    BH, BBH = int(W * TB), int(W * BB)
    CELLH = BH + BBH + 18 + 26 + 10
    PAD = 8
    cv = Image.new('RGB', (PAD + W + PAD, PAD + len(files) * (CELLH + PAD)), (20, 20, 24))
    d = ImageDraw.Draw(cv)
    for i, rel in enumerate(files):
        p = rel if os.path.isabs(rel) else os.path.join(root, rel)
        if not os.path.isfile(p):
            print('  !! 缺文件', p)
            continue
        im = Image.open(p).convert('RGB')
        w0, h0 = im.size
        top = im.crop((0, 0, w0, max(1, int(h0 * TB)))).resize((W, BH), Image.LANCZOS)
        bot = im.crop((0, h0 - max(1, int(h0 * BB)), w0, h0)).resize((W, BBH), Image.LANCZOS)
        y = PAD + i * (CELLH + PAD)
        d.text((PAD + 2, y), '%02d %s   %dx%d' % (i + 1, os.path.basename(rel), w0, h0),
               fill=(240, 240, 246))
        cv.paste(top, (PAD, y + 18))
        cv.paste(bot, (PAD, y + 18 + BH + 6))
        d.rectangle([PAD, y + 18 + BH + 6, PAD + W, y + 18 + BH + 6 + BBH],
                    outline=(120, 120, 130))
    cv.save(out)
    print('->', out, cv.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--files', default='')
    ap.add_argument('--cat', action='append', default=[])
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--per', type=int, default=7)
    ap.add_argument('--outdir', default='.')
    a = ap.parse_args()

    if a.files:
        files = [x.strip() for x in a.files.split(',') if x.strip()]
    else:
        cats = a.cat
        if a.all:
            cats = sorted(x for x in os.listdir(a.root)
                          if os.path.isdir(os.path.join(a.root, x)))
        files = []
        for c in cats:
            d = os.path.join(a.root, c)
            if not os.path.isdir(d):
                continue
            files += [os.path.join(c, f) for f in sorted(os.listdir(d)) if f.endswith('.jpg')]
    for k in range(0, len(files), a.per):
        build(a.root, files[k:k + a.per],
              os.path.join(a.outdir, '_wm_strip_%d.png' % k))
    print('共 %d 张' % len(files))


if __name__ == '__main__':
    main()
