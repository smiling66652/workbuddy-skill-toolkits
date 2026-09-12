---
name: 二级：搜索层 API 选型
---

# 二级：搜索层 API 选型

**适用场景**：内置 WebSearch 不够用时——需要批量搜索、结构化 SERP、语义检索、或让 Agent 自己反复搜

> **默认不需要读这一页**。
> 绝大多数"搜个资料"用内置 **WebSearch** 就够了，它零配置、零成本。
> 只有当你遇到下面任一情况，才来看 API 选型：
> - 要批量跑几十上百次搜索（内置搜索不适合高频）
> - 要结构化 SERP（知识图谱、答案框、排名位置）
> - 要"找和这个相似的东西"这类语义检索
> - 要跳过搜索、直接抓整个站（Firecrawl Crawl）
>
> **本机现状：`TAVILY_API_KEY` / `EXA_API_KEY` / `SERPER_API_KEY` / `JINA_API_KEY` 目前全都未设置**，
> 所以下面这些现在都不可直接用——如需启用，先申请 key 并写入环境变量。

---

## 一张表看懂（2026 年公开数据，用前请复核官网）

| 服务 | 免费额度 | 付费 | 它真正擅长什么 | 关键限制 |
|---|---|---|---|---|
| **WebSearch**（内置） | 无限制 | 无 | 通用发现、给 Agent 定位来源 | 不可编程批量、无结构化字段 |
| **Jina Reader** `r.jina.ai` | 无 key → 20 RPM | 按 token 计（约 $0.05/百万 token） | URL → 干净 Markdown，省 token | **不渲染 JS**；不解决反爬 |
| **Tavily** | 1,000 credits / 月 | $0.008 / credit | LLM 原生搜索，返回带相关度评分的段落 | PAYG 规模化后偏贵（10 万次 ≈ $800） |
| **Exa** | 见下方注¹ | Search $7 / 1k；Contents $1 / 1k 页 | **语义**检索（"找类似这个的"） | 时效性弱于实时搜索 |
| **Serper** | 新账号 2,500 次 | $1 / 1k，高阶 $0.30 / 1k | 便宜的原始 Google SERP | **只搜不抓**，得配抓取工具 |
| **Brave Search** | 新用户 $5/月 credits（约 1k 次）² | $5 / 1k | 独立索引（40B+ 页），无 Google/Bing 依赖 | 已取消新用户免费层 |
| **Firecrawl** | 500 credits（一次性） | $16–19 / 月起 | 整站 Crawl、Map、结构化抽取 | 积分按月不结转；单价偏高 |

¹ Exa 免费额度在不同来源里是 **1,000 / 月** 和 **20,000 / 月** 两个说法，**冲突，以官网为准**。
² Brave 老用户被保留原有免费计划，新用户走 $5/月 credit 制。

**已死**：**Bing Web Search API 已于 2025-03 停止服务**，Azure 未给等价替代。任何引用它的老方案都要迁移（→ Brave / Serper / SerpAPI）。

---

## 选型决策树

```
需要搜索？
├─ 只是"搜个东西"、次数不多
│   └─ → 内置 WebSearch（什么都别装）
├─ 已有 URL，只要正文
│   └─ → Jina（省 token）或 curl（要原始 HTML）或 WebFetch
│       ⚠️ 页面是 SPA/React/Notion 商城 → Jina 会返回残缺内容 → 改用 CDP 直连
├─ 要大批量搜索 / 结构化 SERP
│   └─ → Serper（最便宜）或 Brave（独立索引）
│       再配 Jina / Firecrawl 抓正文 ←「搜索 + 抓取」两段式
├─ 要"找概念相关"而非关键词命中
│   └─ → Exa
├─ 要一次性抓整个站 / 站内 URL 发现
│   └─ → Firecrawl（Crawl / Map），或直接 scrapy（免费，见 网页抓取.md）
└─ 要给 Agent 一个能自己反复搜的工具
    └─ → Tavily
```

---

## 两段式架构（最重要的一条经验）

搜索 API **只负责给 URL**，正文还要另一步。这是行业标准做法，也解释了工具箱为什么把搜索和抓取分成两层：

```
搜索 API（Serper / Brave / Tavily）  →  一堆 URL
              ↓
抓取层（Jina / curl / CDP 直连）     →  正文
              ↓
LLM 消费
```

**别指望一个 API 全包**。唯一的例外是 Firecrawl 的 search 端点（搜索 + 抓全文一体），代价是单价更高。

---

## 各家取舍与坑

### Jina Reader
- ✅ 零配置（URL 前加 `r.jina.ai/`）、无 key 可用、注册送 1000 万 token
- ✅ 已被 **Elastic 收购**，官方承诺继续维护 Reader / Embeddings / Reranker
- ❌ **不执行 JavaScript** —— 这是架构性限制，不是 bug。React / Vue / Next.js 客户端渲染页、Notion 托管文档、Shopify 商品页会返回**只有导航和页脚、没有正文**的 Markdown。官方不会改（改了成本模型就崩）
- ❌ 不绕反爬，被拦就报错
- ❌ 搜索端点 `s.jina.ai` 只返回前 5 条全文，不可配置
- ⚠️ 按 token 计费 → 页面长短导致成本波动 10 倍以上，预算难预测

### Tavily
- ✅ 上手最快，LangChain / n8n 教程默认选择
- ✅ `basic` 1 credit / `advanced` 2 credits，免费 1,000/月 够原型
- ❌ 高频场景贵（$0.008/credit）

### Exa
- ✅ 语义检索独一份，`@web` 类功能的常见底座
- ❌ 自建索引有刷新节奏 → **突发新闻类查询会滞后于实时搜索**

### Serper
- ✅ 最便宜的原始 SERP；返回知识图谱、答案框等结构化对象
- ❌ 完全不做内容提取，必须自己配抓取

### Firecrawl
- ✅ **AGPL-3.0 开源，可自托管**（有数据主权要求时是唯一选择）
- ✅ 支持 PDF / DOCX，能先 click / scroll 再抽取
- ✅ 官方 MCP：`npx -y firecrawl-mcp`
- ❌ 积分一次性的，按月不结转；深爬大站会快速烧积分

---

## 本机启用步骤（如需）

```bash
# 1. 申请 key 后写入环境变量（示例：Tavily）
setx TAVILY_API_KEY "tvly-xxxx"        # Windows，重开 shell 生效

# 2. 装 SDK
"C:/Users/Matebook/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -m pip install tavily-python
```

未配 key 时**不要假装能用**——直接回退到内置 WebSearch + 抓取层，这条链本机完全可用。

---

## 现有工具的补充说明（`cli-anything-hub`）

`cli-hub search <关键词>` 用来发现"有没有现成的专业 CLI 工具"，不是网页搜索工具。它在 PyPI 上真实存在（已核实），安装：

```bash
pip install cli-anything-hub
cli-hub search image / list / install gimp
```

**注意区分**：`cli-hub` 搜的是**命令行软件**，不是网页内容。想搜网页用 WebSearch。
