---
name: 二级：PDF生成
---

# 二级：PDF生成

**适用场景**：用户需要生成精美排版的PDF、报表、证书、发票等

---

## 工具对比

| 工具 | 排版能力 | 中文支持 | 速度 | 推荐场景 |
|------|---------|---------|------|------------|
| **reportlab** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 快 | 复杂排版（推荐） |
| **WeasyPrint** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中 | HTML/CSS生成PDF |
| **fpdf2** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 非常快 | 简单PDF/多语言 |
| **pdfkit** | ⭐⭐⭐ | ⭐⭐⭐ | 中 | WkHTMLToPDF封装 |

---

## 三级执行：reportlab（推荐，复杂排版）

**触发词**：生成PDF、做成PDF、生成报表、生成证书

### 安装

```bash
pip install reportlab
```

### 基础使用

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体（必须！）
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))

# 创建PDF
c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4

# 添加标题
c.setFont("SimSun", 20)
c.drawString(100, height - 100, "报告标题")

# 添加正文
c.setFont("SimSun", 12)
c.drawString(100, height - 150, "这是正文内容，支持中文。")

# 添加图片
c.drawImage("logo.png", 100, height - 300, width=100, height=50)

# 保存
c.save()
```

### 高级：表格+图表

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# 创建文档
doc = SimpleDocTemplate("table_report.pdf")
elements = []

# 表格数据
data = [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"],
]

# 创建表格
table = Table(data, colWidths=[4*cm, 3*cm, 4*cm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('FONTSIZE', (0, 1), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)

# 生成PDF
doc.build(elements)
```

### 中文支持（完整方案）

```python
# 方法1：使用系统字体（Windows）
pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))

# 方法2：下载开源字体
# 下载 Noto Sans CJK：https://github.com/googlefonts/noto-cjk
pdfmetrics.registerFont(TTFont('NotoSansCJK', 'NotoSansCJK-Regular.ttc'))

# 方法3：使用 fpdf2（内置CJK支持）
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.add_font("NotoSansCJK", "", "NotoSansCJK-Regular.ttf", uni=True)
pdf.set_font("NotoSansCJK", size=12)
pdf.cell(200, 10, txt="中文内容", ln=True, align="C")
pdf.output("output.pdf")
```

---

## 三级执行：WeasyPrint（HTML/CSS → PDF）

**触发词**：用HTML生成PDF、网页打印成PDF

### 安装

```bash
pip install weasyprint
```

### 使用

```python
from weasyprint import HTML, CSS

# 从HTML字符串生成
html_string = """
<html>
<head>
    <style>
        @font-face { font-family: 'SimSun'; src: url('simsun.ttc'); }
        body { font-family: 'SimSun'; }
        h1 { color: navy; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid black; padding: 8px; }
    </style>
</head>
<body>
    <h1>报告标题</h1>
    <table>
        <tr><th>姓名</th><th>年龄</th></tr>
        <tr><td>张三</td><td>25</td></tr>
    </table>
</body>
</html>
"""
HTML(string=html_string).write_pdf("output.pdf")

# 从URL生成
HTML('https://example.com').write_pdf("webpage.pdf")

# 从文件生成
HTML(filename='input.html').write_pdf("output.pdf")
```

---

## 三级执行：fpdf2（简单快速）

**触发词**：快速生成PDF、多语言PDF

### 安装

```bash
pip install fpdf2
```

### 使用

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

# 添加字体（支持CJK）
pdf.add_font("NotoSansCJK", "", "NotoSansCJK-Regular.ttf", uni=True)
pdf.set_font("NotoSansCJK", size=14)

# 添加文字
pdf.cell(200, 10, txt="中文内容", ln=True, align="C")
pdf.cell(200, 10, txt="English content", ln=True, align="C")

# 添加图片
pdf.image("logo.png", x=10, y=30, w=50)

# 保存
pdf.output("output.pdf")
```

---

## 使用建议

1. **复杂排版（报表/证书/发票）** → reportlab
2. **HTML/CSS生成PDF** → WeasyPrint
3. **简单PDF/多语言** → fpdf2
4. **中文支持** → 必须注册中文字体，否则乱码
5. **大批量生成** → fpdf2（最快）
