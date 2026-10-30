# 技能索引

> 由 `skill-doctor.py` 自动生成，请勿手工编辑。共 **61** 个技能包。
>
> 用法：**先看「触发词」列判断该用哪个**；「用途」列说明职责边界。
> 标记 ⚡ 的是 `auto_load`（每个任务都会注入，不参与路由选择）。

| # | 目录 | 版本 | 触发词（模型路由依据） | 用途 |
|---|---|---|---|---|
| 1 | ⚡ `WorkBuddy 工作原则` | 2.0.0 | （auto_load，每任务注入，不走路由，无需触发词） | WorkBuddy 执行任务的核心方法论（自动加载） |
| 2 | `AI 工具箱` | 3.2.0 | 语音转文字、转录、音频转文字、字幕生成、模型用量、token统计、自动研究、优化提示词 | AI 工具箱：语音转文字（Whisper）、模型用量统计、自动研究优化、提示词优化 |
| 3 | `accessibility-audit` | 1.0.0 | 无障碍、可访问性、a11y、accessibility、WCAG、WCAG2.2、合规审计、 屏幕阅读器、读屏、键盘导航、焦点可见、focus、alt文本、对比度、色盲、 语义化HTML、ARIA、aria-label、reduced-motion、缩放200%、无障碍整改 | 按 WCAG 2.2 四大类（可感知/可操作/可理解/健壮性）逐条出具可勾选审计清单与修复建议， 输出「问题分级 + 具体改法」的整改报告，默认目标等级 AA |
| 4 | `agent-browser-core` | 1.0.2 | **（缺失！请补触发词）** | OpenClaw skill for the agent-browser CLI (Rust-based with Node.js fallback) enabling AI-friendly web automation with snapshots, refs, and structured commands. |
| 5 | `ai-explainer-video` | 1.0.0 | **（缺失！请补触发词）** | 把一段台词做成"数字人/角色讲解"横屏短视频的完整流水线——生成式工具只出纯场景背景与角色透明素材，配音用 edge-tts，后期用 ffmpeg 把背景循环、角色透明素材叠加、配音合成为 webm 再转 mp4 |
| 6 | `ai-short-video-maker` | 1.0.0 | **（缺失！请补触发词）** | Build short custom videos (birthday greetings, children's stories, |
| 7 | `ai-video-short` | 1.1.2 | **（缺失！请补触发词）** | 用「分段生成 + 本地合成」法把一句话/脚本变成带配音、硬字幕、CTA 的竖屏/横屏 AI 短视频 |
| 8 | `antislop` | 1.0.0 | AI味、AI感、同质化、套路化、千篇一律、假大空、像AI做的、反模式、 交付门禁、delivery gate、设计规则、设计军规、蓝紫渐变、玻璃拟态、圆角过度、 emoji图标、占位文案、死链、为什么不精致、slop、anti-slop | 反「AI 同质化」规则集核心：R-01~R-38 强制规则分三层（Hard Gate 硬门禁 / Purpose-Gate 需说明用途 / Quality Locks 一致性锁）， C-1~C-5 工艺标准，三大活力旋钮（ENERGY/RHYTHM/MOTION），以及交付前必须跑的 Delivery Gate（逐条 PASS/FAIL 且 PASS 需附证据） |
| 9 | `browser-use` | 2.0.7 | **（缺失！请补触发词）** | Automates browser interactions for web testing, form filling, screenshots, and data extraction. |
| 10 | `cangjie-skill` | 2.5.0 | **（缺失！请补触发词）** | Distill a book, long-video transcript, podcast, course, or interview into a coherent set of executable skills. Use when the user asks to 拆书 / 蒸馏一本书 / 把 XX 书做成 skill / 把这个视频/播客/课程蒸馏成 skill / turn a book or video into skills — i.e. wants the frameworks, principles, and methodologies in long-form content extracted into atomic, reusable Claude skills that an agent can invoke in real-world situations. NOT for simple summarization, book reviews, or role-playing as the author (that is nuwa-skill's job). |
| 11 | `delivery-no-pseudoblock` | 1.0.0 | - 检测器扫的是**草稿文本 + 会话上下文**，不是历史错误报告里的字面措辞——历史 3.11 实例只作「对照」附后，不作 | 交付前伪阻断 / 缓干闸门（通用行为级纪律） |
| 12 | `design-review` | 1.0.0 | 设计评审、设计审查、视觉走查、design review、UI走查、交付前检查、质量门、 反模式检查、交互状态检查、无障碍检查、对比参考、设计自查、配色是否多余、间距检查 | 视觉交付质量门：10 份专项参考（排版/色彩/间距/动效/反模式/对齐/响应式/UX文案/灵感/假数据） + 3 个可执行的 Python 检查脚本（反模式扫描、状态完整性、无障碍语义），附交付前自检清单 |
| 13 | `design-router` | 1.0.0 | **（缺失！请补触发词）** | Dispatcher for WorkBuddy's Design assistant. Use this when a design task is in Craft/design mode but the specific deliverable type is not yet determined from UI signals. It first decides which family the deliverable belongs to — an editable canvas design (Ardot) or an AI-generated image/video (Miora) — then names the domain skill to load. Not for PowerPoint .pptx file output (pptx skill). |
| 14 | `edge-tts-read` | 1.0.0 | 文字转语音、朗读、配音、生成语音、TTS、edge-tts | 文字转语音：微软 Edge 在线音色免费合成，中文多音色，可出字幕文件 |
| 15 | `frontend-design-guidelines` | 1.1.0 | 美学方向、设计风格、风格定义、创意UI、独特界面、AI味、避免AI感、紫渐变、 字体选择、字体搭配、展示字体、氛围营造、渐变网格、噪点、视觉冲击、页面调性、设计差异化 | 先定美学方向再写码：10 种极端美学方向（极简/极繁/复古未来/有机/奢华/玩具感/编辑杂志/粗野/装饰艺术/工业）、 字体与配色创意准则、空间构图（非对称/重叠/破网格）、动效与氛围（渐变网格/噪点/颗粒）、以及「AI 味」黑名单 |
| 16 | `frontend-dev` | 0.1.1 | **（缺失！请补触发词）** | Full-stack frontend development combining premium UI design, cinematic animations, AI-generated media assets, persuasive copywriting, and visual art. Builds complete, visually striking web pages with real media, advanced motion, and compelling copy. Use when: building landing pages, marketing sites, product pages, dashboards, generating media assets (image/video/audio/music), writing conversion copy, creating generative art, or implementing cinematic scroll animations. |
| 17 | `fuheshun-auto-clip` | 1.0.1 | 自动剪辑、口播剪辑、视频剪辑流水线、加花字、字幕分页、模版卡片、数据条、去水印、数字人换声、抖音风成片、素材抓配、成片核验 | 把一条竖屏口播原片剪成抖音风成片的 Python+PIL+ffmpeg 流水线：词级对齐花字、短句分页字幕、模版卡片、量化数据条、章节进度条、圆形头像、按场景虚化、语义化音效、混音提速一条龙，不依赖剪映 GUI |
| 18 | `fullstack-dev` | - | **（缺失！请补触发词）** | Full-stack backend architecture and frontend-backend integration guide. TRIGGER when: building a full-stack app, creating REST API with frontend, scaffolding backend service, building todo app, building CRUD app, building real-time app, building chat app, Express + React, Next.js API, Node.js backend, Python backend, Go backend, designing service layers, implementing error handling, managing config/auth, setting up API clients, implementing auth flows, handling file uploads, adding real-time features (SSE/WebSocket), hardening for production. DO NOT TRIGGER when: pure frontend UI work, pure CSS/styling, database schema only. |
| 19 | `git-ship` | 1.0.0 | 提交并推送、一键提交、git 提交推送、开 PR、提交代码、ship it、git-ship、提交前检查 | 把看改动、写规范中文 commit message、提交、推远端、需要时开 PR 串成一条龙；提交前强制做密钥安全检查 |
| 20 | `github` | 1.0.0 | **（缺失！请补触发词）** | Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries. |
| 21 | `grilling` | 1.0.0 | 当用户想被严格拷问、逐题追问、压力测试一个方案或决策 | 当用户想被严格拷问、逐题追问、压力测试一个方案或决策时使用，也响应 grill、grilling、stress-test 等 |
| 22 | `hfut-inspector` | 5.0.0 | 合工大、HFUT、官网巡检、通知扫描、竞赛信息、保研通知、夏令营、讲座、教务通知、巡检报告、每日任务、日报 | 合工大（HFUT）信息巡检统一系统 v5.0 —— 唯一一套系统、唯一入口 hfut.py |
| 23 | `humanizer` | 2.1.1 | **（缺失！请补触发词）** | Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Detects and fixes patterns including: inflated symbolism, promotional language, superficial analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, negative parallelisms, and excessive conjunctive phrases. |
| 24 | `image-to-editable-pptx` | 2.0.0 | 图片转可编辑 PPT、图片转 ppt、截图转 ppt、信息图转 ppt、海报转可编辑、image to editable pptx | 把含文字的图片/截图/信息图/海报变成可编辑的 PowerPoint：OpenCV inpaint 按文字颜色精确擦除笔画 （保留彩色 pill、底条、卡片底色），logo 作图片切片 1:1 还原，其余文字作可编辑文本框叠加 |
| 25 | `kdocs` | 2.5.7 | **（缺失！请补触发词）** | 操作金山文档（WPS 云文档 / Kdocs / 365.kdocs.cn / www.kdocs.cn）云文档的官方 Skill |
| 26 | `local-video-pipeline` | 1.0.1 | 做视频、口播视频、出片、视频合成、配音视频 | 纯 CPU 本地合成口播视频：文案txt → sherpa-onnx中文配音 → Pillow封面卡片 → 文案直出字幕 → ffmpeg合成1080p MP4，全程离线 |
| 27 | `markitdown-skill` | 1.0.1 | **（缺失！请补触发词）** | Convert documents to Markdown using Microsoft's MarkItDown CLI (`markitdown`). Supports PDF, Word, PowerPoint, Excel, images (OCR), audio (transcription), HTML, YouTube, and URLs. Use when a user wants to convert a file or URL to Markdown, extract text from PDFs/images, transcribe audio/video, or batch-convert documents. |
| 28 | `pdf` | 1.0.1 | PDF、读这个PDF、提取PDF文字、OCR、扫描件、扫描版、文字提取、表格提取、拆分、合并、加密、解密、水印、涂黑、脱敏、表单填写、数字签名、转图片、批量处理、pdfkit | Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, handling forms, OCR/scanned-page recognition, encryption/watermarking/redaction, page operations, format conversion, and image text extraction. Use when the user mentions PDF, OCR, scanned documents, or needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale. |
| 29 | `pptx` | 1.0.0 | 做 PPT、幻灯片、演示文稿、slides、deck、presentation、pptx、pitch deck、配色、主题美化、批量生成、JSON 生成 PPT、路演稿 | Use for anything touching .pptx/.potx: create decks and pitch decks, read and extract slide content and speaker notes, edit, combine, and work with templates and layouts; also JSON-driven batch deck generation with 5 built-in color schemes and 11 slide types. |
| 30 | `qf-english-polish` | 1.0.0 | 英文润色、改英文、polish English、英文邮件、英文简历、论文润色、English writing、英文表达 | 英文写作润色：语法纠错、流畅度提升、地道表达改写，覆盖学术/商务/日常/创意四种语域 |
| 31 | `qq-email` | 1.0.0 | 用户要使用 **QQ 邮箱** **发邮件**、**收邮件**、**查邮件**、**代发邮件**或**配置 QQ 邮箱** | QQ邮箱 IMAP receive and SMTP send via Node.js scripts; credentials read from env vars QQ_EMAIL_ACCOUNT and QQ_EMAIL_AUTH_CODE. Use when a user asks to send QQ email, receive/check QQ email, forward email, or configure QQ mailbox. |
| 32 | `responsive-design` | 1.0.0 | 响应式、自适应、移动端适配、断点、媒体查询、container query、容器查询、 流式排版、fluid typography、clamp、移动端布局、手机端、平板、横屏、视口高度、100vh问题 | 响应式实现手册：容器查询、clamp() 流式排版与间距、CSS Grid/Flex 响应式布局、 移动优先断点策略、响应式导航、响应式图片与表格、视口单位（dvh/svh/lvh）与常见坑 |
| 33 | `self-improving-agent` | 1.0.0 | self-improving-agent、捕获学习、错误和纠正，让 Agent 自动积累经验并持续改进 | self-improvement capability in the vertical scenarios and business APIs domain. Use when the user wants to 捕获学习、错误和纠正，让 Agent 自动积累经验并持续改进. Triggers: self-improving-agent, session-logs. Not for requests unrelated to self-improvement. Risk level L1. 中文触发：self-improving-agent、session-logs |
| 34 | `sherpa-onnx-tts` | 1.0.0 | sherpa-onnx-tts、完全离线的文字转语音 | text-to-speech synthesis capability in the creative, voice and multimedia domain. Use when the user wants to 完全离线的文字转语音. Triggers: sherpa-onnx-tts, openai-whisper. Not for requests unrelated to text-to-speech synthesis. Risk level L0. 中文触发：sherpa-onnx-tts、openai-whisper |
| 35 | `short-video-script-to-finished-video` | - | **（缺失！请补触发词）** | 帮助内容创作者、广告与营销团队、电商团队、短剧和漫剧制作团队直接完成“短视频脚本一键生成成片”：既可只输入文字从零生成，也可加入图片、视频或音频控制结果；通过 AI Hive 使用时，生成前自动上传所需素材，提交后自动保存任务、查询进度并下载成片 |
| 36 | `skill-creator` | 0.2.0 | **（缺失！请补触发词）** | Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends CodeBuddy's capabilities with specialized knowledge, workflows, or tool integrations. |
| 37 | `skill-integrator` | 1.0.0 | 搜索、查一下、找最好的 XXX 工具 | 元技能：将多个同类 skills 整合为统一套件的方法论与执行流程 |
| 38 | `tastemaker` | 1.0.0 | 设计、美化、改版、风格、界面、UI、前端页面、落地页、组件、审美、品味、 参考图、参考站、拆解设计、设计DNA、提取配色、提取风格、AI味、同质化、千篇一律、 为什么看着像AI做的、audit this、study this、match this vibe、make this look good、风格锁定、style-lock | 把 UI 设计锚定在「真实像素」而非文字描述上：用脚本从参考图确定性提取配色/结构 DNA， 并用 style-lock 把风格锁住复用到后续每个页面，避免逐页重新推导导致风格漂移 |
| 39 | `techdebt` | 1.0.0 | 技术债、代码坏味道、清理代码、扫描重复代码、找 TODO、tech debt、code smell、重构前的体检 | 扫描一个代码仓库，找出重复代码、明显坏味道、未使用文件/依赖、TODO/FIXME 堆积、超大文件，输出按严重度排序的清单 |
| 40 | `typography` | 1.0.0 | 字体、排版、typography、行高、leading、字距、letter-spacing、字号阶、type scale、 字体配对、font pairing、可变字体、variable font、display cut、中文排版、CJK、中文字体、 行宽、measure、tabular-nums、faux bold、font-display、FOUT、FOIT | Set type for screen and print: measure, leading, tracking, optical sizes, weight axes, and the difference between display and text cuts.（含 CJK 行宽 20-40 字的中文排版参数） |
| 41 | `ui-design` | 1.0.0 | UI设计、界面设计、设计基础、排版规范、配色、色彩搭配、间距系统、视觉层级、 设计审查、设计质量、组件状态、hover态、focus态、设计token、CSS变量、网页美化、视觉规范 | UI 设计基础总纲：布局、排版、色彩、间距、视觉层级、响应式、无障碍、动效、组件状态、设计 Token 三层架构， 含「设计质量 80/20」权重表、8px 间距标尺、1.25 字号阶、WCAG 对比度表，以及交付前 7 类检查清单 |
| 42 | `video-script` | 1.0.0 | \"视频脚本\"、\"短视频脚本\"、\"抖音脚本\"、\"B站脚本\"、 \"视频号脚本\"、\"竖版视频\"、\"Reel 脚本\"、\"写个视频文案\" | 生成视频脚本，覆盖短视频（7-60秒）到中长视频（1-30分钟）全时长 |
| 43 | `web-access` | 2.5.4 | - **程序化方式**（构造 URL 直接导航、eval 操作 DOM）：成功时速度快、精确，但对网站来说不是正常用户行为，可能 | 所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等 |
| 44 | `web-design-guidelines` | 1.0.0 | 网页设计指南、web interface guidelines、界面规范审查、Vercel规范、 审查UI代码、检查可访问性、审计设计、审查UX、检查我的网站、交付前规范体检、逐条比对 | Vercel 官方《Web Interface Guidelines》评审入口：运行时从 GitHub 拉取最新版规则 （vercel-labs/web-interface-guidelines），逐条比对指定文件并输出 file:line 形式的问题清单 |
| 45 | `web-design-layout` | 1.0.0 | 网站设计、页面设计、排版、美化、CSS美化、落地页、网页设计、布局优化、 UI美化、页面改版、设计漂亮的页面、帮我设计一个页面、帮我把页面变好看 | 网站设计与排版美化技能 |
| 46 | `wechat-article-pro` | 1.0.2 | **（缺失！请补触发词）** | 微信公众号文章发布专业版 |
| 47 | `wechat-article-search` | 0.1.1 | **（缺失！请补触发词）** | 搜索微信公众号文章技能 |
| 48 | `weekly-review` | 1.0.0 | 周复盘、本周总结、这周做了什么、周报、weekly review、周报生成、一周回顾 | 汇总本周做了什么：读取 git 提交记录和每日记忆日志，生成结构化周报（本周完成/未完成/卡点/下周计划） |
| 49 | `word-toolkit` | 1.0.1 | Word、DOCX、office 文档、报告、研报、论文、公文、合同、方案、模板、批注、修订（tracked changes）、排版、套模板、写报告、填表，或任务最终产出是 .docx 文件 | Professional Word document (.docx) all-in-one assistant: create, read, edit, format, beautify, apply templates, merge, and validate. Use when the user mentions Word, DOCX, office documents, reports, proposals, contracts, templates, tracked changes, comments, document layout, or any task whose final output is a .docx file. Provides an end-to-end methodology plus a runnable python-docx generator (scripts/make_docx.py), structural inspection & render QA scripts (scripts/inspect_docx.py, scripts/render_docx.py), style assets, and 20 reference docs covering OpenXML, CJK typography, comments/track-changes and scenario workflows (references/). |
| 50 | `xlsx` | 1.0.0 | Excel 表格、xlsx、做个表、spreadsheet、pivot table、透视表、excel chart、公式计算、财务模型、financial model、fill_gaps、merge、OOXML、样式审计、条件格式 | Full lifecycle for Excel files: create workbooks with formulas and formatting, build charts and pivot tables, read and clean data, batch-edit cells, apply conditional formatting, financial modeling, and low-level OOXML surgery (unpack/repack, style audit, formula check). |
| 51 | `yuketang-harvester` | 1.0.0 | 雨课堂、长江雨课堂、下载课件、课程归档、讲义整理、复习资料、课件转 PDF | 批量归档长江雨课堂（changjiang.yuketang.cn）全部课程的课件——课表枚举、课件文字层提取、页图批量下载、讲义装配 |
| 52 | `学术研究工具箱` | 1.0.0 | 论文、文献、检索、查文献、知网、CNKI、arXiv、IEEE、ScienceDirect、 文献综述、怎么写综述、引用、参考文献、BibTeX、Zotero、调研、查资料、柔性抓取、 阻抗控制、软体抓取、compliant grasp、impedance control、soft gripper | 统一学术研究工具箱（三级层级结构） |
| 53 | `安全审查工具箱` | 2.1.0 | 安全审查、这个安全吗、审查这个Skill、安装前检查、第三方Skill、代码安全、依赖安全、漏洞扫描 | 安全审查工具箱：安装 Skill 前安全审计、第三方 Skill 审查、通用代码/依赖安全与漏洞扫描 |
| 54 | `工程方法论工具箱` | 1.0.0 | 调试、debug、报错、修 bug、定位问题、测试、TDD、先写测试、验证、自检、 代码审查、code review、review、需求不清、需求澄清、工程方法论、为什么又出问题 | 统一工程方法论工具箱（三级层级结构） |
| 55 | `开发工具箱` | 4.1.0 | GitHub、Issues、PR、合并请求、CI、跑测试、写单测、生成测试、Flutter、跨平台、Android、Kotlin、Compose、前端、React、Vue、组件、MCP、写代码、构建 | 开发工具箱：GitHub 仓库/Issues/PR 管理，代码静态检查（Semgrep/Bandit/pylint），单元测试与集成测试生成，Flutter/Android 原生/前端 React-Vue/MCP 服务器开发 |
| 56 | `微信小程序开发套件` | 2.1.0 | 小程序、微信小程序、云开发、CloudBase、TDesign、Skyline、小程序UI、部署小程序、小程序性能优化、miniprogram | 微信小程序开发套件：新建小程序项目、UI 组件设计、CloudBase 云开发（云函数/云数据库/部署）、Skyline 高性能渲染、性能优化与部署上线 |
| 57 | `技能包跨机器打包` | 1.0.0 | 打包技能、技能包迁移、另一个电脑用这个技能、离线安装包、portable skill、导出技能、 把技能拷到新电脑、技能搬家、跨机器安装、解压就能用、绿色版技能、skill 分发、拷贝 skills | 把本机 ~/.workbuddy/skills/ 下的任意技能打包成「另一台电脑解压后双击即用」的离线安装包 |
| 58 | `文档工具箱` | 4.1.0 | 读这个PDF、提取PDF文字、改PDF、生成PDF、PDF合并、PDF拆分、创建Word、做PPT、创建Excel、表格处理、转Markdown、OCR、docx、xlsx、pptx | 文档处理工具箱：处理 PDF/Word/Excel/PPT/Markdown 等文件的读取、编辑、生成与格式转换，集成 MinerU（PDF→MD 表格识别 97%）、MarkItDown、pypandoc、docx、pptx、openpyxl |
| 59 | `知识工具箱` | 4.1.0 | 记住这个、记一下、我的笔记、Obsidian笔记、Joplin、上传到知识库、生成播客、追踪目标、知识库搜索 | 知识管理工具箱：跨会话记忆、Obsidian/Joplin 笔记管理、IMA 知识库上传检索、NotebookLM 学习材料生成、目标追踪 |
| 60 | `联网工具箱` | 6.0.0 | 搜索、查资料、查网页、抓取网页、提取正文、浏览器自动化、打开网页、点击、填表、截图、登录后操作、 需要登录态的网站、下载文档、文库下载、付费文档、下载教材、找电子书、找 PDF、搜 ISBN、看视频内容、 YouTube 转录、最新新闻、每日简报、RSS、反爬、Cloudflare、验证码、403、需要绕过拦截、 找回"我之前看过的那个页面"、访问组织内部系统、需要真实浏览器环境 | 所有联网操作的唯一入口，本技能是编排层：先分层判断再分派，实现脚本（CDP 直连 / 本地 Playwright / nodriver 降级链）均已自持在本技能 scripts/ 下，不依赖任何外部技能包 |
| 61 | `评审委员会` | 1.0.0 | 多视角评审、多角色评审、评审委员会、方案评审、设计评审、QA验收、验收、 复盘、retro、多角度看看、帮我审一下、从几个角度看、挑毛病、找问题 （注：单视角的代码审查走「工程方法论工具箱」，本包只接管需要多个视角同时把关的场景） | 多视角评审技能包 |

---

## 关于本索引

- **触发词**取自各技能 frontmatter 的 `description`。这是模型决定「用哪个技能」的唯一依据；
  正文里的词模型看不到。缺触发词的技能会被模型忽略或误判。
- **用途**只取了描述的第一段，完整描述见各技能自己的 `SKILL.md`。
- 技能增删改后重新生成：`python skill-doctor.py <skills目录> --fix-index`。
