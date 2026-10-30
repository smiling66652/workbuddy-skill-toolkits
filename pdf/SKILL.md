---
name: pdf
agent_created: true
version: 1.0.1
display_name: PDF 文档处理
display_name_en: PDF Document Processing
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, handling forms, OCR/scanned-page recognition, encryption/watermarking/redaction, page operations, format conversion, and image text extraction. Use when the user mentions PDF, OCR, scanned documents, or needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale. 触发词：PDF、读这个PDF、提取PDF文字、OCR、扫描件、扫描版、文字提取、表格提取、拆分、合并、加密、解密、水印、涂黑、脱敏、表单填写、数字签名、转图片、批量处理、pdfkit。
description_zh: （本地 PDF 工具箱：与平台内置 PDF 流水线分工——内置走云端编排，本包走本地 pypdf/pdfplumber/reportlab 与 pdfkit 工具链，二者互补）PDF 文档处理工具，支持文本与表格提取、图片/扫描版零依赖文字提取与 OCR、PDF 创建、合并拆分、页面操作、格式转换、加密解密、水印与涂黑脱敏、表单填写、数字签名及批量分析。
description_en: Process PDF documents by extracting text and tables, zero-dependency image/scanned-page text extraction with AI vision OCR, creating, merging, splitting, page operations, conversion, encryption, watermarks, redaction, filling forms, digital signing, and batch analysis.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

## Setup and verification

Run commands from this skill directory, or use absolute script paths.
Install Python dependencies with `python -m pip install -r requirements.txt`.
PDF rendering also requires Poppler (`brew install poppler` on macOS, or
`apt-get install poppler-utils` on Debian/Ubuntu).
The bundled form scripts require pypdf 6.21.1 or newer within major version 6;
they do not patch library internals.

After creating or filling a PDF, render the output and inspect the affected
pages for missing text, clipping, incorrect selections and alignment. Re-read
interactive field values as well. A successful write alone is not verification.
For non-interactive forms, use `pages.json` from the image converter to obtain
the displayed page dimensions needed by `fields.json`.

For regression tests, install `requirements-dev.txt` and run
`python -m unittest discover -s scripts -p '*_test.py'`.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    # Separate identically named fields from different source documents.
    if reader.get_fields():
        reader.add_form_topname(f"document_{len(writer.pages) + 1}")
    writer.append(reader)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.append(reader, pages=[i])
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

writer.append(reader)
writer.pages[0].rotate(90)  # Rotate page 1 clockwise; retain other pages and forms

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
writer.append(reader)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

writer.append(reader)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.append(reader)`; namespace duplicate form names |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## Next Steps

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For troubleshooting guides, see reference.md
- For the full-featured pdfkit CLI (50 commands: smart_edit, OCR, IR, redact, sign, etc.), see reference/pdfkit-api.md — CLI source in scripts/pdfkit_toolkit/
- For zero-dependency image/scanned-page text extraction (AI vision OCR) and batch extraction, see reference/image-text-extraction.md — scripts in scripts/image_text_extractor/

## 合并来源

本技能由以下技能包合并而成（原包已归档至 `C:/Users/Matebook/.workbuddy/.archived_skills/`）：

- 来自 **pdfkit-py**（全能 PDF CLI 工具箱）：
  - `reference/pdfkit-api.md` — 50 个命令的 API 详解与组合技术（阅读分析/编辑修改/组织变换/安全表单/IR 中间表示/元工具），由原 SKILL.md 提炼并入
  - `scripts/pdfkit_toolkit/` — pdfkit CLI 完整源码（入口 `scripts/pdfkit_toolkit/pdfkit.py`，含 setup 脚本与依赖清单）
- 来自 **pdf-image-text-extractor**（零依赖图片/扫描版文字提取）：
  - `reference/image-text-extraction.md` — 扫描版 PDF 渲染 + AI 视觉识别、pymupdf 表格结构化提取、批量目录处理的方法论（由原 SKILL.md 提炼改写）
  - `scripts/image_text_extractor/` — `pdf_text_extractor.py`、`batch_extractor.py`、`record.py`（红狐 API Key 鉴权）、`changelog.py`
