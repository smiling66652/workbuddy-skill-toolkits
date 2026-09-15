---
name: techdebt
description: |
  扫描一个代码仓库，找出重复代码、明显坏味道、未使用文件/依赖、TODO/FIXME 堆积、超大文件，输出按严重度排序的清单。
  触发词：技术债、代码坏味道、清理代码、扫描重复代码、找 TODO、tech debt、code smell、重构前的体检
version: "1.0.0"
author: smiling66652
---

# 技术债清理（techdebt）

> 用途：在重构、交付作品集、交作业前，对仓库做一遍“体检”，把债按严重度列出来，每条都给出**文件路径 + 行号 + 为什么是债**，方便逐个销账。

## 适用场景

- 保研作品集 / 课程大作业提交前，想清理冗余代码
- 接手别人的仓库，先摸清哪里最乱
- 周复盘时顺手扫一遍，防止债越积越多
- 配合 `git-ship` 技能，在提交前先做一次轻量体检

## 执行步骤

先在仓库根目录打开 Git Bash，依次跑下面几条命令。所有命令已避开 `node_modules`、`.git`，Windows 路径用正斜杠。

### 1. 超大文件（单文件 > 400 行）

```bash
for ext in py js ts jsx tsx wxml wxss vue go java; do
  find . -type f -name "*.$ext" -not -path "*/node_modules/*" -not -path "*/.git/*" \
    | while read f; do n=$(wc -l < "$f"); [ "$n" -gt 400 ] && echo "$n  $f"; done
done | sort -rn
```

### 2. TODO / FIXME / HACK / XXX 堆积

```bash
rg -n "TODO|FIXME|HACK|XXX|DEPRECATED" --glob "!.git" --glob "!node_modules" \
   -g "*.py" -g "*.js" -g "*.ts" -g "*.wxml" -g "*.wxss" -g "*.vue" -g "*.go" -g "*.java"
```

### 3. 调试残留（上线前必须清掉）

```bash
rg -n "print\(|console\.log\(|pdb|debugger|alert\(" --glob "!.git" --glob "!node_modules" \
   -g "*.py" -g "*.js" -g "*.ts" -g "*.wxml"
```

### 4. 重复代码（复制粘贴坏味道）

用 ripgrep 统计完全相同的行，行数出现 ≥ 3 次且非 import/空行的高概率重复：

```bash
rg -N --glob "!.git" --glob "!node_modules" -g "*.py" -g "*.js" -g "*.ts" \
   -o ".+" | sort | uniq -c | sort -rn | awk '$1>=3{print}'
```

若想精确定位重复块，跑下面这段 Python（直接复制执行）：

```bash
python - <<'PY'
import os, re, hashlib
SKIP = ("node_modules", ".git", "__pycache__", "dist", "build")
EXT = (".py",".js",".ts",".wxml",".wxss",".vue",".go",".java")
hashes={}
for root,dirs,files in os.walk("."):
    dirs[:]=[d for d in dirs if d not in SKIP]
    for f in files:
        if f.endswith(EXT):
            p=os.path.join(root,f)
            try: lines=[l.strip() for l in open(p,encoding="utf-8",errors="ignore") if l.strip() and not l.strip().startswith(("import","from","#","//"))]
            except: continue
            for i in range(len(lines)-4):
                blk="\n".join(lines[i:i+5]); h=hashlib.md5(blk.encode()).hexdigest()
                hashes.setdefault(h,[]).append((p,i+1))
for h,locs in hashes.items():
    if len(locs)>=2:
        print("重复块(5行) 出现 %d 次:"%len(locs))
        for p,ln in locs: print("   %s:%d"%(p,ln))
PY
```

### 5. 未使用依赖（Python / Node）

- Python：对比 `requirements.txt` 顶层包名与代码里 `import` 的顶层模块，对不上的即为疑似未用依赖。
- Node：`package.json` 的 `dependencies` 与代码里 `require/import` 比对；更准的做法跑 `npx depcheck`（需联网安装）。

### 6. 死文件 / 未跟踪冗余

```bash
git status --porcelain | grep "^??"        # 从未纳入版本控制的散落文件
rg -l "" --files-without-match "." --glob "!.git" | head   # 空文件探测见下
find . -type f -empty -not -path "*/.git/*"               # 空文件
```

## 输出格式

把上面结果汇总成一张表，按严重度排序（高→中→低）。格式固定如下：

| 严重度 | 类型 | 文件路径:行号 | 一句话说明 |
|---|---|---|---|
| 高 | 调试残留 | app.py:42 | 残留 print 会泄漏内部状态，上线前必须删 |
| 高 | 超大文件 | utils/helpers.js:1 | 单文件 820 行，应拆分为模块 |
| 中 | TODO 堆积 | api/client.ts:88 | 3 处 TODO 未实现重试逻辑 |
| 中 | 重复代码 | a.py:12 / b.py:30 | 相同 5 行校验逻辑复制两遍 |
| 低 | 未用依赖 | requirements.txt | 装了 `requests` 但代码未 import |

严重度判定参考：高 = 泄露风险 / 编译或运行隐患 / 明显 bug；中 = 可维护性差但暂不致命；低 = 整洁度问题。

## 注意事项

1. 扫描前先 `git pull` 确保看的是最新代码，避免漏报。
2. `node_modules`、`dist` 等产物目录必须排除，否则全是噪音。
3. 第 6 步的“未使用”只是启发式，删除依赖/文件前务必本地跑一遍测试或启动确认。
4. 本技能只负责**列出清单**，不自动改代码；确认无误后再用 `git-ship` 提交清理结果。
5. 微信小程序项目重点看 `*.wxml/*.wxss` 里的重复 wxss 样式块和未使用的 `utils/*.js`。
