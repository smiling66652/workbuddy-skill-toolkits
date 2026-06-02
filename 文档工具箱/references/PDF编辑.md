---
name: 二级：PDF编辑
---

# 二级：PDF编辑

**适用场景**：用户需要编辑PDF内容、修改文字、添加注释/图片/水印、用自然语言描述修改

---

## 工具对比

| 工具 | 自然语言编辑 | 精确编辑 | 添加水印 | 加密 | 推荐场景 |
|------|------------|---------|---------|------|------------|
| **pdfkit-py** | ✅ | ✅ | ✅ | ✅ | 全能PDF编辑（推荐） |
| **PyPDF2** | ❌ | ✅（基础） | ❌ | ✅ | 简单编辑/加密 |
| **reportlab** | ❌ | ✅ | ✅ | ❌ | 生成新PDF页面 |

---

## 三级执行：pdfkit-py（推荐）

**触发词**：编辑PDF、修改PDF内容、PDF加文字、PDF加水印、PDF加密

### 安装

```bash
pip install pdfkit-py
```

### 基础编辑

```bash
# 添加文字（指定坐标）
pdfkit annotate input.pdf --text "这是新加的文字" --page 1 --x 100 --y 200 -o output.pdf

# 添加图片
pdfkit annotate input.pdf --image logo.png --page 1 --x 50 --y 50 -o output.pdf

# 添加水印（文字）
pdfkit watermark input.pdf --text "机密" --opacity 0.3 -o watermarked.pdf

# 添加水印（图片）
pdfkit watermark input.pdf --image watermark.png -o watermarked.pdf

# 加密PDF
pdfkit encrypt input.pdf --password 123456 -o encrypted.pdf

# 解密PDF
pdfkit decrypt encrypted.pdf --password 123456 -o decrypted.pdf

# 添加注释/高亮
pdfkit annotate input.pdf --highlight --page 1 --text "重要内容" -o output.pdf
```

### 自然语言编辑（实验性）

```bash
# 用自然语言描述修改（需要LLM辅助）
# 步骤1：提取PDF内容
pdfkit extract input.pdf -o content.txt

# 步骤2：让LLM根据自然语言指令修改内容
# （这一步由Agent调用LLM完成）

# 步骤3：将修改后的内容写回PDF
# （需要生成新的PDF，不能完全"原地修改"）
```

> ⚠️ **注意**：PDF格式不支持真正的"原地编辑"，自然语言编辑本质上是：提取→修改→生成新PDF

---

## 三级执行：PyPDF2（基础编辑）

**触发词**：合并PDF、拆分PDF、加密PDF、旋转页面

### 安装

```bash
pip install PyPDF2
```

### 使用

```python
from PyPDF2 import PdfReader, PdfWriter

# 读取PDF
reader = PdfReader("input.pdf")
writer = PdfWriter()

# 合并PDF
reader2 = PdfReader("input2.pdf")
for page in reader.pages:
    writer.add_page(page)
for page in reader2.pages:
    writer.add_page(page)

# 加密
writer.encrypt("password123")

# 保存
with open("merged_encrypted.pdf", "wb") as f:
    writer.write(f)
```

---

## 三级执行：reportlab（生成新PDF页面）

**触发词**：生成PDF、创建PDF、PDF加一页

### 安装

```bash
pip install reportlab
```

### 使用

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 创建PDF
c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4

# 添加文字
c.drawString(100, height - 100, "这是新加的文字")

# 添加图片
c.drawImage("logo.png", 100, height - 200, width=100, height=50)

# 保存
c.save()
```

---

## 使用建议

1. **全能编辑（推荐）** → pdfkit-py
2. **简单合并/拆分/加密** → PyPDF2
3. **生成新PDF页面** → reportlab
4. **自然语言编辑** → 提取内容→LLM修改→生成新PDF（PDF格式限制）
