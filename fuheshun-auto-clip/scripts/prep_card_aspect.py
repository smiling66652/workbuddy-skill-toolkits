# -*- coding: utf-8 -*-
"""素材预裁：按素材卡比例裁好 + 上偏切掉底部水印带（详见 SKILL §D4）

为什么要有这一步：
  * 素材卡是固定比例 908×652（1.3926），原图各种比例都要 cover_crop，
    底部角标（什么值得买 / 123RF / 小红书 / 知乎@xxx / iMore / GDS）会留在画面里。
  * 预裁后 cover_crop 变成**纯缩放**，Ken Burns 不再漂移，画面更稳。

用法:
    python prep_card_aspect.py <src_file> <dst_file> [--trim 0.14] [--long 1362]
    python prep_card_aspect.py <src_dir>  <dst_dir>  [--trim 0.14] [--long 1362]
    python prep_card_aspect.py <src_dir>  <dst_dir>  --pair picks.json

`picks.json` 形如 {"a_vm/a_vm_01.jpg": "a_vm/a_vm_d07.jpg"}（目标名 -> 候选名），
用于「候选池 -> 定稿路径」的映射落地；不带 --pair 时按同名复制。
原文件若已存在于目标位置，会先备份到 <dst>/../_rejected_assets/watermark/ 下。
"""
import argparse, json, os, shutil, sys
from PIL import Image

AR = 908 / 652.0


def crop_to_card(im, trim=0.14):
    w, h = im.size
    h_avail = int(h * (1 - trim))
    w_need = int(h_avail * AR)
    if w_need <= w:
        x0 = (w - w_need) // 2
        box = (x0, 0, x0 + w_need, h_avail)
    else:
        cw = w
        ch = int(cw / AR)
        if ch > h_avail:
            ch, cw = h_avail, int(h_avail * AR)
        y0 = int((h - ch) * 0.12)
        x0 = (w - cw) // 2
        box = (x0, y0, x0 + cw, y0 + ch)
    return im.crop(box)


def do_one(sp, tp, long_edge, trim, rej):
    if not os.path.isfile(sp):
        print('  !! 缺源文件', sp)
        return False
    im = Image.open(sp).convert('RGB')
    out = crop_to_card(im, trim)
    sc = long_edge / out.width
    out = out.resize((long_edge, max(1, int(out.height * sc))), Image.LANCZOS)
    os.makedirs(os.path.dirname(tp) or '.', exist_ok=True)
    if os.path.isfile(tp) and rej:
        os.makedirs(rej, exist_ok=True)
        bp = os.path.join(rej, os.path.basename(tp))
        if not os.path.isfile(bp):
            shutil.copy2(tp, bp)
    out.save(tp, quality=93)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--trim', type=float, default=0.14)
    ap.add_argument('--long', type=int, default=1362)
    ap.add_argument('--pair', default=None)
    ap.add_argument('--no-backup', action='store_true')
    a = ap.parse_args()

    rej = None if a.no_backup else os.path.join(os.path.dirname(os.path.abspath(a.dst)),
                                                '_rejected_assets', 'watermark')
    n = 0
    if a.pair:
        picks = json.load(open(a.pair, encoding='utf-8'))
        for tgt, src in picks.items():
            if do_one(os.path.join(a.src, src), os.path.join(a.dst, tgt),
                      a.long, a.trim, rej):
                n += 1
                print('  %-34s <- %s' % (tgt, src))
    elif os.path.isdir(a.src):
        for root, _ds, fs in os.walk(a.src):
            for f in sorted(fs):
                if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    continue
                rel = os.path.relpath(os.path.join(root, f), a.src)
                if do_one(os.path.join(root, f), os.path.join(a.dst, rel),
                          a.long, a.trim, rej):
                    n += 1
    else:
        if do_one(a.src, a.dst, a.long, a.trim, rej):
            n += 1
    print('PREP', n)


if __name__ == '__main__':
    main()
