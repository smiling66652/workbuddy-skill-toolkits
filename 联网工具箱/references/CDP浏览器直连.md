---
name: 二级：CDP 浏览器直连
---

# 二级：CDP 浏览器直连（P0 首选）

**适用场景**：需要登录态、遇到反爬、静态层拿不到内容、需要像人一样在浏览器里自由导航

> **本层实现已自持**：CDP Proxy 与配套脚本都在本技能 `scripts/` 下，不再依赖任何外部技能包。
> 原实现来自 `web-access`（MIT，作者 一泽Eze，github `eze-is/web-access`），已于 2026-09-12 收编。
> 联网工具箱把它作为**浏览器层的首选实现**，Playwright / Agent Browser 降级为备选。

---

## 为什么 CDP 是首选

CDP Proxy 直连**你日常正在用的 Chrome / Edge**，不启动独立浏览器实例。

| 对比项 | CDP 直连 | Playwright CLI | Agent Browser | Human Browser |
|--------|---------|----------------|---------------|---------------|
| 登录态 | ✅ 天然继承，无需重登 | ❌ 需持久化 profile 重建 | ❌ | ❌ |
| 启动开销 | 无（复用已开浏览器） | 高（拉起新实例） | 高 | 高（远程） |
| 反爬对抗 | 中高（真实浏览器环境） | 中 | 中 | 极高（住宅IP） |
| 真实鼠标手势 | ✅ `/clickAt` | 部分 | ✅ | ✅ |
| 本地书签/历史检索 | ✅ `find-url.mjs` | ❌ | ❌ | ❌ |
| 成本 | 免费 | 免费 | 按量 | 付费 |

**判据**：目标站点**你已在浏览器里登录过**（知网/CARSI/微信/QQ/小红书/公众号后台等）→ 直接 CDP，不要先试静态层。

---

## 前置检查（每次联网任务开始必做）

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/check-deps.mjs"
```

**必须 Node.js 22+**（原生 WebSocket）。按退出码处理：

| 退出码 | 含义 | 处理 |
|--------|------|------|
| `0` | 就绪 | 继续 |
| `1` | 环境错误 | 按 stdout 提示处理；若提示「Agent 处理顺序」，按其步骤执行 |
| `2` | 需选浏览器 | 询问用户，写入 `联网工具箱/config.env` 的 `WEB_ACCESS_BROWSER` |

**首次使用**：需要你在浏览器里开启远程调试——地址栏打开 `chrome://inspect/#remote-debugging`（Edge 是 `edge://inspect/#remote-debugging`），勾选 **Allow remote debugging for this browser instance**。一次性操作，之后长期有效。

切换浏览器时 proxy 是长驻进程，需先 `pkill -f cdp-proxy.mjs` 再重跑 check-deps。

**执行前必须向用户展示**：

```
温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。已内置防护措施但无法完全避免，Agent 继续操作即视为接受。
```

---

## 核心 API（Proxy 地址 `http://localhost:3456`）

> 这只是常用子集。**端点全集、参数位置、返回值形态、错误码表、POST body 的来龙去脉**见 [CDP-API参考](CDP-API参考.md)。
> 调用报错先查 [故障诊断](故障诊断.md)。

```bash
# 列出已打开的 tab
curl -s http://localhost:3456/targets

# 新建后台 tab（URL 走 POST body，避免 query 里 & 被切分）
curl -s -X POST --data-raw 'https://example.com' http://localhost:3456/new

# 页面信息（title / url / readyState）
curl -s "http://localhost:3456/info?target=ID"

# 执行任意 JS —— 看 DOM、提取数据、填表提交、操控 video 元素
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'

# 截图（含视频当前帧）
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"

# 导航 / 后退
curl -s -X POST --data-raw 'https://example.com' "http://localhost:3456/navigate?target=ID"
curl -s "http://localhost:3456/back?target=ID"

# 点击：JS el.click()（快，覆盖大多数场景）
curl -s -X POST "http://localhost:3456/click?target=ID" -d 'button.submit'

# 真实鼠标点击：CDP Input.dispatchMouseEvent（算用户手势，能触发文件对话框）
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.upload'

# 文件上传：绕过文件对话框
curl -s -X POST "http://localhost:3456/setFiles?target=ID" \
  -d '{"selector":"input[type=file]","files":["D:/path/to/file.png"]}'

# 滚动（触发懒加载）
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"

# 关闭 tab
curl -s "http://localhost:3456/close?target=ID"
```

