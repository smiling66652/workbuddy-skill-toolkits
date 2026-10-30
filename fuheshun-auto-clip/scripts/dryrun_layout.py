# -*- coding: utf-8 -*-
"""干跑全时间轴排版 —— 渲染前第二道自检（约 2 分钟，省一次 20 分钟白跑）

用法:
    python dryrun_layout.py <build.py> [--step 0.25]

不渲视频，按 step 秒步长把整条时间轴上的排版函数全调一遍，并打印逐句字幕。
能提前抓到：未定义名 / 索引越界 / 字体缺字 / 切句把词或数字劈开 /
某段时间 render_subs 返回 None / 素材缺图。

依赖 build 脚本暴露的接口（剪辑1 管线约定，缺哪个就跳过哪步）：
    SEGMENTS FIX build_units build_sentences render_subs clean
    DUR FPS W H seg_at shot_of mat_layout chap_card render_hook render_endcard
    build_segs build_timeline resolve_bars resolve_img
    make_shades make_vignette make_soft_floor make_text_card grad_for
    TOP_SHADE BOT_SHADE VIG SOFT_FLOOR  (将被本脚本写入)
"""
import argparse, importlib.util, os, sys
from PIL import Image


def load(path):
    spec = importlib.util.spec_from_file_location('bt', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('build')
    ap.add_argument('--step', type=float, default=0.25)
    a = ap.parse_args()
    m = load(a.build)

    # 模块级缓存（render() 里本来会建，这里替它建）
    for nm, fn in (('TOP_SHADE', None), ('BOT_SHADE', None)):
        pass
    if hasattr(m, 'make_shades'):
        m.TOP_SHADE, m.BOT_SHADE = m.make_shades()
    if hasattr(m, 'make_vignette'):
        m.VIG = m.make_vignette()
    if hasattr(m, 'make_soft_floor'):
        m.SOFT_FLOOR = m.make_soft_floor()

    segs = m.build_segs()
    T = m.build_timeline() if hasattr(m, 'build_timeline') else {}
    bars = m.resolve_bars(T, segs) if hasattr(m, 'resolve_bars') else []
    if bars and hasattr(m, 'make_text_card'):
        for b in bars:
            b['card'] = m.make_text_card(
                b['cn'], b['en'], b['border'], cn_size=b['size'],
                cn_grad=m.grad_for(b['border']) if b.get('grad') else None)

    IMG = {}
    for g in segs:
        if g['kind'] != 'mat':
            continue
        for sh in g['shots']:
            if sh['key'] in IMG:
                continue
            p = m.resolve_img(sh['key']) if hasattr(m, 'resolve_img') else None
            if not p:
                print(f'  !! 缺素材 {sh["key"]}')
            IMG[sh['key']] = Image.open(p).convert('RGB') if p else None

    print('=== 逐句字幕（去重）===')
    n = int(m.DUR * m.FPS)
    step = max(1, int(a.step * m.FPS))
    seen = set()
    none_at = []
    for idx in range(0, n, step):
        t = idx / m.FPS
        try:
            sub = m.render_subs(t)
        except Exception as e:
            print(f'  !! t={t:.2f} render_subs {type(e).__name__}: {e}')
            continue
        if sub is None:
            none_at.append(t)
            continue
        seg = None
        for s in m.SEGMENTS:
            if s['start'] <= t < s['end']:
                seg = s
                break
        if seg is None:
            continue
        chars = []
        for w in seg['words']:
            ws = w['w']
            if not ws:
                continue
            stp = (w['e'] - w['s']) / len(ws)
            for i, ch in enumerate(ws):
                chars.append((ch, w['s'] + i * stp, w['s'] + (i + 1) * stp))
        txt = ''.join(c[0] for c in chars)
        # ⚠️ 不要在这里再跑一遍 FIX/clean：SEGMENTS 的词在构建时已经过 _apply_fix，
        # 二次纠错会把**不等长**规则应用两次（实测 raw「往 前 挪 一」→ 已经变成
        # 「往前挪一步」，再纠一次就成了「往前挪一步步」），干跑报的是假问题。
        # 等长规则（煞车→刹车）看不出差别，所以这个坑一直藏着。详见 SKILL §G⑧。
        toks = list(chars)
        for s in m.build_sentences(m.build_units(toks)):
            k = ''.join(x[0] for x in s)
            if k and k not in seen:
                seen.add(k)
                print(f'  [{s[0][1]:6.2f}] {len(k):2d}字  {k}')
    if none_at:
        print(f'  （{len(none_at)} 个采样点无字幕，即 whisper 段间静默：'
              + ', '.join(f'{x:.2f}' for x in none_at[:14]) + ' …）')

    print('=== 全时间轴排版函数干跑 ===')
    errs = 0
    for idx in range(0, n, step):
        t = idx / m.FPS
        seg = m.seg_at(segs, t)
        try:
            if seg['kind'] == 'mat':
                m.mat_layout(t, seg, m.shot_of(seg, t), IMG)
            else:
                if t < getattr(m, 'HOOK_END', 6.30) and hasattr(m, 'render_hook'):
                    m.render_hook(t)
                if hasattr(m, 'chap_card'):
                    m.chap_card(t, 1.0)
            if hasattr(m, 'render_endcard'):
                m.render_endcard(t, m.DUR - 3.50)
        except Exception as e:
            errs += 1
            if errs < 8:
                print(f'  !! t={t:.2f} {seg["kind"]} {type(e).__name__}: {e}')
    print(f'  干跑完成，异常 {errs} 处')

    print('=== 每张卡单独过一遍 ===')
    for g in segs:
        if g['kind'] != 'mat':
            continue
        for sh in g['shots']:
            for attr, nm in (('make_title_bar', 'title'), ('make_data_bar', 'data')):
                fn = getattr(m, attr, None)
                if not fn:
                    continue
                try:
                    fn(sh)
                except Exception as e:
                    print(f'  !! {nm} {sh["key"]} {type(e).__name__}: {e}')
    print('DONE')


if __name__ == '__main__':
    main()
