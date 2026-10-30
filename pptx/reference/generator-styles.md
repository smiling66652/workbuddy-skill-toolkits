# JSON 驱动批量生成范式与 5 套配色（合并自 pptx-generator）

> 本文档由原 **pptx-generator** 技能包提炼改写并入；生成脚本位于 `scripts/generate_pptx.py`（依赖 `python-pptx`）。
> 适用场景：需要从结构化大纲**一次性批量生成整套 PPT**（封面/目录/章节/内容/图表/表格/时间线等全套页面），且要求产出标准、可编辑的 .pptx。与手工用 OOXML 逐页构建相比，此范式更快、更一致。

## 用法

```bash
python scripts/generate_pptx.py slides.json --out output.pptx
# 也可指定 --style business_blue 覆盖 JSON 内的 style
```

## JSON 结构

```json
{
  "style": "business_blue",
  "footer": "机密",
  "page_numbers": true,
  "output": "report.pptx",
  "slides": [
    {"type": "cover", "title": "标题", "subtitle": "副标题", "variant": "centered"},
    {"type": "section", "title": "第一部分"},
    {"type": "agenda", "title": "目录", "topics": ["主题1", "主题2"], "highlight": 0},
    {"type": "content", "title": "内容页", "items": ["要点1", "要点2"], "columns": 1},
    {"type": "two_column", "title": "双栏", "left": ["左栏"], "right": ["右栏"]},
    {"type": "table", "title": "表格", "headers": ["A","B"], "rows": [[1,2]]},
    {"type": "chart", "title": "图表", "chart_type": "bar|line|pie",
     "categories": ["Q1","Q2"], "series": [{"name":"S1","values":[10,20]}]},
    {"type": "timeline", "title": "时间线",
     "milestones": [{"label":"阶段1","desc":"描述"}]},
    {"type": "quote", "title": "", "quote": "内容", "attribution": "作者"},
    {"type": "image", "title": "图片", "image_path": "img.png", "overlay": false},
    {"type": "summary", "title": "总结", "points": ["要点"], "conclusion": "结论"},
    {"type": "contact", "title": "联系我们", "info": "邮箱/电话"}
  ]
}
```

## 幻灯片类型（11 种）

| 类型 | 功能 |
|------|------|
| cover | 封面，3 种变体：centered / left / split |
| section | 过渡页/章节分隔 |
| agenda | 目录页，支持高亮当前章节 |
| content | 内容页，单栏/双栏、多级列表 |
| two_column | 双栏对比 |
| table | 表格（隔行变色） |
| chart | 柱状/折线/饼图 |
| timeline | 时间线/里程碑 |
| quote | 引用/强调 |
| image | 图片页，普通/全屏叠加两种模式 |
| summary | 总结页，底部结论框 |
| contact | 结尾/联系信息页 |

内置能力：自动页码 + 页脚、渐变色背景、10 色角色调色板、多级列表、错误跳过 + 逐页报告。

## 配色方案（5 套，hex 值与源码一致）

每套配色含 12 个角色位：primary / secondary / accent / highlight / success / warning / text_primary / text_secondary / bg_primary / bg_secondary / gradient_start / gradient_end。

### business_blue（商业汇报，专业稳重）

| 角色 | hex | 角色 | hex |
|------|-----|------|-----|
| primary | #1E3C72 | text_primary | #2C3E50 |
| secondary | #4682B4 | text_secondary | #7F8C8D |
| accent | #FFC107 | bg_primary | #FFFFFF |
| highlight | #E74C3C | bg_secondary | #ECF0F1 |
| success | #27AE60 | gradient_start | #1E3C72 |
| warning | #E67E22 | gradient_end | #3498DB |

### academic_white（学术论文，简洁规范）

| 角色 | hex | 角色 | hex |
|------|-----|------|-----|
| primary | #003366 | text_primary | #333333 |
| secondary | #646464 | text_secondary | #777777 |
| accent | #B22222 | bg_primary | #FFFFFF |
| highlight | #006699 | bg_secondary | #F5F5F5 |
| success | #228B22 | gradient_start | #003366 |
| warning | #B8860B | gradient_end | #006699 |

### creative_purple（创意展示，时尚活力）

| 角色 | hex | 角色 | hex |
|------|-----|------|-----|
| primary | #662D8C | text_primary | #341F47 |
| secondary | #9B59B6 | text_secondary | #88729E |
| accent | #F1C40F | bg_primary | #F8F4FC |
| highlight | #E74C3C | bg_secondary | #EBE1F5 |
| success | #2ECC71 | gradient_start | #662D8C |
| warning | #E67E22 | gradient_end | #9B59B6 |

### tech_dark（技术分享，现代高端）

| 角色 | hex | 角色 | hex |
|------|-----|------|-----|
| primary | #303848 | text_primary | #E6EBF0 |
| secondary | #586478 | text_secondary | #AAB4C3 |
| accent | #00C896 | bg_primary | #3C4455 |
| highlight | #00B4D8 | bg_secondary | #4B5569 |
| success | #2ECC71 | gradient_start | #303848 |
| warning | #F1C40F | gradient_end | #465064 |

### minimal_gray（通用场景，简约百搭）

| 角色 | hex | 角色 | hex |
|------|-----|------|-----|
| primary | #505050 | text_primary | #333333 |
| secondary | #969696 | text_secondary | #999999 |
| accent | #0078D7 | bg_primary | #FAFAFA |
| highlight | #D7503C | bg_secondary | #F0F0F0 |
| success | #3CAA64 | gradient_start | #505050 |
| warning | #D2A028 | gradient_end | #8C8C8C |

## 选型建议

- 商业汇报/路演 → business_blue；论文答辩/学术报告 → academic_white
- 品牌/创意/活动 → creative_purple；技术分享/开发者大会 → tech_dark
- 内部培训/通用文档 → minimal_gray
- 配色也可作为手工 OOXML 构建时的调色参考（直接取上述 hex 值写入主题色）