> **v2.5.3 迁移**：`/new` 与 `/navigate` 的 URL **必须走 POST body**。旧写法 `GET /new?url=...` 会返回 400。

### 页面就绪判断（最容易踩的坑）

`/new` 或 `/navigate` 返回**只代表文档基础加载完成**，不代表你要的内容已出现。HTTP 200、`readyState === "complete"`、标题出现，都不能单独作为完成标准。

**正确做法**：导航后用 `/eval` 检查目标内容。若未出现且页面仍是空白 / 加载态 / 验证页 / 登录跳转，在默认 **15 秒**窗口内持续观察 URL、标题、DOM；页面变化后重新判断。目标内容到手，或窗口结束后仍有明确阻碍，才继续提取或报失败。

---

## 沙箱 / 隔离环境启动浏览器（专属坑）

> 来源：`sandbox-browser-cdp` 技能已于 2026-09-15 并入本技能。其沙箱专属踩坑记录集中保留在此，避免淹没在通用路由手册里。

绝大多数场景直接连**本机正在运行的浏览器**（「前置检查」里的 `chrome://inspect` 开关）即可。但当你**必须新拉起一个隔离浏览器实例**时——沙箱阻断回环、需要干净 profile、或用户日常浏览器占着 9222——走下面的「后台保活」启动法。

### 为什么必须后台保活

工具（Bash / PowerShell）启动的 Edge / Chrome **会在命令结束时被沙箱整体回收子进程树**，表现就是「浏览器秒退、端口一下就没了」。

- **必须在 `run_in_background: true` 下启动**，且命令末尾加 `Start-Sleep 3000` 把父进程钉住：

```powershell
$dir="C:\Users\<user>\AppData\Local\Temp\edge-cdp-9444"
if(-not(Test-Path $dir)){ New-Item -ItemType Directory -Path $dir | Out-Null }
Start-Process -FilePath "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  -ArgumentList @("--remote-debugging-port=9444","--user-data-dir=$dir","--no-first-run","--no-default-browser-check","--new-window","about:blank")
Start-Sleep -Seconds 3000     # 关键：保住父进程，否则浏览器被回收
```

> 启动后，本技能的 `cdp-proxy.mjs` 会通过 `findFallbackPort()` **自动发现这个手动调试端口**，无需改任何配置即可用 `/targets`、`/new`、`/navigate`、`/eval` 等全套 API。

### 验证（必须加 `dangerouslyDisableSandbox: true`）

```bash
netstat -ano | grep -E "9444.*LISTEN"
curl -s --noproxy '*' --max-time 8 http://127.0.0.1:9444/json/version
```

沙箱阻断 loopback，curl 连不上时**加 `dangerouslyDisableSandbox: true`** 即可通（先用 curl 验证，再排查别的）。

### 沙箱专属坑清单

| 现象 | 真因 / 解法 |
|---|---|
| 工具启动的 Edge / Chrome 秒退 | 沙箱回收子进程树 → 必须 `run_in_background: true` + 命令末尾 `Start-Sleep 3000` 保活 |
| Node `fetch` 报 `fetch failed` 但 curl 正常 | 90% 是漏传端口 / 端口无人监听（报错不说明原因）。**CDP 客户端一律用 `node:http` 写，不要用 `fetch`** |
| 9222 端口返回 404 | 用户日常 Edge 常占着 9222 且它不是有效 DevTools 端点。**换任意空闲端口**（如 9444） |
| 脚本操作到错误的页面 | 新 profile 仍会带上用户扩展，产生多个 page target。**选 target 必须按 URL 过滤** |
| `cmd /c` 在 PowerShell 工具里被禁 | 用原生 cmdlet 或 .NET，不要调 `cmd` |

