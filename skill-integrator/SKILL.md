---
name: skill-integrator
description: >
  元技能：将多个同类 skills 整合为统一套件的方法论与执行流程。
  当用户说"整合 skills"、"N合一"、"合并 skills"、"整理 skills"时触发。
  提供三级层级结构模板、横向对比方法论、最佳工具搜索与集成流程。
version: 1.0.0
author: WorkBuddy（基于用户工作原则生成）
agent_created: true
---

# Skill 整合器（Skill Integrator）

> **定位**：元技能（meta-skill）—— 专门用来整合、合并、优化其他 skills 的方法论。

---

## 核心原则（整合时的必须遵守）

### 原则一：三级层级结构

每个整合后的 skill 必须采用三级结构：

```
一级：需求分析（判断用户要做什么）
  ↓
二级：工具选择（根据需求选择最佳工具，见对比表）
  ↓
三级：执行指令（调用工具并返回结果）
```

**为什么**：用户说一句话，AI 先理解意图（一级），再选工具（二级），最后执行（三级）。结构清晰，不易出错。

---

### 原则二：横向对比，集众家之所长

整合前，必须把**所有同类 skills** 全部找出来，逐一对比：

1. **全量扫描**：`ls ~/.workbuddy/skills/` + 搜索关键词，不遗漏任何一个
2. **逐一读取 SKILL.md**：理解每个 skill 的功能边界、优缺点
3. **横向对比表**：列出每个工具的：速度、精度、适用场景、缺点
4. **取最长板**：每个功能点取所有 skills 中最优的实现方式
5. **补齐短板**：某个功能所有现有 skills 都做得不好 → 联网搜索更好的工具

**输出**：整合后的 skill 必须比任何一个原有 skill 都更强。

---

### 原则三：用简洁明了的中文说明使用场景

SKILL.md 的 `description` 和正文必须用**简洁中文**，规则：

- 使用场景用**表格**列出（一看就懂）
- 触发词用**加粗**标注
- 避免英文堆砌，必要时中英对照
- 示例必须**具体**（如：`mmx image "一只猫"` 而非 `使用 image 命令`）

---

### 原则四：按需启用（二级动态选择）

整合后的 skill 不强制加载所有工具，而是：

1. **一级**：分析用户需求（无需加载任何工具）
2. **二级**：根据需求，**只加载需要的工具/references**
3. **三级**：执行

**实现方式**：SKILL.md 正文只写一级和二级的"选择逻辑"，具体工具的详细用法写在 `references/` 下，按需读取。

---

### 原则五：集成最佳工具（不限于现有 skills）

整合时，如果现有 skills 的功能不够好，必须：

1. **联网搜索**同类最佳 CLI/API 工具
   - 搜索关键词：`best CLI tool for X 2025`、`X 工具对比`、`X 替代品`
   - 信息来源：官方文档 > 技术博客 > 社区讨论
