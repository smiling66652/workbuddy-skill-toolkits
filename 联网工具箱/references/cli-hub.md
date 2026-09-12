---
name: CLI 工具中心
---

# CLI 工具中心

**适用场景**：需要确认"本机有什么工具可用"，或需要搜索/安装专业命令行工具时读。**优先用本机已装的，不要临时现找。**

> ⚠️ **本页所有状态均为 2026-09-11 实测**。旧版本此表有 3 处虚假声明（`gh` / `yt-dlp` / `wget` 当时并未安装），已修正。
> 任何时候想复核，跑 `node scripts/doctor.mjs`。

---

## 本机已就绪（实测）

| 工具 | 状态 | 用途与备注 |
|---|---|---|
| `node` / `npx` | ✅ 22.22.2（托管） | 跑本目录下 `.mjs` 脚本。路径：`C:/Users/Matebook/.workbuddy/binaries/node/versions/22.22.2-2/` |
| `python` | ✅ 3.13.12（托管）/ 3.13.14（venv） | 数据处理、抓取。venv：`binaries/python/envs/default/Scripts/python.exe` |
| `playwright` | ✅ 1.63.0（**本目录 node_modules 内**） | 通过 `scripts/pw.mjs` 调用，**无需全局安装**；默认走系统 Edge，免下载浏览器 |
| `curl` | ✅ 8.14.1（Windows 自带） | 直链下载、探接口。**校园网需加 `--ssl-no-revoke`**，否则报 `CRYPT_E_NO_REVOCATION_CHECK` |
| `agent-browser` | ❌ **未安装**（2026-09-12 复核） | 不在 PATH，npm/托管 node 全局均无；只剩 `~/.agent-browser/` 缓存。要用先 `npm install -g agent-browser && agent-browser install` |
| `playwright-cli`（全局） | ⚠️ 装有 `playwright-cli@0.262.0` 但**已被官方废弃为占位包** | 正确包名 `@playwright/cli`。本机不需要它——用 `scripts/pw.mjs` 走工具箱自带的 playwright 1.63 |
| `pip` | ✅ 26.1.2 | 装 Python 包。**必须加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`**（默认源在本机频繁超时） |
| `gh` | ❌ 未安装 | GitHub 操作。装：`winget install GitHub.cli`；不装则用 WebFetch 读页面 |
| `yt-dlp` | ❌ 未安装 | 视频/音频/字幕。装：`venv python -m pip install yt-dlp` |
| `jq` | ❌ 未安装 | JSON 处理。不装则用 `node -e` 或 Python |
| `wget` | ❌ 未安装 | **用 `curl -O` 替代**，不要写 wget |
| `ffmpeg` | ❌ 未安装 | 音视频转码。仅视频处理任务需要 |
| `scrapy` | ❌ 未安装 | 大批量抓取才需要；轻量抓取用 CDP 直连或 pw.mjs |

---

## 本 skill 自带脚本（`scripts/`）

用法统一为：`node scripts/<脚本名>.mjs <参数>`

### CDP 直连（2026-09-12 从 web-access 收编，零依赖，纯 node 内置模块）

| 脚本 | 用途 |
|---|---|
| `check-deps.mjs` | **前置检查 + 自动拉起 Proxy**。退出码 0 就绪 / 1 环境错误 / 2 需选浏览器；`--browser <chrome\|edge>` 单次覆盖 |
| `cdp-proxy.mjs` | **CDP 代理本体**，`localhost:3456` 全部 API。通常由 check-deps 拉起 |
| `find-url.mjs` | **本地书签/历史检索**。`[关键词...] [--only bookmarks\|history] [--browser] [--since 1d] [--sort recent\|visits]` |
| `browser-discovery.mjs` | 浏览器发现 + 读 `config.env` 偏好 + 兜底端口探测（被上面两个 import） |
| `match-site.mjs` | 按域名/别名匹配已积累的站点经验 |

> 配置在技能根目录 `config.env`（`WEB_ACCESS_BROWSER=edge`，已 gitignore）。
> 端点全集见 [CDP-API参考](CDP-API参考.md)。

### 环境与工具

| 脚本 | 用途 |
|---|---|
| `doctor.mjs` | **环境自检**。实测每层是否可用，输出能力矩阵。`--json` 机器可读，`--quick` 跳过联网探测 |
| `pw.mjs` | **本地 playwright-cli 封装**（零安装）。`open <url>` / `snapshot` / `click <ref>` / `eval` / `close`；`-s=<会话>` 命名会话，`--raw` 透传 |
| `site-patterns-check.mjs` | 站点经验体检：校验 frontmatter 格式、查重复域名/别名、标出长期未更新的条目 |
| `rss.mjs` | 零依赖 RSS 阅读器。`--preset news\|tech\|ai\|dev\|all` / `--url` / `--since 1d` / `--json` |

### 下载（电子书 / 教材）

| 脚本 | 用途 |
|---|---|
| `archiveorg-find.mjs` | Internet Archive **API 版**检索并下载（推荐） |
| `archiveorg-search-download.mjs` | IA 网页搜索 + metadata 接口筛 PDF 并下载 |
| `archiveorg-download.mjs` | IA **UI 搜索**版（较慢） |
| `annas-archive-download.mjs` | Anna's Archive 按 ISBN 走 Slow download |
| `jiumo-find.mjs` | ❌ **已失效**（鸠摩搜书 2026-09 全镜像已挂），仅留历史参考 |
| `reuse-chrome-download.mjs` | 复用本机 Chrome/Edge 登录态下载登录墙文档 |

> 完整用法见 [电子书下载](电子书下载.md) 与 [复用Chrome登录态下载](复用Chrome登录态下载.md)。

---

## ⚠️ 本机 venv 的"包被剥离"问题

本机 venv（`binaries/python/envs/default`）出现过**包目录被剥离**：目录在，但 `.py` / `.pyd` 没了，
只剩 `__pycache__`。表现是 `import` 报 `ModuleNotFoundError`，但 `pip list` 显示"已安装"。
最要命的是 `pip` 自身也会被剥离 —— 此时所有安装都失败，**但报错看起来像网络超时**。

完整症状与修复步骤（pip 自修复、单包手工重装、pip 整体回滚的坑）已统一搬到
→ **[故障诊断](故障诊断.md) 第 4 节「Python 抓取栈」**。

三个速记要点：
- 修复必须**先移走残留的 `dist-info`**，否则 `ensurepip` 判定"已满足"而跳过
- 被剥离的包 `pip uninstall` 无效（`no RECORD file was found`），只能删目录重装
- 一律加 `-i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120 --prefer-binary`

---

## 找新工具的流程

1. **先在本页查**有没有现成的
2. 再搜，优先找**有 CLI、有文档、近期有更新**的
3. **装完必须先跑一个最小用例验证**，别只看 README
4. 验证通过后，**把工具补进本页表格 + 跑一次 `doctor.mjs` 确认被识别**

**踩过的坑（务必避免）**：
- 别照抄文档里的安装命令就信 —— 本工具箱历史上就出现过 `@playwright/mcp` 误当 `playwright-cli`、
  `human-browser-cli`（npm 上实为 404）、`agent-browser act` 子命令（不存在）三处错误。
- **装包前先核实包真的存在**：
  `curl -o /dev/null -w '%{http_code}' https://registry.npmjs.org/<包名>` 或
  `https://pypi.org/pypi/<包名>/json`（404 = 不存在）。

---

## 注意

- 需要登录态的站点走 CDP 直连或 `reuse-chrome-download.mjs`，不要硬破
- 下载类操作注意目标站点条款，仅用于自己有权限的内容
- 大文件下载前先 `curl -I` 看 `Content-Length`，避免下到一半才发现是错误页
- 遇强反爬（Cloudflare / Turnstile）先读 [反爬对抗](反爬对抗.md)，别在 CLI 层硬试
- **任何报错先翻 [故障诊断](故障诊断.md)** —— 按症状索引，含 Node、CDP、Playwright、Python、本机网络五类
