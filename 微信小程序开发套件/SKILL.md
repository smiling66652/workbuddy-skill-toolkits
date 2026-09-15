---
name: 微信小程序开发套件
description: >
  微信小程序开发套件：新建小程序项目、UI 组件设计、CloudBase 云开发（云函数/云数据库/部署）、Skyline 高性能渲染、性能优化与部署上线。集成
  CloudBase 全栈开发、TDesign 60+ 组件、微信小程序框架、Skyline 渲染引擎。
  触发词：小程序、微信小程序、云开发、CloudBase、TDesign、Skyline、小程序UI、部署小程序、小程序性能优化、miniprogram
  不用于：其他平台的前端开发（走 开发工具箱）
version: 2.1.0
author: WorkBuddy 整合版（集成 cloudbase/tdesign-miniprogram/wechat-miniprogram/skyline）
---

# 微信小程序开发套件

> **三级层级调用规则**：
> 1. **一级：需求分析** - 判断用户要做什么（新建/UI/云开发/性能/部署）
> 2. **二级：工具选择** - 根据需求选择最佳工具（见下方对比表）
> 3. **三级：执行指令** - 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 二级场景 | 读哪个文档 |
|---|---|---|
| 新建小程序项目、搭框架 | 项目搭建 | [项目结构](references/项目结构.md) ／ [微信框架](references/微信框架.md) |
| 需要后端 / 数据库 / 存储 | 云开发 | [云开发](references/云开发.md) ／ [CloudBase 开发](references/CloudBase开发.md) |
| 需要高质量 UI 组件 | UI 设计 | [TDesign 组件](references/TDesign组件.md) ／ [UI 设计](references/UI设计.md) |
| 需要高性能渲染 / 复杂动画 | 性能优化 | [Skyline 引擎](references/Skyline引擎.md) |
| 需要 AI 聊天界面 | UI 设计 | [TDesign 组件](references/TDesign组件.md) 的 Chat 组件 |
| 发布 / 预览 / 真机调试 | 部署上线 | [部署上线](references/部署上线.md) |

---

## 一级：需求分析

| 需求类型 | 触发词示例 | 跳转二级 |
|---|---|---|
| 新建项目 | 新建小程序、搭建框架、初始化项目 | 项目搭建 |
| UI 设计 | 设计界面、用组件、定制主题、暗黑模式 | UI 设计 |
| 云开发 | 云函数、云数据库、云存储、用户登录 | 云开发 |
| 性能优化 | 渲染性能、动画卡顿、滚动卡顿 | 性能优化 |
| 部署上线 | 部署、发布、预览、真机调试 | 部署上线 |

---

## 二级 + 三级：工具选择与执行

**每个场景的完整做法都在 `references/` 下，按需读取 —— 本文件不重复细节。**

| 二级场景 | 文档 | 覆盖内容 |
|---|---|---|
| 项目搭建 | [项目结构](references/项目结构.md) | 目录规范；`app.js` / `app.json` / `app.wxss` / `project.config.json` 逐文件说明；页面与组件四件套 |
| | [微信框架](references/微信框架.md) | 应用与页面生命周期、WXML 数据绑定、事件处理、自定义组件、WXS、常用 API |
| | [CloudBase 开发](references/CloudBase开发.md) | `@cloudbase/cli` 安装登录、创建带后端的小程序项目 |
| UI 设计 | [UI 设计](references/UI设计.md) | 设计原则、色彩 / 字体 / 间距 / 圆角规范 |
| | [TDesign 组件](references/TDesign组件.md) | 安装、改 `app.json` 与 `project.config.json`、构建 npm、常用组件（Button/Input/Dialog/Toast）、Chat 组件 |
| | [Skyline 引擎](references/Skyline引擎.md) | 启用方式、页面结构、`scroll-view` / `swiper` / `draggable-sheet`、Worklet 动画（共享变量 / timing / spring / decay） |
| 云开发 | [云开发](references/云开发.md) | 初始化云环境、云函数、云数据库增删改查、云存储上传下载 |
| | [CloudBase 开发](references/CloudBase开发.md) | 云函数调用、云数据库、云存储、OPENID 免登录、Web SDK |
| 性能优化 | [Skyline 引擎](references/Skyline引擎.md) | 独立渲染线程、Worklet 动画、高性能组件 |
| 部署上线 | [部署上线](references/部署上线.md) | 预览、真机调试、上传、提交审核、发布、CloudBase 部署与自定义域名 |

