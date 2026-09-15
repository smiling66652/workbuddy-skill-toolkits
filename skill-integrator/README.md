# Skill Integrator (技能整合器)

> 元技能（meta-skill）—— 专门用来整合、合并、优化其他 skills 的方法论与执行流程。

---

## 核心功能

本 skill 提供一套完整的 skill 整合方法论，包括：

1. **三级层级结构**：一级需求分析 → 二级工具选择 → 三级执行指令
2. **横向对比方法论**：全量扫描 → 逐一对比 → 取众家之所长
3. **中文场景说明规范**：用简洁中文说明使用场景
4. **按需启用机制**：按需加载工具和 references，节省 tokens
5. **最佳工具搜索集成**：联网搜索更好的 CLI/API 工具
6. **多级退回机制**：Plan A → Plan B → Plan C，提高鲁棒性
7. **全量扫描规范**：不遗漏任何一个相关 skill
8. **预设期待命中**：预先定义用户可能的期待，直接命中

---

## 使用场景

| 用户输入 | 直接命中 | 说明 |
|-------------|------------|------|
| "整合 skills" | 触发本 skill | 开始整合流程 |
| "N 合一" | 触发本 skill | 开始整合流程 |
| "合并 skills" | 触发本 skill | 开始整合流程 |
| "整理 skills" | 触发本 skill | 开始整合流程 |

---

## 快速开始

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

### Step 3：设计三级层级结构

```
一级：需求分析（判断用户要做什么）
  ↓
二级：工具选择（根据需求选择最佳工具，见对比表）
  ↓
三级：执行指令（调用工具并返回结果）
```

### Step 4：编写 SKILL.md

使用本仓库 `SKILL.md` 作为模板。

### Step 5：创建 references/ 目录（详细文档）

把每个工具的详细用法、API 文档、示例拆到 `references/` 下：

```
skill-name/
├── SKILL.md（主文件，≤ 5000 词）
└── references/
    ├── 工具A.md（详细用法）
    ├── 工具B.md（详细用法）
    └── 工具C.md（详细用法）
```

### Step 6：归档旧 Skills

```bash
# 创建归档目录
mkdir -p "C:/Users/Matebook/.workbuddy/skills/.archived"

# 移动旧 skills 到归档目录
mv "C:/Users/Matebook/.workbuddy/skills/old-skill-A" "C:/Users/Matebook/.workbuddy/skills/.archived/"
```

### Step 7：测试验证

1. **触发测试**：说一句话，确认 skill 被正确触发
2. **功能测试**：测试每个二级功能是否正常工作
3. **退回测试**：故意让 Plan A 失败，确认自动降级到 Plan B
4. **边界测试**：测试用户可能的异常输入

---

## 示例：整合"联网工具箱"

**背景**：原有 10 个独立 skills（web-access、web-scraper、browser-use、playwright-cli、summarize、tavily、perplexity、multi-search-engine、youtube-watcher、news-summary）

**整合步骤**：

1. **全量扫描**：确认这 10 个 skills 都存在
2. **横向对比**：制作对比表，找出每个工具的优缺点
3. **设计三级结构**：
   - 一级：搜索/抓取/自动化/总结/AI搜索/YouTube/新闻
   - 二级：智能搜索/网页抓取/Playwright/Agent Browser/Human Browser/总结/AI搜索/YouTube转录/新闻摘要
   - 三级：具体命令
4. **编写 SKILL.md**：使用上面的模板
5. **创建 references/**：把每个工具的详细用法拆到 `references/`
6. **归档旧 skills**：移动到 `.archived/`
7. **测试验证**：测试每个功能是否正常工作

**结果**：10 个 skills → 1 个 `联网工具箱`，上下文减少 70%，响应速度提升 2-3 倍。

---

## 目录结构

```
skill-integrator/
├── SKILL.md（主文件）
└── references/
    ├── 01-三级层级结构.md
    ├── 02-横向对比方法论.md
    ├── 03-中文场景说明规范.md
    ├── 04-按需启用机制.md
    ├── 05-最佳工具搜索集成.md
    ├── 06-多级退回机制.md
    ├── 07-全量扫描规范.md
    ├── 08-预设期待命中.md
    ├── 09-执行流程-Step1-4.md
    ├── 10-执行流程-Step5-8.md
    ├── 11-高级技巧.md
    └── 12-常见问题.md
```

---

## 贡献

欢迎提交 Pull Request 来改进本 skill！

---

## 许可证

MIT License

---

## 更新记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-06-02 | 初始版本，基于用户工作原则生成 |
