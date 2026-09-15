---
name: yuketang-harvester
version: "1.0.0"
description: 批量归档长江雨课堂（changjiang.yuketang.cn）全部课程的课件——课表枚举、课件文字层提取、页图批量下载、讲义装配。当用户提到雨课堂、长江雨课堂、下载课件、课程归档、讲义整理、复习资料、课件转 PDF 时触发。
whenToUse: 用户需要把自己在长江雨课堂上的课程课件批量下载到本地、整理成可搜索的讲义，或为期末复习批量准备材料时
type: prompt
agent_created: true
---

# 长江雨课堂全课程课件归档

把自己账号里**所有课程**的课件批量抓到本地，整理成「可搜索讲义 + 页图 + 大纲」。

**边界：只做读取与个人学习归档。不实现自动签到、不伪造学习时长、不自动答题。**

---

## 前置条件

1. **本机浏览器已登录** `changjiang.yuketang.cn`（必须是用户自己已登录的浏览器）。
2. **CDP Proxy 已运行**：`http://127.0.0.1:3456`
   - 启动方式见 `联网工具箱` skill（用它自带的 check-deps 脚本拉起）
   - ⚠️ 必须后台常驻启动，否则命令结束进程会被回收：
     ```bash
     cd "C:/Users/Matebook/.workbuddy/skills/联网工具箱" && node scripts/cdp-proxy.mjs
     ```
     用 `run_in_background: true` 启动。
3. **Bash 沙箱会拦回环**：所有 curl 到 `127.0.0.1:3456` 必须加 `dangerouslyDisableSandbox: true` + `--noproxy '*'`。
4. 本机 Bash 的 `mkdir/cat/head/ls/grep/sleep` 不可用 → 建目录用 PowerShell `New-Item`，写文件用 Write 工具。

---

## 执行流程

设 `SKILL` = 本技能目录，`OUT` = 输出根目录（默认 `D:/桌面/浏览器/yuketang-research`）。
脚本里的 `OUT` 常量需要按实际项目调整。

```bash
# 1) 建索引：课程 → 课时 → 课件
node "<SKILL>/scripts/harvest-all.mjs" index

# 2) 双通道抓课件：
#    通道A  presentation/fetch            → 有 shapes[].Text（新课程）
#    通道B  lesson-summary/.../presentation → 只有 cover 页图（旧课程）
node "<SKILL>/scripts/harvest-v2.mjs"

# 3) 下载"页图型"课件的全部页图 → courseware/<课程>__<cid>/<课件名>/p###.jpg
node "<SKILL>/scripts/dl-all-slides.mjs" [课程关键词]

# 4) 装配：每门课一份讲义 + 大纲 + 全局总览
node "<SKILL>/scripts/assemble-v2.mjs"

# 5)（可选）对页图型课件做 OCR，产出可搜索文字
python "<SKILL>/scripts/ocr-courseware.py" [课程关键词]
```

---

## 关键接口（实测，2026-09-14）

鉴权二选一，**两种都通**：

| 方式 | 请求头 |
|---|---|
| Bearer（推荐，浏览器内 fetch 直接用） | `Authorization: Bearer <localStorage.Authorization>`、`X-Client: h5`、`xtbz: ykt` |
| 纯 Cookie（脱离浏览器跑脚本时用） | Cookie `sessionid`+`csrftoken`+`uv_id`+`university_id`+`xtbz`；头 `x-client: web`、`xt-agent: web` |

> 注意 `localStorage.Authorization` 的值**不含** `Bearer ` 前缀，要自己拼。

| 步骤 | 端点 |
|---|---|
| 课程列表 | `GET /v2/api/web/courses/list?identity=2` |
| **课时列表** | `GET /v2/api/web/logs/learn/{classroomId}?actype=-1&page=0&offset=100&sort=-1` → 取 `data.activities[]` 中 `type===14`，其 `courseware_id` 即 lessonId |
| **课件清单** | `GET /api/v3/lesson-summary/student?lesson_id={lessonId}` → `data.presentations[]`（含 `slidesCount`） |
| 课件文字层 | `GET /api/v3/lesson/presentation/fetch?presentation_id={pid}` → `data.slides[].shapes[].Text` |
| 课件页图 | `GET /api/v3/lesson-summary/student/presentation?presentation_id={pid}&lesson_id={lid}` → `data.slides[].cover`（**缺 lesson_id 会 500**） |
| 官方打印页 | `https://changjiang.yuketang.cn/web/print`（无参，一次渲染全部页，**1280×960 比 API 更清晰**；数据源 `localStorage.rain_print`） |

---

## 已知坑（务必先读）

| # | 坑 | 说明 |
|---|---|---|
| 1 | **`403` 不能证明端点存在** | `/api/v3/lesson/<任意未知>` 都返回 403（前缀门禁）。判断存在性要先编假路径做对照；`/api/v3/foobar/*` 才返回 404 |
| 2 | **`200` 不等于有内容** | `/v2/api/web/` 下带 `classroom_id` 的未知路径统一返回桩 `{"2688":<id>}` |
| 3 | **旧学期课件没有文字层** | 2026 春及更早的课件，`presentation/fetch` 返回业务码 **`50009 PRESENTATION_NOT_FOUND`**（HTTP 仍是 200！）→ 必须回退到通道 B 取页图 |
| 4 | 页图 `cover<N>` 的 **N 不是页码** | 必须按返回的 `index` 排序，不能自己拼 URL |
| 5 | 页图 token **约 1 小时过期** | 取 URL 与下载要连着做，不要缓存 URL |
| 6 | 页图**免 Cookie 可下** | 签名通过即可，可交给下载器 |
| 7 | Bash `mkdir/ls/cat/head/grep/sleep` 全缺 | 用 PowerShell / Write 工具替代 |
| 8 | 长 JS 传给 `/eval` 转义地狱 | 先用 Write 落盘，再 `--data-binary "@D:/绝对路径"` |

---

## OCR 卡点（未解决，下次从这里继续）

`rapidocr-onnxruntime 1.2.3` 依赖 **numpy 1.x**（`numpy.core.multiarray`），但 numpy 1.26 没有 **Python 3.13** 的预编译包，源码编译在 meson/VS 环境处失败。

可选解法（按推荐度）：
1. **用 Python 3.11/3.12 建独立 venv 跑 OCR**（最稳，`install_binary` 装 3.12）
2. 换用新版 `rapidocr`（v2，支持 numpy 2）
3. 用 Windows 内置 OCR（`Windows.Media.Ocr`，零安装，需中文语言包）
4. 改用视觉模型直接读页图（不做 OCR）

---

## 输出结构

```
<OUT>/
├── harvest/
│   ├── index.json            课程→课时→课件 索引
│   └── slides/{pid}.json     每个课件（mode: text | image）
├── courses/
│   ├── <课程>__<cid>-讲义.md   文字型：逐页文字；页图型：页图清单
│   ├── <课程>__<cid>-大纲.txt  每页首句拼成的骨架
│   └── <课程>__<cid>-OCR.md   OCR 结果（若已跑）
├── courseware/<课程>__<cid>/<课件名>/p###.jpg
└── 08-全课程课件采集总览.md
```

---

## 合规

- ✅ 读取自己账号可见数据、归档自己所学课程、个人学习使用
- ❌ 自动签到、伪造学习时长、自动答题、代考、对外分发课件
- 课件版权归**合肥工业大学与授课教师**所有，仅限个人学习