---

## 本地浏览器资源检索（独有能力）

用户指向**本人访问过的页面**或**组织内部系统**（公网搜不到）时，搜本地书签/历史：

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/find-url.mjs" [关键词...] \
  [--only bookmarks|history] [--browser chrome|edge] [--limit N] \
  [--since 1d|7h|YYYY-MM-DD] [--sort recent|visits]
```

- 关键词空格分词、多词 AND，匹配 title + url
- 默认遍历 Chrome + Edge，`--browser` 限定单一来源
- `--sort visits` 按访问次数排序（适合「我常去的 XX 网站」）
- `--since` / `--sort` 仅作用于历史
- **零外部依赖**：历史库是 SQLite，脚本优先调系统 `sqlite3` 命令，没有则回退到 Node 22+ 内置的 `node:sqlite`
  （2026-09-12 修正：此前在无 `sqlite3` 命令的 Windows 上直接报错退出，该「独有能力」实际不可用）

**典型场景**：「我之前看的那个讲 X 的文章」「我们那个 XX 平台」→ 先 `find-url`，拿到 URL 再 CDP 打开。

---

## 浏览哲学：目标导向，边看边判断

不要把 CDP 当脚本执行器按预设步骤跑完。带目标进去，每一步结果都是证据：

1. **定义成功标准** — 什么算完成？要拿到什么信息/达到什么状态？
2. **选起点** — 需要登录态、需要操作、已知静态层无效的平台（小红书、微信公众号等）→ 直接 CDP
3. **过程校验** — 结果对照成功标准。方向错了立即调整，**不在同一方式上反复重试**。搜索没命中 ≠ 方法不对，也可能目标不存在
4. **完成判断** — 达成就停，不为「完整」浪费代价

### 程序化 vs GUI 交互

- **程序化**（构造 URL 导航、eval 操作 DOM）：快而精确，但非正常用户行为，可能触发反爬
- **GUI 交互**（点击、填写、滚动）：网站不限制正常 UI 操作，确定性最高

GUI 交互也是程序化的**有效探测**——一次真实交互能观察站点实际行为（URL 模式、必需参数、跳转逻辑），为后续程序化提供依据。程序化受阻时，GUI 是可靠兜底。

**站点内交互产生的链接是可靠的**：通过卡片/条目/按钮自然到达的 URL 天然携带平台所需完整上下文。手动构造的 URL 可能缺隐式参数 → 被拦截、返回错误页、触发反爬。**提取 URL 时保留完整地址，不要裁剪参数。**

---

## 技术事实（写脚本前必读）

- 页面中存在大量**已加载但未展示**的内容：轮播非当前帧、折叠区块文字、懒加载占位元素。以数据结构（容器、属性、节点关系）为单位思考，可直接触达
- DOM 中存在选择器不可跨越的边界：Shadow DOM 的 `shadowRoot`、iframe 的 `contentDocument`。eval 递归遍历可一次穿透所有层级
- `/scroll` 到底部才触发懒加载，**提取图片 URL 前先滚动**
- 媒体资源：公开资源提取 URL 后直接下载读取；需登录态的才在浏览器内 navigate + screenshot
- 短时间内密集 `/new` 大量页面可能触发反爬风控
- 「内容不存在」「页面不见了」**不一定反映真实状态**，可能是 URL 缺参数或触发反爬

## 媒体与视频

- 内容在图片里 → `/eval` 从 DOM 拿图片 URL 定向读取，比全页截图精准得多
- 视频 → `/eval` 操控 `<video>` 元素（获取时长、seek 到任意时间点、播放/暂停），配合 `/screenshot` 采帧，做离散采样分析

## 登录判断

**核心问题只有一个：目标内容拿到了吗？**

打开页面先尝试获取目标内容。只有确认**拿不到**且判断登录能解决时，才提示用户：

> 当前页面在未登录状态下无法获取[具体内容]，请在你的浏览器中登录 [网站名]，完成后告诉我继续。

登录完成无需重启任何东西，直接刷新继续。

## 任务收尾

用 `/close` 关闭**自己创建的** tab，必须保留用户原有 tab。Proxy 持续运行，不建议主动停止（重启后需在浏览器重新授权）。

---

## 并行调研：子 Agent 分治

多个**独立**调研目标时，分治给子 Agent 并行，而非主 Agent 串行。

**收益**：总耗时 ≈ 单个子任务时长；抓取内容不进主 Agent 上下文，省 token。

**并行 CDP**：每个子 Agent 自行 `/new` 建后台 tab、自行操作、结束自行 `/close`。共享同一浏览器同一 Proxy，通过不同 targetId 隔离，无竞态。

**子 Agent prompt 写法**：
- 必须写 `必须加载「联网工具箱」skill 并遵循指引`，子 Agent 会自动加载，不要在 prompt 里复制 skill 内容
- **描述目标，不指定步骤**。避免用暗示手段的动词——「搜索xx」会把子 Agent 锚定到 WebSearch，而反爬站点其实需要 CDP 直连。用「获取」「调研」「了解」

| 适合分治 | 不适合分治 |
|----------|-----------|
| 目标相互独立 | 目标有依赖，下一个要上一个的结果 |
| 每子任务量足够大（多页抓取、多轮搜索） | 简单单页查询，分治开销大于收益 |
| 需要 CDP 或长时间运行 | 几次 WebSearch / Jina 就能完成 |

---

## 站点经验（本技能自持）

**存储位置**：`联网工具箱/references/site-patterns/{domain}.md` ← 读写都在这里

2026-09-12 起 web-access 已删除，站点经验不再有「上游镜像」，**本目录就是唯一数据源**。
体检与匹配用自带脚本：

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/site-patterns-check.mjs"     # 体检：格式 / 重复 / 陈旧
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/match-site.mjs" <域名或关键词>  # 按域名/别名匹配经验
```

