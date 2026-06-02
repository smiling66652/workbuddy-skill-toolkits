---
name: 二级：Word处理
---

# 二级：Word处理（DOCX）

**适用场景**：用户需要创建/编辑Word文档、添加格式/表格/图片、批量生成合同/报告

---

## 工具对比

| 工具 | 格式保留 | 模板渲染 | 速度 | 推荐场景 |
|------|---------|---------|------|------------|
| **python-docx** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 快 | 创建/编辑DOCX（推荐） |
| **docx skill** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 中 | 自然语言操作Word |
| **pandoc** | ⭐⭐⭐⭐⭐ | ⭐⭐ | 中 | 格式转换 |

---

## 三级执行：python-docx（推荐）

**触发词**：创建Word、写个Word文档、编辑Word、批量生成合同

### 安装

```bash
pip install python-docx
```

### 创建新文档

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 创建文档
doc = Document()

# 添加标题
doc.add_heading("报告标题", level=1)

# 添加段落
p = doc.add_paragraph("这是正文内容。")
p.add_run("这是加粗文字").bold = True
p.add_run("这是斜体文字").italic = True

# 添加指定格式的文本
run = p.add_run("红色文字")
run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
run.font.size = Pt(14)

# 添加表格
table = doc.add_table(rows=3, cols=3)
table.style = 'Light Grid Accent 1'
table.cell(0, 0).text = "姓名"
table.cell(0, 1).text = "年龄"
table.cell(1, 0).text = "张三"
table.cell(1, 1).text = "25"

# 添加图片
doc.add_picture("image.png", width=Inches(4))

# 设置段落对齐
for para in doc.paragraphs:
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 保存
doc.save("output.docx")
```

### 编辑现有文档

```python
from docx import Document

# 打开现有文档
doc = Document("input.docx")

# 读取所有文字
full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)
print("\n".join(full_text))

# 修改文字
for para in doc.paragraphs:
    if "旧文字" in para.text:
        for run in para.runs:
            if "旧文字" in run.text:
                run.text = run.text.replace("旧文字", "新文字")

# 添加新段落
doc.add_paragraph("这是新添加的段落。")

# 保存修改
doc.save("modified.docx")
```

### 使用模板（批量生成）

```python
from docx import Document
import jinja2
import os

# 方法1：简单替换
doc = Document("template.docx")
for para in doc.paragraphs:
    if "{{name}}" in para.text:
        para.text = para.text.replace("{{name}}", "张三")
    if "{{age}}" in para.text:
        para.text = para.text.replace("{{age}}", "25")
doc.save("output_张三.docx")

# 方法2：用Jinja2 + python-docx-template（更高级）
# pip install docxtpl
from docxtpl import DocxTemplate

doc = DocxTemplate("template.docx")
context = {
    "name": "张三",
    "age": 25,
    "city": "北京",
    "items": [
        {"desc": "项目1", "amount": 1000},
        {"desc": "项目2", "amount": 2000},
    ]
}
doc.render(context)
doc.save("output.docx")
```

---

## 三级执行：docx skill（自然语言操作）

**触发词**：用Word写、创建Word文档、Word里加表格

### 使用

```
# 让Agent调用 docx skill
# Agent会自动使用 python-docx 执行操作
```

---

## 使用建议

1. **创建新Word文档** → python-docx
2. **编辑现有Word文档** → python-docx
3. **批量生成（合同/报告）** → DocxTemplate（Jinja2模板）
4. **复杂格式保留** → 使用样式（Styles）而非直接设置格式
5. **大批量生成** → 用模板渲染，避免逐段修改
