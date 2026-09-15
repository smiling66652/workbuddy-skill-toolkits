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

| 用户需求 | 推荐工具（二级选择） | 说明 |
|-------------|------------|------|
| 新建小程序项目、搭建框架 | **微信小程序框架** | 官方框架，WXML/WXSS/WXS |
| 需要后端、数据库、部署 | **CloudBase** | 全栈开发，云函数/云数据库/静态托管 |
| 需要高质量 UI 组件 | **TDesign 组件库** | 60+ 企业级组件，支持暗黑模式 |
| 需要高性能渲染、复杂动画 | **Skyline 渲染引擎** | 独立渲染线程，支持 worklet 动画 |
| 需要 AI 聊天界面 | **TDesign Chat 组件** | 专为 AI 对话设计的组件 |
| 需要自定义路由转场动画 | **Skyline 自定义路由** | routeBuilder，7 种预设路由 |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|------------|------------|------------|
| 新建项目 | 新建小程序、搭建框架、初始化项目 | [二级：项目搭建](#二级项目搭建) |
| UI 设计 | 设计界面、用组件、定制主题、暗黑模式 | [二级：UI 设计](#二级ui-设计) |
| 云开发 | 云函数、云数据库、云存储、用户登录 | [二级：云开发](#二级云开发) |
| 性能优化 | 渲染性能、动画卡顿、滚动卡顿 | [二级：性能优化](#二级性能优化) |
| 部署上线 | 部署、发布、预览、真机调试 | [二级：部署上线](#二级部署上线) |

---

## 二级 + 三级：工具选择与执行

---

### 二级：项目搭建

**适用场景**：用户需要新建小程序项目、初始化框架、配置开发环境。

**三级执行**：

#### 方法1：使用微信开发者工具（官方）

```bash
# 1. 下载并安装微信开发者工具
# https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

# 2. 新建项目
# 打开微信开发者工具 → 新建项目 → 填写 AppID → 选择项目目录

# 3. 项目结构
# ├── app.js          # 小程序逻辑
# ├── app.json        # 小程序配置
# ├── app.wxss        # 全局样式
# ├── pages/           # 页面目录
# │   └── index/
# │       ├── index.js    # 页面逻辑
# │       ├── index.json  # 页面配置
# │       ├── index.wxml  # 页面模板
# │       └── index.wxss  # 页面样式
# └── components/     # 自定义组件目录
```

#### 方法2：使用 CloudBase 创建项目（推荐，带后端）

```bash
# 1. 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 2. 登录 CloudBase
tcb login

# 3. 创建小程序项目（自动集成 CloudBase SDK）
tcb init
# 选择：小程序项目 + 云开发环境

# 4. 开发
# 使用微信开发者工具打开项目目录
```

#### 方法3：使用 TDesign 快速启动（推荐，带 UI 组件库）

```bash
# 1. 新建小程序项目（使用微信开发者工具）

# 2. 安装 TDesign
cd your-miniprogram-project
npm i tdesign-miniprogram -S --production

# 3. 修改 app.json
# 删除 "style": "v2"（避免样式冲突）

# 4. 修改 project.config.json
{
  "setting": {
    "packNpmManually": true,
    "packNpmRelationList": [
      {
        "packageJsonPath": "./package.json",
        "miniprogramNpmDistDir": "./"
      }
    ]
  }
}

# 5. 构建 npm
# 在微信开发者工具中：工具 → 构建 npm

# 6. 使用组件
# 在页面 JSON 中引入：
{
  "usingComponents": {
    "t-button": "tdesign-miniprogram/button/button"
  }
}
```

**工具对比**：

| 工具 | 速度 | 功能完整性 | 适用场景 |
|------|------|------------|------------|
| 微信开发者工具 | 快 | 基础 | 纯前端小程序 |
| CloudBase CLI | 中 | **全栈** | 需要后端/数据库/部署 |
| TDesign 快速启动 | 快 | **UI 丰富** | 需要高质量组件库 |

---

### 二级：UI 设计

**适用场景**：用户需要设计界面、使用组件、定制主题、适配暗黑模式。

**三级执行**：

#### 方法1：使用 TDesign 组件库（推荐）

```javascript
// 1. 安装（见上方"方法3"）

// 2. 使用组件（WXML）
// pages/index/index.wxml
<view class="container">
  <t-button theme="primary" size="large">主要按钮</t-button>
  <t-input label="用户名" placeholder="请输入用户名" />
  <t-dialog visible="{{visible}}" title="提示" content="对话框内容" />
</view>

// 3. 定制主题（CSS 变量）
/* app.wxss */
page {
  --td-button-primary-bg-color: #0052d9;
  --td-button-border-radius: 8rpx;
}

// 4. 暗黑模式适配
// app.json
{
  "darkmode": true
}

// app.wxss
@import 'miniprogram_npm/tdesign-miniprogram/common/style/theme/_index.wxss';

// 使用 CSS 变量（自动适配暗黑模式）
.text {
  color: var(--td-text-color-secondary);
}
```

#### 方法2：使用 Skyline 高性能渲染（推荐，复杂界面）

```javascript
// 1. 启用 Skyline（app.json）
{
  "renderer": "skyline",
  "rendererOptions": {
    "skyline": {
      "defaultDisplayBlock": true,
      "defaultContentBox": true
    }
  },
  "componentFramework": "glass-easel"
}

// 2. 使用 scroll-view 实现高性能滚动
// pages/index/index.wxml
<scroll-view type="list" scroll-y style="height: 100vh;">
  <view wx:for="{{list}}" wx:key="id" class="item">
    {{item.title}}
  </view>
</scroll-view>

// 3. 使用 worklet 动画（高性能）
// pages/index/index.js
import { shared, timing } from './worklet';

Page({
  data: {
    scrollTop: shared(0)
  },
  onLoad() {
    // worklet 动画（在 UI 线程执行，不卡顿）
    this.animateButton = timing(300, shared(1), {
      opacity: [0, 1],
      translateY: [100, 0]
    });
  },
  onScroll(e) {
    'worklet';
    const scrollTop = e.detail.scrollTop;
    this.setData({ scrollTop });
  }
})
```

#### 方法3：使用 TDesign Chat 组件（AI 聊天界面）

```javascript
// 1. 引入 Chat 组件
// pages/chat/chat.json
{
  "usingComponents": {
    "t-chat-list": "tdesign-miniprogram/chat-list/chat-list",
    "t-chat-message": "tdesign-miniprogram/chat-message/chat-message",
    "t-chat-sender": "tdesign-miniprogram/chat-sender/chat-sender"
  }
}

// 2. 使用（WXML）
// pages/chat/chat.wxml
<t-chat-list layout="single">
  <t-chat-message
    wx:for="{{messages}}"
    wx:key="id"
    avatar="{{item.avatar}}"
    name="{{item.name}}"
    content="{{item.content}}"
    role="{{item.role}}"
  />
  <view slot="footer">
    <t-chat-sender bind:send="onSend" />
  </view>
</t-chat-list>

// 3. 处理逻辑（JS）
// pages/chat/chat.js
Component({
  data: {
    messages: [
      {
        id: 1,
        role: 'assistant',
        content: [{ type: 'text', data: '你好！我是 AI 助手。' }],
        name: 'AI 助手',
        avatar: 'https://example.com/avatar.png'
      }
    ]
  },
  methods: {
    onSend(e) {
      const { value } = e.detail;
      // 发送消息逻辑
      this.setData({
        messages: [...this.data.messages, {
          id: Date.now(),
          role: 'user',
          content: [{ type: 'text', data: value }],
          name: '用户',
          avatar: ''
        }]
      });
    }
  }
})
```

**工具对比**：

| 工具 | 组件丰富度 | 性能 | 适用场景 |
|------|------------|------|------------|
| TDesign | **60+ 组件** | 中 | 企业级应用、快速开发 |
| Skyline | 基础组件 | **极高** | 复杂动画、长列表滚动 |
| TDesign Chat | AI 聊天专用 | 中 | AI 对话应用 |

---

### 二级：云开发

**适用场景**：用户需要云函数、云数据库、云存储、用户登录。

**三级执行**：

#### 方法1：使用 CloudBase 云开发（推荐）

```javascript
// 1. 初始化 CloudBase（app.js）
// app.js
App({
  onLaunch() {
    // 初始化 CloudBase
    wx.cloud.init({
      env: 'your-env-id' // 云开发环境 ID
    });
  }
})

// 2. 调用云函数
// pages/index/index.js
wx.cloud.callFunction({
  name: 'addTodo', // 云函数名称
  data: {
    title: '学习微信小程序',
    done: false
  },
  success: (res) => {
    console.log(res.result);
  },
  fail: (err) => {
    console.error(err);
  }
})

// 3. 操作云数据库
// pages/index/index.js
const db = wx.cloud.database();

// 插入数据
db.collection('todos').add({
  data: {
    title: '学习微信小程序',
    done: false
  },
  success: (res) => {
    console.log(res._id);
  }
})

// 查询数据
db.collection('todos').where({
  done: false
}).get({
  success: (res) => {
    console.log(res.data);
  }
})

// 4. 上传文件到云存储
wx.cloud.uploadFile({
  cloudPath: 'example.png', // 云存储路径
  filePath: '/local/path/example.png', // 本地文件路径
  success: (res) => {
    console.log(res.fileID); // 云文件 ID
  }
})

// 5. 用户登录（天然免登录，获取 OPENID）
// cloudfunctions/addTodo/index.js
const cloud = require('wx-server-sdk');
cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
});

exports.main = async (event, context) => {
  const { OPENID, APPID } = cloud.getWXContext(); // 获取 OPENID
  const db = cloud.database();
  
  await db.collection('todos').add({
    data: {
      ...event,
      _openid: OPENID,
      createTime: db.serverDate()
    }
  });
  
  return { success: true };
}
```

#### 方法2：使用微信云开发（官方）

```javascript
// 1. 初始化云开发（app.js）
// app.js
App({
  onLaunch() {
    wx.cloud.init({
      env: 'your-env-id'
    });
  }
})

// 2. 使用云函数（同上）

// 3. 使用云数据库（同上）

// 4. 使用云存储（同上）

// 5. 用户登录（同上）
```

**工具对比**：

| 工具 | 功能丰富度 | 部署便利性 | 适用场景 |
|------|------------|------------|------------|
| CloudBase | **全栈**（云函数/云数据库/静态托管/AI） | **一键部署** | 全栈应用、需要后端 |
| 微信云开发 | 基础（云函数/云数据库/云存储） | 需手动部署 | 纯小程序后端 |

---

### 二级：性能优化

**适用场景**：用户需要优化渲染性能、动画性能、滚动性能。

**三级执行**：

#### 方法1：使用 Skyline 渲染引擎（推荐）

```javascript
// 1. 启用 Skyline（见上方"二级：UI 设计 → 方法2"）

// 2. 使用 scroll-view 替代页面滚动（避免卡顿）
// pages/index/index.wxml
<scroll-view type="list" scroll-y style="height: 100vh;">
  <!-- 长列表内容 -->
</scroll-view>

// 3. 使用 worklet 动画（在 UI 线程执行，不卡顿）
// pages/index/index.js
import { shared, timing, spring } from './worklet';

Page({
  onLoad() {
    // 共享变量（跨线程通信）
    const offset = shared(0);
    
    // timing 动画（时间插值）
    const timingAnimation = timing(300, offset, {
      translateX: [0, 100],
      opacity: [0, 1]
    });
    
    // spring 动画（弹簧物理）
    const springAnimation = spring(1000, offset, {
      damping: 10,
      stiffness: 100
    });
  }
})

// 4. 使用 DraggableSheet（半屏可拖拽组件）
// pages/index/index.wxml
<draggable-sheet sheet-height="50%">
  <view slot="sheet-header">标题</view>
  <view slot="sheet-body">
    <!-- 内容 -->
  </view>
</draggable-sheet>
```

#### 方法2：使用微信性能优化技巧（官方）

```javascript
// 1. 使用虚拟列表（长列表优化）
// pages/index/index.wxml
<recycle-view batch="{{batchSetRecycleData}}" id="recycleId">
  <recycle-item wx:for="{{recycleList}}" wx:key="id">
    <view>{{item.title}}</view>
  </recycle-item>
</recycle-view>

// 2. 使用图片懒加载
// pages/index/index.wxml
<image lazy-load src="{{imageUrl}}" />

// 3. 使用代码分包（减少首屏加载时间）
// app.json
{
  "subpackages": [
    {
      "root": "packageA",
      "pages": [
        "pages/cat",
        "pages/dog"
      ]
    }
  ]
}

// 4. 使用预加载（提前加载分包）
// pages/index/index.js
wx.preloadSubpackage({
  name: 'packageA',
  success: (res) => {
    console.log('预加载成功');
  }
})
```

**工具对比**：

| 工具 | 性能提升 | 适用场景 |
|------|------------|------------|
| Skyline | **极高**（独立渲染线程） | 复杂动画、长列表滚动 |
| 微信性能优化 | 中（代码分包/懒加载） | 首屏加载优化 |

---

### 二级：部署上线

**适用场景**：用户需要部署小程序、发布版本、预览效果、真机调试。

**三级执行**：

#### 方法1：使用微信开发者工具部署（官方）

```bash
# 1. 预览
# 在微信开发者工具中：点击"预览" → 扫描二维码 → 在手机上预览

# 2. 真机调试
# 在微信开发者工具中：点击"真机调试" → 扫描二维码 → 在手机上调试

# 3. 上传代码
# 在微信开发者工具中：点击"上传" → 填写版本号和项目备注 → 上传代码

# 4. 提交审核
# 登录微信公众平台 → 开发管理 → 开发版本 → 提交审核

# 5. 发布
# 审核通过后 → 开发管理 → 审核版本 → 发布
```

#### 方法2：使用 CloudBase 部署（推荐，全栈应用）

```bash
# 1. 部署云函数
# 在微信开发者工具中：右键 cloudfunctions/函数名 → 上传并部署

# 2. 部署静态网站（如果有 Web 端）
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署静态网站
tcb hosting deploy ./dist -e your-env-id

# 3. 绑定自定义域名（可选）
# 登录 CloudBase 控制台 → 静态网站托管 → 设置自定义域名
```

**工具对比**：

| 工具 | 便利性 | 适用场景 |
|------|------------|------------|
| 微信开发者工具 | 中（需手动操作） | 纯小程序部署 |
| CloudBase | **高**（CLI 一键部署） | 全栈应用部署 |

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