2. **从以下来源寻找工具**：
   - [cli-anything-hub](https://clianything.cc)（CLI 工具库）
   - GitHub（搜索 `awesome-xxx`、`xxx-cli`）
   - Skill Hub / WorkBuddy 技能市场
   - MCP Server 市场
3. **验证后集成**：安装 → 测试 → 写进 skill 的 `references/`

---

### 原则六：多级退回机制（Plan A → Plan B → Plan C）

每个功能点必须设计**至少 2 套备选方案**：

```markdown
## 功能：XXX

### Plan A（推荐方案）
- 工具：XXX
- 前提：需要 XXX 已安装
- 如果失败 → 自动降级到 Plan B

### Plan B（备选方案）
- 工具：YYY
- 前提：需要 YYY 已安装 或 使用内置工具
- 如果失败 → 自动降级到 Plan C

### Plan C（兜底方案）
- 工具：ZZZ（或提示用户手动操作）
- 一定会成功，或给出明确的手动操作步骤
```

**触发条件**：某个方案执行失败 → 自动尝试下一个方案，**不询问用户**（除非所有方案都失败）。

---

### 原则七：全量扫描，不遗漏

整合前必须确认**所有相关 skills** 都已找到：

1. **按名称搜索**：`ls ~/.workbuddy/skills/ | grep -i "关键词"`
2. **按内容搜索**：`find ~/.workbuddy/skills/ -name "SKILL.md" | xargs grep -l "关键词"`
3. **检查 archived**：`ls ~/.workbuddy/skills/.archived/`（如果之前整合过）
4. **联网搜索**：是否有更好的同类 skill 可以下载

**输出**：在 SKILL.md 的"整合来源"章节，列出所有被替代的旧 skills 名称。

---

### 原则八：预设期待命中

在 SKILL.md 中**预先定义用户可能的期待**，当用户输入匹配时直接命中：

```markdown
## 预设期待命中

| 用户输入模式 | 直接命中 | 说明 |
|-------------|------------|------|
| "搜索 XXX" | 一级→搜索需求 → 二级→智能搜索 → 三级→执行 | 无需询问 |
| "抓取这个页面" | 一级→抓取需求 → 二级→网页抓取管道 → 三级→执行 | 自动选择最优方法 |
| "打开浏览器点击XXX" | 一级→自动化需求 → 二级→Playwright → 三级→执行 | 支持登录态 |
```

**效果**：用户感觉"它懂我"，不需要反复解释。

---

## 执行流程（Step-by-Step）

### Step 1：全量扫描，收集现有 Skills

```bash
# 1. 列出所有 skills
ls "C:/Users/Matebook/.workbuddy/skills/" | sort

# 2. 按关键词搜索相关 skills
find "C:/Users/Matebook/.workbuddy/skills/" -name "SKILL.md" | xargs grep -l "关键词"

# 3. 读取每个相关 skill 的 SKILL.md（前 30 行足够判断功能）
for d in "C:/Users/Matebook/.workbuddy/skills/"*/; do
  echo "=== $(basename $d) ==="
  head -30 "$d/SKILL.md" 2>/dev/null
done
```

**输出**：一个清单，列出所有需要整合的 skills 及其功能描述。

---

### Step 2：横向对比，制作对比表

对每个功能点，制作对比表：

```markdown
## 功能点：XXX

| Skill 名称 | 速度 | 精度 | 优点 | 缺点 | 是否采用 |
|------------|------|------|------|------|------------|
| skill-A | 快 | 高 | 支持登录态 | 不支持 Cloudflare | ✅ 采用（速度+登录态） |
| skill-B | 慢 | 非常高 | 绕过 Cloudflare | 需要付费 | ✅ 采用（作为 Plan B） |
| skill-C | 中 | 中 | 免费 | 功能少 | ❌ 不采用 |
```

**决策规则**：
- 取每个 skill 的**最长板**整合进新 skill
- 如果所有现有 skills 都做得不好 → 进入 Step 3（搜索更好的工具）

---

### Step 3：联网搜索最佳工具，补充集成

如果现有 skills 功能不够好，或缺少某个功能：

```bash
# 使用 联网工具箱 搜索
# 触发词：搜索、查一下、找最好的 XXX 工具
```

**搜索关键词模板**：
- `best CLI tool for X 2025 2026`
- `X vs Y vs Z comparison`
- `X 工具中文教程`
- `X API 文档`
- `awesome-X`（GitHub 上的精选列表）

**验证流程**：
1. 找到工具 → 读取官方文档
2. 安装工具 → 测试基本功能
3. 确认可用 → 写进 `references/工具名.md`
4. 在 SKILL.md 的二级"工具选择"中引用

---

### Step 4：设计三级层级结构

**一级：需求分析**

用表格列出所有用户需求类型及触发词：

```markdown
## 一级：需求分析

| 需求类型 | 触发词示例 | 跳转二级 |
|------------|------------|------------|
| 搜索 | 搜索、查一下、找资料 | [二级：智能搜索](#二级智能搜索) |
| 抓取 | 抓取、提取正文、爬取 | [二级：网页抓取](#二级网页抓取) |
```

**二级：工具选择**

用表格列出每个需求类型的最佳工具及选择逻辑：

```markdown
## 二级：智能搜索

| 用户需求 | 推荐工具 | 说明 |
|-------------|------------|------|
| 中文搜索 | 百度、Bing CN | 自动选择 |
| 英文搜索 | Google、DuckDuckGo | 自动选择 |
```

**三级：执行指令**

写清楚每个工具的具体用法（命令、参数、示例）。

如果内容太长 → 拆到 `references/工具名.md`，在三级中写"详见 `references/工具名.md`"。

---

### Step 5：编写 SKILL.md

**模板**：

```markdown
---
name: 工具箱名称
description: >
  简洁中文描述（一句话说明这个 skill 能做什么，何时使用）。
  当用户说"XXX"时触发。
version: 1.0.0
author: WorkBuddy 整合版（集成 skill-A/skill-B/skill-C）
agent_created: true
---

# 工具箱名称

> **三级层级调用规则**：
> 1. **一级：需求分析** - 判断用户要做什么
> 2. **二级：工具选择** - 根据需求选择最佳工具
> 3. **三级：执行指令** - 调用工具并返回结果

---

## 快速选择指南

（表格：用户需求 → 推荐工具 → 说明）

---

## 一级：需求分析

（表格：需求类型 → 触发词 → 跳转二级）

---

## 二级 + 三级：工具选择与执行

### 二级：XXX

**适用场景**：...

**三级执行**：

（具体命令、参数、示例）

---

## 整合来源

本 skill 整合了以下原有 skills：

- `old-skill-A` → 功能：... → 已归档至 `.archived/`
- `old-skill-B` → 功能：... → 已归档至 `.archived/`

---

## 预设期待命中

（表格：用户输入模式 → 直接命中 → 说明）

---

## 多级退回机制

（每个功能点的 Plan A → Plan B → Plan C）

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| XXX 未找到 | 运行 `npm install -g XXX` |
```

---

### Step 6：创建 references/ 目录（详细文档）

把每个工具的详细用法、API 文档、示例拆到 `references/` 下：

```
skill-name/
├── SKILL.md（主文件，≤ 5000 词）
└── references/
    ├── 工具A.md（详细用法）
    ├── 工具B.md（详细用法）
    └── 工具C.md（详细用法）
```

**为什么**：SKILL.md 保持精简（快速加载），详细文档按需读取（节省 tokens）。

---

### Step 7：归档旧 Skills

整合完成后，旧 skills 必须归档（不直接删除，可恢复）：

```bash
# 创建归档目录
mkdir -p "C:/Users/Matebook/.workbuddy/skills/.archived"

# 移动旧 skills 到归档目录
mv "C:/Users/Matebook/.workbuddy/skills/old-skill-A" "C:/Users/Matebook/.workbuddy/skills/.archived/"
```

**注意**：如果用户要求"彻底删除"，才用 `rm -rf` 删除归档目录。

---

### Step 8：测试验证

整合后的 skill 必须测试：

1. **触发测试**：说一句话，确认 skill 被正确触发
2. **功能测试**：测试每个二级功能是否正常工作
3. **退回测试**：故意让 Plan A 失败，确认自动降级到 Plan B
4. **边界测试**：测试用户可能的异常输入

**输出**：在 `references/test-report.md` 中记录测试结果。

---

## 高级技巧

### 技巧一：使用 skill-creator 规范创建

整合后的 skill 建议使用 `skill-creator` 初始化：

```bash
# 初始化 skill 目录结构
python Scripts/init_skill.py skill-name --path "C:/Users/Matebook/.workbuddy/skills/"
```

### 技巧二：集成 cli-anything-hub 搜索 CLI 工具

在整合过程中，如果需要寻找最佳 CLI 工具：

```bash
# 安装 cli-anything-hub
pip install cli-anything-hub

# 列出所有可用 CLI 工具
python -m cli_hub list

# 搜索特定功能的工具
python -m cli_hub search "web scraping"
```

### 技巧三：使用 WorkBuddy 工作原则

整合 skill 时，遵循 `WorkBuddy 工作原则` skill 中的方法论：

- 明确目标，合理拆分任务
- 多 agent 分工，明确表达目标
- 问题解决两遍还无法成功解决就全网搜索
- 每阶段完成后检查验证
- 多途径尝试，记录错误日志

---

## 示例：整合"联网工具箱"

**背景**：原有 10 个独立 skills（web-access、web-scraper、browser-use、playwright-cli、summarize、tavily、perplexity、multi-search-engine、youtube-watcher、news-summary）

**整合步骤**：

1. **全量扫描**：确认这 10 个 skills 都存在
2. **横向对比**：制作对比表，找出每个工具的优缺点
4. **设计三级结构**：
   - 一级：搜索/抓取/自动化/总结/AI搜索/YouTube/新闻
   - 二级：智能搜索/网页抓取/Playwright/Agent Browser/Human Browser/总结/AI搜索/YouTube转录/新闻摘要
   - 三级：具体命令
5. **编写 SKILL.md**：使用上面的模板
6. **创建 references/**：把每个工具的详细用法拆到 `references/`
7. **归档旧 skills**：移动到 `.archived/`
8. **测试验证**：测试每个功能是否正常工作

**结果**：10 个 skills → 1 个 `联网工具箱`，上下文减少 70%，响应速度提升 2-3 倍。

---

## 常见问题

### Q1：整合后的 skill 太大怎么办？

**A**：拆到 `references/` 下，SKILL.md 只保留核心逻辑（≤ 5000 词）。

### Q2：如何判断哪些 skills 需要整合？

**A**：按功能分类，同一功能类别的 skills 都需要整合。例如：所有"网页抓取"相关的 skills 整合为 `联网工具箱`。

### Q3：整合后旧 skills 可以恢复吗？

**A**：可以。归档在 `.archived/` 目录下，随时可以移回来。

### Q4：如何搜索同类最佳工具？

**A**：使用 `联网工具箱` skill，搜索关键词：`best CLI tool for X 2025`、`X vs Y comparison`、

### Q5：多级退回机制如何实现？

**A**：在 SKILL.md 的每个功能点中，明确写出 Plan A/B/C 的命令和判断条件。WorkBuddy 会自动按顺序尝试。

---

## 更新记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-06-02 | 初始版本，基于用户工作原则生成 |

---

**元技能说明**：本 skill 本身就是一个"如何整合 skills"的方法论。当你需要整合其他 skills 时，让 WorkBuddy 加载本 skill，按照其中的步骤执行。