格式：
```markdown
---
domain: example.com
aliases: [示例, Example]
updated: 2026-09-09
---
## 平台特征
架构、反爬行为、登录需求、内容加载方式
## 有效模式
已验证的 URL 模式、操作策略、选择器
## 已知陷阱
什么会失败以及为什么
```

CDP 操作成功后，若发现新的站点/新模式（URL 结构、平台特征、操作策略），**主动写入**站点经验目录。只写经过验证的事实，不写猜测。经验标注发现日期，当作「可能有效的提示」而非保证；按经验操作失败就回退通用模式并更新文件。

---

## 降级顺序（2026-09-11 实测修订）

```
CDP 直连（本技能自带 Proxy，localhost:3456）
  ↓ 未开调试端口 / Proxy 挂了
agent-browser --cdp 9222 / --auto-connect      复用同一套登录态，零重建
  ↓ 需交互又无调试端口
scripts/pw.mjs（本地 playwright-cli，走系统 Edge，零安装）
  ↓ 强反爬（Cloudflare / Turnstile）
nodriver（Python ≤3.13）→ curl_cffi（仅 TLS-only 站点）
  ↓ 全废
住宅代理 / 托管绕过 API（付费）
```

**三点提醒**：

1. 前两条都**复用真实浏览器登录态**，不要在这两步之间去重建 Cookie —— 重建才是反爬最容易被识别的行为。
2. 旧的「Human Browser（住宅 IP + iPhone 指纹，97% 绕过率）」**已移出主链**：npm 上 `human-browser-cli` 实测 404，本机未安装、未验证，且是付费方案。
3. 完整反爬判定流程与错误码诊断见 [反爬对抗](反爬对抗.md)。
