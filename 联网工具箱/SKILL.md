---
name: 联网工具箱
description: >
  所有联网操作的唯一入口。搜索、查资料、查网页、抓取网页、提取正文、浏览器自动化、打开网页、点击、填表、截图、
  登录后操作、需要登录态的网站、下载文档、文库下载、付费文档、下载教材、找电子书、找 PDF、搜 ISBN、
  看视频内容、YouTube 转录、最新新闻、每日简报、RSS、
  遇到反爬、Cloudflare、验证码、403、需要绕过拦截、
  找回"我之前看过的那个页面"、访问组织内部系统、
  以及任何需要真实浏览器环境的联网任务。
  本技能是编排层：先分层判断再分派，底层实现（CDP 直连 / 本地 Playwright / agent-browser / nodriver）
  全部由本技能统一调用，且实现脚本均已自持在本技能 scripts/ 下，不依赖任何外部技能包。
version: 6.0.0
author: WorkBuddy 整合版
---

# 联网工具箱 · 所有联网操作的唯一入口

> **任何需要联网的事，都从这一个技能进。**
> 本技能是**编排层**：负责「判断该走哪一层」+「调用对应实现」。
> 底层实现（CDP Proxy、本地 Playwright、agent-browser、nodriver）**脚本都在本技能内，不需要你单独加载其它技能**。

---

## 0. 关于"只调一个技能"

| 你会遇到的情况 | 正确做法 |
|---|---|
| 搜索 / 抓网页 / 操作网页 / 下载文档 / 看视频内容 | **只加载本技能** |
| 文档提到 `scripts/check-deps.mjs` / `cdp-proxy.mjs` | 那是**本技能自带的 CDP Proxy 实现**，直接按文档调用即可 |
| 文档提到 `agent-browser` / `playwright-cli` / `scripts/pw.mjs` | 那是**降级执行器**，按本技能指引调用命令即可 |
| 你被直接 `@agent-browser` 唤起 | 仍按本技能的层级决策走，**不要跳层**（例如别在有登录态的情况下先试无头浏览器） |
| 子 Agent 需要联网 | prompt 里写 `必须加载「联网工具箱」skill 并遵循指引` |

**为什么要统一入口**：若干浏览器技能功能高度重叠，且各自文档的历史命令口径不一致
（本工具箱就曾把 `@playwright/mcp` 误当 `playwright-cli`、把不存在的 `agent-browser act` 写进文档）。
**统一从一个入口决策，才能保证每次走的是同一条经过验证的路径。**

> **2026-09-12 起本技能完全自持**：CDP Proxy 等 5 个脚本已从 `web-access`（MIT，作者 一泽Eze）
> 收编进 `scripts/`，配置在技能根目录 `config.env`。外部技能包 `web-access` / `agent-browser` /
> `playwright-cli` 已删除，文档中不再有指向它们的活引用。

---

## 1. 开跑前 30 秒：先自检

环境会变（包被卸载、daemon 挂了、代理端口换了）。**别照文档盲猜，先问环境**：

```bash
node scripts/doctor.mjs            # 人读能力矩阵
node scripts/doctor.mjs --json     # 机器可读，用来自动决定路由
node scripts/doctor.mjs --quick    # 跳过联网探测，最快
```

doctor 会逐层实测「到底能不能用」，并在缺失时给出**正确的**安装命令。
**本 SKILL.md 的层级顺序是原则，具体用哪层以 doctor 的实测结果为准。**

---

## 2. 四层结构（先分层，再选工具）

按**侵入性从低到高**分层。**永远从最轻的一层开始，拿不到才升级**——不要一上来就开浏览器。

| 层 | 手段 | 适用 | 详情 |
|----|------|------|------|
| **L0 静态层** | WebSearch / WebFetch / curl | 公开内容、URL 已知、无需登录 | [智能搜索](references/智能搜索.md) |
| **L0.5 预处理层** | WebFetch（内置）→ Jina `r.jina.ai/<url>` | 正文已在 HTML 里的页面，省 token | [智能搜索](references/智能搜索.md) |
| **L1 CDP 直连**（P0 首选） | 本技能自带 CDP Proxy | 需登录态、静态层失效、需交互 | **[CDP浏览器直连](references/CDP浏览器直连.md)** |
| **L2 独立浏览器**（降级） | `scripts/pw.mjs` / agent-browser | CDP 不可用时 | [浏览器自动化](references/浏览器自动化.md) |
| **L2.5 反爬层** | nodriver / curl_cffi / camoufox | 出现 Cloudflare / Turnstile 时 | [反爬对抗](references/反爬对抗.md) |

