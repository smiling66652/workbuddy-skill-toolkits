# Design System Reference

网站设计系统参考指南，覆盖色彩、排版、间距、布局、动效等核心设计维度。

---

## 1. 色彩系统 Color System

### 1.1 配色方法论

采用 **60-30-10 法则**：
- **60%** 主色（背景/大面积区域）
- **30%** 辅助色（卡片/区块背景）
- **10%** 强调色（按钮/链接/CTA）

### 1.2 常用配色方案

| 方案 | 主色 | 强调色 | 适用场景 |
|------|------|--------|----------|
| 科技蓝 | `#1a56db` / `#2563eb` | `#f59e0b` | SaaS、科技公司 |
| 商务深蓝 | `#1e3a5f` / `#0f172a` | `#3b82f6` | 金融、企业 |
| 清新绿 | `#059669` / `#10b981` | `#f97316` | 环保、健康 |
| 温暖橙 | `#ea580c` / `#f97316` | `#06b6d4` | 电商、消费 |
| 优雅紫 | `#7c3aed` / `#8b5cf6` | `#ec4899` | 创意、美妆 |
| 极简黑白 | `#111827` / `#f9fafb` | `#2563eb` | 作品集、文档 |

### 1.3 CSS 变量模板

```css
:root {
  /* 主色系 */
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;
  /* 强调色 */
  --color-accent: #f59e0b;
  /* 中性色 */
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;
  --color-text: #0f172a;
  --color-text-secondary: #475569;
  --color-text-muted: #94a3b8;
  --color-border: #e2e8f0;
  /* 功能色 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

### 1.4 对比度要求

- 正文文字与背景对比度 ≥ 4.5:1（WCAG AA）
- 大号文字（≥18px bold 或 ≥24px）≥ 3:1
- 纯黑 `#000` 文字在纯白背景上对比度约 21:1，视觉冲击过强，建议用 `#0f172a` 等深灰色

---

## 2. 排版系统 Typography

### 2.1 字号层级（Type Scale）

使用 **1.25 比例**（Major Third）：

| 层级 | 字号 | 用途 |
|------|------|------|
| `--text-xs` | 12px / 0.75rem | 标签、辅助信息 |
| `--text-sm` | 14px / 0.875rem | 次要文字、说明 |
| `--text-base` | 16px / 1rem | 正文 |
| `--text-lg` | 18px / 1.125rem | 强调正文 |
| `--text-xl` | 20px / 1.25rem | 小标题 |
| `--text-2xl` | 24px / 1.5rem | 二级标题 |
| `--text-3xl` | 30px / 1.875rem | 一级标题 |
| `--text-4xl` | 36px / 2.25rem | 页面大标题 |
| `--text-5xl` | 48px / 3rem | Hero 主标题 |
| `--text-6xl` | 60px / 3.75rem | 超大标题 |

### 2.2 中文字体栈

```css
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
  "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue",
  Arial, sans-serif;
```

### 2.3 行高与字间距

- **正文行高**：1.6 - 1.8（中文正文建议 1.8）
- **标题行高**：1.2 - 1.4
- **英文字间距**：`letter-spacing: -0.01em`（大标题可收紧）
- **中文字间距**：默认即可，不建议额外调整

### 2.4 排版 CSS 变量模板

```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono",
    "Courier New", monospace;

  --text-xs: 0.75rem;    --leading-xs: 1rem;
  --text-sm: 0.875rem;   --leading-sm: 1.25rem;
  --text-base: 1rem;     --leading-base: 1.75rem;
  --text-lg: 1.125rem;   --leading-lg: 1.75rem;
  --text-xl: 1.25rem;    --leading-xl: 1.75rem;
  --text-2xl: 1.5rem;    --leading-2xl: 2rem;
  --text-3xl: 1.875rem;  --leading-3xl: 2.25rem;
  --text-4xl: 2.25rem;   --leading-4xl: 2.5rem;
  --text-5xl: 3rem;      --leading-5xl: 1.1;
  --text-6xl: 3.75rem;   --leading-6xl: 1.1;
}
```

---

## 3. 间距系统 Spacing

### 3.1 基于 4px 网格

使用 4px 为基准单位的间距系统：

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
  --space-32: 8rem;     /* 128px */
}
```

### 3.2 常用间距模式

- **Section 上下间距**：`--space-20`（80px）到 `--space-32`（128px）
- **卡片内边距**：`--space-6`（24px）到 `--space-8`（32px）
- **按钮内边距**：垂直 `--space-3`（12px），水平 `--space-6`（24px）
- **元素间距**：`--space-4`（16px）为默认值
- **内容最大宽度**：`max-width: 1200px` 或 `1280px`，左右自动居中

---

## 4. 布局模式 Layout

### 4.1 容器模式

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

.container-narrow {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}
```