### 三条最常用的起步路径

1. **纯小程序（最快）** — 微信开发者工具 → 新建项目 → 填 AppID → 选目录。
   细节见 [项目结构](references/项目结构.md)
2. **带后端（推荐）** — 用 `@cloudbase/cli` 创建项目（自动集成 CloudBase SDK）。
   细节见 [CloudBase 开发](references/CloudBase开发.md)
3. **带 UI 组件库（推荐）** — 新建项目后装 TDesign → 改 `app.json` → 改 `project.config.json` → 在开发者工具里「构建 npm」。
   细节见 [TDesign 组件](references/TDesign组件.md)

> ⚠️ **最高频的两个坑**（都属 TDesign 接入）：
> ① 必须在 `app.json` 里**删掉 `"style": "v2"`**，否则组件样式冲突；
> ② `project.config.json` 需配好 `packNpmManually` / `packNpmRelationList`，否则「构建 npm」找不到包。
>
> 本文件从 655 行精简到约 160 行：原先内联的 530 行二级细节与 `references/` 下的 8 篇文档重复，
> 已删除重复部分（原文备份在 `D:\_trash_\2026-09-15\微信小程序开发套件\SKILL.md.bak`）。
> 入口文件只保留「怎么选」，细节一律去 references。

---

## 通用规则

### 1. 项目结构规范

```
├── app.js                 # 小程序逻辑
├── app.json               # 小程序配置
├── app.wxss               # 全局样式
├── project.config.json     # 项目配置
├── sitemap.json           # 搜索引擎配置
├── pages/                 # 页面目录
│   └── index/
│       ├── index.js        # 页面逻辑
│       ├── index.json      # 页面配置
│       ├── index.wxml      # 页面模板
│       └── index.wxss     # 页面样式
├── components/           # 自定义组件目录
├── cloudfunctions/       # 云函数目录（如果使用云开发）
├── miniprogram_npm/      # npm 包构建目录
└── references/           # 参考文档目录（本 skill 使用）
```

### 2. 命名规范

- **文件/文件夹**：小写字母 + 连字符（kebab-case），如 `pages/user-profile/`
- **组件**：自定义组件使用 PascalCase，如 `MyComponent`
- **变量/函数**：camelCase，如 `getUserInfo`
- **常量**：UPPER_SNAKE_CASE，如 `API_BASE_URL`
- **CSS 类**：kebab-case，如 `.user-profile-card`

### 3. 性能优化建议

- 使用 **Skyline** 渲染引擎（高性能）
- 使用 **scroll-view** 替代页面滚动（避免卡顿）
- 使用 **worklet** 动画（在 UI 线程执行）
- 使用 **虚拟列表**（长列表优化）
- 使用 **图片懒加载**
- 使用 **代码分包**（减少首屏加载时间）

### 4. 调试技巧

```javascript
// 1. 在微信开发者工具中调试
// 点击"调试" → 打开调试器 → 查看 Console/Network/Storage

// 2. 在真机上调试
// 点击"真机调试" → 扫描二维码 → 在手机上打开调试器

// 3. 查看云函数日志
// 登录 CloudBase 控制台 → 云函数 → 日志
```

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/CloudBase开发.md` | 需要 CloudBase 全栈开发时 |
| `references/TDesign组件.md` | 需要使用 TDesign 组件时 |
| `references/微信框架.md` | 需要微信小程序框架开发时 |
| `references/Skyline引擎.md` | 需要 Skyline 渲染引擎时 |
| `references/项目结构.md` | 需要了解项目结构时 |
| `references/云开发.md` | 需要云开发时 |
| `references/UI设计.md` | 需要 UI 设计时 |
| `references/部署上线.md` | 需要部署上线时 |

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| TDesign 组件不显示 | 检查 `app.json` 是否删除了 `"style": "v2"` |
| TDesign 组件样式异常 | 检查是否构建了 npm（工具 → 构建 npm） |
| Skyline 页面不滚动 | 检查是否使用了 `<scroll-view>`（Skyline 页面默认不滚动） |
| 云函数调用失败 | 检查云函数日志（CloudBase 控制台 → 云函数 → 日志） |
| 云数据库权限错误 | 检查安全规则（CloudBase 控制台 → 数据库 → 权限设置） |
| 部署失败 | 检查网络连接，或尝试使用 CloudBase CLI 部署 |
