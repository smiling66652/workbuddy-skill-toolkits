# -*- coding: utf-8 -*-
r"""
第三轮净化：清理源机专属的 D 盘工作路径。

分两类处理：
  1. 代码里的运行时默认值 -> 改为 os.homedir() 动态推导（真正影响能否运行）
  2. 文档/注释里的命令示例 -> 改为 $USERPROFILE 形式
"""
import pathlib

ROOT = pathlib.Path(r"D:\桌面\skills\_build_联网工具箱\payload")

RULES = [
    # --- 1. 代码默认值：动态推导，跨机器自适应 ---
    ("getArg('download-dir', 'D:/桌面/电子书/_downloads')",
     "getArg('download-dir', path.join(os.homedir(), 'Downloads', 'ebooks'))"),

    # --- 2. 文档与注释中的示例 ---
    ("D:/桌面/电子书/_downloads", "$USERPROFILE/Downloads/ebooks"),
    (r"D:\桌面\电子书\_downloads", "$USERPROFILE/Downloads/ebooks"),
    ("D:/桌面/浏览器/yuketang-research", "<你的输出目录>"),
    ("D:/_tmp_/cdp", "$USERPROFILE/cdp-work"),
    ('"@D:/绝对路径"', '"@<绝对路径>"'),
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

# 验证代码默认值已改为动态推导
print("\n=== 验证 downloadDir 默认值 ===")
for f in ["annas-archive-download.mjs", "archiveorg-download.mjs",
          "archiveorg-find.mjs", "archiveorg-search-download.mjs"]:
    fp = ROOT / "scripts" / f
    for line in fp.read_text(encoding="utf-8").splitlines():
        if "downloadDir = getArg" in line:
            print(f"   {f}: {line.strip()}")

print("\n=== 复检：残留 D 盘工作路径 ===")
bad = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or any(x in p.parts for x in SKIP):
        continue
    if p.suffix.lower() not in EXTS:
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for i, line in enumerate(t.splitlines(), 1):
        if "D:/桌面" in line or "D:\\桌面" in line or "_tmp_" in line:
            bad += 1
            print(f"  !! {p.relative_to(ROOT).as_posix()}:{i}: {line.strip()[:110]}")
print(f"残留：{bad}（纯路径示例如 D:/a.png 属正常，不计入）")
