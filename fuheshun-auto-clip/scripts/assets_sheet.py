#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把抓来的素材目录拼成联系表 —— 素材目检必用，不要只看文件名。

用法：
  python assets_sheet.py <assets根> --cats a_google,a_ai,a_hack --cols 4
  python assets_sheet.py <assets根>                 # 全部类
  python assets_sheet.py <某个类目录> --one         # 单个类，大图模式
  python assets_sheet.py <assets根> --out chk.png --cell 240x170

为什么必须有这一步：纯数值打分（宽高比/亮度/对比度）挑出来的图里出现过
素材店水印、招生广告、别人的身份证截图；更严重的是  搜「红色警报 屏幕」
返回的 8 张**全是政治宣传图**——这类只能靠眼睛看，不能靠分数。

判据是「这张图配上这句文案，观众会不会误读」，不是好不好看。
"""
import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

EXT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')


def load(p, cell):
    try:
        im = Image.open(p).convert('RGB')
        im.thumbnail(cell, Image.LANCZOS)
        return im
    except Exception:
        bad = Image.new('RGB', cell, (70, 20, 20))
        d = ImageDraw.Draw(bad)
        d.text((8, 8), 'BROKEN', fill=(255, 200, 200))
        return bad


def grid(cats_root, cats, cols, cell, out, title_fn):
    cw, ch = cell
    LBL = 22
    sheets = []
    for cat in cats:
        d = os.path.join(cats_root, cat)
        fs = sorted(f for f in os.listdir(d) if f.lower().endswith(EXT))
        if not fs:
            continue
        rows = (len(fs) + cols - 1) // cols
        sh = Image.new('RGB', (cols * (cw + 6) + 6, rows * (ch + LBL) + 6), (20, 22, 28))
        dr = ImageDraw.Draw(sh)
        for i, f in enumerate(fs):
            im = load(os.path.join(d, f), cell)
            x = 6 + (i % cols) * (cw + 6)
            y = 6 + (i // cols) * (ch + LBL)
            sh.paste(im, (x + (cw - im.width) // 2, y))
            dr.text((x + 2, y + ch + 3), title_fn(cat, f), fill=(205, 215, 235))
        sheets.append((cat, len(fs), sh))

    if not sheets:
        print('没有可用图片')
        return
    W = max(s[2].width for s in sheets)
    H = sum(s[2].height + 30 for s in sheets) + 10
    out_im = Image.new('RGB', (W + 12, H), (12, 14, 20))
    dr = ImageDraw.Draw(out_im)
    y = 8
    for cat, n, sh in sheets:
        dr.text((6, y), f'[{cat}]  {n} 张', fill=(255, 200, 90))
        out_im.paste(sh, (6, y + 20))
        y += sh.height + 30
    out_im.save(out)
    print('DONE ->', out, out_im.size)
    for cat, n, _ in sheets:
        print(f'  {cat:16s} {n}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--cats', default='')
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--cell', default='240x170')
    ap.add_argument('--out', default='_assets_sheet.png')
    ap.add_argument('--one', action='store_true', help='root 本身就是单个类目录')
    ap.add_argument('--full', action='store_true', help='文件名显示为 类/文件')
    a = ap.parse_args()

    cw, ch = (int(x) for x in a.cell.lower().split('x'))

    if a.one:
        cats = [os.path.basename(a.root.rstrip('/\\'))]
        root = os.path.dirname(a.root.rstrip('/\\'))
    else:
        root = a.root
        cats = [c for c in a.cats.split(',') if c.strip()] if a.cats else \
            sorted(d for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root, d)) and not d.startswith(('_', '.')))

    grid(root, cats, a.cols, (cw, ch), a.out,
         (lambda c, f: f'{c}/{f}') if a.full else (lambda c, f: f))


if __name__ == '__main__':
    main()
