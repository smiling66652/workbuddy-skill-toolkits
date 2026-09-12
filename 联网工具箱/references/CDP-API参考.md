---
name: CDP Proxy API 完整参考
---

# CDP Proxy API 完整参考

**何时读**：需要精确的端点语义、参数位置、返回值形态，或调用失败要查错误码时。
日常操作只需 [CDP浏览器直连](CDP浏览器直连.md) 里的那几条常用命令。

---

## 基础信息

| 项 | 值 |
|---|---|
| 地址 | `http://localhost:3456`（仅监听 127.0.0.1，不对外） |
| 启动 | `node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/check-deps.mjs"`（会自动拉起 Proxy 并等待就绪） |
| 手工启动 | `node ".../scripts/cdp-proxy.mjs"`（一般不必要） |
| 强制停止 | `pkill -f cdp-proxy.mjs` |
| 生命周期 | 启动后长驻，**不建议主动停**——重启后需要在浏览器里重新授权 CDP |
| 环境变量 | `CDP_PROXY_PORT`（默认 3456）、`CDP_TAB_IDLE_TIMEOUT`（默认 900000ms = 15min） |

---

## 端点总览

| 方法 | 端点 | 载荷位置 | 说明 |
|---|---|---|---|
| GET | `/health` | — | 健康检查，返回连接状态 |
| GET | `/targets` | — | 列出已打开的 tab，每项含 `targetId` / `title` / `url` |
| POST | `/new` | **body = 目标 URL** | 新建后台 tab。返回 `{ targetId }` |
| GET | `/close?target=ID` | query | 关闭指定 tab |
| POST | `/navigate?target=ID` | **body = 目标 URL** | 在已有 tab 内导航 |
| GET | `/back?target=ID` | query | 后退一页 |
| GET | `/info?target=ID` | query | 页面基础信息（`title` / `url` / `readyState`） |
| POST | `/eval?target=ID` | **body = JS 表达式** | 执行任意 JS，返回 `{ value }` 或 `{ error }` |
| POST | `/click?target=ID` | **body = CSS 选择器** | JS 层 `el.click()`，自动 `scrollIntoView` |
| POST | `/clickAt?target=ID` | **body = CSS 选择器** | CDP 真实鼠标点击（见下方差异说明） |
| POST | `/setFiles?target=ID` | **body = JSON** | 给 file input 设置本地路径，绕过文件对话框 |
| GET | `/scroll?target=ID&y=3000&direction=down` | query | 滚动。`direction` ∈ `down`(默认) / `up` / `top` / `bottom`；滚动后自动等 800ms 供懒加载 |
| GET | `/screenshot?target=ID&file=/tmp/shot.png` | query | 截图。给 `file` 存盘，不给则返回图片二进制；可加 `format=jpeg` |

**一句话记忆**：**凡是传输「任意字符串载荷」的写操作，一律走 POST body**；只有不透明 ID（`target`）和数值/枚举（`y`、`direction`、`file`）走 query。

### 常用示例

```bash
# 健康检查
curl -s http://localhost:3456/health

# 列出已打开的 tab
curl -s http://localhost:3456/targets

# 新建后台 tab（URL 走 POST body，无需 URL-encode）
curl -s -X POST --data-raw 'https://example.com' http://localhost:3456/new

# 含 query 的目标 URL —— 原样传，不要编码、不要裁参数
curl -s -X POST --data-raw 'https://www.xiaohongshu.com/explore/xxx?xsec_source=app_share&xsec_token=ABC&type=normal' \
  http://localhost:3456/new

# 导航 / 后退 / 页面信息
curl -s -X POST --data-raw 'https://example.com' "http://localhost:3456/navigate?target=ID"
curl -s "http://localhost:3456/back?target=ID"
curl -s "http://localhost:3456/info?target=ID"

# 执行 JS
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'

# 截图（含视频当前帧）
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"

# 文件上传（多文件）
curl -s -X POST "http://localhost:3456/setFiles?target=ID" \
  -d '{"selector":"input[type=file]","files":["D:/a.png","D:/b.png"]}'

# 滚动触发懒加载 / 关闭 tab
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"
curl -s "http://localhost:3456/close?target=ID"
```

---

## 为什么要走 POST body（v2.5.3 的结构性原因）

旧写法 `GET /new?url=<目标URL>` 在目标 URL 自带 query 时会**静默截断**：

```
GET /new?url=https://xhs.com/explore/x?a=1&b=2
→ proxy 解析结果：
   q.url = "https://xhs.com/explore/x?a=1"   ← 被截断
   q.b   = "2"                                ← 被当成 proxy 自己的参数吃掉
```

根因是**用一种带语法的格式（query string）去承载另一种也带该语法的数据（URL）**，存在结构性歧义。靠调用方守纪律做 URL-encode 治标不治本——偶尔忘记就翻车。

改用 POST body 后：HTTP body 是不透明字节流，边界由 `Content-Length` 显式声明，与数据本身解耦，**零编码负担、零歧义**。

### 迁移对照