### 4.2 常用 Flexbox 模式

```css
/* 水平居中 */
.flex-center { display: flex; justify-content: center; align-items: center; }

/* 两端对齐 */
.flex-between { display: flex; justify-content: space-between; align-items: center; }

/* 垂直排列 */
.flex-col { display: flex; flex-direction: column; }

/* 自适应换行网格 */
.flex-wrap { display: flex; flex-wrap: wrap; gap: var(--space-6); }
```

### 4.3 常用 Grid 模式

```css
/* 2 列 */
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-8); }

/* 3 列 */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-8); }

/* 4 列 */
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-6); }

/* 自适应卡片网格（推荐）*/
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-8);
}
```

### 4.4 响应式断点

```css
/* 移动优先，向上扩展 */
/* 平板 */
@media (min-width: 768px) { ... }
/* 小桌面 */
@media (min-width: 1024px) { ... }
/* 大桌面 */
@media (min-width: 1280px) { ... }
```

---

## 5. 视觉层级 Visual Hierarchy

### 5.1 建立层级的四个手段

1. **大小** — 越大越重要。标题 >> 正文 >> 辅助文字
2. **颜色** — 深色重于浅色。正文用深色，辅助信息用灰色
3. **粗细** — Bold > Medium > Regular。标题加粗，正文常规
4. **留白** — 重要元素周围留更多空间

### 5.2 页面内容流（F 型 / Z 型）

- **文字密集型页面**（文章、文档）— 用户扫描模式为 F 型，重要内容放在左上和左侧
- **视觉密集型页面**（落地页、产品页）— 用户扫描模式为 Z 型，从左上到右上，再对角线到左下到右下

### 5.3 视觉焦点引导

```css
/* 使用渐变引导视线 */
.hero { background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); }

/* 使用阴影突出卡片 */
.card { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1); }
.card:hover { box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1); transform: translateY(-4px); }
```

---

## 6. 圆角与阴影

### 6.1 圆角系统

```css
:root {
  --radius-sm: 0.25rem;   /* 4px — 小标签 */
  --radius-md: 0.5rem;    /* 8px — 按钮、输入框 */
  --radius-lg: 0.75rem;   /* 12px — 卡片 */
  --radius-xl: 1rem;      /* 16px — 大卡片、Modal */
  --radius-2xl: 1.5rem;   /* 24px — 大容器 */
  --radius-full: 9999px;  /* 胶囊按钮 */
}
```

### 6.2 阴影层级

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
}
```

---

## 7. 动效与过渡

### 7.1 过渡时长

```css
:root {
  --duration-fast: 150ms;    /* 微交互 */
  --duration-normal: 300ms;  /* 常规过渡 */
  --duration-slow: 500ms;    /* 页面切换 */
}
```

### 7.2 缓动函数

```css
:root {
  --ease-out: cubic-bezier(0, 0, 0.2, 1);       /* 减速 */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);  /* 标准 */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* 弹性 */
}
```

### 7.3 常用动效模式

```css
/* 悬停上浮 */
.card { transition: transform var(--duration-normal) var(--ease-out), box-shadow var(--duration-normal) var(--ease-out); }
.card:hover { transform: translateY(-4px); box-shadow: var(--shadow-xl); }

/* 渐入显示 */
.fade-in { animation: fadeIn var(--duration-slow) var(--ease-out); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* 按钮悬停 */
.btn { transition: all var(--duration-fast) var(--ease-out); }
.btn:hover { filter: brightness(1.1); transform: scale(1.02); }
```

---

## 8. 组件设计规范

### 8.1 按钮

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  font-weight: 600; font-size: var(--text-base);
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer; border: none;
  text-decoration: none;
  gap: 0.5rem;
}
.btn-primary { background: var(--color-primary); color: #fff; }
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-outline { background: transparent; border: 2px solid var(--color-primary); color: var(--color-primary); }
.btn-outline:hover { background: var(--color-primary); color: #fff; }
.btn-lg { padding: 1rem 2rem; font-size: var(--text-lg); }
```

### 8.2 卡片

```css
.card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: all var(--duration-normal) var(--ease-out);
}
.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}
```

### 8.3 输入框

```css
.input {
  width: 100%; padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: border-color var(--duration-fast);
  outline: none;
}
.input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
```

---

## 9. 中文页面特别注意事项

- **行高**：中文正文行高建议 1.7-1.8，标题 1.3-1.5
- **段落间距**：比英文页面适当加大，建议 1.5em-2em
- **最小字号**：中文正文字号不低于 14px，推荐 16px
- **数字处理**：大数字使用千分位分隔符（1,234,567）
- **标点避头尾**：HTML 中不需特殊处理，浏览器会自动处理
- **图片 alt 文本**：必须用中文撰写
- **英文字体回退**：西文部分自动使用系统默认西文字体，无需手动指定
