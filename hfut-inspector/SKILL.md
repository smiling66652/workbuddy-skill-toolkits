---
name: hfut-inspector
description: |
  合工大（HFUT）信息巡检统一系统 v5.0 —— 唯一一套系统、唯一入口 hfut.py。
  官网 18 栏目扫描（约 11 秒）+ QQ群/QQ空间/公众号采集 + AI 三层分析 + 邮件推送 + 知识库检索。
  触发词：合工大、HFUT、官网巡检、通知扫描、竞赛信息、保研通知、夏令营、讲座、教务通知、巡检报告、每日任务、日报
version: "5.0.0"
author: smiling66652
---

# 合工大信息巡检统一系统 v5.0

> **一套系统，一个入口。** 2026-09-11 由三套（v3.1 主仓库 / v3.2 独立脚本 / unified-daily）合并而来。

## read_when
- 用户要求扫描合工大官网、查询通知、生成巡检报告、跑每日任务
- 用户提到合工大、HFUT、保研、竞赛、夏令营、讲座、选课等关键词
- 用户要求查看系统状态、配置邮件、查历史索引

---

## 唯一入口

```
项目根：D:\项目整理\01-代码项目\hfut_info_monitor\
       （D:\hfut_info_monitor 是指向它的目录联接，同一份）
入口：  hfut.py
Python：⚠️ 必须用项目 venv —— .venv\Scripts\python.exe
        （系统 Python 缺 requests/bs4，直接 python 会 ImportError）
```

```bash
cd "D:/项目整理/01-代码项目/hfut_info_monitor"

.venv/Scripts/python.exe hfut.py scan              # 官网 18 栏目增量扫描 + 发邮件（日常）
.venv/Scripts/python.exe hfut.py scan --no-email   # 只扫描不发邮件
.venv/Scripts/python.exe hfut.py scan --full       # 全量扫描
.venv/Scripts/python.exe hfut.py report            # 读现有数据出摘要（0 网络请求）
.venv/Scripts/python.exe hfut.py status            # 系统状态
.venv/Scripts/python.exe hfut.py kb 保研           # 按关键词查历史索引
.venv/Scripts/python.exe hfut.py all               # 全源巡检（官网+QQ群+QQ空间+公众号+AI分析+邮件）
.venv/Scripts/python.exe hfut.py bootstrap         # 环境自检（Ollama / NapCat / 依赖）
```

### 子命令路由

| 命令 | 实际执行 |
|---|---|
| `scan` / `report` / `status` / `kb` | 转发到 `hfut_site/hfut_cli.py`（官网 18 栏目子系统，约 11 秒） |
| `all` | 转发到 `main_controller.py --mode all`（全源，较慢） |
| `bootstrap` | 转发到 `scripts/environment_bootstrap.py --check-only` |

### scan 输出格式（结构化纯文本，AI 直接转发）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 合工大巡检报告 YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总索引: 609 条
今日新增: N 条
覆盖栏目: 18/18
上次扫描: YYYY-MM-DD HH:MM:SS

🔔 关键通知（近7天，共 N 条）:
  [保研/竞赛/教务/奖学金/重要] YYYY-MM-DD 标题
         URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 报告: ...\hfut_site\hfut_report.html
```

---

## 目录结构（只看这几个）

```
hfut.py                     ← 唯一入口
hfut_site/                  ← 官网 18 栏目子系统
  ├─ hfut_scanner.py        核心爬虫引擎（通用解析器 + 并发采集）
  ├─ hfut_cli.py            scan / report / status / kb 子命令
  ├─ hfut_config.py         关键词分类（保研/竞赛/教务/奖学金/基金/学术/就业）
  ├─ hfut_email.py          QQ SMTP 465 邮件推送
  ├─ hfut_report_gen.py     HTML 报告生成
  ├─ hfut_full_index.json   完整通知索引（600+ 条）
  └─ hfut_scan_state.json   扫描状态（含各栏目条数）
