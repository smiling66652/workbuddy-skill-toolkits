---
name: image-to-editable-pptx
description: |
  把含文字的图片/截图/信息图/海报变成可编辑的 PowerPoint：OpenCV inpaint 按文字颜色精确擦除笔画
  （保留彩色 pill、底条、卡片底色），logo 作图片切片 1:1 还原，其余文字作可编辑文本框叠加。全本地、不依赖 imagegen。
  触发词：图片转可编辑 PPT、图片转 ppt、截图转 ppt、信息图转 ppt、海报转可编辑、image to editable pptx
version: "2.0.0"
author: smiling66652
title: 图片转可编辑 PPTX
summary: 把一张含文字的图片/截图变成可编辑的 PowerPoint：底层用 OpenCV inpaint 按文字颜色精确擦除笔画（保留彩色 pill
  / 底条 / 卡片底色），品牌 logo 作图片切片 1:1 还原，其余文字作不透明可编辑 Arial 文本框叠加。全本地、不依赖 imagegen。
read_when:
  - 用户要把图片 / 截图 / 信息图 / 海报变成可编辑的 PPT
  - 用户说"把这张图变成可以改字的 PPT"、"图片转可编辑 ppt"、"提取图里的文字做成 ppt"
  - 图片里有大量结构化文字 + 品牌 logo，需要文字可改、版式还原
triggers:
  - 图片转可编辑
  - 图片转 ppt
  - 截图转 ppt
  - 信息图转 ppt
  - 海报转可编辑
  - image to editable pptx
  - convert image to powerpoint
---

# 图片转可编辑 PPTX

把含文字的图片变成「可见且可编辑」的 PowerPoint。核心难点：直接贴整图 → 文字不可改；整图上叠文字 → 和原图文字重叠双影。本 skill 用三段式解决。

## 适用判断

- 图片是信息图 / 数据卡片 / 概览图 / 海报，文字多且排版规整。
- 用户要「文字能改」+「看起来像原图」。
- 不适用：纯照片、无文字图、要求像素级还原字体的场景（字体无法 1:1，只能近似）。

## 三段式流程

### 第 1 步：标注文字 schema

为图上每段文字记录一条：`text, x, y, w, h, size_pt, color_hex, bold, align`。坐标是源图像素，左上角原点。另列一个 `logos` 集合，放品牌 logo 文字（这些当图片处理，不当文字）。

- 来源：可用 OCR（如 paddleocr / tesseract）初定位，再人工微调；或直接肉眼标注。
- schema 格式见 `references/text_schema.example.json`。
- 颜色用取色器从原图取（PS / GIMP / 在线工具）。

### 第 2 步：两遍 inpaint 擦除文字笔画（保底色、近无痕）

`references/inpaint_text.py`（默认两遍，`--single` 退回单遍）：

**Pass 1** — 对每条非 logo 文字，在其 bbox 内对「到文字颜色的距离图」做 **Otsu 自适应阈值**（比固定阈值鲁棒，自动适应深色字/白字/彩色字），dilate 3 iter，`cv2.inpaint(TELEA, radius=5)` 擦除主体笔画 + 抗锯齿边缘。
**Pass 2** — 检测 pass 1 后**仍接近文字色**的残留像素（漏掉的笔画核心），dilate 2 iter，`cv2.inpaint(NS, radius=3)` 从已干净邻域自然填充。

实测残留率：单遍固定阈值 3.1% → 两遍 0.72%（降 76%）。

**最关键的一点**：mask 只覆盖笔画像素，**绝不覆盖整个 bbox**。很多文字坐在彩色 pill / 深色底条 / 卡片底色上，整 bbox 擦除会把底色一起抹掉（曾把蓝色 ECI pill 抹成白色）。按颜色距离只抓笔画，底色完好保留。logo 文字跳过不擦（下一步作图片切片）。

### 第 3 步：叠加可编辑层

