# -*- coding: utf-8 -*-
"""
模拟「新电脑」执行 install.bat 的端到端测试。

安全设计：USERPROFILE 被覆盖到隔离目录 D:\\_nt_test\\fakehome，
因此绝不会碰到真实的 C:\\Users\\Matebook\\.workbuddy\\skills\\联网工具箱。
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

TEST = Path(r"D:\_nt_test")
ZIP = Path(r"D:\桌面\skills\联网工具箱-离线安装包.zip")

# 每次测试前清空并从最终 zip 重新解压，确保测的就是交付物本身
if TEST.exists():
    shutil.rmtree(TEST)
(TEST / "extract").mkdir(parents=True)
with zipfile.ZipFile(ZIP) as zf:
    zf.extractall(TEST / "extract")
print(f"[准备] 已从 {ZIP.name} 解压到 {TEST / 'extract'}\n")

PKG = TEST / "extract" / "联网工具箱-离线安装包"
BAT = PKG / "install.bat"
FAKE_HOME = TEST / "fakehome"
FAKE_TMP = TEST / "tmp"
DEST = FAKE_HOME / ".workbuddy" / "skills" / "联网工具箱"

FAKE_HOME.mkdir(parents=True, exist_ok=True)
FAKE_TMP.mkdir(parents=True, exist_ok=True)

print("=" * 66)
print("0. install.bat 编码校验（GBK 读回）")
print("=" * 66)
raw = BAT.read_bytes()
try:
    text = raw.decode("gbk")
    print("[OK] 可按 GBK 解码，cmd 下中文将正常显示")
    for line in text.splitlines():
        if "错误" in line or "安装完成" in line:
            print("     ", line.strip()[:70])
            break
except UnicodeDecodeError as e:
    print("[XX] GBK 解码失败：", e)
    sys.exit(1)

print()
print("=" * 66)
print("1. 执行 install.bat（USERPROFILE 隔离到 fakehome）")
print("=" * 66)

env = dict(os.environ)
env["USERPROFILE"] = str(FAKE_HOME)
env["TEMP"] = str(FAKE_TMP)
env["TMP"] = str(FAKE_TMP)

proc = subprocess.run(
    ["cmd", "/c", str(BAT)],
    env=env,
    input=b"\r\n",
    capture_output=True,
    timeout=420,
)

# 输出是 GBK(前半) 与 UTF-8(doctor 段) 混合，宽松解码后只挑关键行
out = proc.stdout.decode("utf-8", errors="replace")
out_gbk = proc.stdout.decode("gbk", errors="replace")


def pick(text, marks):
    for line in text.splitlines():
        s = line.strip()
        if any(m in s for m in marks):
            print("   ", s[:100])


print("--- 关键输出（GBK 解码）---")
pick(out_gbk, ["[1/5]", "[2/5]", "[3/5]", "[4/5]", "[5/5]",
               "已找到 Node", "完成", "全新安装", "错误", "警告", "已随包附带"])

print()
print("=" * 66)
print("2. 安装结果核验")
print("=" * 66)
print(f"目标目录：{DEST}")
print(f"存在：{'是' if DEST.exists() else '否  <<< 失败'}")

if not DEST.exists():
    print("\n--- 完整输出（GBK）---")
    print(out_gbk[:3000])
    sys.exit(1)

must = [
    "SKILL.md", "config.env", "package.json",
    "scripts/doctor.mjs", "scripts/cdp-proxy.mjs", "scripts/cdp-keepalive.mjs",
    "scripts/check-deps.mjs", "scripts/browser-discovery.mjs", "scripts/pw.mjs",
    "references/站点适配-雨课堂.md",
    "scripts/sites/yuketang/harvest-all.mjs",
    "node_modules/playwright/cli.js",
    "node_modules/ws/package.json",
    "templates/config.env.template",
]
print()
for m in must:
    p = DEST / m
    print(f"   {'OK ' if p.exists() else 'XX '} {m}")

n = sum(1 for _ in DEST.rglob("*") if _.is_file())
print(f"\n文件总数：{n}（期望 254）")

print()
print("=== 2b. 安装后残留机器专属路径扫描 ===")
import re
pat = re.compile(r"Matebook|\$TOOLBOX|\$HOME/|C:\\\\Users\\\\")
hits = []
for f in DEST.rglob("*"):
    if not f.is_file() or "node_modules" in f.parts:
        continue
    if f.suffix.lower() not in {".md", ".mjs", ".py", ".json", ".txt"} and f.name != "config.env":
        continue
    try:
        t = f.read_text(encoding="utf-8")
    except Exception:
        continue
    for i, line in enumerate(t.splitlines(), 1):
        if pat.search(line):
            hits.append(f"{f.relative_to(DEST)}:{i}: {line.strip()[:90]}")
if hits:
    print(f"   !! 命中 {len(hits)} 处：")
    for h in hits[:15]:
        print("      ", h)
else:
    print("   [OK] 0 处残留 —— 无机器专属硬编码路径")

print()
print("=" * 66)
print("3. 隔离环境下运行 doctor.mjs（验证技能可独立工作）")
print("=" * 66)

node = None
for cand in ["node"]:
    try:
        r = subprocess.run([cand, "-v"], capture_output=True, timeout=20)
        if r.returncode == 0:
            node = cand
            print(f"node = {r.stdout.decode(errors='replace').strip()}")
            break
    except FileNotFoundError:
        pass
if not node:
    print("[XX] 找不到 node")
    sys.exit(1)

r = subprocess.run(
    [node, str(DEST / "scripts" / "doctor.mjs"), "--quick"],
    capture_output=True, timeout=180, env=env,
)
doc = r.stdout.decode("utf-8", errors="replace")
print(doc)
print(f"doctor 退出码：{r.returncode}（0=L1可用 / 1=仅静态层 / 2=环境致命）")
if r.stderr:
    print("stderr:", r.stderr.decode(errors="replace")[:600])
