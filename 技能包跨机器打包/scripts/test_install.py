#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离线包隔离安装验证器（通用）

模拟「一台新电脑」：把 USERPROFILE 指到临时假 home，从**最终 zip** 解压后跑 install.bat，
逐项检查安装结果。

用法：
    python test_install.py --pkg "<包名>" --zip "<交付目录>\\<包名>-离线安装包.zip"

退出码 0 = 全通；1 = 有失败项。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

WORKROOT = Path(os.environ.get("SKILLPACK_TESTDIR") or (Path.home() / "_skillpack_test"))
MOJIBAKE = re.compile(r"[\ufffd]|锟斤拷|ï»¿")

# 源机用户名：动态取，不要写成字面量 —— 否则扫描器会命中工具自身的模式串
SRC_USER = os.environ.get("USERNAME") or os.environ.get("USER") or ""


def count_files(p: Path) -> int:
    return sum(1 for _ in p.rglob("*") if _.is_file()) if p.exists() else 0


def scan_residue(root: Path, pkg: str):
    """安装后残留扫描：返回命中的 (相对路径, 行号, 内容) 列表"""
    hits = []
    if not root.exists():
        return hits
    parts = [r"C:[\\/]Users[\\/]", "D:[\\\\/]" + "桌面"]
    if SRC_USER:
        parts.append(re.escape(SRC_USER))
    rx = re.compile("|".join(parts))
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {
                ".md", ".txt", ".py", ".mjs", ".js", ".cjs", ".ps1",
                ".bat", ".cmd", ".json", ".env", ".yml", ".yaml", ".sh"}:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            if rx.search(line):
                hits.append((str(p.relative_to(root)), i, line.strip()[:110]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True)
    ap.add_argument("--zip", required=True, dest="zippath")
    ap.add_argument("--keep", action="store_true", help="保留测试目录（排查用）")
    a = ap.parse_args()
    pkg = a.pkg
    zp = Path(a.zippath).resolve()

    print("=" * 64)
    print(f"隔离安装验证：{pkg}")
    print("=" * 64)
    if not zp.exists():
        print(f"[XX] 找不到 zip：{zp}")
        return 1

    base = WORKROOT / pkg
    if base.exists():
        shutil.rmtree(base, ignore_errors=True)
    extract = base / "extract"
    fakehome = base / "fakehome"
    extract.mkdir(parents=True)
    fakehome.mkdir(parents=True)
    (base / "tmp").mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zp) as zf:
        zf.extractall(extract)
    pkgdir = extract / f"{pkg}-离线安装包"
    if not pkgdir.exists():
        cand = [d for d in extract.iterdir() if d.is_dir()]
        pkgdir = cand[0] if cand else extract
    print(f"[1] 已从 zip 解压 -> {pkgdir}")
    print(f"    条目数：{len(zipfile.ZipFile(zp).infolist())}")

    n_payload = count_files(pkgdir / "payload")
    print(f"[2] payload 文件数：{n_payload}")

    env = dict(os.environ)
    env["USERPROFILE"] = str(fakehome)
    env["TEMP"] = env["TMP"] = str(base / "tmp")

    print("[3] 运行 install.bat（USERPROFILE 已隔离）...")
    try:
        r = subprocess.run(["cmd", "/c", "install.bat"], cwd=str(pkgdir), env=env,
                           input=b"\r\n\r\n", capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("    [XX] 超时（可能卡在 pause）")
        return 1

    out = r.stdout.decode("gbk", errors="replace")
    err = r.stderr.decode("gbk", errors="replace")
    print("-" * 64)
    print(out.strip())
    print("-" * 64)
    if err.strip():
        print("[stderr]", err.strip()[:600])

    ok = True
    checks = []

    # 检查 1：跑完
    done = "安装完成" in out
    checks.append(("install.bat 跑到「安装完成」", done))
    ok &= done

    # 检查 2：中文不乱码
    bad = MOJIBAKE.search(out)
    checks.append(("中文输出无乱码", bad is None))
    ok &= (bad is None)

    # 检查 3：文件数一致
    dest = fakehome / ".workbuddy" / "skills" / pkg
    n_dest = count_files(dest)
    same = (n_dest == n_payload and n_dest > 0)
    checks.append((f"文件数一致（安装 {n_dest} / payload {n_payload}）", same))
    ok &= same

    # 检查 4：残留 0
    residue = scan_residue(dest, pkg)
    checks.append((f"安装后硬编码残留 0 处（实际 {len(residue)}）", not residue))
    ok &= (not residue)
    for rel, ln, txt in residue[:8]:
        print(f"      ! {rel}:{ln}  {txt}")

    # 检查 5：SKILL.md 到位
    skill_ok = (dest / "SKILL.md").exists()
    checks.append(("SKILL.md 安装到位", skill_ok))
    ok &= skill_ok

    print("\n" + "=" * 64)
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    print("=" * 64)
    print(f"结论：{'全部通过' if ok else '存在失败项'}")

    if not a.keep:
        shutil.rmtree(base, ignore_errors=True)
        print("[清理] 测试目录已删除")
    else:
        print(f"[保留] {base}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
