---
name: Playwright 高级用法（pw.mjs）
---

# Playwright 高级用法（`scripts/pw.mjs`）

**何时读**：CDP 直连不可用时的降级执行器，或需要请求 mock / 状态存取 / trace 录制 / 录屏 / 生成测试代码时。

> **本机零安装**：Playwright 1.63+ 自带 `cli` 子命令，工具箱 `node_modules` 里已有 `playwright`，
> 所以**不需要** `npm install -g @playwright/cli`（更不要装 `@playwright/mcp`，那是 MCP 服务端，不是这个 CLI）。
> 统一起见，`pw.mjs` 已改为**只在 `open` 子命令上注入 `--browser=msedge`**（其他子命令不接受该选项）。

---

## 0. 铁律（先看这条，能省半小时）

| 坑 | 真相 |
|---|---|
| 以为「用了浏览器就有登录态」 | ❌ 默认是**隔离 browserContext**（等同无痕）。要复用登录态请回 [CDP浏览器直连](CDP浏览器直连.md)，或 `--persistent` / `--profile` |
| `snapshot` 看不到输出 | 快照默认**写文件**到 `.playwright-cli/*.yml`，不打印到 stdout。去 `cat` 它，或建 `playwright-cli.json` 写 `{"outputMode":"stdout"}` |
| `--browser` 加到 `click`/`fill` 上报 `Unknown option` | 实测 1.63 只有 `open` 接受 `--browser`。`pw.mjs` 已修正 |
| 在 Playwright 上死磕 Cloudflare | 先上 CDP 直连。见 [反爬对抗](反爬对抗.md) |

**首动作**：`node scripts/pw.mjs open <url> --browser=msedge`（走系统 Edge，免下载浏览器）。

---

## 1. 基础操作

```bash
node scripts/pw.mjs open https://example.com        # 打开并导航（自动 --browser=msedge）
node scripts/pw.mjs snapshot                        # 取元素 ref → 写入 .playwright-cli/page-*.yml
cat .playwright-cli/page-*.yml                      # ⚠️ 必须 cat 文件，不要指望 stdout
node scripts/pw.mjs click e15                       # 用快照里的 ref 点击
node scripts/pw.mjs fill e5 "user@example.com"
node scripts/pw.mjs type "搜索词"
node scripts/pw.mjs press Enter
node scripts/pw.mjs screenshot
node scripts/pw.mjs close
```

**常用命令全集**（按 `--help` 实测分组）：

| 组 | 命令 |
|---|---|
| Core | `open` `attach` `close` `detach` `goto` `type` `click` `dblclick` `fill` `drag` `drop` `hover` `select` `upload` `check` `uncheck` `snapshot` `find` `eval` `dialog-accept` `dialog-dismiss` `resize` `delete-data` |
| 导航 | `go-back` `go-forward` `reload` |
| 键盘 / 鼠标 | `press` `keydown` `keyup` / `mousemove` `mousedown` `mouseup` `mousewheel` |
| 保存 | `screenshot [target] [--filename=]` `pdf --filename=page.pdf` |
| Tab | `tab-list` `tab-new [url]` `tab-close [idx]` `tab-select <idx>` |
| 存储 | `state-save` `state-load` / `cookie-*` / `localstorage-*` / `sessionstorage-*` |
| 网络 | `requests` `request <i>` `request-headers` `request-body` `response-headers` `response-body` `route` `route-list` `unroute` `network-state-set` |
| DevTools | `console [min-level]` `run-code` `recording-start` `recording-stop` `tracing-start` `tracing-stop` `video-start` `video-stop` `video-chapter` `video-show-actions` `video-hide-actions` `show` `generate-locator` `highlight` |
| 会话 | `list` `close-all` `kill-all` |
| 全局选项 | `-s=<session>` `--json` `--raw` `--help` |

**命名会话**（`-s=` 必须放在子命令**之前**，实测）：

