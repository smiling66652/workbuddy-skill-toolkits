---
name: 技能包跨机器打包
description: >
  把本机 ~/.workbuddy/skills/ 下的任意技能打包成「另一台电脑解压后双击即用」的离线安装包。
  核心是消除机器专属硬编码（绝对路径 / 托管运行时版本号 / 源机工作目录）并做隔离环境端到端验证。
  触发词：打包技能、技能包迁移、另一个电脑用这个技能、离线安装包、portable skill、导出技能、
  把技能拷到新电脑、技能搬家、跨机器安装、解压就能用、绿色版技能、skill 分发、拷贝 skills。
  不用于：新建/修改技能内容（走 skill-creator）；平时使用某个技能（直接加载即可，不需要打包）；本机内部整理技能库（走 skill-doctor / verify-pack / skill-ref-audit 三件套）
version: 1.0.0
author: WorkBuddy
agent_created: true
---

# 技能包跨机器打包

> **目标**：用户说「我想在另一台电脑上同样用这个技能」时，产出「解压 → 双击 → 可用」的离线包。

---

## ⚡ 首选：直接用通用工具链（2026-09-20 新增）

`scripts/` 下有三个**通用**工具，一条命令打包 + 一条命令验证：

| 工具 | 用法 |
|---|---|
| `pack_skill.py` | `--src <技能目录> --name "<包名>" [--keep-node-modules] [--doc <说明md>] [--reuse-payload] [--dry-run]` |
| `install_template.bat` | install.bat 模板（占位符 `{PKGNAME}` / `{NODE_MISSING_NOTE}`），由 pack_skill.py 转 CRLF + GBK 落盘。**不要手工编辑成品 .bat** |
| `test_install.py` | `--pkg "<包名>" --zip "<zip路径>"`，隔离 USERPROFILE 后跑 install.bat，5 项断言 |

`pack_skill.py` 自动完成：复制 payload（排除 `.git`/`__pycache__`/`.playwright-cli`/`*.pyc`）→ 扫硬编码
（文档类自动改、代码类只报告）→ 生成 install.bat/README.txt/使用说明.md 三件套 → 打 zip 并自检
（UTF-8 名标志、CRLF、GBK 可解码、排除项、关键文件）。

**首次使用前改脚本顶部的 `DEFAULT_BUILDROOT` / `DEFAULT_OUT` 两个常量。**

> ### ★ `--reuse-payload`：保住手工 sanitize
> 重跑 pack_skill.py 会 `rmtree` 整个 stage 再从源目录重拷贝，**会抹掉你在构建区 payload 上做的手工修改**。
> 正确流程是三步：
> **① `--doc` 定稿文档与 install.bat（此时会重建 payload）**
> **→ ② 在构建区 `payload/` 上手改代码类残留**
> **→ ③ 加 `--reuse-payload` 重打包（复用 payload，同时保留已有的使用说明.md）**
>
> 源目录全程只读，绝不直接改 `~/.workbuddy/skills/<包>`。

> 原 `01-sanitize.py` ~ `05-test-install.py` 是**联网工具箱专用**脚本（路径常量写死），保留作参考；
> 新任务一律用上面三个通用工具。

## 本机技能库体检（打包前后必读）

`references/本机技能体检.md` 收录了本机四件体检命令（skill-ref-audit / verify-pack / skill-doctor --fix-index / skill-compliance-audit）：
打包交付前先跑 ref-audit 确认无幽灵引用；技能整合/搬迁后四件全绿才算收口。

## 0. 先侦察，别急着复制

**不同技能的坑完全不同**。先花 5 分钟搞清楚三件事：

```bash
# ① 技能体积构成（判断 node_modules 要不要随包带）
du -sh "<技能目录>"; du -sh "<技能目录>"/node_modules 2>/dev/null

# ② 硬编码路径扫描 —— 这是全部工作的重心
grep -rn "<当前用户名>" "<技能目录>" --include="*.md" --include="*.mjs" --include="*.js" --include="*.py" --include="*.json"

# ③ 运行时脚本如何定位自身？（决定可移植性天花板）
grep -rn "import.meta.url\|__dirname\|os.homedir()\|process.env.USERPROFILE\|process.env.LOCALAPPDATA" "<技能目录>"/scripts
```

**判据**：若脚本用 `import.meta.url` / `os.homedir()` 定位 → **运行时已可移植**，
硬编码只污染在文档、注释、提示文本里，替换字符串即可。
若脚本写死了绝对路径 → 必须先改代码逻辑，不能只做文本替换。

---

## 1. 四类硬编码检查表（逐项过）