**升级判据（最重要的一条）**：目标站点**你已在本机浏览器登录过**
（知网 / CARSI / 微信 / QQ / 小红书 / 公众号后台 / 图书馆 / Springer 等），
或已知静态层对该平台无效 → **直接上 L1，别在 L0 浪费轮次。**

---

## 3. 决策树（从需求直达工具）

```
要不要登录态？已知静态层被拦？
├─ 是 → L1 CDP 直连（P0）
│        └ Proxy 起不来？ → agent-browser --cdp 9222（同样复用登录态，零重建）
└─ 否 ↓

是不是 SPA / JS 渲染，curl 拿不到正文？
├─ 是 → L1 CDP 直连；CDP 不可用 → scripts/pw.mjs（零安装，走系统 Edge）
└─ 否 ↓

正文在 HTML 里吗？（先 curl 看有没有 <div id="app"></div> 这种空壳）
├─ 在 → WebFetch 定向提取（内置）
│        ⚠️ Jina（r.jina.ai）本机实测不可达，别作为默认路径
└─ 不在 → 回到上面两条（JS 渲染 → CDP 直连）

遇到 403 / "Verify you are human" / Turnstile？
└─ → 反爬对抗.md（CDP 直连 → nodriver → curl_cffi → 付费），别在 CLI 层硬试

需要批量搜索 / 结构化 SERP / 语义检索？
└─ → 搜索层 API 选型（AI搜索.md）；默认内置 WebSearch 就够

要下载教材 / 找电子书？
└─ → 电子书下载.md（含 5 个自动化脚本）

要新闻 / 每日简报？
└─ → 新闻摘要.md（scripts/rss.mjs，零依赖）
```

---

## 4. 快速选择指南（路由表）

| 用户需求 | 去读 | 推荐工具 |
|---------|------|---------|
| 搜索信息、查资料 | [智能搜索](references/智能搜索.md) | WebSearch（默认）/ WebFetch |
| **需要登录态 / 静态层被反爬拦截** | **[CDP浏览器直连](references/CDP浏览器直连.md)** | **CDP Proxy（P0，天然继承登录态）** |
| 找"我之前看过的那个页面" / 组织内部系统 | [CDP浏览器直连](references/CDP浏览器直连.md) | `find-url.mjs` 本地书签历史检索 |
| 抓取网页内容、提取正文 | [网页抓取](references/网页抓取.md) | 分层降级 + Jina |
| 操作网页、点击、填表、截图 | [CDP浏览器直连](references/CDP浏览器直连.md) → [浏览器自动化](references/浏览器自动化.md) | CDP（P0）→ `scripts/pw.mjs` |
| 需要浏览器但 CDP 不可用 | [浏览器自动化](references/浏览器自动化.md) | `node scripts/pw.mjs open <url>`（零安装，系统 Edge） |
| **遇到 Cloudflare / 强反爬** | **[反爬对抗](references/反爬对抗.md)** | CDP 直连 → nodriver → curl_cffi |
| 需要批量/结构化搜索、语义检索 | [搜索层 API 选型](references/AI搜索.md) | Tavily / Exa / Serper / Brave（**均需 key，本机未配**） |
| 下载付费/受限文档（百度文库、原创力等） | [付费文档下载](references/付费文档下载.md) | CDP 继承登录态 → kill-doc 脚本 |
| 复用本机登录态下载教材/论文 | [复用Chrome登录态下载](references/复用Chrome登录态下载.md) | `scripts/reuse-chrome-download.mjs` |
| 下载教材 / 找电子书 / 搜 ISBN | [电子书下载](references/电子书下载.md) | IA 脚本（推荐）/ Anna's Archive |
| 总结文章 / 视频 / 音频 | [内容总结](references/内容总结.md) | 先拿内容（抓取层）→ 你直接总结，无需第三方 CLI |
| 看 YouTube 视频内容 | [YouTube转录](references/YouTube转录.md) | CDP 直连读转录面板（免安装）/ youtube-transcript-api |
| 获取最新新闻 / 每日简报 | [新闻摘要](references/新闻摘要.md) | `node scripts/rss.mjs --preset all`（零依赖） |
| 生成图片 / 视频 | [AI生成](references/AI生成.md) | **内置 ImageGen / VideoGen 优先**，`mmx` 本机未装 |
| 确认本机有什么工具 | [CLI 工具中心](references/cli-hub.md) | `node scripts/doctor.mjs` |
| **任何一层报错 / 命令没输出 / 进程假死** | **[故障诊断](references/故障诊断.md)** | 按症状对照，先跑 `doctor.mjs` |
| **要精确端点语义 / 查 CDP 错误码** | **[CDP-API参考](references/CDP-API参考.md)** | 端点表 + 迁移对照 + 错误处理 |
| **请求 mock / 存登录态 / trace / 录屏 / 生成测试代码** | **[playwright高级用法](references/playwright高级用法.md)** | `scripts/pw.mjs` 高级命令 |
| 接入 Kimi WebBridge（ego 类本地桥接） | [Kimi WebBridge 本地协议](references/Kimi%20WebBridge%20本地协议.md) | 见文档 |

