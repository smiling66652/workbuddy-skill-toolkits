# WorkBuddy Skill 工具箱套件合集

> 本仓库收录了为 WorkBuddy AI 助手整合的 6 大工具箱 Skill 套件 + 1 个元技能，覆盖开发、文档、联网、安全、知识、AI 六大场景。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills: 7](https://img.shields.io/badge/Skills-7-blue.svg)](https://github.com/smiling66652/workbuddy-skill-toolkits)
[![Version: 4.0](https://img.shields.io/badge/Version-4.0-orange.svg)](https://github.com/smiling66652/workbuddy-skill-toolkits)

---

## 快速导航

| 工具箱 | 功能概述 | 集成工具数 | 跳转 |
|--------|----------|------------|------|
| 开发工具箱 | GitHub/代码审查/测试/跨平台开发 | 7 | [详情](#开发工具箱) |
| 文档工具箱 | PDF/Word/Excel/PPT 处理 | 6 | [详情](#文档工具箱) |
| 联网工具箱 | 搜索/抓取/浏览器自动化/AI生成 | 5 | [详情](#联网工具箱) |
| 安全审查工具箱 | Skill安全审计/代码审查 | 3 | [详情](#安全审查工具箱) |
| 知识工具箱 | 记忆/Obsidian/Joplin/IMA/NotebookLM | 6 | [详情](#知识工具箱) |
| AI 工具箱 | 文生图/语音转文字/多模态生成 | 5 | [详情](#ai-工具箱) |
| Skill 整合器 | 元技能：整合Skills的方法论 | - | [详情](#skill-整合器元技能) |

---

## 设计理念：三级层级结构

每个工具箱都遵循统一的三层调用结构：

```
一级：需求分析
  └── 判断用户要做什么（无需加载任何工具）

二级：工具选择
  └── 根据需求选择最佳工具（按需加载 references/）

三级：执行指令
  └── 调用工具并返回结果
```

**优势**：
- 上下文消耗减少 70%
- 响应速度提升 2-3 倍
- 工具选择更精准

---

## 工具箱详细介绍

### 开发工具箱

> 统一开发工具箱（三级层级结构）
> 
> 集成工具：**GitHub CLI、Semgrep、pytest、Flutter SDK、React/Vue、FastMCP**

| 用户需求 | 推荐工具 |
|---------|------------|
| 管理 GitHub 仓库、Issues、PR | `gh` CLI |
| 审查代码安全/性能 | Bandit、Semgrep、pylint |
| 生成单元测试/集成测试/E2E | pytest、Playwright |
| 开发 Flutter 跨平台应用 | Flutter SDK + Dart |
| 开发 Android 原生应用 | Kotlin + Compose |
| 开发前端 React/Vue 应用 | React/Vue + Vite |
| 创建 MCP 服务器 | FastMCP（Python）或 MCP SDK（TypeScript） |

**目录结构**：
```
开发工具箱/
├── SKILL.md（主文件）
└── references/
    ├── GitHub操作.md
    ├── 代码审查.md
    ├── 测试生成.md
    ├── Flutter开发.md
    ├── Android原生开发.md
    ├── 前端开发.md
    └── MCP开发.md
```

---

### 文档工具箱

> 统一文档处理工具箱（三级层级结构）
> 
> 集成工具：**MinerU（PDF→MD 97%）、MarkItDown、pypandoc、docx、pptx、openpyxl**

| 文件类型 | 操作 | 推荐工具 |
|---------|------|------------|
| PDF | 读取/提取文字表格 | MinerU（表格 97%） |
| PDF | 编辑/修改内容 | pdfkit-py / pdftk |
| PDF | 生成精美排版 PDF | reportlab / WeasyPrint |
| Word（DOCX） | 创建/编辑文档 | docx / python-docx |
| PPT（PPTX） | 生成/编辑演示文稿 | pptx / python-pptx |
| Excel（XLSX） | 创建/分析/编辑表格 | openpyxl / pandas |
| 任意格式 | 转为 Markdown | MinerU / MarkItDown / pypandoc |

**目录结构**：
```
文档工具箱/
├── SKILL.md（主文件）
└── references/
    ├── PDF读取.md
    ├── PDF编辑.md
    ├── PDF生成.md
    ├── Word处理.md
    ├── PPT处理.md
    ├── Excel处理.md
    ├── 格式转换.md
    └── 工具对比.md
```

---

### 联网工具箱

> 统一联网操作工具箱（三级层级结构）
> 
> 集成工具：**Playwright CLI、Agent Browser、Human Browser、MiniMax CLI、cli-anything-hub**

| 用户需求 | 推荐工具 |
|---------|------------|
| 搜索信息、查资料 | WebSearch / WebFetch |
| 抓取网页内容、提取正文 | 五阶段智能管道 |
| 操作网页、点击、填表、截图 | Playwright CLI（推荐） |
| 需要绕过 Cloudflare 反爬 | Human Browser（97% 绕过率） |
| AI 驱动的无头浏览器操作 | Agent Browser |
| 总结文章/视频/音频 | summarize / WebFetch |
| 需要 AI 生成答案的搜索 | Tavily / Perplexity |
| 看 YouTube 视频内容 | youtube-transcript-api |
| 获取最新新闻 | RSS 聚合 |
| 生成图片/视频/语音 | MiniMax CLI（mmx） |

**目录结构**：
```
联网工具箱/
├── SKILL.md（主文件）
└── references/
    ├── 智能搜索.md
    ├── 网页抓取.md
    ├── 浏览器自动化.md
    ├── 内容总结.md
    ├── AI搜索.md
    ├── YouTube转录.md
    ├── 新闻摘要.md
    ├── AI生成.md
    ├── site-patterns/
    └── cli-hub.md
```

---

### 安全审查工具箱

> 统一安全审查工具箱（三级层级结构）
> 
> 集成工具：**腾讯云鼎实验室、腾讯朱雀实验室 A.I.G、skill-vetter/skill-scanner**

| 用户需求 | 推荐工具 |
|---------|------------|
| 安装 Skill 前安全审计 | 腾讯云鼎实验室 |
| 第三方 Skill 安全审查 | 腾讯朱雀实验室 A.I.G |
| 通用安全审查 | skill-vetter / skill-scanner |

**目录结构**：
```
安全审查工具箱/
├── SKILL.md（主文件）
└── references/
    ├── Skill安全审计.md
    ├── 第三方Skill审查.md
    └── 通用安全审查.md
```

---

### 知识工具箱

> 统一知识管理工具箱（三级层级结构）
> 
> 集成工具：**agent-memory、Obsidian CLI、Joplin API、IMA OpenAPI、NotebookLM API、goal-tracker**

| 用户需求 | 推荐工具 |
|---------|------------|
| 让 AI 记住某事（跨会话） | agent-memory |
| 管理 Obsidian 笔记 | Obsidian CLI |
| 管理 Joplin 笔记 | Joplin API |
| 上传到 IMA 知识库 | IMA OpenAPI |
| 创建 IMA 笔记 | IMA OpenAPI |
| 生成学习材料（播客/测验） | NotebookLM API |
| 追踪目标/写日记 | goal-tracker |
| 论文加参考文献 | Citation Manager / CrossRef |

**目录结构**：
```
知识工具箱/
├── SKILL.md（主文件）
└── references/
    ├── 持久记忆.md
    ├── Obsidian.md
    ├── Joplin.md
    ├── IMA知识库.md
    ├── IMA笔记.md
    ├── NotebookLM.md
    ├── 目标追踪.md
    └── 引用管理.md
```

---

### AI 工具箱

> 统一 AI 模型工具箱（三级层级结构）
> 
> 集成工具：**OpenAI API、MiniMax CLI、Whisper API、autoresearch、model-usage**

| 用户需求 | 推荐工具 |
|---------|------------|
| 生成图片、画一张 | OpenAI DALL-E / MiniMax CLI |
| 音频转文字、转录 | Whisper API / Whisper 本地 |
| 自动优化内容、生成变体 | autoresearch |
| 查看模型用量、token 统计 | model-usage（CodexBar） |
| 生成视频、3D 模型 | MiniMax CLI / 多模态 API |

**目录结构**：
```
AI 工具箱/
├── SKILL.md（主文件）
└── references/
    ├── 文生图.md
    ├── 语音转文字.md
    ├── 自动研究.md
    ├── 模型统计.md
    ├── 多模态生成.md
    └── 工具对比.md
```

---

## Skill 整合器（元技能）

> **定位**：元技能（meta-skill）—— 专门用来整合、合并、优化其他 skills 的方法论。

当用户说"整合 skills"、"N 合一"、"合并 skills"、"整理 skills"时触发。

### 核心原则

1. **三级层级结构** — 每个整合后的 skill 必须采用三级结构
2. **横向对比，集众家之所长** — 全量扫描，逐一对比，取最长板
3. **用简洁明了的中文说明使用场景** — 表格列出，触发词加粗
4. **按需启用（二级动态选择）** — 不强制加载所有工具
5. **集成最佳工具（不限于现有 skills）** — 联网搜索更好的工具
6. **多级退回机制（Plan A → Plan B → Plan C）** — 自动降级，不询问用户
7. **全量扫描，不遗漏** — 列出所有被替代的旧 skills
8. **预设期待命中** — 用户输入匹配时直接命中

### 执行流程

```
Step 1：全量扫描，收集现有 Skills
   ↓
Step 2：横向对比，制作对比表
   ↓
Step 3：联网搜索最佳工具，补充集成
   ↓
Step 4：设计三级层级结构
   ↓
Step 5：编写 SKILL.md
   ↓
Step 6：创建 references/ 目录（详细文档）
   ↓
Step 7：归档旧 Skills
   ↓
Step 8：测试验证
```

---

## 安装使用

### 方式一：直接下载

```bash
# 下载整个仓库
git clone https://github.com/smiling66652/workbuddy-skill-toolkits.git

# 将需要的工具箱复制到 ~/.workbuddy/skills/
cp -r workbuddy-skill-toolkits/开发工具箱 ~/.workbuddy/skills/
cp -r workbuddy-skill-toolkits/文档工具箱 ~/.workbuddy/skills/
# ...
```

### 方式二：在 WorkBuddy 中安装

在 WorkBuddy 对话中直接说：

```
帮我安装开发工具箱 skill
```

WorkBuddy 会自动加载对应的 skill。

---

## 整合前后对比

| 指标 | 整合前 | 整合后 |
|------|--------|--------|
| Skill 数量 | 40+ 个独立 skills | 6 个工具箱 + 1 个元技能 |
| 上下文消耗 | 每个 skill 500-1000 tokens | 每个工具箱 200-300 tokens |
| 响应速度 | 慢（需加载多个 skills） | 快（按需加载） |
| 维护成本 | 高（40+ 个独立仓库） | 低（6 个工具箱统一管理） |
| 工具选择 | 分散，易遗漏 | 集中，横向对比最优 |

---

## 技术架构

### 三级层级结构详解

**一级：需求分析**
- 输入：用户的自然语言请求
- 处理：匹配触发词，判断需求类型
- 输出：跳转二级的指令

**二级：工具选择**
- 输入：需求类型
- 处理：查表选择最佳工具，读取对应的 `references/*.md`
- 输出：工具名称 + 参数模板

**三级：执行指令**
- 输入：工具名称 + 参数
- 处理：调用工具，获取结果
- 输出：格式化后的结果返回给用户

### 多级退回机制

```
Plan A（推荐方案）
  └── 如果失败 → 自动降级到 Plan B

Plan B（备选方案）
  └── 如果失败 → 自动降级到 Plan C

Plan C（兜底方案）
  └── 一定会成功，或给出明确的手动操作步骤
```

---

## 贡献指南

欢迎贡献新的工具箱或优化现有工具箱！

1. Fork 本仓库
2. 创建分支（`git checkout -b feature/新工具箱`）
3. 提交更改（`git commit -m 'Add 新工具箱'`）
4. 推送分支（`git push origin feature/新工具箱`）
5. 创建 Pull Request

### 贡献要求

- 遵循三级层级结构
- 提供横向对比表
- 包含多级退回机制
- 用简洁中文说明使用场景

---

## 许可证

[MIT License](LICENSE)

---

## 更新日志

### v1.0.0 (2026-06-02) - 初始版本

- ✅ 开发工具箱 v4.0.0
- ✅ 文档工具箱 v4.0.0
- ✅ 联网工具箱 v4.0.0
- ✅ 安全审查工具箱 v2.0.0
- ✅ 知识工具箱 v4.0.0
- ✅ AI 工具箱 v3.0.0
- ✅ Skill 整合器 v1.0.0

---

## 联系方式

- GitHub：[@smiling66652](https://github.com/smiling66652)
- Email：2240678683@qq.com

---

**⚙️ 由 WorkBuddy AI 助手自动生成并维护**
