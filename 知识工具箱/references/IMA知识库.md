# 二级：IMA 知识库 —— 已降级为指针

> **2026-09-15 变更**：本文件原为 IMA 知识库操作的本地实现说明，经比对确认是
> **`ima-skills` 技能（供应商权威实现，v1.1.9）的简化子集**，且缺少权威版已有的关键内容，
> 因此降级为指针，不再维护副本（避免上游升级后副本漂移）。

## 要做 IMA 相关操作时

**加载 `ima-skills` 技能**（`C:\Users\Matebook\.workbuddy\skills\ima-skills\`）。

权威版比本副本**多**这些内容（都是实用项）：

| 权威版独有 | 说明 |
|---|---|
| ⚠️ **PowerShell 5.1 GBK 静默转码坑** | 本机是 Windows + PS 5.1，这个坑**必须**看权威版；本副本没有 |
| 版本检测 + UTF-8 字节数组发送模板 | 规避上面那个坑的具体写法 |
| 内建每日更新检查 | `-200` 码触发更新指引，技能会随上游自我演进 |
| 两层错误处理 | `-100` 程序错误 / `-200` 需更新 |
| 凭证优先级 | 环境变量 → `~/.config/ima/` 配置文件 |

权威版已完整覆盖：UTF-8 校验铁律、文件名=标题、不支持类型（视频/B站/YouTube/`file://`）拒绝上传、
二进制原样上传、路由速查表、`import_doc` / `append_doc` / `get_doc_content` / `add_knowledge media_type=11` 等命令、
跨模块任务需同时读两个子模块。

## 仅在「不走 wrapper」时才需要的两条（本副本独有，已保留备查）

若将来确实需要**绕开 `ima_api.cjs` 包装、直连 IMA OpenAPI**（更脆弱、无错误处理与更新机制，不推荐）：

- 原始 REST 端点：`/api/v1/upload`、`/api/v1/add_url`、`/api/v1/search`（用 Python `requests` 直调）
- ~~IMA MCP 安装：`npm install -g @ima/mcp-server`~~ —— **2026-09-15 核实：npm 上不存在该包（404）**，此路已失效；要连 IMA 请直接用 `ima-skills`

> 原文件完整内容已备份至 `D:\_trash_\2026-09-15\知识工具箱-references\IMA知识库.md`。