---

## 5. 一级：需求分析（触发词）

| 需求类型 | 触发词示例 | 去读 |
|---------|------------|------|
| 搜索 | 搜索、查一下、找资料、有什么最新进展 | [智能搜索](references/智能搜索.md) |
| 抓取 | 抓取、提取正文、爬取、这个页面内容 | [网页抓取](references/网页抓取.md) |
| **登录态 / 反爬操作** | 登录后操作、小红书、公众号、我账号里的、之前看过的页面 | **[CDP浏览器直连](references/CDP浏览器直连.md)** |
| 浏览器自动化 | 打开网页、点击、填表、截图 | [CDP浏览器直连](references/CDP浏览器直连.md)（P0）→ [浏览器自动化](references/浏览器自动化.md) |
| 反爬 | 403、Cloudflare、验证、被拦、绕不过 | [反爬对抗](references/反爬对抗.md) |
| 下载文档 | 下载文档、文库下载、付费文档、受限内容、下载PDF | [付费文档下载](references/付费文档下载.md) |
| 找书 | 下载教材、找电子书、搜 ISBN、绝版书 | [电子书下载](references/电子书下载.md) |
| 新闻 | 今天有什么新闻、每日简报、最新动态 | [新闻摘要](references/新闻摘要.md) |
| 总结 | 总结这个页面、这篇论文讲了什么、这个视频说了什么 | [内容总结](references/内容总结.md) |
| 生成 | 生成图片、画一张、生成视频 | [AI生成](references/AI生成.md) |

---

## 6. 通用规则

### 信息核实：一手来源优先

搜索引擎是**发现**工具，不是**证明**工具。多个媒体引用同一个错误会造成循环印证假象。

| 信息类型 | 一手来源 |
|---|---|
| 政策 / 法规 | 发布机构官网 |
| 企业公告 | 公司官方新闻页 |
| 学术声明 | 原始论文 / 机构官网 |
| 工具能力 / 用法 | 官方文档、源码（**不要凭记忆写命令**） |

找不到官网时，用权威媒体的**原创报道**（非转载），并向用户说明来源与转述误差可能。

### 浏览哲学（进入浏览器层后必读）

**像人一样思考，带目标进去，边看边判断**——不要按预设步骤跑完就算完。

1. **定义成功标准** — 什么算完成？要拿到什么信息 / 达到什么状态？这是后续所有判断的锚点
2. **选起点** — 需要操作、需要登录态、已知静态层无效 → 直接 CDP
3. **过程校验** — 每一步结果都是证据，对照成功标准。方向错了立即调整，**不在同一方式上反复重试**。搜索没命中 ≠ 方法不对，也可能目标不存在
4. **完成判断** — 达成就停，不为「完整」浪费代价

**页面就绪 ≠ 内容就绪**：HTTP 200、`readyState === "complete"`、标题出现，**都不能单独作为完成标准**。
导航后必须用 `/eval` 检查目标内容；未出现则在 **15 秒**窗口内持续观察 URL / 标题 / DOM。

> 同理：**HTTP 200 也不代表有内容**。本工具箱实测到 RSS 源返回 200 但 body 为 0 字节（假活）。

**程序化 vs GUI**：程序化（构造 URL + eval）快而精确但可能触发反爬；GUI 交互（点击/填写/滚动）确定性最高。
GUI 也是程序化的有效探测——一次真实交互能观察站点实际行为。程序化受阻时 GUI 是可靠兜底。
**站点内交互产生的链接是可靠的**，手动构造的 URL 可能缺隐式参数被拦截；提取 URL 时保留完整地址，不要裁参数。

