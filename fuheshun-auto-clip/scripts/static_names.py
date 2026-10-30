# -*- coding: utf-8 -*-
"""静态扫未定义全局名 —— 渲染前第一道自检（几秒，省一次 20 分钟白跑）

用法:
    python static_names.py <build.py>

真实案例（）：
    fork 出来的 build 脚本里 render_subs() 用了字典 `FIX`，**而它从未被定义**
    （只有 `FIX_LIST` 列表）。上一版之所以没崩，只因为那版改词表一条都没命中
    字幕原文、`else` 分支从没执行到；换文案后第一次命中，跑到 t=50s 才抛
    `NameError`，11 分钟渲染白费。

说明:
    这是**保守近似**检查器：不建完整的词法作用域树，用"本函数局部 + 祖先闭包
    + 嵌套函数形参"近似代替。目标名（如 `FIX`）从未在任何地方定义，
    所以任何近似都不会把它放过。

    它**能**正确处理：模块级定义、闭包变量、嵌套函数形参、lambda 形参、
    comprehension 目标、except ... as、import 别名。
    可能漏报的只有"函数 A 误用一个只在函数 B 内定义的名字"这种罕见错法
    —— 这类会在 dryrun_layout.py 里当场炸出来，不必靠静态扫。

用法:
    输出的名单应**逐条人工确认**；若出现真实未定义名，先补定义再渲染。
"""
import ast, builtins, io, sys


def main(path):
    src = io.open(path, encoding='utf-8').read()
    tree = ast.parse(src)

    mod = set(dir(builtins))
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            mod.add(n.name)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        mod.add(x.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                mod.add((a.asname or a.name).split('.')[0])
        elif isinstance(n, (ast.For, ast.Try, ast.If, ast.While)):
            for x in ast.walk(n):
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store):
                    mod.add(x.id)

    # 记录每个函数的祖先函数链：闭包变量来自祖先作用域，必须一并算作"已定义"
    parents = {}

    def walk(node, stack):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parents[ch] = list(stack)
                walk(ch, stack + [ch])
            else:
                walk(ch, stack)

    walk(tree, [])

    def own_locals(fn):
        loc = {a.arg for a in list(fn.args.args) + list(fn.args.kwonlyargs)}
        if fn.args.vararg:
            loc.add(fn.args.vararg.arg)
        if fn.args.kwarg:
            loc.add(fn.args.kwarg.arg)
        for x in ast.walk(fn):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store):
                loc.add(x.id)
            elif isinstance(x, (ast.Import, ast.ImportFrom)):
                for a in x.names:
                    loc.add((a.asname or a.name).split('.')[0])
            elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef,
                                ast.ClassDef)) and x is not fn:
                loc.add(x.name)
                # 嵌套函数的**参数**必须一并收：ast.walk 已经走进了它的函数体，
                # 所以它的形参会以 Load 形式出现在本函数的扫描范围里。
                #  实测：`def _big(dr, fill=255)` 的 dr/fill 被误报成
                # "在 make_data_bar() 中未定义"——就是漏了这一步。
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for a in (list(x.args.args) + list(x.args.posonlyargs)
                              + list(x.args.kwonlyargs)):
                        loc.add(a.arg)
                    for a in (x.args.vararg, x.args.kwarg):
                        if a:
                            loc.add(a.arg)
            elif isinstance(x, ast.ExceptHandler) and x.name:
                loc.add(x.name)
            elif isinstance(x, ast.comprehension):
                for y in ast.walk(x.target):
                    if isinstance(y, ast.Name):
                        loc.add(y.id)
            elif isinstance(x, ast.Lambda):
                for a in list(x.args.args) + list(x.args.kwonlyargs):
                    loc.add(a.arg)
                if x.args.vararg:
                    loc.add(x.args.vararg.arg)
                if x.args.kwarg:
                    loc.add(x.args.kwarg.arg)
        return loc

    bad = []
    for fn in [n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        local = set()
        for anc in parents.get(fn, []):
            local |= own_locals(anc)          # 闭包：祖先作用域可见
        local |= own_locals(fn)
        g = set()
        for x in ast.walk(fn):
            if isinstance(x, ast.Global):
                g.update(x.names)
        for x in ast.walk(fn):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
                if x.id not in local and x.id not in mod and x.id not in g:
                    bad.append((fn.name, x.id, x.lineno))

    seen, n = set(), 0
    for f, nm, ln in sorted(bad, key=lambda z: z[2]):
        if (f, nm) in seen:
            continue
        seen.add((f, nm))
        n += 1
        print(f'  可疑未定义  {nm}  在 {f}()  行 {ln}')
    print(f'--- {n} 条可疑（含闭包误报，人工扫一眼）---' if n
          else '--- 未发现未定义全局名 ---')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'build.py')
