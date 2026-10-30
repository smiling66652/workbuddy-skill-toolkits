# 图片/扫描版 PDF 文字提取（零依赖方案，合并自 pdf-image-text-extractor）

> 本文档由原 **pdf-image-text-extractor** 技能包的 SKILL.md 提炼改写并入；原脚本位于 `scripts/image_text_extractor/`（`pdf_text_extractor.py`、`batch_extractor.py`、`record.py`、`changelog.py`）。
> 核心思路：**无需安装任何 OCR 引擎或表格库**——扫描版 PDF 自动渲染为高清 PNG 交由 AI 视觉（read_image）识别；表格用 pymupdf 内置 `find_tables()` 结构化提取。仅需 `pymupdf>=1.23.0` + `requests>=2.28.0`。

## 适用场景

- 从图片（PNG/JPG/JPEG/GIF/WebP/BMP/TIFF）提取文字
- 从 PDF（文字版 + 扫描版）提取文字与表格
- 批量处理目录（PDF + 图片混合）
- 用户要求 OCR 识别、提取 PDF 表格、转可编辑文本（Markdown）

> 注意：原包脚本带红狐 API Key 鉴权（`scripts/image_text_extractor/record.py`，需 `REDFOX_API_KEY` 环境变量）；未配置 Key 时可按本文档的方法论直接用 AI 视觉完成提取。

## PDF 提取流程

```bash
# 标准模式（自动检测扫描页渲染为图片 + 提取表格）
python scripts/image_text_extractor/pdf_text_extractor.py <pdf_path>

# 仅提取文字，跳过表格（更快）
python scripts/image_text_extractor/pdf_text_extractor.py <pdf_path> --no-tables

# 不渲染扫描页（仅提示哪些页是扫描页）
python scripts/image_text_extractor/pdf_text_extractor.py <pdf_path> --no-render

# 自定义扫描页图片输出目录 / 渲染分辨率
python scripts/image_text_extractor/pdf_text_extractor.py <pdf_path> --scan-dir ./ocr_pages --dpi 300
```

脚本返回 JSON，关键字段：

| 字段 | 说明 |
|------|------|
| `success` | 是否成功 |
| `text` | Markdown 格式正文（文字层） |
| `page_count` | 总页数 |
| `tables_markdown` | 所有表格的 Markdown 汇总 |
| `ocr_images` | 需 AI 视觉识别的图片清单 `[{'page','image'}]` |
| `warnings` | 非致命警告 |

处理规则：`ocr_images` 非空时逐张用 `read_image`（AI 视觉）识别并并入正文；文字层稀少（< 20 字符）的页面视为扫描页自动渲染。不支持加密 PDF。

## 批量处理流程

```bash
# 合并 Markdown 到终端 / 保存到文件 / JSON 结构化
python scripts/image_text_extractor/batch_extractor.py <目录路径>
python scripts/image_text_extractor/batch_extractor.py <目录路径> -o result.md
python scripts/image_text_extractor/batch_extractor.py <目录路径> --json
```

按文件名字母序处理；批量模式下图片统一汇入 `ocr_images` 由 AI 逐张识别；建议每次不超过 100 个文件；建议指定 `-o` 保存结果。

## 图片文字提取（AI 视觉法）

1. **全局识别**：用 `read_image` 识别图片，prompt 中要求识别所有文字（标题、正文、注释、水印），保持原结构与排版。
2. **数字二次聚焦校验**（静默执行，不向用户展示过程）：对所有关键数字串（手机号、订单号、金额、日期）做第二轮聚焦识别——prompt 只要求识别该数字区域并逐位描述视觉形状（封闭圆圈数、开口方向、弧线走向），两轮一致则确认，不一致标注 `[待确认：第一轮X，第二轮Y]`；无法确认的字符用 `[?]` 标注并给 2 个备选。
3. **易混淆数字速查**：8=上下两个封闭圆圈；6=仅下方一个圆圈、顶部左弯；9=仅上方一个圆圈；0=完整封闭椭圆；3=右侧开口两弧；5=顶部横线+左竖线+下圆弧。

## 注意事项

- 识别准确性受图片清晰度、字体、背景影响；关键数字串必须两轮识别
- 表格提取用 pymupdf `find_tables()`，复杂表格（合并/嵌套单元格）效果可能不佳
- 保持原文段落结构与标题层级输出 Markdown
- 建议 < 50MB 的文件；处理内容仅在当前会话使用
