---
name: word-toolkit
agent_created: true
display_name: "Word 文档创作与美化"
display_name_en: "Word Document Authoring & Beautification"
description_zh: "（本地 python-docx 深度工具箱，与平台内置文档流水线分工：内置版走云端编排，本包走本地 python-docx，二者互为补充）专业 Word 文档（.docx）全流程处理助手：创建/生成、读取/审阅、编辑、排版美化、模板套用、合并转换与质量校验。当用户提到 Word、DOCX、office 文档、报告、研报、论文、公文、合同、方案、模板、批注、修订（tracked changes）、排版、套模板、写报告、填表，或任务最终产出是 .docx 文件时调用。提供从结构规划、内容撰写到版式美化（标题层级、封面、目录、表格、正文样式、中文字体、页码页眉）的方法论，附 python-docx 生成脚本（scripts/make_docx.py）、结构检查与渲染质检脚本（scripts/inspect_docx.py、scripts/render_docx.py）、样式规范与封面模板，以及 OpenXML 结构百科、CJK 排版、批注/修订、场景化操作等 20 篇参考文档（references/）。"
description: "Professional Word document (.docx) all-in-one assistant: create, read, edit, format, beautify, apply templates, merge, and validate. Use when the user mentions Word, DOCX, office documents, reports, proposals, contracts, templates, tracked changes, comments, document layout, or any task whose final output is a .docx file. Provides an end-to-end methodology plus a runnable python-docx generator (scripts/make_docx.py), structural inspection & render QA scripts (scripts/inspect_docx.py, scripts/render_docx.py), style assets, and 20 reference docs covering OpenXML, CJK typography, comments/track-changes and scenario workflows (references/)."
description_en: "Professional Word document (.docx) all-in-one assistant: create, read, edit, format, beautify, apply templates, merge, and validate. Use when the user mentions Word, DOCX, office documents, reports, proposals, contracts, templates, tracked changes, comments, document layout, or any task whose final output is a .docx file. Provides an end-to-end methodology plus a runnable python-docx generator, structural inspection & render QA scripts, style assets, and 20 reference docs covering OpenXML, CJK typography, comments/track-changes and scenario workflows."
version: "1.0.1"
---


# Word 文档创作与美化

一个面向实战的 Word（.docx）技能：既能**从零生成**专业文档，也能对**已有文档做排版美化与风格统一**。核心依赖 `python-docx`，所有产物都是标准 .docx，可直接在 Word / WPS 打开。

## 能力边界

- ✅ 生成：研报、论文、公文、合同、商业计划书、会议纪要、产品方案等结构化 .docx
- ✅ 美化：统一标题层级、正文字体、表格样式、页眉页脚、封面、目录
- ✅ 自动化：通过 `scripts/make_docx.py` 把"大纲 JSON"一键渲染成成品 .docx
- 🔀 分工：平台内置 Word 流水线（腾讯文档编排）负责云端协作/在线文档转化；本包负责**本地 .docx** 的生成/美化/质检，二者可叠加使用（先内置出稿，再本包精修）
- ⚠️ 不负责：文档的**事实准确性与内容合规**（由调用方/用户负责）；不替代专业法务/学术校对

## 标准工作流（创作）

1. **明确类型与受众**：先确认文档类型（研报 / 论文 / 公文 / 合同 / 方案），不同类别的版式与措辞差异很大。
2. **规划结构大纲**：用"章节 → 要点"的层级列出骨架（建议 2–4 级标题），避免写到一半结构崩塌。
3. **撰写内容**：先填干货（结论、数据、论点），再润色。遵循"先结论后展开"。
4. **套用版式**：用 `assets/style-guide.md` 的规范统一字体、字号、行距、配色；用 `assets/cover-template.md` 做封面。
5. **生成文件**：调用 `scripts/make_docx.py`，传入大纲 JSON，输出 .docx。
6. **自检**：检查标题层级连续、表格不溢出、中文字体生效、页码/页眉正确。

## 标准工作流（美化已有文档）

1. 读取现有 .docx，盘点其标题层级、字体、配色、表格样式的不一致处。
2. 按 `assets/style-guide.md` 定义一套目标样式（字体、字号、颜色、间距）。
3. 用 python-docx 批量重设：Normal 样式、各级标题、表格边框与底纹、页眉页脚。
4. 输出美化后的新文件，保留原文内容，仅改版式。

