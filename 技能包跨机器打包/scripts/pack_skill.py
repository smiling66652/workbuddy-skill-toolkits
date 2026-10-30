#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""技能包离线化打包器（通用）

用法：
    python pack_skill.py --src "<技能目录>" --name "<包名>" [选项]

选项：
    --buildroot DIR   构建暂存根（默认 D:\\.workbuddy\\tmp\\skill-pack-2026-09-19）
    --out DIR         交付根（默认 D:\\桌面\\技能包_离线安装_2026-09-19）
    --doc FILE        使用说明.md 内容来源（UTF-8）。不给则生成骨架。
    --keep-node-modules   随包携带 node_modules（联网工具箱需要）
    --template FILE   install.bat 模板（默认同目录 install_template.bat）
    --dry-run         只做残留扫描，不打 zip

产出：
    <buildroot>/<name>/payload/          ← sanitize 后的技能本体（供汇总复用）
    <buildroot>/<name>-残留报告.txt        ← 硬编码清单（含已自动修复项）
    <out>/<name>-离线安装包.zip            ← 交付物
"""
import argparse
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 默认值：换机可直接用；也可用 --buildroot / --out 覆盖，或用环境变量指定
DEFAULT_BUILDROOT = Path(os.environ.get("SKILLPACK_BUILD") or (Path.home() / "_skillpack_build"))
DEFAULT_OUT = Path(os.environ.get("SKILLPACK_OUT") or (Path.home() / "Desktop" / "skill-packages"))

# 源机用户名：动态取，不要写成字面量 ——
# 否则本工具自身的模式串会被残留扫描器当成"源机残留"命中（自我命中）。
SRC_USER = os.environ.get("USERNAME") or os.environ.get("USER") or ""

EXCLUDE = [".git", "__pycache__", ".playwright-cli", ".pytest_cache",
           "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db", "desktop.ini"]

DOC_EXT = {".md", ".txt", ".rst"}
CODE_EXT = {".py", ".mjs", ".js", ".cjs", ".ps1", ".bat", ".cmd", ".json", ".env", ".sh", ".yml", ".yaml"}

# 自动修复规则：只作用于文档（.md/.txt），代码文件只报告
PKGNAME_PLACEHOLDER = "{PKGNAME}"
NODE_NOTE_PLACEHOLDER = "{NODE_MISSING_NOTE}"

NODE_VER_RE = re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/\s\"']+[\\/]\.workbuddy[\\/]binaries[\\/]node[\\/]versions[\\/][^\\/\s\"']+[\\/]node\.exe")


def to_crlf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\n", "\r\n")


def auto_fix_text(text: str, pkgname: str) -> str:
    """机械替换（仅文档）。返回修复后文本。"""
    out = text
    # 0) frontmatter 里的源机用户名 -> 真实署名
    #    这不是路径，但换机后留在 frontmatter 里没有意义，且会被残留扫描判为命中。
    #    用户名动态取自环境变量（见 SRC_USER），工具自身不出现字面量。
    if SRC_USER:
        out = re.sub(rf"^(author:\s*){re.escape(SRC_USER)}\s*$", r"\1义航", out, flags=re.M)
    # 1) 技能自身绝对路径 -> 相对
    if SRC_USER:
        for sep in ("\\", "/"):
            prefix = f"C:{sep}Users{sep}{SRC_USER}{sep}.workbuddy{sep}skills{sep}{pkgname}{sep}"
            out = out.replace(prefix, "")
            out = out.replace(prefix.replace("\\", "/"), "")
    # 2) 托管 node.exe -> node
    out = NODE_VER_RE.sub("node", out)
    # 3) 用户目录 -> %USERPROFILE%
    #    拼接写法：避免工具自身的模式串被残留扫描器判为"源机残留"（自我命中）
    if SRC_USER:
        out = out.replace("C:\\" + "Users\\" + SRC_USER, r"%USERPROFILE%")
        out = out.replace("C:/" + "Users/" + SRC_USER, "%USERPROFILE%")
    # 4) 源机桌面（D 盘重定向）-> %USERPROFILE%\Desktop
    out = out.replace("D:\\" + "桌面", r"%USERPROFILE%\Desktop")
    out = out.replace("D:/" + "桌面", "%USERPROFILE%/Desktop")
    return out


def scan_hardcode(root: Path, pkgname: str):
    """扫描硬编码。返回 (findings, doc_fixed_count, code_findings)"""
    findings = []
    code_findings = []
    fixed = 0
    pats = []
    if SRC_USER:
        pats.append(("用户名", re.compile(re.escape(SRC_USER))))
    pats += [("用户目录", re.compile(r"C:[\\/]Users[\\/]")),
             ("托管运行时", NODE_VER_RE),
             ("D盘工作路径", re.compile("D:[\\\\/]" + "桌面"))]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (DOC_EXT | CODE_EXT):
            continue
        try:
            raw = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(root).as_posix()
        hits = []
        for line_no, line in enumerate(raw.splitlines(), 1):
            for label, rx in pats:
                if rx.search(line):
                    hits.append((line_no, label, line.strip()[:120]))
                    break
        if not hits:
            continue
        if p.suffix.lower() in DOC_EXT:
            new = auto_fix_text(raw, pkgname)
            if new != raw:
                p.write_text(new, encoding="utf-8", newline="")
                remaining = auto_fix_text(new, pkgname)
                after = sum(1 for ln in remaining.splitlines()
                            for _l, rx in pats if rx.search(ln))
                fixed += len(hits)
                if after:
                    findings.append((rel, hits, "部分残留"))
                else:
                    findings.append((rel, hits, "已自动修复"))
            else:
                findings.append((rel, hits, "未自动修复"))
        else:
            code_findings.append((rel, hits))
    return findings, fixed, code_findings


def write_report(path: Path, pkgname: str, findings, fixed, code_findings):
    lines = [f"# {pkgname} · 硬编码残留报告", ""]
    lines.append(f"自动修复（文档）：{fixed} 处")
    lines.append("")
    lines.append(f"## 文档类（{len(findings)} 个文件）")
    for rel, hits, status in findings:
        lines.append(f"\n### {rel}  [{status}]")
        for ln, label, txt in hits:
            lines.append(f"  L{ln} [{label}] {txt}")
    lines.append("")
    lines.append(f"## 代码类（{len(code_findings)} 个文件，需人工判断，脚本不自动改）")
    for rel, hits in code_findings:
        lines.append(f"\n### {rel}")
        for ln, label, txt in hits:
            lines.append(f"  L{ln} [{label}] {txt}")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_install_bat(template_path: Path, dest: Path, pkgname: str, has_node_deps: bool):
    tpl = template_path.read_text(encoding="utf-8")
    note = "        本包为文档/脚本型技能，不依赖 Node，可正常使用。" if not has_node_deps \
        else "        [注意] 本包需要 Node 运行环境，请先安装 Node.js 后重跑本脚本。"
    text = tpl.replace(PKGNAME_PLACEHOLDER, pkgname).replace(NODE_NOTE_PLACEHOLDER, note)
    text = to_crlf(text)
    dest.write_bytes(text.encode("gbk"))
    b = dest.read_bytes()
    assert b.count(b"\r") == b.count(b"\n") > 0, "install.bat 行尾不是 CRLF！"
    try:
        b.decode("gbk")
    except UnicodeDecodeError as e:
        raise SystemExit(f"install.bat 含 GBK 无法编码的字符：{e}")
    return text.count("\r\n")


def write_readme(dest: Path, pkgname: str):
    txt = f"""============================================================
  {pkgname}  ·  离线安装包