`references/build_editable_pptx.py`：
- 底层：贴上第 2 步的干净背景图。
- logo 层：从**原图**（不是 inpaint 后的）按 bbox 裁切 logo，`add_picture` 贴回原坐标，品牌字 1:1 还原。
- 文字层：其余每条文字作不透明（alpha=100）Arial 文本框，`add_textbox` 放在原坐标，可改字 / 改色 / 改字号。

### QA

- 渲染：`references/render_pptx.ps1` 用 PowerPoint COM 把 slide1 导出 PNG。
- 对比：`references/qa_compare.py` 生成 side_by_side / blend / diff_heatmap / SSIM。
- 验收：logo 区域 diff 应接近 0；文字区域 diff 主要来自 Arial vs 原字体的度量差（不可消除，可接受）。SSIM 0.75+ 为合格。

## 关键技巧（踩坑总结）

1. **OpenCV 中文路径**：`cv2.imread` / `cv2.imwrite` 不支持非 ASCII 路径（中文、日文等）。用 `cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)` 读，`ok, buf = cv2.imencode(ext, img); buf.tofile(path)` 写。务必封装成 `imread_unicode` / `imwrite_unicode`。
2. **笔画 mask vs 整 bbox mask**：这是成败关键。整 bbox mask 会擦掉彩色底块（如把蓝色 pill 抹成白色）。颜色距离阈值 90 对绝大多数场景够用；dilate 2 iter 覆盖抗锯齿边缘。
3. **两遍 inpaint 比单遍干净得多**：pass1 用 Otsu 自适应阈值（在「到文字色的距离图」上做 Otsu，比固定阈值鲁棒）+ TELEA r5 擦主体；pass2 检测残留像素（仍接近文字色的点）+ NS r3 精修。残留率 3.1%→0.72%。Otsu 比 fixed-90 抓得更全（coverage 9.7%→17.3%），dilate 用 3 是甜点（4 反而残留升高）。
4. **logo 切片 vs 文字渲染**：品牌 logo 是艺术字，Arial 重画会失真。从原图裁切贴回最忠实。代价：logo 不可编辑文字（但艺术字本就该是图）。
4. **PowerPoint COM 渲染**：`Presentations.Open(path, $true, $false, $false)`（只读、无标题、无窗口）→ `Slides.Item(1).Export(out, 'PNG', w, h)` → `Close()` / `Quit()` + `ReleaseComObject`。比 LibreOffice 更稳（装了 Office 时）。注意 finally 里一定要 Quit 释放，否则 POWERPNT.EXE 残留。
5. **slide 尺寸**：保持源图宽高比。13.333in 宽 × (H/W×13.333) 高，多数 16:9 图正好 7.5in。
6. **文本框命名**：`add_textbox` 后设 `shape.name = 'editable__' + 前缀`，PowerPoint 选择窗格里易定位。
7. **字体差异是固有的**：不要试图靠调字号完全消除 diff。Arial 与原图字体度量不同，强行调可能越调越偏。SSIM 0.8 左右已是最佳折中。

## 命令模板

```bash
# 假设 schema.json 已备好，源图 source.png 在当前目录
python references/inpaint_text.py schema.json source.png outputs/background.png
python references/build_editable_pptx.py schema.json source.png outputs/background.png outputs/result.pptx
powershell -File references/render_pptx.ps1 -Pptx outputs/result.pptx -OutPng outputs/preview.png -Width 1672 -Height 941
python references/qa_compare.py source.png outputs/preview.png outputs/qa
```

## 依赖

- Python: opencv-python, numpy, python-pptx, scikit-image, Pillow
- PowerShell + Microsoft PowerPoint（用于渲染 QA；无 Office 时可用 LibreOffice `soffice --headless --convert-to png`）

## 已知局限

- 字体只能近似（Arial），无法 1:1 还原原图字体。
- 复杂背景（渐变 / 纹理 / 照片底）的 inpaint 可能有涂抹痕迹，需局部调大 radius 或改用 NS 算法。
- 手写体 / 艺术字 logo 必须当图片切片，不能当可编辑文字。
- 多行文字的行距 / 字距与 PowerPoint 默认可能不同，必要时逐行拆成独立文本框。
