---
name: TDesign 组件使用指南
description: TDesign 微信小程序组件库使用指南（60+ 组件）
---

# TDesign 组件使用指南

## 快速开始 #

### 安装

```bash
npm i tdesign-miniprogram -S --production
```

### 修改 app.json

```json
{
  "style": "v2" // 删除这一行，避免样式冲突
}
```

### 修改 project.config.json

```json
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
```

### 构建 npm

在微信开发者工具中：工具 → 构建 npm

---

## 使用组件 #

### 引入组件

```json
// pages/index/index.json
{
  "usingComponents": {
    "t-button": "tdesign-miniprogram/button/button",
    "t-input": "tdesign-miniprogram/input/input"
  }
}
```

### 使用组件（WXML）

```html
<!-- pages/index/index.wxml -->
<t-button theme="primary">主要按钮</t-button>
<t-input label="用户名" placeholder="请输入用户名" />
```

---

## 常用组件 #

### 按钮（Button）

```html
<!-- 主要按钮 -->
<t-button theme="primary" size="large">主要按钮</t-button>

<!-- 浅色按钮 -->
<t-button theme="light" size="large">浅色按钮</t-button>

<!-- 轮廓按钮 -->
<t-button theme="primary" variant="outline" size="large">轮廓按钮</t-button>

<!-- 文字按钮 -->
<t-button theme="primary" variant="text" size="large">文字按钮</t-button>

<!-- 禁用状态 -->
<t-button theme="primary" size="large" disabled>禁用按钮</t-button>

<!-- 加载状态 -->
<t-button theme="primary" size="large" loading>加载中</t-button>

<!-- 块级按钮 -->
<t-button theme="primary" size="large" block>块级按钮</t-button>
```

### 输入框（Input）

```html
<!-- pages/index/index.wxml -->
<t-input
  label="用户名"
  placeholder="请输入用户名"
  value="{{value}}"
  bind:change="onChange"
/>
```

```javascript
// pages/index/index.js
Page({
  data: {
    value: ''
  },
  onChange(e) {
    this.setData({
      value: e.detail.value
    });
  }
})
```

### 对话框（Dialog）

```html
<!-- pages/index/index.wxml -->
<t-dialog
  visible="{{visible}}"
  title="提示"
  content="对话框内容"
  confirm-btn="确认"
  cancel-btn="取消"
  bind:confirm="onConfirm"
  bind:cancel="onCancel"
/>
```

```javascript
// pages/index/index.js
Page({
  data: {
    visible: false
  },
  showDialog() {
    this.setData({ visible: true });
  },
  onConfirm() {
    console.log('确认');
    this.setData({ visible: false });
  },
  onCancel() {
    console.log('取消');
    this.setData({ visible: false });
  }
})
```

### 消息提示（Toast）

```javascript
// pages/index/index.js
import Toast from 'tdesign-miniprogram/toast/index';

Page({
  showToast() {
    Toast({
      context: this,
      selector: '#t-toast',
      message: '消息提示'
    });
  }
})
```

```html
<!-- pages/index/index.wxml -->
<t-toast id="t-toast" />
```

---

## 主题定制 #

### 使用 CSS 变量

```css
/* app.wxss */
page {
  --td-button-primary-bg-color: #0052d9;
  --td-button-border-radius: 8rpx;
}
```

### 暗黑模式适配

```json
// app.json
{
  "darkmode": true
}
```

```css
/* app.wxss */
@import 'miniprogram_npm/tdesign-miniprogram/common/style/theme/_index.wxss';

.text {
  color: var(--td-text-color-secondary);
}
```

---

## AI 聊天界面 #

### 引入 Chat 组件

```json
// pages/chat/chat.json
{
  "usingComponents": {
    "t-chat-list": "tdesign-miniprogram/chat-list/chat-list",
    "t-chat-message": "tdesign-miniprogram/chat-message/chat-message",
    "t-chat-sender": "tdesign-miniprogram/chat-sender/chat-sender"
  }
}
```

### 使用 Chat 组件

```html
<!-- pages/chat/chat.wxml -->
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
```

```javascript
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