============================================================

三步安装：
  1. 把本压缩包解压到一个【纯英文路径】的文件夹（例如 D:\\skill_pkg）
  2. 双击 install.bat
  3. 看到「安装完成」后，按任意键关闭窗口，重启 WorkBuddy

安装位置：
  %USERPROFILE%\\.workbuddy\\skills\\{pkgname}

说明：
  - 若提示旧版目录被占用，请完全退出 WorkBuddy（含右下角托盘）后重跑。
  - 脚本会自动把已有旧版备份为 "{pkgname}_backup_<随机数>"，不会直接删除。
  - 详细用法见同目录下的「使用说明.md」。

============================================================
"""
    dest.write_bytes(b"\xef\xbb\xbf" + to_crlf(txt).encode("utf-8"))


def write_doc_skeleton(dest: Path, pkgname: str):
    txt = f"""# {pkgname} · 使用说明

## 安装

解压后双击 `install.bat`，装到：

```
%USERPROFILE%\\.workbuddy\\skills\\{pkgname}
```

> 注意：`install.bat` 必须与 `payload` 目录在同一层，不要只复制单个文件。

## 安装后必做

1. 重启 WorkBuddy（或新开一个会话）。
2. 在对话中说出该技能的触发词即可。

## 常见问题

**Q：提示「找不到 payload\\SKILL.md」？**
A：没有完整解压，或解压时只拖出了部分文件。请重新解压整个压缩包。

