#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_docx.py —— Word 文档创作与美化技能的可执行生成器。

把一份"大纲 JSON"渲染为标准 .docx，遵循 assets/style-guide.md 的版式规范。
不依赖任何外部二进制（原内置技能依赖的 dist/cli.cjs 在此环境无法分发），
纯 python-docx 实现，可离线运行。

用法：
    python make_docx.py --json outline.json --out report.docx
    python make_docx.py --demo --out demo.docx        # 生成一份示例文档

也可在 Python 中 import 后调用 build_from_outline() / DocxBuilder。
"""
import argparse
import json
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ---------------- 样式规范（与 assets/style-guide.md 保持一致） ----------------
THEME = {
    "cn_font": "微软雅黑",        # 中文
    "en_font": "Calibri",         # 西文
    "title_size": 26,
    "h1_size": 18,
    "h2_size": 15,
    "h3_size": 13,
    "body_size": 11,
    "accent": RGBColor(0x1F, 0x4E, 0x79),   # 深蓝主色
    "accent2": RGBColor(0xC0, 0x50, 0x4D),  # 辅助红
    "text": RGBColor(0x22, 0x22, 0x22),
}


def set_run_font(run, cn=THEME["cn_font"], en=THEME["en_font"], size=None, color=None, bold=None):
    """同时设置中西文字体，避免中文回退乱版。"""
    if cn:
        run.font.name = en or cn
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:eastAsia"), cn)
        rfonts.set(qn("w:ascii"), en or cn)
        rfonts.set(qn("w:hAnsi"), en or cn)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    if bold is not None:
        run.font.bold = bold


class DocxBuilder:
    def __init__(self):
        self.doc = Document()
        self._base_setup()

    def _base_setup(self):
        # 页面：A4，默认页边距
        sec = self.doc.sections[0]
        sec.page_height = Inches(11.69)
        sec.page_width = Inches(8.27)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        # 默认正文样式
        normal = self.doc.styles["Normal"]
        normal.font.name = THEME["en_font"]
        normal.font.size = Pt(THEME["body_size"])
        normal.font.color.rgb = THEME["text"]
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:eastAsia"), THEME["cn_font"])

    def cover(self, meta):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.space_before = Pt(120)
        r = p.add_run(meta.get("title", "文档标题"))
        set_run_font(r, size=THEME["title_size"], color=THEME["accent"], bold=True)
        if meta.get("subtitle"):
            p2 = self.doc.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r2 = p2.add_run(meta["subtitle"])
            set_run_font(r2, size=14, color=THEME["text"])
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = info.add_run(f"{meta.get('author','')}    {meta.get('date','')}")
        set_run_font(r3, size=11, color=THEME["text"])
        self.doc.add_page_break()

    def heading(self, text, level=1):
        sizes = {1: THEME["h1_size"], 2: THEME["h2_size"], 3: THEME["h3_size"]}
        p = self.doc.add_paragraph()
        p.space_before = Pt(12 if level == 1 else 8)
        r = p.add_run(text)
        set_run_font(r, size=sizes.get(level, 13), color=THEME["accent"], bold=True)
        return p

    def paragraph(self, text, style="body"):
        p = self.doc.add_paragraph()
        r = p.add_run(text)
        set_run_font(r, size=THEME["body_size"], color=THEME["text"])
        return p

    def bullets(self, items):
        for it in items:
            p = self.doc.add_paragraph(style="List Bullet")
            r = p.add_run(it)
            set_run_font(r, size=THEME["body_size"], color=THEME["text"])

    def numbered(self, items):
        for it in items:
            p = self.doc.add_paragraph(style="List Number")
            r = p.add_run(it)
            set_run_font(r, size=THEME["body_size"], color=THEME["text"])

    def table(self, headers, rows):
        t = self.doc.add_table(rows=1, cols=len(headers))
        t.style = "Light Grid Accent 1"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = t.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            r = hdr[i].paragraphs[0].add_run(h)
            set_run_font(r, size=11, color=RGBColor(0xFF, 0xFF, 0xFF), bold=True)
            shade_cell(hdr[i], "1F4E79")
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                r = cells[i].paragraphs[0].add_run(str(v))
                set_run_font(r, size=10, color=THEME["text"])
        return t

    def pagebreak(self):
        self.doc.add_page_break()

    def add_page_number(self):
        """在页脚插入 PAGE 域（页码）。"""
        sec = self.doc.sections[0]
        footer = sec.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        fld1 = OxmlElement("w:fldSimple")
        fld1.set(qn("w:instr"), "PAGE")
        run._element.addnext(fld1)

    def save(self, path):
        self.doc.save(path)


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def build_from_outline(outline):
    """把大纲 dict 渲染成 Document 并保存（若含 out 键）。返回 DocxBuilder。"""
    b = DocxBuilder()
    meta = outline.get("meta", {})
    if outline.get("blocks") and outline["blocks"][0].get("type") == "cover":
        b.cover(meta)
    elif meta:
        # 若未显式放 cover 块但有 meta，默认先出封面
        b.cover(meta)
    for blk in outline.get("blocks", []):
        t = blk.get("type")
        if t == "cover":
            b.cover(meta)
        elif t == "h1":
            b.heading(blk["text"], 1)
        elif t == "h2":
            b.heading(blk["text"], 2)
        elif t == "h3":
            b.heading(blk["text"], 3)
        elif t == "p":
            b.paragraph(blk.get("text", ""))
        elif t == "bullets":
            b.bullets(blk.get("items", []))
        elif t == "numbered":
            b.numbered(blk.get("items", []))
        elif t == "table":
            b.table(blk.get("headers", []), blk.get("rows", []))
        elif t == "pagebreak":
            b.pagebreak()
    if outline.get("page_number", True):
        b.add_page_number()
    return b


def demo_outline():
    return {
        "meta": {"title": "示例文档", "subtitle": "由 Word 文档创作与美化技能生成", "author": "WorkBuddy", "date": "2026-10-26"},
        "blocks": [
            {"type": "h1", "text": "第一章 概述"},
            {"type": "p", "text": "这是一段示例正文，演示中文字体与正文样式的统一。"},
            {"type": "bullets", "items": ["要点一：结构清晰", "要点二：版式统一", "要点三：中西文混排不乱"]},
            {"type": "h2", "text": "1.1 关键指标"},
            {"type": "table", "headers": ["指标", "数值", "说明"], "rows": [["营收", "12 亿", "同比增长 20%"], ["净利", "3 亿", "毛利率 35%"]]},
            {"type": "pagebreak"},
            {"type": "h1", "text": "第二章 结论"},
            {"type": "p", "text": "结论先行：本技能可离线生成标准 .docx。"}
        ]
    }


def main():
    ap = argparse.ArgumentParser(description="Word 文档大纲渲染器")
    ap.add_argument("--json", help="大纲 JSON 文件路径")
    ap.add_argument("--out", default="output.docx", help="输出 .docx 路径")
    ap.add_argument("--demo", action="store_true", help="生成示例文档")
    args = ap.parse_args()

    if args.demo:
        outline = demo_outline()
    elif args.json:
        with open(args.json, encoding="utf-8") as f:
            outline = json.load(f)
    else:
        ap.print_help()
        return 1

    b = build_from_outline(outline)
    b.save(args.out)
    print(f"OK -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