| # | 类别 | 典型形态 | 正确处理 |
|---|---|---|---|
| 1 | **技能自身路径** | `<用户目录>/.workbuddy/skills/<技能名>/scripts/<脚本>.mjs` | → **相对路径** `scripts/<脚本>.mjs`，并在 SKILL.md 顶部加「路径约定」说明相对基准 |
| 2 | **托管运行时** | `.../binaries/node/versions/22.22.2-2/node.exe` | → `node`（走 PATH）；代码内用 `os.homedir()` 推导。**禁止写死版本号**（同机都可能并存多版本） |
| 3 | **源机工作目录** | 默认下载目录 `D:/桌面/电子书/_downloads` | 代码默认值 → `path.join(os.homedir(), 'Downloads', '...')`；文档示例 → `$USERPROFILE/...` |
| 4 | **源机专属工具/快照** | `tools/xxx.py`、本机工具状态表 | 文档加注「源机快照，换机即失效」；外部工具改写成「需自行安装」 |

**校验**：替换后必须复检为 0 残留 ——

```python
pat = re.compile(r"<用户名>|\$HOME/|C:\\\\Users\\\\")
# 遍历技能目录（排除 node_modules/.git），逐行匹配，要求命中 0
```

> ⚠️ 文档里**刻意保留**的说明文字（如"不要用 `$HOME` 拼路径"）会命中 grep，属正常，需人工判断。

---

## 2. ★ 七个必踩的坑（每个都让包直接失效）

### 坑 1：`.bat` 必须是 CRLF

Write 工具和 `Path.read_text()` 都会把行尾归一化为 LF。**纯 LF 的 bat 在 cmd 下会崩**：
`if (...)` 括号块解析错位，块内的中文 `echo` 行被当成独立命令执行，报
`'，且本文件与payload' 不是内部或外部命令`（症状：安装脚本刚开头就退出，输出为空）。

```python
def to_crlf(text): 
    return text.replace("\r\n", "\n").replace("\n", "\r\n")
```

打包脚本里加自检：`assert bat_bytes.count(b"\r") == bat_bytes.count(b"\n") > 0`

### 坑 2：`$HOME` / `~` 不能拼路径传给原生程序

Git Bash 把 `$HOME` 展开成 `/c/Users/x`（MSYS 路径），而 `node.exe` / `curl.exe` / `python.exe`
是原生 Windows 程序，把 `/c/Users/<用户名>` 理解成 `d:\c\Users\<用户名>`（当前盘符 + 路径），报
`Error: Cannot find module 'd:\c\Users\...'`。

| 写法 | Git Bash | 说明 |
|---|---|---|
| `node "$HOME/x/y.mjs"` | ❌ | 展开成 MSYS 路径，原生程序不认 |
| `node "$USERPROFILE/x/<脚本>.mjs"` | ✅ | `$USERPROFILE` = `C:\Users\<用户名>`，原生程序认 |
| `cd "$USERPROFILE/x" && node y.mjs` | ✅ **推荐** | 先 cd 再相对路径，最稳 |

**因此**：文档里的命令统一改成「先 `cd` 进技能根目录 + 相对路径」两步式，
并在 SKILL.md 顶部写清三种 shell 的 cd 写法（Git Bash / CMD / PowerShell）。

### 坑 3：中文 `.bat` 用 GBK 编码，不用 UTF-8

cmd 默认代码页 936（中文系统）：
- UTF-8 **无 BOM** → 中文乱码
- UTF-8 **带 BOM** → 首行 `@echo off` 前多出 `ï»¿`，命令解析失败
- ✅ **GBK 编码 + 开头 `chcp 936 >nul`** → 中文正确显示

```python
bat_text = to_crlf(src)               # 先 CRLF
(STAGE / "install.bat").write_bytes(bat_text.encode("gbk"))   # 再 GBK
```

配套：`.md` / `.txt` 说明文件用 **UTF-8 with BOM**（记事本可直接正确打开）。

---

### 坑 4：`.bat` 里的外部命令要用绝对路径（否则被 Git Bash 劫持，假死）

在**测试环境**（测试进程的 PATH 继承自 Git Bash）里跑 install.bat，`find` 会解析到 `/usr/bin/find`
（GNU find），而 MSYS 又把 `/c` 参数转成 `C:\` —— 于是 `find /c /v ""` 变成「递归遍历整个 C 盘」，
**脚本假死，看起来像卡在自检那一步，实际在扫全盘**。

```bat
rem ❌ 会被 Git Bash 的 GNU find 劫持
for /f %%c in ('dir /b /s /a-d "%DEST%" ^| find /c /v ""') do set "N=%%c"

