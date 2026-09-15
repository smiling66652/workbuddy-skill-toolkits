---
name: Skyline 渲染引擎指南
description: 微信小程序 Skyline 渲染引擎（组件、动画、路由、样式）
---

# Skyline 渲染引擎指南

## 启用 Skyline #

### app.json

```json
{
  "renderer": "skyline",
  "rendererOptions": {
    "skyline": {
      "defaultDisplayBlock": true,
      "defaultContentBox": true,
      "disableABTest": true
    }
  },
  "componentFramework": "glass-easel",
  "lazyCodeLoading": "requiredComponents"
}
```

### page.json

```json
{
  "navigationStyle": "custom",
  "disableScroll": true
}
```

---

## 页面结构 #

```html
<!-- pages/index/index.wxml -->
<scroll-view type="list" scroll-y style="height: 100vh;">
  <view class="container">
    <!-- 页面内容 -->
  </view>
</scroll-view>
```

> **注意**：Skyline 页面默认不滚动，必须使用 `<scroll-view>` 实现滚动内容。

---

## 组件 #

### scroll-view（滚动视图）

```html
<!-- 基础用法 -->
<scroll-view type="list" scroll-y style="height: 100vh;">
  <view wx:for="{{list}}" wx:key="id">{{item.title}}</view>
</scroll-view>

<!-- 增强模式（列表/嵌套滚动） -->
<scroll-view type="list" scroll-y enhanced show-scrollbar>
  <view wx:for="{{list}}" wx:key="id">{{item.title}}</view>
</scroll-view>

<!-- 嵌套滚动 -->
<scroll-view type="nested" scroll-y style="height: 50vh;">
  <scroll-view type="list" scroll-y style="height: 30vh;">
    <view wx:for="{{sublist}}" wx:key="id">{{item.title}}</view>
  </scroll-view>
</scroll-view>
```

### swiper（轮播）

```html
<swiper autoplay circular style="height: 300rpx;">
  <swiper-item wx:for="{{banners}}" wx:key="id">
    <image src="{{item.imageUrl}}" style="width: 100%; height: 100%;" />
  </swiper-item>
</swiper>
```

### draggable-sheet（半屏可拖拽组件）

```html
<draggable-sheet sheet-height="50%">
  <view slot="sheet-header">标题</view>
  <view slot="sheet-body">
    <!-- 内容 -->
  </view>
</draggable-sheet>
```

---

## Worklet 动画 #

### 共享变量（SharedValue）

```javascript
// pages/index/index.js
import { shared } from './worklet';

Page({
  data: {
    scrollTop: shared(0) // 共享变量（跨线程通信）
  },
  onLoad() {
    'worklet';
    const scrollTop = this.data.scrollTop;
    
    // 读取共享变量
    const currentTop = scrollTop.value;
    
    // 修改共享变量
    scrollTop.value = 100;
  }
})
```

### timing 动画（时间插值）

```javascript
// pages/index/index.js
import { shared, timing } from './worklet';

Page({
  onLoad() {
    'worklet';
    const offset = shared(0);
    
    // timing 动画（线性插值）
    const timingAnimation = timing(300, offset, {
      translateX: [0, 100], // 从 0 到 100
      opacity: [0, 1]         // 从透明到不透明
    });
  }
})
```

### spring 动画（弹簧物理）

```javascript
// pages/index/index.js
import { shared, spring } from './worklet';

Page({
  onLoad() {
    'worklet';
    const offset = shared(0);
    
    // spring 动画（弹簧效果）
    const springAnimation = spring(1000, offset, {
      damping: 10,      // 阻尼（值越小，弹簧效果越明显）
      stiffness: 100    // 刚度（值越大，回弹越快）
    });
  }
})
```

### decay 动画（衰减）

```javascript
// pages/index/index.js
import { shared, decay } from './worklet';

Page({
  onLoad() {
    'worklet';
    const velocity = shared(1000);
    
    // decay 动画（速度衰减）
    const decayAnimation = decay(1000, velocity, {
      deceleration: 0.997 // 衰减系数（值越大，衰减越慢）
    });
  }
})
```

### Easing 缓动函数 #

