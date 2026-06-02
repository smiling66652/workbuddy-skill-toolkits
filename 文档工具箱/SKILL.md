---
name: 文档工具箱
description: >
  统一文档处理工具箱（三级层级结构）：
  一级：分析用户需求和文件类型（PDF/Word/Excel/PPT/Markdown）
  二级：选择最佳工具（MinerU/MarkItDown/pypandoc/docx/pptx/openpyxl）
  三级：执行指令并返回结果。
  集成最佳工具：MinerU（PDF→MD表格97%）、MarkItDown、pypandoc、docx、pptx、openpyxl。
version: 4.0.0
author: WorkBuddy 整合版
---

# 文档工具箱

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断文件类型和要做什么（读取/编辑/生成/转换）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 文件类型 | 你要做什么 | 跳转二级 | 推荐工具 |
|---------|------------|---------|---------|
| PDF | 读取/提取文字表格 | [二级：PDF读取](references/PDF读取.md) | MinerU（表格97%） |
| PDF | 编辑/修改内容 | [二级：PDF编辑](references/PDF编辑.md) | pdfkit-py / pdftk |
| PDF | 用自然语言描述修改 | [二级：PDF编辑](references/PDF编辑.md) | pdfkit-py natural language |
| PDF | 生成精美排版PDF | [二级：PDF生成](references/PDF生成.md) | reportlab / WeasyPrint |
| Word(DOCX) | 创建/编辑文档 | [二级：Word处理](references/Word处理.md) | docx / python-docx |
| PPT(PPTX) | 生成/编辑演示文稿 | [二级：PPT处理](references/PPT处理.md) | pptx / python-pptx |
| Excel(XLSX) | 创建/分析/编辑表格 | [二级：Excel处理](references/Excel处理.md) | openpyxl / pandas |
| 任意格式 | 转为Markdown | [二级：格式转换](references/格式转换.md) | MinerU / MarkItDown / pypandoc |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 读取PDF | 读这个PDF、提取PDF文字、PDF讲了什么、OCR这个PDF | [二级：PDF读取](references/PDF读取.md) |
| 编辑PDF | 修改PDF、编辑PDF内容、PDF加文字、PDF加图片 | [二级：PDF编辑](references/PDF编辑.md) |
| 生成PDF | 生成PDF、导出PDF、做成PDF | [二级：PDF生成](references/PDF生成.md) |
| Word文档 | 创建Word、写个文档、编辑Word | [二级：Word处理](references/Word处理.md) |
| PPT演示 | 做PPT、生成幻灯片、编辑演示文稿 | [二级：PPT处理](references/PPT处理.md) |
| Excel表格 | 创建Excel、分析数据、编辑表格 | [二级：Excel处理](references/Excel处理.md) |
| 格式转换 | 转为Markdown、转Word、转PDF | [二级：格式转换](references/格式转换.md) |

---

## 通用规则

### 工具选择原则

1. **优先用Python库**（openpyxl/docx/pptx）— 无需安装Office
2. **大文件用流式处理** — 避免内存溢出
3. **中文编码用UTF-8** — 避免乱码
4. **操作后验证** — 读取生成的文件确认正确

### 并行策略

- 多个独立文档操作 → 用子 Agent 分治并行执行
- 每个子 Agent 处理不同文件，无竞态风险

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/PDF读取.md` | 需要读取/提取PDF内容时 |
| `references/PDF编辑.md` | 需要编辑/修改PDF内容时 |
| `references/PDF生成.md` | 需要生成精美排版PDF时 |
| `references/Word处理.md` | 需要创建/编辑Word文档时 |
| `references/PPT处理.md` | 需要创建/编辑PPT演示文稿时 |
| `references/Excel处理.md` | 需要创建/分析/编辑Excel表格时 |
| `references/格式转换.md` | 需要格式转换时 |
| `references/工具对比.md` | 需要选择最佳工具时 |