### 站点经验积累（本技能自持）

**唯一数据源**：`references/site-patterns/{domain}.md` ← 读写都在这里。

```bash
node scripts/site-patterns-check.mjs    # 体检：格式 / 重复域名与别名 / 陈旧条目
node scripts/match-site.mjs <域名或关键词>   # 按域名/别名匹配已有经验
```

只写经过验证的事实，不写未确认的猜测；经验标注发现日期，当作「可能有效的提示」而非保证。

### 并行策略

多个**独立**目标时，用子 Agent 分治并行。每个子 Agent 自行 `/new` 建后台 tab、自行 `/close`，共享同一 Proxy 无竞态。

- 子 Agent prompt 必须写 `必须加载「联网工具箱」skill 并遵循指引`
- **描述目标，不指定步骤**——避免「搜索xx」这类暗示手段的动词把子 Agent 锚定到 WebSearch
- ⚠️ **不要在并发子 Agent 间驱动同一个标签页**：不同 targetId 无竞态，但同页并发会互相干扰导航、页面状态与网络拦截，也更容易触发风控

---

## 7. 核心工作流：登录墙处理

**这是最常见的拦路虎**，所以单独列为核心工作流。

| 优先级 | 方案 | 何时用 |
|---|---|---|
| **P0（首选）** | **CDP 直连** | 你**已在该站登录**时。零登录成本、真实浏览器环境 → [CDP浏览器直连](references/CDP浏览器直连.md) |
| **P0.5** | agent-browser `--cdp 9222` | CDP Proxy 起不来，但仍要复用登录态 |
| P1 | kill-doc 脚本 | 百度文库/原创力等 30+ 中文文档站，无需登录 |
| P2 | 复用本机浏览器登录态下载 | CDP 不便于直接下载文件时 → [复用Chrome登录态下载](references/复用Chrome登录态下载.md) |
| P3 | 有头浏览器 + 手动登录 | 上述都不适用、且本机也未登录 |
| P4 | 反爬方案 | 遇到 Cloudflare → [反爬对抗](references/反爬对抗.md) |

### P0：CDP 直连 —— 已登录时零成本

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/check-deps.mjs"
curl -s -X POST --data-raw '<目标URL>' http://localhost:3456/new
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.body.innerText'
curl -s "http://localhost:3456/close?target=ID"
```

**执行前必须向用户展示**：

```
温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。已内置防护措施但无法完全避免，Agent 继续操作即视为接受。
```

### P3：登录墙中断-恢复

```
检测登录墙 → 启动有头浏览器 → 告知用户在哪登录 → 每 3 秒轮询（默认超时 120 秒）
→ 用户确认"好了" → 在当前会话继续（不要重启浏览器，会丢会话）
```

> **更省事的做法**：若该站你本机浏览器已登录，直接用 CDP 直连，根本不需要中断流程。

---

## 8. 反爬（出现才需要）

只要看到 403 / "Just a moment" / "Verify you are human" / Turnstile，**立刻转 [反爬对抗](references/反爬对抗.md)**。

一句话版本（免费，按顺序）：

```
CDP 直连真实浏览器（navigator.webdriver 天然 false）
  → agent-browser --cdp 9222
  → nodriver（Python ≤3.13，免 WebDriver）
  → curl_cffi（仅 TLS-only 站点）
  → camoufox → 付费方案
