---
name: 开发工具箱
description: >
  统一开发工具箱（三级层级结构）：
  一级：分析开发需求（GitHub/代码审查/测试/Flutter/Android/前端/MCP）
  二级：选择最佳工具（gh CLI/Semgrep/pytest/Flutter CLI/Android Studio/React/Vue/FastMCP）
  三级：执行指令并返回结果。
  集成最佳工具：GitHub CLI、Semgrep、pytest、Flutter、React、Vue、FastMCP。
version: 4.0.0
author: WorkBuddy 整合版（集成 github/code-review/test-generator/flutter-dev/android-native-dev/frontend-dev/impeccable/mcp-builder）
---

# 开发工具箱

> **三级层级调用规则**：
> 1. **一级：需求分析** — 判断用户要做什么（GitHub/代码审查/测试/跨平台/原生/前端/MCP）
> 2. **二级：工具选择** — 根据需求选择最佳工具（见下方快速选择指南）
> 3. **三级：执行指令** — 调用工具并返回结果

---

## 快速选择指南

| 用户需求 | 跳转二级 | 推荐工具 |
|---------|---------|---------|
| 管理GitHub仓库、Issues、PR | [二级：GitHub操作](references/GitHub操作.md) | `gh` CLI |
| 审查代码安全/性能 | [二级：代码审查](references/代码审查.md) | Bandit、Semgrep、pylint |
| 生成单元测试/集成测试/E2E | [二级：测试生成](references/测试生成.md) | pytest、Playwright |
| 开发Flutter跨平台应用 | [二级：Flutter开发](references/Flutter开发.md) | Flutter SDK + Dart |
| 开发Android原生应用 | [二级：Android原生](references/Android原生开发.md) | Kotlin + Compose |
| 开发前端React/Vue应用 | [二级：前端开发](references/前端开发.md) | React/Vue + Vite |
| 创建MCP服务器 | [二级：MCP开发](references/MCP开发.md) | FastMCP（Python）或 MCP SDK（TypeScript） |

---

## 一级：需求分析

**触发词分类**：

| 需求类型 | 触发词示例 | 跳转二级 |
|------------|------------|------------|
| GitHub仓库管理 | GitHub、Issues、PR、合并请求、CI、pipeline | [二级：GitHub操作](references/GitHub操作.md) |
| 代码审查 | 审查代码、code review、这个PR有什么问题 | [二级：代码审查](references/代码审查.md) |
| 测试生成 | 生成测试、写单测、测试覆盖、单元测试 | [二级：测试生成](references/测试生成.md) |
| Flutter开发 | Flutter、跨平台、Widget、Riverpod | [二级：Flutter开发](references/Flutter开发.md) |
| Android开发 | Android、Kotlin、Compose、Material3 | [二级：Android原生](references/Android原生开发.md) |
| 前端开发 | 前端、React、Vue、组件、页面 | [二级：前端开发](references/前端开发.md) |
| MCP开发 | 开发MCP、创建MCP服务器、MCP开发指南 | [二级：MCP开发](references/MCP开发.md) |

---

## 通用规则

### Git 工作流

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

### 代码风格

- **Python**：遵循 PEP 8（用 `ruff` 或 `black` 格式化）
- **JavaScript/TypeScript**：遵循 ESLint 规则（用 `prettier` 格式化）
- **Kotlin**：遵循官方代码规范（用 `ktlint` 检查）
- **Dart**：遵循 Effective Dart（用 `dart format` 格式化）

---

## References

| 文件 | 何时读取 |
|------|------------|
| `references/GitHub操作.md` | 需要管理GitHub仓库、Issues、PR时 |
| `references/代码审查.md` | 需要审查代码安全、性能、可维护性时 |
| `references/测试生成.md` | 需要生成单元测试、集成测试、E2E测试时 |
| `references/Flutter开发.md` | 需要开发Flutter跨平台应用时 |
| `references/Android原生开发.md` | 需要开发Android原生应用时 |
| `references/前端开发.md` | 需要开发前端React/Vue应用时 |
| `references/MCP开发.md` | 需要开发MCP服务器时 |

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| `gh auth status` 显示未认证 | 运行 `gh auth login` |
| 代码审查工具未找到 | 运行 `pip install bandit semgrep pylint` |
| 测试运行失败 | 检查测试框架安装，运行 `pip install pytest` |
| Flutter 命令未找到 | 将 Flutter bin 目录添加到 PATH |
| Android Studio 未找到 SDK | 在 IDE 中配置 SDK 路径 |
| Node.js 版本不兼容 | 使用 `nvm` 切换版本 |
| MCP 服务器启动失败 | 检查 `command` 和 `args` 是否正确 |

---

## 注意事项

1. **安全性** — 不要在代码中硬编码 API Key、密码等敏感信息
2. **版本控制** — 使用 Git 进行版本控制，遵循分支策略
3. **测试先行** — 先写测试或同时写测试，确保代码质量
4. **文档同步** — 代码变更时同步更新文档
5. **依赖管理** — 定期更新依赖，修复安全漏洞
