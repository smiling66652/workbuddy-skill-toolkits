#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""单元素出图诊断 —— 改单个版式组件时用，别拿整片验证（整片 20 分钟）。

用法：
  # 1) 逐个 case 出单图
  python debug_component.py <build.py> make_data_bar \
      --json '[{"shot":{...}}, {"shot":{...}}]' --out _db.png

  # 2) 更常用：用一个 Python 表达式生成 cases（--gen）
  python debug_component.py <build.py> make_data_bar \
      --gen "[(dict(num='今夏', unit='真实发生', note='非实验室假设')), \
             (dict(num='-2780', unit='亿美元', note='净现金流'))]" \
      --key num --out _db.png

  --gen 会被 eval（可访问模块里的名字，如 MAT_SEGS / SEGMENTS）；
  --key 指定用哪个字段给输出文件命名/标注。

原理：importlib 加载 build 脚本 → 只调那一个函数 → 拼成一张对比表。
 就是靠这个在几十秒内定位到「数据条汉字漏加 pad 偏移」的，
而整片渲一遍要 20 分钟。
"""
import os
import sys
import json
import argparse
import importlib.util
from PIL import Image, ImageDraw

BG = (16, 18, 24)
LBL = 26


def load_module(path):
    spec = importlib.util.spec_from_file_location('__dbg_build__', path)
    m = importlib.util.module_from_spec(spec)
    sys.modules['__dbg_build__'] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('build')
    ap.add_argument('func')
    ap.add_argument('--json', default='')
    ap.add_argument('--gen', default='')
    ap.add_argument('--key', default='')
    ap.add_argument('--out', default='_dbg.png')
    ap.add_argument('--cols', type=int, default=0)
    a = ap.parse_args()

    m = load_module(os.path.abspath(a.build))
    fn = getattr(m, a.func, None)
    if fn is None:
        print('DONE  !! 模块里没有函数:', a.func)
        return

    if a.gen:
        cases = eval(a.gen, vars(m))
    elif a.json:
        cases = json.loads(a.json)
    else:
        print('DONE  !! 需要 --json 或 --gen')
        return

    # 目标函数可能收「一个 dict」(make_data_bar(shot))，也可能收若干关键字。
    # 用 signature 判，不要一律 **c —— 否则 make_data_bar(**shot) 直接 TypeError。
    import inspect
    ps = [p for p in inspect.signature(fn).parameters.values()
          if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]

    ims, names = [], []
    for i, c in enumerate(cases):
        if isinstance(c, dict) and 'args' in c:
            im = fn(*c['args'], **c.get('kwargs', {}))
        elif isinstance(c, dict):
            im = fn(c) if len(ps) == 1 else fn(**c)
        else:
            im = fn(c)
        if im is None:
            print(f'  [skip] case{i} 返回 None')
            continue
        if isinstance(im, tuple):
            im = im[0]
        ims.append(im if im.mode == 'RGB' else im.convert('RGBA'))
        names.append(str(c.get(a.key, '')) if (a.key and isinstance(c, dict)) else f'case{i}')

    if not ims:
        print('DONE  !! 全部返回 None')
        return

    cols = a.cols or min(len(ims), 4)
    cw = max(i.width for i in ims)
    ch = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (cw + 10) + 10,
                           rows * (ch + LBL) + 10), BG)
    d = ImageDraw.Draw(sh)
    for i, im in enumerate(ims):
        x = 10 + (i % cols) * (cw + 10)
        y = 10 + (i // cols) * (ch + LBL)
        lay = Image.new('RGBA', sh.size, (0, 0, 0, 0))
        lay.alpha_composite(im.convert('RGBA'), (x, y))
        sh = Image.alpha_composite(sh.convert('RGBA'), lay).convert('RGB')
        d = ImageDraw.Draw(sh)
        d.text((x, y + ch + 4), names[i], fill=(210, 220, 240))
    sh.save(a.out)
    print('DONE ->', a.out, sh.size, f'({len(ims)} cases)')


if __name__ == '__main__':
    main()