```bash
node scripts/pw.mjs -s=wenku open https://wenku.baidu.com/ --persistent
node scripts/pw.mjs -s=wenku click e6
node scripts/pw.mjs -s=wenku close          # 下次 -s=wenku 状态仍在
node scripts/pw.mjs list                    # 列出所有会话
node scripts/pw.mjs close-all               # 全部关闭
node scripts/pw.mjs kill-all                # 强杀僵尸进程
```

环境变量 `PLAYWRIGHT_CLI_SESSION=<name>` 可设默认会话名。

---

## 2. 生成测试代码（原「test-generation」）

**这是最容易被忽略的能力**：你每做一步操作，CLI 会把对应的 Playwright TypeScript 代码一并打印出来，可以直接攒成测试文件。

```bash
node scripts/pw.mjs recording-start          # 开始录制用户操作
node scripts/pw.mjs open https://example.com/login
node scripts/pw.mjs snapshot
node scripts/pw.mjs fill e1 "user@example.com"
node scripts/pw.mjs fill e2 "password123"
node scripts/pw.mjs click e3
node scripts/pw.mjs recording-stop           # 停止并把操作序列打印成 Playwright 代码
```

产出的就是这种可直接粘进测试文件的代码：

```typescript
await page.goto('https://example.com/login');
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
await page.getByRole('textbox', { name: 'Password' }).fill('password123');
await page.getByRole('button', { name: 'Sign In' }).click();
```

相关辅助：`generate-locator <target>` 为某元素单独生成定位器；`highlight [target]` 在页面上高亮元素核对。

**要点**：
- **优先用语义定位器** `getByRole(...)`，比 CSS `#submit-btn` 抗改版得多
- 录制只捕获**动作**，断言要自己补：`await expect(page.getByText('Success')).toBeVisible();`
- 先 `snapshot` 看清结构再录制，减少走弯路

---

## 3. 请求拦截与 mock

```bash
# 打桩
node scripts/pw.mjs route "**/*.jpg" --status=404
node scripts/pw.mjs route "**/api/users" --body='[{"id":1,"name":"Alice"}]' --content-type=application/json
node scripts/pw.mjs route "**/api/data" --body='{"ok":true}' --header="X-Custom: value"
node scripts/pw.mjs route "**/*" --remove-header=cookie,authorization   # 剥掉请求头

node scripts/pw.mjs route-list
node scripts/pw.mjs unroute "**/*.jpg"
node scripts/pw.mjs unroute                    # 清空全部
```

**URL 模式语法**：

| 模式 | 匹配 |
|---|---|
| `**/api/users` | 精确路径 |
| `**/api/*/details` | 路径中通配 |
| `**/*.{png,jpg,jpeg}` | 文件扩展名 |
| `**/search?q=*` | 带 query |

**条件响应 / 改真实响应 / 模拟断网**（`run-code`）：

```bash
# 按请求内容分流
node scripts/pw.mjs run-code "async page => {
  await page.route('**/api/login', route => {
    const body = route.request().postDataJSON();
    if (body.username === 'admin') route.fulfill({ body: JSON.stringify({ token: 'mock-token' }) });
    else route.fulfill({ status: 401, body: JSON.stringify({ error: 'Invalid' }) });
  });
}"

# 抓真实响应后篡改再放行
node scripts/pw.mjs run-code "async page => {
  await page.route('**/api/user', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.isPremium = true;
    await route.fulfill({ response, json });
  });
}"

# 模拟网络失败 / 延迟
node scripts/pw.mjs run-code "async page => { await page.route('**/api/offline', r => r.abort('internetdisconnected')); }"
node scripts/pw.mjs run-code "async page => {
  await page.route('**/api/slow', async r => { await new Promise(x => setTimeout(x, 3000)); r.fulfill({ body: '{}' }); });
}"
```

`abort` 可选原因：`connectionrefused` / `timedout` / `connectionreset` / `internetdisconnected`。

**网络观测**（不 mock，只看）：

