# -*- coding: utf-8 -*-
r"""
第二轮净化：修正 $HOME 在 Git Bash 下的失效问题。

背景（实测）：
    node "$HOME/.workbuddy/skills/联网工具箱/scripts/doctor.mjs"
  -> Git Bash 把 $HOME 展开为 /c/Users/Matebook/...
  -> node.exe 是原生 Windows 程序，把该 MSYS 路径解释为 d:\c\Users\...
  -> Error: Cannot find module 'd:\c\Users\Matebook\...'

方案：
  1. 技能内路径 -> 相对路径（基准 = 技能根目录），由 SKILL.md 的「路径约定」约束
  2. 技能外路径 -> $USERPROFILE/...（实测在 Git Bash 下可正确传给原生程序）
"""
import pathlib

ROOT = pathlib.Path(r"D:\桌面\skills\_build_联网工具箱\payload")

PREFIX = "$HOME/.workbuddy/skills/联网工具箱"

RULES = [
    (PREFIX + "/", ""),                       # 技能内 -> 相对路径
    (PREFIX, "."),                            # 剩余（如 cd 到技能根目录）
    ("$HOME/.workbuddy/", "$USERPROFILE/.workbuddy/"),
    ("$HOME/Downloads", "$USERPROFILE/Downloads"),
    ("$HOME`", "$USERPROFILE`"),
]

EXTS = {".md", ".mjs", ".js", ".py", ".json", ".txt", ".template"}
SKIP = {"node_modules", ".git"}

changed = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or any(x in p.parts for x in SKIP):
        continue
    if p.suffix.lower() not in EXTS and p.name != "config.env":
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    o = t
    for old, new in RULES:
        t = t.replace(old, new)
    if t != o:
        p.write_text(t, encoding="utf-8", newline="")
        changed.append(p.relative_to(ROOT).as_posix())

print(f"修改文件：{len(changed)}")
for c in changed:
    print("   ", c)

print("\n=== 复检：残留 $HOME / 绝对用户路径 ===")
bad = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or any(x in p.parts for x in SKIP):
        continue
    if p.suffix.lower() not in EXTS and p.name != "config.env":
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for i, line in enumerate(t.splitlines(), 1):
        if "$HOME" in line or "Matebook" in line:
            bad += 1
            print(f"  !! {p.relative_to(ROOT).as_posix()}:{i}: {line.strip()[:110]}")
print(f"残留：{bad}")
