---
name: AI 工具箱
description: >
  AI 工具箱：语音转文字（Whisper）、模型用量统计、自动研究优化、提示词优化。
  ⚠️ 2026-09-15 一手核实：本机**无任何一项可用**。`autoresearch` / `model-usage` / `codexbar`
  在 PyPI 上**不存在（404）**，装不上；`mmx-cli` 在 npm 存在但本机未装；`openai-whisper` 真实存在但本机未装；
  且环境变量里没有任何 OPENAI/MINIMAX key。图片/视频/3D 生成请用内置 ImageGen/VideoGen。
  触发词：语音转文字、转录、音频转文字、字幕生成、模型用量、token统计、自动研究、优化提示词
version: 3.2.0
author: WorkBuddy 整合版
---

# AI 工具箱

> ⚠️ **本技能当前没有任何可用能力**（2026-09-15 实测 + 包存在性核实）：
> - `autoresearch`、`model-usage`、`codexbar` —— **PyPI 上不存在**，无法安装
> - `mmx-cli` —— npm 上存在，但本机未安装
> - `openai-whisper` / `faster-whisper` —— PyPI 上存在，但本机未安装
> - 无 OPENAI / MINIMAX 环境变量
>
> **要做这些事，直接用内置工具**：图片/视频生成 → `ImageGen` / `VideoGen`；
> 音频转文字 → 需要先 `pip install openai-whisper` 并自备模型权重。
> 本技能保留是因为它是**安装指引与能力清单**，不是因为它现在能用。

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断用户要做什么（文生图/语音转文字/研究优化/统计/多模态）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 跳转二级 | 推荐工具 |
|---------|---------|---------|
| 音频转文字、转录 | [二级：语音转文字](references/语音转文字.md) | `openai-whisper`（PyPI 存在，**本机未装**） |
| 自动优化内容、生成变体 | [二级：自动研究优化](references/自动研究.md) | ❌ `autoresearch` **PyPI 不存在**，此路不通 |
| 查看模型用量、token统计 | [二级：模型使用统计](references/模型统计.md) | ❌ `model-usage` / `codexbar` **PyPI 均不存在**，此路不通 |
| 生成图片/视频/3D | 内置 ImageGen / VideoGen | ✅ 无需外部依赖，**优先使用** |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|---------|------------|---------|
| 语音转文字 | 转文字、语音转文字、转录音频、Whisper | [二级：语音转文字](references/语音转文字.md) |
| 自动研究 | 自动优化、生成变体、研究这个话题 | [二级：自动研究优化](references/自动研究.md) |
| 模型统计 | 模型用量、token统计、查看使用量 | [二级：模型使用统计](references/模型统计.md) |
| 文生图/视频/3D | 生成图片、生成视频、做3D | 内置 ImageGen / VideoGen（无需本技能） |

---

## 通用规则

### API Key 管理

- 所有 API Key 统一放在环境变量或 `.env` 文件中
- 不要将 API Key 写入代码或上传到 Git
- 使用 `python-dotenv` 加载 `.env` 文件

### 成本控制

- 图片/视频/3D 生成请用内置 ImageGen/VideoGen，按平台计费，避免额外外部依赖
- 语音转文字按分钟计费（Whisper 本地免费，API 按量），长音频先切片
- 模型用量请通过 model-usage 查询，避免超额

### 并行策略

- 多个独立 AI 任务 → 用子 Agent 分治并行执行
- 每个子 Agent 调用不同 API，无竞态风险

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/语音转文字.md` | 需要转录音频时（需先安装 Whisper） |
| `references/自动研究.md` | 需要自动优化内容时（需先安装 autoresearch） |
| `references/模型统计.md` | 需要查看模型用量时（需先安装 model-usage） |
| `references/工具对比.md` | 需要选择最佳工具时 |
