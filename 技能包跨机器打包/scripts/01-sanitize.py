# -*- coding: utf-8 -*-
"""
联网工具箱 · 离线包净化脚本
把源机上的一切机器专属硬编码路径替换为跨机器通用写法。

设计原则：
  1. 技能包自身的路径 -> $HOME/.workbuddy/skills/联网工具箱
     （在 Git Bash 与 PowerShell 下均可展开，且能容忍用户名含空格）
  2. 外部运行时（node / python）-> 走 PATH，不写死托管路径与版本号
  3. 只改 .md / .mjs / .py / .json，不动 node_modules
"""
import pathlib
import sys

ROOT = pathlib.Path(r"D:\桌面\skills\_build_联网工具箱\payload")

# 顺序敏感：长串在前，避免前缀被提前吃掉
RULES = [
    # ---- 技能包自身路径 ----
    ("C:/Users/Matebook/.workbuddy/skills/联网工具箱",
     "$HOME/.workbuddy/skills/联网工具箱"),
    (r"C:\Users\Matebook\.workbuddy\skills\联网工具箱",
     "$HOME/.workbuddy/skills/联网工具箱"),

    # ---- 托管 Node：不写死版本号（源机就有 -2/-3 两个版本并存）----
    ("C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe", "node"),
    ("C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-3/node.exe", "node"),
    ("C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/", "node/"),
    ("C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-3/", "node/"),

    # ---- 托管 Python ----
    ("C:/Users/Matebook/.workbuddy/binaries/python/envs/default/Scripts/python.exe", "python"),
    ("C:/Users/Matebook/.workbuddy/binaries/python/envs/default/bin/python", "python"),
    ("C:/Users/Matebook/.workbuddy/binaries/python/versions/3.13.12/python.exe", "python"),
    ("C:/Users/Matebook/.workbuddy/binaries/python/envs/default/Lib/site-packages",
     "<python>/Lib/site-packages"),
    (r"C:\Users\Matebook\.workbuddy\binaries\python\envs\default\Scripts\python.exe", "python"),

    # ---- 用户级目录 ----
    ("C:/Users/Matebook/Downloads", "$HOME/Downloads"),

    # ---- 源机自研工具（新机器不存在，改指本机等价做法）----
    (r"C:\Users\Matebook\.workbuddy\tools\fix-bash-path.py",
     "$HOME/.workbuddy/tools/fix-bash-path.py"),

    # ---- 收尾兜底：任何漏网的用户目录引用 ----
    (r"C:\Users\Matebook", "$HOME"),
    ("C:/Users/Matebook", "$HOME"),
]

EXTS = {".md", ".mjs", ".js", ".py", ".json", ".txt", ".template", ".env"}
SKIP_DIRS = {"node_modules", ".git"}

changed, scanned, hits = [], 0, []

for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    if any(part in SKIP_DIRS for part in p.parts):
        continue
    if p.suffix.lower() not in EXTS and p.name != "config.env":
        continue

    scanned += 1
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    orig = text
    file_hits = []
    for old, new in RULES:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            file_hits.append((old, n))
    if text != orig:
        p.write_text(text, encoding="utf-8", newline="")
        rel = p.relative_to(ROOT).as_posix()
        changed.append(rel)
        for old, n in file_hits:
            hits.append((rel, old, n))

print(f"扫描文件：{scanned}")
print(f"修改文件：{len(changed)}")
print(f"替换次数：{sum(h[2] for h in hits)}")
print()
for rel, old, n in hits:
    print(f"  [{n}] {rel}\n        <- {old}")

# 复检
print("\n=== 复检：残留 Matebook / 绝对用户路径 ===")
leftover = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
        continue
    if p.suffix.lower() not in EXTS and p.name != "config.env":
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if "Matebook" in text:
        leftover += 1
        for i, line in enumerate(text.splitlines(), 1):
            if "Matebook" in line:
                print(f"  !! {p.relative_to(ROOT).as_posix()}:{i}: {line.strip()[:120]}")
print(f"残留文件数：{leftover}")
