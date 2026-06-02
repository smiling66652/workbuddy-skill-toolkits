---
name: 二级：PDF读取
---

# 二级：PDF读取

**适用场景**：用户需要读取PDF内容、提取文字/表格/图片、OCR扫描版PDF

---

## 工具对比

| 工具 | 表格识别 | 公式识别 | 中文支持 | 速度 | 推荐场景 |
|------|---------|---------|---------|------|------------|
| **MinerU** | ⭐⭐⭐⭐⭐ (97%) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中 | PDF→Markdown（推荐） |
| **pdfkit-py** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 快 | 读取/提取/合并/拆分 |
| **PyPDF2** | ⭐ | ⭐ | ⭐⭐⭐ | 快 | 简单读取/合并 |
| **pdfplumber** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | 中 | 表格提取精确 |
| **OCRmyPDF** | N/A | N/A | ⭐⭐⭐⭐⭐ | 慢 | 扫描版PDF+OCR |

> 📊 **最新对比（2025）**：MinerU 表格识别准确率 97%，远超 Marker(82%) 和 Docling(75%)

---

## 三级执行：MinerU（推荐，PDF→Markdown）

**触发词**：读这个PDF、提取PDF文字、PDF转Markdown、这个PDF讲了什么

### 安装

```bash
# 方法1：pip 安装
pip install magic-pdf[full]

# 方法2：下载Release版本（无需编译）
# 访问 https://github.com/opendatalab/MinerU/releases
```

### 使用

```bash
# 命令行转换（自动输出到 ./output/）
magic-pdf -p input.pdf -o ./output

# 转换为Markdown（默认输出格式）
# 输出：./output/input.md + ./output/input/（图片文件夹）

# Python API
python -c "
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
from magic_pdf.data.data_reader_writer import DataWriter
import magic_pdf

# 转换PDF到Markdown
result = magic_pdf.pdf_to_markdown('input.pdf', 'output/')
print(result['markdown_path'])
"
```

### 输出内容

- `output.md` — 正文Markdown（含表格）
- `images/` — 提取的图片
- `tables/` — 表格（CSV格式）
- `formula/` — 公式（LaTeX格式）

---

## 三级执行：pdfkit-py（全能PDF操作）

**触发词**：提取PDF、合并PDF、拆分PDF、PDF转文字

### 安装

```bash
pip install pdfkit-py
# 需要系统安装 wkhtmltopdf（PDF生成用）
```

### 使用

```bash
# 提取文字
pdfkit extract input.pdf -o output.txt

# OCR识别（扫描版PDF）
pdfkit ocr input.pdf -o output.txt

# 合并PDF
pdfkit merge a.pdf b.pdf -o merged.pdf

# 拆分PDF
pdfkit split input.pdf --pages 1-5,10-15 -o part.pdf

# 提取指定页面
pdfkit extract input.pdf --pages 1,3,5 -o pages.txt

# 旋转页面
pdfkit rotate input.pdf --pages 1-5 --degrees 90 -o rotated.pdf

# 填写表单
pdfkit form fill input.pdf form_data.json -o filled.pdf
```

---

## 三级执行：pdfplumber（精确表格提取）

**触发词**：提取PDF表格、这个PDF里的表格

### 安装

```bash
pip install pdfplumber
```

### 使用

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    # 提取第1页文字
    page = pdf.pages[0]
    text = page.extract_text()
    print(text)
    
    # 提取表格
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            print(row)
    
    # 提取图片
    images = page.images
    print(f"找到 {len(images)} 张图片")
```

---

## 三级执行：OCRmyPDF（扫描版PDF+OCR）

**触发词**：OCR这个PDF、扫描版PDF识别、图片PDF转文字

### 安装

```bash
# Windows
pip install ocrmypdf

# 需要安装 Tesseract OCR
# 下载：https://github.com/tesseract-ocr/tesseract/releases
```

### 使用

```bash
# 对扫描版PDF进行OCR（原地修改）
ocrmypdf input.pdf output.pdf

# 指定语言（中文+英文）
ocrmypdf -l chi_sim+eng input.pdf output.pdf

# 只OCR指定页面
ocrmypdf --pages 1-5 input.pdf output.pdf

# 跳过已有文字层（避免重复OCR）
ocrmypdf --skip-text input.pdf output.pdf
```

---

## 使用建议

1. **PDF→Markdown（含表格）** → MinerU（97%准确率）
2. **简单读取/合并/拆分** → pdfkit-py
3. **精确提取表格** → pdfplumber
4. **扫描版PDF+OCR** → OCRmyPDF
5. **大文件（100+页）** → MinerU（自动分块处理）
