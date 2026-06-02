---
name: 二级：IMA知识库
---

# 二级：IMA知识库

**适用场景**：上传文件/网页到IMA知识库、搜索知识库内容、管理知识库

---

## 工具对比

| 工具 | 操作类型 | 速度 | 推荐场景 |
|------|---------|------|------------|
| **IMA OpenAPI** | 上传/搜索/管理 | 中 | 程序化操作（推荐） |
| **IMA Web** | 手动上传/搜索 | 慢 | 一次性操作 |

---

## 三级执行：IMA OpenAPI（推荐）

**触发词**：上传到知识库、搜索知识库、IMA知识库、上传文件到IMA

### 前置条件

需要 `IMA_API_KEY`，在 [IMA平台](https://ima.qq.com/) 获取。

### 上传文件

```python
import requests

api_key = "YOUR_IMA_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}

# 上传文件
with open("document.pdf", "rb") as f:
    response = requests.post(
        "https://ima.qq.com/api/v1/upload",
        headers=headers,
        files={"file": f},
    )
print(f"上传成功：{response.json()}")
```

### 上传网页

```python
# 上传网页到知识库
response = requests.post(
    "https://ima.qq.com/api/v1/add_url",
    headers=headers,
    json={"url": "https://example.com/article"},
)
print(f"上传成功：{response.json()}")
```

### 搜索知识库

```python
# 搜索知识库内容
response = requests.post(
    "https://ima.qq.com/api/v1/search",
    headers=headers,
    json={"query": "用户的问题", "top_k": 5},
)
results = response.json()["results"]
for result in results:
    print(f"来源：{result['source']}")
    print(f"内容：{result['content'][:200]}...")
```

---

## 三级执行：IMA MCP（通过MCP服务器）

**触发词**：用MCP操作IMA、IMA知识库MCP

### 安装

```bash
# 安装 IMA MCP 服务器
npm install -g @ima/mcp-server

# 配置到 .mcp.json
# （IMA skill 会自动处理）
```

### 使用

```bash
# 通过 MCP 调用 IMA 操作
# Agent 会自动选择合适的工具
```

---

## 使用建议

1. **程序化上传/搜索** → IMA OpenAPI
2. **批量上传** → Python脚本 + IMA API
3. **一次性操作** → IMA Web界面
4. **实时搜索** → IMA OpenAPI 的搜索接口
5. **管理知识库** → IMA OpenAPI 的管理接口

---

## 注意事项

- **API Key 保护**：不要将 API Key 写入代码或上传到 Git
- **文件大小限制**：通常有单文件大小限制（检查官方文档）
- **速率限制**：API 有调用频率限制，批量操作注意间隔
- **知识库权限**：确保 API Key 有对应知识库的访问权限
