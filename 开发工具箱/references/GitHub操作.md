---
name: GitHub操作
description: GitHub仓库管理、Issues、PR、CI/CD操作指南
---

# 二级：GitHub操作

**适用场景**：用户需要管理GitHub仓库、创建Issue、提交PR、配置CI/CD等。

---

## 三级执行：GitHub CLI 操作

### 安装 GitHub CLI

```bash
# Windows (Scoop)
scoop install gh

# Windows (WinGet)
winget install --id GitHub.cli

# 验证安装
gh --version
```

### 认证登录

```bash
# 交互式登录
gh auth login

# 查看认证状态
gh auth status

# 配置Git使用gh凭证助手
gh auth setup-git
```

---

## 仓库管理

### 创建仓库

```bash
# 创建新仓库（当前目录）
gh repo create my-repo --public

# 从现有目录创建
gh repo create owner/repo-name --private --source=. --push

# 克隆仓库
gh repo clone owner/repo-name
```

### 仓库设置

```bash
# 查看仓库设置
gh repo view --json visibility,defaultBranchRef

# 修改仓库可见性
gh repo edit --visibility private

# 启用Issues/Projects/Wiki
gh repo edit --enable-issues --enable-projects --enable-wiki
```

---

## Issues 管理

### 创建Issue

```bash
# 交互式创建
gh issue create

# 命令行创建
gh issue create --title "Bug: 登录失败" --body "详细描述..." --label bug --assignee username

# 从模板创建
gh issue create --template bug_report.md
```

### 查看/更新Issue

```bash
# 列出Issues
gh issue list
gh issue list --state open --label bug

# 查看单个Issue
gh issue view 123

# 更新Issue
gh issue edit 123 --title "新标题" --add-label enhancement

# 关闭Issue
gh issue close 123 --reason "fixed"
```

### 评论Issue

```bash
# 添加评论
gh issue comment 123 --body "已修复，请验证"

# 编辑评论
gh issue comment 123 --edit 456 --body "更新后的评论"
```

---

## Pull Request 管理

### 创建PR

```bash
# 从当前分支创建PR
gh pr create --title "功能：添加登录模块" --body "实现了..." --base main

# 交互式创建
gh pr create

# 草稿PR
gh pr create --draft
```

### 查看/更新PR

```bash
# 列出PRs
gh pr list
gh pr list --state open --author username

# 查看PR详情
gh pr view 456

# 更新PR
gh pr edit 456 --title "新标题" --add-label review-needed

# 合并PR
gh pr merge 456 --squash --delete-branch
```

### Review PR

```bash
# 查看需要review的PR
gh pr list --review-requested username

# Approve PR
gh pr review 456 --approve --body "LGTM!"

# 请求修改
gh pr review 456 --request-changes --body "需要修复：..."

# 添加评论
gh pr comment 456 --body "建议优化这里的性能"
```

---

## CI/CD 管理

### Actions 工作流

```bash
# 列出workflows
gh workflow list

# 查看workflow运行历史
gh run list

# 查看特定run详情
gh run view 123456

# 重新运行失败的workflow
gh run rerun 123456

# 取消运行中的workflow
gh run cancel 123456
```

### 部署管理

```bash
# 查看部署环境
gh deployment list

# 创建部署
gh deployment create --environment production --ref main
```

---

## 最佳实践

### 分支策略

```
main (生产)
  ├── develop (开发)
       ├── feature/xxx (功能分支)
       ├── bugfix/xxx (修复分支)
       └── hotfix/xxx (热修复)
```

### Commit 规范

```bash
# 使用约定式提交
feat: 添加用户登录功能
fix: 修复首页加载失败
docs: 更新API文档
test: 添加登录模块测试
refactor: 重构用户服务
```

### PR 模板

创建 `.github/pull_request_template.md`：

```markdown
## 变更说明
- 

## 关联Issue
Closes #

## 测试计划
- [ ] 单元测试通过
- [ ] 手动测试完成
- [ ] CI/CD通过

## 截图（如有）
```

---

## 与 WorkBuddy 集成

### 自动化流程

```bash
# 创建Issue并自动分配
gh issue create --title "TODO: 实现XX功能" --assignee @me

# 创建PR并请求review
gh pr create --reviewer username --base main

# 合并后自动关闭Issue
gh pr merge --auto --delete-branch
```

### 与 MCP 集成

如果使用 `github` MCP服务器：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| `gh auth status` 显示未认证 | 运行 `gh auth login` |
| PR创建失败（权限不足） | 检查token权限或fork仓库 |
| Actions运行失败 | 查看 `gh run view --log` |
| 合并冲突 | 本地 `git pull --rebase` 解决后推送 |
| 无法push | 运行 `gh auth setup-git` |

---

## 注意事项

1. **Token安全** — 不要在代码中硬编码 `GITHUB_TOKEN`
2. **分支保护** — 重要分支启用保护规则（禁止force push、需要review）
3. **CI/CD成本** — GitHub Actions有免费额度限制
4. **敏感信息** — 使用Secrets存储API Key等敏感信息
