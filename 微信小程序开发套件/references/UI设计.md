---
name: UI 设计指南
description: 微信小程序 UI 设计（色彩、字体、间距、图标）
---

# 微信小程序 UI 设计指南

## 设计原则 #

1. **一致性** - 保持整体风格一致
2. **简洁性** - 避免信息过载
3. **可用性** - 操作直观易懂
4. **反馈性** - 操作后有明确反馈

---

## 色彩规范 #

### 主色调 #

```css
/* app.wxss */
page {
  --primary-color: #07c160; /* 微信绿 */
  --secondary-color: #576b95; /* 辅助色 */
  --success-color: #07c160; /* 成功色 */
  --warning-color: #fba82e; /* 警告色 */
  --danger-color: #f44; /* 危险色 */
}
```

### 文字颜色 #

```css
/* app.wxss */
page {
  --text-primary: #000000; /* 主要文字 */
  --text-secondary: #888888; /* 次要文字 */
  --text-hint: #b2b2b2; /* 提示文字 */
  --text-disabled: #d0d0d0; /* 禁用文字 */
}
```

### 背景颜色 #

```css
/* app.wxss */
page {
  --bg-page: #efefef; /* 页面背景 */
  --bg-card: #ffffff; /* 卡片背景 */
  --bg-mask: rgba(0, 0, 0, 0.5); /* 遮罩背景 */
}
```

---

## 字体规范 #

### 字体大小 #

```css
/* app.wxss */
page {
  --font-xs: 20rpx; /* 极小 */
  --font-sm: 24rpx; /* 小 */
  --font-base: 28rpx; /* 基础 */
  --font-lg: 32rpx; /* 大 */
  --font-xl: 36rpx; /* 极大 */
  --font-xxl: 40rpx; /* 超大 */
}
```

### 字体粗细 #

```css
/* app.wxss */
page {
  --font-normal: 400; /* 常规 */
  --font-medium: 500; /* 中等 */
  --font-bold: 700; /* 加粗 */
}
```

### 行高 #

```css
/* app.wxss */
page {
  --line-height-tight: 1.2; /* 紧凑 */
  --line-height-normal: 1.5; /* 正常 */
  --line-height-loose: 1.8; /* 宽松 */
}
```

---

## 间距规范 #

### 内边距 #

```css
/* app.wxss */
page {
  --spacing-xs: 8rpx; /* 极小 */
  --spacing-sm: 16rpx; /* 小 */
  --spacing-base: 24rpx; /* 基础 */
  --spacing-lg: 32rpx; /* 大 */
  --spacing-xl: 48rpx; /* 极大 */
}
```

### 外边距 #

```css
/* app.wxss */
page {
  --margin-xs: 8rpx;
  --margin-sm: 16rpx;
  --margin-base: 24rpx;
  --margin-lg: 32rpx;
  --margin-xl: 48rpx;
}
```

### 圆角 #

```css
/* app.wxss */
page {
  --radius-sm: 4rpx; /* 小圆角 */
  --radius-base: 8rpx; /* 基础圆角 */
  --radius-lg: 16rpx; /* 大圆角 */
  --radius-full: 50%; /* 圆形 */
}
```

---

## 图标使用 #

### 使用 Icon 组件（TDesign）#

```json
/* pages/index/index.json */
{
  "usingComponents": {
    "t-icon": "tdesign-miniprogram/icon/icon"
  }
}
```

```html
<!--pages/index/index.wxml-->
<t-icon name="logo-github" size="48rpx" color="#07c160" />
```

### 使用图片图标 #

```html
<!--pages/index/index.wxml-->
<image src="/images/icon.png" style="width: 48rpx; height: 48rpx;" />
```

---

## 布局规范 #

### Flex 布局 #

```css
/* pages/index/index.wxss */
.container {
  display: flex;
  flex-direction: column; /* 纵向排列 */
  align-items: center; /* 水平居中 */
  justify-content: center; /* 垂直居中 */
  padding: var(--spacing-base);
}
```

### Grid 布局 #

```css
/* pages/index/index.wxss */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 两列 */
  gap: var(--spacing-base);
  padding: var(--spacing-base);
}
```

---

## 组件设计 #

### 卡片设计 #

```css
/* pages/index/index.wxss */
.card {
  background-color: var(--bg-card);
  border-radius: var(--radius-base);
  padding: var(--spacing-base);
  margin-bottom: var(--margin-base);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}
```

### 列表设计 #

```html
<!--pages/index/index.wxml-->
<view class="list-item" wx:for="{{list}}" wx:key="id">
  <image src="{{item.avatar}}" class="avatar" />
  <view class="info">
    <text class="name">{{item.name}}</text>
    <text class="desc">{{item.desc}}</text>
  </view>
</view>
```

```css
/* pages/index/index.wxss */
.list-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-base);
  border-bottom: 1rpx solid #eee;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: var(--radius-full);
  margin-right: var(--spacing-base);
}

.info {
  flex: 1;
}

.name {
  font-size: var(--font-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.desc {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}
```

---

## 动效设计 #

### 使用 CSS 动画 #

```css
/* pages/index/index.wxss */
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### 使用 worklet 动画（Skyline）#

```javascript
// pages/index/index.js
import { shared, timing } from './worklet';

Page({
  onLoad() {
    'worklet';
    const opacity = shared(0);
    this.setData({ opacity });
    
    // timing 动画
    timing(300, opacity, {
      opacity: [0, 1]
    });
  }
})
```

---

## 暗黑模式适配 #

### 启用暗黑模式 #

```json
/* app.json */
{
  "darkmode": true
}
```

### 使用 CSS 变量 #

```css
/* app.wxss */
page {
  /* 浅色模式 */
  --bg-color: #ffffff;
  --text-color: #000000;
}

@media (prefers-color-scheme: dark) {
  page {
    /* 暗黑模式 */
    --bg-color: #1a1a1a;
    --text-color: #ffffff;
  }
}

.container {
  background-color: var(--bg-color);
  color: var(--text-color);
}
```

---

## 故障排查 #

| 问题 | 解决方案 |
|------|-----------|
| 样式不生效 | 检查是否使用了正确的 CSS 变量 |
| 暗黑模式不生效 | 检查是否启用了 `darkmode` |
| 动画卡顿 | 使用 Skyline 渲染引擎 + worklet 动画 |
| 图标不显示 | 检查是否引入了 `t-icon` 组件 |
