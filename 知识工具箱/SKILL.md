---
name: 知识工具箱
description: >
  统一知识管理工具箱（三级层级结构）： 一级：分析用户需求（记忆/笔记/Obsidian/IMA/目标追踪/引用）
  二级：选择最佳工具（agent-memory/Obsidian/Joplin/IMA/NotebookLM） 三级：执行指令并返回结果。
  集成最佳工具：agent-memory、Obsidian CLI、Joplin、IMA知识库、NotebookLM、目标追踪。
version: 4.0.0
author: WorkBuddy 整合版
disable: true
---

# 知识工具箱

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断用户要做什么（记忆/笔记/知识库/目标/引用）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 跳转二级 | 推荐工具 |
|---------|---------|---------|
| 让AI记住某事（跨会话） | [二级：持久记忆](references/持久记忆.md) | agent-memory |
| 管理Obsidian笔记 | [二级：Obsidian管理](references/Obsidian.md) | Obsidian CLI |
| 管理Joplin笔记 | [二级：Joplin管理](references/Joplin.md) | Joplin API |
| 上传到IMA知识库 | [二级：IMA知识库](references/IMA知识库.md) | IMA OpenAPI |
| 创建IMA笔记 | [二级：IMA笔记](references/IMA笔记.md) | IMA OpenAPI |
| 生成学习材料（播客/测验） | [二级：NotebookLM](references/NotebookLM.md) | NotebookLM API |
| 追踪目标/写日记 | [二级：目标追踪](references/目标追踪.md) | goal-tracker |
| 论文加参考文献 | [二级：引用管理](references/引用管理.md) | Citation Manager / CrossRef |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 持久记忆 | 记住这个、别忘了、我的偏好是、以后都这样 | [二级：持久记忆](references/持久记忆.md) |
| Obsidian | Obsidian笔记、创建笔记、搜索Obsidian | [二级：Obsidian管理](references/Obsidian.md) |
| Joplin | Joplin笔记、创建笔记、同步笔记 | [二级：Joplin管理](references/Joplin.md) |
| IMA知识库 | 上传到知识库、搜索知识库、IMA笔记 | [二级：IMA知识库](references/IMA知识库.md) |
| NotebookLM | 生成播客、生成测验、学习内容 | [二级：NotebookLM](references/NotebookLM.md) |
| 目标追踪 | 追踪目标、写日记、里程碑 | [二级：目标追踪](references/目标追踪.md) |
| 引用管理 | 加参考文献、引用格式、CrossRef | [二级：引用管理](references/引用管理.md) |

---

## 通用规则

### 知识库选择建议

- **个人知识管理** → Obsidian（本地，Markdown）
- **跨设备同步** → Joplin（支持移动端）
- **AI辅助学习** → NotebookLM（Google生态）
- **企业知识库** → IMA（腾讯生态）
- **跨会话记忆** → agent-memory（WorkBuddy内置）

### 并行策略

- 多个独立知识操作 → 用子 Agent 分治并行执行
- 每个子 Agent 操作不同知识库，无竞态风险

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/持久记忆.md` | 需要跨会话记忆时 |
| `references/Obsidian.md` | 需要管理Obsidian笔记时 |
| `references/Joplin.md` | 需要管理Joplin笔记时 |
| `references/IMA知识库.md` | 需要操作IMA知识库时 |
| `references/IMA笔记.md` | 需要创建/搜索IMA笔记时 |
| `references/NotebookLM.md` | 需要生成学习材料时 |
| `references/目标追踪.md` | 需要追踪目标/写日记时 |
| `references/引用管理.md` | 需要管理参考文献时 |
