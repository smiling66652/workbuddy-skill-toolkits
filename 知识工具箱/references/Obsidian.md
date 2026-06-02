---
name: 二级：Obsidian管理
---

# 二级：Obsidian管理

**适用场景**：管理Obsidian笔记库、创建/编辑笔记、批量操作

---

## 工具对比

| 工具 | 速度 | 批量操作 | 推荐场景 |
|------|------|---------|------------|
| **Obsidian CLI** | 快 | ✅ | 命令行操作（推荐） |
| **直接操作Markdown文件** | 非常快 | ✅ | 简单读写 |
| **Obsidian API（社区插件）** | 中 | ❌ | 需要Obsidian运行时 |

---

## 三级执行：Obsidian CLI（推荐）

**触发词**：Obsidian笔记、创建笔记、搜索Obsidian、编辑Obsidian

### 安装

```bash
# 安装 Obsidian CLI
npm install -g obsidian-cli

# 验证安装
obsidian --version
```

### 使用

```bash
# 创建新笔记
obsidian create "笔记标题"

# 打开笔记
obsidian open "笔记标题"

# 搜索笔记
obsidian search "关键词"

# 列出所有笔记
obsidian list

# 删除笔记
obsidian delete "笔记标题"

# 追加内容到笔记
echo "新内容" >> "Vault路径/笔记标题.md"

# 用Agent直接读写Markdown文件
# （Obsidian vault 就是一堆Markdown文件）
```

---

## 三级执行：直接操作Markdown文件（简单高效）

**触发词**：读写Obsidian笔记、批量修改Obsidian

### 读取笔记

```python
# 读取单个笔记
with open("Vault路径/笔记标题.md", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

### 创建/更新笔记

```python
# 创建新笔记
note_content = """---
title: 笔记标题
tags: [tag1, tag2]
---

# 笔记标题

这是正文内容。
"""

with open("Vault路径/笔记标题.md", "w", encoding="utf-8") as f:
    f.write(note_content)
```

### 批量操作

```python
import os
import re

vault_path = "Vault路径"

# 批量读取所有笔记
for filename in os.listdir(vault_path):
    if filename.endswith(".md"):
        with open(os.path.join(vault_path, filename), "r", encoding="utf-8") as f:
            content = f.read()
            # 处理内容
            print(f"{filename}: {len(content)} 字符")

# 批量替换文字
for filename in os.listdir(vault_path):
    if filename.endswith(".md"):
        filepath = os.path.join(vault_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("旧文字", "新文字")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
```

---

## 使用建议

1. **简单读写** → 直接操作Markdown文件（最快）
2. **需要Obsidian命令** → 用 Obsidian CLI
3. **批量操作** → Python脚本直接处理
4. **Vault路径** → 通常是 `C:/Users/Matebook/Documents/Obsidian Vault/`
5. **Frontmatter** → Obsidian笔记顶部的 `---` 之间是YAML元数据

---

## 注意事项

- **路径中含有空格** → 用引号包裹路径
- **编码问题** → 始终用 `utf-8` 编码
- **Frontmatter** → 不要随意修改顶部 `---` 之间的内容
- **双向链接** → Obsidian使用 `[[笔记标题]]` 格式，保留它们
