---
name: AI 工具箱
description: >
  统一 AI 模型工具箱（三级层级结构）： 一级：分析用户需求（文生图/语音转文字/自动化研究/模型统计/多模态生成）
  二级：选择最佳工具（OpenAI/MiniMax/Whisper/autoresearch） 三级：执行指令并返回结果。 集成最佳工具：OpenAI
  API、MiniMax CLI、Whisper、autoresearch、model-usage。
version: 3.0.0
author: WorkBuddy 整合版
disable: true
---

# AI 工具箱

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断用户要做什么（文生图/语音转文字/研究优化/统计/多模态）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 跳转二级 | 推荐工具 |
|---------|---------|---------|
| 生成图片、画一张 | [二级：文生图](references/文生图.md) | OpenAI DALL-E / MiniMax CLI |
| 音频转文字、转录 | [二级：语音转文字](references/语音转文字.md) | Whisper API / Whisper 本地 |
| 自动优化内容、生成变体 | [二级：自动研究优化](references/自动研究.md) | autoresearch |
| 查看模型用量、token统计 | [二级：模型使用统计](references/模型统计.md) | model-usage (CodexBar) |
| 生成视频、3D模型 | [二级：多模态生成](references/多模态生成.md) | MiniMax CLI / 多模态API |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 文生图 | 生成图片、画一张、AI画画、做个logo | [二级：文生图](references/文生图.md) |
| 语音转文字 | 转文字、语音转文字、转录音频、Whisper | [二级：语音转文字](references/语音转文字.md) |
| 自动研究 | 自动优化、生成变体、研究这个话题 | [二级：自动研究优化](references/自动研究.md) |
| 模型统计 | 模型用量、token统计、查看使用量 | [二级：模型使用统计](references/模型统计.md) |
| 多模态生成 | 生成视频、生成3D、图片特效 | [二级：多模态生成](references/多模态生成.md) |

---

## 通用规则

### API Key 管理

- 所有 API Key 统一放在环境变量或 `.env` 文件中
- 不要将 API Key 写入代码或上传到 Git
- 使用 `python-dotenv` 加载 `.env` 文件

### 成本控制

- 文生图按张计费，注意批量生成数量
- 语音转文字按分钟计费，长音频先切片
- 多模态生成（视频/3D）按秒/按模型计费

### 并行策略

- 多个独立 AI 任务 → 用子 Agent 分治并行执行
- 每个子 Agent 调用不同 API，无竞态风险

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/文生图.md` | 需要生成图片时 |
| `references/语音转文字.md` | 需要转录音频时 |
| `references/自动研究.md` | 需要自动优化内容时 |
| `references/模型统计.md` | 需要查看模型用量时 |
| `references/多模态生成.md` | 需要生成视频/3D时 |
| `references/工具对比.md` | 需要选择最佳工具时 |
