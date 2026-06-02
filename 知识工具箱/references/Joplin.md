---
name: 二级：Joplin管理
---

# 二级：Joplin管理

**适用场景**：管理Joplin笔记、创建/编辑笔记、同步笔记

---

## 工具对比

| 工具 | 速度 | 批量操作 | 推荐场景 |
|------|------|---------|------------|
| **Joplin API** | 中 | ✅ | 程序化操作（推荐） |
| **Joplin CLI** | 快 | ✅ | 命令行操作 |
| **直接操作数据库** | 非常快 | ✅ | 高级用户 |

---

## 三级执行：Joplin API（推荐）

**触发词**：Joplin笔记、创建Joplin笔记、搜索Joplin

### 前置条件

需要 Joplin 的 Web Clipper 服务端口（默认 41184）

### 使用

```python
import requests

# 基础URL
base_url = "http://localhost:41184"

# 获取所有笔记
response = requests.get(f"{base_url}/notes")
notes = response.json()
for note in notes:
    print(f"{note['id']}: {note['title']}")

# 创建新笔记
new_note = {
    "title": "新笔记标题",
    "body": "# 笔记标题\n\n这是正文内容。",
    "parent_id": "",  # 笔记本ID，空字符串表示根目录
}
response = requests.post(f"{base_url}/notes", json=new_note)
print(f"创建成功：{response.json()['id']}")

# 更新笔记
note_id = "note_id_here"
updated_note = {
    "body": "# 更新后的标题\n\n更新后的内容。"
}
response = requests.put(f"{base_url}/notes/{note_id}", json=updated_note)

# 删除笔记
response = requests.delete(f"{base_url}/notes/{note_id}")
```

---

## 三级执行：Joplin CLI

### 安装

```bash
# 通常Joplin桌面版自带CLI
# 位置：
# Windows: C:\Program Files\Joplin\Joplin.exe
# Mac: /Applications/Joplin.app/Contents/MacOS/Joplin
```

### 使用

```bash
# 创建新笔记
joplin create "新笔记标题" --body "# 标题\n\n内容"

# 列出所有笔记
joplin ls

# 搜索笔记
joplin search "关键词"

# 打开笔记
joplin open "笔记标题"

# 同步笔记
joplin sync
```

---

## 使用建议

1. **程序化操作** → Joplin API（最灵活）
2. **简单命令行操作** → Joplin CLI
3. **批量操作** → Python + Joplin API
4. **同步** → 确保Joplin客户端正在运行
5. **端口号** → 默认41184，可在Joplin设置中修改

---

## 注意事项

- **Web Clipper必须启用** → 设置 → Web Clipper → 启用服务
- **API token** → 如果需要认证，在请求头中加入 `Authorization: Bearer TOKEN`
- **批量操作** → 注意API速率限制
- **同步冲突** → 通过API创建的笔记可能需要手动同步
