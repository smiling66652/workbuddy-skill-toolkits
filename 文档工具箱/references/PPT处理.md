---
name: 二级：PPT处理
---

# 二级：PPT处理（PPTX）

**适用场景**：用户需要生成/编辑PowerPoint演示文稿、批量生成幻灯片、添加图表/动画

---

## 工具对比

| 工具 | 模板支持 | 图表 | 动画 | 推荐场景 |
|------|---------|------|------|------------|
| **python-pptx** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 创建/编辑PPTX（推荐） |
| **pptx skill** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 自然语言操作PPT |
| **deck-generator** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | AI生成精美PPT |

---

## 三级执行：python-pptx（推荐）

**触发词**：做PPT、生成幻灯片、编辑演示文稿、批量生成PPT

### 安装

```bash
pip install python-pptx
```

### 创建新PPT

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# 创建演示文稿
prs = Presentation()

# 添加标题幻灯片
slide_layout = prs.slide_layouts[0]  # 0=标题幻灯片
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "演示文稿标题"
subtitle.text = "副标题"

# 添加内容幻灯片
slide_layout = prs.slide_layouts[1]  # 1=标题+内容
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
title.text = "第一页内容"

# 添加项目符号
body = slide.placeholders[1]
tf = body.text_frame
tf.text = "第一项"

p = tf.add_paragraph()
p.text = "第二项"
p.level = 1  # 二级项目符号

p = tf.add_paragraph()
p.text = "第三项"
p.level = 2  # 三级项目符号

# 添加图片
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 6=空白
left = Inches(1)
top = Inches(1)
slide.shapes.add_picture("image.png", left, top, width=Inches(5))

# 添加表格
slide = prs.slides.add_slide(prs.slide_layouts[6])
rows, cols = 3, 3
left = Inches(2)
top = Inches(2)
width = Inches(6)
height = Inches(2)
table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 填充表格
table.cell(0, 0).text = "姓名"
table.cell(0, 1).text = "年龄"
table.cell(1, 0).text = "张三"
table.cell(1, 1).text = "25"

# 保存
prs.save("output.pptx")
```

### 编辑现有PPT

```python
from pptx import Presentation

# 打开现有PPT
prs = Presentation("input.pptx")

# 读取所有文字
for i, slide in enumerate(prs.slides):
    print(f"=== 第 {i+1} 页 ===")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                print(para.text)

# 修改文字
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                if "旧文字" in para.text:
                    para.text = para.text.replace("旧文字", "新文字")

# 添加新幻灯片
new_slide = prs.slides.add_slide(prs.slide_layouts[1])
new_slide.shapes.title.text = "新添加的页面"

# 保存修改
prs.save("modified.pptx")
```

### 使用模板（批量生成）

```python
from pptx import Presentation

# 打开模板
prs = Presentation("template.pptx")

# 替换文字（简单方案）
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                para.text = para.text.replace("{{name}}", "张三")
                para.text = para.text.replace("{{age}}", "25")

# 保存生成的PPT
prs.save("output_张三.pptx")
```

---

## 三级执行：deck-generator（AI生成精美PPT）

**触发词**：AI生成PPT、自动生成幻灯片、漂亮的PPT

### 安装

```bash
# 需要安装 deck-generator 依赖
# 具体安装方法参考原 skill
```

### 使用

```python
# 让Agent调用 deck-generator skill
# 会自动根据内容生成精美排版的PPT
```

---

## 使用建议

1. **创建新PPT** → python-pptx
2. **编辑现有PPT** → python-pptx
3. **AI生成精美PPT** → deck-generator
4. **批量生成（替换模板变量）** → python-pptx + 字符串替换
5. **添加图表** → python-pptx 的 `slide.shapes.add_chart()`
6. **动画效果** → python-pptx 支持有限，复杂动画建议手动在PowerPoint中添加