**Q：提示「旧版目录被占用」？**
A：WorkBuddy 正在运行并锁住了技能目录。完全退出（含托盘图标）后重跑。

**Q：中文显示乱码？**
A：`install.bat` 是 GBK 编码，请用 cmd 直接双击运行，不要在 UTF-8 编辑器里保存它。
"""
    dest.write_bytes(to_crlf(txt).encode("utf-8"))


def make_zip(stage: Path, zip_path: Path, pkgname: str):
    if zip_path.exists():
        zip_path.unlink()
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                zf.write(p, (Path(pkgname) / p.relative_to(stage)).as_posix())
                count += 1
    return count


def verify_zip(zip_path: Path, pkgname: str, payload_files: int):
    problems = []
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        bad_flag = [i.filename for i in infos
                    if not i.filename.isascii() and not (i.flag_bits & 0x800)]
        unwanted = [n for n in names if "/.git/" in n or "/__pycache__/" in n
                    or "/.playwright-cli/" in n or n.endswith(".pyc")]
        must = [f"{pkgname}/install.bat", f"{pkgname}/README.txt",
                f"{pkgname}/使用说明.md", f"{pkgname}/payload/SKILL.md"]
        missing = [m for m in must if m not in names]
        bat = zf.read(f"{pkgname}/install.bat")
        crlf_ok = bat.count(b"\r") == bat.count(b"\n") > 0
        try:
            bat.decode("gbk")
            gbk_ok = True
        except UnicodeDecodeError:
            gbk_ok = False
        if bad_flag:
            problems.append(f"缺 UTF-8 标志的条目 {len(bad_flag)} 个：{bad_flag[:3]}")
        if unwanted:
            problems.append(f"混入应排除文件 {len(unwanted)} 个：{unwanted[:3]}")
        if missing:
            problems.append(f"缺关键文件：{missing}")
        if not crlf_ok:
            problems.append("install.bat 行尾不是 CRLF")
        if not gbk_ok:
            problems.append("install.bat 无法 GBK 解码")
    return problems, len(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--buildroot", default=str(DEFAULT_BUILDROOT))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--doc")
    ap.add_argument("--template", default=str(HERE / "install_template.bat"))
    ap.add_argument("--keep-node-modules", action="store_true")
    ap.add_argument("--reuse-payload", action="store_true",
                    help="复用构建区已存在的 payload，保留手工 sanitize（重跑打包时不会抹掉手改）")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    src = Path(a.src).resolve()
    pkgname = a.name
    buildroot = Path(a.buildroot)
    outroot = Path(a.out)
    pkgdir_name = f"{pkgname}-离线安装包"
    stage = buildroot / pkgdir_name
    payload = stage / "payload"

    if not (src / "SKILL.md").exists():
        raise SystemExit(f"[XX] 源目录无 SKILL.md：{src}")

    # ---- 1. 复制 payload（--reuse-payload 时保留构建区已有的手工 sanitize）----
    if a.reuse_payload and payload.exists() and any(payload.iterdir()):
        n_payload = sum(1 for _ in payload.rglob("*") if _.is_file())
        print(f"[1/6] 复用已有 payload -> {n_payload} 个文件（保留手工 sanitize）")
    else:
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        ignore = list(EXCLUDE)
        if not a.keep_node_modules:
            ignore.append("node_modules")
        shutil.copytree(src, payload, ignore=shutil.ignore_patterns(*ignore))
        n_payload = sum(1 for _ in payload.rglob("*") if _.is_file())
        print(f"[1/6] 复制 payload -> {n_payload} 个文件")

    # ---- 2. 残留扫描 + 自动修复 ----
    findings, fixed, code_findings = scan_hardcode(payload, pkgname)
    report = buildroot / f"{pkgname}-残留报告.txt"
    write_report(report, pkgname, findings, fixed, code_findings)
    n_left = sum(len(h) for _r, h, s in findings if s != "已自动修复")
    print(f"[2/6] 硬编码：文档自动修复 {fixed} 处，待人工处理 {n_left} 处，"
          f"代码类 {len(code_findings)} 个文件 -> {report.name}")

    if a.dry_run:
        print("[dry-run] 停在扫描阶段")
        return

    # ---- 3. install.bat / README / 使用说明 ----
    has_node_deps = (payload / "node_modules").exists() or (payload / "package.json").exists()
    lines = write_install_bat(Path(a.template), stage / "install.bat", pkgname, has_node_deps)
    write_readme(stage / "README.txt", pkgname)
    doc_src = Path(a.doc) if a.doc else None
    doc_dest = stage / "使用说明.md"
    keep_doc = (a.reuse_payload and not doc_src and doc_dest.exists()
                and len(doc_dest.read_text(encoding="utf-8").splitlines()) >= 40)
    if keep_doc:
        n_doc = len(doc_dest.read_text(encoding="utf-8").splitlines())
        doc_by = f"保留构建区已有版本（{n_doc} 行）"
    elif doc_src and doc_src.exists():
        doc_dest.write_bytes(to_crlf(doc_src.read_text(encoding="utf-8")).encode("utf-8"))
        doc_by = "自定义"
    else:
        write_doc_skeleton(doc_dest, pkgname)
        doc_by = "骨架（需补写）"
    print(f"[3/6] install.bat(GBK+CRLF, {lines} 行) / README.txt(UTF-8 BOM) / 使用说明.md({doc_by})")

    # ---- 4. 打包 ----
    outroot.mkdir(parents=True, exist_ok=True)
    zip_path = outroot / f"{pkgname}-离线安装包.zip"
    count = make_zip(stage, zip_path, pkgdir_name)
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"[4/6] {zip_path.name} -> {count} 条目 / {size_mb:.2f} MB")

    # ---- 5. 自检 ----
    problems, n_names = verify_zip(zip_path, pkgdir_name, n_payload)
    if problems:
        print("[5/6] 自检发现问题：")
        for p in problems:
            print("      [XX]", p)
    else:
        print(f"[5/6] 自检通过：{n_names} 条目、中文带 UTF-8 标志、无排除项混入、install.bat CRLF+GBK")

    # ---- 6. 交付信息 ----
    print(f"[6/6] 交付：{zip_path}")
    print("\n===== 交付报告字段 =====")
    print(f"包名：{pkgname}")
    print(f"源文件数：{n_payload}（payload，已排除 {', '.join(EXCLUDE)}"
          f"{'' if a.keep_node_modules else ', node_modules'}）")
    print(f"硬编码自动修复：{fixed} 处；代码类待人工：{len(code_findings)} 文件；"
          f"报告：{report}")
    print(f"zip：{zip_path} ({size_mb:.2f} MB, {count} 条目)")
    if problems:
        print(f"自检问题：{problems}")


if __name__ == "__main__":
    main()
