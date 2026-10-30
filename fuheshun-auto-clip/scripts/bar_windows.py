# -*- coding: utf-8 -*-
"""金句条窗口自检 —— 渲前 10 秒跑完，省一次全片白跑

抓三类问题（都是曾踩过的）：
  1) 锚点命中不到（跨句短语：word_time 只在同一个 whisper 段内累积）
  2) 两条窗口重叠（两张大字叠在同一屏）
  3) 单条短于 0.8s 读不完（锚点落在段尾被 clamp 砍短）

用法:
    python bar_windows.py <build.py>
"""
import argparse
import importlib.util


def load(path):
    spec = importlib.util.spec_from_file_location('bt', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('build')
    ap.add_argument('--min', type=float, default=0.8, help='最短可读时长(s)')
    a = ap.parse_args()
    m = load(a.build)

    T = m.build_timeline()
    segs = m.build_segs()
    bars = m.resolve_bars(T, segs)
    cut = m.DUR - 3.60                      # BAR_CUT 之后的条本来就会被砍

    print('=== 锚点命中 ===')
    for row in getattr(m, 'BARS', []):
        cn, en, anchor = row[0], row[1], row[2]
        t = T.get(anchor) or next((T[k] for k in T if anchor in k), None)
        print('  %-6s %-16s anchor=%-14s %s'
              % ('OK' if t else 'MISS', cn, anchor,
                 ('%.2f-%.2f' % t) if t else '→ 命中不到，这条不会出现'))

    print('=== 窗口 ===')
    hook_end = getattr(m, 'HOOK_END', None)
    seq = sorted(bars, key=lambda x: x['s'])
    prev = None
    n_ov = n_short = 0
    for b in seq:
        dur = b['e'] - b['s']
        flag = []
        if b['s'] >= cut:
            flag.append('在 BAR_CUT 之后（渲染时被砍）')
        if prev is not None and b['s'] < prev:
            flag.append('!! 与上一条重叠 %.2fs' % (prev - b['s']))
            n_ov += 1
        if dur < a.min:
            # 钩子段尾的金句条天然短：它和钩子卡是同一句话，观众已经在上面的卡上读过，
            # 这里只是一记"补拍"，短闪是设计不是 bug。
            if hook_end and b['e'] <= hook_end + 0.01:
                flag.append('· 钩子尾条 %.2fs（与钩子卡同句，短闪属设计）' % dur)
            else:
                flag.append('!! 只有 %.2fs，读不完' % dur)
                n_short += 1
        print('  %-16s %6.2f-%6.2f  %.2fs  %s'
              % (b['cn'], b['s'], b['e'], dur, ' | '.join(flag)))
        prev = b['e']

    print()
    if n_ov or n_short:
        print('❌ 重叠 %d 条 / 过短 %d 条 —— 改 BARS 第 3 列（锚点），'
              '注意锚点文本 ≠ 条上显示的字' % (n_ov, n_short))
    else:
        print('✅ 无重叠、无过短')


if __name__ == '__main__':
    main()
