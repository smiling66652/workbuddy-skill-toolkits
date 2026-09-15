# WorkBuddy 技能库（workbuddy-skill-toolkits）

> 本仓库是 WorkBuddy AI 助手的**技能库（skill suite）**：把一组相互独立、可单独取用的技能（Skill）集中管理，便于复制、归档与索引。
> 当前收录 **19 个技能**，覆盖联网、文档、开发、知识、学术研究、小程序、安全、AI、工程方法论、项目专用等场景。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills: 19](https://img.shields.io/badge/Skills-19-blue.svg)](INDEX.md)
[![Index](https://img.shields.io/badge/Index-INDEX.md-purple.svg)](INDEX.md)

> **关于技能数**：本仓库 `git` 跟踪的技能目录共 **19** 个（见下文「项目结构」）。
> 本机 skills 目录另有 `goodnight-letter`（私人项目）与 `ima-skills`（供应商技能，许可不允许转分发）两个技能
> **有意未收入本仓库**，因此仓库根目录的 `INDEX.md` 由 `skill-doctor.py` 以 `--exclude` 生成，表头即「19 个」并与实际目录一致。
> 生成命令见「技能索引」一节。

---

## 快速导航

技能分五类。**先看「触发场景」判断该用哪个**——`description` 里的触发词是模型路由的唯一依据，正文关键词模型看不到。

| 类别 | 技能 | 一句话用途 | 跳转 |
|------|------|-----------|------|
| 常驻规程 | `WorkBuddy 工作原则` | 每个任务自动注入的 12 条工作原则（`auto_load`） | [详情](#常驻规程) |
| 领域工具箱 | `联网工具箱` | 一切联网/浏览器/下载/反爬/AI生成的唯一入口 | [详情](#领域工具箱) |
| 领域工具箱 | `文档工具箱` | PDF/Word/PPT/Excel/Markdown 本地处理 | [详情](#领域工具箱) |
| 领域工具箱 | `开发工具箱` | 写代码/构建/Git/测试/前端/移动端/MCP | [详情](#领域工具箱) |
| 领域工具箱 | `知识工具箱` | 笔记/记忆/目标追踪（IMA、引用→指向权威实现） | [详情](#领域工具箱) |
| 领域工具箱 | `学术研究工具箱` | 文献检索/综述/引用/一手源调研 | [详情](#领域工具箱) |
| 领域工具箱 | `微信小程序开发套件` | 小程序垂直全流程 | [详情](#领域工具箱) |
| 领域工具箱 | `安全审查工具箱` | Skill 安全审计/第三方审查/代码安全 | [详情](#领域工具箱) |
| 领域工具箱 | `AI 工具箱` | 语音转文字/模型用量/自动研究（⚠ 依赖本机未装） | [详情](#领域工具箱) |
| 方法论 | `工程方法论工具箱` | 怎么做得可靠：调试/TDD/验证/审查/需求澄清 | [详情](#方法论与元技能) |
| 方法论 | `评审委员会` | 多视角把关（工程/产品/设计/QA/复盘） | [详情](#方法论与元技能) |
| 方法论 | `skill-integrator` | 元技能：如何合并技能 | [详情](#方法论与元技能) |
| 单点工具 | `git-ship` | 提交推送 + 密钥安全检查 | [详情](#单点工具) |
| 单点工具 | `techdebt` | 仓库技术债体检 | [详情](#单点工具) |
| 单点工具 | `weekly-review` | 周报生成 | [详情](#单点工具) |
| 单点工具 | `qf-english-polish` | 英文写作润色 | [详情](#单点工具) |
| 单点工具 | `image-to-editable-pptx` | 图片 → 可编辑 PPTX | [详情](#单点工具) |
| 项目专用 | `hfut-inspector` | 合工大（HFUT）信息巡检 | [详情](#项目专用) |
| 项目专用 | `yuketang-harvester` | 长江雨课堂课件归档 | [详情](#项目专用) |

---

## 设计理念：三级层级结构（工具箱类技能）

`WorkBuddy 工作原则` 规定，工具箱类技能采用统一的三层调用结构（**不是每个技能都如此**——单点工具、项目专用技能通常是单文件、单目的，不套用此结构）：

```
一级：需求分析
  └── 判断用户要做什么（匹配触发词，无需加载任何工具）

二级：工具选择
  └── 根据需求选择最佳工具（按需读取 references/ 下的二级文档）

三级：执行指令
  └── 调用工具并返回结果
```

**优势**：按需加载，避免一次性把所有细节灌进上下文；工具选择更精准；二级文档可独立维护。

---

## 多级退回机制（Plan A → Plan B → Plan C）

本仓库的技能普遍遵循「任何目标必须有 fallback 链路」的原则（详见 `WorkBuddy 工作原则` 的「原则六」）：

```
Plan A（首选方案）
  └── 如果失败 → 自动降级到 Plan B

Plan B（备选方案）
  └── 如果失败 → 自动降级到 Plan C

Plan C（兜底方案）
  └── 仍失败 → 全网搜索 + 向用户报告完整排查过程
```

以 `联网工具箱` 为例：L0 静态层（WebSearch/WebFetch/curl）→ L1 CDP 直连（P0）→ L2 本地 Playwright（`pw.mjs`）→ L2.5 反爬（nodriver/curl_cffi）→ 付费方案。每升一层都是上一层的兜底。

---

## 技能总览

> 下表「版本」取自各技能 `SKILL.md` 的 `version` 字段；「触发场景」取自 `description` 的触发词；「用途边界」取自 `description` 首段。完整描述以各技能自己的 `SKILL.md` 为准。

### 常驻规程

| 技能 | 版本 | 用途边界 | 触发场景 |
|------|------|----------|----------|
| `WorkBuddy 工作原则` | 2.0.0 | 执行任务的核心方法论（`auto_load: true`，每个任务自动注入），含目标/拆分/多 Agent/工具选择/多级退回/全网搜索/验证/记录/Skill 迭代/预设期待/风控 12 条原则 | 自动加载，无触发词；含「路由卫生」硬要求：每个技能 `description` 必须带「触发词：」 |

### 领域工具箱

| 技能 | 版本 | 用途边界 | 触发场景 |
|------|------|----------|----------|
| `联网工具箱` | 6.0.0 | 所有联网操作的**唯一入口**（编排层）：搜索/抓取/浏览器自动化/登录态/下载文档/反爬/新闻/RSS/AI 生成。实现脚本（CDP Proxy、`pw.mjs`、RSS、电子书下载等）**自持在本技能 `scripts/` 下** | 搜索、查资料、抓取网页、浏览器自动化、打开网页、点击、填表、截图、登录后操作、下载文档/教材/电子书、反爬、Cloudflare、验证码、403、新闻、每日简报、RSS |
| `文档工具箱` | 4.1.0 | 本地文档格式处理：PDF/Word/PPT/Excel/Markdown 的读取、编辑、生成与转换 | 读这个PDF、提取PDF文字、改PDF、生成PDF、PDF合并、创建Word、做PPT、创建Excel、表格处理、转Markdown、OCR |
| `开发工具箱` | 4.1.0 | GitHub 仓库/Issues/PR 管理；代码静态检查（Semgrep/Bandit/pylint）；单元测试与集成测试生成；Flutter/Android 原生/前端 React-Vue/MCP 服务器开发 | GitHub、Issues、PR、CI、Flutter、跨平台、Android、Kotlin、Compose、前端、React、Vue、MCP、写代码、构建、写单测 |
| `知识工具箱` | 4.1.0 | 跨会话记忆、Obsidian/Joplin 笔记、NotebookLM 学习材料、目标追踪；IMA 相关操作**指向 `ima-skills`（权威实现）**，文献/引用**指向 `学术研究工具箱`** | 记住这个、Obsidian笔记、Joplin、上传到知识库、生成播客、追踪目标、知识库搜索 |
| `学术研究工具箱` | 1.0.0 | 文献检索/综述结构化/引用管理（BibTeX+Zotero）/一手源研究；面向合工大在校生，优先用 CARSI 订阅库 | 论文、文献、检索、知网、CNKI、arXiv、IEEE、ScienceDirect、文献综述、引用、参考文献、BibTeX、Zotero、调研、阻抗控制、软体抓取 |
| `微信小程序开发套件` | 2.1.0 | 小程序垂直全流程：新建项目、UI 组件、CloudBase 云开发、Skyline 渲染、性能优化与部署上线 | 小程序、微信小程序、云开发、CloudBase、TDesign、Skyline、小程序UI、部署小程序、小程序性能优化 |
| `安全审查工具箱` | 2.1.0 | 安装 Skill 前安全审计、第三方 Skill 审查、通用代码/依赖安全与漏洞扫描 | 安全审查、这个安全吗、审查这个Skill、安装前检查、第三方Skill、代码安全、依赖安全、漏洞扫描 |
| `AI 工具箱` | 3.1.0 | 语音转文字（Whisper）、模型用量统计（model-usage）、自动研究优化（autoresearch）、提示词优化；图片/视频/3D 生成请优先用内置 ImageGen/VideoGen | 语音转文字、转录、音频转文字、字幕生成、模型用量、token统计、自动研究、优化提示词 |

> **诚实标注**：`AI 工具箱` 的 SKILL.md 明确写明——本机当前**未安装**依赖（`mmx`/`whisper`/`autoresearch`/`model-usage` 及 `OPENAI`/`MINIMAX` 环境变量均缺失），相关能力需先按 references 安装后才能用；`联网工具箱` 的 AI 生成同样依赖内置 `ImageGen`/`VideoGen`，其 `mmx` 本机未装。

### 方法论与元技能

| 技能 | 版本 | 用途边界 | 触发场景 |
|------|------|----------|----------|
| `工程方法论工具箱` | 1.0.0 | 系统化调试 / TDD / 完成前验证 / 单视角代码审查 / 需求澄清（三条铁律） | 调试、debug、报错、修 bug、测试、TDD、先写测试、验证、自检、代码审查、code review、需求不清、需求澄清 |
| `评审委员会` | 1.0.0 | 多视角评审技能包：工程/产品/设计/QA/复盘 五视角；严重程度四级 + 置信度 1-10 + 证据门 | 多视角评审、方案评审、设计评审、QA验收、验收、复盘、挑毛病、找问题 |
| `skill-integrator` | 1.0.0 | 元技能：把多个同类 skills 整合为统一套件的方法论与执行流程 | 整合 skills、N合一、合并 skills、整理 skills |

### 单点工具

| 技能 | 版本 | 用途边界 | 触发场景 |
|------|------|----------|----------|
| `git-ship` | 1.0.0 | 看改动 → 密钥安全检查 → 规范中文 commit → push → 按需 `gh pr create` | 提交并推送、一键提交、git 提交推送、开 PR、提交代码、ship it、提交前检查 |
| `techdebt` | 1.0.0 | 扫描仓库：超大文件/TODO 堆积/调试残留/重复代码/未用依赖/死文件，输出严重度分级表 | 技术债、代码坏味道、清理代码、扫描重复代码、找 TODO、code smell、重构前的体检 |
| `weekly-review` | 1.0.0 | 读 git 本周提交 + 记忆日志，生成结构化周报（完成/未完成/卡点/下周计划） | 周复盘、本周总结、这周做了什么、周报、weekly review、一周回顾 |
| `qf-english-polish` | 1.0.0 | 英文写作润色：语法纠错/流畅度/地道改写，覆盖学术·商务·日常·创意四语域，输出「修改+理由」对照 | 英文润色、改英文、polish English、英文邮件、英文简历、论文润色、English writing |
| `image-to-editable-pptx` | 2.0.0 | 图片→可编辑 PPTX：OpenCV inpaint 按色擦字（保留 pill/底条/卡片底色），logo 切片 1:1，其余文字转可编辑文本框 | 图片转可编辑PPT、截图转ppt、信息图转ppt、海报转可编辑、image to editable pptx |

### 项目专用

| 技能 | 版本 | 用途边界 | 触发场景 |
|------|------|----------|----------|
| `hfut-inspector` | 5.0.0 | 合工大（HFUT）信息巡检统一系统：官网栏目扫描 + QQ群/空间/公众号采集 + AI 三层分析 + 邮件推送 + 知识库检索 | 合工大、HFUT、官网巡检、通知扫描、竞赛信息、保研通知、夏令营、讲座、教务通知、日报 |
| `yuketang-harvester` | 1.0.0 | 批量归档长江雨课堂课件：课表枚举、课件文字层提取、页图批量下载、讲义装配 | 雨课堂、长江雨课堂、下载课件、课程归档、讲义整理、复习资料、课件转 PDF |

---

## 各工具箱实际集成/调用的能力

> 只看 `SKILL.md` 里**确实写明**的工具与脚本，未核实的一律不写。带 ⚠ 的是本机当前**未安装/未配置**的能力，使用前需先准备环境。

- **联网工具箱**：自持 `scripts/` 脚本——`check-deps.mjs` + `cdp-proxy.mjs`（CDP 直连，P0）、`pw.mjs`（本地 Playwright 1.63，走系统 Edge，零安装）、`rss.mjs`、`find-url.mjs`、电子书下载脚本（archive.org / Anna's Archive）等。反爬层用 nodriver / curl_cffi / camoufox。⚠ Tavily/Exa/Serper/Brave 等搜索 API 均需 key 且本机未配；Jina `r.jina.ai` 本机实测不可达。
- **文档工具箱**：MinerU（PDF→MD 表格识别）、MarkItDown、pypandoc、docx/python-docx、pptx/python-pptx、openpyxl；PDF 生成用 reportlab / WeasyPrint。PDF 编辑用 **pikepdf / pypdf / PyMuPDF**（2026-09-15 核实：文档原先写的 `pdfkit-py` 在 PyPI 上**不存在**，那是 WorkBuddy 插件名，已更正）。
- **开发工具箱**：`gh` CLI、Semgrep、Bandit、pylint、pytest、Playwright（测试）、Flutter SDK + Dart、Kotlin + Compose、React/Vue + Vite、FastMCP（Python）/ MCP SDK（TypeScript）。
- **知识工具箱**：agent-memory、Obsidian CLI、Joplin API、NotebookLM API、goal-tracker、CrossRef（取 DOI 信息）；IMA 操作与文献库/BibTeX/Zotero 分别指向 `ima-skills` 与 `学术研究工具箱`。
- **学术研究工具箱**：arXiv / Semantic Scholar / CNKI / IEEE Xplore / ScienceDirect / Google Scholar；合工大 CARSI 订阅库；DOI→BibTeX（curl 需 `--ssl-no-revoke`）；Zotero。
- **微信小程序开发套件**：CloudBase 全栈开发、TDesign 组件库、微信小程序框架、Skyline 渲染引擎。
- **安全审查工具箱**：腾讯云鼎实验室、腾讯朱雀实验室 A.I.G、skill-vetter / skill-scanner；Skill 安全审计优先用内置插件 `skills安全审计`（skills-sec-audit）。⚠ **不是** sqlmap/nmap/OWASP ZAP/Grype/Trivy 之类渗透工具——本技能做的是 Skill 与代码/依赖的安全审计。
- **AI 工具箱**：Whisper（语音转文字）、autoresearch（自动研究）、model-usage（模型使用统计）；图片/视频/3D 生成用内置 ImageGen/VideoGen。⚠ **2026-09-15 一手核实：该技能当前没有任何可用能力**——`autoresearch` / `model-usage` / `codexbar` 在 **PyPI 上不存在（404）**，装不上；`openai-whisper` 存在但本机未装；且无任何 OPENAI/MINIMAX key。保留它是作为**安装指引与能力清单**，不是因为它现在能用。

---

## 安装使用

技能是**独立目录**，可单独取用，无需整体克隆。把需要的技能目录复制到 WorkBuddy 的技能目录即可。

### 方式一：从本仓库复制

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/smiling66652/workbuddy-skill-toolkits.git
cd workbuddy-skill-toolkits

# 2. 把需要的技能目录复制到 WorkBuddy 技能目录（按需，挑你想要的）
cp -r 联网工具箱   ~/.workbuddy/skills/
cp -r 文档工具箱   ~/.workbuddy/skills/
cp -r git-ship     ~/.workbuddy/skills/
# ……其余同理，目录即技能，整目录复制即可

# 3. 验证：WorkBuddy 启动后会在可用技能列表里看到它们
```

### 方式二：在 WorkBuddy 中安装

在 WorkBuddy 对话里直接说，例如：

```
帮我安装 联网工具箱 skill
```

WorkBuddy 会按它的技能安装流程加载对应目录。

> 注意：本仓库各技能目录自带 `SKILL.md` 与 `references/`、`scripts/`，复制时请保留完整目录结构，不要只拷 `SKILL.md`。

---

## 项目结构

```text
workbuddy-skill-toolkits/
├── INDEX.md                 # 技能索引（唯一权威清单，由 skill-doctor.py 生成）
├── README.md                # 本文件（主文档）
├── README_zh.md             # 精简版说明
├── LICENSE                  # MIT
├── docs/                    # 项目相关说明（见 docs/README.md）
├── WorkBuddy 工作原则/       # 常驻规程（auto_load）
├── 联网工具箱/              # 领域工具箱 ×8
├── 文档工具箱/
├── 开发工具箱/
├── 知识工具箱/
├── 学术研究工具箱/
├── 微信小程序开发套件/
├── 安全审查工具箱/
├── AI 工具箱/
├── 工程方法论工具箱/         # 方法论/元技能 ×3
├── 评审委员会/
├── skill-integrator/
├── git-ship/               # 单点工具 ×5
├── techdebt/
├── weekly-review/
├── qf-english-polish/
├── image-to-editable-pptx/
├── hfut-inspector/          # 项目专用 ×2
└── yuketang-harvester/
```

每个技能目录约定包含：`SKILL.md`（主文件，含 frontmatter 与三级/二级路由）、`references/`（二级详细文档）、`scripts/`（实现脚本，按需）。

---

## 技能索引

**技能清单的唯一来源是根目录 `INDEX.md`**，不要另起一份副本（历史教训：`WorkBuddy 工作原则` 曾维护一份速查表，结果推荐了已删除的技能）。

- `INDEX.md` 由 `skill-doctor.py` 自动生成，**请勿手工编辑**。
- 技能增删改后，重新生成：

```bash
# 本仓库范围（19 个）：需排除两个「本机有、本仓库不收」的技能
python skill-doctor.py <本机skills目录> \
  --exclude "goodnight-letter,ima-skills" \
  --out INDEX.md --fix-index
```

- 触发词取自各技能 `description` 的「触发词：」段，是模型决定「用哪个技能」的唯一依据；正文里的词模型看不到。缺触发词的技能会被模型忽略或误判（详见 `WorkBuddy 工作原则` 的「路由卫生」要求）。
- `skill-doctor.py` 还会顺带体检：frontmatter 规范、相对引用与**绝对路径**存在性、是否引用了已删除的技能名。发现问题会直接打印，不会静默通过。

---

## 更新日志

### 2026-09-15 — 全量入库 + 文档校正

- ✅ 技能从旧版（README 曾写 7 个）扩到 **19 个目录**，统一了各技能 `description` 触发词
- ✅ 删除 `sandbox-browser-cdp`，其 CDP 能力并入 `联网工具箱`（v6.0.0 完全自持化：收编 CDP 脚本、补齐 references 与 scripts）
- ✅ `联网工具箱` 自持化：不再依赖外部 `web-access` / `agent-browser` / `playwright-cli`（均已删除）
- ✅ 校正 README：去掉虚构的工具清单（如安全审查工具箱的 sqlmap/nmap、联网工具箱的 Agent Browser/MiniMax CLI、AI 工具箱的 Ollama/DeepSeek 等），仅保留 SKILL.md 中确认存在的能力，并如实标注本机未装依赖
- ✅ 补全「安装使用」「项目结构」「技能索引」章节；保留「三级层级结构」「多级退回机制」（改为「工具箱类技能采用」，不再绝对化到所有技能）
- ✅ 清理 `docs/`：移走一次性检查报告、未完成攻略提纲、专家会话缓存（见 `docs/README.md`）

### v1.0.0 (2026-06-02) — 初始版本

- 开发/文档/联网/安全/知识/AI 六大工具箱 + Skill 整合器（旧版口径，已演进）

---

## 贡献指南

欢迎贡献新的技能或优化现有技能！

1. Fork 本仓库
2. 创建分支（`git checkout -b feature/新技能`）
3. 提交更改（每个技能是独立目录，含 `SKILL.md` 与必要的 `references/`、`scripts/`）
4. 推送分支（`git push origin feature/新技能`）
5. 创建 Pull Request

### 贡献要求

- 每个技能的 `description` **必须包含「触发词：」段落**（5–12 个用户真实会说的词），这是路由依据
- 工具箱类技能建议采用三级层级结构；单点工具保持单文件、单目的
- 写进文档的工具/命令必须**经过核实**，未安装/未验证的须明确标注，不要写没核实过的内容

---

## 许可证

[MIT License](LICENSE)

---

## 联系方式

- GitHub：[@smiling66652](https://github.com/smiling66652)
- Email：2240678683@qq.com

---

**⚙️ 由 WorkBuddy AI 助手整理（repo-curator）**