main_controller.py          ← 全源巡检（QQ/公众号/AI 三层）
scripts/                    ← qq_group_monitor / qzone_monitor / wechat_monitor / ai_secretary ...
config/config.json + .env   ← 配置（敏感项在 .env）
```

---

## 全源巡检（hfut.py all）

覆盖：官网 18 栏目 + QQ 群 + QQ 空间好友动态 + 微信公众号 + AI 三层分析（L1 规则 / L2 Ollama / L3 DeepSeek 兜底）+ 邮件推送。

⚠️ 无人值守必须先设 `QZONE_LOGIN_TIMEOUT=0`，否则会卡在 QQ 扫码等待：

```bash
QZONE_LOGIN_TIMEOUT=0 .venv/Scripts/python.exe hfut.py all
```

NapCat 离线时 QQ 群自动跳过，不阻塞整体；Ollama 起不来则降级为 L1 规则引擎。

---

## ⚠️ 环境事实（2026-09-11 实测，写新逻辑前必读）

| 事项 | 说明 |
|---|---|
| **本机代理对 hfut 域名返回 502** | 走 `http_proxy` 时 `news.hfut.edu.cn` 直接 502；**直连只要 0.1 秒**。脚本已内置绕过（`trust_env=False` / 无代理 opener）。新写抓取代码必须照做，否则会误判"站点不可达"。**这是踩坑第一名** |
| **Playwright 分两侧看** | **Python 侧未装**（本项目 venv `import playwright` 报 `ModuleNotFoundError`）→ Python 里写浏览器兜底是死路。**Node 侧可用**：`联网工具箱/scripts/pw.mjs`（Playwright 1.63.0，走系统 Edge，零安装，2026-09-15 实测）。需要登录态优先用 CDP 直连日常浏览器 |
| **宣城校区 xc.hfut.edu.cn 校外不可达** | 需校园网或 WebVPN `https://webvpn.hfut.edu.cn`。不是故障，别反复重试 |
| **3 个域名已废弃** | `dqxy`（电气学院已改 `ea`）、`job`、`cxcy` —— DNS 解析到 IPv6 link-local |
| **lib.hfut.edu.cn 校外不可达** | 校内资源，暂不纳入 |
| **多套 CMS 并存** | 详情页两种形态：`/YYYY/MMDD/c{栏}a{id}/page.htm`（网站群，日期嵌在 URL 里）和 `info/{栏}/{id}.htm`（老 CMS）。**通用解析器 `extract_items_generic()` 已按 URL 形态处理，新增栏目优先复用它**，别再写站点专属正则 |
| **旧副本已清理** | 原 `D:\.workbuddy\scripts`（v3.2 独立仓库）已并入本项目 `hfut_site/`，旧归档 `_trash_\2026-09-11` 已于 2026-09-14 清空。**不要再引用该路径**，唯一入口是 `hfut.py` |

---

## 维护要点

1. 单栏目连续失败 ≥2 次会自动跳过；修好后把 `hfut_site/hfut_failed_sites.json` 置为 `{}` 即可让所有栏目重新参与
2. **新增栏目**：改 `hfut_site/hfut_scanner.py` 的 `CHANNELS` 表，格式 `(名称, URL, 域名, 栏目类型, CMS类型, 是否需浏览器)`，解析走通用解析器
3. 邮件用 QQ SMTP 465（SSL），需要**授权码**而非登录密码；配置在 `hfut_site/hfut_email_config.json`
4. 增量扫描基于上次扫描日期向前 3 天缓冲
5. 数据全部本地存储

## 浏览器层：CDP 直连兜底

需要登录态才能访问的栏目（如教务部 jwc.hfut.edu.cn 动态渲染），用 CDP 直连日常浏览器，天然继承登录态：

```bash
node "C:/Users/Matebook/.workbuddy/skills/联网工具箱/scripts/check-deps.mjs"   # 确认 3456 端口在监听
curl -s --noproxy '*' -X POST --data-raw 'https://jwc.hfut.edu.cn/' http://127.0.0.1:3456/new
curl -s --noproxy '*' -X POST "http://127.0.0.1:3456/eval?target=ID" -d 'document.body.innerText.slice(0,2000)'
curl -s --noproxy '*' "http://127.0.0.1:3456/close?target=ID"
```

两个坑：**curl 必须加 `--noproxy '*'`**（本机代理会拦 localhost）；**`/new` 返回 ≠ 内容就绪**，要 sleep 6-8 秒再 eval。

> 完整 CDP 用法见 `联网工具箱/references/CDP浏览器直连.md`。
