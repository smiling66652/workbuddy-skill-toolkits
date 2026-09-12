# 复用浏览器登录态下载电子书 / 文档

> 适用场景：目标站点需要登录（知网 / CARSI / 图书馆 / 各类会员资源），但你**已经在浏览器里登录过**，不想再走一遍人工登录。

## 核心思路

用 Playwright 驱动**本机已安装的 Edge / Chrome**（默认自动检测，优先 Edge），把 `userDataDir` 指向本机浏览器的 `User Data` 目录。新开的浏览器会话会直接继承 `Default` 档案里的全部 Cookie 与登录态——等于"以你本人的身份"去访问网站，Agent 无需知道账号密码，也跳过二次验证。

- 自动检测 Edge / Chrome 路径 → **免下载浏览器**，复用现有安装。
- `acceptDownloads: true` + 监听 `page.on('download')` → 自动把文件落盘到指定目录。
- 会话持久化（`launchPersistentContext`）→ 关掉重开仍保留登录态。
- 脚本目录已自带 `playwright` 依赖，直接用 managed node 运行即可。

## 使用方法

脚本位置：`scripts/reuse-chrome-download.mjs`

```bash
# 默认自动检测浏览器（本机只有 Edge 时会自动用 Edge）
"C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/node.exe" \
scripts/reuse-chrome-download.mjs \
  --url "https://目标站点/某书/下载页" \
  --download-dir "D:/桌面/电子书/_downloads"

# 显式指定 Edge（或 --browser chrome）
... reuse-chrome-download.mjs --browser edge --url "..." --download-dir "..."
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--url` | ✅ | 目标页面 |
| `--download-dir` | | 保存目录，默认 `~/Downloads/ebooks` |
| `--click` | | 触发下载的按钮/链接 CSS 选择器，命中后自动点击 |
| `--profile` | | 子档案名（如 `WorkBuddy`）；省略则复用本机 `Default` |
| `--browser` | | `edge` \| `chrome`（默认自动检测） |
| `--headless` | | 加此 flag 用无头模式 |
| `--wait` | | 下载等待毫秒数，默认 `8000` |

### 两种档案模式

1. **复用本机 Default（默认，最省事）**
   - 直接继承你所有已登录站点。
   - ⚠️ 运行前**关闭所有浏览器窗口**，否则 `SingletonLock` 冲突导致启动失败。

2. **独立子档案 `--profile WorkBuddy`**
   - 在 `User Data/` 下新建独立档案，不与日常浏览冲突。
   - 首次用有头模式（`--headless` 不加）打开登录一次，之后复用该档案即可。

## 典型流程

```
1. 关闭其他浏览器窗口（用 Default 模式时）
2. 运行脚本，--url 指向资源页
3. 若站点需"点击下载"按钮，加 --click "选择器"
4. 文件自动保存到 --download-dir
5. context.close() 自动释放
```

## 与 kill-doc / P0 方案的关系

- **P0 kill-doc**：30+ 文库类站点免登录直接下载，优先用。
- **本方案**：针对"必须登录、且你已登录"的**教材/论文/图书馆资源**（知网、Springer、Elsevier、学校图书馆系统），用你既有身份合规访问，无需破解。
- **P2 Human Browser**：仅当遇到 Cloudflare 等强反爬封 IP 时兜底。

## 安全与合规

- 仅用于你有权访问的本人账号资源（学校订阅、个人会员），登录态不会离开本机。
- 不要用于批量爬取或突破授权范围，避免账号风控。
