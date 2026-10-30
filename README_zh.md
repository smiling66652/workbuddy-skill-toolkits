# WorkBuddy 技能库

> 本仓库是 WorkBuddy 的**技能库**：一组相互独立、可单独取用的技能（Skill）集中管理。当前收录 **61 个技能**，覆盖联网、文档、开发、知识、学术研究、小程序、安全、AI、工程方法论、项目专用，以及设计/前端/UI、视频/多媒体/语音、办公/文档、微信/内容运营、写作/内容质量等场景。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills: 61](https://img.shields.io/badge/Skills-61-blue.svg)](INDEX.md)
[![Index](https://img.shields.io/badge/Index-INDEX.md-purple.svg)](INDEX.md)

> 技能清单唯一权威来源是根目录 `INDEX.md`。本仓库共 **61 个目录**，完整清单（含版本/触发词/用途）一律以 `INDEX.md` 为准；`INDEX.md` 表头即「61 个」。`goodnight-letter`、`ima-skills`、`group-intel`、`napcat-ops` 等本机有、本仓库不收的技能不计入。

## 技能分组

**常驻规程**
- `WorkBuddy 工作原则` (2.0.0) — 每个任务自动注入的 12 条工作原则（`auto_load`，无触发词）

**领域工具箱**
- `联网工具箱` (6.0.0) — 联网/浏览器/下载/反爬/AI生成唯一入口（自持 CDP Proxy、`pw.mjs` 等脚本）
- `文档工具箱` (4.1.0) — PDF/Word/PPT/Excel/Markdown 本地处理
- `开发工具箱` (4.1.0) — 写代码/构建/Git/测试/前端/移动端/MCP
- `知识工具箱` (4.1.0) — 笔记/记忆/目标追踪（IMA、引用→指向权威实现）
- `学术研究工具箱` (1.0.0) — 文献检索/综述/引用/一手源调研
- `微信小程序开发套件` (2.1.0) — 小程序垂直全流程
- `安全审查工具箱` (2.1.0) — Skill 安全审计/第三方审查/代码安全（腾讯云鼎/朱雀实验室、skill-vetter）
- `AI 工具箱` (3.1.0) — 语音转文字/模型用量/自动研究 ⚠ 本机依赖未装

**方法论与元技能**
- `工程方法论工具箱` (1.0.0) — 调试/TDD/验证/审查/需求澄清
- `评审委员会` (1.0.0) — 多视角把关（工程/产品/设计/QA/复盘）
- `skill-integrator` (1.0.0) — 元技能：如何合并技能

**单点工具**
- `git-ship` (1.0.0) 提交推送+密钥检查
- `techdebt` (1.0.0) 仓库技术债体检
- `weekly-review` (1.0.0) 周报生成
- `qf-english-polish` (1.0.0) 英文润色
- `image-to-editable-pptx` (2.0.0) 图片→可编辑 PPTX

**项目专用**
- `hfut-inspector` (5.0.0) 合工大信息巡检
- `yuketang-harvester` (1.0.0) 长江雨课堂课件归档

### 新增技能（42 个，2026-10-30 整合入库）

> 以下为本次新增、未在上方逐行展开的技能，完整版本 / 触发词 / 用途见 `INDEX.md`。

- **设计 / 前端 / UI（11）**：`accessibility-audit`、`design-review`、`design-router`、`frontend-design-guidelines`、`frontend-dev`、`responsive-design`、`tastemaker`、`typography`、`ui-design`、`web-design-guidelines`、`web-design-layout`
- **视频 / 多媒体 / 语音（9）**：`ai-explainer-video`、`ai-short-video-maker`、`ai-video-short`、`edge-tts-read`、`fuheshun-auto-clip`、`local-video-pipeline`、`sherpa-onnx-tts`、`short-video-script-to-finished-video`、`video-script`
- **办公 / 文档（6）**：`kdocs`、`markitdown-skill`、`pdf`、`pptx`、`word-toolkit`、`xlsx`
- **微信 / 内容运营（3）**：`wechat-article-pro`、`wechat-article-search`、`qq-email`
- **开发 / 工程 / Agent（6）**：`agent-browser-core`、`browser-use`、`fullstack-dev`、`github`、`self-improving-agent`、`web-access`
- **写作 / 内容质量（2）**：`antislop`、`humanizer`
- **元技能 / 方法论（5）**：`cangjie-skill`、`delivery-no-pseudoblock`、`grilling`、`skill-creator`、`技能包跨机器打包`

> 每个技能的完整触发词、用途见 `INDEX.md` 与各技能自己的 `SKILL.md`。`description` 里的触发词是模型路由的唯一依据。

## 设计理念

工具箱类技能采用**三级层级结构**（一级需求分析 → 二级工具选择 → 三级执行），并普遍遵循**多级退回机制**（Plan A → B → C，失败自动降级）。单点工具、项目专用技能通常是单文件、单目的，不套用此结构。

## 快速安装

技能是独立目录，可单独取用：

```bash
git clone https://github.com/smiling66652/workbuddy-skill-toolkits.git
cp -r 联网工具箱 ~/.workbuddy/skills/   # 挑你需要的目录整目录复制
```

或在 WorkBuddy 对话中说「帮我安装 联网工具箱 skill」。

## 技能索引

`INDEX.md` 是技能清单唯一来源（由 `skill-doctor.py` 生成，勿手改）。技能增删改后重新生成：

```bash
python skill-doctor.py <skills目录> --fix-index
```

## 文档

`docs/` 仅保留与项目相关的持续约定（命名规范、目录结构、操作指南），详见 `docs/README.md`。

## 许可证

MIT License