```bash
node scripts/pw.mjs requests                  # 列出本次加载的所有请求（带编号）
node scripts/pw.mjs request 3                 # 某条请求的完整细节（头 / body / 响应）
node scripts/pw.mjs response-body 3           # 只取响应体（文本内联，二进制存文件并打印路径）
node scripts/pw.mjs network-state-set offline # 切离线
```

---

## 4. 存储状态（登录态迁移）

### 整站状态存取

```bash
node scripts/pw.mjs state-save auth.json      # 存 cookie + localStorage 到文件
# ... 换会话/换天 ...
node scripts/pw.mjs state-load auth.json
node scripts/pw.mjs open https://app.example.com/dashboard   # 已是登录态
```

文件格式：

```json
{
  "cookies": [
    { "name": "session_id", "value": "abc123", "domain": "example.com", "path": "/",
      "expires": 1735689600, "httpOnly": true, "secure": true, "sameSite": "Lax" }
  ],
  "origins": [
    { "origin": "https://example.com", "localStorage": [{ "name": "theme", "value": "dark" }] }
  ]
}
```

### Cookie / Storage 细粒度

```bash
node scripts/pw.mjs cookie-list [--domain=example.com] [--path=/api]
node scripts/pw.mjs cookie-get session_id
node scripts/pw.mjs cookie-set session abc123 --domain=example.com --path=/ --httpOnly --secure --sameSite=Lax
node scripts/pw.mjs cookie-set remember_me t123 --expires=1735689600    # Unix 时间戳
node scripts/pw.mjs cookie-delete session_id / cookie-clear

node scripts/pw.mjs localstorage-list | localstorage-get token | localstorage-set theme dark
node scripts/pw.mjs localstorage-delete token | localstorage-clear
node scripts/pw.mjs sessionstorage-list | sessionstorage-get form_data | sessionstorage-set step 3
node scripts/pw.mjs sessionstorage-delete step | sessionstorage-clear
```

### IndexedDB（只能走 run-code，无专用命令）

```bash
node scripts/pw.mjs run-code "async page => page.evaluate(async () => await indexedDB.databases())"
node scripts/pw.mjs run-code "async page => page.evaluate(() => { indexedDB.deleteDatabase('myDatabase'); })"
```

**批量注入多个 cookie**（`cookie-set` 一次只能一个）：

```bash
node scripts/pw.mjs run-code "async page => {
  await page.context().addCookies([
    { name: 'session_id', value: 'sess_abc', domain: 'example.com', path: '/', httpOnly: true },
    { name: 'prefs', value: JSON.stringify({ theme: 'dark' }), domain: 'example.com', path: '/' }
  ]);
}"
```

**安全**：`*.auth-state.json` 一律加进 `.gitignore`；含 token 的状态文件用完即删；默认 in-memory 会话更安全。

---

## 5. run-code：任意 Playwright 代码

`run-code` 接受 `async page => { ... }`，`page.context()` 可拿到整个浏览器上下文。

```bash
# 地理位置与权限
node scripts/pw.mjs run-code "async page => {
  await page.context().grantPermissions(['geolocation','notifications','camera','microphone']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"
node scripts/pw.mjs run-code "async page => page.context().clearPermissions()"
node scripts/pw.mjs run-code "async page => page.context().grantPermissions(['clipboard-read'], { origin: 'https://example.com' })"

# 媒体仿真
node scripts/pw.mjs run-code "async page => page.emulateMedia({ colorScheme: 'dark' })"
node scripts/pw.mjs run-code "async page => page.emulateMedia({ reducedMotion: 'reduce' })"
node scripts/pw.mjs run-code "async page => page.emulateMedia({ media: 'print' })"

# 等待策略（比死等更可靠）
node scripts/pw.mjs run-code "async page => page.waitForLoadState('networkidle')"
node scripts/pw.mjs run-code "async page => page.waitForSelector('.loading', { state: 'hidden' })"
node scripts/pw.mjs run-code "async page => page.waitForFunction(() => window.appReady === true)"
node scripts/pw.mjs run-code "async page => page.waitForSelector('.result', { timeout: 10000 })"

# iframe
node scripts/pw.mjs run-code "async page => page.locator('iframe#f').contentFrame().locator('button').click()"
node scripts/pw.mjs run-code "async page => page.frames().map(f => f.url())"

# 文件下载
node scripts/pw.mjs run-code "async page => {
  const [dl] = await Promise.all([page.waitForEvent('download'), page.click('a.download-link')]);
  await dl.saveAs('./downloaded.pdf');
  return dl.suggestedFilename();
}"

# 剪贴板
node scripts/pw.mjs run-code "async page => {
  await page.context().grantPermissions(['clipboard-read']);
  return await page.evaluate(() => navigator.clipboard.readText());
}"

# 带错误处理（元素可能不存在时）
node scripts/pw.mjs run-code "async page => {
  try { await page.click('.maybe-missing', { timeout: 1000 }); return 'clicked'; }
  catch (e) { return 'element not found'; }
}"

# 多页循环抓取
node scripts/pw.mjs run-code "async page => {
  const out = [];
  for (let i = 1; i <= 3; i++) {
    await page.goto(\`https://example.com/page/\${i}\`);
    out.push(...await page.locator('.item').allTextContents());
  }
  return out;
}"
```

