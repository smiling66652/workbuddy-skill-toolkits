---
name: git-ship
description: |
  把看改动、写规范中文 commit message、提交、推远端、需要时开 PR 串成一条龙；提交前强制做密钥安全检查。
  触发词：提交并推送、一键提交、git 提交推送、开 PR、提交代码、ship it、git-ship、提交前检查
version: "1.0.0"
author: smiling66652
---

# 提交并推送一条龙（git-ship）

> 用途：保研作品集频繁提交，避免“手快把 .env 推上去”的事故。本技能**先安全检查，再提交推送**，最后按需开 PR。

## 执行步骤

### 第 0 步：密钥安全检查（必须，不过就 abort）

先 `git status -s` 看有哪些改动，再用下面命令扫描**将纳入提交**的文件中是否含密钥/凭证：

```bash
git add -A -N                      # 让 untracked 文件进入待检范围但不真正暂存
git diff --cached --name-only      # 列出将要提交的文件
git diff --cached -G "password|secret|token|api[_-]?key|access[_-]?key|私钥|AKID" --name-only
```

同时按文件名拦截敏感文件：

```bash
git diff --cached --name-only | grep -iE "\.env|config\.json|\.pem|\.key|id_rsa|credentials|\.tfvars|token"
```

**若上面任一命令有输出 → 立即中止**，把命中的文件加入 `.gitignore` 或用 `git reset HEAD <文件>` 取消暂存，并提醒用户：密钥一旦推送，必须轮换，后果严重。

### 第 1 步：看改动

```bash
git status -s
git diff --stat
git diff --cached --stat
```

据此判断本次改动属于哪类（见下方 commit 类型表），并决定 commit 范围（建议按功能 `git add <具体文件>`，少用 `git add -A`）。

### 第 2 步：写规范中文 commit message

格式（参考 Conventional Commits，描述用中文）：

```
<type>(<scope>): <中文简述>

<可选正文：为什么改、怎么改>

<可选> BREAKING CHANGE: <破坏性说明>
```

type 取值：

| type | 含义 |
|---|---|
| feat | 新功能 |
| fix | 修 bug |
| docs | 文档/注释 |
| style | 格式（不改逻辑） |
| refactor | 重构 |
| perf | 性能 |
| test | 测试 |
| chore | 构建/依赖/杂务 |

示例：`feat(登录): 接入 wx.login 完成小程序授权`；`fix(api): 修复 token 过期未刷新导致 401`。

### 第 3 步：提交

```bash
git add <具体文件或目录>
git commit -m "feat(登录): 接入 wx.login 完成小程序授权"
```

若用户要求补全正文，用多行 `-m` 或编辑器提交。

### 第 4 步：推远端

```bash
git push
# 首次推送远程没有的分支：
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

推送前确认当前分支名合理（feature/xxx、fix/xxx 最佳）。

### 第 5 步：需要时开 PR

若目标仓库在 GitHub 且配有 `gh`，且当前不是 main/master：

```bash
gh pr create --title "feat(登录): 接入 wx.login" --body "$(git log --since='1 week ago' --pretty=format:'- %s')"
```

若未装 `gh` 或仓库非 GitHub，改为提示用户去网页端手动开 PR，并附上本次提交摘要。

## 输出格式

完成后给用户一句确认 + 关键信息：

```
✅ 已提交并推送
分支: feature/login  →  origin/feature/login
提交: a1b2c3d feat(登录): 接入 wx.login 完成小程序授权
PR:   https://github.com/xxx/yyy/pull/12  (已创建)
```

未开 PR 时写明原因（非 GitHub / 未装 gh / 已在 main 分支直接推送）。

## 注意事项

1. **安全检查不可跳过**：宁可多一步确认，也别把 `.env`、`config.json`、`*.pem` 推到远端。
2. 推送前用 `git status` 二次确认工作区干净、无遗漏文件。
3. 不要 `git commit --no-verify` 绕过钩子，除非用户明确要求。
4. 一次提交只做一件事，方便 reviewer 和日后 `git bisect`。
5. 微信小程序项目注意 `project.config.json` 里的 AppID 是否误提交；私有 appid 建议放本地配置忽略。