| 场景 | ❌ 旧（v2.5.2） | ✅ 新 |
|---|---|---|
| 简单 URL | `curl ".../new?url=https://example.com"` | `curl -X POST --data-raw 'https://example.com' .../new` |
| URL 含 query | `.../new?url=https://x.com/a?t=ABC`（token 丢失） | `curl -X POST --data-raw 'https://x.com/a?t=ABC' .../new` |
| URL 含 `#` | `.../new?url=https://a/p#sec`（fragment 丢失） | `curl -X POST --data-raw 'https://a/p#sec' .../new` |
| navigate | `.../navigate?target=ID&url=URL` | `curl -X POST --data-raw 'URL' ".../navigate?target=ID"` |

**自检 checklist**（遇到任何来源的旧写法）：
1. 搜字符串 `localhost:3456/new?url=` 或 `.../navigate?` 后跟 `&url=` → 属旧写法
2. 按上表改写成 POST 形式
3. 若旧写法来自 `references/site-patterns/*.md`，**把源文件也一并改掉**，否则下次复用同一经验还会踩
4. URL 里的 `?`、`&`、`=`、`#`、`%` 一律**不转义**，从 DOM/分享链接抓到什么样就传什么样

> `GET ?url=` 收到的是 **HTTP 400 + 迁移指引**，不会静默失败——这是个明确信号，看到就改写法。

---

## `/eval` 使用提示

- POST body 是**任意 JS 表达式**，支持 `await`（内部按 `awaitPromise` 处理），返回 `{ value }` 或 `{ error }`
- **返回值必须可序列化**：DOM 节点不能直接返回，要提取属性（如 `el.innerText`、`el.getAttribute('href')`）
- 提取批量数据用 `JSON.stringify()` 包裹，确保拿到字符串
- 穿透 Shadow DOM / iframe：用递归遍历（`shadowRoot`、`contentDocument`），选择器跨不过这些边界
- **按页面真实 DOM 写选择器**，不要套用固定模板

```bash
# 批量提取
curl -s -X POST "http://localhost:3456/eval?target=ID" \
  -d 'JSON.stringify([...document.querySelectorAll(".item")].map(e => ({ t: e.innerText, h: e.querySelector("a")?.href })))'

# 操控 video（配合 /screenshot 采帧）
curl -s -X POST "http://localhost:3456/eval?target=ID" \
  -d 'document.querySelector("video").duration'
```

---

## `/click` 与 `/clickAt` 的差异（选错会卡住）

| | `/click` | `/clickAt` |
|---|---|---|
| 实现 | JS `el.click()` | CDP `Input.dispatchMouseEvent` |
| 是否用户手势 | ❌ 否（`isTrusted === false`） | ✅ 是 |
| 速度 | 快 | 稍慢（先取坐标再按下/释放） |
| 能触发文件对话框 | ❌ 不能 | ✅ 能 |
| 能过部分反自动化检测 | 弱 | 较强 |
| 适用 | 展开、翻页、进详情——**绝大多数场景** | 上传按钮、被 `isTrusted` 挡住的按钮 |

**默认先用 `/click`**；点了没反应、或目标按钮依赖真实手势时，换 `/clickAt`。
上传文件其实**不必**用 `/clickAt`——直接 `/setFiles` 更可靠（完全绕过对话框）。

---

## 错误处理

| 错误 | 原因 | 解决 |
|---|---|---|
| `Chrome 未开启远程调试端口` | 浏览器没开调试开关 | 让用户打开 `edge://inspect/#remote-debugging`（Chrome 为 `chrome://...`）并勾选 **Allow remote debugging for this browser instance** |
| `attach 失败` | `targetId` 失效或 tab 已关 | 重新 `GET /targets` 取最新列表 |
| `CDP 命令超时` | 页面长时间无响应 | 重试；或 `/info` 看 tab 是否卡死，必要时 `/close` 重建 |
| `端口已被占用` | 已有 proxy 在跑 | **直接复用**，不要再起一个 |
| 调用返回 400 且含 `migration` 字样 | 用了 v2.5.2 旧写法 | 见上方「迁移对照」 |
| `readyState: complete` 但内容为空 | 见下一节 | 不是 CDP 的问题，是就绪判断的问题 |

### 页面就绪 ≠ 内容就绪（最常踩的坑）

`/new` 或 `/navigate` 返回**只代表文档基础加载完成**。HTTP 200、`readyState === "complete"`、标题出现，**都不能单独作为完成标准**。

正确做法：导航后用 `/eval` 检查目标内容；若未出现且页面仍是空白 / 加载态 / 验证页 / 登录跳转，在默认 **15 秒**窗口内持续观察 URL、标题、DOM，页面变化后重新判断。目标内容到手、或窗口结束仍有明确阻碍，才继续提取或报失败。

> 同理，**HTTP 200 也不代表有内容**——本工具箱实测到 RSS 源返回 200 但 body 为 0 字节（假活）。

---

## 相关文档

- 操作范式、降级顺序、站点经验 → [CDP浏览器直连](CDP浏览器直连.md)
- 遇到 403 / Cloudflare / Turnstile → [反爬对抗](反爬对抗.md)
- 抓取管道 → [网页抓取](网页抓取.md)