---

## 6. trace 录制与回放（调试首选）

```bash
node scripts/pw.mjs tracing-start
node scripts/pw.mjs open https://app.example.com
node scripts/pw.mjs click e5                 # 假设这一步失败了，为什么？
node scripts/pw.mjs tracing-stop
# 打开 trace 查看点击时的 DOM 状态
```

`traces/` 目录产物：

| 文件 | 内容 |
|---|---|
| `trace-{ts}.trace` | 动作日志：每步的 DOM 快照、截图、时序、console 消息、源码位置 |
| `trace-{ts}.network` | 完整网络日志：请求/响应头与体、DNS/连接/TLS/TTFB/下载耗时、失败请求 |
| `resources/` | 缓存资源（图片、字体、样式、脚本、响应体），用于回放页面状态 |

**最佳实践**：从问题**之前**就开始录，而不是只录失败那一步。清理旧 trace：

```bash
find .playwright-cli/traces -mtime +7 -delete
```

---

## 7. 录屏

```bash
node scripts/pw.mjs video-start
node scripts/pw.mjs open https://example.com
node scripts/pw.mjs click e1
node scripts/pw.mjs video-stop recordings/login-flow.webm    # WebM (VP8/VP9)
node scripts/pw.mjs video-chapter "登录步骤"                  # 加章节标记
node scripts/pw.mjs video-show-actions                       # 在页面上给动作加标注气泡
```

| | trace | video | screenshot |
|---|---|---|---|
| 格式 | `.trace` | `.webm` | `.png` / `.jpeg` |
| DOM 检视 | ✅ | ❌ | ❌ |
| 网络细节 | ✅ | ❌ | ❌ |
| 逐步回放 | ✅ | 连续 | 单帧 |
| 体积 | 中 | 大 | 小 |
| 适合 | **调试** | 演示 | 快速留证 |

---

## 8. 排障速查

| 现象 | 原因 / 解决 |
|---|---|
| `playwright` 未找到 | 工具箱 `node_modules` 缺依赖：`cd 联网工具箱 && npm install`（**不是** `@playwright/mcp`） |
| `--self-check` 报错 | `node scripts/pw.mjs --self-check` 看 cli.js 路径与版本 |
| 快照没输出 | 去 `cat .playwright-cli/page-*.yml`，或设 `outputMode: stdout` |
| 截图失败 | 先确认浏览器已 `open` |
| 看不到我的登录态 | 默认隔离上下文；用 `--persistent` / `--profile`，或直接回 CDP 直连 |
| `Unknown option: --browser` | 旧版 `pw.mjs` 的 bug，已修；确认脚本是最新的 |
| 僵尸进程 | `node scripts/pw.mjs kill-all` |
| 遇 Cloudflare / Turnstile | **不要**在这层硬试 → [反爬对抗](反爬对抗.md) |
