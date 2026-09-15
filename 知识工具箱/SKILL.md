---
name: 知识工具箱
description: >
  知识管理工具箱：跨会话记忆、Obsidian/Joplin 笔记管理、IMA 知识库上传检索、NotebookLM 学习材料生成、目标追踪。集成
  agent-memory、Obsidian CLI、Joplin、IMA 知识库、NotebookLM、goal-tracker。
  触发词：记住这个、记一下、我的笔记、Obsidian笔记、Joplin、上传到知识库、生成播客、追踪目标、知识库搜索
  不用于：文献/参考文献/BibTeX/Zotero（走 学术研究工具箱）；IMA 相关操作（走 ima-skills，供应商权威实现）
version: 4.1.0
author: WorkBuddy 整合版
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
| 上传到IMA知识库 / 创建IMA笔记 | **加载 `ima-skills` 技能**（权威实现） | IMA OpenAPI |
| 生成学习材料（播客/测验） | [二级：NotebookLM](references/NotebookLM.md) | NotebookLM API |
| 追踪目标/写日记 | [二级：目标追踪](references/目标追踪.md) | goal-tracker |
| 快速按格式写引用示例（APA/MLA/Chicago/GB-T） | [二级：引用管理](references/引用管理.md) | 四种格式手写示例 + CrossRef |
| 文献库 / BibTeX / Zotero / DOI 抓取 | **走 `学术研究工具箱/references/引用管理.md`**（边界见下） | — |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 持久记忆 | 记住这个、别忘了、我的偏好是、以后都这样 | [二级：持久记忆](references/持久记忆.md) |
| Obsidian | Obsidian笔记、创建笔记、搜索Obsidian | [二级：Obsidian管理](references/Obsidian.md) |
| Joplin | Joplin笔记、创建笔记、同步笔记 | [二级：Joplin管理](references/Joplin.md) |
| IMA知识库 / IMA笔记 | 上传到知识库、搜索知识库、IMA笔记 | **加载 `ima-skills` 技能**（本目录两篇 IMA 文档已降级为指针） |
| NotebookLM | 生成播客、生成测验、学习内容 | [二级：NotebookLM](references/NotebookLM.md) |
| 目标追踪 | 追踪目标、写日记、里程碑 | [二级：目标追踪](references/目标追踪.md) |
| 引用管理（手写格式示例） | 加参考文献、引用格式、APA/MLA/Chicago/GB-T | [二级：引用管理](references/引用管理.md) |
| 引用管理（文献库/抓取） | BibTeX、Zotero、DOI、文献库 | 走 `学术研究工具箱/references/引用管理.md` |

> **两处「引用管理」的分工（2026-09-15 划清，避免模型漂移）**：
> - **本技能（知识工具箱）**＝「**按指定格式快速写出引用文本**」：APA / MLA / Chicago / GB-T 7714 四种格式的具体书写示例、CrossRef 取 DOI 信息、`citation-manager` 技能指针。
> - **学术研究工具箱**＝「**文献库与自动化**」：BibTeX 条目模板、DOI→BibTeX 实测 curl 命令、Zotero 集成（Word/LaTeX/合工大）、引用规范对比表、去重与批量整理。
> - 两份是**互补关系**，不是重复，故都保留。判据：要「一段现成的引用文字」来这边；要「管文献库/抓 BibTeX/配 Zotero」去那边。

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
| `references/IMA知识库.md` | ⚠️ 已降级为**指针**（指向 `ima-skills`），仅保留「绕开 wrapper 直连 OpenAPI」的两条备查 |
| `references/IMA笔记.md` | ⚠️ 已降级为**指针**（指向 `ima-skills`），不要按旧内容操作 |
| `references/NotebookLM.md` | 需要生成学习材料时 |
| `references/目标追踪.md` | 需要追踪目标/写日记时 |
| `references/引用管理.md` | 需要**按格式手写引用示例**时（文献库/BibTeX/Zotero → 学术研究工具箱） |
