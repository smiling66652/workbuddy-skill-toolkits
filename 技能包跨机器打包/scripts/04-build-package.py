# -*- coding: utf-8 -*-
"""
联网工具箱 · 离线安装包构建脚本
1. 组装发布目录（install.bat 用 GBK 编码落盘，保证 cmd 原生中文零乱码）
2. 打包 zip（UTF-8 文件名标志，跨机解压不乱码）
"""
import shutil
import zipfile
from pathlib import Path

BUILD = Path(r"D:\桌面\skills\_build_联网工具箱")
OUT_ROOT = Path(r"D:\桌面\skills")
PKG_NAME = "联网工具箱-离线安装包"
STAGE = OUT_ROOT / PKG_NAME
ZIP_PATH = OUT_ROOT / f"{PKG_NAME}.zip"

PAYLOAD = BUILD / "payload"


def to_crlf(text: str) -> str:
    """统一为 CRLF。

    必须做：.bat 用纯 LF 时 cmd 的 if(...) 括号块会解析错位，
    中文 echo 行会被当成独立命令执行（实测报错：
    '，且本文件与payload' 不是内部或外部命令）。
    """
    return text.replace("\r\n", "\n").replace("\n", "\r\n")


def main():
    # ---------- 1. 组装发布目录 ----------
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    # install.bat: UTF-8 源 -> CRLF + GBK 落盘
    # （cmd 默认代码页 936 正确显示中文；CRLF 保证括号块解析正确）
    src_bat = (BUILD / "install_src.bat").read_text(encoding="utf-8")
    bat_text = to_crlf(src_bat)
    try:
        (STAGE / "install.bat").write_bytes(bat_text.encode("gbk"))
        crlf = bat_text.count("\r\n")
        print(f"[OK] install.bat  -> GBK + CRLF 写入（{crlf} 行）")
    except UnicodeEncodeError as e:
        print(f"[XX] install.bat 含 GBK 无法编码的字符：{e}")
        raise

    # README.txt: UTF-8 with BOM + CRLF（记事本可直接正确打开）
    readme = to_crlf((BUILD / "README.txt.src").read_text(encoding="utf-8"))
    (STAGE / "README.txt").write_bytes(b"\xef\xbb\xbf" + readme.encode("utf-8"))
    print("[OK] README.txt   -> UTF-8 BOM + CRLF 写入")

    # 使用说明.md
    (STAGE / "使用说明.md").write_bytes(
        to_crlf((BUILD / "使用说明.md").read_text(encoding="utf-8")).encode("utf-8"))
    print("[OK] 使用说明.md  -> UTF-8 + CRLF 写入")

    # payload 技能本体
    shutil.copytree(PAYLOAD, STAGE / "payload")
    n = sum(1 for _ in (STAGE / "payload").rglob("*") if _.is_file())
    print(f"[OK] payload/     -> {n} 个文件")

    # ---------- 2. 打包 zip ----------
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file():
                arc = Path(PKG_NAME) / p.relative_to(STAGE)
                zf.write(p, arc.as_posix())
                count += 1
    print(f"[OK] {ZIP_PATH.name} -> {count} 个条目，"
          f"{ZIP_PATH.stat().st_size / 1024 / 1024:.1f} MB")

    # ---------- 3. 自检：中文文件名是否带 UTF-8 标志 ----------
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = []
        cjk = 0
        for info in zf.infolist():
            if not info.filename.isascii():
                cjk += 1
                if not (info.flag_bits & 0x800):
                    bad.append(info.filename)
        print(f"\n[自检] 非 ASCII 条目 {cjk} 个，缺 UTF-8 标志 {len(bad)} 个")
        if bad:
            print("   [XX] 这些条目在中文系统外可能乱码：", bad[:5])
        else:
            print("   [OK] 全部带 UTF-8 标志，跨机解压不乱码")

        # 关键文件抽查
        names = {i.filename for i in zf.infolist()}
        must = [
            f"{PKG_NAME}/install.bat",
            f"{PKG_NAME}/README.txt",
            f"{PKG_NAME}/使用说明.md",
            f"{PKG_NAME}/payload/SKILL.md",
            f"{PKG_NAME}/payload/config.env",
            f"{PKG_NAME}/payload/scripts/doctor.mjs",
            f"{PKG_NAME}/payload/scripts/cdp-proxy.mjs",
            f"{PKG_NAME}/payload/node_modules/playwright/cli.js",
            f"{PKG_NAME}/payload/references/站点适配-雨课堂.md",
            f"{PKG_NAME}/payload/scripts/sites/yuketang/harvest-all.mjs",
        ]
        print("\n[自检] 关键文件：")
        for m in must:
            print(f"   {'OK ' if m in names else 'XX '} {m}")

        # 排除项检查
        unwanted = [n for n in names
                    if "/.git/" in n or "/__pycache__/" in n
                    or "/.playwright-cli/" in n or n.endswith(".pyc")]
        print(f"\n[自检] 不应出现的文件（.git/__pycache__/.playwright-cli）：{len(unwanted)} 个")
        for u in unwanted[:5]:
            print("   XX", u)

        # install.bat 行尾复检（LF 会让 cmd 括号块解析错位）
        bat_bytes = zf.read(f"{PKG_NAME}/install.bat")
        cr, lf = bat_bytes.count(b"\r"), bat_bytes.count(b"\n")
        ok_crlf = (cr == lf and cr > 0)
        print(f"\n[自检] install.bat 行尾：CR={cr} LF={lf} -> "
              f"{'CRLF 正常' if ok_crlf else '!! 行尾异常，cmd 括号块会出错'}")

        # install.bat 可 GBK 解码复检
        try:
            bat_bytes.decode("gbk")
            print("[自检] install.bat GBK 解码：正常（cmd 下中文不乱码）")
        except UnicodeDecodeError:
            print("[自检] install.bat GBK 解码：!! 失败")


if __name__ == "__main__":
    main()