rem ✅ 用绝对路径，两种环境都稳
for /f %%c in ('dir /b /s /a-d "%DEST%" ^| "%SystemRoot%\System32\find.exe" /c /v "") do set "N=%%c"
```

同理 `where` → `"%SystemRoot%\System32\where.exe"`。`dir`/`move`/`mkdir` 是 cmd 内部命令，不受影响。
（`install_template.bat` 已按此修好。）

### 坑 5：同一文件并行发多个 Edit 会**静默覆盖**

批量改脚本时，如果在**一条消息里**对同一个文件发多个 Edit，后执行的会基于旧内容写回，
前面几处修改直接消失，而且工具会报 `success`。改完必须 `grep` 复检是否真的落盘。

**规则：同一文件的多个编辑必须串行；不同文件才能并行。**

### 坑 6：脚本语法校验会污染 payload

改完 `.py` 跑 `py_compile` 校验时会在脚本旁生成 `__pycache__/`，它会跟着 payload 进 zip。
校验完必须删掉构建区 payload 里的 `__pycache__`，再重跑打包。`pack_skill.py` 的 zip 自检会报出混入项。

### 坑 7：改完代码要重跑打包

`pack_skill.py` 打包的是**构建区副本**，不是源目录。任何手改都在副本上，改完不重跑 = zip 里还是旧的。

## 3. 包结构（「点点就能用」的形态）

```
<技能名>-离线安装包/
├── install.bat          ← 用户双击这个（GBK + CRLF，纯 ASCII 文件名）
├── README.txt           ← 简版三步说明（UTF-8 BOM）
├── 使用说明.md           ← 完整说明（安装位置/首启必做/命令速查/FAQ/差异说明）
└── payload/             ← 全 ASCII 目录名，装的是技能本体
    ├── SKILL.md
    ├── node_modules/    ← 随包带，实现"零联网依赖"
    └── ...
```

### install.bat 五步骨架

1. 找 Node（先 `where node`，再扫 `%USERPROFILE%\.workbuddy\binaries\node\versions\` 取最新）
2. 备份已有旧版（`move` 到 `_backup_<random>`，失败则提示"先退出 WorkBuddy"）
3. `xcopy /E /I /H /Y /Q` 复制，复制后校验 `SKILL.md` 存在
4. 校验依赖（`node_modules/playwright/cli.js` 在则秒过；不在才 `npm install`）
5. 跑技能自带 `doctor.mjs --quick` 自检 → 最后 `pause` 让用户看清

> `chcp 65001` 只包住 doctor 那一次调用（Node 输出 UTF-8），前后恢复 936。

---

## 4. 打包 zip

用 Python `zipfile`（**中文文件名自动带 UTF-8 flag**，实测 Windows 资源管理器
`Expand-Archive` 解压不乱码）：

```python
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for p in sorted(STAGE.rglob("*")):
        if p.is_file():
            zf.write(p, (Path(PKG_NAME) / p.relative_to(STAGE)).as_posix())
```
打包后自检 `info.flag_bits & 0x800`，要求非 ASCII 条目全部带标志。

---

## 5. ★ 端到端验证（不可跳过）

**隔离 `USERPROFILE` 模拟新电脑，绝不碰真实技能目录**：

```python
env = dict(os.environ)
env["USERPROFILE"] = r"D:\_nt_test\fakehome"     # 关键：隔离
env["TEMP"] = env["TMP"] = r"D:\_nt_test\tmp"
subprocess.run(["cmd", "/c", "install.bat"], cwd=str(PKG),   # cwd 传中文路径更稳
               env=env, input=b"\r\n", capture_output=True, timeout=420)
```

验证清单（缺一不可）：
- [ ] `install.bat` 五步全跑完，**中文输出无乱码**（GBK 解码读取它的 stdout）
- [ ] 目标目录文件数 == payload 文件数
- [ ] **安装后残留扫描 0 处**（无用户名、无 `$HOME/`、无 `C:\Users\`）
- [ ] 在隔离目录跑 `node <DEST>/scripts/doctor.mjs --quick` 成功（证明能用 `import.meta.url` 自定位）
- [ ] 从最终 zip 重新解压再测一遍（测的是交付物本身，不是构建目录）
- [ ] 确认**源机真实技能目录未被改动**（比对 SKILL.md 字节数/mtime）

> PowerShell `Expand-Archive` 要用 PowerShell 工具跑（Bash 内调 PowerShell 会被安全策略拦截）。

---

## 6. 收尾

1. 清理测试目录与 `__pycache__`（`py_compile` 会污染 payload）
2. `present_files` 展示 zip + 解压目录
3. 交付说明里必须写清的差异项：日常浏览器（改 `config.env` 一行）、Python 依赖（可选）、
   登录态（每台机独立）、站点可达性（源机经验不通用）

---

## 附：本次实战参数（联网工具箱，2026-09-17）

| 项 | 值 |
|---|---|
| 源 | `~/.workbuddy/skills/联网工具箱`（348 文件，含 .git/node_modules） |
| 包 | 257 条目 / 4.4 MB（payload 254 文件 / 解压 19 MB） |
| 清除硬编码 | 41 处绝对路径 + 12 处托管运行时 + 15 处 D 盘工作路径 |
| 验证 | 隔离安装全通、0 残留、doctor 独立运行成功 |

构建脚本模板见 `scripts/`（`sanitize` / `build` / `test_install`），**需改顶部的路径常量**。