```

**不要在 Playwright / 无头浏览器上死磕 Cloudflare。** 也不要再用 FlareSolverr、老版 puppeteer-stealth（已被秒识别）。

---

## 9. 本技能自带的脚本（`scripts/`）

### CDP 直连（L1，P0 首选，2026-09-12 收入本技能）

| 脚本 | 用途 |
|---|---|
| `check-deps.mjs` | **前置检查 + 自动拉起 Proxy**。退出码：0 就绪 / 1 环境错误 / 2 需选浏览器。`--browser <chrome\|edge>` 单次覆盖 |
| `cdp-proxy.mjs` | **CDP 代理本体**，`localhost:3456` 全部 HTTP API。通常由 check-deps 拉起，无需手工启动 |
| `find-url.mjs` | **本地书签/历史检索**。`[关键词...] [--only bookmarks\|history] [--browser chrome\|edge] [--since 1d] [--sort recent\|visits]` |
| `browser-discovery.mjs` | 发现本机可用浏览器、读取 `config.env` 偏好、兜底端口探测（被上面两个 import） |
| `match-site.mjs` | 按域名/别名匹配已积累的站点经验 |

### 环境与工具

| 脚本 | 用途 |
|---|---|
| `doctor.mjs` | **环境自检**，输出能力矩阵。`--json` / `--quick` |
| `pw.mjs` | **本地 playwright-cli 封装（零安装）**。`open <url>` / `snapshot` / `click <ref>` / `eval` / `close`，默认走系统 Edge |
| `rss.mjs` | **零依赖 RSS 阅读器**。`--preset news\|tech\|ai\|dev\|all` / `--url` / `--since 1d` / `--json`；内置**冻结源检测** |
| `site-patterns-check.mjs` | 站点经验体检：frontmatter 格式、重复域名/别名、陈旧条目 |

### 下载（电子书 / 文档）

| 脚本 | 用途 |
|---|---|
| `reuse-chrome-download.mjs` | 复用本机 Edge/Chrome 登录态下载登录墙文档 |
| `archiveorg-find.mjs` | Internet Archive API 检索并下载电子书（**推荐**） |
| `archiveorg-search-download.mjs` | IA 网页搜索 + metadata 筛 PDF 并下载 |
| `archiveorg-download.mjs` | IA UI 搜索版（较慢） |
| `annas-archive-download.mjs` | Anna's Archive 按 ISBN 下载 |
| `jiumo-find.mjs` | ❌ 已失效（鸠摩搜书全镜像已挂），仅留历史参考 |

工具清单与安装状态见 [CLI 工具中心](references/cli-hub.md)。

---

## 10. References 索引

| 文件 | 何时读 |
|---|---|
| **[CDP浏览器直连](references/CDP浏览器直连.md)** | **需要登录态、静态层被拦、需交互（浏览器层 P0 首选）** |
| **[CDP-API参考](references/CDP-API参考.md)** | **要精确的端点/参数位置/返回值，或调用失败查错误码** |
| **[故障诊断](references/故障诊断.md)** | **任何一层报错、命令无输出、进程假死、装包失败** |
| **[playwright高级用法](references/playwright高级用法.md)** | **请求 mock / 状态存取 / trace / 录屏 / 生成测试代码** |
| [反爬对抗](references/反爬对抗.md) | 遇到 403 / Cloudflare / Turnstile |
| [智能搜索](references/智能搜索.md) | 搜索与信息核实流程 |
| [网页抓取](references/网页抓取.md) | 抓取网页、提取正文 |
| [浏览器自动化](references/浏览器自动化.md) | CDP 不可用时的降级执行器 |
| [搜索层 API 选型](references/AI搜索.md) | 需要批量/结构化/语义搜索 |
| [付费文档下载](references/付费文档下载.md) | 百度文库、原创力、夸克文档等 |
| [电子书下载](references/电子书下载.md) | 教材、专著、绝版书、ISBN 检索 |
| [复用Chrome登录态下载](references/复用Chrome登录态下载.md) | 知网 / CARSI / Springer 等已登录资源 |
| [内容总结](references/内容总结.md) | 总结文章、视频、音频 |
| [YouTube转录](references/YouTube转录.md) | 获取视频字幕 |
| [新闻摘要](references/新闻摘要.md) | 最新新闻、每日简报 |
| [AI生成](references/AI生成.md) | 生成图片 / 视频 / 语音 |
| [CLI 工具中心](references/cli-hub.md) | 确认本机工具与脚本清单 |
| [Kimi WebBridge 本地协议](references/Kimi%20WebBridge%20本地协议.md) | 接入本地浏览器桥接 |
| `references/site-patterns/{domain}.md` | 确定目标网站后，读对应站点经验 |

---

## 11. 维护本技能（重要）

本技能是**编排层**，它的价值全在「推荐的东西是真的能用」。所以：

1. **改动后必跑** `node scripts/doctor.mjs`，确认推荐的工具确实被识别
2. **新增工具前先验证包存在**：
   `curl -o /dev/null -w '%{http_code}' https://registry.npmjs.org/<包名>`（404 = 不存在）
3. **不要把"未验证的命令"写进文档**。本工具箱历史上有三处此类错误
   （`@playwright/mcp` 误当 `playwright-cli`、`human-browser-cli`（404）、`agent-browser act`（不存在）），
   每一次都会让后续的自己白排查半小时
4. 发现文档与实际不符 → **先改文档**，再继续任务
