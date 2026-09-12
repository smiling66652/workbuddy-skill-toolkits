# Kimi WebBridge 本地协议（逆向发现，用于接入 WorkBuddy）

> 状态：部分逆向（2026-09-08）。Kimi WebBridge 是 ego 类"AI 共用浏览器会话"的 Windows 平替。本机已安装，守护进程监听 `127.0.0.1:10086`。

## 已确认事实

| 项 | 值 |
|---|---|
| 安装路径 | `~/.kimi-webbridge/bin/kimi-webbridge.exe`（v2.0.5） |
| 守护进程状态 | `running:true`，监听 `127.0.0.1:10086`（本地、登录态不出本机） |
| HTTP 端点 | `GET /status` → 200 JSON；`GET /` → 404；`GET /ws` → 403（需带扩展 Origin） |
| WebSocket | `ws://127.0.0.1:10086/ws` |
| 扩展 ID | `bnlffdbcfnanfbknnlaflhlhkocccckg`（Edge 中名为 "Kimi"，版本 2.0.1） |
| 扩展权限 | `debugger`（说明它通过 CDP 控制浏览器）、`downloads`、`tabs`、`scripting` 等 |
| 扩展 CSP | 允许连接 `ws://127.0.0.1:*`、`ws://localhost:*`、`ws://*:10086`、以及 kimi.com 域名 |

## 握手流程（已实测通过）

```js
const ws = new WebSocket('ws://127.0.0.1:10086/ws', {
  origin: 'chrome-extension://bnlffdbcfnanfbknnlaflhlhkocccckg'
});
ws.on('open', () => {
  ws.send(JSON.stringify({ type: 'hello', version: '2.0.1' }));
});
// 服务器回复：
// {"type":"hello_ack","payload":{"daemonVersion":"v2.0.5"}}
```

要点：
- **必须带 `origin: chrome-extension://<扩展ID>`**，否则 403。
- 握手后发 `{type:'hello'}` 收到 `hello_ack`。
- 发 `{type:'ping'}` 收到 `{type:'pong'}`（其余试探类型静默，完整业务协议待继续逆向 `background.js`）。

## 接入 WorkBuddy 的两条路

### 路线 A（推荐，已可用）：直接用 Edge + 本 skill 的复用登录态脚本
Kimi 扩展装在 Edge 上，而 Edge 本就支持 CDP。直接用
`scripts/reuse-chrome-download.mjs --browser edge`（脚本已自动检测 Edge），
即可在 WorkBuddy 里以你的 Edge 登录态驱动下载，无需经过 Kimi 的私有协议。

### 路线 B（进阶）：充当 WebBridge 的"Agent"端
WebBridge 的设计是"扩展 ↔ 守护进程 ↔ 支持的 Agent（Kimi Code / Claude Code）"。
WorkBuddy 不在其硬编码支持列表，但协议是开放 WebSocket：
1. 连 `ws://127.0.0.1:10086/ws`（带扩展 Origin）；
2. 解析 `background.js` 中的业务消息类型（当前混淆，需美化/AST 提取字符串常量数组）；
3. 实现一个本地 MCP server，把"导航/点击/截图/下载"等动作桥接到 WorkBuddy 工具。
   逆向 `background.js` 的下一步：用 `js-beautify` 美化后提取 `type:` 字符串表与消息 schema。

## 启动/停止命令

```bash
# 常驻（run 是前台命令，start 会 fork 后被回收，需用 run）
~/.kimi-webbridge/bin/kimi-webbridge.exe run          # 后台常驻
~/.kimi-webbridge/bin/kimi-webbridge.exe status       # 查状态
~/.kimi-webbridge/bin/kimi-webbridge.exe stop         # 停止
```

> 注：`extension_connected:false` 表示还需在 Edge 里点击 Kimi 扩展图标 / 打开 kimi.com 激活一次，扩展才会连上守护进程。要真正"接管浏览器"还需配一个它支持的 Agent。
