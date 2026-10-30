---
displayName: "网页设计指南"
version: "1.0.0"
slug: web-design-guidelines
name: web-design-guidelines
agent_created: true
description: |
  Vercel 官方《Web Interface Guidelines》评审入口：运行时从 GitHub 拉取最新版规则
  （vercel-labs/web-interface-guidelines），逐条比对指定文件并输出 file:line 形式的问题清单。
  触发词：网页设计指南、web interface guidelines、界面规范审查、Vercel规范、
  审查UI代码、检查可访问性、审计设计、审查UX、检查我的网站、交付前规范体检、逐条比对
  不用于：创意方向（走 frontend-design-guidelines）；设计基础（走 ui-design）
  注意：需联网抓取 raw.githubusercontent.com，离线时本技能不可用。
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