## 中文字体要点（易错）

- 务必同时设置 **西文与中文** 字体名（`font.name` + `w:eastAsia`），否则中文会回退到默认字体、版式错乱。
- 推荐组合：正文「微软雅黑 / 等线」，标题「微软雅黑 / 黑体」，正式公文可用「仿宋 / 楷体 / 方正小标宋」。
- 行距建议 1.5 倍或固定值；段前/段后间距统一，避免"看着挤"。

## 脚本用法

`scripts/make_docx.py` 把一个大纲 JSON 渲染为标准 .docx：

```bash
# 由大纲生成文档
python scripts/make_docx.py --json outline.json --out report.docx

# 也可在 Python 内直接调用函数（见脚本 docstring）
```

大纲 JSON 结构（节选自 `scripts/make_docx.py` 的 `build_from_outline`）：

```json
{
  "meta": { "title": "文档标题", "subtitle": "副标题", "author": "作者", "date": "2026-10-26" },
  "blocks": [
    { "type": "h1", "text": "第一章 引言" },
    { "type": "p",  "text": "正文段落……", "style": "body" },
    { "type": "bullets", "items": ["要点一", "要点二"] },
    { "type": "table", "headers": ["指标", "数值"], "rows": [["营收", "12亿"], ["净利", "3亿"]] },
    { "type": "pagebreak" }
  ]
}
```

支持的 block 类型：`h1/h2/h3`（标题）、`p`（正文）、`bullets`（无序列表）、`numbered`（有序列表）、`table`（表格）、`pagebreak`（分页）、`cover`（封面页，读取 meta）。

## 交付检查清单

- [ ] `display_name` / `description_zh` / `version` 已填写且合规
- [ ] 标题层级从 1 开始、不跳级
- [ ] 中文与西文字体均已设置
- [ ] 表格宽度适配页面、无溢出
- [ ] 如需页码/页眉，已正确插入域
- [ ] 输出文件用 Word/WPS 实测可打开、无乱码

## 参考资源

- 版式与配色规范：`assets/style-guide.md`
- 封面模板：`assets/cover-template.md`
- 生成脚本：`scripts/make_docx.py`
- 结构检查与渲染质检：`scripts/inspect_docx.py`、`scripts/render_docx.py`
- 参考文档目录：`references/`（常用入口：`references/operations.md` 常见操作示例、`references/quality-checklist.md` 交付检查清单、`references/typography_guide.md` 与 `references/cjk_typography.md` 中西文排版、`references/troubleshooting.md` 问题排查、`references/scenario_a_create.md` / `scenario_b_edit_content.md` / `scenario_c_apply_template.md` 三大场景、`references/openxml_encyclopedia_part1.md` ~ `part3.md` OpenXML 结构百科）

## 合并来源

本技能由以下技能包合并而成（原包已归档至 `C:/Users/Matebook/.workbuddy/.archived_skills/`）：

- 来自 **docx**（任务路由与质检流水线）：
  - `references/operations.md`（常见操作与实现示例）
  - `references/quality-checklist.md`（结构/视觉质检清单）
  - `scripts/inspect_docx.py`（结构检查脚本）
  - `scripts/render_docx.py`（渲染检查脚本，支持导出 PDF）
- 来自 **minimax-docx**（OpenXML 深度处理与排版规范）：
  - `references/openxml_encyclopedia_part1.md` ~ `part3.md`、`openxml_element_order.md`、`openxml_namespaces.md`、`openxml_units.md`（OpenXML 结构与元素顺序）
  - `references/cjk_typography.md`、`typography_guide.md`、`cjk_university_template_guide.md`（中文排版与高校模板）
  - `references/comments_guide.md`、`track_changes_guide.md`（批注与修订）
  - `references/design_principles.md`、`design_good_bad_examples.md`（设计原则与正反例）
  - `references/scenario_a_create.md`、`scenario_b_edit_content.md`、`scenario_c_apply_template.md`（三大场景操作指南）
  - `references/troubleshooting.md`、`xsd_validation_guide.md`（故障排查与 XSD 校验）
  - 注：minimax-docx 的 .NET/OpenXML SDK CLI 工程未并入本包；如需可直接操作 OOXML 的 .NET 工具链，可从归档目录找回原包。
