---
name: 联网工具箱
description: >
  统一联网操作工具箱（三级层级结构）：
  一级：分析用户需求（搜索/抓取/自动化/总结/生成）
  二级：选择最佳工具（Playwright/Agent Browser/Human Browser/MiniMax CLI）
  三级：执行指令并返回结果。
  集成最佳工具：Playwright CLI、Agent Browser、Human Browser、MiniMax CLI、cli-anything-hub。
version: 4.0.0
author: WorkBuddy 整合版
---

# 联网工具箱

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断用户要做什么（搜索/抓取/自动化/总结/生成）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 跳转二级 | 推荐工具 |
|---------|---------|---------|
| 搜索信息、查资料 | [二级：智能搜索](references/智能搜索.md) | WebSearch / WebFetch |
| 抓取网页内容、提取正文 | [二级：网页抓取](references/网页抓取.md) | 五阶段智能管道 |
| 操作网页、点击、填表、截图 | [二级：浏览器自动化](references/浏览器自动化.md) | Playwright CLI（推荐） |
| 需要绕过 Cloudflare 反爬 | [二级：浏览器自动化](references/浏览器自动化.md) | Human Browser（97%绕过率） |
| AI驱动的无头浏览器操作 | [二级：浏览器自动化](references/浏览器自动化.md) | Agent Browser |
| 总结文章/视频/音频 | [二级：内容总结](references/内容总结.md) | summarize / WebFetch |
| 需要AI生成答案的搜索 | [二级：AI搜索](references/AI搜索.md) | Tavily / Perplexity |
| 看YouTube视频内容 | [二级：YouTube转录](references/YouTube转录.md) | youtube-transcript-api |
| 获取最新新闻 | [二级：新闻摘要](references/新闻摘要.md) | RSS聚合 |
| 生成图片/视频/语音 | [二级：AI生成](references/AI生成.md) | MiniMax CLI（mmx） |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 搜索 | 搜索、查一下、找资料、有什么最新进展 | [二级：智能搜索](references/智能搜索.md) |
| 抓取 | 抓取、提取正文、爬取、这个页面内容 | [二级：网页抓取](references/网页抓取.md) |
| 浏览器自动化 | 打开网页、点击、填表、截图、登录后操作 | [二级：浏览器自动化](references/浏览器自动化.md) |
| 总结 | 总结这个页面、这篇论文讲了什么、这个视频说了什么 | [二级：内容总结](references/内容总结.md) |
| AI生成 | 生成图片、画一张、生成视频、转文字 | [二级：AI生成](references/AI生成.md) |

---

## 通用规则

### 信息核实
- **一手来源优先**：搜索引擎是发现工具，不是证明工具
- 政策/法规 → 发布机构官网
- 企业公告 → 公司官方新闻页
- 学术声明 → 原始论文/机构官网
- 找不到官网时，用权威媒体原创报道（需向用户说明来源）

### 站点经验积累
- 操作成功后，将新站点/新模式写入 `references/site-patterns/{domain}.md`
- 只写经过验证的事实，不写未确认的猜测
- 经验标注发现日期，作为"可能有效的提示"而非保证

### 并行策略
- 多个独立目标时，用子 Agent 分治并行执行
- 每个子 Agent 在自己后台 tab 中操作，无竞态风险
- 主 Agent 写 prompt 时描述**目标**，不过度指定**步骤**

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/智能搜索.md` | 需要处理搜索请求时 |
| `references/网页抓取.md` | 需要抓取网页内容时 |
| `references/浏览器自动化.md` | 需要操作网页/绕过反爬时 |
| `references/内容总结.md` | 需要总结文章/视频/音频时 |
| `references/AI搜索.md` | 需要AI生成答案的搜索时 |
| `references/YouTube转录.md` | 需要获取YouTube视频内容时 |
| `references/新闻摘要.md` | 需要获取最新新闻时 |
| `references/AI生成.md` | 需要生成图片/视频/语音时 |
| `references/site-patterns/{domain}.md` | 确定目标网站后，读取对应站点经验 |
| `references/cli-hub.md` | 需要搜索/安装专业CLI工具时 |