```javascript
// pages/index/index.js
import { Easing } from './worklet';

Page({
  onLoad() {
    'worklet';
    const offset = shared(0);
    
    // 使用缓动函数
    const easedAnimation = timing(300, offset, {
      translateX: [0, 100],
      easing: Easing.inOut(Easing.quad) // 二次缓动（先加速后减速）
    });
  }
})
```

---

## 自定义路由 #

### routeBuilder（路由构建器）

```javascript
// pages/index/index.js
import { routeBuilder } from './route';

Page({
  onLoad() {
    // 自定义路由动画
    routeBuilder('open', {
      enter: (stack, screen) => {
        // 进入动画
        screen.animate('timing', 300, {
          translateX: [100, 0]
        });
      },
      exit: (stack, screen) => {
        // 退出动画
        screen.animate('timing', 300, {
          translateX: [0, -100]
        });
      }
    });
  }
})
```

### 预设路由（7 种）

```javascript
// pages/index/index.js
Page({
  onLoad() {
    // 1. 缩放（zoom）
    wx.navigateTo({
      url: '/pages/detail/detail',
      routeType: 'zoom'
    });
    
    // 2. 右进左出（slide-right）
    wx.navigateTo({
      url: '/pages/detail/detail',
      routeType: 'slide-right'
    });
    
    // 3. 下进上出（slide-bottom）
    wx.navigateTo({
      url: '/pages/detail/detail',
      routeType: 'slide-bottom'
    });
    
    // 4. 淡入淡出（fade）
    wx.navigateTo({
      url: '/pages/detail/detail',
      routeType: 'fade'
    });
    
    // 5. 无动画（none）
    wx.navigateTo({
      url: '/pages/detail/detail',
      routeType: 'none'
    });
  }
})
```

---

## 滚动控制 API #

### ScrollViewContext #

```javascript
// pages/index/index.js
Page({
  onReady() {
    'worklet';
    const scrollViewContext = this.createSelectorQuery().select('#scroll-view').scrollViewContext;
    
    // 程序化下拉刷新
    scrollViewContext.triggerRefresh();
    
    // 程序化滚动到指定位置
    scrollViewContext.scrollTo({ x: 0, y: 100, animated: true });
  }
})
```

### DraggableSheetContext #

```javascript
// pages/index/index.js
Page({
  onReady() {
    'worklet';
    const draggableSheetContext = this.createSelectorQuery().select('#draggable-sheet').draggableSheetContext;
    
    // 程序化控制半屏面板位置
    draggableSheetContext.snapTo(50); // 滚动到 50% 位置
  }
})
```

---

## WXSS 样式支持 #

### 支持的 CSS 属性 #

| 属性 | 支持值 | 备注 |
|--------|----------|------|
| `display` | `block`, `flex`, `grid`, `none` | 不支持 `inline` |
| `position` | `static`, `relative`, `absolute`, `fixed`, `sticky` | 支持 `sticky` |
| `filter` | `blur()`, `brightness()`, `contrast()`, `grayscale()`, `hue-rotate()`, `invert()`, `opacity()`, `saturate()`, `sepia()` | 支持滤镜效果 |
| `gradient` | `linear-gradient()`, `radial-gradient()`, `conic-gradient()` | 支持渐变 |
| `overflow` | `visible`, `hidden`, `scroll`, `auto` | 支持溢出控制 |

### 不支持的 CSS 属性 #

| 属性 | 替代方案 |
|--------|------------|
| `float` | 使用 `flex` 布局 |
| `vertical-align` | 使用 `align-items` 或 `align-self` |
| `font-weight: bold` | 使用 `font-weight: 700` |
| `text-align: justify` | 不支持，需手动调整 |

---

## 故障排查 #

| 问题 | 解决方案 |
|------|-----------|
| 页面不滚动 | 检查是否使用了 `<scroll-view>`（Skyline 页面默认不滚动） |
| 动画不执行 | 检查是否在 `worklet` 中执行动画代码 |
| 共享变量不更新 | 检查是否使用 `shared()` 创建共享变量 |
| 路由动画不生效 | 检查是否配置了 `routeBuilder` 或 `routeType` |
| 样式不生效 | 检查是否使用了不支持的 CSS 属性（参考上方"不支持的 CSS 属性"表） |
